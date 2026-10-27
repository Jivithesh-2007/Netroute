"""
network.py — Network Topology, Router Models, and Graph Representations.

Demonstrates CO2 (Dynamic Data Structures) and CO5 (Graph Representations).
Maintains real-time synchronization between the dynamic Adjacency List O(V + E)
and the Adjacency Matrix O(V^2).
"""

import math
import random
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Any


class Router:
    """Represents a network router (vertex in the graph)."""
    def __init__(self, router_id: str, name: str = "", x: float = 200.0, y: float = 200.0, is_online: bool = True):
        self.id = router_id.strip().upper()
        self.name = name.strip() or f"Router {self.id}"
        self.x = float(x)
        self.y = float(y)
        self.is_online = bool(is_online)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "is_online": self.is_online
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Router":
        return cls(
            router_id=data["id"],
            name=data.get("name", ""),
            x=data.get("x", 200.0),
            y=data.get("y", 200.0),
            is_online=data.get("is_online", True)
        )


class Graph:
    """
    Undirected Network Graph representation.
    Maintains router objects and adjacency lists for fast neighbor traversal.
    """
    def __init__(self):
        self.routers: Dict[str, Router] = {}
        self.adjacency: Dict[str, List[str]] = {}

    def add_router(self, router_id: str, name: str = "", x: float = 200.0, y: float = 200.0, is_online: bool = True) -> bool:
        """Adds a new router with unique ID validation."""
        valid, _ = validate_router_id(router_id)
        if not valid:
            return False
        rid = router_id.strip().upper()
        if rid in self.routers:
            return False
        self.routers[rid] = Router(rid, name, x, y, is_online)
        self.adjacency[rid] = []
        return True

    def remove_router(self, router_id: str) -> bool:
        """Removes a router and safely cascades deletion of all its incident links."""
        rid = router_id.strip().upper()
        if rid not in self.routers:
            return False
        del self.routers[rid]
        del self.adjacency[rid]
        for u in self.adjacency:
            self.adjacency[u] = [v for v in self.adjacency[u] if v != rid]
        return True

    def rename_router(self, router_id: str, new_name: str) -> bool:
        """Renames an existing router."""
        rid = router_id.strip().upper()
        if rid in self.routers and new_name.strip():
            self.routers[rid].name = new_name.strip()
            return True
        return False

    def add_connection(self, u: str, v: str) -> bool:
        """Adds an undirected transmission link between routers u and v."""
        u_id, v_id = u.strip().upper(), v.strip().upper()
        if u_id not in self.routers or v_id not in self.routers or u_id == v_id:
            return False
        if v_id in self.adjacency[u_id]:
            return False  # Link already exists
        self.adjacency[u_id].append(v_id)
        self.adjacency[v_id].append(u_id)
        return True

    def remove_connection(self, u: str, v: str) -> bool:
        """Removes the transmission link between routers u and v."""
        u_id, v_id = u.strip().upper(), v.strip().upper()
        if u_id in self.adjacency and v_id in self.adjacency[u_id]:
            self.adjacency[u_id].remove(v_id)
            self.adjacency[v_id].remove(u_id)
            return True
        return False

    def toggle_router_status(self, router_id: str) -> Optional[bool]:
        """Toggles router online/offline state for failure simulation."""
        rid = router_id.strip().upper()
        if rid in self.routers:
            self.routers[rid].is_online = not self.routers[rid].is_online
            return self.routers[rid].is_online
        return None

    def get_edges(self) -> List[Tuple[str, str]]:
        """Returns sorted list of unique undirected edges (u, v)."""
        edge_set = set()
        for u, neighbors in self.adjacency.items():
            for v in neighbors:
                edge_set.add(tuple(sorted((u, v))))
        return sorted(list(edge_set))

    def get_adjacency_list(self) -> Dict[str, List[str]]:
        """Returns a sorted Adjacency List O(V + E)."""
        return {r: sorted(self.adjacency[r]) for r in sorted(self.routers.keys())}

    def get_adjacency_matrix(self) -> Tuple[List[str], List[List[int]]]:
        """Returns ordered node labels and the 2D Adjacency Matrix O(V^2)."""
        nodes = sorted(self.routers.keys())
        idx_map = {r: i for i, r in enumerate(nodes)}
        n = len(nodes)
        matrix = [[0] * n for _ in range(n)]
        for u, neighbors in self.adjacency.items():
            for v in neighbors:
                if u in idx_map and v in idx_map:
                    matrix[idx_map[u]][idx_map[v]] = 1
        return nodes, matrix

    def get_connected_components(self) -> List[Set[str]]:
        """Finds connected components of online routers using BFS."""
        visited = set()
        components = []
        for rid, router in sorted(self.routers.items()):
            if not router.is_online or rid in visited:
                continue
            comp = set()
            queue = deque([rid])
            visited.add(rid)
            while queue:
                curr = queue.popleft()
                comp.add(curr)
                for nbr in self.adjacency.get(curr, []):
                    if nbr in self.routers and self.routers[nbr].is_online and nbr not in visited:
                        visited.add(nbr)
                        queue.append(nbr)
            components.append(comp)
        return components

    def is_connected(self) -> bool:
        """Returns True if all online routers belong to a single connected component."""
        online_count = sum(1 for r in self.routers.values() if r.is_online)
        if online_count <= 1:
            return True
        comps = self.get_connected_components()
        return len(comps) == 1 and len(comps[0]) == online_count

    def is_reachable(self, src: str, dst: str) -> bool:
        """Checks if a reachable path exists between online src and dst."""
        src, dst = src.strip().upper(), dst.strip().upper()
        if src not in self.routers or dst not in self.routers:
            return False
        if not self.routers[src].is_online or not self.routers[dst].is_online:
            return False
        if src == dst:
            return True
        visited = {src}
        queue = deque([src])
        while queue:
            curr = queue.popleft()
            if curr == dst:
                return True
            for nbr in self.adjacency.get(curr, []):
                if nbr in self.routers and self.routers[nbr].is_online and nbr not in visited:
                    visited.add(nbr)
                    queue.append(nbr)
        return False

    def auto_layout(self):
        """Arranges routers in a deterministic circle for clean visualization."""
        nodes = sorted(self.routers.keys())
        n = len(nodes)
        if n == 0:
            return
        cx, cy = 340.0, 200.0
        radius = min(220.0, max(90.0, 32.0 * n))
        for i, rid in enumerate(nodes):
            angle = (2 * math.pi * i) / n - (math.pi / 2)
            self.routers[rid].x = round(cx + radius * math.cos(angle), 1)
            self.routers[rid].y = round(cy + radius * math.sin(angle), 1)

    def clear(self):
        """Clears all routers and connections."""
        self.routers.clear()
        self.adjacency.clear()

    def load_preset(self, preset_name: str):
        """Loads educational topology presets."""
        self.clear()
        p = preset_name.lower()

        if p == "direct":
            # Linear chain: R1 - R2 - R3 - R4
            nodes = [("R1", 120, 180), ("R2", 260, 180), ("R3", 400, 180), ("R4", 540, 180)]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y)
            for u, v in [("R1", "R2"), ("R2", "R3"), ("R3", "R4")]:
                self.add_connection(u, v)

        elif p == "multi_route":
            # Spine-leaf: upper path 3 hops, lower path 4 hops
            nodes = [
                ("R1", 100, 180), ("R2", 260, 90), ("R3", 420, 90),
                ("R4", 220, 270), ("R5", 340, 270), ("R6", 460, 270),
                ("R7", 580, 180)
            ]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y)
            links = [
                ("R1", "R2"), ("R2", "R3"), ("R3", "R7"),
                ("R1", "R4"), ("R4", "R5"), ("R5", "R6"), ("R6", "R7")
            ]
            for u, v in links:
                self.add_connection(u, v)

        elif p == "cyclic":
            # 6-node cycle with cross-links
            nodes = [
                ("R1", 140, 130), ("R2", 300, 80), ("R3", 460, 130),
                ("R4", 460, 250), ("R5", 300, 300), ("R6", 140, 250)
            ]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y)
            links = [
                ("R1", "R2"), ("R2", "R3"), ("R3", "R4"),
                ("R4", "R5"), ("R5", "R6"), ("R6", "R1"),
                ("R2", "R5"), ("R2", "R4")
            ]
            for u, v in links:
                self.add_connection(u, v)

        elif p == "disconnected":
            # Two isolated subnets (R1-R2-R3) and (R4-R5-R6)
            nodes = [
                ("R1", 140, 120), ("R2", 240, 90), ("R3", 200, 240),
                ("R4", 440, 120), ("R5", 540, 90), ("R6", 500, 240)
            ]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y)
            for u, v in [("R1", "R2"), ("R2", "R3"), ("R1", "R3"), ("R4", "R5"), ("R5", "R6"), ("R4", "R6")]:
                self.add_connection(u, v)

        elif p == "offline_router":
            # Bridge router R2 is offline; bypass via R4 exists
            nodes = [
                ("R1", 120, 180), ("R2", 280, 120), ("R3", 440, 180),
                ("R4", 280, 250), ("R5", 560, 180)
            ]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y, is_online=(rid != "R2"))
            for u, v in [("R1", "R2"), ("R2", "R3"), ("R1", "R4"), ("R4", "R3"), ("R3", "R5")]:
                self.add_connection(u, v)

        else:
            # Default balanced 6-router mesh
            import os
            import json
            sample_file = os.path.join(os.path.dirname(__file__), "data", "sample_network.json")
            loaded_from_file = False
            if os.path.exists(sample_file):
                try:
                    with open(sample_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ok, _ = self.load_from_dict(data)
                    if ok:
                        loaded_from_file = True
                except Exception:
                    loaded_from_file = False

            if not loaded_from_file:
                nodes = [
                    ("R1", 120, 110), ("R2", 300, 70), ("R3", 480, 110),
                    ("R4", 170, 250), ("R5", 350, 260), ("R6", 520, 250)
                ]
                for rid, x, y in nodes:
                    self.add_router(rid, x=x, y=y)
                for u, v in [("R1", "R2"), ("R1", "R4"), ("R2", "R3"), ("R2", "R5"), ("R3", "R6"), ("R4", "R5"), ("R5", "R6")]:
                    self.add_connection(u, v)

    def get_summary(self) -> Dict[str, Any]:
        """Returns high-level graph statistics."""
        online_count = sum(1 for r in self.routers.values() if r.is_online)
        comps = self.get_connected_components()
        return {
            "total_routers": len(self.routers),
            "online_routers": online_count,
            "offline_routers": len(self.routers) - online_count,
            "total_edges": len(self.get_edges()),
            "is_connected": self.is_connected(),
            "component_count": len(comps),
            "components": [sorted(list(c)) for c in comps]
        }

    def generate_random_connected(self, num_routers: int = 6):
        """Generates a connected random network with circular coordinates."""
        self.clear()
        n = max(3, min(12, num_routers))
        names = [f"R{i+1}" for i in range(n)]
        cx, cy, radius = 340.0, 200.0, 160.0
        for i, name in enumerate(names):
            ang = (2 * math.pi * i) / n - (math.pi / 2)
            self.add_router(name, x=round(cx + radius * math.cos(ang), 1), y=round(cy + radius * math.sin(ang), 1))

        # Build spanning tree first to guarantee connectivity
        for i in range(n - 1):
            self.add_connection(names[i], names[i + 1])
        if n > 2:
            self.add_connection(names[-1], names[0])
            for _ in range(n // 2):
                u, v = random.sample(names, 2)
                self.add_connection(u, v)

    def generate_random_disconnected(self, num_routers: int = 6):
        """Generates a partitioned network with two disconnected subnets."""
        self.clear()
        n = max(4, min(12, num_routers))
        half = n // 2
        g1 = [f"R{i+1}" for i in range(half)]
        g2 = [f"R{i+1}" for i in range(half, n)]

        for i, name in enumerate(g1):
            self.add_router(name, x=140.0 + (i % 2) * 110.0, y=100.0 + (i // 2) * 120.0)
        for i, name in enumerate(g2):
            self.add_router(name, x=440.0 + (i % 2) * 110.0, y=100.0 + (i // 2) * 120.0)

        for i in range(len(g1) - 1):
            self.add_connection(g1[i], g1[i + 1])
        if len(g1) > 2:
            self.add_connection(g1[-1], g1[0])

        for i in range(len(g2) - 1):
            self.add_connection(g2[i], g2[i + 1])
        if len(g2) > 2:
            self.add_connection(g2[-1], g2[0])

    def to_dict(self) -> Dict[str, Any]:
        """Serializes topology to a portable dictionary format."""
        return {
            "routers": [r.to_dict() for r in self.routers.values()],
            "edges": self.get_edges()
        }

    def load_from_dict(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Loads and validates a topology from a dictionary."""
        if not isinstance(data, dict) or "routers" not in data or "edges" not in data:
            return False, "Invalid topology format: 'routers' and 'edges' keys required."
        self.clear()
        for rdata in data["routers"]:
            if "id" not in rdata:
                continue
            self.add_router(
                router_id=rdata["id"],
                name=rdata.get("name", ""),
                x=rdata.get("x", 200.0),
                y=rdata.get("y", 200.0),
                is_online=rdata.get("is_online", True)
            )
        for edge in data["edges"]:
            if len(edge) >= 2:
                self.add_connection(edge[0], edge[1])
        return True, f"Loaded {len(self.routers)} routers and {len(self.get_edges())} connections."


def validate_router_id(router_id: str) -> Tuple[bool, str]:
    """Validates router ID format: non-empty, alphanumeric, max 8 chars."""
    rid = router_id.strip().upper()
    if not rid:
        return False, "Router ID cannot be empty."
    if len(rid) > 8:
        return False, "Router ID cannot exceed 8 characters."
    if not rid.isalnum():
        return False, "Router ID must be alphanumeric (e.g., R1, GW2)."
    return True, rid
