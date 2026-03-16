import re

from fastapi import APIRouter, Depends

from api.deps import get_current_user
from models.User import User

router = APIRouter(tags=["core"])


@router.get("/", response_model=dict, status_code=200)
def read_root():
    return {"message": "Welcome to the ChatBox API!"}


@router.get("/health", response_model=dict, status_code=200)
def health_check():
    return {"status": "ok"}


@router.get("/me", response_model=User, status_code=200)
def read_me(current_user = Depends(get_current_user)):
    return User.model_validate(current_user)
