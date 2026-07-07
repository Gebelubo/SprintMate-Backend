from sqlalchemy.orm import Session

from src.entities.models import PlanningPokerSession
from src.entities.enums import PlanningPokerStatusEnum


class PlanningPokerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project_id: int, created_by: int) -> PlanningPokerSession:
        session = PlanningPokerSession(
            project_id=project_id,
            created_by=created_by,
            status=PlanningPokerStatusEnum.OPEN,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_by_id(self, session_id: int) -> PlanningPokerSession | None:
        return (
            self.db.query(PlanningPokerSession)
            .filter(PlanningPokerSession.id == session_id)
            .first()
        )

    def get_by_id_in_project(
        self, session_id: int, project_id: int
    ) -> PlanningPokerSession | None:
        return (
            self.db.query(PlanningPokerSession)
            .filter(
                PlanningPokerSession.id == session_id,
                PlanningPokerSession.project_id == project_id,
            )
            .first()
        )

    def get_project_sessions(self, project_id: int) -> list[PlanningPokerSession]:
        return (
            self.db.query(PlanningPokerSession)
            .filter(PlanningPokerSession.project_id == project_id)
            .order_by(PlanningPokerSession.id.desc())
            .all()
        )

    def get_active_for_project(self, project_id: int) -> PlanningPokerSession | None:
        return self.db.query(PlanningPokerSession).filter(
            PlanningPokerSession.project_id == project_id,
            PlanningPokerSession.status != PlanningPokerStatusEnum.CLOSED
        ).order_by(PlanningPokerSession.id.desc()).first()

    def update_status(self, session_id: int, status: PlanningPokerStatusEnum) -> PlanningPokerSession:
        session = self.get_by_id(session_id)
        if session:
            session.status = status
            self.db.commit()
            self.db.refresh(session)
        return session

    def close(self, session_id: int) -> PlanningPokerSession:
        return self.update_status(session_id, PlanningPokerStatusEnum.CLOSED)