from fastapi import HTTPException, status

def not_found(task_id: int) -> HTTPException:
  return HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail={"error": f"No Task {task_id} found"}
  )

def bad_request(msg: str) -> HTTPException:
  return HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"error": msg}
  )

def invalid_login(msg: str) -> HTTPException:
  return HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"error": msg}
  )