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
    #  1. Convert the incoming string id into a clean UUID object
    artifact_id = uuid.UUID(str(state["artifact_id"]))

    async with AsyncSessionLocal() as db:
        artifact = await crud.get_artifact(db, artifact_id)
        if artifact:
            artifact.status = "processed"
            await db.commit()
            logger.info("Successfully updated database status to processed for artifact: %s", artifact_id)

        else:
            logger.error("Could not find artifact in database to finalize: %s", artifact_id)
            
    logger.info("Finalized artifacts=%s | chunks_written = %d", artifact_id, state.get("embeddings_written", 0))
    return {"status":"processed"}