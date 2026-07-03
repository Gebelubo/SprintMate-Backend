from sqlalchemy.orm import Session

from src.entities.models import Project, ProjectUser
from src.entities.schemas import ProjectCreate, ProjectUpdate, ProjectUserAdd, ProjectUserUpdateRole
from src.repositories.project_repository import ProjectRepository
from src.entities.schemas import ProjectUserResponseWithUser, SprintProjectCreate
from src.entities.enums import RoleEnum

from src.utils.send_email import send_project_invite_email
class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)

    def create_project(self, data: ProjectCreate, created_by: int) -> Project | None:
        try:
            response = self.repository.create(data, created_by)
            self.repository.add_user(response.id, ProjectUserAdd(user_id=created_by, role=RoleEnum.OWNER.value))
        except Exception as e:
            raise e
        return response
    def get_all_projects(self) -> list[Project]:
        return self.repository.get_all()

    def get_project(self, project_id: int) -> Project | None:
        return self.repository.get_by_id(project_id)

    def update_project(self, project_id: int, data: ProjectUpdate) -> Project | None:
        return self.repository.update(project_id, data)

    def delete_project(self, project_id: int) -> bool:
        return self.repository.delete(project_id)

    def is_project_member(self, project_id: int, user_id: int) -> bool:
        return self.repository.get_project_user(project_id, user_id) is not None

    def get_user_role(self, project_id: int, user_id: int) -> RoleEnum | None:
        project_user = self.repository.get_project_user(project_id, user_id)
        return project_user.role if project_user else None

    def is_project_leader(self, project_id: int, user_id: int) -> bool:
        
        role = self.get_user_role(project_id, user_id)
        return role in (RoleEnum.OWNER, RoleEnum.ADMIN)

    def get_project_users(
        self,
        project_id: int
    ) -> list[ProjectUserResponseWithUser]:

        users = self.repository.get_users(project_id)

        return [
            ProjectUserResponseWithUser(
                id=user.id,
                user_name=user.user.name,
                email=user.user.email,
                user_id=user.user_id,
                project_id=user.project_id,
                role=user.role
            )
            for user in users
        ]

    def add_user_to_project(self, project_id: int, data: ProjectUserAdd) -> ProjectUser | None:
        return self.repository.add_user(project_id, data)

    def update_user_role(self, project_id: int, user_id: int, data: ProjectUserUpdateRole) -> ProjectUser | None:
        return self.repository.update_user_role(project_id, user_id, data.role)

    def remove_user_from_project(self, project_id: int, user_id: int) -> bool:
        return self.repository.remove_user(project_id, user_id)
    
    async def invite_user(
        self,
        project_id: int,
        email: str
    ):
        project = self.repository.get_by_id(project_id)
        if project is None:
            raise Exception("Project not found")

        await send_project_invite_email(
            email=email,
            project_id=project_id,
            subject=f"Convite para o projeto {project.name}",
            project_name=project.name
        )

        return {
            "message": "Invitation sent successfully"
        }