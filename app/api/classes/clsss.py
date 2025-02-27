from fastapi import HTTPException
from app.core.database_con import User, Account_Data, AsyncSession
from app.api.models.users import User_Form
from sqlalchemy.future import select
import re
import httpx
from app.core.path import apipath

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
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
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
            result = await self.db.execute(select(table).filter(table.id==id))
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            print(f"ERROR: {id} is not a 'id' ")

    async def from_trade_id(self, id: int):
        try:
            table = self.table
            result = await self.db.execute(select(table).filter(table.trade_id==id))
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            print(f"ERROR: {id} is not a 'id' ")

    async def from_account_id(self, account_id: int):
        try:
            table = self.table
            result = await self.db.execute(select(table).filter(table.account_id==account_id))
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            print(f"ERROR: {id} is not a 'account_id' ")

    async def from_username(self, username):
        try:
            table = self.table
            result = await self.db.execute(select(table).filter(table.username==username))
            user = result.scalar_one_or_none()
            return user
        except Exception as e: 
            print(f"ERROR: {username} is not a 'user_name' ")

    async def from_token(self, token):
        try:
            async with httpx.AsyncClient() as client:
                cookies = {"access_token": token}
                response = await client.get(f"{apipath}/api/v1/verify_jwt_token/", cookies=cookies)
            username = response.json()
            if 'detail' in username:
                return "no token"
            username = username["user_name"]
            return await self.from_username(username)

        except Exception as e:
            return HTTPException(status_code=401, detail="Токен не найден", headers={"WWW-Authenticate": "Bearer"})


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