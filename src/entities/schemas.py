from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import datetime
import re


# ------------- USER ----------------

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

# ------------ TAKSKS -----------------

from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from src.entities.models import TaskTypeEnum, PriorityEnum


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

    type: TaskTypeEnum
    priority: PriorityEnum

    column_id: Optional[int] = None
    project_id: int
    sprint_id: Optional[int] = None

    parent_id: Optional[int] = None
    epic: Optional[int] = None

    estimate: Optional[datetime] = None
    points: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    type: Optional[TaskTypeEnum] = None
    priority: Optional[PriorityEnum] = None

    column_id: Optional[int] = None
    project_id: Optional[int] = None
    sprint_id: Optional[int] = None

    parent_id: Optional[int] = None
    epic: Optional[int] = None

    estimate: Optional[datetime] = None
    points: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    created_by: int

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

from pydantic import BaseModel


class NotificationConfigResponse(BaseModel):
    id: int
    user_id: int

    mention: bool
    late: bool
    blocked: bool

    model_config = {
        "from_attributes": True
    }


class NotificationConfigUpdate(BaseModel):
    mention: bool | None = None
    late: bool | None = None
    blocked: bool | None = None

# --------------- PROJECT -------------------

from src.entities.enums import RoleEnum

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    code: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# ---------- PROJECT USER ----------------

class ProjectUserAdd(BaseModel):
    user_id: int
    role: RoleEnum

class ProjectUserUpdateRole(BaseModel):
    role: RoleEnum

class ProjectUserResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    role: RoleEnum

    model_config = {"from_attributes": True}