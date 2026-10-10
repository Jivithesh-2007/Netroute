"""
Graph data model supporting Adjacency List and Adjacency Matrix representations,
router online/offline toggling, and network graph operations.
"""
import json
from typing import Dict, List, Set, Tuple, Optional, Any
from models.router import Router


class Graph:
    """Network graph containing routers and connection links."""

    def __init__(self, directed: bool = False):
        self.directed = directed
        self.routers: Dict[str, Router] = {}
        # adj_list maps router_id -> dict of {neighbor_id: weight}
        self.adj_list: Dict[str, Dict[str, float]] = {}

    def add_router(self, router: Router) -> bool:
        """Add a router to the graph if ID is unique."""
        if router.id in self.routers:
            return False
        self.routers[router.id] = router
        self.adj_list[router.id] = {}
        return True

    def remove_router(self, router_id: str) -> bool:
        """Remove a router and all connected edges."""
        if router_id not in self.routers:
            return False
        
        del self.routers[router_id]
        del self.adj_list[router_id]

        for u in self.adj_list:
            if router_id in self.adj_list[u]:
                del self.adj_list[u][router_id]
        return True

    def add_edge(self, u: str, v: str, weight: float = 1.0) -> bool:
        """Add an edge between router u and router v."""
        if u not in self.routers or v not in self.routers or u == v:
            return False
        
        self.adj_list[u][v] = weight
        if not self.directed:
            self.adj_list[v][u] = weight
        return True

    def remove_edge(self, u: str, v: str) -> bool:
        """Remove an edge between router u and router v."""
        removed = False
        if u in self.adj_list and v in self.adj_list[u]:
            del self.adj_list[u][v]
            removed = True
        if not self.directed and v in self.adj_list and u in self.adj_list[v]:
            del self.adj_list[v][u]
            removed = True
        return removed

    def set_router_online_status(self, router_id: str, is_online: bool) -> bool:
        """Set a router's online/offline status."""
        if router_id not in self.routers:
            return False
        self.routers[router_id].is_online = is_online
        return True

    def get_neighbors(self, router_id: str, include_offline: bool = False) -> List[str]:
        """Get neighbors for a given router."""
        if router_id not in self.routers:
            return []
        
        neighbors = []
        for nbr in self.adj_list.get(router_id, {}):
            if include_offline or self.routers[nbr].is_online:
                neighbors.append(nbr)
        return neighbors

    def get_adjacency_list_view(self) -> Dict[str, List[str]]:
        """Return adjacency list mapping router names/IDs to neighbor IDs."""
        result = {}
        for rid in sorted(self.routers.keys()):
            neighbors = [nbr for nbr in self.adj_list[rid].keys()]
            result[rid] = sorted(neighbors)
        return result

    def get_adjacency_matrix_view(self) -> Tuple[List[str], List[List[int]]]:
        """Return ordered router IDs and the N x N adjacency matrix."""
        nodes = sorted(list(self.routers.keys()))
        idx_map = {rid: i for i, rid in enumerate(nodes)}
        n = len(nodes)
        matrix = [[0] * n for _ in range(n)]

        for u in self.adj_list:
            if u not in idx_map:
                continue
            i = idx_map[u]
            for v, w in self.adj_list[u].items():
                if v in idx_map:
                    j = idx_map[v]
                    matrix[i][j] = int(w) if w == 1.0 else w
        return nodes, matrix

    def get_edges(self) -> List[Tuple[str, str, float]]:
        """Return list of distinct edges as tuples (u, v, weight)."""
        edges = []
        seen = set()
        for u in self.adj_list:
            for v, w in self.adj_list[u].items():
                edge_key = tuple(sorted([u, v])) if not self.directed else (u, v)
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append((u, v, w))
        return edges

    def get_connected_components(self) -> List[List[str]]:
        """Compute connected components considering online nodes."""
        visited = set()
        components = []

        for rid in self.routers:
            if rid not in visited and self.routers[rid].is_online:
                comp = []
                queue = [rid]
                visited.add(rid)
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for nbr in self.get_neighbors(curr, include_offline=False):
                        if nbr not in visited:
                            visited.add(nbr)
                            queue.append(nbr)
                components.append(comp)
        return components

    def clear(self):
        """Clear all nodes and edges."""
        self.routers.clear()
        self.adj_list.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary."""
        return {
            "directed": self.directed,
            "routers": [r.to_dict() for r in self.routers.values()],
            "edges": self.get_edges()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Graph':
        """Create Graph from dictionary."""
        g = cls(directed=data.get("directed", False))
        for r_data in data.get("routers", []):
            g.add_router(Router.from_dict(r_data))
        for edge in data.get("edges", []):
            u, v = edge[0], edge[1]
            w = edge[2] if len(edge) > 2 else 1.0
            g.add_edge(u, v, w)
        return g

    def save_to_file(self, filepath: str):
        """Save graph to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Graph':
        """Load graph from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
