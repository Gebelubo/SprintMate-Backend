from fastapi import FastAPI
from src.db.db import get_db_instance
from src.routers import user

app = FastAPI()

app.include_router(user.router)

@app.on_event("startup")
async def startup_event():
    db = get_db_instance()
    db.test_connection()
    db.create_tables()

@app.get("/")
def health_check():
    return "It's working"
