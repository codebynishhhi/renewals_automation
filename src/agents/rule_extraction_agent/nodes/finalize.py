import logging
import uuid
from src.common.database import AsyncSessionLocal
from src.api import crud
from src.agents.rule_extraction_agent.state import RuleExtractionAgentState

logger = logging.getLogger(__name__)

async def finalize(state:RuleExtractionAgentState) -> dict:
    artifact_id = uuid.UUID(state["artifact_id"])

    # update databse status with "extracted"
    async with AsyncSessionLocal() as db:
        artifact = await crud.get_artifact(db, artifact_id)
        if artifact:
            artifact.status = "extracted"
            await db.commit()

    logger.info("Artifact %s marked as extracted | rules=%d", artifact_id, state.get("rules_written",0))
    return {"status": "extracted"}