from sqlalchemy.orm import Session

from src.entities.models import NotificationConfig


class NotificationConfigRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(
        self,
        user_id: int
    ) -> NotificationConfig | None:

        return (
            self.db.query(NotificationConfig)
            .filter(
                NotificationConfig.user_id == user_id
            )
            .first()
        )

    def save(
        self,
        config: NotificationConfig
    ) -> NotificationConfig:

        self.db.commit()
        self.db.refresh(config)

        return config