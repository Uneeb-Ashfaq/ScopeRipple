
class PermissionGraph:

    # Initialize graph connections and metadata
    def __init__(self):
        self.graph = {}
        self.nodes = {}
        self.permissions = {}

    # Add a node with its type and sensitivity
    def add_node(self, node_id, node_type="resource", sensitivity="public"):

        valid_types = {"agent", "tool", "resource"}
        valid_sensitivity = {
            "public", "internal", "confidential", "restricted"
        }

        if node_type not in valid_types:
            raise ValueError(f"Invalid node type: {node_type}")

        if sensitivity not in valid_sensitivity:
            raise ValueError(f"Invalid sensitivity: {sensitivity}")

        if node_id in self.nodes:
            raise ValueError(f"Duplicate node: {node_id}")

        self.graph[node_id] = []
        self.nodes[node_id] = {"type": node_type,"sensitivity": sensitivity}

    # Add a directed edge with a permission action
    def add_edge(self, source, target, action="read"):

        valid_actions = {"read", "write", "execute"}

        if source not in self.graph:
            raise ValueError(f"Unknown source node: {source}")

        if target not in self.graph:
            raise ValueError(f"Unknown target node: {target}")

        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}")

        edge = (source, target)

        if target not in self.graph[source]:
            self.graph[source].append(target)

        if edge not in self.permissions:
            self.permissions[edge] = set()

        self.permissions[edge].add(action)

    # Return direct neighbors of a node
    def get_neighbors(self, node_id):
        if node_id not in self.graph:
            raise ValueError(f"Unknown node: {node_id}")

        return self.graph[node_id].copy()



    # Return the actions allowed on an edge
    def get_permissions(self, source, target):
        return self.permissions.get((source, target), set()).copy()

    # Check whether an edge allows an action
    def has_permission(self, source, target, action):
        return action in self.get_permissions(source, target)

    # Return metadata for a node
    def get_node(self, node_id):
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")

        return self.nodes[node_id].copy()
