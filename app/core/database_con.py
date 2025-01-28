from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float


SQLACHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:vjnjh421@localhost/Converter_db"
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
    user_id = Column(Integer, ForeignKey("User_data.id"))
    result = Column(Integer, ForeignKey("Trade_Result.trade_id"))

class Trade_Result(Base):
    __tablename__ = "Trade_Result"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, index=True, unique=True)
    trade_result = Column(String, index=True)
    money = Column(Float, index=True)

class User(Base):
    __tablename__ = "User_data"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String)
    

# redis
redis_client = redis.from_url("redis://localhost:6379", db=0)
