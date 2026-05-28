from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.repositories import user_repository
from src.db.deps import get_db

router = APIRouter(prefix="/users", tags=["Users"])

# POST /users
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = user_repository.create_user(db, data)
    if not user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return user


# GET /users 
@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return user_repository.get_all_users(db)


# GET /users/{id}
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_repository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# PUT /users/{id} 
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = user_repository.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found or email already in use")
    return user


# DELETE /users/{id} 
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = user_repository.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")