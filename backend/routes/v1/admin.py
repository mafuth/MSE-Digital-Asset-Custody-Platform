from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel as PydanticBaseModel
from lib.database.main import get_session
from lib.database.models.account import Account, AccountType, AccountStatus
from lib.database.models.metal import Metal
from lib.database.models.deposit import Deposit
from lib.auth import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["admin v1"])

class AccountUpdate(PydanticBaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    type: Optional[AccountType] = None
    status: Optional[AccountStatus] = None

def require_admin(current_user: Account = Depends(get_current_user)):
    if current_user.type != AccountType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin access only"
        )
    return current_user

@router.post("/metals", response_model=Metal)
async def add_metal(
    metal_data: Metal, 
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    # Check if metal already exists
    existing = db.query(Metal).filter(Metal.code == metal_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Metal with this code already exists")
    
    db.add(metal_data)
    db.commit()
    db.refresh(metal_data)
    return metal_data

@router.get("/accounts", response_model=List[Account])
async def list_accounts(
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    return db.query(Account).filter(Account.type == AccountType.CUSTOMER).all()

@router.patch("/accounts/{account_id}", response_model=Account)
async def update_account(
    account_id: UUID, 
    update_data: AccountUpdate,
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(account, key, value)
            
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.get("/accounts/{account_id}/portfolio")
async def get_customer_portfolio(
    account_id: UUID, 
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    deposits = db.query(Deposit).filter(Deposit.account_id == account_id).all()
    
    portfolio = {}
    total_valuation = 0.0
    
    for deposit in deposits:
        metal = deposit.metal
        if metal.code not in portfolio:
            portfolio[metal.code] = {
                "name": metal.name,
                "quantity": 0.0,
                "valuation": 0.0,
                "price_per_kg": metal.current_price_kg
            }
        
        portfolio[metal.code]["quantity"] += deposit.quantity_kg
        current_val = deposit.quantity_kg * metal.current_price_kg
        portfolio[metal.code]["valuation"] += current_val
        total_valuation += current_val
        
    return {
        "account": {
            "id": str(account.id),
            "name": account.name,
            "email": account.email
        },
        "assets": portfolio,
        "total_valuation": total_valuation
    }
