from pydantic import BaseModel, ConfigDict, field_validator, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
import re
from src.entities.models import SprintStatusEnum

from src.entities.models import TaskTypeEnum, PriorityEnum


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


class TaskCreate(BaseModel):
    title: str
    type: TaskTypeEnum
    priority: PriorityEnum
    project_id: int
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    type: Optional[TaskTypeEnum] = None
    priority: Optional[PriorityEnum] = None

    column_id: Optional[int] = None
    project_id: Optional[int] = None
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None

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

from src.entities.enums import AttachTypeEnum, CommentTypeEnum, RoleEnum

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
class SprintCreate(BaseModel):
    name: str
    project_id: int
    start_date: date
    end_date: date

class SprintCreate(BaseModel):
    name: str
    project_id: int
    start_date: date
    end_date: date

class SprintProjectCreate(BaseModel):
    name: str
    start_date: date
    end_date: date


class SprintUpdate(BaseModel):
    name: str | None = None
    project_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: SprintStatusEnum | None = None
    goal: str | None = None
    points: int | None = None

class SprintResponse(BaseModel):
    id: int
    name: str
    project_id: int
    start_date: date
    end_date: date
    status: SprintStatusEnum
    goal: str | None
    points: int | None

class SprintDatesResponse(BaseModel):
    id: int
    start_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)

class ProjectWithRoleResponse(ProjectResponse):
    role: RoleEnum

class CommentCreate(BaseModel):
    content: str
    type: Optional[CommentTypeEnum] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    type: Optional[CommentTypeEnum] = None


class CommentResponse(BaseModel):
    id: int

    task_id: int
    user_id: int

    content: str
    type: Optional[CommentTypeEnum]

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class AttachmentCreate(BaseModel):
    url: str
    type: AttachTypeEnum


class AttachmentResponse(BaseModel):
    id: int

    task_id: int

    url: str
    type: AttachTypeEnum

    model_config = {
        "from_attributes": True
    }

# ----------- BOARD COLUMN ----------------

class BoardColumnCreate(BaseModel):
    name: str
    order: int = 0

class BoardColumnUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None

class BoardColumnResponse(BaseModel):
    id: int
    name: Optional[str]
    order: Optional[int]
    project_id: Optional[int]

    model_config = {"from_attributes": True}

class TaskMoveRequest(BaseModel):
    column_id: int

class ProjectUserResponseWithUser(BaseModel):
    id: int
    user_id: int
    user_name: str
    email: str
    project_id: int
    role: RoleEnum


class ProjectInvite(BaseModel):
    email: str

class UserTaskCreate(BaseModel):
    user_id: int
    task_id: int

class UserTaskResponse(BaseModel):
    id: int
    user_id: int
    item_id: int 

    model_config = ConfigDict(from_attributes=True)

# ----------- PLANNING POKER SESSION ----------------

from src.entities.enums import PlanningPokerStatusEnum

class PlanningPokerSessionResponse(BaseModel):
    id: int
    project_id: int
    created_by_id: int = Field(alias="created_by")
    status: PlanningPokerStatusEnum

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ----------- PLANNING POKER VOTE ----------------

PLANNING_POKER_CARDS: list[str] = [
    "0", "1", "2", "3", "5", "8", "13", "21", "34", "55", "89", "?", "BREAK",
]


class PlanningPokerVoteCreate(BaseModel):
    item_id: int
    vote_value: str

    @field_validator("vote_value")
    @classmethod
    def vote_value_must_be_valid_card(cls, v):
        if v not in PLANNING_POKER_CARDS:
            raise ValueError(
                f"Invalid vote_value. Allowed cards: {PLANNING_POKER_CARDS}"
            )
        return v


class PlanningPokerVoteResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    item_id: int
    vote_value: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class PlanningPokerCardsResponse(BaseModel):
    cards: list[str]


class PlanningPokerResultResponse(BaseModel):
    session_id: int
    item_id: int
    votes: list[PlanningPokerVoteResponse]
    average: Optional[float]
    final_estimate: Optional[str]

class PlanningPokerInviteSchema(BaseModel):
    emails: list[str]