from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship, declarative_base

from src.entities.enums import (
    RoleEnum,
    SprintStatusEnum,   
    TaskTypeEnum,
    PriorityEnum,
    CommentTypeEnum,
    AttachTypeEnum,
    NotificationTypeEnum,
    PlanningPokerStatusEnum
)

from src.entities.mixins import TimestampMixin

Base = declarative_base()
Base.metadata.schema = "public"




# =========================================================
# USER
# =========================================================

class User(Base, TimestampMixin):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)

    verified = Column(Boolean, nullable=False, default=False)

    # RELATIONSHIPS
    projects_created = relationship("Project", back_populates="creator")

    project_associations = relationship(
        "ProjectUser",
        back_populates="user"
    )

    tasks_created = relationship(
        "Task",
        back_populates="creator"
    )

    assigned_tasks = relationship(
        "UserTask",
        back_populates="user"
    )

    comments = relationship(
        "Comment",
        back_populates="user"
    )

    notifications = relationship(
        "Notification",
        back_populates="user"
    )

    planning_sessions = relationship(
        "PlanningPokerSession",
        back_populates="creator"
    )

    planning_votes = relationship(
        "PlanningPokerVote",
        back_populates="user"
    )

    notification_config = relationship(
        "NotificationConfig",
        back_populates="user",
        uselist=False
    )


# =========================================================
# PROJECT
# =========================================================

class Project(Base, TimestampMixin):
    __tablename__ = "project"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(255), nullable=False)
    description = Column(String(255))

    created_by = Column(
        Integer,
        ForeignKey("public.user.id"),
        nullable=False
    )

    code = Column(Integer, nullable=False, unique=True)

    # RELATIONSHIPS
    creator = relationship(
        "User",
        back_populates="projects_created"
    )

    users = relationship(
        "ProjectUser",
        back_populates="project"
    )

    sprints = relationship(
        "Sprint",
        back_populates="project"
    )

    columns = relationship(
        "BoardColumn",
        back_populates="project"
    )

    tasks = relationship(
        "Task",
        back_populates="project"
    )

    planning_sessions = relationship(
        "PlanningPokerSession",
        back_populates="project"
    )


# =========================================================
# PROJECT USER
# =========================================================

class ProjectUser(Base):
    __tablename__ = "project_user"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("public.user.id"),
        nullable=False
    )

    project_id = Column(
        Integer,
        ForeignKey("public.project.id"),
        nullable=False
    )

    role = Column(
        Enum(RoleEnum, name="role_t"),
        nullable=False
    )

    # RELATIONSHIPS
    user = relationship(
        "User",
        back_populates="project_associations"
    )

    project = relationship(
        "Project",
        back_populates="users"
    )


# =========================================================
# SPRINT
# =========================================================

class Sprint(Base):
    __tablename__ = "sprint"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(255), nullable=False)

    project_id = Column(
        Integer,
        ForeignKey("public.project.id"),
        nullable=False
    )

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    status = Column(
        Enum(SprintStatusEnum, name="status_t"),
        nullable=False
    )

    goal = Column(String(255))
    points = Column(Integer)

    # RELATIONSHIPS
    project = relationship(
        "Project",
        back_populates="sprints"
    )

    tasks = relationship(
        "Task",
        back_populates="sprint"
    )


# =========================================================
# BOARD COLUMN
# =========================================================

class BoardColumn(Base):
    __tablename__ = "board_column"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(255))

    order = Column(Integer)

    project_id = Column(
        Integer,
        ForeignKey("public.project.id")
    )

    # RELATIONSHIPS
    project = relationship(
        "Project",
        back_populates="columns"
    )

    tasks = relationship(
        "Task",
        back_populates="column"
    )


# =========================================================
# TASK
# =========================================================

class Task(Base, TimestampMixin):
    __tablename__ = "task"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String(255), nullable=False)
    description = Column(Text)

    type = Column(
        Enum(TaskTypeEnum, name="task_type_t"),
        nullable=False
    )

    priority = Column(
        Enum(PriorityEnum, name="priority_t"),
        nullable=False
    )

    column_id = Column(
        Integer,
        ForeignKey("public.board_column.id")
    )

    project_id = Column(
        Integer,
        ForeignKey("public.project.id"),
        nullable=False
    )

    sprint_id = Column(
        Integer,
        ForeignKey("public.sprint.id")
    )

    parent_id = Column(
        Integer,
        ForeignKey("public.task.id")
    )

    estimate = Column(DateTime)

    created_by = Column(
        Integer,
        ForeignKey("public.user.id"),
        nullable=False
    )

    points = Column(Integer)

    epic = Column(
        Integer,
        ForeignKey("public.task.id")
    )

    # RELATIONSHIPS
    column = relationship(
        "BoardColumn",
        back_populates="tasks"
    )

    project = relationship(
        "Project",
        back_populates="tasks"
    )

    sprint = relationship(
        "Sprint",
        back_populates="tasks"
    )

    creator = relationship(
        "User",
        back_populates="tasks_created"
    )

    parent_task = relationship(
        "Task",
        remote_side=[id],
        foreign_keys=[parent_id]
    )

    epic_task = relationship(
        "Task",
        remote_side=[id],
        foreign_keys=[epic]
    )

    dependencies = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.item_id",
        back_populates="task"
    )

    dependents = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.dependency_item_id",
        back_populates="dependency_task"
    )

    assigned_users = relationship(
        "UserTask",
        back_populates="task"
    )

    comments = relationship(
        "Comment",
        back_populates="task"
    )

    attachments = relationship(
        "Attach",
        back_populates="task"
    )

    planning_votes = relationship(
        "PlanningPokerVote",
        back_populates="task"
    )


# =========================================================
# TASK DEPENDENCY
# =========================================================

class TaskDependency(Base):
    __tablename__ = "task_dependency"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    item_id = Column(
        Integer,
        ForeignKey("public.task.id"),
        nullable=False
    )

    dependency_item_id = Column(
        Integer,
        ForeignKey("public.task.id"),
        nullable=False
    )

    # RELATIONSHIPS
    task = relationship(
        "Task",
        foreign_keys=[item_id],
        back_populates="dependencies"
    )

    dependency_task = relationship(
        "Task",
        foreign_keys=[dependency_item_id],
        back_populates="dependents"
    )


# =========================================================
# USER TASK
# =========================================================

class UserTask(Base):
    __tablename__ = "user_task"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("public.user.id")
    )

    item_id = Column(
        Integer,
        ForeignKey("public.task.id")
    )

    # RELATIONSHIPS
    user = relationship(
        "User",
        back_populates="assigned_tasks"
    )

    task = relationship(
        "Task",
        back_populates="assigned_users"
    )

    historicals = relationship(
        "Historical",
        back_populates="user_task"
    )


# =========================================================
# COMMENT
# =========================================================

class Comment(Base, TimestampMixin):
    __tablename__ = "comment"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    task_id = Column(
        Integer,
        ForeignKey("public.task.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("public.user.id"),
        nullable=False
    )

    content = Column(String(255), nullable=False)

    type = Column(
        Enum(CommentTypeEnum, name="comment_type_t")
    )

    # RELATIONSHIPS
    task = relationship(
        "Task",
        back_populates="comments"
    )

    user = relationship(
        "User",
        back_populates="comments"
    )


# =========================================================
# ATTACH
# =========================================================

class Attach(Base):
    __tablename__ = "attach"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    task_id = Column(
        Integer,
        ForeignKey("public.task.id"),
        nullable=False
    )

    url = Column(String(255), nullable=False)

    type = Column(
        Enum(AttachTypeEnum, name="attach_type_t"),
        nullable=False
    )

    # RELATIONSHIPS
    task = relationship(
        "Task",
        back_populates="attachments"
    )


# =========================================================
# NOTIFICATION
# =========================================================

class Notification(Base, TimestampMixin):
    __tablename__ = "notification"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("public.user.id"),
        nullable=False
    )

    type = Column(
        Enum(NotificationTypeEnum, name="notification_type_t"),
        nullable=False
    )

    message = Column(String(255), nullable=False)

    read = Column(Boolean, nullable=False, default=False)

    # RELATIONSHIPS
    user = relationship(
        "User",
        back_populates="notifications"
    )


# =========================================================
# NOTIFICATION CONFIG
# =========================================================

class NotificationConfig(Base):
    __tablename__ = "notification_config"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("public.user.id"),
        nullable=False
    )

    mention = Column(Boolean, nullable=False, default=True)
    late = Column(Boolean, nullable=False, default=True)
    blocked = Column(Boolean, nullable=False, default=True)

    # RELATIONSHIPS
    user = relationship(
        "User",
        back_populates="notification_config"
    )


# =========================================================
# PLANNING POKER SESSION
# =========================================================

class PlanningPokerSession(Base):
    __tablename__ = "planning_poker_session"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    project_id = Column(
        Integer,
        ForeignKey("public.project.id"),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("public.user.id"),
        nullable=False
    )

    status = Column(
        Enum(PlanningPokerStatusEnum, name="planning_poker_status_t"),
        nullable=False
    )

    # RELATIONSHIPS
    project = relationship(
        "Project",
        back_populates="planning_sessions"
    )

    creator = relationship(
        "User",
        back_populates="planning_sessions"
    )

    votes = relationship(
        "PlanningPokerVote",
        back_populates="session"
    )


# =========================================================
# PLANNING POKER VOTE
# =========================================================

class PlanningPokerVote(Base):
    __tablename__ = "planning_poker_vote"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    session_id = Column(
        Integer,
        ForeignKey("public.planning_poker_session.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("public.user.id"),
        nullable=False
    )

    item_id = Column(
        Integer,
        ForeignKey("public.task.id"),
        nullable=False
    )

    vote_value = Column(String(255), nullable=False)

    # RELATIONSHIPS
    session = relationship(
        "PlanningPokerSession",
        back_populates="votes"
    )

    user = relationship(
        "User",
        back_populates="planning_votes"
    )

    task = relationship(
        "Task",
        back_populates="planning_votes"
    )


# =========================================================
# HISTORICAL
# =========================================================

class Historical(Base):
    __tablename__ = "historical"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_item_id = Column(
        Integer,
        ForeignKey("public.user_task.id"),
        nullable=False
    )

    # RELATIONSHIPS
    user_task = relationship(
        "UserTask",
        back_populates="historicals"
    )


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

if __name__ == "__main__":
    from sqlalchemy import create_engine

    DATABASE_URL = (
        "postgresql+psycopg2://postgres:password@localhost:5432/mydb"
    )

    engine = create_engine(DATABASE_URL)

    Base.metadata.create_all(engine)

    print("Banco criado com sucesso.")