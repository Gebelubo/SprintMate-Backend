from sqlalchemy.orm import Session

from src.entities.models import Sprint
from src.entities.schemas import SprintCreate, SprintUpdate
from src.repositories.sprint_repository import SprintRepository


class SprintService:
    def __init__(self, db: Session):
        self.repository = SprintRepository(db)

    def create_sprint(self, data: SprintCreate) -> Sprint:
        return self.repository.create(data)

    def get_all_sprints(self) -> list[Sprint]:
        return self.repository.get_all()

    def get_sprint(self, sprint_id: int) -> Sprint | None:
        return self.repository.get_by_id(sprint_id)

    def update_sprint(
        self,
        sprint_id: int,
        data: SprintUpdate
    ) -> Sprint | None:
        return self.repository.update(sprint_id, data)

    def delete_sprint(self, sprint_id: int) -> bool:
        return self.repository.delete(sprint_id)