
import pytest

from app.core.graph import PermissionGraph
from app.core.traversal import bfs


# Create a sample graph for testing
def create_test_graph():
    graph = PermissionGraph()

    for node in ["agent", "tool", "resource"]:
        graph.add_node(node)

    graph.add_edge("agent", "tool")
    graph.add_edge("tool", "resource")

    return graph


# Check that BFS finds all reachable nodes
def test_bfs_reachable():
    graph = create_test_graph()

    assert bfs(graph, "agent") == [
        "agent", "tool", "resource"
    ]


# Check that BFS follows directed edges
def test_bfs_direction():
    graph = create_test_graph()

    assert bfs(graph, "resource") == ["resource"]


# Check that BFS handles cycles
def test_bfs_cycle():
    graph = create_test_graph()
    graph.add_edge("resource", "agent")

    assert bfs(graph, "agent") == [
        "agent", "tool", "resource"
    ]


# Check that BFS rejects unknown nodes
def test_bfs_unknown_node():
    graph = create_test_graph()

    with pytest.raises(ValueError):
        bfs(graph, "missing")
