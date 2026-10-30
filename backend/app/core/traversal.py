
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
