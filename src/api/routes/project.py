import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.schema import ProjectCreate, ProjectResponse
from src.api.services import project as project_service
from src.common.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

# Always place your static (literal text) routes completely ABOVE your dynamic (variable parameter) routes.

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload:ProjectCreate,
    db : AsyncSession = Depends(get_db)
):
    project = await project_service.create_project(
        db, name=payload.name, created_by=payload.created_by
    )
    return project

@router.get("/all_projects", response_model=list[ProjectResponse])
async def get_all_projects(limit : int = 20, offset : int = 0, db: AsyncSession = Depends(get_db)):
    projects = await project_service.get_all_projects(db, limit=limit, offset=offset)
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id : uuid.UUID, db : AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db,project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found!")
    return project


    