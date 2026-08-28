import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage


def load_prompt(filename: str) -> str:
    """
    Загрузка промптов из файлов.
    """
    with open(os.path.join(os.path.dirname(__file__), "..", "prompts", filename), "r", encoding="utf-8") as f:
        return f.read().strip()

class RouterDecision(BaseModel):
    intent: list[Literal["recipes", "planner", "reject"]]
    reason: str

def create_router_node(llm: ChatOpenAI):
    """
    Создание нода роутера.
    """
    router_llm = llm.with_structured_output(RouterDecision)
    system_prompt = load_prompt("router.txt")
    
    def router_node(state: MessagesState):
        messages_with_system = [{"role": "system", "content": system_prompt}] + state["messages"]
        decision: RouterDecision = router_llm.invoke(messages_with_system)
        
        valid_intents = [i for i in decision.intent if i != "reject"]

        if not valid_intents:
            return {"next_nodes": ["reject"]}
            
        return {"next_nodes": valid_intents}
    
    return router_node

def create_recipe_node(llm, tools):
    """
    Создание нода по рецептам.
    """
    prompt = load_prompt("recipe_agent.txt")
    return create_react_agent(llm, tools, prompt=prompt)

def create_planner_node(llm, tools):
    """
    Создание нода по планированию меню.
    """
    prompt = load_prompt("planner_agent.txt")
    return create_react_agent(llm, tools, prompt=prompt)


def reject_node(state: MessagesState):
    """
    Создание нода по отказу.
    """
    msg = AIMessage(content="Я специализируюсь только на кулинарии!")
    return {"messages": [msg]}