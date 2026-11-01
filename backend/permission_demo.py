
from app.core.graph import PermissionGraph
from app.core.traversal import reachable_resources


# Create a sample agent permission graph
graph = PermissionGraph()

graph.add_node("agent", "agent")
graph.add_node("file_tool", "tool")
graph.add_node("db_tool", "tool")

graph.add_node(
    "public_files", "resource", "public"
)

graph.add_node(
    "private_db", "resource", "restricted"
)

# Grant the agent access to both tools
graph.add_edge("agent", "file_tool", "execute")
graph.add_edge("agent", "db_tool", "execute")

# Configure resource permissions
graph.add_edge("file_tool", "public_files", "read")
graph.add_edge("db_tool", "private_db", "read")

# Display configured permissions
print("DB permissions:")
print(graph.get_permissions("db_tool", "private_db"))

# Find resources the agent can read
print("\nReadable resources:")
print(reachable_resources(graph, "agent", "read"))

# Find resources the agent can write
print("\nWritable resources:")
print(reachable_resources(graph, "agent", "write"))

# Check whether the agent has write access
print("\nCan write to private database:")
print(graph.has_permission("db_tool", "private_db", "write"))
