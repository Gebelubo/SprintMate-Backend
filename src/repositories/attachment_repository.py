from sqlalchemy.orm import Session

from src.entities.models import Attach


class AttachmentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, attachment: Attach):
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)

        return attachment

    def get_by_id(self, attachment_id: int):
        return (
            self.db.query(Attach)
            .filter(Attach.id == attachment_id)
            .first()
        )

    def get_by_task(self, task_id: int):
        return (
            self.db.query(Attach)
            .filter(Attach.task_id == task_id)
            .all()
        )

    def delete(self, attachment: Attach):
        self.db.delete(attachment)
        self.db.commit()