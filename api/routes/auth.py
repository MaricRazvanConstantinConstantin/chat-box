from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.database import get_db
from db.models import UserRecord
from models.User import User, UserCreate
from api.services.auth import AuthService, get_auth_service


router = APIRouter(prefix="/auth", tags=["auth"])

class TokenResponse(BaseModel):
    access_token: str
    user: User

class LoginPayload(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginPayload, db: Session = Depends(get_db), auth_service: AuthService = Depends(get_auth_service)):
    stmt = select(UserRecord).where(UserRecord.email == payload.email)
    user_rec = db.execute(stmt).scalar_one_or_none()
    if not user_rec:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    try:
        if not auth_service.verify_password(payload.password, user_rec.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication error")

    user = User.model_validate(user_rec)
    try:
        access_token = auth_service.create_access_token(data={"sub": str(user.id), "email": user.email})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create access token")
    return TokenResponse(access_token=access_token, user=user)

@router.post("/sign-up", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def register(payload: UserCreate, db = Depends(get_db), auth_service: AuthService = Depends(get_auth_service)):

    stmt = select(UserRecord).where(UserRecord.email == payload.email)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    hashed_password = auth_service.hash_password(payload.password_hash)

    new_user = UserRecord(email=payload.email, name=payload.name, password_hash=hashed_password, avatar_url=payload.avatar_url)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

    user = User.model_validate(new_user)

    try:
        access_token = auth_service.create_access_token(data={"sub": str(user.id), "email": user.email})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create access token")

    return TokenResponse(access_token=access_token, user=user)
