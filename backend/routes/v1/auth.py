from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from lib.database.main import get_session
from lib.database.models.account import Account, AccountType
from lib.database.models.schemas import UserCreate, UserLogin, Token, PasswordResetRequest, PasswordResetConfirm
from lib.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from lib.logger import logger
from jose import jwt, JWTError

router = APIRouter(prefix="/api/v1/auth", tags=["auth v1"])

@router.post("/register", response_model=Account)
async def register(user: UserCreate, db: Session = Depends(get_session)):
    logger.debug(f"Registration attempt for email: {user.email}")
    db_user = db.query(Account).filter(Account.email == user.email).first()
    if db_user:
        logger.warning(f"Registration failed: Email {user.email} already exists.")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if this is the first user to register
    user_count = db.query(Account).count()
    account_type = AccountType.ADMIN if user_count == 0 else AccountType.CUSTOMER
    
    hashed_password = get_password_hash(user.password)
    new_user = Account(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        type=account_type
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_session)):
    user = db.query(Account).filter(Account.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/password-reset-request")
async def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_session)):
    user = db.query(Account).filter(Account.email == request.email).first()
    if not user:
        # Don't reveal if user exists for security, but for our prototype we can be simple
        return {"message": "If the account exists, a reset link has been sent."}
    
    # Generate a short-lived reset token
    reset_token = create_access_token(
        data={"sub": user.email, "purpose": "password_reset"}, 
        expires_delta=timedelta(minutes=10)
    )
    
    # In a real app, send email. Here, we just return it for the prototype.
    return {
        "message": "Password reset token generated (mock email sent)",
        "reset_token": reset_token
    }

@router.post("/password-reset-confirm")
async def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        purpose: str = payload.get("purpose")
        if email is None or purpose != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user = db.query(Account).filter(Account.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = get_password_hash(request.new_password)
    db.add(user)
    db.commit()
    
    return {"message": "Password has been successfully reset"}

@router.post("/verify-otp")
async def verify_otp(otp_data: dict, db: Session = Depends(get_session)):
    # Mock OTP verification for prototype
    otp = otp_data.get("otp")
    if otp == "123456":
        return {"message": "OTP verified successfully"}
    raise HTTPException(status_code=400, detail="Invalid OTP code")
