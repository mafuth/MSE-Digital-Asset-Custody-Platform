from .base import BaseModel
from sqlmodel import Field, Relationship
from typing import List

class Account(BaseModel, table=True):
    name: str
    email: str = Field(index=True, unique=True)
    hashed_password: str
    
    deposits: List["Deposit"] = Relationship(back_populates="account")
    transactions: List["Transaction"] = Relationship(back_populates="account")
