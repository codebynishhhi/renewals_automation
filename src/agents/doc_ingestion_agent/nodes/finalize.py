import logging
import uuid
from datetime import datetime, timezone
from src.common.database import AsyncSessionLocal
from src.api import crud
from src.agents.doc_ingestion_agent.state import DocumentIngestionAgentState


logger = logging.getLogger()

async def finalize(state:DocumentIngestionAgentState) -> dict:
    """
    Node 5 : Mark artifact as processed in DB.
    """
    artifact_id = state["artifact_id"]
    async with AsyncSessionLocal() as db:
        artifact = await crud.get_artifact_by_hash(db, artifact_id)
        if artifact:
            artifact.status = "processed"
            await db.commit()

        
    logger.info("Finalized artifacts=%s | chunks_written = %d", artifact_id, state.get("embeddings_written", 0))
    return {"status":"processed"}