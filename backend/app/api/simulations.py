
from fastapi import APIRouter, HTTPException

from app.core.graph import PermissionGraph
from app.core.simulator import simulate_multiple_changes
from app.core.risk_analyzer import analyze_simulation
from app.schemas.simulation import SimulationRequest


from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Project, Node, Permission, Simulation
from app.schemas.simulation import SavedSimulationRequest

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




# Load a project's saved nodes and permissions into a graph
def load_saved_graph(db, project_id):
    graph = PermissionGraph()

    # Retrieve nodes belonging to the project
    statement = select(Node).where(Node.project_id == project_id)
    nodes = db.scalars(statement).all()

    node_names = {}

    for node in nodes:
        graph.add_node(
            node.node_id,
            node.node_type,
            node.sensitivity
        )

        node_names[node.id] = node.node_id

    # Retrieve saved permissions
    statement = select(Permission).where(
        Permission.project_id == project_id
    )
    permissions = db.scalars(statement).all()

    for permission in permissions:
        graph.add_edge(
            node_names[permission.source_id],
            node_names[permission.target_id],
            permission.action
        )

    return graph



# Run and save a simulation using a stored project graph
@router.post("/projects/{project_id}/simulations", status_code=201)
def run_saved_simulation(
    project_id: int,
    request: SavedSimulationRequest,
    db: Session = Depends(get_db)
):

    # Check that the project exists
    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Load the project's existing permissions
    graph = load_saved_graph(db, project_id)

    # Convert the requested changes into dictionaries
    changes = []

    for change in request.changes:
        changes.append(change.model_dump())

    try:
        # Simulate the proposed permission changes
        result = simulate_multiple_changes(
            graph,
            request.agent_id,
            changes
        )

        # Evaluate the newly introduced security risks
        findings = analyze_simulation(result)

    except (ValueError, KeyError) as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error

    # Save simulation results without changing the graph
    saved_simulation = Simulation(
        project_id=project_id,
        agent_id=request.agent_id,
        changes=changes,
        results={
            "simulation": result,
            "findings": findings
        }
    )

    db.add(saved_simulation)
    db.commit()
    db.refresh(saved_simulation)

    return {
        "id": saved_simulation.id,
        "project_id": project_id,
        "simulation": result,
        "findings": findings
    }




# Retrieve all saved simulations for a project
@router.get("/projects/{project_id}/simulations")
def get_project_simulations(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    statement = select(Simulation).where(
        Simulation.project_id == project_id
    ).order_by(Simulation.id.desc())

    simulations = db.scalars(statement).all()

    results = []

    # Convert saved simulations into API responses
    for simulation in simulations:
        results.append({
            "id": simulation.id,
            "agent_id": simulation.agent_id,
            "changes": simulation.changes,
            "results": simulation.results,
            "created_at": simulation.created_at
        })

    return results


# Retrieve an individual saved simulation
@router.get("/simulations/{simulation_id}")
def get_saved_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):

    simulation = db.get(Simulation, simulation_id)

    if simulation is None:
        raise HTTPException(
            status_code=404,
            detail="Simulation not found"
        )

    return {
        "id": simulation.id,
        "project_id": simulation.project_id,
        "agent_id": simulation.agent_id,
        "changes": simulation.changes,
        "results": simulation.results,
        "created_at": simulation.created_at
    }
