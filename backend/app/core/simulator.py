
from collections import deque

from app.core.traversal import reachable_resources


# Find a valid permission path to a resource
def find_access_path(graph, agent_id, resource_id, action):
    #error handling for invalid inputs
    if agent_id not in graph.nodes:
        raise ValueError(f"Unknown agent: {agent_id}")

    if resource_id not in graph.nodes:
        raise ValueError(f"Unknown resource: {resource_id}")

    if graph.nodes[agent_id]["type"] != "agent":
        raise ValueError("Start node must be an agent")

    if graph.nodes[resource_id]["type"] != "resource":
        raise ValueError("Target must be a resource")

    if action not in {"read", "write"}:
        raise ValueError(f"Invalid action: {action}")

    queue = deque([agent_id])
    parent = {agent_id: None}

    while queue:
        current = queue.popleft()

        for neighbor in graph.get_neighbors(current):
            node_type = graph.nodes[neighbor]["type"]

            if node_type == "tool":
                required = "execute"
            elif node_type == "resource":
                required = action
            else:
                continue

            if not graph.has_permission(current, neighbor, required):
                continue

            if neighbor in parent:
                continue

            parent[neighbor] = current

            if neighbor == resource_id:
                path = []
                node = neighbor

                while node is not None:
                    path.append(node)
                    node = parent[node]

                return path[::-1]

            if node_type == "tool":
                queue.append(neighbor)

    return None


# Compare resource access before and after a permission change
def simulate_permission_change(graph, agent_id, source, target, action, operation="add"):
    if agent_id not in graph.nodes:
        raise ValueError(f"Unknown agent: {agent_id}")

    if graph.nodes[agent_id]["type"] != "agent":
        raise ValueError("Start node must be an agent")

    if source not in graph.nodes or target not in graph.nodes:
        raise ValueError("Unknown source or target node")

    if action not in {"read", "write", "execute"}:
        raise ValueError(f"Invalid action: {action}")

    if operation not in {"add", "remove"}:
        raise ValueError(f"Invalid operation: {operation}")

    # Preserve the original graph
    modified = graph.clone()

    # Apply the proposed permission change
    if operation == "add":
        modified.add_edge(source, target, action)
    else:
        modified.remove_permission(source, target, action)

    results = {
        "operation": operation,
        "permission": {"source": source,"target": target,"action": action},"new_access": [],"lost_access": []}

    # Compare read and write access independently
    for resource_action in ["read", "write"]:
        before = set(reachable_resources(graph, agent_id, resource_action))

        after = set(reachable_resources(modified, agent_id, resource_action))

        for resource in sorted(after - before):
            results["new_access"].append({
                "resource": resource,
                "action": resource_action,
                "sensitivity": modified.nodes[resource]["sensitivity"],
                "path": find_access_path(modified, agent_id, resource, resource_action)
            })

        for resource in sorted(before - after):
            results["lost_access"].append({
                "resource": resource,
                "action": resource_action,
                "sensitivity": graph.nodes[resource]["sensitivity"],
                "path": find_access_path(graph, agent_id, resource, resource_action)
            })

    return results



# Simulate multiple permission changes without modifying the original graph
def simulate_multiple_changes(graph, agent_id, changes):

    if agent_id not in graph.nodes:
        raise ValueError(f"Unknown agent: {agent_id}")

    if graph.nodes[agent_id]["type"] != "agent":
        raise ValueError("Start node must be an agent")

    # Create a separate graph for the simulation
    modified = graph.clone()

    # Apply each proposed permission change
    for change in changes:

        source = change["source"]
        target = change["target"]
        action = change["action"]
        operation = change["operation"]

        if operation == "add":
            modified.add_edge(source, target, action)

        elif operation == "remove":
            modified.remove_permission(source, target, action)

        else:
            raise ValueError(f"Invalid operation: {operation}")

    results = {"changes": changes,"new_access": [],"lost_access": []}

    # Compare resource access before and after all changes
    for action in ["read", "write"]:
        before = set(reachable_resources(graph, agent_id, action))
        after = set(reachable_resources(modified, agent_id, action))

        # Find newly accessible resources
        for resource in sorted(after - before):

            results["new_access"].append({
                "resource": resource,
                "action": action,
                "sensitivity": modified.nodes[resource]["sensitivity"],
                "path": find_access_path(modified, agent_id, resource, action)
            })

        # Find resources that lost access
        for resource in sorted(before - after):

            results["lost_access"].append({
                "resource": resource,
                "action": action,
                "sensitivity": graph.nodes[resource]["sensitivity"],
                "path": find_access_path(graph, agent_id, resource, action)
            })

    return results
