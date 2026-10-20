from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import Task


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[Task]:
        stmt = select(Task).order_by(Task.id)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def get_by_done(self, done: bool) -> list[Task]:
        stmt = select(Task).where(Task.done == done).order_by(Task.id)
        return list(self.db.scalars(stmt).all())

    def count_total(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Task)) or 0

    def count_by_done(self, done: bool) -> int:
        stmt = select(func.count()).select_from(Task).where(Task.done == done)
        return self.db.scalar(stmt) or 0

    def create(self, title: str, done: bool) -> Task:
        task = Task(title=title, done=done)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task, title: str, done: bool) -> Task:
        task.title = title
        task.done = done
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
