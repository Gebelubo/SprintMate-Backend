from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import joinedload

from src.entities.models import Project, ProjectUser
from src.entities.schemas import ProjectCreate, ProjectUpdate, ProjectUserAdd
from src.entities.enums import RoleEnum
import random


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def _normalize_role(self, role: RoleEnum | str) -> str:
        role_value = role.value if isinstance(role, RoleEnum) else str(role)
        role_value = role_value.upper()
        
        if role_value == "DEV":
            return "MEMBER"

        return role_value

    def _generate_unique_code(self) -> int:
        while True:
            code = random.randint(10000, 99999)
            exists = self.db.query(Project).filter(Project.code == code).first()
            if not exists:
                return code

    def create(self, data: ProjectCreate, created_by: int) -> Project | None:
        project = Project(
            name=data.name,
            description=data.description,
            code=self._generate_unique_code(),
            created_by=created_by,
        )
        self.db.add(project)
        try:
            self.db.commit()
            self.db.refresh(project)
        except IntegrityError:
            self.db.rollback()
            return None
        return project

    def get_all(self) -> list[Project]:
        return self.db.query(Project).all()

    def get_by_id(self, project_id: int) -> Project | None:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def update(self, project_id: int, data: ProjectUpdate) -> Project | None:
        project = self.get_by_id(project_id)
        if not project:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        project.updated_at = datetime.utcnow()
        try:
            self.db.commit()
            self.db.refresh(project)
        except IntegrityError:
            self.db.rollback()
            return None
        return project

    def delete(self, project_id: int) -> bool:
        project = self.get_by_id(project_id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True

    # --- Project members ---

    def get_users(self, project_id: int):
        return (
            self.db.query(ProjectUser)
            .options(joinedload(ProjectUser.user))
            .filter(ProjectUser.project_id == project_id)
            .all()
        )

    def add_user(self, project_id: int, data: ProjectUserAdd) -> ProjectUser | None:
        assoc = ProjectUser(
            project_id=project_id,
            user_id=data.user_id,
            role=data.role.lower(),
        )
        self.db.add(assoc)
        try:
            self.db.commit()
            self.db.refresh(assoc)
        except IntegrityError:
            self.db.rollback()
            return None
        return assoc

    def get_project_user(self, project_id: int, user_id: int) -> ProjectUser | None:
        return (
            self.db.query(ProjectUser)
            .filter(
                ProjectUser.project_id == project_id,
                ProjectUser.user_id == user_id,
            )
            .first()
        )

    def update_user_role(self, project_id: int, user_id: int, role: RoleEnum) -> ProjectUser | None:
        assoc = self.get_project_user(project_id, user_id)
        if not assoc:
            return None
        assoc.role = role.lower()
        self.db.commit()
        self.db.refresh(assoc)
        return assoc

    def remove_user(self, project_id: int, user_id: int) -> bool:
        assoc = self.get_project_user(project_id, user_id)
        if not assoc:
            return False
        self.db.delete(assoc)
        self.db.commit()
        return True