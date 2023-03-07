from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .Database import Base
from datetime import datetime
import pydantic

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True)
    hashed_password = Column(String)
    token = Column(String)
    expires_in = Column(DateTime)

class UserBaseShema(pydantic.BaseModel):
    phone: str

class UserCreateShema(UserBaseShema):
    password: str

class UserShema(UserBaseShema):
    id: int
    token: str
    expires_in: datetime

    class Config:
        orm_mode = True
