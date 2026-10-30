class PermissionGraph:

    # Initialize an empty graph
    def __init__(self):
        self.graph = {}

    # Add a node if it doesn't already exist
    def add_node(self, node_id):
        if node_id not in self.graph:
            self.graph[node_id] = []

    # Create a directed connection between two nodes
    def add_edge(self, source, target):
        if source not in self.graph:
            raise ValueError(f"Unknown source node: {source}")

        if target not in self.graph:
            raise ValueError(f"Unknown target node: {target}")

        if target not in self.graph[source]:
            self.graph[source].append(target)

    # Return the direct neighbors of a node
    def get_neighbors(self, node_id):
        if node_id not in self.graph:
            raise ValueError(f"Unknown node: {node_id}")

        return self.graph[node_id].copy()