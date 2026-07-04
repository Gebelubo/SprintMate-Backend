from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket


@dataclass
class SessionConnections:
    connections: dict[int, set[WebSocket]] = field(default_factory=dict)

    def add(self, user_id: int, websocket: WebSocket) -> None:
        self.connections.setdefault(user_id, set()).add(websocket)

    def remove(self, user_id: int, websocket: WebSocket) -> None:
        sockets = self.connections.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            del self.connections[user_id]

    def all_sockets(self) -> list[WebSocket]:
        return [ws for sockets in self.connections.values() for ws in sockets]

    def user_ids(self) -> list[int]:
        return list(self.connections.keys())

    def is_empty(self) -> bool:
        return not self.connections


class ConnectionManager:
    def __init__(self) -> None:
        self._sessions: dict[int, SessionConnections] = {}
        self._lock = asyncio.Lock()

    async def connect(self, session_id: int, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._sessions.setdefault(session_id, SessionConnections()).add(
                user_id, websocket
            )
        await self.broadcast(
            session_id,
            "participant_joined",
            {"user_id": user_id},
            exclude_user_id=None,
        )

    async def disconnect(self, session_id: int, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return
            session.remove(user_id, websocket)
            if session.is_empty():
                del self._sessions[session_id]

        await self.broadcast(
            session_id,
            "participant_left",
            {"user_id": user_id},
        )

    async def broadcast(
        self,
        session_id: int,
        event_type: str,
        payload: dict[str, Any],
        exclude_user_id: int | None = None,
    ) -> None:
        session = self._sessions.get(session_id)
        if session is None:
            return

        message = json.dumps({"type": event_type, "data": payload})

        dead: list[tuple[int, WebSocket]] = []
        for user_id, sockets in list(session.connections.items()):
            if exclude_user_id is not None and user_id == exclude_user_id:
                continue
            for ws in list(sockets):
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.append((user_id, ws))

        if dead:
            async with self._lock:
                for user_id, ws in dead:
                    session.remove(user_id, ws)
                if session.is_empty():
                    self._sessions.pop(session_id, None)

    def active_participant_ids(self, session_id: int) -> list[int]:
        session = self._sessions.get(session_id)
        return session.user_ids() if session else []


manager = ConnectionManager()


