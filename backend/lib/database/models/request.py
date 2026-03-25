from .base import BaseModel
from .enums import TransactionType, StorageType, RequestStatus
from sqlmodel import Field, Relationship
from typing import Optional
from uuid import UUID
from datetime import datetime

class Request(BaseModel, table=True):
    account_id: UUID = Field(foreign_key="account.id")
    metal_id: UUID = Field(foreign_key="metal.id")
    vault_id: UUID = Field(foreign_key="vault.id")
    type: TransactionType
    quantity_kg: float
    storage_type: StorageType
    serial_number: Optional[str] = None
    status: RequestStatus = Field(default=RequestStatus.PENDING)
    transaction_id: Optional[UUID] = Field(default=None, foreign_key="transaction.id")
    
    account: "Account" = Relationship()
    metal: "Metal" = Relationship()
    vault: "Vault" = Relationship()
    transaction: Optional["Transaction"] = Relationship()
