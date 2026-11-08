from fastapi import FastAPI, Request
from routers import tasks, auth
from database import init_db

from services.auth_service import InvalidAuthError
from fastapi.responses import JSONResponse

init_db()

app = FastAPI()

app.include_router(tasks.router)
app.include_router(auth.router)

@app.exception_handler(InvalidAuthError)
async def invalid_auth_handler(request: Request, exc: InvalidAuthError):
  return JSONResponse(
    status_code=401,
    content={"error": str(exc)},
    headers={"WWW-Authenticate": "Bearer"}
  )