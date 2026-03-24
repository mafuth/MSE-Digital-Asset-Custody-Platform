from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from lib.database.main import get_session
from lib.database.models.account import Account
from lib.database.models.deposit import Deposit
from lib.database.models.metal import Metal
from lib.auth import get_current_user

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts v1"])

@router.get("/me", response_model=Account)
async def get_me(current_user: Account = Depends(get_current_user)):
    return current_user

@router.get("/portfolio", tags=["valuation v1"])
async def get_portfolio(
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    deposits = db.query(Deposit).filter(Deposit.account_id == current_user.id).all()
    
    portfolio = {}
    total_valuation = 0.0
    
    for deposit in deposits:
        metal = deposit.metal
        if metal.code not in portfolio:
            portfolio[metal.code] = {
                "name": metal.name,
                "quantity": 0.0,
                "valuation": 0.0,
                "price_per_kg": metal.current_price_kg,
                "storage_breakdown": {
                    "ALLOCATED": 0.0,
                    "UNALLOCATED": 0.0
                }
            }
        
        portfolio[metal.code]["quantity"] += deposit.quantity_kg
        portfolio[metal.code]["storage_breakdown"][deposit.storage_type] += deposit.quantity_kg
        current_val = deposit.quantity_kg * metal.current_price_kg
        portfolio[metal.code]["valuation"] += current_val
        total_valuation += current_val
        
    return {
        "user_id": str(current_user.id),
        "assets": portfolio,
        "total_valuation": total_valuation
    }
