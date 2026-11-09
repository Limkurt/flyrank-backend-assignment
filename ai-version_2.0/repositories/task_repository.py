from dataclasses import dataclass

from psycopg_pool import ConnectionPool


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool


class TaskRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def list_all(self) -> list[Task]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            ).fetchall()
        return [Task(**row) for row in rows]

    def list_by_status(self, done: bool) -> list[Task]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT id, title, done FROM tasks WHERE done = %s ORDER BY id",
                (done,),
            ).fetchall()
        return [Task(**row) for row in rows]

    def get(self, task_id: int) -> Task | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s", (task_id,)
            ).fetchone()
        return Task(**row) if row else None

    def create(self, title: str, done: bool) -> Task:
        with self._pool.connection() as conn:
            row = conn.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) "
                "RETURNING id, title, done",
                (title, done),
            ).fetchone()
        assert row is not None
        return Task(**row)

    def update(self, task_id: int, title: str, done: bool) -> Task | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s "
                "RETURNING id, title, done",
                (title, done, task_id),
            ).fetchone()
        return Task(**row) if row else None

    def delete(self, task_id: int) -> bool:
        with self._pool.connection() as conn:
            cur = conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            return cur.rowcount > 0

    def count(self) -> tuple[int, int]:
        """Return (total, completed)."""
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS total, "
                "COUNT(*) FILTER (WHERE done) AS completed FROM tasks"
            ).fetchone()
        assert row is not None
        return int(row["total"]), int(row["completed"])
