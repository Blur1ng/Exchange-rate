from fastapi import APIRouter, HTTPException, Depends, Request, status

from app.core.database_con import AsyncSession, User, get_db, redis_client

from app.api.classes.clsss import AccountEnterData, GetData, UserData
from app.api.classes.account import ConfimEmail

from app.core.security import get_jwt_from_cookie
from fastapi.templating import Jinja2Templates

import jwt

import logging

logger = logging.getLogger(__name__)


templates = Jinja2Templates("app/templates")

router_account = APIRouter()


@router_account.post("/api/v1/update_account/{email}/")
async def update_account(
    email: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_jwt_from_cookie),
):
    if AccountEnterData.check_email(email):
        user: User = await GetData(db, User).from_token(token)
        await UserData(db, user).update_email(email)

        # Создаем ссылку подтверждения email
        verify_email = await ConfimEmail().create_confim_url()
        print(verify_email)
        await redis_client.set(f"{verify_email}", f"{user.id}", ex=300)

        return {
            "email": email,
        }
    raise HTTPException(
        status_code=401, detail=f"Invalid email", headers={"WWW-Authenticate": "Bearer"}
    )


@router_account.get("/verify-email/{user_url}")
async def verify_email(
    request: Request,
    user_url: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_jwt_from_cookie),
):
    try:
        user_id = await redis_client.get(f"{user_url}")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Срок действия ссылки истек",
            )
        user_id = int(user_id.decode())
        user: User = await GetData(db, User).from_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )
        user.is_verified = True
        return templates.TemplateResponse(
            "verify_email.html",
            {"request": request, "title": "VERIFIED EMAIL", "token": token},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Что то пошло не так, повторите позже",
        )
