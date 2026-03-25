from .base import BaseModel
from .enums import TransactionType, TransactionStatus
from sqlmodel import Field, Relationship
from typing import Optional
from uuid import UUID

class Transaction(BaseModel, table=True):
    account_id: UUID = Field(foreign_key="account.id")
    metal_id: UUID = Field(foreign_key="metal.id")
    vault_id: Optional[UUID] = Field(default=None, foreign_key="vault.id")
    bar_ref_id: Optional[str] = Field(default=None)
    type: TransactionType
    quantity: float
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    
    account: "Account" = Relationship(back_populates="transactions")
    metal: "Metal" = Relationship(back_populates="transactions")
    vault: Optional["Vault"] = Relationship()
