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
    return result.scalar_one_or_none

async def get_all_projects(db:AsyncSession,limit:int = 20, offset:int = 20) -> list[Project] | None:
    result = await db.execute(select(Project).order_by(Project.created_at.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())
