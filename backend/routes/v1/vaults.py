from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from lib.database.main import get_session
from lib.database.models.vault import Vault
from lib.auth import get_current_user
from lib.database.models.account import Account

router = APIRouter(prefix="/api/v1/vaults", tags=["vaults v1"])

@router.get("/", response_model=List[Vault])
async def list_vaults(
    db: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user)
):
    return db.query(Vault).filter(Vault.status == "ACTIVE").all()
