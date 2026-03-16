from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FileCreate(BaseModel):
    filename: str
    content_type: Optional[str] = None
    size: int
    path: str

    model_config = ConfigDict(from_attributes=True)


class File(BaseModel):
    id: int
    user_id: int
    filename: str
    content_type: Optional[str] = None
    size: int
    path: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
