
import pytest

from app.core.graph import PermissionGraph


def test_add_node():
    graph = PermissionGraph()

    graph.add_node("agent")

    assert "agent" in graph.graph


def test_add_edge():
    graph = PermissionGraph()

    graph.add_node("agent")
    graph.add_node("tool")
    graph.add_edge("agent", "tool")

    assert graph.get_neighbors("agent") == ["tool"]


def test_duplicate_edges():
    graph = PermissionGraph()

    graph.add_node("agent")
    graph.add_node("tool")

    graph.add_edge("agent", "tool")
    graph.add_edge("agent", "tool")

    assert graph.get_neighbors("agent") == ["tool"]


def test_unknown_target():
    graph = PermissionGraph()

    graph.add_node("agent")

    with pytest.raises(ValueError):
        graph.add_edge("agent", "missing_tool")
