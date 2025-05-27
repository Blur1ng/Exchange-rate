from fastapi import HTTPException
from app.core.database_con import User, Account_Data, AsyncSession
from app.api.models.users import User_Form
from sqlalchemy.future import select
import re
from datetime import datetime, timedelta, UTC
import random
import httpx
from app.api.anotherAPI.currency import get_crypto_price


class UserEnterData:
    def __init__(self, user: User_Form):
        self.user = user

    def check_password(self) -> bool:
        """
        Проверка пароля на достаточную надежность
        """
        forbidden_symbols = r'[!@#$%^&*()_+=\-\[\]{}|\\:";\'<>,.?/]'
        password = self.user.password
        if 6 <= len(password) <= 17 and not re.search(forbidden_symbols, password):
            return False
        return True

    def check_username(self) -> bool:
        """
        Проверка юсернейма на валидность
        Проверка на допустимые символы (буквы, цифры, дефисы, подчеркивания)
        """
        forbidden_symbols = r'[!@#$%^&*()+=\-\[\]{}|\\:";\'<>,.?/]'
        username = self.user.username
        if 3 <= len(username) <= 17 and not re.search(forbidden_symbols, username):
            return False
        return True


class AccountEnterData:
    @staticmethod
    def check_email(email: str) -> bool:
        """
        Проверка email на валидность
        """
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(email_regex, email):
            return True
        return False


class GetData:
    def __init__(self, db: AsyncSession, table: User | Account_Data):
        self.db = db
        self.table = table

    async def from_id(self, id: int):
        try:
            table = self.table
            result = await self.db.execute(select(table).filter(table.id == id))
            data = result.scalar_one_or_none()
            return data
        except Exception as e:
            print(f"ERROR: {id} is not a 'id' ")

    async def from_user_id(self, id: int):
        try:
            table = self.table
            result = await self.db.execute(select(table).filter(table.user_id == id))
            data = result.scalar_one_or_none()
            return data
        except Exception as e:
            print(f"ERROR: {id} is not a 'user_id' ")

    async def from_trade_id(self, id: int):
        try:
            table = self.table
            result = await self.db.execute(select(table).filter(table.trade_id == id))
            data = result.scalar_one_or_none()
            return data
        except Exception as e:
            print(f"ERROR: {id} is not a 'id' ")

    async def from_account_id(self, account_id: int):
        try:
            table = self.table
            result = await self.db.execute(
                select(table).filter(table.account_id == account_id)
            )
            data = result.scalar_one_or_none()
            return data
        except Exception as e:
            print(f"ERROR: {id} is not a 'account_id' ")

    async def from_username(self, username):
        try:
            table = self.table
            result = await self.db.execute(
                select(table).filter(table.username == username)
            )
            data = result.scalar_one_or_none()
            return data
        except Exception as e:
            print(f"ERROR: {username} is not a 'user_name' ")

    async def from_token(self, token):
        try:
            async with httpx.AsyncClient() as client:
                cookies = {"access_token": token}
                response = await client.get(
                    f"http://fastapi:8000/api/v1/verify_jwt_token/", cookies=cookies
                )
            username = response.json()
            if "detail" in username:
                return "no token"
            username = username["user_name"]
            return await self.from_username(username)

        except Exception as e:
            return HTTPException(
                status_code=401,
                detail="Токен не найден",
                headers={"WWW-Authenticate": "Bearer"},
            )


class UserData:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user

    async def update_balance(self, update: float) -> None:
        user_id = self.user.account_id
        db = self.db
        try:
            account = await GetData(db, Account_Data).from_account_id(user_id)
            account.balance += update
            await db.commit()
            await db.refresh(account)
        except Exception as e:
            print("[-] Аккаунт не найден")

    async def update_status(self):
        pass

    async def update_email(self, update):
        user_id = self.user.account_id
        db = self.db
        try:
            account = await GetData(db, Account_Data).from_account_id(user_id)
            account.email = update
            await db.commit()
            await db.refresh(account)
        except Exception as e:
            print("[-] Аккаунт не найден")

    async def update_is_verified(self):
        pass

    async def update_last_enter(self):
        pass

    async def update_username(self):
        pass

    async def update_password(self):
        pass


class Exchange:
    def __init__(self, exchange: str):
        self.exchange = exchange

    def get_current_exchange(self):
        try:
            response = get_crypto_price(self.exchange)
            return response[f"{self.exchange}USDT"]
        except Exception as e:
            return e


class RandomData:
    def __init__(self, limit: int, start: int = 0):
        self.limit = limit
        self.start = start

    async def get_time(self):
        seconds = random.randint(self.start, self.limit)
        milliseconds = random.randint(1, 999)
        time = datetime.now(UTC) + timedelta(seconds=seconds, milliseconds=milliseconds)
        return time


class Casino:
    @staticmethod
    async def get_second(time: datetime):
        t_ms = time.microsecond / 1_000_000
        t_s = time.second + t_ms
        return t_s

    @staticmethod
    async def get_zabrannyyX(time_start: datetime, time_take_profit: datetime):
        ts_s = await Casino.get_second(time_start)
        ttp_s = await Casino.get_second(time_take_profit)
        return (ttp_s - ts_s) * 100
