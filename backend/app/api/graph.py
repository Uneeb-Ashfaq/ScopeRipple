
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Project, Node, Permission
from app.schemas.graph import NodeCreate, PermissionCreate


router = APIRouter()


# Check that a project exists
def check_project(db, project_id):
    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )


# Find a node by its name within a project
def find_node(db, project_id, node_id):
    statement = select(Node).where(
        Node.project_id == project_id,
        Node.node_id == node_id
    )

    return db.scalars(statement).first()


# Add a new agent, tool, or resource to a project
@router.post("/projects/{project_id}/nodes", status_code=201)
def create_node(
    project_id: int,
    node: NodeCreate,
    db: Session = Depends(get_db)
):
    check_project(db, project_id)

    if find_node(db, project_id, node.node_id):
        raise HTTPException(
            status_code=409,
            detail="Node already exists"
        )

    new_node = Node(
        project_id=project_id,
        node_id=node.node_id,
        node_type=node.node_type,
        sensitivity=node.sensitivity
    )

    db.add(new_node)
    db.commit()
    db.refresh(new_node)

    return {
        "id": new_node.id,
        "node_id": new_node.node_id,
        "node_type": new_node.node_type,
        "sensitivity": new_node.sensitivity
    }


# Add a directed permission between two nodes
@router.post("/projects/{project_id}/permissions", status_code=201)
def create_permission(
    project_id: int,
    permission: PermissionCreate,
    db: Session = Depends(get_db)
):
    check_project(db, project_id)

    source = find_node(db, project_id, permission.source)
    target = find_node(db, project_id, permission.target)

    if source is None or target is None:
        raise HTTPException(
            status_code=404,
            detail="Source or target node not found"
        )

    statement = select(Permission).where(
        Permission.project_id == project_id,
        Permission.source_id == source.id,
        Permission.target_id == target.id,
        Permission.action == permission.action
    )

    existing = db.scalars(statement).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Permission already exists"
        )

    new_permission = Permission(
        project_id=project_id,
        source_id=source.id,
        target_id=target.id,
        action=permission.action
    )

    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)

    return {
        "id": new_permission.id,
        "source": source.node_id,
        "target": target.node_id,
        "action": new_permission.action
    }


# Retrieve all nodes and permissions belonging to a project
@router.get("/projects/{project_id}/graph")
def get_graph(
    project_id: int,
    db: Session = Depends(get_db)
):
    check_project(db, project_id)

    node_statement = select(Node).where(
        Node.project_id == project_id
    ).order_by(Node.id)

    permission_statement = select(Permission).where(
        Permission.project_id == project_id
    ).order_by(Permission.id)

    nodes = db.scalars(node_statement).all()
    permissions = db.scalars(permission_statement).all()

    # Convert database nodes into API response dictionaries
    node_results = []
    node_names = {}

    for node in nodes:
        node_names[node.id] = node.node_id

        node_results.append({
            "id": node.node_id,
            "type": node.node_type,
            "sensitivity": node.sensitivity
        })

    # Convert database permissions into graph edges
    permission_results = []

    for permission in permissions:
        permission_results.append({
            "source": node_names[permission.source_id],
            "target": node_names[permission.target_id],
            "action": permission.action
        })

    return {
        "project_id": project_id,
        "nodes": node_results,
        "permissions": permission_results
    }
