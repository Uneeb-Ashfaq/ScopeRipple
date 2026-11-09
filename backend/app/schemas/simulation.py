
from pydantic import BaseModel, Field
from typing import Literal


# Define the information required for a graph node
class NodeInput(BaseModel):
    id: str
    type: Literal["agent", "tool", "resource"]
    sensitivity: Literal["public", "internal", "confidential", "restricted"] = "public"


# Define a permission between two nodes
class PermissionInput(BaseModel):
    source: str
    target: str
    action: Literal["read", "write", "execute"]


# Define a proposed permission change
class ChangeInput(PermissionInput):
    operation: Literal["add", "remove"]


# Define the complete simulation request
class SimulationRequest(BaseModel):
    agent_id: str
    nodes: list[NodeInput] = Field(min_length=1)
    permissions: list[PermissionInput]
    changes: list[ChangeInput]


# Define a simulation request using a saved project
class SavedSimulationRequest(BaseModel):
    agent_id: str
    changes: list[ChangeInput]
