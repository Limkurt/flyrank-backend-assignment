from fastapi import FastAPI, HTTPException

#Dummy data
tasks = [
  { "id": 1, "title": "Draw", "done": False}, 
  { "id": 2, "title": "Watch", "done": False},
  { "id": 3, "title": "Listen", "done": False}
]

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
    return tasks[id]
  except:
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})