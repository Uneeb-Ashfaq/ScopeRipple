
import pytest

from app.core.graph import PermissionGraph
from app.core.traversal import reachable_resources


# Create a graph with read-only database access
def create_permission_graph():
    graph = PermissionGraph()

    graph.add_node("agent", "agent")
    graph.add_node("db_tool", "tool")
    graph.add_node("private_db", "resource", "restricted")

    graph.add_edge("agent", "db_tool", "execute")
    graph.add_edge("db_tool", "private_db", "read")

    return graph


# Check that read permission works
def test_read_access():
    graph = create_permission_graph()

    assert reachable_resources(graph, "agent", "read") == [
        "private_db"
    ]


# Check that read does not imply write
def test_write_denied():
    graph = create_permission_graph()

    assert reachable_resources(graph, "agent", "write") == []


# Check that write permission can be granted
def test_write_granted():
    graph = create_permission_graph()

    graph.add_edge("db_tool", "private_db", "write")

    assert reachable_resources(graph, "agent", "write") == [
        "private_db"
    ]


# Check that tool execution is required
def test_missing_execute_permission():
    graph = PermissionGraph()

    graph.add_node("agent", "agent")
    graph.add_node("tool", "tool")
    graph.add_node("resource", "resource")

    graph.add_edge("agent", "tool", "read")
    graph.add_edge("tool", "resource", "read")

    assert reachable_resources(graph, "agent", "read") == []


# Check that invalid actions are rejected
def test_invalid_permission():
    graph = create_permission_graph()

    with pytest.raises(ValueError):
        graph.add_edge("db_tool", "private_db", "delete")


# Check that non-agent start nodes are rejected
def test_invalid_start_node():
    graph = create_permission_graph()

    with pytest.raises(ValueError):
        reachable_resources(graph, "db_tool", "read")


# Check that duplicate nodes are rejected
def test_duplicate_node():
    graph = create_permission_graph()

    with pytest.raises(ValueError):
        graph.add_node("agent", "agent")


# Check that the graph still supports standard BFS
def test_existing_bfs_compatibility():
    from app.core.traversal import bfs

    graph = create_permission_graph()

    assert bfs(graph, "agent") == [
        "agent", "db_tool", "private_db"
    ]
