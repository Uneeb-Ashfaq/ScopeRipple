
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Define the information needed to create a project
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


# Define the project information returned by the API
class ProjectResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    # Allow Pydantic to read SQLAlchemy model attributes
    model_config = ConfigDict(from_attributes=True)
