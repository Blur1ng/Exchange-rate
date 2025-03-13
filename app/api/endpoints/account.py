from fastapi import APIRouter, HTTPException, Depends

from app.core.database_con import AsyncSession, User, get_db

from app.api.classes.clsss import AccountEnterData, GetData, UserData

from app.core.security import get_jwt_from_cookie
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates("app/templates")

router_account = APIRouter()

@router_account.post("/api/v1/update_account/{email}/")
async def update_account(email: str, db: AsyncSession = Depends(get_db), token: str = Depends(get_jwt_from_cookie)):
    if AccountEnterData.check_email(email):
        user = await GetData(db, User).from_token(token)
        await UserData(db, user).update_email(email)
        return {"email": email,}
    raise HTTPException(status_code=401, detail=f"Invalid email", headers={"WWW-Authenticate": "Bearer"})


