from fastapi import APIRouter, HTTPException, Depends, Response, logger
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timedelta, UTC

from app.api.models.users import User_Form
from app.webapp.models.trade import Trade_Form
from app.core.database_con import  AsyncSession, redis_client, User, Trade, Account_Data, Trade_Result, get_db
from app.core.security import pwd_context, create_jwt_token, verify_jwt_token

from app.core.celery_con import celery, process_trade

from app.api.classes.clsss import GetData, UserEnterData, UserData

import asyncio


router_users = APIRouter()

TOKEN_LIFE_TIME = 30 #minutes

@router_users.post("/api/v1/auth/register/")
async def register(enter_data: User_Form, db: AsyncSession = Depends(get_db)):
    """
    Регистрация пользователя и проверка вводимых данных
    """
    user = UserEnterData(enter_data)
    if user.check_password():
        raise HTTPException(401, "[-] Weak password")
    if user.check_username():
        raise HTTPException(401, "[-] Invalid username")
    try:
        hash_password = pwd_context.hash(enter_data.password)
        user = User(username=enter_data.username, password=hash_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        user = await GetData(db, User).from_username(user.username)

        account = Account_Data(account_id=user.id)
        db.add(account)
        await db.commit()
        await db.refresh(account)

        user.account_id = user.id
        await db.commit()
        await db.refresh(user)
        return {"Registration was successful"}
    except Exception as e:
            raise HTTPException(status_code=401, detail="Username already exists")

async def check_for_past_tense(username: str) -> bool:
    """
    Проверка заблокирован ли пользователь
    Функция не дает пользователю войти, если он все еще в бан листе
    Даже, если он ввел верные данные, система их не проверяет
    """
    block_key = f"blocked:{username}"
    block_time = await redis_client.get(block_key)

    if block_time:
        block_time = datetime.fromisoformat(block_time.decode())
        if datetime.now() > block_time:
            # Разблокировать пользователя
            await redis_client.delete(block_key)
            await redis_client.delete(f"wrong_attempts:{username}")
            return True
        return False
    return True

async def anti_password_selection_system(username: str) -> bool:
    """
    Анти-спам система для попыток входа
    При 5 неправильных попытках ввода пользователь помещается в бан лист,
    Где ожидает следующих попыток
    """
    attempts_key = f"wrong_attempts:{username}"
    wrong_attempts = await redis_client.get(attempts_key)

    if wrong_attempts:
        wrong_attempts = int(wrong_attempts.decode())
        wrong_attempts += 1
    else:
        wrong_attempts = 1

    await redis_client.set(attempts_key, wrong_attempts, ex=60)

    if wrong_attempts >= 5:
        # Блокируем пользователя на 1 минуту
        block_key = f"blocked:{username}"
        await redis_client.set(block_key, (datetime.now() + timedelta(minutes=1)).isoformat(), ex=60)
        return True
    return False

@router_users.post("/api/v1/auth/login/")
async def login(user_data: User_Form, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Вход юзера в систему с созданием jwt токена
    Также идет проверка на username, password и, при неправильно вводимых данных 
    Вызывается функция анти_подбора_паролей() (anti_password_selection_system())
    """
    username = user_data.username
    user = await GetData(db, User).from_username(username)

    if await check_for_past_tense(username) and user and pwd_context.verify(user_data.password, user.password):
        # Время жизни токена
        token_lifetime = datetime.now(UTC) + timedelta(minutes=TOKEN_LIFE_TIME)
        token = create_jwt_token({"username": username, "exp": token_lifetime})
        # Устанавливаем токен в защищенные куки
        response.set_cookie(
            "access_token",
            token,
            max_age=TOKEN_LIFE_TIME*60,
            expires=TOKEN_LIFE_TIME,
            httponly=True, # только серверу, а не клиентскому JavaScript.
            secure=True, # https only
            samesite="Strict", # ограничивает отправку cookie только с того же домена.
        )
        return {"message": "[+] Login successful"}
        
    if await anti_password_selection_system(username):
        raise HTTPException(status_code=429, detail="Too many attempts, try again in a few minutes", headers={"WWW-Authenticate": "Bearer"})
    
    raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})

@router_users.get("/api/v1/verify_jwt_token/")
async def verify_jwt_token_point(verify: dict = Depends(verify_jwt_token)):
    return {"user_name": verify}

@router_users.post("/api/v1/trade_it/")
async def trade_it(trade_data: Trade_Form, db: AsyncSession = Depends(get_db)):
    """
    Сохранения результатов сделки в postgre
    Временное сохранение в redis    
    """
    time = datetime.now(UTC) + timedelta(minutes=trade_data.time) # Переводим из int в datetime

    exchange=trade_data.exchange
    bet_amount=trade_data.bet_amount
    leverageX=trade_data.leverage
    direction=trade_data.direction
    time_naive = time.replace(tzinfo=None) # Преобразуем в naive datetime (без временной зоны)
    start_price=trade_data.start_price
    user_name=trade_data.user_name


    user = await GetData(db, User).from_username(user_name)
    user_id = user.id

    trade = Trade(
        exchange=exchange,
        bet_amount=bet_amount,
        leverageX=leverageX,
        direction=direction,
        time=time_naive,
        start_price=start_price,
        user_id=user_id,
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)

    # Фоновая задача
    process_trade.apply_async(
        args=[trade.id],
        countdown=trade_data.time * 60  # Задержка в секундах
    )
    return {"trade_id": trade.id}

@router_users.websocket("/api/v1/ws/trade_status/{trade_id}")
async def websocket_trade_status(websocket: WebSocket, trade_id: int, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    
    try:
        while True:
            # Используем отдельную сессию для каждого запроса
            async with db.begin():
                trade = await GetData(db, Trade).from_id(trade_id)
                
                if not trade:
                    await websocket.send_json({"error": "Trade not found"})
                    break
                
                # Принудительно обновляем данные
                await db.refresh(trade)
                
                if trade.status != "pending":
                    trade_result = await GetData(db, Trade_Result).from_trade_id(trade_id)
                    
                    response = {
                        "status": trade.status,
                        "result": trade.trade_result,
                        "end_price": trade_result.end_price if trade_result else None,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_json(response)
                    await UserData(db, trade.user).update_balance(trade_result.money)
                    await websocket.close()
                    break

            await asyncio.sleep(3)  # Уменьшенный интервал проверки
            
    except WebSocketDisconnect:
        await websocket.close()
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()