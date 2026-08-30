import os
from datetime import datetime, timedelta, timezone
from typing import Callable, Literal, Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool
from langgraph.graph import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel


def get_moscow_datetime() -> tuple[str, str]:
    """
    Возвращает текущие дату и время в московском часовом поясе (UTC+3).
    """
    msk_tz = timezone(timedelta(hours=3))
    now = datetime.now(msk_tz)
    return now.strftime("%Y-%m-%d"), now.strftime("%H-%M")


def load_prompt(filename: str) -> str:
    """
    Загрузка промптов из файлов относительно текущей директории.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


class RouterDecision(BaseModel):
    """
    Структура ответа роутера, валидируемая через Pydantic.
    """
    intent: list[Literal["recipes", "planner", "reject"]]
    reason: str


def create_router_node(
    llm: BaseChatModel,
) -> Callable[[MessagesState], dict[str, list[str]]]:
    """
    Создание нода роутера для определения намерений пользователя.
    """
    router_llm = llm.with_structured_output(RouterDecision)
    system_prompt = load_prompt("router.txt")

    def router_node(state: MessagesState) -> dict[str, list[str]]:
        messages_with_system = [{"role": "system", "content": system_prompt}] + state[
            "messages"
        ]
        decision: RouterDecision = router_llm.invoke(messages_with_system)

        valid_intents: list[str] = [i for i in decision.intent if i != "reject"]

        if not valid_intents:
            return {"next_nodes": ["reject"]}

        return {"next_nodes": valid_intents}

    return router_node


def create_recipe_node(
    llm: BaseChatModel, tools: Sequence[BaseTool]
) -> CompiledStateGraph:
    """
    Создание нода по рецептам.
    """
    prompt = load_prompt("recipe_agent.txt")
    return create_react_agent(llm, tools, prompt=prompt)


def create_planner_node(
    llm: BaseChatModel, tools: Sequence[BaseTool]
) -> CompiledStateGraph:
    """
    Создание нода по планированию меню.
    """
    prompt_template = load_prompt("planner_agent.txt")
    current_date, current_time = get_moscow_datetime()
    prompt = prompt_template.format(
        current_datetime=f"{current_date} {current_time}",
        current_date=current_date,
        current_time=current_time,
    )
    return create_react_agent(llm, tools, prompt=prompt)


def reject_node(state: MessagesState) -> dict[str, list[AIMessage]]:
    """
    Создание нода по отказу.
    """
    msg = AIMessage(content="Я специализируюсь только на кулинарии!")
    return {"messages": [msg]}
