from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from datetime import datetime

from src.entities.models import User
from src.entities.schemas import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: UserCreate) -> User | None:
        user = User(
            name=data.name,
            email=data.email,
            password_hash=_hash_password(data.password),
            verified=False,
        )
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            return None
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self) -> list[User]:
        return self.db.query(User).all()

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        user = self.get_by_id(user_id)
        if not user:
            return None

        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            user.email = data.email
        if data.password is not None:
            user.password_hash = _hash_password(data.password)

        user.updated_at = datetime.utcnow()
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            return None
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
