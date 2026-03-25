from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from lib.database.main import get_session
from lib.database.models.account import Account
from lib.database.models.deposit import Deposit
from lib.database.models.metal import Metal
from lib.database.models.enums import StorageType
from lib.database.models.schemas import UserUpdate, PasswordChange
from lib.auth import get_current_user, verify_password, get_password_hash

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts v1"])

@router.get("/me", response_model=Account)
async def get_me(current_user: Account = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=Account)
async def update_me(
    update_data: UserUpdate,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    if update_data.name is not None:
        current_user.name = update_data.name
    if update_data.email is not None:
        # Check if email is already taken
        existing_user = db.query(Account).filter(Account.email == update_data.email, Account.id != current_user.id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = update_data.email
        
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.hashed_password = get_password_hash(data.new_password)
    db.add(current_user)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/buy-storage")
async def buy_storage(
    plan_id: str,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    # Mock storage plans
    plans = {
        "starter": 100.0,
        "pro": 500.0,
        "enterprise": 5000.0
    }
    
    if plan_id not in plans:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid plan ID")
    
    # Increase purchased storage capacity
    current_user.purchased_storage_kg += plans[plan_id]
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"message": f"Successfully purchased {plans[plan_id]}kg storage", "new_limit": current_user.purchased_storage_kg}

@router.get("/portfolio", tags=["valuation v1"])
async def get_portfolio(
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    from lib.database.models.vault import Vault
    deposits = db.query(Deposit).filter(Deposit.account_id == current_user.id).all()
    vaults = db.query(Vault).all()
    
    total_physical_capacity = sum(v.capacity_kg for v in vaults)
    total_physical_load = sum(v.current_load_kg for v in vaults)
    
    portfolio = {}
    total_valuation = 0.0
    
    for deposit in deposits:
        metal = deposit.metal
        if metal.code not in portfolio:
            portfolio[metal.code] = {
                "id": str(metal.id),
                "name": metal.name,
                "quantity": 0.0,
                "valuation": 0.0,
                "price_per_kg": metal.current_price_kg,
                "storage_breakdown": {
                    StorageType.ALLOCATED: 0.0,
                    StorageType.UNALLOCATED: 0.0
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
        "total_valuation": total_valuation,
        "total_weight_kg": sum(p["quantity"] for p in portfolio.values()),
        "purchased_storage_kg": current_user.purchased_storage_kg,
        "vault_metrics": {
            "total_capacity_kg": total_physical_capacity,
            "total_load_kg": total_physical_load,
            "available_physical_kg": total_physical_capacity - total_physical_load
        }
    }
