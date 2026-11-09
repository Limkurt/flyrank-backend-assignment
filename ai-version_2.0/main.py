from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from database import check_connection, close_pool, init_db, open_pool
from exceptions import register_exception_handlers
from router import auth, tasks


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    open_pool()
    init_db()
    try:
        yield
    finally:
        close_pool()


app = FastAPI(
    title="CRUD API",
    version="1.0.0",
    description="RESTful CRUD API with FastAPI, Postgres and Supabase Auth.",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(tasks.router)
app.include_router(auth.router)


@app.get("/", tags=["system"], summary="Home")
def home() -> dict[str, str]:
    return {
        "message": "Welcome to the CRUD API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["system"], summary="API health check")
def health() -> JSONResponse:
    ok = check_connection()
    return JSONResponse(
        status_code=200 if ok else 503,
        content={"status": "ok" if ok else "degraded", "database": "up" if ok else "down"},
    )
