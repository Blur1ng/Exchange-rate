from fastapi import APIRouter, HTTPException
import httpx
import xml.etree.ElementTree as ET
from app.core.security import CMC_API_KEY


router_rate = APIRouter()

@router_rate.get("/api/v1/rate/coin/{coin_ticket}/")
async def get_crypto_price(coin_ticket: str):
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

