from fastapi import HTTPException, status
from datetime import datetime, UTC, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from decouple import config
from src.repositories.user_repository import UserRepository
from src.service.reset_password import send_reset_email
from src.service.user_service import UserService
from sqlalchemy.orm import Session
from src.entities.schemas import UserCreate
from src.entities.models import User

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
        self.user_repository = UserRepository(db)
        self.user_service = UserService(db)

    def create_user(self, data: UserCreate) -> User | None:
        hashed_password = self.user_service._hash_password(data.password)
        return self.user_repository.create(data, hashed_password)

    def user_login(self, email: str, password: str):

        user_on_db = self.user_repository.get_by_email(email)

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
        
    async def forgot_password(self, email: str):

        user = self.user_repository.get_by_email(email)

        if not user:
            return {"message": "Email não cadastrado"}

        token = create_reset_token(email)

        await send_reset_email(email, token)

        return {
            "message": "Link de recuperação enviado"
        }

    async def validation_email(self, email: str):

        await send_reset_email(email, token)

        return {
            "message": "Link de recuperação enviado"
        }
    
    def reset_password(self, token: str, new_password: str):

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            email = payload["sub"]

        except JWTError:
            raise HTTPException(
                status_code=400,
                detail="Token inválido ou expirado"
            )

        user = self.user_repository.get_by_email(email)

        user.password = self.user_service._hash_password(new_password)

        self.user_repository.save(user)

        return {"message": "Senha alterada com sucesso"}