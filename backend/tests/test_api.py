
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


# Create a sample request for testing the API
def create_test_request():
    return {
        "agent_id": "agent",
        "nodes": [
            {"id": "agent", "type": "agent"},
            {"id": "tool", "type": "tool"},
            {
                "id": "private_db",
                "type": "resource",
                "sensitivity": "restricted"
            }
        ],
        "permissions": [
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
        ],
        "changes": [
            {
                "source": "tool",
                "target": "private_db",
                "action": "write",
                "operation": "add"
            }
        ]
    }


# Check that the simulation API detects critical risks
def test_simulation_api():
    request = create_test_request()

    response = client.post(
        "/api/v1/simulations",
        json=request
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["simulation"]["new_access"]) == 1
    assert data["findings"][0]["severity"] == "critical"


# Check that invalid operations are rejected
def test_invalid_api_operation():
    request = create_test_request()

    request["changes"][0]["operation"] = "update"

    response = client.post(
        "/api/v1/simulations",
        json=request
    )

    assert response.status_code == 422


# Check that unknown graph nodes are rejected
def test_unknown_node():
    request = create_test_request()

    request["changes"][0]["target"] = "missing_db"

    response = client.post(
        "/api/v1/simulations",
        json=request
    )

    assert response.status_code == 422


# Check that the existing health endpoint works
def test_health_api():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
