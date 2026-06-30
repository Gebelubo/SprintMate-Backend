from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.schemas import (
    SprintCreate,
    SprintUpdate,
    SprintResponse,
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

@router.get("/sprints")
def get_sprints(
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.get_all_sprints()

@router.get("/sprints/{sprint_id}")
def get_sprint(
    sprint_id: int,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.get_sprint(sprint_id)

@router.patch("/sprints/{sprint_id}")
def update_sprint(
    sprint_id: int,
    data: SprintUpdate,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.update_sprint(sprint_id, data)

@router.delete("/sprints/{sprint_id}")
def delete_sprint(
    sprint_id: int,
    db: Session = Depends(get_db)
):
    service = SprintService(db)
    return service.delete_sprint(sprint_id)