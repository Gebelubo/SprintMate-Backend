from sqlalchemy.orm import Session

from src.entities.models import BoardColumn, Task
from src.entities.schemas import BoardColumnCreate, BoardColumnUpdate
from src.repositories.board_repository import BoardRepository
from src.repositories.task_repository import TaskRepository


class BoardService:
    def __init__(self, db: Session):
        self.repository = BoardRepository(db)
        self.task_repository = TaskRepository(db)

    def get_project_columns(self, project_id: int) -> list[BoardColumn]:
        return self.repository.get_by_project(project_id)

    def get_column(self, column_id: int) -> BoardColumn | None:
        return self.repository.get_by_id(column_id)

    def create_column(self, project_id: int, data: BoardColumnCreate) -> BoardColumn | None:
        return self.repository.create(project_id, data)

    def update_column(self, column_id: int, data: BoardColumnUpdate) -> BoardColumn | None:
        return self.repository.update(column_id, data)

    def delete_column(self, column_id: int) -> bool:
        return self.repository.delete(column_id)

    def get_column_tasks(self, column_id: int) -> list[Task]:
        return self.repository.get_tasks(column_id)

    def move_task(self, task_id: int, column_id: int) -> Task | None:
        task = self.task_repository.get_by_id(task_id)
        if not task:
            return None
        column = self.repository.get_by_id(column_id)
        if not column or column.project_id != task.project_id:
            return None
        task.column_id = column_id
        return self.repository.save(task)