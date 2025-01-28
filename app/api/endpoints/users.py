from fastapi import APIRouter, HTTPException, Depends, Response, Request
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta, UTC
import re

from api.models.users import User_Form
from webapp.models.trade import Trade_Form, Trade_EndResult
from core.database_con import async_session, AsyncSession
from core.database_con import redis_client
from core.database_con import User, Trade, Trade_Result

from core.security import pwd_context
from core.security import create_jwt_token, verify_jwt_token

router_users = APIRouter()

TOKEN_LIFE_TIME = 30 #minutes

async def get_db():
    # Сессия с бд
    async with async_session() as db:
        yield db

def check_password(password: str) -> bool:
    # Проверка пароля на достаточную надежность
    if password.lower()!=password and 6 <= len(password) <= 17 and not re.match("^[a-zA-Z0-9_-]*$", password):
        return False
    return True

def check_username(username: str) -> bool:
    """
    Проверка юсернейма на адекватность
    Проверка на допустимые символы (буквы, цифры, дефисы, подчеркивания)
    """
    if not (3 <= len(username) <= 17 and re.match("^[a-zA-Z0-9_-]*$", username)):
        return False
    return True

@router_users.post("/api/v1/auth/register/")
async def register(user: User_Form, db: AsyncSession = Depends(get_db)):
    """
    Регистрация пользователя и проверка вводимых данных
    """
    if check_password(user.password):
        raise HTTPException(401, "[-] Weak password")
    if check_username(user.username):
        raise HTTPException(401, "[-] Invalid username")
    
    hash_password = pwd_context.hash(user.password)
    user = User(username=user.username, password=hash_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"Registration was successful"}

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
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()

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
    """
    Верификация JWT токена и получение id User'а
    """
    return {"user_name": verify}

@router_users.post("/api/v1/trade_it/")
async def trade_it(trade_data: Trade_Form, db: AsyncSession = Depends(get_db)):
    """
    Сохранения результатов сделки в postgre
    Временное сохранение в redis
    """
    time = datetime.now(UTC) + timedelta(minutes=trade_data.time) # Переводим из int в datetime
    user_name=trade_data.user_name

    exchange=trade_data.exchange
    bet_amount=trade_data.bet_amount
    leverageX=trade_data.leverage
    direction=trade_data.direction
    time_naive = time.replace(tzinfo=None) # Преобразуем в naive datetime (без временной зоны)
    start_price=trade_data.start_price
    user_name=trade_data.user_name

    result=await db.execute(select(User).filter(User.username==user_name))
    user_id=result.scalar_one_or_none().id
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

    result = await db.execute(select(func.max(Trade.id)))
    trade_id = result.scalar_one_or_none()
    redis_data = {
        "bet_amount_X_leverageX": bet_amount*leverageX,
        "direction": direction,
        "start_price": start_price,
    }
    await redis_client.hmset("trade_data", redis_data)
    return {"trade_id": trade_id}

@router_users.post("/api/v1/check_trade/")
async def check_trade(trade_result: Trade_EndResult, db: AsyncSession = Depends(get_db)):
    """
    Вычисление выигрыша или проигрыша и загрузка в базу данных
    """
    past_data = await redis_client.hgetall("trade_data")
    past_data = {k.decode("utf-8"): v.decode("utf-8") for k, v in past_data.items()}

    await redis_client.delete("trade_data")

    trade_id = trade_result.trade_id
    all_bet = float(past_data["bet_amount_X_leverageX"])
    end_price=trade_result.end_price

    if end_price > float(past_data["start_price"]):
        if past_data["direction"] == "up":
            end_trade_result = "W"
            end_price = all_bet
        else:
            end_trade_result = "L"
            end_price = -all_bet
    else:
        if past_data["direction"] == "down":
            end_trade_result = "W"
            end_price = all_bet
        else:
            end_trade_result = "L"
            end_price = -all_bet

    result = Trade_Result(
        trade_id=trade_id,
        trade_result=end_trade_result,
        money=end_price,
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)

    trade = await db.execute(select(Trade).filter(Trade.id==trade_id))
    trade = trade.scalar_one_or_none()
    trade.result = trade_id
    await db.commit()
    await db.refresh(trade)
    if end_trade_result == "W":
        return {"message": f"WIN +{all_bet}"}
    return {"message": f"Lose -{all_bet}"}
    


