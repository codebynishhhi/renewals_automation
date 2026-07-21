import asyncio
from langgraph.graph import StateGraph, END
from typing import TypedDict
from src.common.logging_config import setup_logging
from src.agents.base import BaseAgent

setup_logging()

# state for dummy agent 
class DummyState(TypedDict):
    message : str

# node 1
def hello_node(state:DummyState) -> dict:
    return {"message":"Hello nishi this side"}

# my dummy test agent
class DummyAgent(BaseAgent):

    def build_graph(self):
        graph = StateGraph(DummyState)
        graph.add_node("hello", hello_node)
        graph.set_entry_point("hello")
        graph.add_edge("hello", END)
        return graph.compile(checkpointer=self.checkpointer)


async def main():
    agent = DummyAgent(workflow_run_id="1")
    result = await agent.run({"message":"start"})
    print(result)

asyncio.run(main())