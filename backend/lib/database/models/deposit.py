from .base import BaseModel
from sqlmodel import Field, Relationship
from typing import Optional
from uuid import UUID

class Deposit(BaseModel, table=True):
    account_id: UUID = Field(foreign_key="account.id")
    metal_id: UUID = Field(foreign_key="metal.id")
    quantity_kg: float
    storage_type: str # ALLOCATED | UNALLOCATED
    serial_number: Optional[str] = None # For Allocated
    vault_location: str
    
    account: "Account" = Relationship(back_populates="deposits")
    metal: "Metal" = Relationship(back_populates="deposits")
