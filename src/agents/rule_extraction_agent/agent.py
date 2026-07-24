import logging
from src.agents.rule_extraction_agent.state import RuleExtractionAgentState 
from src.agents.base import BaseAgent
from src.agents.rule_extraction_agent.nodes import plan_queries, retrieve, write_rules, extract, finalize
from langgraph.graph import StateGraph, END

class RuleExtractionAgent(BaseAgent):

    def build_graph(self):
        graph = StateGraph(RuleExtractionAgentState)

        # add all nodes
        graph.add_node("plan_queries",plan_queries)
        graph.add_node("retrieve", retrieve)
        graph.add_node("extract_rules", extract)
        graph.add_node("write_rules", write_rules)
        graph.add_node("finalize", finalize)

        graph.set_entry_point("plan_queries")
        graph.add_edge("plan_queries", "retrieve")
        graph.add_edge("retrieve", "extract_rules")
        graph.add_edge("extract_rules", "write_rules")
        graph.add_edge("write_rules", "finalize")
        graph.add_edge("finalize", END)

        return graph.compile(checkpointer=self.checkpointer)