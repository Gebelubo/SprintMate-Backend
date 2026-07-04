from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.entities.models import Sprint, Task
from src.entities.enums import SprintStatusEnum
from src.entities.schemas import SprintCreate, SprintUpdate, SprintProjectCreate
from src.repositories.sprint_repository import SprintRepository
from src.repositories.board_repository import BoardRepository


class SprintService:
    def __init__(self, db: Session):
        self.repository = SprintRepository(db)

    def create_sprint(self, data: SprintCreate) -> Sprint:
        return self.repository.create(data)

    def get_all_sprints(self) -> list[Sprint]:
        return self.repository.get_all()

    def get_sprint(self, sprint_id: int) -> Sprint | None:
        return self.repository.get_by_id(sprint_id)

    def get_sprint_dates(self, sprint_id: int) -> Sprint | None:
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

    def start_sprint(
        self,
        project_id: int,
        sprint_id: int,
    ) -> Sprint:
        sprint = self.repository.get_by_id_in_project(sprint_id, project_id)

        if sprint is None:
            raise HTTPException(status_code=404, detail="Sprint not found in this project")

        if sprint.status == SprintStatusEnum.ACTIVE:
            raise HTTPException(status_code=400, detail="Sprint is already active")

        if sprint.status == SprintStatusEnum.FINISHED:
            raise HTTPException(status_code=400, detail="Cannot start a sprint that is already finished")

        sprint = self.repository.start(sprint_id)

        self._place_tasks_on_board(project_id, sprint_id)

        return sprint

    def _place_tasks_on_board(self, project_id: int, sprint_id: int) -> None:

        board_repository = BoardRepository(self.repository.db)
        columns = board_repository.get_by_project(project_id)

        if not columns:
            raise HTTPException(
                status_code=400,
                detail="Project has no board columns configured"
            )

        default_column = columns[0]

        tasks = self.repository.get_all_tasks(sprint_id)

        for task in tasks:
            if task.column_id is None:
                task.column_id = default_column.id

        self.repository.db.commit()


    def get_all_tasks(self, sprint_id: int,):
        return self.repository.get_all_tasks(sprint_id)
    
    def stop_sprint(self, project_id: int, sprint_id: int) -> Sprint | None:

        sprint = self.repository.get_by_id_in_project(sprint_id, project_id)

        if sprint is None:
            raise HTTPException(status_code=404, detail="Sprint not found in this project")

        if sprint.status != SprintStatusEnum.ACTIVE:
            raise HTTPException(status_code=400, detail="Sprint no active")

        return self.repository.stop(sprint_id)
    
    def remove_task_from_sprint(self, sprint_id, task_id)-> Task | None:
        return self.repository.remove_task_from_sprint(sprint_id, task_id)