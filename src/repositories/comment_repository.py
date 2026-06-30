from sqlalchemy.orm import Session

from src.entities.models import Comment


class CommentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, comment: Comment):
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        return comment

    def get_by_id(self, comment_id: int):
        return (
            self.db.query(Comment)
            .filter(Comment.id == comment_id)
            .first()
        )

    def get_by_task(self, task_id: int):
        return (
            self.db.query(Comment)
            .filter(Comment.task_id == task_id)
            .all()
        )

    def delete(self, comment: Comment):
        self.db.delete(comment)
        self.db.commit()