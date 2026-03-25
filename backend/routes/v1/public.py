from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from lib.database.main import get_session
from lib.database.models.metal import Metal

from lib.database.models.vault import Vault

router = APIRouter(prefix="/api/v1/public", tags=["public v1"])

@router.get("/prices")
async def get_market_prices(session: Session = Depends(get_session)):
    """
    Exposes current market prices for all metals.
    """
    statement = select(Metal)
    metals = session.exec(statement).all()
    return [
        {
            "code": m.code,
            "name": m.name,
            "price_kg": m.current_price_kg,
            "updated_at": m.updated_at
        }
        for m in metals
    ]

@router.get("/vaults")
async def get_public_vaults(session: Session = Depends(get_session)):
    """
    Exposes high-level status of storage facilities.
    """
    statement = select(Vault)
    vaults = session.exec(statement).all()
    return [
        {
            "name": v.name,
            "location": v.location,
            "status": v.status,
            "capacity_kg": v.capacity_kg,
            "current_load_kg": v.current_load_kg
        }
        for v in vaults
    ]
