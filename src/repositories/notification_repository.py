from sqlalchemy.orm import Session

from src.entities.models import Notification


class NotificationRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        notification_id: int
    ) -> Notification | None:

        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

    def get_by_user(
        self,
        user_id: int
    ) -> list[Notification]:

        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .all()
        )

    def save(
        self,
        notification: Notification
    ) -> Notification:

        self.db.commit()
        self.db.refresh(notification)

        return notification

    def save_all(self):

        self.db.commit()