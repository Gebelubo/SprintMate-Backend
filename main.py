from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.db import get_db_instance
from src.routers import user, auth, task, me

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(task.router)
app.include_router(me.router)

@app.on_event("startup")
async def startup_event():
    db = get_db_instance()
    db.test_connection()
    db.create_tables()

@app.get("/")
def health_check():
    return "It's working"
