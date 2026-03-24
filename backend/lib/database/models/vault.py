from .base import BaseModel
from sqlmodel import Field
from typing import Optional

class Vault(BaseModel, table=True):
    name: str = Field(unique=True)
    location: str
    capacity_kg: float
    current_load_kg: float = Field(default=0.0)
    status: str = Field(default="ACTIVE") # ACTIVE | FULL | MAINTENANCE
