
from app.core.graph import PermissionGraph
from app.core.simulator import simulate_permission_change


# Create the original permission graph
graph = PermissionGraph()

graph.add_node("agent", "agent")
graph.add_node("db_tool", "tool")
graph.add_node("private_db", "resource", "restricted")

graph.add_edge("agent", "db_tool", "execute")
graph.add_edge("db_tool", "private_db", "read")


# Simulate granting write access
result = simulate_permission_change(
    graph,
    agent_id="agent",
    source="db_tool",
    target="private_db",
    action="write",
    operation="add"
)

print("\nSimulation Results:")
print(result)

# Check that the original graph was not modified
print("\nOriginal database permissions:")
print(graph.get_permissions("db_tool", "private_db"))
