from sqlalchemy.orm import Session
from src.entities.schemas import UserTaskCreate
from src.entities.models import UserTask
from src.repositories.user_repository import UserRepository
from src.repositories.task_repository import TaskRepository


class UserTaskRepository:
    def __init__(self, db: Session):
            self.db = db

    def create(self, data: UserTaskCreate) -> UserTask:
        user_task = UserTask(
            user_id=data.user_id,
            item_id=data.task_id
        )

        self.db.add(user_task)
        self.db.commit()
        self.db.refresh(user_task)

        return user_task
    
    def assign_user_to_task(self, item_id: int, user_id: int) -> UserTask | None:
        repo_task = TaskRepository(self.db)

        task = repo_task.get_by_id(item_id)

        if not task:
            return None
        
        repo = UserRepository(self.db)
        
        if repo.get_by_id(user_id) is None:
            return None
        
        existing = (
            self.db.query(UserTask)
            .filter(
                UserTask.item_id == item_id,
                UserTask.user_id == user_id
            )
            .first()
        )

        if existing:
            raise ValueError("User is already assigned to this task.")

        user_task = self.create(UserTaskCreate(user_id=user_id, task_id=item_id))

        task.responsible_user_id = user_id
        self.db.commit()

        return user_task
