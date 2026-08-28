import os

from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessagesState, StateGraph

from agents.nodes import (
    create_planner_node,
    create_recipe_node,
    create_router_node,
    reject_node,
)
from tools.mcp_loader import load_mcp_tools
from utils.logger import setup_logger

logger = setup_logger()
graph_app = None


class CustomState(MessagesState):
    next_nodes: list[str]


async def setup_graph() -> None:
    """
    Компиляция графа.
    """
    global graph_app

    logger.info("Инициализация LLM")
    llm = ChatOpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_HOST"),
        model=os.getenv("LLM_MODEL"),
        temperature=0.0,
    )

    all_tools = await load_mcp_tools()

    logger.info("Создание узлов графа (все инструменты доступны всем агентам)")

    graph = StateGraph(CustomState)

    graph.add_node("router", create_router_node(llm))
    graph.add_node("recipes", create_recipe_node(llm, all_tools))
    graph.add_node("planner", create_planner_node(llm, all_tools))
    graph.add_node("reject", reject_node)

    graph.set_entry_point("router")

    def route_decision(state: CustomState) -> dict:
        nodes_to_visit = state.get("next_nodes", ["reject"])
        if isinstance(nodes_to_visit, str):
            nodes_to_visit = [nodes_to_visit]

        logger.info(f"Роутер направляет запрос в узлы: {nodes_to_visit}")
        return nodes_to_visit

    graph.add_conditional_edges(
        "router",
        route_decision,
        {"recipes": "recipes", "planner": "planner", "reject": "reject"},
    )

    graph.add_edge("recipes", END)
    graph.add_edge("planner", END)
    graph.add_edge("reject", END)

    graph_app = graph.compile()
    logger.info("LangGraph успешно скомпилирован")


def get_graph() -> StateGraph:
    """
    Получает граф.
    """
    if graph_app is None:
        raise RuntimeError("Граф не инициализирован. Вызовите setup_graph() первым.")
    return graph_app
