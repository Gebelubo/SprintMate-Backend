from fastapi import FastAPI
from src.db.db import Database
from src.routers import user

db = Database()

app = FastAPI()

app.include_router(user.router)

@app.on_event("startup")
async def startup_event():
    print("ok")
    db.test_connection()
    db.create_tables()

@app.get("/")
def health_check():
    return "It's working"