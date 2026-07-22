import uuid
import logging
from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database import get_db
from src.api.schema import ArtifactResponse  # Adjust to match your schema file path
from src.api.services import artifacts as artifact_service

logger = logging.getLogger(__name__)

# 🌟 CLEAN STATIC PREFIX
router = APIRouter(prefix="/api/v1/projects", tags=["Artifacts"])

# 🌟 DYNAMIC VARIABLE MOVED INTO THE ROUTE PATH
@router.post("/{project_id}/artifacts", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def upload_artifact(
    project_id: uuid.UUID, 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    return await artifact_service.upload_artifacts(db, project_id=project_id, file=file)

# 🌟 ROUTE PATH MATCHES POST LAYOUT EXACTLY & FIXED response_model
@router.get("/{project_id}/artifacts", response_model=list[ArtifactResponse])
async def list_all_artifacts(
    project_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db)
):
    return await artifact_service.list_artifacts(db, project_id)
