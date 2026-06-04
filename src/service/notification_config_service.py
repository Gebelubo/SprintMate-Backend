from sqlalchemy.orm import Session

from src.repositories.notification_config_repository import (
    NotificationConfigRepository
)
from src.entities.schemas import NotificationConfigUpdate
from src.utils.exceptions import (
    NotificationConfigNotFoundError
)


class NotificationConfigService:

    def __init__(self, db: Session):
        self.repository = NotificationConfigRepository(db)

    def get_config(
        self,
        user_id: int
    ):

        config = self.repository.get_by_user_id(
            user_id
        )

        if config is None:
            raise NotificationConfigNotFoundError()

        return config

    def update_config(
        self,
        user_id: int,
        data: NotificationConfigUpdate
    ):

        config = self.repository.get_by_user_id(
            user_id
        )

        if config is None:
            raise NotificationConfigNotFoundError()

        if data.mention is not None:
            config.mention = data.mention

        if data.late is not None:
            config.late = data.late

        if data.blocked is not None:
            config.blocked = data.blocked

        return self.repository.save(config)