from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.service.notification_config_service import NotificationConfigService
from src.service.notification_service import NotificationService
from src.utils.dependencies import get_current_user
from src.entities.models import User
from src.entities.schemas import NotificationConfigResponse, NotificationConfigUpdate, UserResponse
from src.db.deps import get_db

from src.service.me_service import MeService
from src.utils.exceptions import NotificationConfigNotFoundError, NotificationNotFoundError, NotificationAccessDeniedError

service = MeService()

router = APIRouter(tags=["Me"])

def get_notification_service(
    db: Session = Depends(get_db)
) -> NotificationService:
    return NotificationService(db)

def get_notification_config_service(
    db: Session = Depends(get_db)
):
    return NotificationConfigService(db)

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/me/projects")
def my_projects(
    current_user: User = Depends(get_current_user)
):
    return service.get_projects_from_me(current_user)

@router.get("/me/tasks")
def my_tasks(
    current_user: User = Depends(get_current_user)
):
    return service.get_tasks_from_me(current_user)

@router.get("/me/comments")
def my_comments(
    current_user: User = Depends(get_current_user)
):
    return service.get_comments_from_me(current_user)

@router.get("/me/notifications")
def get_notifications(
    current_user: User = Depends(get_current_user)
):
    return service.get_notifications_from_me(current_user)

@router.get("/me/notifications/{notification_id}")
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user)
):
    notification = service.get_notifications_from_me_by_id(
        current_user,
        notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return notification

@router.patch("/me/notifications/{notification_id}/read")
def read_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(
        get_notification_service
    )
):
    try:

        return service.mark_as_read(
            notification_id,
            current_user.id
        )

    except NotificationNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    except NotificationAccessDeniedError:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
@router.patch("/me/notifications/read-all")
def read_all_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(
        get_notification_service
    )
):
    return service.mark_all_as_read(
        current_user.id
    )

@router.get(
    "/me/notification-config",
    response_model=NotificationConfigResponse
)
def get_notification_config(
    current_user: User = Depends(get_current_user),
    service: NotificationConfigService = Depends(
        get_notification_config_service
    )
):
    try:
        return service.get_config(
            current_user.id
        )

    except NotificationConfigNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Notification config not found"
        )
    
@router.patch(
    "/me/notification-config",
    response_model=NotificationConfigResponse
)
def update_notification_config(
    data: NotificationConfigUpdate,
    current_user: User = Depends(get_current_user),
    service: NotificationConfigService = Depends(
        get_notification_config_service
    )
):
    try:
        return service.update_config(
            current_user.id,
            data
        )

    except NotificationConfigNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Notification config not found"
        )