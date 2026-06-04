from sqlalchemy.orm import Session

from src.entities.models import Task
from src.entities.schemas import TaskCreate, TaskUpdate
from src.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, db: Session):
        self.repository = TaskRepository(db)

    def create_task(
        self,
        data: TaskCreate,
        created_by: int
    ) -> Task | None:
        return self.repository.create(data, created_by)

    def get_task(self, task_id: int) -> Task | None:
        return self.repository.get_by_id(task_id)

    def get_all_tasks(self) -> list[Task]:
        return self.repository.get_all()

    def get_tasks_by_project(
        self,
        project_id: int
    ) -> list[Task]:
        return self.repository.get_by_project(project_id)

    def get_tasks_by_sprint(
        self,
        sprint_id: int
    ) -> list[Task]:
        return self.repository.get_by_sprint(sprint_id)

    def get_tasks_by_column(
        self,
        column_id: int
    ) -> list[Task]:
        return self.repository.get_by_column(column_id)

    def update_task(
        self,
        task_id: int,
        data: TaskUpdate
    ) -> Task | None:
        return self.repository.update(task_id, data)

    def delete_task(
        self,
        task_id: int
    ) -> bool:
        return self.repository.delete(task_id)

    def save_task(
        self,
        task: Task
    ) -> Task:
        return self.repository.save(task)