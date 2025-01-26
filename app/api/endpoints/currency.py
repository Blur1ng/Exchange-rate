from fastapi import APIRouter, Depends
from core.security import verify_jwt_token
import httpx


router_rate = APIRouter()


API_BTCUSDT_URL = "https://api.coindesk.com/v1/bpi/currentprice.json"
@router_rate.get("/rate/bitcoin/")
async def bitcoin_rate(verify_user: dict = Depends(verify_jwt_token)):
    async with httpx.AsyncClient() as client:
        response = await client.get(API_BTCUSDT_URL)
        response.raise_for_status()  # Это поднимет исключение, если статус код будет не 2xx
        data = response.json()  # Преобразует ответ в формат JSON

        price_usd = data["bpi"]["USD"]["rate_float"]
        # Отличе цены API и Trading View на 810 пунктов
        return {"BTCUSDT":price_usd+810}