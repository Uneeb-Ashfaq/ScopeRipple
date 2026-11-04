
import pytest

from app.core.graph import PermissionGraph
from app.core.simulator import simulate_multiple_changes


# Create a sample graph for multiple change testing
def create_test_graph():
    graph = PermissionGraph()

    graph.add_node("agent", "agent")
    graph.add_node("tool", "tool")
    graph.add_node("resource_a", "resource", "public")
    graph.add_node("resource_b", "resource", "restricted")

    graph.add_edge("agent", "tool", "execute")
    graph.add_edge("tool", "resource_a", "read")

    return graph


# Check multiple permissions can be added together
def test_multiple_additions():
    graph = create_test_graph()

    changes = [
        {
            "source": "tool",
            "target": "resource_b",
            "action": "read",
            "operation": "add"
        },
        {
            "source": "tool",
            "target": "resource_b",
            "action": "write",
            "operation": "add"
        }
    ]

    result = simulate_multiple_changes(graph, "agent", changes)

    assert len(result["new_access"]) == 2


# Check that removed access is detected
def test_multiple_removals():
    graph = create_test_graph()

    changes = [
        {
            "source": "tool",
            "target": "resource_a",
            "action": "read",
            "operation": "remove"
        }
    ]

    result = simulate_multiple_changes(graph, "agent", changes)

    assert len(result["lost_access"]) == 1


# Check that the original graph is unchanged
def test_original_graph_unchanged():
    graph = create_test_graph()

    changes = [
        {
            "source": "tool",
            "target": "resource_b",
            "action": "write",
            "operation": "add"
        }
    ]

    simulate_multiple_changes(graph, "agent", changes)

    assert graph.has_permission(
        "tool", "resource_b", "write"
    ) is False


# Check that invalid operations are rejected
def test_invalid_operation():
    graph = create_test_graph()

    changes = [
        {
            "source": "tool",
            "target": "resource_b",
            "action": "write",
            "operation": "update"
        }
    ]

    with pytest.raises(ValueError):
        simulate_multiple_changes(graph, "agent", changes)


# Check combined changes can create new access
def test_combined_permissions():
    graph = PermissionGraph()

    graph.add_node("agent", "agent")
    graph.add_node("tool", "tool")
    graph.add_node("resource", "resource", "restricted")

    changes = [
        {
            "source": "agent",
            "target": "tool",
            "action": "execute",
            "operation": "add"
        },
        {
            "source": "tool",
            "target": "resource",
            "action": "read",
            "operation": "add"
        }
    ]

    result = simulate_multiple_changes(graph, "agent", changes)

    assert len(result["new_access"]) == 1
    assert result["new_access"][0]["resource"] == "resource"
