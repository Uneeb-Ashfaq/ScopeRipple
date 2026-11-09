
from app.core.graph import PermissionGraph
from app.core.simulator import simulate_multiple_changes
from app.core.risk_analyzer import analyze_simulation


# Create a sample permission graph
graph = PermissionGraph()

graph.add_node("agent", "agent")
graph.add_node("db_tool", "tool")
graph.add_node("file_tool", "tool")

graph.add_node("private_db", "resource", "restricted")
graph.add_node("public_files", "resource", "public")
graph.add_node("financial_records", "resource", "confidential")

# Set up the original permissions
graph.add_edge("agent", "db_tool", "execute")
graph.add_edge("agent", "file_tool", "execute")

graph.add_edge("db_tool", "private_db", "read")
graph.add_edge("file_tool", "public_files", "read")

# Define multiple proposed changes
changes = [
    {"source": "db_tool", "target": "private_db", "action": "write", "operation": "add"},
    {"source": "file_tool", "target": "financial_records", "action": "read", "operation": "add"},
    {"source": "file_tool", "target": "public_files", "action": "read", "operation": "remove"}
]


# Run the simulation
result = simulate_multiple_changes(graph, "agent", changes)

# Analyze newly granted access
findings = analyze_simulation(result)

print("\nNew Access:")
for access in result["new_access"]:
    print(access)

print("\nLost Access:")
for access in result["lost_access"]:
    print(access)

print("\nSecurity Findings:")
for finding in findings:
    print(finding["resource"],finding["action"],finding["severity"])
