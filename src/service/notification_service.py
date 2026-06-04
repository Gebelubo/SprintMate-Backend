from sqlalchemy.orm import Session

from src.repositories.notification_repository import NotificationRepository
from src.utils.exceptions import (
    NotificationNotFoundError,
    NotificationAccessDeniedError
)


class NotificationService:

    def __init__(self, db: Session):
        self.repository = NotificationRepository(db)

    def mark_as_read(
        self,
        notification_id: int,
        user_id: int
    ):

        notification = self.repository.get_by_id(
            notification_id
        )

        if notification is None:
            raise NotificationNotFoundError()

        if notification.user_id != user_id:
            raise NotificationAccessDeniedError()

        notification.read = True

        return self.repository.save(notification)

    def mark_all_as_read(
        self,
        user_id: int
    ):

        notifications = self.repository.get_by_user(
            user_id
        )

        for notification in notifications:
            notification.read = True

        self.repository.save_all()

        return {
            "message": "All notifications marked as read"
        }