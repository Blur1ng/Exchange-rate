from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.security import get_jwt_from_cookie
from app.api.classes.clsss import GetData
from app.core.database_con import AsyncSession, User, Account_Data, get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import logging
templates = Jinja2Templates("app/templates")

router_main_back = APIRouter()

@router_main_back.get("/")
async def get_home_page(request: Request, token: str = Depends(get_jwt_from_cookie)):
    return templates.TemplateResponse("mainpage.html", {"request": request, "title": "Nenaebalovo.ru", "token": token})

@router_main_back.get("/login")
async def login(request: Request, token: str = Depends(get_jwt_from_cookie)):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login", "token": token})

@router_main_back.get("/register")
async def register(request: Request, token: str = Depends(get_jwt_from_cookie)):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Register", "token": token})

@router_main_back.get("/trade")
async def trade(request: Request, token: str = Depends(get_jwt_from_cookie)):
    return templates.TemplateResponse("trade.html", {"request": request, "title": "Trade", "token": token})

@router_main_back.get("/rocket")
async def roulette(request: Request, token: str = Depends(get_jwt_from_cookie)):
    return templates.TemplateResponse("rocket.html", {"request": request, "title": "Rocket", "token": token})

@router_main_back.get("/account")
async def trade(request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(get_jwt_from_cookie)):
    user: User = await GetData(db, User).from_token(token)
    if user == "no token":
        return RedirectResponse(url="/")
    username = user.username
    account: Account_Data = await GetData(db, Account_Data).from_account_id(user.account_id)
    balance = account.balance
    user_email = account.email
    is_verified = account.is_verified

    return templates.TemplateResponse("account.html", {
        "token": token,
        "request": request, 
        "title": "Account", 
        "username": username,
        "balance": balance,
        "email": user_email,
        "is_verified": is_verified
    })




