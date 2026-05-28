from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.entities.models import User
from src.schemas.user import UserCreate, UserUpdate
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_user(db: Session, data: UserCreate) -> User | None:
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        verified=False,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user) 
    except IntegrityError:
        db.rollback()
        return None  
    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()


def update_user(db: Session, user_id: int, data: UserUpdate) -> User | None:
    user = get_user(db, user_id)
    if not user:
        return None  

    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.password_hash = hash_password(data.password)

    user.updated_at = datetime.utcnow()
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return None  
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False  

    db.delete(user)
    db.commit()
    return True