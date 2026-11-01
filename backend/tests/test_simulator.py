
import pytest

from app.core.graph import PermissionGraph
from app.core.simulator import (
    find_access_path,
    simulate_permission_change
)


# Create a graph with read-only database access
def create_test_graph():
    graph = PermissionGraph()

    graph.add_node("agent", "agent")
    graph.add_node("db_tool", "tool")
    graph.add_node("private_db", "resource", "restricted")

    graph.add_edge("agent", "db_tool", "execute")
    graph.add_edge("db_tool", "private_db", "read")

    return graph


# Check that valid permission paths are found
def test_access_path():
    graph = create_test_graph()

    assert find_access_path(
        graph, "agent", "private_db", "read"
    ) == ["agent", "db_tool", "private_db"]


# Check that missing permissions block access paths
def test_access_path_denied():
    graph = create_test_graph()

    assert find_access_path(
        graph, "agent", "private_db", "write"
    ) is None


# Detect newly granted write access
def test_new_write_access():
    graph = create_test_graph()

    result = simulate_permission_change(
        graph, "agent", "db_tool",
        "private_db", "write", "add"
    )

    assert len(result["new_access"]) == 1
    assert result["new_access"][0]["action"] == "write"
    assert result["new_access"][0]["path"] == [
        "agent", "db_tool", "private_db"
    ]


# Detect access removed by a permission change
def test_lost_read_access():
    graph = create_test_graph()

    result = simulate_permission_change(
        graph, "agent", "db_tool",
        "private_db", "read", "remove"
    )

    assert len(result["lost_access"]) == 1
    assert result["lost_access"][0]["action"] == "read"


# Ensure simulations preserve the original graph
def test_simulation_isolation():
    graph = create_test_graph()

    simulate_permission_change(
        graph, "agent", "db_tool",
        "private_db", "write", "add"
    )

    assert graph.get_permissions(
        "db_tool", "private_db"
    ) == {"read"}


# Detect new access caused by tool execution

# Check that granting tool execution creates new access
def test_new_tool_access():
    graph = create_test_graph()

    # Remove the agent's tool execution permission
    graph.remove_permission(
        "agent", "db_tool", "execute"
    )

    # Adding resource permission alone should not grant access
    result = simulate_permission_change(
        graph, "agent", "db_tool",
        "private_db", "read", "add"
    )

    assert result["new_access"] == []

    # Restoring tool execution should grant resource access
    result = simulate_permission_change(
        graph, "agent", "agent",
        "db_tool", "execute", "add"
    )

    assert len(result["new_access"]) == 1
    assert result["new_access"][0]["resource"] == "private_db"
    assert result["new_access"][0]["action"] == "read"


# Reject invalid simulation operations
def test_invalid_operation():
    graph = create_test_graph()

    with pytest.raises(ValueError):
        simulate_permission_change(
            graph, "agent", "db_tool",
            "private_db", "write", "update"
        )
