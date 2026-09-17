"""
repositories/task_repository.py

Data-access layer for the `tasks` table. Every raw SQL statement in the
app lives here — main.py never talks to sqlite3 directly.
"""

import sqlite3
from typing import Optional


class TaskRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_all(self) -> list[sqlite3.Row]:
        cursor = self.conn.execute("SELECT id, title, done FROM tasks ORDER BY id")
        return cursor.fetchall()

    def get_by_id(self, task_id: int) -> Optional[sqlite3.Row]:
        cursor = self.conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        )
        return cursor.fetchone()

    def get_by_done(self, done: bool) -> list[sqlite3.Row]:
        cursor = self.conn.execute(
            "SELECT id, title, done FROM tasks WHERE done = ? ORDER BY id",
            (int(done),),
        )
        return cursor.fetchall()

    def get_stats(self) -> dict:
        cursor = self.conn.execute(
            "SELECT done, COUNT(*) AS count FROM tasks GROUP BY done"
        )
        rows = cursor.fetchall()

        stats = {"total": 0, "done": 0, "not_done": 0}
        for row in rows:
            stats["total"] += row["count"]
            if row["done"]:
                stats["done"] = row["count"]
            else:
                stats["not_done"] = row["count"]
        return stats

    def create(self, title: str, done: bool = False) -> sqlite3.Row:
        cursor = self.conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", (title, int(done))
        )
        new_id = cursor.lastrowid
        row = self.get_by_id(new_id)
        assert row is not None  # just inserted, must exist
        return row

    def update(self, task_id: int, title: str, done: bool) -> Optional[sqlite3.Row]:
        existing = self.get_by_id(task_id)
        if existing is None:
            return None
        self.conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title, int(done), task_id),
        )
        return self.get_by_id(task_id)

    def delete(self, task_id: int) -> bool:
        existing = self.get_by_id(task_id)
        if existing is None:
            return False
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return True
