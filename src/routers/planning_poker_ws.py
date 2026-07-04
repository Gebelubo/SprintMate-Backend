from __future__ import annotations

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.models import User
from src.repositories.user_repository import UserRepository
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
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(session_id, user.id, websocket)