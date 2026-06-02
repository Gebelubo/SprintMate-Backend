from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.entities.models import User
from src.entities.schemas import UserCreate, UserUpdate
from src.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_user(self, data: UserCreate) -> User | None:
        hashed_password = self._hash_password(data.password)
        return self.repository.create(data, hashed_password)

    def get_user(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)

    def get_all_users(self) -> list[User]:
        return self.repository.get_all()

    def update_user(self, user_id: int, data: UserUpdate) -> User | None:
        hashed_password = self._hash_password(data.password)
        return self.repository.update(user_id, data, hashed_password)

    def delete_user(self, user_id: int) -> bool:
        return self.repository.delete(user_id)
    