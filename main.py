from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3
from contextlib import closing

from database import init_db
from repositories import task_repository

init_db()

# class Task(BaseModel):
#   id: int | None = None
#   title: str
#   done: bool | None = False

app = FastAPI()

def get_db():
  return sqlite3.connect("tasks.db")

def _normalize_title(task_title: str) -> str:
  return task_title.strip().lower()

def _title_taken(normalized_task_title: str, exclude_id: int | None = None) -> bool:
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      """
      SELECT id, title
      FROM tasks  
      """
    )

    for id, title in cur:
      if exclude_id is not None and id == exclude_id:
        continue
      if _normalize_title(title) == normalized_task_title:
        return True
    return False

def _not_found(task_id: int) -> HTTPException:
  return HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail={"error": f"Task {task_id} not found"}
  )

def _bad_request(msg: str) -> HTTPException:
  return HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"error": msg}
  )


# --------------------------------------------------------------------------
# 1. Home
# --------------------------------------------------------------------------

@app.get("/", description="Home")
async def root():
  return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

# --------------------------------------------------------------------------
# 2. Health
# --------------------------------------------------------------------------

@app.get("/health", description="Provides the status of the API")
async def health():
  return {"status": "ok"}

# --------------------------------------------------------------------------
# 3. Get all tasks
# --------------------------------------------------------------------------

@app.get("/tasks", description="Output all the tasks")
async def getAll():
  return task_repository.getAll()

# --------------------------------------------------------------------------
# 4. Get specific tasks by ID
# --------------------------------------------------------------------------

@app.get("/tasks/{id}", description="Output a specified task")
async def getTask(id: int):
  res = task_repository.find_task(id)

  if res:
    return res
  raise _not_found(id)

# --------------------------------------------------------------------------
# 5. Get all finished task
# --------------------------------------------------------------------------

@app.get("/tasks/", description="Filter task by done")
async def getDoneTask(done: bool = True):
  doneTask = []

  for i in range(len(tasks)):
    if tasks[i].get("done") == done:
      doneTask.append(tasks[i])

  if not doneTask:
    raise HTTPException(status_code=404, detail={"error": "No Task Found"})
  
  return doneTask

# --------------------------------------------------------------------------
# 6. Tasks Statistics
# --------------------------------------------------------------------------

@app.get("/stats", description="Provides stats of tasks")
async def getStats():
  if not tasks:
    raise HTTPException(status_code=404, detail={"error": "No Task Found"})
  
  totalTask = len(tasks)
  countDone = 0

  for i in range(totalTask):
    if tasks[i].get("done") == True:
      countDone += 1

  return {"total": totalTask, "done": countDone, "open": totalTask - countDone}

# --------------------------------------------------------------------------
# 7. Create a new task
# --------------------------------------------------------------------------

@app.post("/tasks", status_code=201, description="Create a new task")
async def createTask(title: str):
  normalized = _normalize_title(title)

  # Error Handling
  if not normalized:
    raise _bad_request("A task title cannot be empty")
  elif _title_taken(normalized):
    raise _bad_request(f"A task title '{title}' already exists")

  # Insert New Task
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      """
      INSERT INTO tasks (title, done)
      VALUES (?, ?)
      """,
      (title, 0)
    )
    con.commit()
    
    cur.execute(
      """
      SELECT *
      FROM tasks
      WHERE title = ?
      """,
      (title,)
    )
    res = cur.fetchall()

    return res

# --------------------------------------------------------------------------
# 8. Update task
# --------------------------------------------------------------------------

@app.put("/tasks/{id}", description="Update a specified task")
async def updateTask(id: int, title: str | None = None, done: bool | None = None):
  if not task_repository.find_task(id):
    raise _not_found(id)

  if title is None and done is None:
    raise _bad_request("Provide at least one of 'title' or 'done' to update")

  if title is not None:
    normalized = _normalize_title(title)
    if not normalized:
      raise _bad_request("A task title cannot be empty")
    if _title_taken(normalized, exclude_id=id):
      raise _bad_request(f"A task title '{title}' already exists")
    task_repository.update_title(id, title)

  if done is not None:
    task_repository.update_done(id, done)

  return task_repository.find_task(id)

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a specified task")
async def deleteTask(id: int):
  if not task_repository.find_task(id):
    raise _not_found(id)

  task_repository.delete_task(id)