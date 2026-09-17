from contextlib import closing

from database import get_db

def find_task(task_id: int) -> tuple | None:
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      "SELECT * FROM tasks WHERE id = ?",
      (task_id,)
    )
    return cur.fetchone()

def getAll() -> list[tuple]:
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute("SELECT * FROM tasks")

    return cur.fetchall()

def getDone(task_done: bool) -> list[tuple]:
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      "SELECT * FROM tasks WHERE done = ?",
      (task_done,)
    )

    return cur.fetchall()

def update_title(task_id: int, task_title: str) -> None:
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      "UPDATE tasks SET title = ? WHERE id = ?",
      (task_title, task_id)
    )
    con.commit()

def update_done(task_id: int, task_done: bool) -> None:
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      "UPDATE tasks SET done = ? WHERE id = ?",
      (task_done, task_id)
    )
    con.commit()

def delete_task(task_id: int) -> None:
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      "DELETE FROM tasks WHERE id = ?",
      (task_id,)
    )
    con.commit()