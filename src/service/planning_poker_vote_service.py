from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.entities.enums import PlanningPokerStatusEnum
from src.entities.models import PlanningPokerVote, Task
from src.entities.schemas import (
    PLANNING_POKER_CARDS,
    PlanningPokerResultResponse,
    PlanningPokerVoteCreate,
)
from src.repositories.planning_poker_repository import PlanningPokerRepository
from src.repositories.planning_poker_vote_repository import (
    PlanningPokerVoteRepository,
)
from src.repositories.task_repository import TaskRepository

_NUMERIC_CARDS = sorted(
    (card for card in PLANNING_POKER_CARDS if card.isdigit()),
    key=float,
)


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

    def get_item_results(
        self, project_id: int, session_id: int, item_id: int
    ) -> PlanningPokerResultResponse:
        session = self.session_repository.get_by_id_in_project(
            session_id, project_id
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Planning poker session not found in this project",
            )

        if session.status != PlanningPokerStatusEnum.CLOSED:
            raise HTTPException(
                status_code=409,
                detail="Votes have not been revealed yet for this session",
            )

        votes = self.repository.get_by_session_and_item(session_id, item_id)

        if not votes:
            raise HTTPException(
                status_code=404,
                detail="No votes found for this task in this session",
            )

        average = self._calculate_average(votes)
        final_estimate = self._calculate_final_estimate(average)

        return PlanningPokerResultResponse(
            session_id=session_id,
            item_id=item_id,
            votes=votes,
            average=average,
            final_estimate=final_estimate,
        )

    def apply_final_estimate(
        self, project_id: int, session_id: int, item_id: int
    ) -> Task:
    
        result = self.get_item_results(project_id, session_id, item_id)

        if result.final_estimate is None:
            raise HTTPException(
                status_code=409,
                detail="There is no numeric estimate to apply for this task",
            )

        task = self.task_repository.get_by_id(item_id)

        if task is None or task.project_id != project_id:
            raise HTTPException(
                status_code=404,
                detail="Task not found in this project",
            )

        task.points = int(float(result.final_estimate))

        return self.task_repository.save(task)

    @staticmethod
    def _calculate_average(votes: list[PlanningPokerVote]) -> float | None:
        numeric_values = []

        for vote in votes:
            if vote.vote_value is None:
                continue
            try:
                numeric_values.append(float(vote.vote_value))
            except ValueError:
                continue

        if not numeric_values:
            return None

        return round(sum(numeric_values) / len(numeric_values), 2)

    @staticmethod
    def _calculate_final_estimate(average: float | None) -> str | None:
        if average is None:
            return None

        for card in _NUMERIC_CARDS:
            if float(card) >= average:
                return card

        return _NUMERIC_CARDS[-1] if _NUMERIC_CARDS else None

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
    