from .base import BaseModel
from .enums import StorageType
from sqlmodel import Field, Relationship
from typing import Optional
from uuid import UUID

class Deposit(BaseModel, table=True):
    account_id: UUID = Field(foreign_key="account.id")
    metal_id: UUID = Field(foreign_key="metal.id")
    vault_id: UUID = Field(foreign_key="vault.id")
    quantity_kg: float
    storage_type: StorageType = Field(default=StorageType.UNALLOCATED)
    serial_number: Optional[str] = None # For Allocated
    
    account: "Account" = Relationship(back_populates="deposits")
    metal: "Metal" = Relationship(back_populates="deposits")
    vault: "Vault" = Relationship()
