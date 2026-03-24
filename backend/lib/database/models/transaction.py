from .base import BaseModel
from sqlmodel import Field, Relationship
from uuid import UUID

class Transaction(BaseModel, table=True):
    account_id: UUID = Field(foreign_key="account.id")
    metal_id: UUID = Field(foreign_key="metal.id")
    type: str # DEPOSIT | WITHDRAWAL
    quantity: float
    status: str = Field(default="COMPLETED")
    
    account: "Account" = Relationship(back_populates="transactions")
    metal: "Metal" = Relationship(back_populates="transactions")
