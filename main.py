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
  try:
    return tasks[id + 1]
  except:
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