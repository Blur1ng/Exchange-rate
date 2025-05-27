from pydantic import BaseModel


class Trade_Form(BaseModel):
    exchange: str
    bet_amount: float
    leverage: int
    direction: str
    time: int

    class Config:
        from_attributes = True


class Trade_EndResult(BaseModel):
    trade_id: int
    end_price: float

    class Config:
        from_attributes = True
