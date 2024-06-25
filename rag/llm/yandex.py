"""
Yandex GPT LLM for LlamaIndex
"""

from logging import getLogger
from typing import Any, Generator, Sequence

from langchain_community.chat_models.yandex import ChatYandexGPT
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from llama_index.core.base.llms.types import CompletionResponse
from llama_index.core.llms import (
    LLM,
    ChatMessage,
    ChatResponse,
    ChatResponseAsyncGen,
    CompletionResponseAsyncGen,
    CompletionResponseGen,
    LLMMetadata,
    MessageRole,
)
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback

logger = getLogger(__name__)


class YandexLLM(LLM):
    """
    Yandex GPT LLM for LlamaIndex
    """

    yandex_gpt: ChatYandexGPT

    @property
    def metadata(self) -> LLMMetadata:
        """
        LLM metadata.

        Returns:
            LLMMetadata: LLM metadata containing various information about the LLM.
        """
        return LLMMetadata(
            model_name="yandexgpt",
            context_window=8000,
            num_output=2000,
            is_chat_model=True,
            is_function_calling_model=False,
        )

    @llm_chat_callback()
    async def achat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        logger.debug("achat, messages=%s", messages)
        return ChatResponse(
            message=ChatMessage(
                role=MessageRole.ASSISTANT, content="Hello, I am Yandex GPT!"
            )
        )

    @llm_chat_callback()
    async def astream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponseAsyncGen:
        logger.debug("astream_chat, messages=%s", messages)

        async def gen() -> ChatResponseAsyncGen:
            for message in [
                ChatResponse(
                    message=ChatMessage(
                        role=MessageRole.ASSISTANT, content="Hello, I am Yandex GPT!"
                    )
                )
            ]:
                yield message

        return gen()

    @llm_completion_callback()
    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        logger.debug("acomplete, prompt=%s, formatted=%s", prompt, formatted)
        return await super().acomplete(prompt, formatted, **kwargs)

    @llm_completion_callback()
    async def astream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        logger.debug("astream_complete, prompt=%s, formatted=%s", prompt, formatted)
        return await super().astream_complete(prompt, formatted, **kwargs)

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        logger.debug("chat, messages=%s", messages)
        converted_messages: list[BaseMessage] = []

        for message in messages:
            if message.role == MessageRole.USER:
                converted_messages.append(HumanMessage(content=message.content))
            elif message.role == MessageRole.SYSTEM:
                converted_messages.append(SystemMessage(content=message.content))
            elif message.role == MessageRole.ASSISTANT:
                converted_messages.append(AIMessage(content=message.content))

        result_message: BaseMessage = self.yandex_gpt.invoke(converted_messages)

        return ChatResponse(
            message=ChatMessage(
                role=MessageRole.ASSISTANT, content=result_message.content
            )
        )

    @llm_chat_callback()
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> Generator[ChatResponse, None, None]:
        logger.debug("stream_chat, messages=%s", messages)
        return super().stream_chat(messages, **kwargs)

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        logger.debug("complete, prompt=%s, formatted=%s", prompt, formatted)
        result: BaseMessage = self.yandex_gpt.invoke(prompt)
        return CompletionResponse(text=result.content)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        logger.debug("stream_complete, prompt=%s, formatted=%s", prompt, formatted)
        return super().stream_complete(prompt, formatted, **kwargs)

    @classmethod
    def class_name(cls) -> str:
        return "YandexLLM"
