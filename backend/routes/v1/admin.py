from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel as PydanticBaseModel
from lib.database.main import get_session
from lib.database.models.account import Account
from lib.database.models.enums import AccountType, AccountStatus, VaultStatus, TransactionType, TransactionStatus, StorageType, RequestStatus
from lib.database.models.metal import Metal
from lib.database.models.deposit import Deposit
from lib.database.models.vault import Vault
from lib.database.models.request import Request
from lib.database.models.transaction import Transaction
from lib.database.models.schemas import RequestRead
from lib.auth import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["admin v1"])

class AccountUpdate(PydanticBaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    type: Optional[AccountType] = None
    status: Optional[AccountStatus] = None

class VaultCreate(PydanticBaseModel):
    name: str
    location: str
    capacity_kg: float
    status: Optional[VaultStatus] = VaultStatus.ACTIVE

class VaultUpdate(PydanticBaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity_kg: Optional[float] = None
    status: Optional[VaultStatus] = None

class MetalUpdate(PydanticBaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None
    current_price_kg: Optional[float] = None
    bar_kg: Optional[float] = None

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

@router.patch("/metals/{metal_id}", response_model=Metal)
async def update_metal(
    metal_id: UUID, 
    update_data: MetalUpdate,
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    metal = db.query(Metal).filter(Metal.id == metal_id).first()
    if not metal:
        raise HTTPException(status_code=404, detail="Metal not found")
        
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(metal, key, value)
            
    db.add(metal)
    db.commit()
    db.refresh(metal)
    return metal

@router.get("/accounts", response_model=List[Account])
async def list_accounts(
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    return db.query(Account).all()

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
                "price_per_kg": metal.current_price_kg,
                "breakdown": {
                    "ALLOCATED": {"quantity": 0.0, "bars": []},
                    "UNALLOCATED": {"quantity": 0.0}
                }
            }
        
        portfolio[metal.code]["quantity"] += deposit.quantity_kg
        current_val = deposit.quantity_kg * metal.current_price_kg
        portfolio[metal.code]["valuation"] += current_val
        total_valuation += current_val

        if deposit.storage_type == StorageType.ALLOCATED:
            portfolio[metal.code]["breakdown"]["ALLOCATED"]["quantity"] += deposit.quantity_kg
            portfolio[metal.code]["breakdown"]["ALLOCATED"]["bars"].append({
                "serial": deposit.serial_number,
                "weight": deposit.quantity_kg,
                "vault": deposit.vault.name if deposit.vault else "Unknown"
            })
        else:
            portfolio[metal.code]["breakdown"]["UNALLOCATED"]["quantity"] += deposit.quantity_kg
        
    return {
        "account": {
            "id": str(account.id),
            "name": account.name,
            "email": account.email
        },
        "assets": portfolio,
        "total_valuation": total_valuation
    }

@router.post("/vaults", response_model=Vault)
async def create_vault(
    vault_data: VaultCreate, 
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    # Check if vault already exists
    existing = db.query(Vault).filter(Vault.name == vault_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vault with this name already exists")
    
    vault = Vault(**vault_data.model_dump())
    db.add(vault)
    db.commit()
    db.refresh(vault)
    return vault

@router.patch("/vaults/{vault_id}", response_model=Vault)
async def update_vault(
    vault_id: UUID, 
    update_data: VaultUpdate,
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    vault = db.query(Vault).filter(Vault.id == vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
        
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(vault, key, value)
            
    db.add(vault)
    db.commit()
    db.refresh(vault)
    return vault

@router.get("/requests", response_model=List[RequestRead])
async def list_pending_requests(
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    return db.query(Request).filter(Request.status == RequestStatus.PENDING).all()

@router.post("/requests/{request_id}/approve")
async def approve_request(
    request_id: UUID,
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request is already processed")
    
    # Process the request
    if req.type == TransactionType.DEPOSIT:
        # Check vault capacity
        vault = db.query(Vault).filter(Vault.id == req.vault_id).first()
        if not vault:
            req.status = RequestStatus.REJECTED
            db.add(req)
            db.commit()
            raise HTTPException(status_code=404, detail="Vault not found")
            
        if vault.current_load_kg + req.quantity_kg > vault.capacity_kg:
            req.status = RequestStatus.REJECTED
            db.add(req)
            db.commit()
            raise HTTPException(status_code=400, detail="Insufficient vault capacity")

        # Create/Update Deposit
        existing_deposit = db.query(Deposit).filter(
            Deposit.account_id == req.account_id,
            Deposit.metal_id == req.metal_id,
            Deposit.vault_id == req.vault_id,
            Deposit.storage_type == req.storage_type,
            Deposit.serial_number == req.serial_number
        ).first()

        if existing_deposit:
            existing_deposit.quantity_kg += req.quantity_kg
            db.add(existing_deposit)
        else:
            new_deposit = Deposit(
                account_id=req.account_id,
                metal_id=req.metal_id,
                vault_id=req.vault_id,
                quantity_kg=req.quantity_kg,
                storage_type=req.storage_type,
                serial_number=req.serial_number
            )
            db.add(new_deposit)

        # Update Vault Load
        vault.current_load_kg += req.quantity_kg
        db.add(vault)

    elif req.type == TransactionType.WITHDRAWAL:
        # Check availability
        query = db.query(Deposit).filter(
            Deposit.account_id == req.account_id,
            Deposit.metal_id == req.metal_id,
            Deposit.vault_id == req.vault_id,
            Deposit.storage_type == req.storage_type
        )
        if req.storage_type == StorageType.ALLOCATED:
            query = query.filter(Deposit.serial_number == req.serial_number)
        
        deposits = query.all()
        total_available = sum(d.quantity_kg for d in deposits)
        
        if total_available < req.quantity_kg:
            req.status = RequestStatus.REJECTED
            db.add(req)
            db.commit()
            raise HTTPException(status_code=400, detail="Insufficient quantity for withdrawal")

        # Deduct from deposits (FIFO)
        remaining = req.quantity_kg
        for d in deposits:
            if remaining <= 0: break
            if d.quantity_kg <= remaining:
                remaining -= d.quantity_kg
                db.delete(d)
            else:
                d.quantity_kg -= remaining
                remaining = 0
                db.add(d)
        
        # Update Vault Load
        vault = db.query(Vault).filter(Vault.id == req.vault_id).first()
        if vault:
            vault.current_load_kg -= req.quantity_kg
            db.add(vault)

    # Update linked Transaction Status
    if req.transaction_id:
        tx = db.query(Transaction).filter(Transaction.id == req.transaction_id).first()
        if tx:
            tx.status = TransactionStatus.COMPLETED
            db.add(tx)

    # Update Request Status
    req.status = RequestStatus.APPROVED
    db.add(req)
    
    db.commit()
    return {"status": "success", "request_id": str(req.id)}

@router.post("/requests/{request_id}/reject")
async def reject_request(
    request_id: UUID,
    db: Session = Depends(get_session),
    _: Account = Depends(require_admin)
):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request is already processed")
        
    req.status = RequestStatus.REJECTED
    
    # Update linked Transaction Status
    if req.transaction_id:
        tx = db.query(Transaction).filter(Transaction.id == req.transaction_id).first()
        if tx:
            tx.status = TransactionStatus.REJECTED
            db.add(tx)
            
    db.add(req)
    db.commit()
    return {"status": "rejected"}
