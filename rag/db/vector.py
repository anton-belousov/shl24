"""
Vector database connection logic.
"""

from logging import getLogger
from typing import Optional

from langchain_community.embeddings.yandex import YandexGPTEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.vector_stores.weaviate import WeaviateVectorStore

from rag.config import (
    INDEX_NAME,
    WEAVIATE_HOST,
    WEAVIATE_PORT,
    YANDEX_API_KEY,
    YANDEX_FOLDER_ID,
)
from weaviate import WeaviateClient, connect_to_local

_client: Optional[WeaviateClient] = None
_store: Optional[WeaviateVectorStore] = None
_model: Optional[LangchainEmbedding] = None

logger = getLogger(__name__)


def get_vector_store() -> WeaviateVectorStore:
    """Get the Weaviate vector store."""
    global _client
    global _store

    if _store is not None:
        return _store

    if _client is None:
        _client = connect_to_local(host=WEAVIATE_HOST, port=WEAVIATE_PORT)

    _store = WeaviateVectorStore(_client, index_name=INDEX_NAME)

    return _store


def get_embedding_model() -> LangchainEmbedding:
    """
    Get embedding model
    """
    global _model

    if _model is not None:
        return _model

    logger.debug("get_embedding_model, loading model")
    _model = LangchainEmbedding(
        YandexGPTEmbeddings(api_key=YANDEX_API_KEY, folder_id=YANDEX_FOLDER_ID)
    )

    return _model


def stop():
    """Stop weaviate"""
    global _client

    if _client is not None:
        del _client
        _client = None
