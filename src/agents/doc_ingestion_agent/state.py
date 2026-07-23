from typing import TypedDict

class DocumentIngestionAgentState(TypedDict):
    # ----- inputs when base agent run() function is called-------
    workflow_run_id : str
    project_id:str
    artifact_id:str
    # minio path to pdf 
    storage_key :str 

    # --------for node 1 - raw_pages to parse as [{page:1, text:""}]----------
    raw_pages : list[dict]

    # ----- for node 2-------
    chunks:list[dict]

    # ------ for node 3 -------
    embeddings_written : int

    # ------ for node 4 --------
    status :str
    error:str | None

