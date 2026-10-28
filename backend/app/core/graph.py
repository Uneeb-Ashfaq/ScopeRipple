
class PermissionGraph:
    def __init__(self):
        self.graph = {}

    def add_node(self, node_id):
        if node_id not in self.graph:
            self.graph[node_id] = []

    def add_edge(self, source, target):
        if source not in self.graph:
            raise ValueError(f"Unknown source node: {source}")

        if target not in self.graph:
            raise ValueError(f"Unknown target node: {target}")

        if target not in self.graph[source]:
            self.graph[source].append(target)

    def get_neighbors(self, node_id):
        if node_id not in self.graph:
            raise ValueError(f"Unknown node: {node_id}")

        return self.graph[node_id].copy()
