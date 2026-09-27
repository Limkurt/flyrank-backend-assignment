from fastapi import FastAPI
from routers import tasks
from database import init_db

init_db()

app = FastAPI()

app.include_router(tasks.router)




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

