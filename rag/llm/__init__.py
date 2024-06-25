"""
LLM functions
"""

from logging import getLogger
from typing import Optional

from langchain_community.chat_models import ChatYandexGPT

from rag.config import YANDEX_API_KEY, YANDEX_FOLDER_ID
from rag.llm.yandex import YandexLLM

_model: Optional[YandexLLM] = None
logger = getLogger(__name__)


def get_llm() -> YandexLLM:
    """
    Get the LLM model.
    """
    global _model

    if _model is not None:
        return _model

    _model = YandexLLM(
        yandex_gpt=YandexGPT(
            api_key=YANDEX_API_KEY, folder_id=YANDEX_FOLDER_ID, model_name="yandexgpt"
        )
    )

    return _model
