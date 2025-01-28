from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from core.security import get_jwt_from_cookie


router_main_back = APIRouter()

templates = Jinja2Templates("app/templates")


@router_main_back.get("/")
async def get_home_page(request: Request, token: str = Depends(get_jwt_from_cookie)):
    """
    Главная страница, которая требует авторизации.
    Если токен присутствует и валиден, продолжаем выполнение.
    Если токен отсутствует или невалиден — показываем страницу логина.
    """
    if token:
        return RedirectResponse(url='/trade')
    else:
        return RedirectResponse(url='/login')

@router_main_back.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router_main_back.get("/trade")
async def login(request: Request):
    return templates.TemplateResponse("trade.html", {"request": request})

@router_main_back.get("/register")
async def login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})




