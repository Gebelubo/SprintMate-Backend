from src.db.db import Database
from fastapi import FastAPI

db = Database()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("ok")
    db.test_connection()
    db.create_tables()

@app.get("/")
def health_check():
    return "It's working"