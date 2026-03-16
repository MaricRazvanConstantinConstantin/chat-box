from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(default='', min_length=5, max_length=100)
    avatar_url: str = Field(default='')
    password_hash: str = Field(min_length=8)

    model_config = ConfigDict(from_attributes = True)


class User(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)
