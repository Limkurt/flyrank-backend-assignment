from fastapi import FastAPI
from routers import tasks, auth
from database import init_db

init_db()

app = FastAPI()

app.include_router(tasks.router)
app.include_router(auth.router)