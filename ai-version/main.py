"""
main.py

FastAPI application entrypoint. Defines Pydantic schemas and HTTP routes,
and wires each request to the TaskRepository via a fresh SQLite
connection (see database.get_db). No SQL lives in this file.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from database import get_db, init_db
from repositories.task_repository import TaskRepository


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, examples=["Buy milk"])
    done: bool = False


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, examples=["Buy milk"])
    done: bool = False


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool


class TaskStats(BaseModel):
    total: int
    done: int
    not_done: int


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # create table + seed 3 dummy tasks if empty
    yield


app = FastAPI(
    title="Tasks CRUD API",
    description="A minimal RESTful CRUD API for managing tasks, backed by SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


def _row_to_task(row) -> TaskOut:
    return TaskOut(id=row["id"], title=row["title"], done=bool(row["done"]))


# ---------------------------------------------------------------------------
# Home / Health
# ---------------------------------------------------------------------------
@app.get("/", tags=["Home"], summary="Home")
def home() -> dict:
    return {"message": "Welcome to the Tasks CRUD API. Visit /docs for Swagger UI."}


@app.get("/health", tags=["Health"], summary="Check API status")
def health_check() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Tasks — reads
# NOTE: /tasks/ (filter by done) is declared before /tasks/{task_id} so the
# static path always wins; Starlette also would not match an empty path
# segment against {task_id}, but ordering it this way keeps intent explicit.
# ---------------------------------------------------------------------------
@app.get("/tasks", response_model=list[TaskOut], tags=["Tasks"], summary="Retrieve all tasks")
def get_all_tasks() -> list[TaskOut]:
    with get_db() as conn:
        rows = TaskRepository(conn).get_all()
    return [_row_to_task(r) for r in rows]


@app.get(
    "/tasks/",
    response_model=list[TaskOut],
    tags=["Tasks"],
    summary="Retrieve all tasks by done",
)
def get_tasks_by_done(
    done: bool = Query(..., description="Filter tasks by their done status"),
) -> list[TaskOut]:
    with get_db() as conn:
        rows = TaskRepository(conn).get_by_done(done)
    return [_row_to_task(r) for r in rows]


@app.get("/stats", response_model=TaskStats, tags=["Tasks"], summary="Retrieve tasks stats by done")
def get_stats() -> TaskStats:
    with get_db() as conn:
        stats = TaskRepository(conn).get_stats()
    return TaskStats(**stats)


@app.get("/tasks/{task_id}", response_model=TaskOut, tags=["Tasks"], summary="Retrieve a task by ID")
def get_task(task_id: int) -> TaskOut:
    with get_db() as conn:
        row = TaskRepository(conn).get_by_id(task_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task {task_id} not found")
    return _row_to_task(row)


# ---------------------------------------------------------------------------
# Tasks — writes
# ---------------------------------------------------------------------------
@app.post(
    "/tasks",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    summary="Create a new task",
)
def create_task(task: TaskCreate) -> TaskOut:
    with get_db() as conn:
        row = TaskRepository(conn).create(task.title, task.done)
    return _row_to_task(row)


@app.put("/tasks/{task_id}", response_model=TaskOut, tags=["Tasks"], summary="Update an existing task")
def update_task(task_id: int, task: TaskUpdate) -> TaskOut:
    with get_db() as conn:
        row = TaskRepository(conn).update(task_id, task.title, task.done)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task {task_id} not found")
    return _row_to_task(row)


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
    summary="Delete a task",
)
def delete_task(task_id: int) -> None:
    with get_db() as conn:
        deleted = TaskRepository(conn).delete(task_id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task {task_id} not found")
