from src.entities.enums import SprintStatusEnum
from src.entities.models import User
from src.entities.enums import SprintStatusEnum
from src.entities.schemas import ProjectResponse, ProjectWithRoleResponse

class MeService:


    def get_projects_from_me(
        self,
        current_user: User 
    ):
        return [
            ProjectWithRoleResponse(
                **ProjectResponse.model_validate(association.project).model_dump(),
                role=association.role
            )
            for association in current_user.project_associations
        ]

    def get_tasks_from_me(
        self,
        current_user: User
    ):
        return [
            assignment.task
            for assignment in current_user.assigned_tasks
        ]

    def get_active_tasks_from_me(
        self,
        current_user: User
    ):
        return [
            assignment.task
            for assignment in current_user.assigned_tasks
            if assignment.task.sprint is not None
            and assignment.task.sprint.status == SprintStatusEnum.ACTIVE
        ]

    def get_comments_from_me(
        self,
        current_user: User
    ):
        return current_user.comments

    def get_notifications_from_me(
        self,
        current_user: User
    ):
        return current_user.notifications

    def get_notifications_from_me_by_id(
        self,
        current_user: User,
        notification_id: int
    ):
        notification = next(
            (
                n
                for n in current_user.notifications
                if n.id == notification_id
            ),
            None
        )

        return notification