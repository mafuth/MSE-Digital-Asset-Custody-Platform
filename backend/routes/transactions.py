from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from lib.database.main import get_session
from lib.database.models.transaction import Transaction
from lib.database.models.deposit import Deposit
from lib.database.models.account import Account
from lib.database.models.metal import Metal
from lib.auth import get_current_user
from lib.events import dispatch_event

router = APIRouter(prefix="/api/v1/transactions", tags=["api","v1","transactions"])

@router.post("/deposit", response_model=Deposit)
async def create_deposit(
    metal_id: UUID,
    quantity_kg: float,
    storage_type: str, # ALLOCATED | UNALLOCATED
    vault_location: str,
    serial_number: Optional[str] = None,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    if storage_type == "ALLOCATED" and not serial_number:
        raise HTTPException(status_code=400, detail="Serial number required for allocated storage")
    
    # Check if metal exists
    metal = db.query(Metal).filter(Metal.id == metal_id).first()
    if not metal:
        raise HTTPException(status_code=404, detail="Metal not found")

    # Create Deposit record
    new_deposit = Deposit(
        account_id=current_user.id,
        metal_id=metal_id,
        quantity_kg=quantity_kg,
        storage_type=storage_type,
        serial_number=serial_number,
        vault_location=vault_location
    )
    db.add(new_deposit)
    
    # Create Transaction record
    new_transaction = Transaction(
        account_id=current_user.id,
        metal_id=metal_id,
        type="DEPOSIT",
        quantity=quantity_kg
    )
    db.add(new_transaction)
    
    db.commit()
    db.refresh(new_deposit)
    
    # Dispatch real-time notification
    await dispatch_event(str(current_user.id), "NEW_DEPOSIT", {
        "deposit_id": str(new_deposit.id),
        "quantity": quantity_kg,
        "metal": metal.name
    })
    
    return new_deposit

@router.get("/history", response_model=List[Transaction])
async def get_transaction_history(
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    return db.query(Transaction).filter(Transaction.account_id == current_user.id).order_by(Transaction.created_at.desc()).all()
