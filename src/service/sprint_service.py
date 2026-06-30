from sqlalchemy.orm import Session

from src.entities.models import Sprint
from src.entities.schemas import SprintCreate, SprintUpdate, SprintProjectCreate
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
    
    def get_sprint_by_id(
        self,
        sprint_id:int
):
        return self.repository.get_by_id(sprint_id)
    
    def add_task_to_sprint(
        self,
        sprint_id,
        task_id
    ):
        return self.repository.add_task_to_sprint(sprint_id, task_id)
    
    def create_sprint_in_project(
        self,
        data: SprintProjectCreate,
        project_id: int,
    ):
        return self.repository.create_project(data, project_id)
    
    def get_project_sprints(
        self,
        project_id: int,
    ):
        return self.repository.get_project_sprints(project_id)