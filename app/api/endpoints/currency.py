from fastapi import APIRouter, Depends, HTTPException
from core.security import verify_jwt_token
import httpx
import xml.etree.ElementTree as ET
from core.security import CMC_API_KEY, FIXER_API_KEY


router_rate = APIRouter()

@router_rate.get("/rate/coin/{coin_ticket}/")
async def get_crypto_price(coin_ticket: str, verify: dict = Depends(verify_jwt_token)):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json',
    }
    params = {
        'convert': 'USD'
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        data = response.json()
        coin_ticket = coin_ticket.upper()
        coin_price = next(item for item in data['data'] if item['symbol'] == coin_ticket)['quote']['USD']['price']
        return {f"{coin_ticket}USDT":coin_price}
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error while fetching data: {exc if exc else "Try in a few seconds"}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error occurred: {exc if exc else "Try in a few seconds"}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc if exc else "Try in a few seconds"}")

@router_rate.get("/rate/rub_to/{exchange}")
async def get_rub_usd_rate(exchange: str, verify: dict = Depends(verify_jwt_token)):
    url = 'https://www.cbr.ru/scripts/XML_daily.asp'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        data = response.text
        root = ET.fromstring(data)

        exchange = exchange.upper()
        for child in root.findall(".//Valute"):
            if child.find("CharCode").text == exchange:
                rate = child.find("Value").text
                return {exchange: rate}
        raise HTTPException(status_code=404, detail=f"Currency {exchange} not found.")
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch data from Central Bank API")



#API BITCOIN V1
#API_BTCUSDT_URL = "https://api.coindesk.com/v1/bpi/currentprice.json"
#@router_rate.get("/rate/bitcoin/")
#async def bitcoin_rate(verify_user: dict = Depends(verify_jwt_token)):
#    async with httpx.AsyncClient() as client:
#        response = await client.get(API_BTCUSDT_URL)
#        response.raise_for_status()  # Это поднимет исключение, если статус код будет не 2xx
#        data = response.json()  # Преобразует ответ в формат JSON
#
#        price_usd = data["bpi"]["USD"]["rate_float"]
#        # Отличе цены API и Trading View на 810 пунктов
#        return {"BTCUSDT":price_usd+810}