from fastapi import HTTPException, status
from datetime import datetime, UTC, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from decouple import config
from src.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session

from src.service.jwt_tokens import (
    create_access_token, 
    create_refresh_token,
    create_reset_token
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

class AuthService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def user_login(self, email: str, password: str):

        user_on_db = self.repository.get_by_email(email)

        if user_on_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not pwd_context.verify(password, user_on_db.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token({
            "sub": user_on_db.email
        })

        refresh_token = create_refresh_token({
            "sub": user_on_db.email
        })

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def refresh_token(self, refresh_token: str):

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing"
            )

        try:

            payload = jwt.decode(
                refresh_token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            email = payload.get("sub")

            new_access_token = create_access_token({
                "sub": email
            })

            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
    def forgot_password(self, email: str):

        user = self.repository.get_by_email(email)

        if user is None:
            return {
                "message": "If the email exists, a recovery link was sent"
            }

        reset_token = create_reset_token(email)

        reset_link = (
            f"http://localhost:3000/reset-password?"
            f"token={reset_token}"
        )

        print(reset_link)

        return {
            "message": "Recovery email sent"
        }
    
    def reset_password(
        self,
        token: str,
        new_password: str
    ):

        try:

            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            if payload.get("type") != "reset":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            email = payload.get("sub")

            user = self.repository.get_by_email(email)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            hashed_password = pwd_context.hash(new_password)

            user.password_hash = hashed_password

            self.repository.update(user)

            return {
                "message": "Password updated successfully"
            }

        except JWTError:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )