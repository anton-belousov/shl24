"""
Main app entry point
"""

from contextlib import asynccontextmanager
from logging import getLogger
from os import environ

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from rag.api.chat import router
from rag.app import configure_database, configure_logging

configure_logging()
logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Lifespan event handler

    Args:
        app (FastAPI): FastAPI instance
    """
    logger.info("lifespan, starting up")
    await configure_database()
    yield

    logger.info("lifespan, shutting down")


app: FastAPI = FastAPI(
    title="SHL24",
    description="Saint HighLoad++ 2024",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router, prefix="/chat", tags=["chat"])


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom swagger configuration
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url, title=app.title + " - Swagger UI"
    )


if __name__ == "__main__":
    workers: int = int(environ.get("API_WORKERS", "1"))
    port: int = int(environ.get("API_PORT", "8000"))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        log_config=None,
    )
