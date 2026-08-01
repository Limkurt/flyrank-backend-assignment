"""
To-Do List CRUD API
====================
A simple in-memory To-Do list API built with FastAPI.

Run with:
    uvicorn main:app --reload

Swagger UI:
    http://127.0.0.1:8000/docs
ReDoc:
    http://127.0.0.1:8000/redoc
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# --------------------------------------------------------------------------
# App metadata / instance
# --------------------------------------------------------------------------

API_VERSION = "1.1.0"

app = FastAPI(
    title="To-Do List API",
    description="A simple CRUD API for managing a to-do list, backed by an in-memory store.",
    version=API_VERSION,
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------


class TaskCreate(BaseModel):
    """Payload for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200, description="The task title")
    done: bool = Field(default=False, description="Whether the task is completed")

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()


class Task(BaseModel):
    id: int = Field(..., description="Unique task identifier")
    title: str
    done: bool


class ErrorResponse(BaseModel):
    error: str
    detail: str


class StatsResponse(BaseModel):
    total: int
    done: int
    not_done: int


# --------------------------------------------------------------------------
# In-memory "database"
# --------------------------------------------------------------------------

tasks_db: List[dict] = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Write project report", "done": True},
    {"id": 3, "title": "Schedule dentist appointment", "done": False},
]

# DESIGN DECISION (stated explicitly, not silent): ids are unique only among
# currently active tasks, not globally unique forever. A new task always gets
# the SMALLEST positive integer not currently in use -- not just max+1. That
# means deleting task 2 out of [1,2,3] leaves a hole at 2, and the next task
# created fills that hole (gets id=2) rather than skipping straight to 4.
# If you need ids to never be reused across the lifetime of the service,
# replace this with a monotonic counter that is never derived from tasks_db.


def _get_next_id() -> int:
    existing_ids = {t["id"] for t in tasks_db}
    candidate = 1
    while candidate in existing_ids:
        candidate += 1
    return candidate


def _find_task_index(task_id: int) -> Optional[int]:
    for idx, t in enumerate(tasks_db):
        if t["id"] == task_id:
            return idx
    return None


def _normalize_title(title: str) -> str:
    return title.strip().lower()


def _title_taken(title: str, exclude_id: Optional[int] = None) -> bool:
    """DESIGN DECISION (stated explicitly): titles must be unique among
    currently active tasks, compared case-insensitively after trimming
    whitespace. 'Buy milk' and '  buy milk  ' are treated as duplicates."""
    normalized = _normalize_title(title)
    for t in tasks_db:
        if exclude_id is not None and t["id"] == exclude_id:
            continue
        if _normalize_title(t["title"]) == normalized:
            return True
    return False


def _bad_request(msg: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": "Bad Request", "detail": msg},
    )


def _not_found(task_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "Not Found", "detail": f"Task with id {task_id} not found"},
    )


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Turns FastAPI/Pydantic's default 422 validation errors (missing fields,
    wrong types, unparsable path/query params, etc.) into a consistent
    400 Bad Request with the same JSON error shape used everywhere else.
    """
    messages = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
        msg = err.get("msg", "Invalid value")
        messages.append(f"{loc}: {msg}" if loc else msg)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {
                "error": "Bad Request",
                "detail": "; ".join(messages) if messages else "Invalid request body",
            }
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Ensures every HTTPException (400s, 404s, etc.) responds with a
    consistent JSON error shape: {"error": ..., "detail": ...}
    """
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail and "detail" in detail:
        content = detail
    else:
        content = {"error": _status_to_label(exc.status_code), "detail": str(detail)}

    return JSONResponse(status_code=exc.status_code, content=content)


def _status_to_label(code: int) -> str:
    return {
        400: "Bad Request",
        404: "Not Found",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }.get(code, "Error")


# --------------------------------------------------------------------------
# 1. Home
# --------------------------------------------------------------------------


@app.get(
    "/",
    tags=["Meta"],
    summary="API info",
    status_code=status.HTTP_200_OK,
)
def read_root():
    """Returns basic information about this API."""
    return {
        "name": "To-Do List API",
        "version": API_VERSION,
        "description": "A simple CRUD API for managing a to-do list.",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "GET /": "API info",
            "GET /health": "Health check",
            "GET /tasks": "Retrieve all tasks",
            "GET /tasks/{id}": "Retrieve a task by ID",
            "GET /tasks/": "Retrieve all tasks filtered by done status (?done=true|false)",
            "GET /stats": "Retrieve task statistics grouped by done status",
            "POST /tasks": "Create a new task",
            "PUT /tasks/{id}": "Update an existing task (?title=...&done=...)",
            "DELETE /tasks/{id}": "Delete a task",
        },
    }


# --------------------------------------------------------------------------
# 2. Health
# --------------------------------------------------------------------------


@app.get(
    "/health",
    tags=["Meta"],
    summary="Health check",
    status_code=status.HTTP_200_OK,
)
def health_check():
    """Simple liveness/health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# --------------------------------------------------------------------------
# 3. Retrieve all tasks
# --------------------------------------------------------------------------


@app.get(
    "/tasks",
    tags=["Tasks"],
    summary="Retrieve all tasks",
    response_model=List[Task],
    status_code=status.HTTP_200_OK,
)
def get_tasks():
    """Returns the full list of tasks currently stored."""
    return tasks_db


# --------------------------------------------------------------------------
# 5. Retrieve all tasks filtered by done status
#    Route is "/tasks/" (matching the original spec) rather than a renamed
#    "/tasks/filter/{done}". Declaration order relative to "/tasks/{id}"
#    doesn't matter here -- "/tasks/" (empty id segment) can never match an
#    int path param, so FastAPI falls through to this route correctly
#    regardless of order. Verified empirically.
# --------------------------------------------------------------------------


@app.get(
    "/tasks/",
    tags=["Tasks"],
    summary="Retrieve all tasks by done status",
    response_model=List[Task],
    status_code=status.HTTP_200_OK,
    responses={400: {"model": ErrorResponse, "description": "Missing or invalid 'done' value"}},
)
def get_tasks_by_done(
    done: bool = Query(
        ...,
        description="Filter tasks by completion status: true or false. Required.",
    ),
):
    """
    Returns all tasks whose `done` field matches the given boolean.

    DESIGN DECISION (stated explicitly): a filter that matches zero tasks is
    NOT a 404. The collection /tasks/ exists; it just has no members meeting
    the filter, so this returns 200 with an empty list -- consistent with
    /stats never 404ing on an empty store either. 404 is reserved for
    "this specific task id doesn't exist" (see get_task, update_task,
    delete_task below), not "this query returned nothing."
    """
    return [t for t in tasks_db if t["done"] == done]


# --------------------------------------------------------------------------
# 6. Stats
# --------------------------------------------------------------------------


@app.get(
    "/stats",
    tags=["Tasks"],
    summary="Retrieve task statistics by done status",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
)
def get_stats():
    """Returns counts of total / done / not-done tasks. Always 200, even
    when the store is empty (0/0/0 is a valid, non-error state)."""
    total = len(tasks_db)
    done_count = sum(1 for t in tasks_db if t["done"])
    return {
        "total": total,
        "done": done_count,
        "not_done": total - done_count,
    }


# --------------------------------------------------------------------------
# 4. Retrieve a task by ID
# --------------------------------------------------------------------------


@app.get(
    "/tasks/{id}",
    tags=["Tasks"],
    summary="Retrieve a task by ID",
    response_model=Task,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Task not found"}},
)
def get_task(id: int = Path(..., description="The ID of the task to retrieve")):
    """No lower-bound constraint on id: 0 or a negative number is a
    syntactically valid integer that simply doesn't match any task, so it
    falls through to the same 404 as any other unknown id -- not a separate
    400 validation error."""
    idx = _find_task_index(id)
    if idx is None:
        raise _not_found(id)
    return tasks_db[idx]


# --------------------------------------------------------------------------
# 7. Create a new task
# --------------------------------------------------------------------------


@app.post(
    "/tasks",
    tags=["Tasks"],
    summary="Create a new task",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse, "description": "Invalid or duplicate title"}},
)
def create_task(payload: TaskCreate):
    if _title_taken(payload.title):
        raise _bad_request(f"A task titled '{payload.title}' already exists")

    new_task = {
        "id": _get_next_id(),
        "title": payload.title,
        "done": payload.done,
    }
    tasks_db.append(new_task)
    return new_task


# --------------------------------------------------------------------------
# 8. Update an existing task
#    Takes title/done as query params (partial update), matching the
#    original design rather than requiring a full JSON body replace.
# --------------------------------------------------------------------------


@app.put(
    "/tasks/{id}",
    tags=["Tasks"],
    summary="Update an existing task",
    response_model=Task,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid, empty, or duplicate title"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
def update_task(
    id: int = Path(..., description="The ID of the task to update"),
    title: Optional[str] = Query(default=None, description="New title (optional)"),
    done: Optional[bool] = Query(default=None, description="New done status (optional)"),
):
    idx = _find_task_index(id)
    if idx is None:
        raise _not_found(id)

    if title is None and done is None:
        raise _bad_request("Provide at least one of 'title' or 'done' to update")

    if title is not None:
        if not title.strip():
            raise _bad_request("Title cannot be empty")
        if _title_taken(title, exclude_id=id):
            raise _bad_request(f"A task titled '{title}' already exists")
        tasks_db[idx]["title"] = title.strip()

    if done is not None:
        tasks_db[idx]["done"] = done

    return tasks_db[idx]


# --------------------------------------------------------------------------
# 9. Delete a task
# --------------------------------------------------------------------------


@app.delete(
    "/tasks/{id}",
    tags=["Tasks"],
    summary="Delete a task",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse, "description": "Task not found"}},
)
def delete_task(id: int = Path(..., description="The ID of the task to delete")):
    idx = _find_task_index(id)
    if idx is None:
        raise _not_found(id)
    tasks_db.pop(idx)
    return None
