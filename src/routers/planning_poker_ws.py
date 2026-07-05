from __future__ import annotations

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.models import User
from src.entities.enums import PlanningPokerStatusEnum
from src.entities.schemas import PlanningPokerVoteResponse
from src.repositories.user_repository import UserRepository
from src.service.planning_poker_service import PlanningPokerService
from src.service.planning_poker_vote_service import PlanningPokerVoteService
from src.service.project_service import ProjectService
from src.websocket.connection_manager import manager

from src.utils.dependencies import SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix="/projects/{project_id}/planning-poker/sessions",
    tags=["Planning Poker WebSocket"],
)


async def get_current_user_ws(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db),
) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            raise ValueError("wrong token type")

        email = payload.get("sub")
        if email is None:
            raise ValueError("no sub in token")

        user = UserRepository(db).get_by_email(email)
        if user is None:
            raise ValueError("user not found")

        return user
    except (JWTError, ValueError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None


@router.websocket("/{session_id}/ws")
async def planning_poker_ws(
    websocket: WebSocket,
    project_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_ws),
):
    if user is None:
        return

    project_service = ProjectService(db)
    if not project_service.is_project_member(project_id, user.id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(session_id, user.id, websocket)

    # --- START: New logic to sync participants on connect ---
    # 1. Get a list of users already in the session
    connected_user_ids = manager.active_participant_ids(session_id)
    current_item = manager.get_current_item(session_id)
    participants = []
    user_repo = UserRepository(db)
    for uid in connected_user_ids:
        p_user = user_repo.get_by_id(uid)
        if p_user:
            role = project_service.get_user_role(project_id, p_user.id)
            participants.append({
                "userId": p_user.id,
                "fullName": p_user.name,
                "email": p_user.email,
                "role": role.value if role else None,
            })

    votes_payload: list[dict] = []
    if current_item and current_item.get("item_id") is not None:
        vote_service = PlanningPokerVoteService(db)
        votes = vote_service.repository.get_by_session_and_item(
            session_id,
            int(current_item["item_id"]),
        )
        votes_payload = [
            PlanningPokerVoteResponse.model_validate(vote).model_dump()
            for vote in votes
        ]

    # 2. Send the current participant list ONLY to the newly connected user
    await websocket.send_json(
        {
            "event": "session_state",
            "payload": {
                "participants": participants,
                "currentItem": current_item,
                "votes": votes_payload,
            },
        }
    )
    # --- END: New logic ---

    user_role = project_service.get_user_role(project_id, user.id)
    await manager.broadcast(
        session_id,
        "user_joined",
        {
            "userId": user.id,
            "fullName": user.name,
            "email": user.email,
            "role": user_role.value if user_role else None,
        },
    )

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            payload = data.get("payload", {})

            if event == "start_voting_on_item":
                # Only the project leader can start a vote on an item
                if project_service.is_project_leader(project_id, user.id):
                    item_id = payload.get("item_id")
                    if item_id is not None:
                        PlanningPokerService(db).repository.update_status(
                            session_id,
                            PlanningPokerStatusEnum.OPEN,
                        )
                        current_item_payload = payload.get("item") or {"item_id": item_id}
                        manager.set_current_item(session_id, current_item_payload)
                        await manager.broadcast(
                            session_id,
                            "voting_on_item",
                            current_item_payload,
                        )
            elif event == "clear_current_item":
                if project_service.is_project_leader(project_id, user.id):
                    manager.set_current_item(session_id, None)
                    await manager.broadcast(session_id, "current_item_cleared", {})
    except WebSocketDisconnect:
        pass
    finally:
        await manager.broadcast(
            session_id,
            "user_left",
            {"userId": user.id},
        )
        await manager.disconnect(session_id, user.id, websocket)
