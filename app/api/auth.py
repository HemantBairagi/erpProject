from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.security import get_password_hash , authenticate_user , oauth2_scheme , verify_password , create_access_token
from app.db.db import get_db
from app.schema.user_schema import LoginRequest, RegisterRequest, TokenResponse, UserOut, UserShort
from app.models.User import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = "CHANGE_ME_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8 




def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserOut, summary="Register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=payload.name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        phone=payload.phone,
        is_active=True,
        is_superuser=False,
        failed_login_attempts=0,
        password_changed_at=datetime.utcnow(),
        preferences={},  # avoid mutable default issue
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


MAX_FAILED_ATTEMPTS = 5
LOCK_TIME_MINUTES = 15


@router.post("/login", response_model=TokenResponse, summary="Login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=403,
            detail=f"Account locked until {user.locked_until}",
        )

    # Check password
    if not verify_password(payload.password, user.password_hash):
        user.failed_login_attempts += 1

        # Lock account if too many attempts
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_TIME_MINUTES)
            user.failed_login_attempts = 0

        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if inactive
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    # Successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token(
        {"sub": str(user.id), "role": user.role.value},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=token,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut, summary="Current user")
def current_user(user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return user


@router.post("/logout", summary="Logout")
def logout():
    """
    Client-side logout – invalidate the token on the client.
    For server-side invalidation, implement a token blacklist.
    """
    return {"message": "Logged out successfully"}
