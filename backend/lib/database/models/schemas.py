from sqlmodel import SQLModel
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserCreate(SQLModel):
    name: str
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str

class PasswordResetRequest(SQLModel):
    email: str

class PasswordResetConfirm(SQLModel):
    token: str
    new_password: str

class MetalRead(SQLModel):
    id: UUID
    code: str
    name: str

class TransactionRead(SQLModel):
    id: UUID
    account_id: UUID
    metal_id: UUID
    type: str # DEPOSIT | WITHDRAWAL
    quantity: float
    status: str
    created_at: datetime
    metal: Optional[MetalRead] = None

class TransactionCreate(BaseModel):
    metal_id: UUID
    quantity_kg: float
    storage_type: str # ALLOCATED | UNALLOCATED
    vault_id: UUID
    serial_number: Optional[str] = None
