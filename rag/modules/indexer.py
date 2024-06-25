"""
Indexer - ingests data from DATA_PATH directory and adds it to Weaviate database.
"""

from logging import getLogger

from llama_index.core import (
    Document,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.weaviate import WeaviateVectorStore

from rag.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_PATH
from rag.db.vector import get_embedding_model, get_vector_store

logger = getLogger(__name__)


def run():
    """Run the indexer."""
    logger.debug("run")

    vector_store: WeaviateVectorStore = get_vector_store()
    documents: list[Document]

    try:
        documents: list[Document] = SimpleDirectoryReader(
            DATA_PATH, recursive=True, exclude=["weaviate"]
        ).load_data()
    except ValueError:
        logger.error("run, no documents found in %s", DATA_PATH)
        return

    logger.debug("run, loaded documents=%s", documents)
    storage_context: StorageContext = StorageContext.from_defaults(
        vector_store=vector_store
    )

    logger.debug("run, creating vector store index")
    index: VectorStoreIndex = VectorStoreIndex.from_documents(
        documents,
        embed_model=get_embedding_model(),
        storage_context=storage_context,
        transformations=[
            SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        ],
        show_progress=True,
    )

    logger.debug(
        "retriever test 1, %s", index.as_retriever().retrieve("Question answering")
    )
    logger.debug("retriever test 2, %s", index.as_retriever().retrieve("MERA"))

    logger.debug("run, vector store index created, %s", index)
