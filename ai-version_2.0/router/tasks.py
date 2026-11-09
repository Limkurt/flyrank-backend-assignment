from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from pydantic import BaseModel, ConfigDict, Field

from database import pool
from repositories.task_repository import TaskRepository
from services.task_service import TaskService

router = APIRouter(tags=["tasks"])


# ---- schemas -----------------------------------------------------------
class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255, examples=["Buy milk"])
    done: bool = False


class TaskUpdate(BaseModel):
    """PUT replaces the whole task, so both fields are required."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    done: bool


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool


class StatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    completed: int
    pending: int
    completion_rate: float


# ---- dependencies ------------------------------------------------------
def get_task_service() -> TaskService:
    return TaskService(TaskRepository(pool))


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
TaskId = Annotated[int, Path(ge=1, le=2_147_483_647, description="Task ID")]


# ---- endpoints ---------------------------------------------------------
@router.get("/tasks", response_model=list[TaskOut], summary="Retrieve all tasks")
def list_tasks(service: TaskServiceDep) -> list[TaskOut]:
    return [TaskOut.model_validate(t) for t in service.list_tasks()]


@router.get(
    "/tasks/",
    response_model=list[TaskOut],
    summary="Retrieve tasks by status",
)
def list_tasks_by_status(
    service: TaskServiceDep,
    done: Annotated[bool, Query(description="true = completed, false = pending")],
) -> list[TaskOut]:
    return [TaskOut.model_validate(t) for t in service.list_tasks_by_status(done)]


@router.get(
    "/tasks/{task_id}",
    response_model=TaskOut,
    summary="Retrieve a task",
    responses={404: {"description": "Task not found"}},
)
def get_task(task_id: TaskId, service: TaskServiceDep) -> TaskOut:
    return TaskOut.model_validate(service.get_task(task_id))


@router.get("/stats", response_model=StatsOut, summary="Task statistics")
def get_stats(service: TaskServiceDep) -> StatsOut:
    return StatsOut.model_validate(service.get_stats())


@router.post(
    "/tasks", response_model=TaskOut, status_code=201, summary="Create a task"
)
def create_task(payload: TaskCreate, service: TaskServiceDep) -> TaskOut:
    return TaskOut.model_validate(service.create_task(payload.title, payload.done))


@router.put(
    "/tasks/{task_id}",
    response_model=TaskOut,
    summary="Update a task",
    responses={404: {"description": "Task not found"}},
)
def update_task(
    task_id: TaskId, payload: TaskUpdate, service: TaskServiceDep
) -> TaskOut:
    return TaskOut.model_validate(
        service.update_task(task_id, payload.title, payload.done)
    )


@router.delete(
    "/tasks/{task_id}",
    status_code=204,
    response_class=Response,
    summary="Delete a task",
    responses={404: {"description": "Task not found"}},
)
def delete_task(task_id: TaskId, service: TaskServiceDep) -> None:
    service.delete_task(task_id)
