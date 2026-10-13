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

    def is_reachable(self, start_id: str, end_id: str) -> bool:
        """Check if end_id is reachable from start_id considering online routers."""
        if start_id not in self.routers or end_id not in self.routers:
            return False
        if not self.routers[start_id].is_online or not self.routers[end_id].is_online:
            return False
        if start_id == end_id:
            return True

        visited = {start_id}
        queue = [start_id]
        while queue:
            curr = queue.pop(0)
            if curr == end_id:
                return True
            for nbr in self.get_neighbors(curr, include_offline=False):
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append(nbr)
        return False

    def get_isolated_routers(self) -> List[str]:
        """Return list of routers with degree 0."""
        isolated = []
        for rid in sorted(self.routers.keys()):
            nbrs = self.adj_list.get(rid, {})
            if len(nbrs) == 0:
                isolated.append(rid)
        return isolated

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

    @classmethod
    def create_default_topology(cls) -> 'Graph':
        """Standard balanced 6-router topology."""
        g = cls(directed=False)
        g.add_router(Router("R1", "Core R1", 100, 140))
        g.add_router(Router("R2", "Edge R2", 280, 90))
        g.add_router(Router("R3", "Gateway R3", 470, 90))
        g.add_router(Router("R4", "Switch R4", 170, 270))
        g.add_router(Router("R5", "Distributor R5", 360, 270))
        g.add_router(Router("R6", "Border R6", 550, 200))

        g.add_edge("R1", "R2")
        g.add_edge("R1", "R4")
        g.add_edge("R2", "R3")
        g.add_edge("R2", "R5")
        g.add_edge("R3", "R6")
        g.add_edge("R4", "R5")
        g.add_edge("R5", "R6")
        return g

    @classmethod
    def create_small_connected(cls) -> 'Graph':
        """Small 5-router connected ring-and-chord topology."""
        g = cls(directed=False)
        g.add_router(Router("R1", "Access R1", 110, 180))
        g.add_router(Router("R2", "Core R2", 240, 90))
        g.add_router(Router("R3", "Core R3", 390, 90))
        g.add_router(Router("R4", "Edge R4", 240, 270))
        g.add_router(Router("R5", "Dest R5", 510, 180))

        g.add_edge("R1", "R2")
        g.add_edge("R1", "R4")
        g.add_edge("R2", "R3")
        g.add_edge("R2", "R4")
        g.add_edge("R3", "R5")
        g.add_edge("R4", "R5")
        return g

    @classmethod
    def create_medium_network(cls) -> 'Graph':
        """Realistic 9-router hierarchical network."""
        g = cls(directed=False)
        g.add_router(Router("R1", "Core R1", 100, 180))
        g.add_router(Router("R2", "Dist R2", 240, 80))
        g.add_router(Router("R3", "Dist R3", 240, 280))
        g.add_router(Router("R4", "Transit R4", 380, 80))
        g.add_router(Router("R5", "Center R5", 380, 180))
        g.add_router(Router("R6", "Transit R6", 380, 280))
        g.add_router(Router("R7", "Edge R7", 520, 110))
        g.add_router(Router("R8", "Edge R8", 520, 250))
        g.add_router(Router("R9", "Gateway R9", 640, 180))

        g.add_edge("R1", "R2")
        g.add_edge("R1", "R3")
        g.add_edge("R2", "R4")
        g.add_edge("R2", "R5")
        g.add_edge("R3", "R5")
        g.add_edge("R3", "R6")
        g.add_edge("R4", "R7")
        g.add_edge("R5", "R7")
        g.add_edge("R5", "R8")
        g.add_edge("R6", "R8")
        g.add_edge("R7", "R9")
        g.add_edge("R8", "R9")
        return g

    @classmethod
    def create_disconnected_network(cls) -> 'Graph':
        """Topology partitioned into 2 distinct connected components."""
        g = cls(directed=False)
        # Component 1
        g.add_router(Router("R1", "LAN A Core", 110, 120))
        g.add_router(Router("R2", "LAN A Edge", 250, 100))
        g.add_router(Router("R3", "LAN A Host", 180, 240))
        g.add_edge("R1", "R2")
        g.add_edge("R1", "R3")
        g.add_edge("R2", "R3")

        # Component 2 (Isolated partition)
        g.add_router(Router("R4", "LAN B Core", 440, 120))
        g.add_router(Router("R5", "LAN B Edge", 580, 100))
        g.add_router(Router("R6", "LAN B Host", 510, 240))
        g.add_edge("R4", "R5")
        g.add_edge("R4", "R6")
        g.add_edge("R5", "R6")
        return g

    @classmethod
    def create_alternate_routes(cls) -> 'Graph':
        """
        Topology with direct short path (2 hops) vs longer deep branch (4 hops).
        Demonstrates why BFS guarantees 2 hops while DFS may explore the 4-hop branch!
        """
        g = cls(directed=False)
        g.add_router(Router("R1", "Source R1", 100, 180))
        g.add_router(Router("R2", "Bridge R2", 280, 80))
        g.add_router(Router("R3", "Long A R3", 200, 280))
        g.add_router(Router("R4", "Long B R4", 320, 310))
        g.add_router(Router("R5", "Long C R5", 440, 280))
        g.add_router(Router("R6", "Dest R6", 520, 180))

        # Short path: R1 -> R2 -> R6 (2 hops)
        g.add_edge("R1", "R2")
        g.add_edge("R2", "R6")

        # Long alternate path: R1 -> R3 -> R4 -> R5 -> R6 (4 hops)
        g.add_edge("R1", "R3")
        g.add_edge("R3", "R4")
        g.add_edge("R4", "R5")
        g.add_edge("R5", "R6")
        return g

    @classmethod
    def create_offline_scenario(cls) -> 'Graph':
        """Topology where the primary bottleneck router R2 is offline, forcing reroute via R4."""
        g = cls(directed=False)
        g.add_router(Router("R1", "Ingress R1", 100, 180))
        g.add_router(Router("R2", "Primary (Down)", 290, 100, is_online=False))
        g.add_router(Router("R3", "Backup R3", 290, 270))
        g.add_router(Router("R4", "Backup R4", 430, 270))
        g.add_router(Router("R5", "Egress R5", 550, 180))

        # Direct primary link through offline R2
        g.add_edge("R1", "R2")
        g.add_edge("R2", "R5")

        # Redundant online link through R3 and R4
        g.add_edge("R1", "R3")
        g.add_edge("R3", "R4")
        g.add_edge("R4", "R5")
        return g
