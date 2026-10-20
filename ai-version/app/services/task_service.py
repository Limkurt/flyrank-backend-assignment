from app.database import Task
from app.repositories.task_repository import TaskRepository


class TaskNotFoundError(Exception):
    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task with id {task_id} not found")
        self.task_id = task_id


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def list_tasks(self) -> list[Task]:
        return self.repository.get_all()

    def get_task(self, task_id: int) -> Task:
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def list_tasks_by_done(self, done: bool) -> list[Task]:
        return self.repository.get_by_done(done)

    def get_stats(self) -> dict[str, int]:
        return {
            "total": self.repository.count_total(),
            "done": self.repository.count_by_done(True),
            "pending": self.repository.count_by_done(False),
        }

    def create_task(self, title: str, done: bool) -> Task:
        return self.repository.create(title=title.strip(), done=done)

    def update_task(self, task_id: int, title: str, done: bool) -> Task:
        task = self.get_task(task_id)
        return self.repository.update(task, title=title.strip(), done=done)

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.repository.delete(task)
