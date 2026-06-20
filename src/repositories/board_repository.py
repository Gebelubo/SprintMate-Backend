from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.entities.models import BoardColumn, Task
from src.entities.schemas import BoardColumnCreate, BoardColumnUpdate

class BoardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_project(self, project_id: int) -> list[BoardColumn]:
        return (
            self.db.query(BoardColumn)
            .filter(BoardColumn.project_id == project_id)
            .order_by(BoardColumn.order)
            .all()
        )

    def get_by_id(self, column_id: int) -> BoardColumn | None:
        return (
            self.db.query(BoardColumn)
            .filter(BoardColumn.id == column_id)
            .first()
        )

    def create(self, project_id: int, data: BoardColumnCreate) -> BoardColumn | None:
        column = BoardColumn(
            project_id=project_id,
            name=data.name,
            order=data.order,
        )
        self.db.add(column)
        try:
            self.db.commit()
            self.db.refresh(column)
        except IntegrityError:
            self.db.rollback()
            return None
        return column

    def update(self, column_id: int, data: BoardColumnUpdate) -> BoardColumn | None:
        column = self.get_by_id(column_id)
        if not column:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(column, field, value)
        try:
            self.db.commit()
            self.db.refresh(column)
        except IntegrityError:
            self.db.rollback()
            return None
        return column

    def delete(self, column_id: int) -> bool:
        column = self.get_by_id(column_id)
        if not column:
            return False
        self.db.delete(column)
        self.db.commit()
        return True

    def get_tasks(self, column_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .filter(Task.column_id == column_id)
            .all()
        )

    def save(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task