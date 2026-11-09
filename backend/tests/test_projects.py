
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db
from app.db.models import Base

from app.db.models import Node, Permission




# Create a temporary database for each test
@pytest.fixture
def client(tmp_path):

    database_path = tmp_path / "test.db"
    database_url = f"sqlite:///{database_path}"

    engine = create_engine(database_url)

    # Create the tables needed for testing
    Base.metadata.create_all(bind=engine)

    TestSession = sessionmaker(bind=engine)

    # Use the test database instead of the real database
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


# Check that a project can be created
def test_create_project(client):

    response = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Project"
    assert data["id"] == 1


# Check that saved projects can be retrieved
def test_get_projects(client):

    client.post(
        "/api/v1/projects",
        json={"name": "Project A"}
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Project A"


# Check that a specific project can be retrieved
def test_get_project_by_id(client):

    client.post(
        "/api/v1/projects",
        json={"name": "Project A"}
    )

    response = client.get("/api/v1/projects/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Project A"


# Check that unknown projects return 404
def test_project_not_found(client):

    response = client.get("/api/v1/projects/999")

    assert response.status_code == 404


# Check that an empty project name is rejected
def test_invalid_project_name(client):

    response = client.post(
        "/api/v1/projects",
        json={"name": ""}
    )

    assert response.status_code == 422





# Check that a node can be saved to a project
def test_create_node(client):
    client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    )

    response = client.post(
        "/api/v1/projects/1/nodes",
        json={
            "node_id": "agent",
            "node_type": "agent"
        }
    )

    assert response.status_code == 201
    assert response.json()["node_id"] == "agent"


# Check that duplicate nodes are rejected
def test_duplicate_node_api(client):
    client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    )

    node = {
        "node_id": "agent",
        "node_type": "agent"
    }

    client.post("/api/v1/projects/1/nodes", json=node)

    response = client.post(
        "/api/v1/projects/1/nodes",
        json=node
    )

    assert response.status_code == 409


# Check that saved nodes and permissions form a graph
def test_saved_graph(client):
    client.post(
        "/api/v1/projects",
        json={"name": "Test Project"}
    )

    for node_id, node_type in [
        ("agent", "agent"),
        ("tool", "tool"),
        ("resource", "resource")
    ]:
        client.post(
            "/api/v1/projects/1/nodes",
            json={
                "node_id": node_id,
                "node_type": node_type
            }
        )

    response = client.post(
        "/api/v1/projects/1/permissions",
        json={
            "source": "agent",
            "target": "tool",
            "action": "execute"
        }
    )

    assert response.status_code == 201

    response = client.get("/api/v1/projects/1/graph")

    assert response.status_code == 200
    assert len(response.json()["nodes"]) == 3
    assert len(response.json()["permissions"]) == 1
