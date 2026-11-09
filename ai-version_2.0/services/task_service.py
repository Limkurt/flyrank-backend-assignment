from dataclasses import dataclass

from exceptions import TaskNotFoundError
from repositories.task_repository import Task, TaskRepository


@dataclass(frozen=True)
class TaskStats:
    total: int
    completed: int
    pending: int
    completion_rate: float  # percent, 0-100


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repo = repository

    def list_tasks(self) -> list[Task]:
        return self._repo.list_all()

    def list_tasks_by_status(self, done: bool) -> list[Task]:
        return self._repo.list_by_status(done)

    def get_task(self, task_id: int) -> Task:
        task = self._repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(self, title: str, done: bool = False) -> Task:
        return self._repo.create(title, done)

    def update_task(self, task_id: int, title: str, done: bool) -> Task:
        task = self._repo.update(task_id, title, done)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def delete_task(self, task_id: int) -> None:
        if not self._repo.delete(task_id):
            raise TaskNotFoundError(task_id)

    def get_stats(self) -> TaskStats:
        total, completed = self._repo.count()
        rate = round(completed / total * 100, 2) if total else 0.0
        return TaskStats(
            total=total,
            completed=completed,
            pending=total - completed,
            completion_rate=rate,
        )
