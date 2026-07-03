from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.entities.enums import PlanningPokerStatusEnum
from src.entities.models import PlanningPokerSession
from src.repositories.planning_poker_repository import PlanningPokerRepository


class PlanningPokerService:
    def __init__(self, db: Session):
        self.repository = PlanningPokerRepository(db)

    def create_session(
        self, project_id: int, created_by: int
    ) -> PlanningPokerSession:
        return self.repository.create(project_id, created_by)

    def get_session(self, session_id: int) -> PlanningPokerSession | None:
        return self.repository.get_by_id(session_id)

    def get_session_in_project(
        self, project_id: int, session_id: int
    ) -> PlanningPokerSession:
        session = self.repository.get_by_id_in_project(session_id, project_id)

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Planning poker session not found in this project",
            )

        return session

    def get_project_sessions(self, project_id: int) -> list[PlanningPokerSession]:
        return self.repository.get_project_sessions(project_id)

    def close_session(self, project_id: int, session_id: int) -> PlanningPokerSession:
        session = self.get_session_in_project(project_id, session_id)

        return self.repository.close(session.id)

    def reveal_votes(self, project_id: int, session_id: int) -> PlanningPokerSession:
        session = self.get_session_in_project(project_id, session_id)

        if session.status == PlanningPokerStatusEnum.CLOSED:
            raise HTTPException(
                status_code=409,
                detail="Votes for this planning poker session have already been revealed",
            )

        return self.repository.close(session.id)