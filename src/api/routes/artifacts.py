import uuid
import logging
from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException, BackgroundTasks
from src.common.database import AsyncSessionLocal
from src.common.database import get_db
from src.api.schema import ArtifactResponse  # Adjust to match your schema file path
from src.api.services import artifacts as artifact_service
from src.agents.rule_extraction_agent.agent import RuleExtractionAgent
from src.agents.doc_ingestion_agent.agent import DocumentIngestionAgent
from src.api import crud
import asyncio
from fastapi import BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.models import Rules

logger = logging.getLogger(__name__)

#  CLEAN STATIC PREFIX
router = APIRouter(prefix="/api/v1/projects", tags=["Artifacts"])

# ----------------------- Artifacts --------------------------

#  DYNAMIC VARIABLE MOVED INTO THE ROUTE PATH
@router.post("/{project_id}/artifacts", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def upload_artifact(
    project_id: uuid.UUID, 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    return await artifact_service.upload_artifacts(db, project_id=project_id, file=file)

# ROUTE PATH MATCHES POST LAYOUT EXACTLY & FIXED response_model
@router.get("/{project_id}/artifacts", response_model=list[ArtifactResponse])
async def list_all_artifacts(
    project_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db)
):
    return await artifact_service.list_artifacts(db, project_id)


@router.post("/{artifact_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_artifacts(project_id : uuid.UUID,background_tasks: BackgroundTasks, artifact_id:uuid.UUID, db:AsyncSession = Depends(get_db)):
    """ Trigger document ingestion agent for uploaded artifacts """
    # fetch the artifact
    artifact = await crud.get_artifact(db, artifact_id)
    logger.info("getting the artifact | id=%s", artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found!")
    if artifact.status != "uploaded":
        raise HTTPException(status_code=404, detail=f"Artifact status is {artifact.status} ,expected 'uploaded")
    
    # update the status to processing 
    artifact.status = "processing"
    await db.commit()

    # run agent in backgrond so api return response immediately
    async def run_agent():

        # Instantiate your agent worker object structure
        agent = DocumentIngestionAgent(workflow_run_id = str(artifact_id))
        await agent.run(
            {
                "workflow_run_id" : str(artifact_id),
                "project_id": str(project_id),
                "artifact_id" : str(artifact_id),
                "storage_key" : artifact.storage_key
            }
        )

    background_tasks.add_task(run_agent)
    # RIGHT: Truthful async status
    return {"status": "processing", "artifact_id": artifact_id}

@router.get("/{artifact_id}/status")
async def get_extraction_status(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """ Check if the extraction background worker is finished and view generated rules count """
    clean_artifact_id = artifact_id.strip()
    
    # 1. Fetch the artifact metadata state row
    artifact = await crud.get_artifact(db, clean_artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found!")
        
    # 2. Count how many rules have been generated and written to the DB for this artifact
    result = await db.execute(
        select(func.count(Rules.id)).where(Rules.artifact_id == uuid.UUID(clean_artifact_id))
    )
    rules_count = result.scalar_one_or_none() or 0

    return {
        "artifact_id": clean_artifact_id,
        "status": artifact.status,  # Will dynamically transition: "extracting" -> "extracted"
        "rules_generated_count": rules_count
    }

# ------------------------------- Rules ---------------------------------------

@router.post("/{artifact_id}/extract", status_code=status.HTTP_202_ACCEPTED)
async def extract_rules(project_id:str, background_tasks: BackgroundTasks, artifact_id : str, db : AsyncSession = Depends(get_db)):
    """ Trigger rule extraction agent. Artifact must be in processed state """
    # 1. Clean the incoming strings to remove accidental tabs (\t) or spaces
    clean_project_id = project_id.strip()
    clean_artifact_id = artifact_id.strip()
    artifact = await crud.get_artifact(db, clean_artifact_id)

    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found for extraction!")
    
    if artifact.status != "processed":
        raise HTTPException(status_code=400, detail=f"Artifact must be processed first got - {artifact.status}")
    
    artifact.status = "extracting"
    await db.commit()

    async def run_agent():
        try:
            logger.info("Starting background RuleExtractionAgent pipeline for artifact: {}", clean_artifact_id)
            agent = RuleExtractionAgent(workflow_run_id=str(artifact_id))

            # run the ai graph
            await agent.run({
                "workflow_run" : clean_artifact_id,
                "project_id": clean_project_id,
                "artifact_id":str(artifact_id),
                "storage_key" : artifact.storage_key
            })
            logger.info("RuleExtractionAgent background task finished successfully!")
        except Exception as e:
            logger.warning("Background extraction agent failed!")
            logger.error("Error message:{str(e)}")

            # reset database row status to failed using a fresh connection
            async with AsyncSessionLocal() as db:
                err_artifact = await crud.get_artifact(db, clean_artifact_id)
                if err_artifact:
                    err_artifact.status = "failed"
                    await db.commit()
                    logger.warning("Artifact status reset to 'failed' due to background crash.")

    # 3. Queue the task safely using FastAPI's official manager
    background_tasks.add_task(run_agent)
    return {"status":"extracting", "artifact_id":str(artifact_id)}