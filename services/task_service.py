from repositories import task_repository

# --------------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------------

class InvalidTaskError(Exception):
  pass

# --------------------------------------------------------------------------
# Validation Helper
# --------------------------------------------------------------------------

def _normalize_title(task_title: str) -> str:
  return task_title.strip().lower()

def _title_taken(normalized_task_title: str, exclude_id: int | None = None) -> bool:
  tasks = task_repository.get_all()

  for id, title, _ in tasks:
    if exclude_id is not None and id == exclude_id:
      continue
    if _normalize_title(title) == normalized_task_title:
      return True
  return False

# --------------------------------------------------------------------------
# Task services
# --------------------------------------------------------------------------

def get_all() -> list[tuple]:
  return task_repository.get_all()

def find_task(task_id: int) -> tuple | None:
  return task_repository.find_task(task_id)

def create_task(task_title: str) -> tuple | Exception:
  normalized_title = _normalize_title(task_title)

  if not normalized_title:
    raise InvalidTaskError("A task title cannot be empty")
  elif _title_taken(normalized_title):
    raise InvalidTaskError(f"A task title '{task_title}' already exists")

  return task_repository.create_task(task_title)

def update_task(task_id: int, task_title: str | None = None, task_done: bool | None = None) -> tuple | Exception:
  if task_title is None and task_done is None:
    raise InvalidTaskError("Provide at least one of 'title' or 'done' to update")

  if task_title is not None:
    normalized_title = _normalize_title(task_title)
    if not normalized_title:
      raise InvalidTaskError("A task title cannot be empty")
    elif _title_taken(normalized_title, exclude_id=task_id):
      raise InvalidTaskError(f"A task title '{task_title}' already exists")
    task_repository.update_title(task_id, task_title)

  if task_done is not None:
    task_repository.update_done(task_id, task_done)

  return task_repository.find_task(task_id)

def delete_task(task_id: int) -> None:
  task_repository.delete_task(task_id)