from fastapi import APIRouter, HTTPException, Depends, Request, Response 
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.entities.schemas import UserCreate, UserResponse, ResetPasswordRequest, ForgotPasswordRequest
from src.service.auth_service import AuthService
from src.db.deps import get_db


router = APIRouter(prefix="/auth", tags=["Auth"])

def get_user_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/register", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, service: AuthService = Depends(get_user_service)):
    user = service.create_user(data)
    if not user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return user

@router.post("/login")
def login(
    response: Response,
    request_form_user: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_user_service)
):

    result = service.user_login(
        email=request_form_user.username,
        password=request_form_user.password
    )

    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,  
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return {
        "access_token": result["access_token"],
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(
    request: Request,
    service: AuthService = Depends(get_user_service)
):

    refresh_token = request.cookies.get("refresh_token")

    return service.refresh_token(refresh_token)

@router.post("/logout")
def logout(response: Response):

    response.delete_cookie("refresh_token")

    return {
        "message": "Logged out"
    }

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    service: AuthService = Depends(get_user_service)
):
    return await service.forgot_password(request.email)

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    service: AuthService = Depends(get_user_service)
):
    return service.reset_password(
        token=request.token,
        new_password=request.new_password
    )