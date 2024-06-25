"""
SQL connection and session management
"""

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from rag.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(AsyncAttrs, DeclarativeBase):
    """Base model class"""


async def get_db() -> AsyncIterator[AsyncSession]:
    """Get DB connection as async generator, for FastAPI dependencies and post-processing"""
    db: AsyncSession = async_session()

    try:
        yield db
    finally:
        await db.close()
