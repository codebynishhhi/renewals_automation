import logging
from src.agents.doc_ingestion_agent.state import DocumentIngestionAgentState
from src.agents.base import BaseAgent
from src.agents.doc_ingestion_agent.nodes import chunk, embed, finalize, parse
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

class DocumentIngestionAgent(BaseAgent):

    def build_graph(self):
        graph = StateGraph(DocumentIngestionAgentState)

        graph.add_node("parse", parse.parse_documents)
        graph.add_node("chunk", chunk.chunk_documents)
        graph.add_node("embed", embed.embed_and_store)
        graph.add_node("finalize", finalize.finalize)

        graph.set_entry_point("parse")
        graph.add_edge("parse","chunk")
        graph.add_edge("chunk", "embed")
        graph.add_edge("embed", "finalize")
        graph.add_edge("finalize", END)

        return graph.compile(checkpointer=self.checkpointer)
    
    
