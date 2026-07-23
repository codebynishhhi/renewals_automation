import logging
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.models import Artifact, Project, Rules

logger = logging.getLogger(__name__)

async def create_project(db : AsyncSession, name:str, created_by : str) -> Project:
    project = Project(name = name, created_by = created_by)
    db.add(project)
    # sends insert, assigns project.id - still in transcation
    await db.flush()
    logger.info("Project Created with id= %s", project.id)
    return project

async def get_project(db:AsyncSession, project_id:uuid.UUID) -> Project | None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()

async def get_all_projects(db:AsyncSession,limit:int = 20, offset:int = 20) -> list[Project] | None:
    result = await db.execute(select(Project).order_by(Project.created_at.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())

async def create_artifact(db:AsyncSession, project_id : uuid.UUID, name : str, file_type : str, storage_key : str, size_bytes : int, content_hash :str) -> Artifact:
    """ 
    saves metadata record into postgress so the app knows : 
    - this file exists, where it lives in Minio(storage_key)
    - what project it belogs to 
    - what status it's in
    """
    artifact = Artifact(
        project_id = project_id,
        name = name,
        file_type = file_type,
        storage_key = storage_key,
        size_bytes = size_bytes,
        content_hash = content_hash,
        status = "uploaded"
    )
    db.add(artifact)
    await db.flush()
    logger.info("Created artifact id= %s name = %s", artifact.id, name)
    return artifact

async def get_artifact_by_hash(db :AsyncSession, project_id : uuid.UUID, content_hash : str) -> Artifact | None:
    """ Used to detect duplicate uploads."""
    result = await db.execute(select(Artifact).where(Artifact.project_id == project_id, Artifact.content_hash == content_hash))
    return result.scalar_one_or_none()

async def get_artifact(db: AsyncSession, artifact_id: uuid.UUID) -> Artifact | None:
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id)
    )
    return result.scalar_one_or_none()

async def list_artifacts(db : AsyncSession, project_id : uuid.UUID) -> list[Artifact]:
    result = await db.execute(
        select(Artifact)
        .where(Artifact.project_id == project_id)
        .order_by(Artifact.uploaded_at.desc())
    )
    return result.scalars().all()

