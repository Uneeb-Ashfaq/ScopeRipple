
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db
from app.db.models import Base


# Create a temporary SQLite database for each test
@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "test.db"
    database_url = f"sqlite:///{database_path}"

    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    TestSession = sessionmaker(bind=engine)

    # Replace the real database with our test database
    def get_test_db():
        with TestSession() as db:
            yield db

    app.dependency_overrides[get_db] = get_test_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


# Create a project with an agent, tool, and resource
def create_simulation_project(client):
    response = client.post(
        "/api/v1/projects",
        json={"name": "Simulation Test"}
    )

    project_id = response.json()["id"]

    nodes = [
        {"node_id": "agent", "node_type": "agent"},
        {"node_id": "tool", "node_type": "tool"},
        {
            "node_id": "private_db",
            "node_type": "resource",
            "sensitivity": "restricted"
        }
    ]

    for node in nodes:
        client.post(
            f"/api/v1/projects/{project_id}/nodes",
            json=node
        )

    permissions = [
        {
            "source": "agent",
            "target": "tool",
            "action": "execute"
        },
        {
            "source": "tool",
            "target": "private_db",
            "action": "read"
        }
    ]

    for permission in permissions:
        client.post(
            f"/api/v1/projects/{project_id}/permissions",
            json=permission
        )

    return project_id


# Check that simulations run and save successfully
def test_saved_simulation(client):
    project_id = create_simulation_project(client)

    response = client.post(
        f"/api/v1/projects/{project_id}/simulations",
        json={
            "agent_id": "agent",
            "changes": [
                {
                    "source": "tool",
                    "target": "private_db",
                    "action": "write",
                    "operation": "add"
                }
            ]
        }
    )

    assert response.status_code == 201
    assert response.json()["findings"][0]["severity"] == "critical"


# Check that simulation history can be retrieved
def test_simulation_history(client):
    project_id = create_simulation_project(client)

    client.post(
        f"/api/v1/projects/{project_id}/simulations",
        json={"agent_id": "agent", "changes": []}
    )

    response = client.get(
        f"/api/v1/projects/{project_id}/simulations"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# Check that simulations do not modify saved permissions
def test_saved_graph_unchanged(client):
    project_id = create_simulation_project(client)

    client.post(
        f"/api/v1/projects/{project_id}/simulations",
        json={
            "agent_id": "agent",
            "changes": [
                {
                    "source": "tool",
                    "target": "private_db",
                    "action": "write",
                    "operation": "add"
                }
            ]
        }
    )

    response = client.get(
        f"/api/v1/projects/{project_id}/graph"
    )

    permissions = response.json()["permissions"]

    assert len(permissions) == 2
    assert {
        "source": "tool",
        "target": "private_db",
        "action": "write"
    } not in permissions


# Check that unknown projects cannot run simulations
def test_simulation_project_not_found(client):
    response = client.post(
        "/api/v1/projects/999/simulations",
        json={"agent_id": "agent", "changes": []}
    )

    assert response.status_code == 404
