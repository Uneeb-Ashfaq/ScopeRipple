
import pytest

from app.core.graph import PermissionGraph
from app.core.traversal import bfs, dfs, shortest_path

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

# Check that DFS visits all reachable nodes
def test_dfs_reachable():
    graph = create_test_graph()

    assert dfs(graph, "agent") == [
        "agent", "tool", "resource"
    ]


# Check that DFS handles cycles
def test_dfs_cycle():
    graph = create_test_graph()
    graph.add_edge("resource", "agent")

    assert dfs(graph, "agent") == [
        "agent", "tool", "resource"
    ]


# Check that DFS rejects unknown nodes
def test_dfs_unknown_node():
    graph = create_test_graph()

    with pytest.raises(ValueError):
        dfs(graph, "missing")


# Check that shortest path returns a valid route
def test_shortest_path():
    graph = create_test_graph()

    assert shortest_path(graph, "agent", "resource") == [
        "agent", "tool", "resource"
    ]


# Check that unreachable nodes return None
def test_shortest_path_unreachable():
    graph = create_test_graph()

    assert shortest_path(graph, "resource", "agent") is None


# Check that a node can reach itself
def test_shortest_path_same_node():
    graph = create_test_graph()

    assert shortest_path(graph, "agent", "agent") == ["agent"]


# Check that BFS finds the shortest route
def test_shortest_path_multiple_routes():
    graph = PermissionGraph()

    for node in ["agent", "tool_a", "tool_b", "extra", "resource"]:
        graph.add_node(node)

    graph.add_edge("agent", "tool_a")
    graph.add_edge("tool_a", "extra")
    graph.add_edge("extra", "resource")

    graph.add_edge("agent", "tool_b")
    graph.add_edge("tool_b", "resource")

    assert shortest_path(graph, "agent", "resource") == [
        "agent", "tool_b", "resource"
    ]
