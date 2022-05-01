from pydantic import BaseModel

from db.base import Base

class User(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode=True

class Tokens(BaseModel):
    access_token: str
    refresh_token: str

class Message(BaseModel):
    message: str