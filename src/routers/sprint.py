from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.entities.models import User
from src.utils.dependencies import get_current_user

from src.db.deps import get_db
from src.entities.schemas import (
    SprintCreate,
    SprintUpdate,
    SprintResponse,
    SprintProjectCreate,
    SprintDatesResponse
)
from src.service.sprint_service import SprintService

router = APIRouter(
    prefix="/sprints",
    tags=["Sprints"],
)

@router.post("/")
def create_sprint(
    data: SprintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SprintService(db)
    return service.create_sprint(data)

@router.get("/")
def get_sprints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SprintService(db)
    return service.get_all_sprints()

@router.get("/{sprint_id}", response_model=SprintResponse)
def get_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SprintService(db)
    return service.get_sprint(sprint_id)

@router.get("/{sprint_id}/dates", response_model=SprintDatesResponse)
def get_sprint_dates(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SprintService(db)
    sprint = service.get_sprint_dates(sprint_id)

    if sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")

    return sprint

@router.patch("/{sprint_id}")
def update_sprint(
    sprint_id: int,
    data: SprintUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SprintService(db)
    return service.update_sprint(sprint_id, data)

@router.delete("/{sprint_id}")
def delete_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SprintService(db)
    return service.delete_sprint(sprint_id)

@router.get("/{sprint_id}")
def get_sprint_by_id(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SprintService(db)
    return service.get_sprint_by_id(sprint_id)

@router.post("/{sprint_id}/tasks/{task_id}")
def add_task_to_sprint(
    sprint_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SprintService(db)
    return service.add_task_to_sprint(sprint_id, task_id)

@router.get("/{sprint_id}/tasks")
def get_all_tasks(
    sprint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.get_all_tasks(sprint_id)

@router.put("/{sprint_id}/tasks/{task_id}")
def remove_task_from_sprint(
    sprint_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    task = service.remove_task_from_sprint(sprint_id, task_id)

    if task is None:
        raise HTTPException(status_code=403, detail="Task does not exist.")
    
    return task