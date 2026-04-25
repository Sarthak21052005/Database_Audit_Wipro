from pydantic import BaseModel , Field
from typing import Optional, Dict
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str = Field(... , max_length= 72)
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AuditLogResponse(BaseModel):
    id: int
    table_name: str
    operation: str
    old_data: Optional[Dict]
    new_data: Optional[Dict]
    timestamp : datetime

    class Config:
        from_attributes = True