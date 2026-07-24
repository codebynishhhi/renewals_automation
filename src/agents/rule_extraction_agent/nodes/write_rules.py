import logging
from src.api.models import Rules
from src.agents.rule_extraction_agent.state import RuleExtractionAgentState
from src.common.settings import settings
from src.common.database import AsyncSessionLocal
import uuid

logger = logging.getLogger(__name__)

async def write_rules(state:RuleExtractionAgentState) -> dict:
    extracted_rules = state.get("extracted_rules", [])
    artifact_id = uuid.UUID(str(state["artifact_id"]))

    if not extracted_rules:
        logger.warning("No rules were exctracted, write to db operation failed !")
        return {"rules_written":0}
    
    # write the rules to the db
    async with AsyncSessionLocal() as db:
        for rule_data in extracted_rules:
            rule = Rules(
                artifact_id = artifact_id,
                product_name = rule_data.get("product_name"),
                feature_name = rule_data.get("feature_name"),
                name = rule_data.get("name", "unnamed"),
                rule_type = rule_data.get("rule_type", "configuration"),
                condition = rule_data.get("condition"),
                if_true = rule_data.get("if_true"),
                if_false = rule_data.get("if_false"),
                confidence_score = rule_data.get("confidence"),
                status = "pending_review"
           )
            db.add(rule)
        await db.commit()

    logger.info("Wrote %d rules | artifact=%s", len(extracted_rules), artifact_id)
    return {"rules_written":len(extracted_rules)}

