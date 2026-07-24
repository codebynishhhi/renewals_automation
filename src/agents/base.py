import os
import logging
from abc import ABC, abstractmethod
from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from src.common.settings import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):

    def __init__(self, workflow_run_id:str)-> None:
        self.workflow_run_id = workflow_run_id
        self.llm = self.build_llm()
        self.checkpointer = MemorySaver()
        self.langfuse_handler = self.build_langfuse_handler()
        self.state_graph: CompiledStateGraph = self.build_graph()

        logger.info("Agent %s ready | run_id=%s", self.__class__.__name__, self.workflow_run_id)


    def build_llm(self) -> ChatOpenAI:
        """
        ChatOpenAI speaks Open ai protocols 
        Litellm understands that protocol & routes it to specific provider
        Leads to 0 code changes when provider changes
        """

        return ChatOpenAI(
            model=settings.model_name,
            temperature=0,
            api_key=settings.groq_api_key or "placeholder"
        )

    def build_langfuse_handler(self):
        """
        Return langfuse callback handler if keys exist else None
        App works without it - tracing using langfuse is observability
        """
        if not settings.langfuse_public_key or settings.langfuse_secret_key:
            logger.warning("Langfuse key is miising - tracing disabled!")
            return None
        
        try:
            from langfuse.langchain import CallbackHandler
            handler = CallbackHandler(
                public_key=settings.langfuse_public_key,
                secret_key = settings.langfuse_secret_key,
                host = settings.langfuse_host,
                session_id = self.workflow_run_id
            )

            logger.info("Langfuse tracing enabled | session=%s", self.workflow_run_id)

            return handler
        except Exception as e:
            logger.warning("Langfuse unavaible!", e)
            return None
        
    @abstractmethod
    def build_graph(self) -> CompiledStateGraph:
        """
        Each subclass/agent defines its own build_graph function
        """
        ...
    
    async def run(self, inputs : dict[str, Any]) -> dict[str, Any]:
        """
        Run the agent graph
        thread_id = workflow_run_id so Langgraph checkpoints & langfuse also traces
        """
        # for langfuse tracing
        callbacks = [self.langfuse_handler] if self.langfuse_handler else []
        config = {
            "configurable":{"thread_id":self.workflow_run_id},
            "callbacks":callbacks
        }

        logger.info("%s starting run_id=%s", self.__class__.__name__, self.workflow_run_id)
        result = await self.state_graph.ainvoke(inputs, config=config)
        logger.info("%s done | run_id=%s", self.__class__.__name__, self.workflow_run_id)
        return result