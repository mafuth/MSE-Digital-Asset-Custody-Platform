from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from lib.database.main import get_session
from lib.database.models.transaction import Transaction
from lib.database.models.deposit import Deposit
from lib.database.models.account import Account
from lib.database.models.metal import Metal
from lib.auth import get_current_user
from lib.events import dispatch_event
from lib.database.models.schemas import TransactionRead, TransactionCreate

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions V1"])

@router.post("/deposit", response_model=Deposit)
async def create_deposit(
    data: TransactionCreate,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    from lib.database.models.vault import Vault
    if data.storage_type == "ALLOCATED" and not data.serial_number:
        raise HTTPException(status_code=400, detail="Serial number required for allocated storage")
    
    # Check if metal exists
    metal = db.query(Metal).filter(Metal.id == data.metal_id).first()
    if not metal:
        raise HTTPException(status_code=404, detail="Metal not found")

    # Check vault capacity
    vault = db.query(Vault).filter(Vault.id == data.vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
        
    if vault.current_load_kg + data.quantity_kg > vault.capacity_kg:
        raise HTTPException(status_code=400, detail=f"Insufficient capacity in vault {vault.name}. Available: {vault.capacity_kg - vault.current_load_kg}kg")

    # Create Deposit record
    new_deposit = Deposit(
        account_id=current_user.id,
        metal_id=data.metal_id,
        vault_id=data.vault_id,
        quantity_kg=data.quantity_kg,
        storage_type=data.storage_type,
        serial_number=data.serial_number
    )
    db.add(new_deposit)
    
    # Update vault load
    vault.current_load_kg += data.quantity_kg
    db.add(vault)
    
    # Create Transaction record
    new_transaction = Transaction(
        account_id=current_user.id,
        metal_id=data.metal_id,
        type="DEPOSIT",
        quantity=data.quantity_kg
    )
    db.add(new_transaction)
    
    db.commit()
    db.refresh(new_deposit)
    
    # Dispatch real-time notification
    await dispatch_event(str(current_user.id), "NEW_DEPOSIT", {
        "deposit_id": str(new_deposit.id),
        "quantity": data.quantity_kg,
        "metal": metal.name,
        "vault": vault.name
    })
    
    return new_deposit

@router.get("/history", response_model=List[TransactionRead])
async def get_transaction_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    query = db.query(Transaction).options(joinedload(Transaction.metal)).filter(Transaction.account_id == current_user.id)
    
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
        
    return query.order_by(Transaction.created_at.desc()).all()

@router.post("/withdraw", response_model=TransactionRead)
async def create_withdrawal(
    data: TransactionCreate, # Changed from query params
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    from lib.database.models.vault import Vault
    
    # Check if metal exists
    metal = db.query(Metal).filter(Metal.id == data.metal_id).first()
    if not metal:
        raise HTTPException(status_code=404, detail="Metal not found")

    # Check vault
    vault = db.query(Vault).filter(Vault.id == data.vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")

    # Find deposits for this user, metal, vault, and storage type
    query = db.query(Deposit).filter(
        Deposit.account_id == current_user.id,
        Deposit.metal_id == data.metal_id,
        Deposit.vault_id == data.vault_id,
        Deposit.storage_type == data.storage_type
    )

    if data.storage_type == "ALLOCATED":
        if not data.serial_number:
            raise HTTPException(status_code=400, detail="Serial number (Bar Ref ID) required for allocated withdrawal")
        query = query.filter(Deposit.serial_number == data.serial_number)

    deposits = query.all()
    
    total_available = sum(d.quantity_kg for d in deposits)
    if total_available < data.quantity_kg:
        raise HTTPException(status_code=400, detail=f"Insufficient {metal.name} in {data.storage_type} storage. Available: {total_available}kg")

    # Deduct from deposits (FIFO approach)
    remaining_to_withdraw = data.quantity_kg
    for deposit in deposits:
        if remaining_to_withdraw <= 0:
            break
        if deposit.quantity_kg <= remaining_to_withdraw:
            remaining_to_withdraw -= deposit.quantity_kg
            db.delete(deposit)
        else:
            deposit.quantity_kg -= remaining_to_withdraw
            remaining_to_withdraw = 0
            db.add(deposit)

    # Update vault load
    vault.current_load_kg -= data.quantity_kg
    db.add(vault)
    
    # Create Transaction record
    new_transaction = Transaction(
        account_id=current_user.id,
        metal_id=data.metal_id,
        type="WITHDRAWAL",
        quantity=data.quantity_kg,
        status="COMPLETED"
    )
    db.add(new_transaction)
    
    db.commit()
    db.refresh(new_transaction)
    
    # Dispatch real-time notification
    await dispatch_event(str(current_user.id), "NEW_WITHDRAWAL", {
        "transaction_id": str(new_transaction.id),
        "quantity": data.quantity_kg,
        "metal": metal.name,
        "vault": vault.name
    })
    
    return new_transaction
