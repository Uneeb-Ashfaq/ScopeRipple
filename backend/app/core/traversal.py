
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
