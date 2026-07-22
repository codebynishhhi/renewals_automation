import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.api import crud
from src.api.models import Project

logger = logging.getLogger(__name__)

async def create_project(db:AsyncSession, name:str, created_by : str) -> Project:
    """
    Business logic goes in here. Right now - it just calls CRUD
    As the app grows we add - validation, events, notification here
    """
    project = await crud.create_project(db, name = name, created_by=created_by)
    logger.info("Project Created | id= %s", project.id)
    return project

async def get_project(db:AsyncSession, project_id:uuid) -> Project | None:
    return await crud.get_project(db, project_id)

async def get_all_projects(db:AsyncSession, limit:int= 20, offset:int = 0) -> list[Project]:
    return await crud.get_all_projects(db, limit= limit, offset=offset)