from src.repositories.attachment_repository import AttachmentRepository
from src.entities.models import Attach
from src.entities.schemas import AttachmentCreate


class AttachmentService:

    def __init__(self, db):
        self.dao = AttachmentRepository(db)

    def create_attachment(
        self,
        task_id: int,
        data: AttachmentCreate
    ):
        attachment = Attach(
            task_id=task_id,
            url=data.url,
            type=data.type
        )

        return self.dao.create(attachment)

    def get_attachment(
        self,
        attachment_id: int
    ):
        return self.dao.get_by_id(attachment_id)

    def get_task_attachments(
        self,
        task_id: int
    ):
        return self.dao.get_by_task(task_id)

    def delete_attachment(
        self,
        attachment_id: int
    ):
        attachment = self.dao.get_by_id(
            attachment_id
        )

        if not attachment:
            return False

        self.dao.delete(attachment)

        return True