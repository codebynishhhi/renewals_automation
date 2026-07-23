import uuid
from datetime import datetime
from pydantic import BaseModel, Field
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

# ------------------------------ Artifact --------------------------------
class ArtifactResponse(BaseModel):
    id : uuid.UUID
    project_id : uuid.UUID
    name : str
    file_type : str
    storage_key : str | None
    status : str
    size_bytes : int | None
    uploaded_at :datetime

    model_config = {"from_attributes":True}

# ------------------------------ Rules ----------------------------------
class ExtractedRule(BaseModel):
    """ 
    Extact shape we ask teh llm to produce for each rule. Langchain's with_structured_output forces the LLM to fill this 
    """
    product_name : str = Field(description="Product this rule applies to")
    feature_name : str = Field(description="Feature or category, e.g - Storage, Memory")
    rule_name : str = Field(description="Short description of the rule name")
    rule_type : str = Field(description="One of : configuration, validation , eligiblity")
    condition : str = Field(description="The If part - what triggers this rule")
    if_true : str = Field(description="What happens when condition is true")
    if_false : str | None = Field(default="None", description="What happens when condition is false")
    confidence : float = Field(description="How confident you are 0.0 to 1.0", ge=0.0, le= 1.0) 

class ExtractRulesList(BaseModel):
    """ Wrapper so LLM returns a list of rules in one call. """
    rules : list[ExtractedRule]

