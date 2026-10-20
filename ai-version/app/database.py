import os
import time
from collections.abc import Generator

from sqlalchemy import Boolean, Text, create_engine, false, func, select, text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/tasks_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    done: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _wait_for_database(retries: int = 15, delay: float = 2.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception:
            if attempt == retries:
                raise
            time.sleep(delay)


def init_db() -> None:
    """Create the tasks table if missing and seed 3 tasks if it is empty."""
    _wait_for_database()
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(Task)) or 0
        if count == 0:
            db.add_all(
                [
                    Task(title="Learn FastAPI", done=True),
                    Task(title="Build a CRUD API", done=False),
                    Task(title="Write documentation", done=False),
                ]
            )
            db.commit()
