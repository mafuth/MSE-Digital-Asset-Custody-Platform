from .base import BaseModel
from sqlmodel import Field, Relationship
from uuid import UUID

class MetalMarketHistory(BaseModel, table=True):
    __tablename__ = "metals_market_history"
    
    metal_id: UUID = Field(foreign_key="metal.id")
    price_per_kg: float
    
    metal: "Metal" = Relationship(back_populates="history")
