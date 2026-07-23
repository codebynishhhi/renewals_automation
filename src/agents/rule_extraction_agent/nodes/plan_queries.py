import logging
from langchain_openai import ChatOpenAI
from src.common.settings import settings
from src.agents.rule_extraction_agent.state import RuleExtractionAgentState
logger = logging.getLogger(__name__)

def plan_queries(state:dict) -> dict:
    """
      Node 1 - ask llm to genearte diverse search engine.
      These queries will be used to retrieve releavnt chunks from the pgvector
    """

    llm = ChatOpenAI(
        model=settings.model_name, 
        temperature=0.2,
        api_key=settings.groq_api_key or "placeholder",
    )

    prompt = """
    You are an expert at analyzing hardware documentations with products and features specifications.
    Generate exactly 5 serach queries to find configuration rules in the document
    Cover different aspects :  compatibilty, constraints, eligibilty, validation, pricing.

    Return only a JSON array of 5 search queries. No explanations needed.

    Example : ["Storage compatibilty rules", "memory configuration constraints", "..."]
    """

    response = llm.invoke(prompt)

    # parse the JSON array from response
    import json
    try:
        queries = json.loads(response)
        if not isinstance(queries, list):
            queries = [response.content]

    except json.JSONDecodeError:
        # FALLBACK - split by newlines if llm DOSN'T return valid json
        queries = [line.strip().strip("") for line in response.content.split("\n") if line.strip()[:5]]

    logger.info("Genearted %d retrieval queries", len(queries))
    return {"retrieval_queries": queries}