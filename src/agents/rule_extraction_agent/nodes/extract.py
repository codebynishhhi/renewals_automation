import logging
from src.api.schema import ExtractedRule, ExtractRulesList
from src.agents.rule_extraction_agent.state import RuleExtractionAgentState
from src.common.settings import settings
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

def extract_rules(state : RuleExtractionAgentState) -> dict:
    """
    Node 3 : Send the retrieved chunks to LLM, get structred rules as output
    with_structured_output forces LLM to generate valid ExtractedRule JSON
    """

    chunks = state["retrieved_chunks"]

    if not chunks:
        logger.warning("No chunks retrieved !")
        return {"extracted_rules" : []}
    
    # build context from the chunks
    context = "\n\n--\n\n".join(f"[Page {c['page']}]\n{c['text']}" for c in chunks)

    # give that context to llm
    llm = ChatOpenAI(
        model=settings.model_name,
        temperature=0.3,
        api_key=settings.groq_api_key or "placeholder"
    )

    structured_llm = llm.with_structured_output(ExtractedRule)

    prompt = f"""
    You are an expert at extracting configuration rules from hardware product specifications, with diffrenet file types - pdfs, excels etc.
    Read the following excerpts and extract all configuration rules you find.
    Each rule must have a clear if condition then conditom 

    Document exceprt:{context}
    Rule if example - 
    if - processror = r60 and core =  4
    condition = then something hardware configuration
    Extract all the possible rules.
    Be specific and precise
    """
    try:
        result : ExtractRulesList = structured_llm.invoke(prompt)
        rules = [r.model_dump() for r in result.rules]
        logger.info("Extracted %d rules from %d chunks", len(rules), len(chunks))
        return {"extracted_rules":rules}
    except Exception as e:
        logger.error("Rule extraction failed: %s", e)
        return {"extracted_rules":[]}

