from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.entities.models import User
from src.entities.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: UserCreate, hashed_password) -> User | None:
        user = User(
            name=data.name,
            email=data.email,
            password_hash=hashed_password,
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

    def update(self, user_id: int, data: UserUpdate, hashed_password) -> User | None:
        user = self.get_by_id(user_id)
        if not user:
            return None

        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            user.email = data.email
        if data.password is not None:
            user.password_hash = hashed_password

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
