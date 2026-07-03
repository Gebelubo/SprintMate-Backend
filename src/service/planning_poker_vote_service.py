from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.entities.enums import PlanningPokerStatusEnum
from src.entities.models import PlanningPokerVote
from src.entities.schemas import PLANNING_POKER_CARDS, PlanningPokerVoteCreate
from src.repositories.planning_poker_repository import PlanningPokerRepository
from src.repositories.planning_poker_vote_repository import (
    PlanningPokerVoteRepository,
)
from src.repositories.task_repository import TaskRepository


class PlanningPokerVoteService:
    def __init__(self, db: Session):
        self.repository = PlanningPokerVoteRepository(db)
        self.session_repository = PlanningPokerRepository(db)
        self.task_repository = TaskRepository(db)

    def get_cards(self) -> list[str]:
        return PLANNING_POKER_CARDS

    def create_vote(
        self,
        project_id: int,
        session_id: int,
        user_id: int,
        data: PlanningPokerVoteCreate,
    ) -> PlanningPokerVote:
        session = self.session_repository.get_by_id_in_project(
            session_id, project_id
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Planning poker session not found in this project",
            )

        if session.status != PlanningPokerStatusEnum.OPEN:
            raise HTTPException(
                status_code=409,
                detail="Voting is closed for this planning poker session",
            )

        task = self.task_repository.get_by_id(data.item_id)

        if task is None or task.project_id != project_id:
            raise HTTPException(
                status_code=404,
                detail="Task not found in this project",
            )

        existing_vote = self.repository.get_by_session_user_and_item(
            session_id, user_id, data.item_id
        )

        if existing_vote is not None:
            raise HTTPException(
                status_code=409,
                detail="User has already voted for this task in this session",
            )

        return self.repository.create(
            session_id, user_id, data.item_id, data.vote_value
        )

    def get_session_votes(
        self, project_id: int, session_id: int, current_user_id: int
    ) -> list[PlanningPokerVote]:
        session = self.session_repository.get_by_id_in_project(
            session_id, project_id
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Planning poker session not found in this project",
            )

        votes = self.repository.get_by_session(session_id)

        if session.status == PlanningPokerStatusEnum.OPEN:
            return self._hide_votes(votes, current_user_id)

        return votes

    @staticmethod
    def _hide_votes(
        votes: list[PlanningPokerVote], current_user_id: int
    ) -> list[PlanningPokerVote]:

        hidden_votes = []

        for vote in votes:
            if vote.user_id == current_user_id:
                hidden_votes.append(vote)
                continue

            hidden_votes.append(
                PlanningPokerVote(
                    id=vote.id,
                    session_id=vote.session_id,
                    user_id=vote.user_id,
                    item_id=vote.item_id,
                    vote_value=None,
                )
            )

        return hidden_votes
