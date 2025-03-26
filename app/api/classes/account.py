import random
from app.core.database_con import redis_client, User


class ConfimEmail:
    SIMBOL_LIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    async def create_confim_url(self):
        user_url = ""
        for _ in range(10):
            user_url+=self.SIMBOL_LIST[random.randint(0,61)]
        return user_url