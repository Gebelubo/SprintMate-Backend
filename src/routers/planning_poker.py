import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.models import User
from src.entities.schemas import (
    PlanningPokerCardsResponse,
    PlanningPokerInviteSchema,
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
from src.websocket.connection_manager import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
async def create_session(
    project_id: int,
    data: PlanningPokerInviteSchema,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to create a planning poker session",
        )

    session = service.create_session(project_id, current_user.id)

    # Send invitation emails
    if data.emails:
        logger.info(f"--- Received request to invite emails: {data.emails} ---")
        project = project_service.get_project(project_id)
        if project is None:
            # This should ideally not happen if the member check passed
            raise HTTPException(status_code=404, detail="Project not found")

        from src.utils.send_email import send_planning_poker_invite_email

        for email in data.emails:
            try:
                await send_planning_poker_invite_email(
                    email=email,
                    project_id=project_id,
                    project_name=project.name,
                    subject=f"Convite para o Planning Poker: {project.name}",
                )
            except Exception as e:
                logger.error(f"Failed to send email to {email}: {e}", exc_info=True)

    await manager.broadcast(
        session.id,
        "session_created",
        {"session_id": session.id, "created_by": current_user.id},
    )
    return session


@router.get("/active", response_model=PlanningPokerSessionResponse, responses={404: {"description": "No active session found"}})
def get_active_session(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_member(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of this project to view sessions",
        )

    session = service.get_active_session_for_project(project_id)
    if session is None:
        raise HTTPException(status_code=404, detail="No active session found for this project")
    return session


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


@router.post("/{session_id}/close", response_model=PlanningPokerSessionResponse)
async def close_session(
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

    session = service.close_session(project_id, session_id)

    # Disconnect all clients, which will trigger the UI to update
    # via the websocket 'onclose' event handler.
    await manager.disconnect_all(session_id, code=4000, reason="Session closed by leader")

    return session


@router.post("/{session_id}/reveal", response_model=PlanningPokerSessionResponse)
async def reveal_votes(
    project_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: PlanningPokerService = Depends(get_planning_poker_service),
    project_service: ProjectService = Depends(get_project_service),
):
    if not project_service.is_project_leader(project_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Only the project leader can reveal votes",
        )

    session = service.reveal_votes(project_id, session_id)

    session_data = PlanningPokerSessionResponse.model_validate(session).model_dump(
        mode="json"
    )

    await manager.broadcast(
        session_id,
        "votes_revealed",
        {"session_id": session_id, "session": session_data},
    )
    return session


@router.post("/{session_id}/votes", response_model=PlanningPokerVoteResponse)
async def create_vote(
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

    vote = service.create_vote(project_id, session_id, current_user.id, data)

    await manager.broadcast(
        session_id,
        "vote_created",
        {
            "item_id": getattr(data, "item_id", None),
            "user_id": current_user.id,
        },
    )

    if hasattr(service, "have_all_members_voted") and service.have_all_members_voted(
        project_id, session_id, getattr(data, "item_id", None)
    ):
        await manager.broadcast(
            session_id,
            "all_voted",
            {"item_id": getattr(data, "item_id", None)},
        )

    return vote


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
async def apply_estimate(
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

    task = service.apply_final_estimate(project_id, session_id, item_id)

    task_data = TaskResponse.model_validate(task).model_dump()

    await manager.broadcast(
        session_id,
        "estimate_applied",
        {
            "item_id": item_id,
            "task": task_data,
        },
    )
    return task


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