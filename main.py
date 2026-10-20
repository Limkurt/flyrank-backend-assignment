from fastapi import FastAPI
from routers import tasks
from database import init_db

init_db()

app = FastAPI()

app.include_router(tasks.router)