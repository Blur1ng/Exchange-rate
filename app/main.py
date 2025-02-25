from fastapi import FastAPI
from api.endpoints.users import router_users
from api.endpoints.currency import router_rate
from api.endpoints.account import router_account
from webapp.endpoints.main_back import router_main_back
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

app.include_router(router_users)
app.include_router(router_rate) 
app.include_router(router_main_back)
app.include_router(router_account)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)