from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from lib.database.main import get_session
from lib.database.models.metal import Metal
from lib.database.models.account import Account
from lib.database.models.market_history import MetalMarketHistory
from lib.auth import get_current_user

from uuid import UUID

router = APIRouter(prefix="/api/v1/metals", tags=["api","v1","metals"])

@router.get("/", response_model=List[Metal])
async def get_metals(db: Session = Depends(get_session), current_user: Account = Depends(get_current_user)):
    return db.query(Metal).all()

@router.get("/{metal_id}", response_model=Metal)
async def get_metal(metal_id: UUID, db: Session = Depends(get_session), current_user: Account = Depends(get_current_user)):
    metal = db.query(Metal).filter(Metal.id == metal_id).first()
    if not metal:
        raise HTTPException(status_code=404, detail="Metal not found")
    return metal

@router.get("/{metal_id}/history", response_model=List[MetalMarketHistory])
async def get_metal_history(
    metal_id: UUID, 
    db: Session = Depends(get_session), 
    current_user: Account = Depends(get_current_user)
):
    history = db.query(MetalMarketHistory).filter(MetalMarketHistory.metal_id == metal_id).order_by(MetalMarketHistory.created_at.desc()).limit(50).all()
    return history
