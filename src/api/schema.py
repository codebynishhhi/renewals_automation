import uuid
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

#---------------------------- Projects -------------------------------
class ProjectCreate(BaseModel):
    """ What the user send in payload """
    name : str
    description: str | None = None
    created_by : str 
    created_at : str | None = None

class ProjectStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ProjectResponse(BaseModel):
    """ What response backend sends """
    id : uuid.UUID
    name : str
    description : str | None 
    status : ProjectStatusEnum
    created_at : datetime

    model_config = {"from_attributes":True} 
