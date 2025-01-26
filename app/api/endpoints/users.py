from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.future import select
from datetime import datetime, timedelta, UTC

from api.models.users import User, User_Form
from api.database_con import async_session, AsyncSession

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

@router_users.post("/auth/register/")
async def register(user: User_Form, db: AsyncSession = Depends(get_db)):
    # Регистрация пользователя и проверка вводимых данных
    if not check_password(user.password):
        raise HTTPException(401, "[-] Weak password")
    if not check_username(user.username):
        raise HTTPException(401, "[-] Invalid username")
    
    hash_password = pwd_context.hash(user.password)
    user = User(username=user.username, password=hash_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"[+] Registration was successful"}

blocked_users = {} # {username: time_until_release}
wrong_attempts = {} # {username: number_of_wrong_attemtpts}

def check_for_past_tense(username: str):
    # Функция не дает пользователю войти, если он все еще в бан листе
    # Даже, если он ввел верные данные, система их не проверяет
    if f"{username}" in blocked_users:
        if datetime.now(UTC) > blocked_users[f"{username}"]:
            wrong_attempts.pop(f"{username}")
            blocked_users.pop(f"{username}")
            return 1
        return 0
    return 1

def anti_password_selection_system(username: str):
    # При 5 неправильных попытках ввода пользователь помещается в бан лист,
    # Где ожидает следующих попыток через timedelta(minutes=1)
    if f"{username}" not in wrong_attempts:
        wrong_attempts[f"{username}"] = 1
    else:
        attempts = wrong_attempts[f"{username}"]
        wrong_attempts[f"{username}"] = attempts + 1
        if attempts + 1 >= 5:
            if f"{username}" in blocked_users:
                if datetime.now(UTC) > blocked_users[f"{username}"]:
                    wrong_attempts.pop(f"{username}")
                    blocked_users.pop(f"{username}")
                    return 0
            blocked_users[f"{username}"] = datetime.now(UTC) + timedelta(minutes=1)
            return 1
    return 0

@router_users.post("/auth/login/")
async def login(user_data: User_Form, response: Response, db: AsyncSession = Depends(get_db)):
    # Вход юзера в систему с созданием jwt токена
    # Также идет проверка на username, password и, при неправильно вводимых данных 
    # Вызывается функция анти_подбора_паролей() (anti_password_selection_system())
    username = user_data.username
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()

    if check_for_past_tense(username) and user and pwd_context.verify(user_data.password, user.password):
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
        
    if anti_password_selection_system(username):
        raise HTTPException(status_code=429, detail="[-] Too many attempts, try again in a few minutes", headers={"WWW-Authenticate": "Bearer"})
    raise HTTPException(status_code=401, detail="[-] Invalid credentials", headers={"WWW-Authenticate": "Bearer"})

