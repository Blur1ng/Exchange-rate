from fastapi import HTTPException
from app.core.security import CMC_API_KEY
import requests


def get_crypto_price(coin_ticket: str):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    headers = {
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
        "Accept": "application/json",
    }
    params = {"convert": "USD"}
    try:
        response = requests.get(url, headers=headers, params=params)

        data = response.json()
        coin_ticket = coin_ticket.upper()
        coin_price = next(
            item for item in data["data"] if item["symbol"] == coin_ticket
        )["quote"]["USD"]["price"]
        return {f"{coin_ticket}USDT": coin_price}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {e if e else "Try in a few seconds"}",
        )
