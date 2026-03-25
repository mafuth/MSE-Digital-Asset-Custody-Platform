from sqlmodel import SQLModel
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from .enums import TransactionType, TransactionStatus, StorageType, RequestStatus

class UserCreate(SQLModel):
    name: str
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None

class PasswordChange(SQLModel):
    current_password: str
    new_password: str

class Token(SQLModel):
    access_token: str
    token_type: str

class PasswordResetRequest(SQLModel):
    email: str

class PasswordResetConfirm(SQLModel):
    token: str
    new_password: str

class AccountRead(SQLModel):
    id: UUID
    name: str
    email: str

class VaultRead(SQLModel):
    id: UUID
    name: str
    location: str

class MetalRead(SQLModel):
    id: UUID
    code: str
    name: str

class TransactionRead(SQLModel):
    id: UUID
    account_id: UUID
    metal_id: UUID
    type: TransactionType
    quantity: float
    status: TransactionStatus
    created_at: datetime
    vault_id: Optional[UUID] = None
    bar_ref_id: Optional[str] = None
    metal: Optional[MetalRead] = None
    vault: Optional[VaultRead] = None

class TransactionCreate(BaseModel):
    metal_id: UUID
    quantity_kg: float
    storage_type: StorageType
    vault_id: UUID
    serial_number: Optional[str] = None
    serial_numbers: Optional[List[str]] = None

class RequestRead(BaseModel):
    id: UUID
    account_id: UUID
    metal_id: UUID
    vault_id: UUID
    type: TransactionType
    quantity_kg: float
    storage_type: StorageType
    serial_number: Optional[str] = None
    status: RequestStatus
    created_at: datetime
    metal: Optional[MetalRead] = None
    account: Optional[AccountRead] = None
    vault: Optional[VaultRead] = None

    class Config:
        from_attributes = True
