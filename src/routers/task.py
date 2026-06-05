from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)
from src.service.task_service import TaskService
from src.utils.dependencies import get_current_user
from src.entities.models import User


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


def get_task_service(
    db: Session = Depends(get_db)
) -> TaskService:
    return TaskService(db)


@router.post("/", response_model=TaskResponse)
def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    task= service.create_task(
        data=data,
        created_by=current_user.id
    )
    return task


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    service: TaskService = Depends(get_task_service)
):
    return service.get_all_tasks()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    data: TaskUpdate,
    service: TaskService = Depends(get_task_service)
):
    task = service.update_task(task_id, data)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=204
)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    deleted = service.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )