"""
Internet fetcher - creates a QueryEngineTool, that sends query to Brave Search API,
gets first 2 results, fetches their content and asks LLM to answer the query using data
from those 2 websites.
"""

import re
from json import loads
from logging import getLogger

from inscriptis import get_text
from llama_index.core import Document, PromptTemplate
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.tools.brave_search import BraveSearchToolSpec
from requests import Response
from requests import get as http_get

from rag.config import BRAVE_SEARCH_API_KEY
from rag.llm import get_llm
from rag.llm.yandex import YandexLLM

logger = getLogger(__name__)


class InternetSearchQueryEngine(CustomQueryEngine):
    """Own RAG query engine with web search support"""

    ANSWER_PROMPT: PromptTemplate = PromptTemplate(
        "Ниже представлена контекстная информация.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Используя контекстную информацию, а не предыдущие знания, ответь на следующий вопрос.\n"
        "Вопрос: {query_str}\n"
        "Ответ:"
    )

    llm: YandexLLM
    search_tool: BraveSearchToolSpec

    def _clear_text(self, text: str) -> str:
        """Clear text"""
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r" \n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _search(self, query: str) -> list[str]:
        """Search internet and get content list"""
        # get a result list from Brave API
        search_results: list[Document] = self.search_tool.brave_search(query, "ru", 5)
        search_result_list: list[dict] = loads(search_results[0].text)["web"]["results"]
        contents: list[str] = []

        for search_result in search_result_list[:2]:
            logger.debug("_search, fetching url=%s", search_result["url"])
            response: Response = http_get(search_result["url"], timeout=10)
            content: str = get_text(response.text).strip()
            content = self._clear_text(content)

            # avoid too long content
            if len(content) > 1024:
                content = content[:1024]

            contents.append(content)

        return contents

    def custom_query(self, query_str: str) -> str:
        """Custom query handler"""
        logger.debug("custom_query, query_str=%s", query_str)

        search_results: list[str] = self._search(query_str)
        context_str: str = "\n---\n".join(search_results)
        prompt: str = self.ANSWER_PROMPT.format(
            context_str=context_str, query_str=query_str
        )
        logger.debug("custom_query, prompt=%s", prompt)

        result: str = str(self.llm.complete(prompt)).strip()
        logger.debug("custom_query, result=%s", result)

        return result


def get_tool() -> QueryEngineTool:
    """Get internet search query engine."""
    logger.debug("get_tool")

    tool: BraveSearchToolSpec = BraveSearchToolSpec(api_key=BRAVE_SEARCH_API_KEY)
    search_query_engine: InternetSearchQueryEngine = InternetSearchQueryEngine(
        llm=get_llm(), search_tool=tool
    )

    query_engine_tool: QueryEngineTool = QueryEngineTool.from_defaults(
        query_engine=search_query_engine,
        name="internet_search_tool",
        description=(
            "Полезен для поиска информации в интернете по любой теме, не подходящей для других инструментов."
        ),
    )

    return query_engine_tool
