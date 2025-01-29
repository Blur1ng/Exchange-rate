from celery import Celery
from sqlalchemy import select
import requests
from .database_con import Trade, Trade_Result, sync_session


celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)
celery.conf.update(
    broker_connection_retry_on_startup=True
)
@celery.task(name="core.celery_con.process_trade")
def process_trade(trade_id: int):
    """
    Используем синхронный подход как для функции так и для подключению к бд
    Получаем результат ставки, заносим его в бд и возвращаем статус, результат(W/L)
    """
    session = sync_session()
    try:
        trade = session.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            return {"status": "error", "message": "Trade not found"}

        try:
            # Обращаемся к api и узнаем текущий курс
            response = requests.get(f"http://localhost:8000/api/v1/rate/coin/{trade.exchange}/")
            data = response.json()
            end_price = data[f"{trade.exchange}USDT"]

            if (end_price > trade.start_price and trade.direction == "up") or (end_price < trade.start_price and trade.direction == "down"):
                result = "W"
                profit = trade.bet_amount * trade.leverageX
            else:
                result = "L"
                profit = -trade.bet_amount * trade.leverageX

            trade_result = Trade_Result(
                trade_id=trade.id,
                end_price=end_price,
                money=profit
            )      
            session.add(trade_result)
            session.commit()

            trade.status = "completed"
            trade.trade_result=result,
            trade.result=trade.id
            session.commit()

            return {"status": "completed", "result": result}

        except Exception as e:
            trade.status = "failed"
            session.commit()
            return {"status": "error", "message": str(e)}

    finally:
        session.close()