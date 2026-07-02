from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.models import User
from src.entities.schemas import PlanningPokerSessionResponse
from src.service.planning_poker_service import PlanningPokerService
from src.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/projects/{project_id}/planning-poker/sessions",
    tags=["Planning Poker"],
)


def get_planning_poker_service(db: Session = Depends(get_db)) -> PlanningPokerService:
    return PlanningPokerService(db)


@router.post("/", response_model=PlanningPokerSessionResponse)
def create_session(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
):
    return service.create_session(project_id, current_user.id)


@router.get("/", response_model=list[PlanningPokerSessionResponse])
def list_sessions(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
):
    return service.get_project_sessions(project_id)


@router.get("/{session_id}", response_model=PlanningPokerSessionResponse)
def get_session(
    project_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
):
    return service.get_session_in_project(project_id, session_id)


@router.post("/{session_id}/close", response_model=PlanningPokerSessionResponse)
def close_session(
    project_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
):
    return service.close_session(project_id, session_id)