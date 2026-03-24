from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from lib.database.main import get_session
from lib.database.models.metal import Metal

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
