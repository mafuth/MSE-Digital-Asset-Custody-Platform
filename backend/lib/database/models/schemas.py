from sqlmodel import SQLModel
from typing import Optional

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
