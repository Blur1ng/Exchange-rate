from fastapi import FastAPI
from api.endpoints.users import router_users
from api.endpoints.currency import router_rate
import uvicorn

app = FastAPI()

app.include_router(router_users)
app.include_router(router_rate)



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)