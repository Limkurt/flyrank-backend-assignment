from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from contextlib import closing

#Dummy data
data = [
  { "id": 1, "title": "Draw", "done": False}, 
  { "id": 2, "title": "Watch", "done": False},
  { "id": 3, "title": "Listen", "done": False}
]

#Create table
con = sqlite3.connect("tasks.db")
cur = con.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT ,
  done BOOLEAN
);
'''

cur.execute(create_table_query)
con.commit()

#Insert Query
cur.execute("SELECT EXISTS(SELECT 1 FROM tasks)")
is_empty = cur.fetchone()[0] == 0 # Checks if table has data

if is_empty:
  for item in data:
    cur.execute(
      """
      INSERT INTO tasks (title, done)
      VALUES (?, ?)      
      """,
      (item["title"], item["done"])
    )

  con.commit()
con.close()

class Task(BaseModel):
  id: int | None = None
  title: str
  done: bool | None = False

app = FastAPI()

def get_db():
  return sqlite3.connect("tasks.db")

# def _find_task_index(task_id: int):
#   for idx, t in enumerate(tasks):
#     if t["id"] == task_id:
#       return idx
#   return None

def _not_found(task_id: int) -> HTTPException:
  return HTTPException(
      status_code=404,
      detail={"error": f"Task {task_id} not found"}
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
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute("SELECT * FROM tasks")
    res = cur.fetchall()

    return res

# --------------------------------------------------------------------------
# 4. Get specific tasks by ID
# --------------------------------------------------------------------------

@app.get("/tasks/{id}", description="Output a specified task")
async def getTask(id: int):
  with closing(get_db()) as con:
    cur = con.cursor()

    cur.execute(
      """
      SELECT *
      FROM tasks
      WHERE id = ?
      """,
      (id,)
    )
    res = cur.fetchall()

    if res:
      return res
    return _not_found(id)

@app.get("/tasks/", description="Filter task by done")
async def getDoneTask(done: bool = True):
  doneTask = []

  for i in range(len(tasks)):
    if tasks[i].get("done") == done:
      doneTask.append(tasks[i])

  if not doneTask:
    raise HTTPException(status_code=404, detail={"error": "No Task Found"})
  
  return doneTask

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

@app.post("/tasks", status_code=201, description="Create a new task")
async def createTask(task: Task):
  if not task.title.strip():
    raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})

  new_task = {
    "id": len(tasks) + 1,
    "title": task.title,
    "done": task.done
  }

  tasks.append(new_task)

  return new_task

@app.put("/tasks/{id}", description="Update a specified task")
async def updateTask(id: int, title: str | None = None, done: bool | None = None):
  if id <= len(tasks) and id > 0:
    if title is not None and done is not None:
      tasks[id - 1]["title"] = title
      tasks[id - 1]["done"] = done
    elif title is not None:
      tasks[id - 1]["title"] = title
    elif done is not None:
      tasks[id - 1]["done"] = done
    else:
      raise HTTPException(status_code=400, detail={"error": "Empty/invalid body"})

  else:
    raise HTTPException(status_code=404, detail={"error": "Unknown id"})

  return tasks[id - 1]

@app.delete("/tasks/{id}", status_code=204, description="Delete a specified task")
async def deleteTask(id: int):
  if id <= len(tasks) and id > 0 and tasks[id - 1]["id"] == id:
    tasks.pop(id - 1)

    return {
      "message": "Delete successful"
    }

  else:
    raise HTTPException(status_code=404, detail={"error": "Unknown id"})