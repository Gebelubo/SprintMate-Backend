from sqlalchemy.orm import Session

from src.entities.models import PlanningPokerVote


class PlanningPokerVoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_session_user_and_item(
        self, session_id: int, user_id: int, item_id: int
    ) -> PlanningPokerVote | None:
        return (
            self.db.query(PlanningPokerVote)
            .filter(
                PlanningPokerVote.session_id == session_id,
                PlanningPokerVote.user_id == user_id,
                PlanningPokerVote.item_id == item_id,
            )
            .first()
        )

    def get_by_session(self, session_id: int) -> list[PlanningPokerVote]:
        return (
            self.db.query(PlanningPokerVote)
            .filter(PlanningPokerVote.session_id == session_id)
            .all()
        )

    def get_by_session_and_item(
        self, session_id: int, item_id: int
    ) -> list[PlanningPokerVote]:
        return (
            self.db.query(PlanningPokerVote)
            .filter(
                PlanningPokerVote.session_id == session_id,
                PlanningPokerVote.item_id == item_id,
            )
            .all()
        )

    def create(
        self, session_id: int, user_id: int, item_id: int, vote_value: str
    ) -> PlanningPokerVote:
        vote = PlanningPokerVote(
            session_id=session_id,
            user_id=user_id,
            item_id=item_id,
            vote_value=vote_value,
        )

        self.db.add(vote)
        self.db.commit()
        self.db.refresh(vote)

        return vote
