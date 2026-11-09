
from typing import Literal

from pydantic import BaseModel, Field


# Define the information needed to create a graph node
class NodeCreate(BaseModel):
    node_id: str = Field(min_length=1, max_length=100)
    node_type: Literal["agent", "tool", "resource"]
    sensitivity: Literal[
        "public", "internal", "confidential", "restricted"
    ] = "public"


# Define the information needed to create a permission
class PermissionCreate(BaseModel):
    source: str
    target: str
    action: Literal["read", "write", "execute"]
