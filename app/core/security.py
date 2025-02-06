from dotenv import load_dotenv
import os
from fastapi import Depends, HTTPException, Request
import jwt

from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
CMC_API_KEY = os.getenv("CMC_API_KEY")
FIXER_API_KEY = os.getenv("FIXER_API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Создание JWT токена
def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# Получение Cookie
def get_jwt_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    return token

# Верификация JWT токена
async def verify_jwt_token(token: str = Depends(get_jwt_from_cookie)):
    if token is None:
        raise HTTPException(status_code=401, detail="[-] No token found", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["username"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="The token has expired", headers={"WWW-Authenticate": "Bearer"})
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})




