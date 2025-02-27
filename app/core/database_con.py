from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, create_engine
from .security import DB_PASSWORD, POSTGRES_DB, POSTGRES_USER



# Синхронная сессия для Celery
sinc_engine = create_engine(f"postgresql+psycopg2://{POSTGRES_USER}:{DB_PASSWORD}@db:5432/{POSTGRES_DB}")
sync_session = sessionmaker(bind=sinc_engine)

# Асинхронная сессия
SQLACHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{DB_PASSWORD}@db:5432/{POSTGRES_DB}"
engine = create_async_engine(SQLACHEMY_DATABASE_URL)


Base = declarative_base()

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Trade(Base):
    __tablename__ = "Trade_data"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, index=True)
    bet_amount = Column(Float, index=True)
    leverageX = Column(Integer)
    direction = Column(String)
    time = Column(DateTime)
    start_price = Column(Float)
    status = Column(String, index=True, default="pending")
    trade_result = Column(String, index=True, default="pending") #W/L

    user_id = Column(Integer, ForeignKey("User_data.id"))
    result = Column(Integer, ForeignKey("Trade_result.trade_id"))

class Trade_Result(Base):
    __tablename__ = "Trade_result"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, index=True, unique=True)
    end_price = Column(Float, nullable=True)
    money = Column(Float, index=True)

class User(Base):
    __tablename__ = "User_data"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    password = Column(String)

    account_id = Column(Integer, ForeignKey("Account_data.account_id"))

class Account_Data(Base):
    __tablename__ = "Account_data"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, index=True, unique=True)
    balance = Column(Float, index=True, default=0.0)
    last_enter = Column(DateTime)
    status = Column(String, index=True, default="Offline")
    email = Column(String(100), unique=True, index=True)
    is_verified = Column(Boolean, default=False)  

    

# redis
redis_client = redis.from_url(f"redis://redis:6379", db=0)

async def get_db():
        # Сессия с бд
        async with async_session() as db:
            yield db