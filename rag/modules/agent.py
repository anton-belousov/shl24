"""
Query router - determines user's intent and either sends request to Weaviate, or to
internet search module.
"""

from logging import getLogger
from typing import Optional

from llama_index.core import PromptTemplate, Response
from llama_index.core.llms import ChatMessage, ChatResponse, MessageRole
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.tools import QueryEngineTool

from rag.llm import get_llm
from rag.llm.yandex import YandexLLM
from rag.modules import internet, search
from rag.modules.guard import is_prompt_injection

logger = getLogger(__name__)


class AgentQueryEngine(CustomQueryEngine):
    """Agent query engine"""

    MAX_CALLS: int = 5
    SYSTEM_PROMPT: PromptTemplate = PromptTemplate(
        """Ты - агент, обрабатывающий запросы пользователя. Помоги пользователю найти ответ на его вопрос.
        
Cписок инструментов, их параметры и описание.
---------------------
{tools_str}

stop: Ответ был найден ранее и присутствует в контексте, остановить обработку запроса и дальнейшие вызовы инструментов.
---------------------

Твоя задача - ответить на запрос пользователя, используя наиболее подходящий инструмент из списка.
Не вызывай один и тот же инструмент несколько раз с одинаковыми параметрами.
Если ответ на запрос присутствует в истории, используй инструмент 'stop' для завершения обработки запроса и возврата ответа.

Если запрос состоит из нескольких частей, разбей его на несколько вопросов и используй несколько инструментов последовательно для обработки запроса.
Ответ должен содержать только имя инструмента и параметры для его вызова."""
    )

    SUMMARIZE_PROMPT: PromptTemplate = PromptTemplate(
        """Первоначальный запрос пользователя:
---------------------
{query_str}
---------------------

История вызовов инструментов:
---------------------
{tool_history_str}
---------------------

Твоя задача - суммаризировать ответы инструментов и ответить на вопрос пользователя.
Ответ:"""
    )

    llm: YandexLLM
    tools: list[QueryEngineTool]

    def summarize(self, query: str, tool_history: dict) -> str:
        """
        Summarize the query using the tool history and the query itself.
        """
        logger.debug("summarize, query=%s, tool_history=%s", query, tool_history)

        prompt: str = self.SUMMARIZE_PROMPT.format(
            query_str=query,
            tool_history_str="\n\n".join(
                [f"{k}\n{v}" for k, v in tool_history.items()]
            ),
        )
        logger.debug("summarize, prompt=%s", prompt)

        return str(self.llm.complete(prompt)).strip()

    def custom_query(self, query_str: str) -> str:
        """Custom query handler"""
        logger.debug("custom_query, query_str=%s", query_str)

        if is_prompt_injection(self.llm, query_str):
            logger.warning("custom_query, possible prompt injection detected")
            return "Извините, я не могу найти ответ на ваш запрос."

        current_response: str = ""
        tool_history = {}

        # buiding a tool list for an LLM
        tools = []

        for tool in self.tools:
            tools.append(f"{tool.metadata.name}(query): {tool.metadata.description}")

        tools_str: str = "\n\n".join(tools)

        messages: list[ChatMessage] = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=self.SYSTEM_PROMPT.format(tools_str=tools_str),
            ),
            ChatMessage(role=MessageRole.USER, content=query_str),
        ]
        current_call: int = 0

        while current_call < self.MAX_CALLS:
            logger.debug("custom_query, current_call=%s", current_call)
            response: ChatResponse = self.llm.chat(messages)
            messages.append(response.message)

            selected_tool: str = str(response.message.content).strip()
            logger.debug("custom_query, selected_tool=%s", selected_tool)

            tool_name: str = selected_tool.split("(", maxsplit=1)[0].strip()
            tool_params: str = selected_tool[
                selected_tool.find("(") + 1 : selected_tool.find(")")
            ].strip()

            if tool_params.startswith('"') and tool_params.endswith('"'):
                tool_params = tool_params[1:-1]

            if f'{tool_name}("{tool_params}")' in tool_history:
                logger.warning(
                    "custom_query, tool=%s, params=%s already called",
                    tool_name,
                    tool_params,
                )

                break

            logger.debug(
                "custom_query, tool_name=%s, tool_params=%s", tool_name, tool_params
            )

            if tool_name == "stop":
                break

            else:
                tool_obj: Optional[QueryEngineTool] = None

                for tool in self.tools:
                    if tool_name == tool.metadata.name:
                        tool_obj = tool
                        break

                if tool_obj is None:
                    logger.error("custom_query, unknown tool=%s", tool_name)
                    break

                current_response = tool_obj.call(tool_params).content

            tool_history[f'{tool_name}("{tool_params}")'] = current_response
            messages.append(
                ChatMessage(role=MessageRole.ASSISTANT, content=current_response)
            )
            messages.append(
                ChatMessage(role=MessageRole.USER, content="Следующий инструмент")
            )
            current_call += 1

        if len(tool_history) > 0:
            current_response = self.summarize(query_str, tool_history)

        if not current_response:
            current_response = "Извините, я не могу найти ответ на ваш запрос."

        return current_response


def run(query: str) -> str:
    """Run the router."""
    logger.debug("run, query=%s", query)

    agent: AgentQueryEngine = AgentQueryEngine(
        llm=get_llm(),
        tools=[search.get_tool(), internet.get_tool()],
    )

    response: Response = agent.query(query)
    response_text: str = response.response

    if response_text == "Empty Response":
        response_text = "Извините, я не могу найти ответ на ваш запрос."

    logger.debug("run, querying router, got response=%s", response.response)

    return response_text
