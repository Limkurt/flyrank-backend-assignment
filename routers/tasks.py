from fastapi import APIRouter, HTTPException, status
from services import task_service
from services.task_service import InvalidTaskError

router = APIRouter()

# --------------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------------

def _not_found(task_id: int) -> HTTPException:
  return HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail={"error": f"No Task {task_id} found"}
  )

def _bad_request(msg: str) -> HTTPException:
  return HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"error": msg}
  )

# --------------------------------------------------------------------------
# 1. Home
# --------------------------------------------------------------------------

@router.get("/", description="Home")
async def root():
  return {"name": "Task API", "version": "3.0", "endpoints": ["/tasks"]}

# --------------------------------------------------------------------------
# 2. Health
# --------------------------------------------------------------------------

@router.get("/health", description="Provides the status of the API")
async def health():
  return task_service.get_health()

# --------------------------------------------------------------------------
# 3. Get all tasks
# --------------------------------------------------------------------------

@router.get("/tasks", description="Output all the tasks")
async def getAll():
  return task_service.get_all()

# --------------------------------------------------------------------------
# 4. Get specific tasks by ID
# --------------------------------------------------------------------------

@router.get("/tasks/{id}", description="Output a specified task")
async def getTask(id: int):
  task = task_service.find_task(id)

  if task:
    return task

  raise _not_found(id)

# --------------------------------------------------------------------------
# 5. Get all finished task
# --------------------------------------------------------------------------

@router.get("/tasks/", description="Filter task by status")
async def getDoneTask(done: bool):
  tasks = task_service.get_tasks_by_done(done)

  if tasks:
    return tasks

  raise _not_found(done)

# --------------------------------------------------------------------------
# 6. Tasks Statistics
# --------------------------------------------------------------------------

@router.get("/stats", description="Provides stats of tasks")
async def getStats():
  count_done = len(task_service.get_tasks_by_done(True))
  task_total = len(task_service.get_all())

  return {"total": task_total, "done": count_done, "open": task_total - count_done}

# --------------------------------------------------------------------------
# 7. Create a new task
# --------------------------------------------------------------------------

@router.post("/tasks", status_code=201, description="Create a new task")
async def createTask(title: str):
  try:
    return task_service.create_task(title)
  except InvalidTaskError as e:
    raise _bad_request(str(e))

# --------------------------------------------------------------------------
# 8. Update task
# --------------------------------------------------------------------------

@router.put("/tasks/{id}", description="Update a specified task")
async def updateTask(id: int, title: str | None = None, done: bool | None = None):
  try:
    if not task_service.find_task(id):
      raise _not_found(id)
    
    return task_service.update_task(id, title, done)
    
  except InvalidTaskError as e:
    raise _bad_request(str(e))

# --------------------------------------------------------------------------
# 9. Delete task
# --------------------------------------------------------------------------

@router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a specified task")
async def deleteTask(id: int):
  if not task_service.find_task(id):
    raise _not_found(id)

  task_service.delete_task(id)