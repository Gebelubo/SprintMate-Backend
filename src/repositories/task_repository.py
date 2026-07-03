from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.entities.models import Task, User
from src.entities.schemas import TaskCreate, TaskUpdate
from src.repositories.user_repository import UserRepository



class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        data: TaskCreate,
        created_by: int
    ) -> Task | None:

        task = Task(
            title=data.title,
            type=data.type,
            priority=data.priority,
            project_id=data.project_id,
            responsible_user_id=data.assignee_id,
            created_by=created_by
        )

        self.db.add(task)

        try:
            self.db.commit()
            self.db.refresh(task)
        except IntegrityError:
            self.db.rollback()
            return None

        return task

    def get_by_id(self, task_id: int) -> Task | None:
        return (
            self.db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )

    def get_all(self) -> list[Task]:
        return self.db.query(Task).all()

    def get_by_project(self, project_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id)
            .all()
        )

    def get_by_sprint(self, sprint_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .filter(Task.sprint_id == sprint_id)
            .all()
        )

    def get_by_column(self, column_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .filter(Task.column_id == column_id)
            .all()
        )

    def update(
        self,
        task_id: int,
        data: TaskUpdate
    ) -> Task | None:

        task = self.get_by_id(task_id)

        if not task:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(task)
        except IntegrityError:
            self.db.rollback()
            return None

        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)

        if not task:
            return False

        self.db.delete(task)
        self.db.commit()

        return True

    def save(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task
