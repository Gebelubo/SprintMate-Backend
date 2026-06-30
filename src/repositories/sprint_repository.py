from sqlalchemy.orm import Session

from src.entities.models import Sprint, Task
from src.entities.enums import SprintStatusEnum
from src.entities.schemas import SprintCreate, SprintUpdate, SprintProjectCreate


class SprintRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: SprintCreate) -> Sprint:
        sprint = Sprint(
            name=data.name,
            project_id=data.project_id,
            start_date=data.start_date,
            end_date=data.end_date,
            status=SprintStatusEnum.NOSTATUS,
            goal=None,
            points=0,
        )

        self.db.add(sprint)
        self.db.commit()
        self.db.refresh(sprint)

        return sprint
    
    def create_project(self, data: SprintProjectCreate, project_id:int) -> Sprint:
        sprint = Sprint(
            name=data.name,
            project_id=project_id,
            start_date=data.start_date,
            end_date=data.end_date,
            status=SprintStatusEnum.NOSTATUS,
            goal=None,
            points=None,
        )

        self.db.add(sprint)
        self.db.commit()
        self.db.refresh(sprint)

        return sprint

    def get_by_id(self, sprint_id: int) -> Sprint | None:
        return (
            self.db.query(Sprint)
            .filter(Sprint.id == sprint_id)
            .first()
        )

    def get_all(self) -> list[Sprint]:
        return self.db.query(Sprint).all()

    def update(
        self,
        sprint_id: int,
        data: SprintUpdate
    ) -> Sprint | None:

        sprint = self.get_by_id(sprint_id)

        if not sprint:
            return None

        if data.name is not None:
            sprint.name = data.name

        if data.project_id is not None:
            sprint.project_id = data.project_id

        if data.start_date is not None:
            sprint.start_date = data.start_date

        if data.end_date is not None:
            sprint.end_date = data.end_date

        if data.status is not None:
            sprint.status = data.status

        if data.goal is not None:
            sprint.goal = data.goal

        if data.points is not None:
            sprint.points = data.points

        self.db.commit()
        self.db.refresh(sprint)

        return sprint

    def delete(self, sprint_id: int) -> bool:
        sprint = self.get_by_id(sprint_id)

        if not sprint:
            return False

        self.db.delete(sprint)
        self.db.commit()

        return True
    
    def add_task_to_sprint(self, sprint_id: int, task_id:int) -> Task | None:
        sprint = (self.db.query(Sprint).filter(Sprint.id==sprint_id).first())

        if sprint is None:
            return None

        task = (self.db.query(Task).filter(Task.id==task_id).first())

        if task is None:
            return None

        task.sprint_id = sprint_id

        self.db.commit()
        self.db.refresh(task)

        return task
    
    def get_project_sprints(self, project_id: int) -> list[Sprint]:
        return self.db.query(Sprint).filter(Sprint.project_id==project_id).all()
