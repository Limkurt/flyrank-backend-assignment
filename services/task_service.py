from repositories import task_repository

def get_all() -> list[tuple]:
  return task_repository.get_all()

def find_task(task_id: int) -> tuple | None:
  return task_repository.find_task(task_id)