"""
Configuration for the system.
"""

from os import environ

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

DATABASE_HOST = environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = environ.get("DATABASE_PORT", "5432")
DATABASE_NAME = environ.get("DATABASE_NAME", "shl24")
DATABASE_USER = environ.get("DATABASE_USER", "shl24")
DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD", "shl24")
DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

INDEX_NAME = environ.get("INDEX_NAME", "SaintHighLoad2024")
DATA_PATH = environ.get("DATA_PATH", "./data")
WEAVIATE_DATA_PATH = environ.get("WEAVIATE_DATA_PATH", "./weaviate")
HYBRID_ALPHA = float(environ.get("HYBRID_ALPHA", 0.5))
WEAVIATE_SEARCH_TOP_K = int(environ.get("WEAVIATE_SEARCH_TOP_K", 2))
CHUNK_SIZE = int(environ.get("CHUNK_SIZE", 1024))
CHUNK_OVERLAP = int(environ.get("CHUNK_OVERLAP", 20))
BRAVE_SEARCH_API_KEY = environ.get("BRAVE_SEARCH_API_KEY", "")
LOG_LEVEL = environ.get("LOG_LEVEL", "DEBUG")

YANDEX_API_KEY = environ.get("YANDEX_API_KEY", "")
YANDEX_FOLDER_ID = environ.get("YANDEX_FOLDER_ID", "")


class LogConfig(BaseModel):
    """Logging configuration"""

    LOGGER_NAME: str = "shl24"
    LOG_FORMAT: str = (
        "%(asctime)s\t%(process)d\t%(thread)d\t%(name)-40s\t%(levelname)-8s%(message)s"
    )
    LOG_LEVEL: str = LOG_LEVEL

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers: dict = {
        "": {"handlers": ["default"], "level": LOG_LEVEL},
        "httpx": {"handlers": ["default"], "level": "ERROR"},
        "httpcore": {"handlers": ["default"], "level": "INFO"},
        "urllib3": {"handlers": ["default"], "level": "INFO"},
        "multipart": {"handlers": ["default"], "level": "INFO"},
    }
