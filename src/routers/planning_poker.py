from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.models import User
from src.entities.schemas import (
    PlanningPokerCardsResponse,
    PlanningPokerResultResponse,
    PlanningPokerSessionResponse,
    PlanningPokerVoteCreate,
    PlanningPokerVoteResponse,
    TaskResponse,
)
from src.service.planning_poker_service import PlanningPokerService
from src.service.planning_poker_vote_service import PlanningPokerVoteService
from src.service.project_service import ProjectService
from src.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/projects/{project_id}/planning-poker/sessions",
    tags=["Planning Poker"],
)

cards_router = APIRouter(
    prefix="/planning-poker",
    tags=["Planning Poker"],
)


def get_planning_poker_service(db: Session = Depends(get_db)) -> PlanningPokerService:
    return PlanningPokerService(db)


def get_planning_poker_vote_service(
    db: Session = Depends(get_db),
) -> PlanningPokerVoteService:
    return PlanningPokerVoteService(db)


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@cards_router.get("/cards", response_model=PlanningPokerCardsResponse)
def get_voting_cards(
    current_user: User = Depends(get_current_user),
    service: PlanningPokerVoteService = Depends(get_planning_poker_vote_service),
):
    return PlanningPokerCardsResponse(cards=service.get_cards())


@router.post("/", response_model=PlanningPokerSessionResponse)
def create_session(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to create a planning poker session",
        )

    return service.create_session(project_id, current_user.id)


@router.get("/", response_model=list[PlanningPokerSessionResponse])
def list_sessions(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to list planning poker sessions",
        )

    return service.get_project_sessions(project_id)


@router.get("/{session_id}", response_model=PlanningPokerSessionResponse)
def get_session(
    project_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to view this session",
        )

    return service.get_session_in_project(project_id, session_id)


@router.post("/{session_id}/close", response_model=PlanningPokerSessionResponse)
def close_session(
    project_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_leader(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Only the project leader can close a planning poker session",
        )

    return service.close_session(project_id, session_id)


@router.post("/{session_id}/reveal", response_model=PlanningPokerSessionResponse)
def reveal_votes(
    project_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to reveal votes",
        )

    return service.reveal_votes(project_id, session_id)


@router.post("/{session_id}/votes", response_model=PlanningPokerVoteResponse)
def create_vote(
    project_id: int,
    session_id: int,
    data: PlanningPokerVoteCreate,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerVoteService = Depends(get_planning_poker_vote_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to vote",
        )

    return service.create_vote(project_id, session_id, current_user.id, data)


@router.get("/{session_id}/votes", response_model=list[PlanningPokerVoteResponse])
def list_votes(
    project_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerVoteService = Depends(get_planning_poker_vote_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to view the votes",
        )

    return service.get_session_votes(project_id, session_id, current_user.id)


@router.get(
    "/{session_id}/items/{item_id}/results",
    response_model=PlanningPokerResultResponse,
)
def get_item_results(
    project_id: int,
    session_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerVoteService = Depends(get_planning_poker_vote_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to view the results",
        )

    return service.get_item_results(project_id, session_id, item_id)


@router.post(
    "/{session_id}/items/{item_id}/apply-estimate",
    response_model=TaskResponse,
)
def apply_estimate(
    project_id: int,
    session_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerVoteService = Depends(get_planning_poker_vote_service),
    project_service: ProjectService = Depends(get_project_service),
):
    
    if not project_service.is_project_leader(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Only the project leader can define the task estimate",
        )

    return service.apply_final_estimate(project_id, session_id, item_id)