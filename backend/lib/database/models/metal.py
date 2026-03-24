from .base import BaseModel
from sqlmodel import Field, Relationship
from typing import List

class Metal(BaseModel, table=True):
    code: str = Field(index=True, unique=True) # GOLD, SILVER, PLATINUM
    name: str
    category: str # e.g. Precious Metals
    current_price_kg: float
    
    deposits: List["Deposit"] = Relationship(back_populates="metal")
    transactions: List["Transaction"] = Relationship(back_populates="metal")
    history: List["MetalMarketHistory"] = Relationship(back_populates="metal")
