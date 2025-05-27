import asyncio
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse

from app.core.database_con import AsyncSession, get_db, Rocket, User
from app.api.classes.clsss import GetData, RandomData, UserData

router_rocket = APIRouter()

START_ROCKET_TIME = 0
LIMIT_ROCKET_TIME = 9
USLOZHNENIYE = 2  # Усложнение игры. Чем больше, тем раньше закончится ракетка. max=8
UTC = timezone.utc


async def increase_multiplier(websocket: WebSocket, multiplier_state: dict):
    try:
        k = 0.1
        while True:
            multiplier_state["value"] += k
            multiplier_state["value"] = round(multiplier_state["value"], 1)
            if multiplier_state["value"] > 8:
                k = 1
            elif multiplier_state["value"] > 4:
                k = 0.3
            elif multiplier_state["value"] == 1.5:
                k = 0.1

            await websocket.send_json(
                {"action": "update_multiplier", "value": multiplier_state["value"]}
            )

            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        raise


@router_rocket.websocket("/api/v1/ws/rocket/")
async def rocket_con(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """
    1. Приходит ставка
    2. Рассчитывается: время через какое нужно успеть забрать time_uspel
    3. Если пользователь успел нажать кнопку "Забрать X", то uspel = True
    4. В случае, если время вышло, на фронт приходит сообщение: "ракетка улетела", uspel = False
    5. В случае успеха end_bet=start_bet*zabrannyyX, иначе end_bet=0
    """
    await websocket.accept()
    multiplier_task = None
    zabrannyyX = 0

    multiplier_state = {"value": 0}

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")

            token = websocket.cookies.get("access_token")

            user = await GetData(db, User).from_token(token)
            if user == "no token":
                await websocket.close()
                return RedirectResponse(url="/")

            if action == "start_bet":
                start_bet = int(message.get("betValue"))
                time_uspel = await RandomData(
                    start=START_ROCKET_TIME, limit=LIMIT_ROCKET_TIME
                ).get_time()
                time_uspel = time_uspel.replace(tzinfo=None)
                rocket = Rocket(
                    start_bet=start_bet,
                    time_uspel=time_uspel - timedelta(seconds=USLOZHNENIYE),
                    user_id=user.id,
                )

                db.add(rocket)
                await db.commit()
                await db.refresh(rocket)

                multiplier_state["value"] = 0

                # включение счетчика
                multiplier_task = asyncio.create_task(
                    increase_multiplier(websocket, multiplier_state)
                )

            if action == "take_profit":
                # отключение счетчика
                if multiplier_task and not multiplier_task.done():
                    zabrannyyX = multiplier_state["value"]
                    multiplier_task.cancel()
                else:
                    zabrannyyX = multiplier_state["value"]

                time_take_profit = datetime.now(timezone.utc).replace(tzinfo=None)
                rocket.time_take_profit = time_take_profit
                result = time_uspel - time_take_profit - timedelta(seconds=USLOZHNENIYE)
                end_bet = rocket.start_bet
                if result.days == 0:
                    uspel = True
                    # обновление икса на финальное значение
                    zabrannyyX = multiplier_state["value"]
                    end_bet = round(end_bet * zabrannyyX, 2)
                    await UserData(db, user).update_balance(end_bet)
                else:
                    uspel = False
                    zabrannyyX = 0
                    await UserData(db, user).update_balance(-end_bet)

                rocket.end_bet = end_bet
                rocket.uspel = uspel
                rocket.zabrannyyX = zabrannyyX

                await db.commit()
                await db.refresh(rocket)

                if uspel:
                    await websocket.send_json({"status": "WIN", "end_bet": end_bet})
                else:
                    await websocket.send_json({"status": "Lose", "end_bet": end_bet})
                await websocket.close()
                break

    except WebSocketDisconnect:
        if multiplier_task and not multiplier_task.done():
            multiplier_task.cancel()
        await websocket.close()
