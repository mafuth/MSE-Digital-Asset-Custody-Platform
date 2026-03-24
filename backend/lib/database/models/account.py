import enum
from .base import BaseModel
from sqlmodel import Field, Relationship
from typing import List, Optional

class AccountType(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    REMOVED = "removed"

class Account(BaseModel, table=True):
    name: str
    email: str = Field(index=True, unique=True)
    hashed_password: str
    type: AccountType = Field(default=AccountType.CUSTOMER)
    status: AccountStatus = Field(default=AccountStatus.ACTIVE)
    purchased_storage_kg: float = Field(default=50.0)
    
    deposits: List["Deposit"] = Relationship(back_populates="account")
    transactions: List["Transaction"] = Relationship(back_populates="account")
