"""
Application configuration and setup.
"""

from logging import getLogger
from logging.config import dictConfig

from sqlalchemy import text

from rag.config import LogConfig
from rag.db.sql.connection import engine
from rag.db.sql.models import Base

logger = getLogger(__name__)


def configure_logging():
    """Configure logging"""
    dictConfig(LogConfig().model_dump())


async def configure_database():
    """Configure database"""
    async with engine.begin() as db:
        result = await db.execute(
            text(
                """SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND 
                    table_name = 'chat'
                );"""
            )
        )
        exists: bool = result.scalar()
        logger.info("configure_database, tables exist=%s", exists)

        if not exists:
            await db.run_sync(Base.metadata.create_all)
