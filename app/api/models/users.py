from pydantic import BaseModel

class User_Form(BaseModel):
    id: int | None = None
    username: str
    password: str

    class Config:
        from_attributes = True
