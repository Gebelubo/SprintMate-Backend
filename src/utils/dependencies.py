from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from decouple import config

from src.db.deps import get_db
from src.entities.models import User
from src.repositories.user_repository import UserRepository


SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise credentials_exception

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    repository = UserRepository(db)

    user = repository.get_by_email(email)

    if user is None:
        raise credentials_exception

    return user