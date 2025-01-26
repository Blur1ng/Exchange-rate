from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.future import select
from datetime import datetime, timedelta, UTC

from api.models.users import User, User_Form
from api.database_con import async_session, AsyncSession
from api.database_con import redis_client, redis

from core.security import pwd_context
from core.security import create_jwt_token

router_users = APIRouter()

async def get_db():
    # Сессия с бд
    async with async_session() as db:
        yield db

def check_password(password: str) -> bool:
    # Проверка пароля на достаточную надежность
    if [letter.isdigit() for letter in password] and password.lower()!=password and 6 <= len(password) <= 17:
        return True
    return False

def check_username(username: str) -> bool:
    # Проверка юсернейма на адекватность
    if not([letter in "/-+=*&^$#@!~}'{|?№%:,.;)(><" for letter in username]) and 5 <= len(username) <= 17:
        return True
    return False


async def check_for_past_tense(username: str, redis_client: redis.Redis) -> bool:
    # Проверка заблокирован ли пользователь
    # Функция не дает пользователю войти, если он все еще в бан листе
    # Даже, если он ввел верные данные, система их не проверяет
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

async def anti_password_selection_system(username: str, redis_client: redis.Redis) -> bool:
    # Анти-спам система для попыток входа
    # При 5 неправильных попытках ввода пользователь помещается в бан лист,
    # Где ожидает следующих попыток
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

@router_users.post("/auth/login/")
async def login(user_data: User_Form, response: Response, db: AsyncSession = Depends(get_db)):
    # Вход юзера в систему с созданием jwt токена
    # Также идет проверка на username, password и, при неправильно вводимых данных 
    # Вызывается функция анти_подбора_паролей() (anti_password_selection_system())
    username = user_data.username
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()

    if await check_for_past_tense(username, redis_client) and user and pwd_context.verify(user_data.password, user.password):
        # Время жизни токена
        token_lifetime = datetime.now(UTC) + timedelta(minutes=5)
        token = create_jwt_token({"username": username, "exp": token_lifetime})
        # Устанавливаем токен в защищенные куки
        response.set_cookie(
            "access_token",
            token,
            max_age=5*60,
            expires=token_lifetime,
            httponly=True, # только серверу, а не клиентскому JavaScript.
            secure=True, # https only
            samesite="Strict", # ограничивает отправку cookie только с того же домена.
        )
        return {"message": "[+] Login successful"}
        
    if await anti_password_selection_system(username, redis_client):
        raise HTTPException(status_code=429, detail="[-] Too many attempts, try again in a few minutes", headers={"WWW-Authenticate": "Bearer"})
    
    raise HTTPException(status_code=401, detail="[-] Invalid credentials", headers={"WWW-Authenticate": "Bearer"})

