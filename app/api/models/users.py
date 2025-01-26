from pydantic import BaseModel
from ..database_con import Base
from sqlalchemy import Column, Integer, String

class User_Form(BaseModel):
    id: int | None = None
    username: str
    password: str

    class Config:
        from_attributes = True

class User(Base):
    __tablename__ = "User_data"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)