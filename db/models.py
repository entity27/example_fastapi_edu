from sqlalchemy import Column, String, DateTime
from .base import Base

class UserModel(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    password = Column(String)
    created = Column(DateTime)