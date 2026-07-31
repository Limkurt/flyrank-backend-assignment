from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

#Dummy data
tasks = [
  { "id": 1, "title": "Draw", "done": False}, 
  { "id": 2, "title": "Watch", "done": False},
  { "id": 3, "title": "Listen", "done": False}
]

class Task(BaseModel):
  id: int | None = None
  title: str
  done: bool | None = False

app = FastAPI()

@app.get("/")
async def root():
  return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
  return {"status": "ok"}

@app.get("/tasks")
def getAll():
  return tasks

@app.get("/tasks/{id}")
async def getTask(id: int):
  if id <= len(tasks) and id > 0:
      return tasks[id - 1]
  else:
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

@app.post("/tasks", status_code=201)
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

@app.put("/tasks/{id}")
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

@app.delete("/tasks/{id}", status_code=204)
async def deleteTask(id: int):
  if id <= len(tasks) and id > 0 and tasks[id - 1]["id"] == id:
    tasks.pop(id - 1)

    return {
      "message": "Delete successful"
    }

  else:
    raise HTTPException(status_code=404, detail={"error": "Unknown id"})