from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.schemas import (
    SprintCreate,
    SprintUpdate,
    SprintResponse,
    SprintProjectCreate
)
from src.service.sprint_service import SprintService

router = APIRouter(
    prefix="/sprints",
    tags=["Sprints"],
)

@router.post("/")
def create_sprint(
    data: SprintCreate,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.create_sprint(data)

@router.get("/")
def get_sprints(
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.get_all_sprints()

@router.get("/{sprint_id}")
def get_sprint(
    sprint_id: int,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.get_sprint(sprint_id)

@router.patch("/{sprint_id}")
def update_sprint(
    sprint_id: int,
    data: SprintUpdate,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.update_sprint(sprint_id, data)

@router.delete("/{sprint_id}")
def delete_sprint(
    sprint_id: int,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.delete_sprint(sprint_id)

@router.get("/{sprint_id}")
def get_sprint_by_id(
    sprint_id: int,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.get_sprint_by_id(sprint_id)

@router.post("/{sprint_id}/tasks/{task_id}")
def add_task_to_sprint(
    sprint_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.add_task_to_sprint(sprint_id, task_id)

@router.get("/{sprint_id}/tasks")
def get_all_tasks(
    sprint_id: int,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.get_all_tasks(sprint_id)