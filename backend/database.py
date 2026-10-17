"""
Flash Flood Early Warning Platform — Database Connection

PostgreSQL + PostGIS + TimescaleDB.
Async connection via asyncpg + SQLAlchemy 2.0.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


engine = None
async_session_factory = None

try:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.app_debug,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
except BaseException:
    # Graceful fallback when PostgreSQL / asyncpg binary is not installed in local env
    pass


async def get_db() -> AsyncSession:
    """Dependency injection for FastAPI routes."""
    if async_session_factory is None:
        yield None
        return
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create tables if they don't exist. For development only — use Alembic in production."""
    async with engine.begin() as conn:
        # Enable PostGIS extension
        await conn.execute(
            __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS postgis;")
        )
        await conn.run_sync(Base.metadata.create_all)
