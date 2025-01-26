from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLACHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:vjnjh421@localhost/Converter_db"
engine = create_async_engine(SQLACHEMY_DATABASE_URL)


Base = declarative_base()

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

