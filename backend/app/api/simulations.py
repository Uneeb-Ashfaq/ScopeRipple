
from fastapi import APIRouter, HTTPException

from app.core.graph import PermissionGraph
from app.core.simulator import simulate_multiple_changes
from app.core.risk_analyzer import analyze_simulation
from app.schemas.simulation import SimulationRequest


router = APIRouter()


# Build a permission graph from the API request
def build_graph(request):
    graph = PermissionGraph()

    # Add all nodes to the graph
    for node in request.nodes:
        graph.add_node(node.id,node.type,node.sensitivity)

    # Add the original permissions
    for permission in request.permissions:
        graph.add_edge(permission.source,permission.target,permission.action)
    return graph


# Run a security simulation and return its findings
@router.post("/simulations")
def run_simulation(request: SimulationRequest):

    try:
        # Build the original graph
        graph = build_graph(request)

        # Convert proposed changes into dictionaries
        changes = []

        for change in request.changes:
            changes.append(change.model_dump())

        # Simulate the changes
        result = simulate_multiple_changes(graph,request.agent_id,changes)

        # Evaluate new security risks
        findings = analyze_simulation(result)

        return {"simulation": result,"findings": findings}

    except (ValueError, KeyError) as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error
