from src.db.db import get_db_instance
from sqlalchemy.orm import Session
from typing import Generator


def get_db() -> Generator[Session, None, None]:
    db = get_db_instance()
    with db.get_session() as session:
        yield session
