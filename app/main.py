from fastapi import FastAPI
from app.api.endpoints.users import router_users
from app.api.endpoints.account import router_account
from app.api.endpoints.rocket import router_rocket
from app.webapp.endpoints.main_back import router_main_back
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

app.include_router(router_users)
app.include_router(router_main_back)
app.include_router(router_account)
app.include_router(router_rocket)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)#127.0.0.1