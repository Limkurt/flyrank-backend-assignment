from database import get_db

def get_all() -> list[tuple]:
  with get_db() as con:
    with con.cursor() as cur:

      cur.execute("SELECT * FROM tasks")

      return cur.fetchall()

def find_task(task_id: int) -> tuple | None:
  with get_db() as con:
    with con.cursor() as cur:

      cur.execute(
        "SELECT * FROM tasks WHERE id = %s",
        (task_id,)
      )
      return cur.fetchone()

def getDone(task_done: bool) -> list[tuple]:
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      "SELECT * FROM tasks WHERE done = ?",
      (task_done,)
    )

    return cur.fetchall()

def create_task(task_title: str) -> tuple:
  with get_db() as con:
    with con.cursor() as cur:

      cur.execute(
        """
        INSERT INTO tasks (title, done)
        VALUES (%s, %s)
        RETURNING *
        """,
        (task_title, False)
      )

      return cur.fetchone()

def update_title(task_id: int, task_title: str) -> None:
  with get_db() as con:
    with con.cursor() as cur:

      cur.execute(
        "UPDATE tasks SET title = %s WHERE id = %s",
        (task_title, task_id)
      )

def update_done(task_id: int, task_done: bool) -> None:
  with get_db() as con:
    with con.cursor() as cur:

      cur.execute(
        "UPDATE tasks SET done = %s WHERE id = %s",
        (task_done, task_id)
      )

def delete_task(task_id: int) -> None:
  with get_db() as con:
    with con.cursor() as cur:

      cur.execute(
        "DELETE FROM tasks WHERE id = %s",
        (task_id,)
      )