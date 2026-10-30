
from app.core.graph import PermissionGraph
from app.core.traversal import bfs
graph = PermissionGraph()

# Create nodes
graph.add_node("agent")
graph.add_node("file_tool")
graph.add_node("database_tool")
graph.add_node("public_files")
graph.add_node("private_db")

# Create connections
graph.add_edge("agent", "file_tool")
graph.add_edge("agent", "database_tool")
graph.add_edge("file_tool", "public_files")
graph.add_edge("database_tool", "private_db")

print("Full graph:")
print(graph.graph)

print("\nAgent's direct connections:")
print(graph.get_neighbors("agent"))
# Find all nodes reachable from the agent
print("\nBFS Traversal:")
print(bfs(graph, "agent"))