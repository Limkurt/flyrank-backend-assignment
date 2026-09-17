"""
database.py

Owns the SQLite connection lifecycle and schema/seed initialization.
No business logic lives here — only connection management and bootstrapping.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DB_PATH = Path(__file__).parent / "app.db"


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection with sane defaults."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name (row["title"])
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """
    Request-scoped connection context manager.

    Usage:
        with get_db() as conn:
            repo = TaskRepository(conn)
            ...
    Commits on success, rolls back on exception, always closes.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Create the `tasks` table if it doesn't exist, and seed it with
    3 dummy tasks if it's empty. Called once at application startup.
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done  BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()

        row = conn.execute("SELECT COUNT(*) AS count FROM tasks").fetchone()
        if row["count"] == 0:
            dummy_tasks = [
                ("Buy groceries", 0),
                ("Finish backend API assignment", 0),
                ("Read a book", 1),
            ]
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)", dummy_tasks
            )
            conn.commit()
    finally:
        conn.close()
