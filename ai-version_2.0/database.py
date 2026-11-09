import os

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool, PoolTimeout

DATABASE_URL: str = os.environ["DATABASE_URL"]

pool: ConnectionPool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    kwargs={"row_factory": dict_row},
    open=False,
)

SEED_TASKS: list[tuple[str, bool]] = [
    ("Set up the project", True),
    ("Build the CRUD endpoints", False),
    ("Write the README", False),
]


def open_pool() -> None:
    pool.open(wait=True, timeout=30.0)


def close_pool() -> None:
    pool.close()


def init_db() -> None:
    """Create the tasks table if missing and seed 3 tasks if it is empty."""
    with pool.connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id    SERIAL PRIMARY KEY,
                title TEXT    NOT NULL,
                done  BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        row = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()
        if row is not None and row["n"] == 0:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)", SEED_TASKS
                )


def check_connection() -> bool:
    try:
        with pool.connection(timeout=2.0) as conn:
            conn.execute("SELECT 1")
        return True
    except (psycopg.Error, PoolTimeout):
        return False
