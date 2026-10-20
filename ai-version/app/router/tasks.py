from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskNotFoundError, TaskService

router = APIRouter(tags=["Tasks"])


# ---------- Schemas ----------
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, examples=["Buy groceries"])
    done: bool = False


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, examples=["Buy groceries"])
    done: bool


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool


class TaskStats(BaseModel):
    total: int
    done: int
    pending: int


# ---------- Dependency ----------
def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db))


# ---------- Endpoints ----------
@router.get("/tasks", response_model=list[TaskRead], summary="Retrieve all tasks")
def list_tasks(service: TaskService = Depends(get_task_service)):
    return service.list_tasks()


@router.get(
    "/tasks/",
    response_model=list[TaskRead],
    summary="Retrieve all tasks by done",
)
def list_tasks_by_done(
    done: bool = Query(..., description="Filter tasks by completion status"),
    service: TaskService = Depends(get_task_service),
):
    return service.list_tasks_by_done(done)


@router.get(
    "/tasks/{task_id}", response_model=TaskRead, summary="Retrieve a task by ID"
)
def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        return service.get_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/stats", response_model=TaskStats, summary="Retrieve tasks stats by done"
)
def get_stats(service: TaskService = Depends(get_task_service)):
    return service.get_stats()


@router.post(
    "/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    payload: TaskCreate, service: TaskService = Depends(get_task_service)
):
    return service.create_task(title=payload.title, done=payload.done)


@router.put(
    "/tasks/{task_id}", response_model=TaskRead, summary="Update an existing task"
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    try:
        return service.update_task(task_id, title=payload.title, done=payload.done)
    except TaskNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        service.delete_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
