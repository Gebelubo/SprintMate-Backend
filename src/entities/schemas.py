from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import datetime
import re
from src.entities.models import SprintStatusEnum


# =========================================================
# USER SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v):
        pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.com$"
        if not re.match(pattern, v):
            raise ValueError("Email must be lowercase and end with .com")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v):
        if v is None:
            return v
        pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.com$"
        if not re.match(pattern, v):
            raise ValueError("Email must be lowercase and end with .com")
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    verified: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class EmailRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class SprintCreate(BaseModel):
    name: str
    project_id: int
    start_date: datetime
    end_date: datetime
    status: SprintStatusEnum
    goal: str | None = None
    points: int | None = None


class SprintUpdate(BaseModel):
    name: str | None = None
    project_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: SprintStatusEnum | None = None
    goal: str | None = None
    points: int | None = None
