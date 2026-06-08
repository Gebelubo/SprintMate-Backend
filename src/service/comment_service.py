from src.repositories.comment_repository import CommentRepository
from src.entities.models import Comment
from src.entities.schemas import (
    CommentCreate,
    CommentUpdate
)


class CommentService:

    def __init__(self, db):
        self.dao = CommentRepository(db)

    def create_comment(
        self,
        task_id: int,
        user_id: int,
        data: CommentCreate
    ):
        comment = Comment(
            task_id=task_id,
            user_id=user_id,
            content=data.content,
            type=data.type
        )

        return self.dao.create(comment)

    def get_comment(
        self,
        comment_id: int
    ):
        return self.dao.get_by_id(comment_id)

    def get_task_comments(
        self,
        task_id: int
    ):
        return self.dao.get_by_task(task_id)

    def update_comment(
        self,
        comment_id: int,
        data: CommentUpdate
    ):
        comment = self.dao.get_by_id(comment_id)

        if not comment:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(comment, key, value)

        self.dao.db.commit()
        self.dao.db.refresh(comment)

        return comment

    def delete_comment(
        self,
        comment_id: int
    ):
        comment = self.dao.get_by_id(comment_id)

        if not comment:
            return False

        self.dao.delete(comment)

        return True