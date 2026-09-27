from fastapi import FastAPI
from routers import tasks
from database import init_db

init_db()

app = FastAPI()

app.include_router(tasks.router)

# def get_db():
#   return sqlite3.connect("tasks.db")

# def _normalize_title(task_title: str) -> str:
#   return task_title.strip().lower()

# def _title_taken(normalized_task_title: str, exclude_id: int | None = None) -> bool:
#   with closing(get_db()) as con:
#     cur = con.cursor()

#     cur.execute(
#       """
#       SELECT id, title
#       FROM tasks  
#       """
#     )

#     for id, title in cur:
#       if exclude_id is not None and id == exclude_id:
#         continue
#       if _normalize_title(title) == normalized_task_title:
#         return True
#     return False


# # --------------------------------------------------------------------------
# # 5. Get all finished task
# # --------------------------------------------------------------------------

# @app.get("/tasks/", description="Filter task by done")
# async def getDoneTask(done: bool = True):
#   done_tasks = task_repository.getDone(done)

#   if done_tasks:
#     return done_tasks
#   raise _bad_request(f"No found {done} task")

# # --------------------------------------------------------------------------
# # 6. Tasks Statistics
# # --------------------------------------------------------------------------

# @app.get("/stats", description="Provides stats of tasks")
# async def getStats():
#   count_done = len(task_repository.getDone(True))
#   task_total = len(task_repository.getAll())

#   return {"total": task_total, "done": count_done, "open": task_total - count_done}

# # --------------------------------------------------------------------------
# # 7. Create a new task
# # --------------------------------------------------------------------------

# @app.post("/tasks", status_code=201, description="Create a new task")
# async def createTask(title: str):
#   normalized = _normalize_title(title)

#   # Error Handling
#   if not normalized:
#     raise _bad_request("A task title cannot be empty")
#   elif _title_taken(normalized):
#     raise _bad_request(f"A task title '{title}' already exists")

#   # Insert New Task
#   with closing(get_db()) as con:
#     cur = con.cursor()

#     cur.execute(
#       """
#       INSERT INTO tasks (title, done)
#       VALUES (?, ?)
#       """,
#       (title, 0)
#     )
#     con.commit()
    
#     cur.execute(
#       """
#       SELECT *
#       FROM tasks
#       WHERE title = ?
#       """,
#       (title,)
#     )
#     res = cur.fetchall()

#     return res

# # --------------------------------------------------------------------------
# # 8. Update task
# # --------------------------------------------------------------------------

# @app.put("/tasks/{id}", description="Update a specified task")
# async def updateTask(id: int, title: str | None = None, done: bool | None = None):
#   if not task_repository.find_task(id):
#     raise _not_found(id)

#   if title is None and done is None:
#     raise _bad_request("Provide at least one of 'title' or 'done' to update")

#   if title is not None:
#     normalized = _normalize_title(title)
#     if not normalized:
#       raise _bad_request("A task title cannot be empty")
#     if _title_taken(normalized, exclude_id=id):
#       raise _bad_request(f"A task title '{title}' already exists")
#     task_repository.update_title(id, title)

#   if done is not None:
#     task_repository.update_done(id, done)

#   return task_repository.find_task(id)

# @app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a specified task")
# async def deleteTask(id: int):
#   if not task_repository.find_task(id):
#     raise _not_found(id)

#   task_repository.delete_task(id)