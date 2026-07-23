from typing import TypedDict

class RuleExtractionAgentState(TypedDict, total = False):
    # ----------- input ----------------
    workflow_run_id : str
    project_id : str
    artifact_id : str
    storage_key : str

    # ------------ Node 1 - plan queries --------------
    # LLM generated search queries
    retrieval_queries : list[str]

    # ------------ Node 2 - reterieve -----------------
    # top-k chunks from pgvector per query
    retrieved_chunks : list[dict]

    # ------------ Node 3 - extract_rule --------------
    # structured llm rules
    extracted_rules : list[dict]

    # ------------ Node 4 - write rules --------------
    rules_written : int

    # ------------ Node 5 - finalize -------------
    status : str
    error : str | None 