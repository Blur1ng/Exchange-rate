from dotenv import load_dotenv
import os
from fastapi import Depends, HTTPException, Request
import jwt

from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Создание JWT токена
def create_jwt_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# Получение Cookie
def get_jwt_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="[-] No token found", headers={"WWW-Authenticate": "Bearer"})
    return token

# Верификация JWT токена
async def verify_jwt_token(token: str = Depends(get_jwt_from_cookie)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["username"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="[-] The token has expired", headers={"WWW-Authenticate": "Bearer"})
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="[-] Invalid token", headers={"WWW-Authenticate": "Bearer"})

