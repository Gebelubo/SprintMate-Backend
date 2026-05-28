from src.db.db import Database

db = Database()

def get_db():
    with db.get_session() as session:
        yield session