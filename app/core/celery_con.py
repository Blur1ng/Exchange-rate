from celery import Celery
from .database_con import Trade, Trade_Result, sync_session
from app.api.classes.clsss import Exchange


celery = Celery(
    "tasks",
    broker=f"redis://redis:6379/0",
    backend=f"redis://redis:6379/1"
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
            end_price = Exchange(trade.exchange).get_current_exchange()

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
            session.refresh(trade_result)

            trade.status = "completed"
            trade.trade_result=result
            trade.result=trade.id
            session.commit()
            session.begin()
            session.refresh(trade)

            return {"status": "completed", "result": result}

        except Exception as e:
            trade.status = "failed"
            session.commit()
            return {"status": "error", "message": str(e)}

    finally:
        session.close()