"""
Indexer module
"""

from logging import getLogger

from rag.app import configure_logging
from rag.modules import indexer

configure_logging()
logger = getLogger(__name__)


def index():
    """Index data from data folder."""
    logger.debug("index")
    indexer.run()


if __name__ == "__main__":
    index()
