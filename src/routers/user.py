from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.entities.schemas import UserCreate, UserUpdate, UserResponse
from src.service.user_service import UserService
from src.db.deps import get_db

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

# POST /users
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    user = service.create_user(data)
    if not user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return user

# GET /users
@router.get("/", response_model=list[UserResponse])
def list_users(service: UserService = Depends(get_user_service)):
    return service.get_all_users()

# GET /users/{id}
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# PUT /users/{id}
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, service: UserService = Depends(get_user_service)):
    user = service.update_user(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found or email already in use")
    return user

# DELETE /users/{id}
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    deleted = service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
