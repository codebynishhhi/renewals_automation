import uuid
import logging
from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database import get_db
from src.api.schema import ArtifactResponse  # Adjust to match your schema file path
from src.api.services import artifacts as artifact_service
from src.agents.doc_ingestion_agent.agent import DocumentIngestionAgent
from src.api import crud
from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)

#  CLEAN STATIC PREFIX
router = APIRouter(prefix="/api/v1/projects", tags=["Artifacts"])

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
        agent = DocumentIngestionAgent(workflow_run_id=str(artifact_id))
        await agent.run(
            {
                "workflow_run_id" : str(artifact_id),
                "project_id":project_id,
                "artifact_id" : artifact_id,
                "storage_key" : artifact.storage_key
            }
        )

    background_tasks.add_task(run_agent)
    return {"status" :"processing", "artifact_id":str(artifact_id)}
