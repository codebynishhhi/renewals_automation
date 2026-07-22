import logging
import uuid
from src.api import crud
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.models import Artifact
from src.common.minio_client import upload_file, compute_hash

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
ALLOWED_EXTENSIONS = {"pdf", "xlsx"}

async def upload_artifacts(db : AsyncSession, file:UploadFile, project_id : uuid.UUID) -> Artifact:
    """ Upload artifacts function """

    # 1. Validate file_type
    extension = file.filename.rsplit(".",1)[-1].lower() if file.filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type :{extension}. Allowed :{ALLOWED_EXTENSIONS}"
        )

    # 2. Read bytes
    file_bytes = await file.read()
    size_bytes = len(file_bytes)

    # 3. Hash for dedup
    content_hash = compute_hash(file_bytes)
    existing = await crud.get_artifact_by_hash(db, project_id, content_hash)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= f"File already uploaded : artifact_id = {existing.id}"
        )
    
    # 4. Upload to MinIO
    storage_key = f"projects/{project_id}/{file.filename}"
    upload_file(file_bytes, storage_key, content_type=file.content_type or "application/octet-stream")

    # 5. Save metadata to DB
    artifact = await crud.create_artifact(
        db, 
        project_id=project_id,
        name = file.filename,
        file_type=  extension,
        storage_key=storage_key,
        size_bytes=size_bytes,
        content_hash=content_hash
    )
    logger.info("Artifact uploaded | id=%s | project = %s | size= %d", artifact.id, project_id, size_bytes)
    return artifact

async def list_artifacts(db : AsyncSession, project_id:uuid.UUID) -> list[Artifact]:
    return await crud.list_artifacts(db, project_id)