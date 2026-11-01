
from collections import deque


# Traverse all reachable nodes using BFS
def bfs(graph, start):
    if start not in graph.graph:
        raise ValueError(f"Unknown start node: {start}")

    visited = {start}
    queue = deque([start])
    result = []

    while queue:
        current = queue.popleft()
        result.append(current)

        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return result

# Traverse all reachable nodes using DFS
def dfs(graph, start):
    if start not in graph.graph:
        raise ValueError(f"Unknown start node: {start}")

    visited = set()
    stack = [start]
    result = []

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)
        result.append(current)

        for neighbor in reversed(graph.get_neighbors(current)):
            if neighbor not in visited:
                stack.append(neighbor)

    return result


# Find the shortest path between two nodes using BFS
def shortest_path(graph, start, target):
    if start not in graph.graph:
        raise ValueError(f"Unknown start node: {start}")

    if target not in graph.graph:
        raise ValueError(f"Unknown target node: {target}")

    queue = deque([start])
    parent = {start: None}

    while queue:
        current = queue.popleft()

        if current == target:
            path = []

            while current is not None:
                path.append(current)
                current = parent[current]

            return path[::-1]

        for neighbor in graph.get_neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)

    return None



# Find resources accessible through valid permission paths
def reachable_resources(graph, agent_id, action="read"):

    if agent_id not in graph.nodes:
        raise ValueError(f"Unknown agent: {agent_id}")

    if graph.nodes[agent_id]["type"] != "agent":
        raise ValueError("Start node must be an agent")

    if action not in {"read", "write"}:
        raise ValueError(f"Invalid resource action: {action}")

    visited = {agent_id}
    queue = deque([agent_id])
    resources = []

    while queue:
        current = queue.popleft()

        for neighbor in graph.get_neighbors(current):

            if graph.nodes[neighbor]["type"] == "tool":
                required_action = "execute"

            elif graph.nodes[neighbor]["type"] == "resource":
                required_action = action

            else:
                continue

            if not graph.has_permission(
                current, neighbor, required_action
            ):
                continue

            if neighbor in visited:
                continue

            visited.add(neighbor)

            if graph.nodes[neighbor]["type"] == "resource":
                resources.append(neighbor)

            else:
                queue.append(neighbor)

    return resources
