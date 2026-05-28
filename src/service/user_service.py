from sqlalchemy.orm import Session

from src.entities.models import User
from src.entities.schemas import UserCreate, UserUpdate
from src.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def create_user(self, data: UserCreate) -> User | None:
        return self.repository.create(data)

    def get_user(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)

    def get_all_users(self) -> list[User]:
        return self.repository.get_all()

    def update_user(self, user_id: int, data: UserUpdate) -> User | None:
        return self.repository.update(user_id, data)

    def delete_user(self, user_id: int) -> bool:
        return self.repository.delete(user_id)
