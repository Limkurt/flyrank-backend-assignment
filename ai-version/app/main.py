from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.router import tasks


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title="CRUD API",
    description="Demonstrates RESTful CRUD operations with FastAPI and Postgres.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(tasks.router)


@app.get("/", tags=["General"], summary="Home")
def home() -> dict[str, str]:
    return {"message": "Welcome to the CRUD API", "docs": "/docs"}


@app.get("/health", tags=["General"], summary="Check API status.")
def health() -> dict[str, str]:
    return {"status": "ok"}
