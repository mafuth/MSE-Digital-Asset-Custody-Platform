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
from lib.database.models.enums import TransactionType, StorageType, RequestStatus, TransactionStatus
from lib.database.models.schemas import TransactionRead, TransactionCreate, RequestRead

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions V1"])

@router.post("/deposit", response_model=RequestRead)
async def create_deposit_request(
    data: TransactionCreate,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    from lib.database.models.request import Request
    from lib.database.models.vault import Vault
    
    if data.storage_type == StorageType.ALLOCATED:
        if not data.serial_number and not data.serial_numbers:
            raise HTTPException(status_code=400, detail="Serial number(s) required for allocated storage")
        
        # Normalize to strip but preserve user case
        if data.serial_numbers:
            data.serial_numbers = [sn.strip() for sn in data.serial_numbers]
            if any(not sn for sn in data.serial_numbers):
                raise HTTPException(status_code=400, detail="All serial numbers must be non-empty for allocated storage")
        
        if data.serial_number:
            data.serial_number = data.serial_number.strip()
            if not data.serial_number:
                raise HTTPException(status_code=400, detail="Serial number cannot be empty for allocated storage")
    
    # Check if metal exists
    metal = db.query(Metal).filter(Metal.id == data.metal_id).first()
    if not metal:
        raise HTTPException(status_code=404, detail="Metal not found")

    # Check vault exists
    vault = db.query(Vault).filter(Vault.id == data.vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")

    # Create Request(s)
    requests_to_create = []
    
    if data.storage_type == StorageType.ALLOCATED and data.serial_numbers:
        for sn in data.serial_numbers:
            new_request = Request(
                account_id=current_user.id,
                metal_id=data.metal_id,
                vault_id=data.vault_id,
                type=TransactionType.DEPOSIT,
                quantity_kg=metal.bar_kg if metal.bar_kg > 0 else (data.quantity_kg / len(data.serial_numbers)),
                storage_type=data.storage_type,
                serial_number=sn,
                status=RequestStatus.PENDING
            )
            requests_to_create.append(new_request)
    else:
        new_request = Request(
            account_id=current_user.id,
            metal_id=data.metal_id,
            vault_id=data.vault_id,
            type=TransactionType.DEPOSIT,
            quantity_kg=data.quantity_kg,
            storage_type=data.storage_type,
            serial_number=data.serial_number,
            status=RequestStatus.PENDING
        )
        requests_to_create.append(new_request)

    for req in requests_to_create:
        db.add(req)
        # Create a matching pending Transaction record
        new_tx = Transaction(
            account_id=req.account_id,
            metal_id=req.metal_id,
            vault_id=req.vault_id,
            bar_ref_id=req.serial_number,
            type=req.type,
            quantity=req.quantity_kg,
            status=TransactionStatus.PENDING
        )
        db.add(new_tx)
        db.flush() # Get transaction ID
        req.transaction_id = new_tx.id
    
    db.commit()
    for req in requests_to_create:
        db.refresh(req)
    
    # Return the first one or a summary if needed, for now just the first
    return requests_to_create[0]

@router.get("/history", response_model=List[TransactionRead])
async def get_transaction_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    query = db.query(Transaction).options(joinedload(Transaction.metal), joinedload(Transaction.vault)).filter(Transaction.account_id == current_user.id)
    
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
        
    return query.order_by(Transaction.created_at.desc()).all()

@router.post("/withdraw", response_model=RequestRead)
async def create_withdrawal_request(
    data: TransactionCreate,
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    from lib.database.models.request import Request
    
    # Check if metal exists
    metal = db.query(Metal).filter(Metal.id == data.metal_id).first()
    if not metal:
        raise HTTPException(status_code=404, detail="Metal not found")

    if data.storage_type == StorageType.ALLOCATED:
        if not data.serial_number and not data.serial_numbers:
            raise HTTPException(status_code=400, detail="Serial number(s) required for allocated storage")
            
        # Normalize to strip but preserve user case (case-insensitive check follows)
        if data.serial_numbers:
            data.serial_numbers = [sn.strip() for sn in data.serial_numbers]
            if any(not sn for sn in data.serial_numbers):
                raise HTTPException(status_code=400, detail="All serial numbers must be non-empty for allocated storage")
        
        if data.serial_number:
            data.serial_number = data.serial_number.strip()
            if not data.serial_number:
                raise HTTPException(status_code=400, detail="Serial number cannot be empty for allocated storage")

    # Ownership & Balance Validation
    deposits = db.query(Deposit).filter(
        Deposit.account_id == current_user.id,
        Deposit.metal_id == data.metal_id,
        Deposit.vault_id == data.vault_id
    ).all()
    
    pending_withdrawals = db.query(Request).filter(
        Request.account_id == current_user.id,
        Request.metal_id == data.metal_id,
        Request.vault_id == data.vault_id,
        Request.type == TransactionType.WITHDRAWAL,
        Request.status == RequestStatus.PENDING
    ).all()

    if data.storage_type == StorageType.UNALLOCATED:
        current_unallocated = sum(d.quantity_kg for d in deposits if d.storage_type == StorageType.UNALLOCATED)
        pending_unallocated = sum(r.quantity_kg for r in pending_withdrawals if r.storage_type == StorageType.UNALLOCATED)
        available = current_unallocated - pending_unallocated
        if data.quantity_kg > available:
            raise HTTPException(status_code=400, detail=f"Insufficient unallocated balance. Available: {available:.3f}kg")

    from sqlalchemy import func
    if data.storage_type == StorageType.ALLOCATED:
        serials_to_check = data.serial_numbers if data.serial_numbers else ([data.serial_number] if data.serial_number else [])
        
        for sn in serials_to_check:
            # Case-insensitive direct query for ownership in this specific vault
            asset_exists = db.query(Deposit).filter(
                Deposit.account_id == current_user.id,
                Deposit.metal_id == metal.id,
                Deposit.vault_id == data.vault_id,
                Deposit.storage_type == StorageType.ALLOCATED,
                Deposit.serial_number == sn
            ).first()

            if not asset_exists:
                raise HTTPException(status_code=400, detail=f"Asset not found in your portfolio at this facility: {sn}")

            # Case-insensitive direct query for pending withdrawals
            withdrawal_pending = db.query(Request).filter(
                Request.account_id == current_user.id,
                Request.metal_id == metal.id,
                Request.vault_id == data.vault_id,
                Request.type == TransactionType.WITHDRAWAL,
                Request.status == RequestStatus.PENDING,
                func.lower(Request.serial_number) == sn.lower()
            ).first()

            if withdrawal_pending:
                raise HTTPException(status_code=400, detail=f"Withdrawal already pending for asset: {sn}")

    # Create Request(s)
    requests_to_create = []
    
    if data.storage_type == StorageType.ALLOCATED and data.serial_numbers:
        for sn in data.serial_numbers:
            new_request = Request(
                account_id=current_user.id,
                metal_id=data.metal_id,
                vault_id=data.vault_id,
                type=TransactionType.WITHDRAWAL,
                quantity_kg=metal.bar_kg if metal.bar_kg > 0 else (data.quantity_kg / len(data.serial_numbers)),
                storage_type=data.storage_type,
                serial_number=sn,
                status=RequestStatus.PENDING
            )
            requests_to_create.append(new_request)
    else:
        new_request = Request(
            account_id=current_user.id,
            metal_id=data.metal_id,
            vault_id=data.vault_id,
            type=TransactionType.WITHDRAWAL,
            quantity_kg=data.quantity_kg,
            storage_type=data.storage_type,
            serial_number=data.serial_number,
            status=RequestStatus.PENDING
        )
        requests_to_create.append(new_request)

    for req in requests_to_create:
        db.add(req)
        # Create a matching pending Transaction record
        new_tx = Transaction(
            account_id=req.account_id,
            metal_id=req.metal_id,
            vault_id=req.vault_id,
            bar_ref_id=req.serial_number,
            type=req.type,
            quantity=req.quantity_kg,
            status=TransactionStatus.PENDING
        )
        db.add(new_tx)
        db.flush() # Get transaction ID
        req.transaction_id = new_tx.id
    
    db.commit()
    for req in requests_to_create:
        db.refresh(req)
    
    return requests_to_create[0]
