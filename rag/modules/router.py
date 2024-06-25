"""
Query router - determines user's intent and either sends request to Weaviate, or to
internet search module.
"""

from logging import getLogger
from typing import Optional

from llama_index.core import PromptTemplate, Response
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.tools import QueryEngineTool

from rag.llm import get_llm
from rag.llm.yandex import YandexLLM
from rag.modules import internet, search

logger = getLogger(__name__)


class RAGQueryEngine(CustomQueryEngine):
    """Own RAG query engine with web search support"""

    TOOLS_PROMPT: PromptTemplate = PromptTemplate(
        "Ниже представлен список инструментов.\n"
        "---------------------\n"
        "{tools_str}\n"
        "---------------------\n"
        "Выбери инструмент из этого списка, наиболее подходящий для обработки запроса. "
        "Ответ должен включать только имя инструмента и ничего больше.\n"
        "Запрос: {query_str}\n"
        "Инструмент:"
    )

    llm: YandexLLM
    tools: list[QueryEngineTool]

    def custom_query(self, query_str: str) -> str:
        """Custom query handler"""
        logger.debug("custom_query, query_str=%s", query_str)

        # buiding a tool list for an LLM
        tools_str: str = "\n\n".join(
            [f"{t.metadata.name}: {t.metadata.description}" for t in self.tools]
        )
        prompt: str = self.TOOLS_PROMPT.format(tools_str=tools_str, query_str=query_str)
        logger.debug("custom_query, prompt=%s", prompt)
        selected_tool: str = str(self.llm.complete(prompt)).strip()

        # some modules continue generation after tool selection
        if "\n" in selected_tool:
            selected_tool = selected_tool[: selected_tool.find("\n")].strip()

        logger.debug("custom_query, selected_tool=%s", selected_tool)

        tool_obj: Optional[QueryEngineTool] = None

        for tool in self.tools:
            if selected_tool == tool.metadata.name:
                tool_obj = tool
                break

        if tool_obj is None:
            return "Unknown tool: " + selected_tool

        return tool_obj.call(query_str).content


def run(query: str) -> str:
    """Run the router."""
    logger.debug("run, query=%s", query)

    router: RAGQueryEngine = RAGQueryEngine(
        llm=get_llm(),
        tools=[search.get_tool(), internet.get_tool()],
    )

    response: Response = router.query(query)
    response_text: str = response.response

    if response_text == "Empty Response":
        response_text = "Извините, я не могу найти ответ на ваш запрос."

    logger.debug("run, querying router, got response=%s", response.response)

    return response_text
