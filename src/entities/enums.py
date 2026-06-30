import enum

# =========================================================
# ENUMS
# =========================================================

class RoleEnum(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    DEV = "dev"


class SprintStatusEnum(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class TaskTypeEnum(enum.Enum):
    TASK = "TASK"
    BUG = "BUG"
    STORY = "STORY"
    EPIC = "EPIC"


class PriorityEnum(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CommentTypeEnum(enum.Enum):
    COMMENT = "COMMENT"
    SYSTEM = "SYSTEM"


class AttachTypeEnum(enum.Enum):
    IMAGE = "IMAGE"
    FILE = "FILE"
    LINK = "LINK"


class NotificationTypeEnum(enum.Enum):
    MENTION = "MENTION"
    LATE = "LATE"
    BLOCKED = "BLOCKED"


class PlanningPokerStatusEnum(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

