"""
network.py — Network Topology, Router Models, and Graph Representations.

Provides:
- Graph Operations (Adding/Removing Vertices & Edges, Adjacency Lists/Matrices)
- Network Graph Representation & Traditional Routing Table Generation
"""

import math
import os
import json
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
        self.weights: Dict[Tuple[str, str], float] = {}
        self.failed_edges: Set[Tuple[str, str]] = set()

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
        self.weights = {k: w for k, w in self.weights.items() if rid not in k}
        self.failed_edges = {k for k in self.failed_edges if rid not in k}
        return True

    def rename_router(self, router_id: str, new_name: str) -> bool:
        """Renames an existing router."""
        rid = router_id.strip().upper()
        if rid in self.routers and new_name.strip():
            self.routers[rid].name = new_name.strip()
            return True
        return False

    def auto_layout(self):
        """Arranges all routers in a balanced circular layout for clear visualization."""
        nodes = sorted(self.routers.keys())
        n = len(nodes)
        if n == 0:
            return
        cx, cy = 360.0, 210.0
        radius = min(220.0, max(100.0, 28.0 * n))
        for i, rid in enumerate(nodes):
            angle = (2 * math.pi * i) / n - (math.pi / 2)
            self.routers[rid].x = round(cx + radius * math.cos(angle), 1)
            self.routers[rid].y = round(cy + radius * math.sin(angle), 1)

    def add_connection(self, u: str, v: str, weight: float = 1.0) -> bool:
        """Adds an undirected transmission link between routers u and v."""
        u_id, v_id = u.strip().upper(), v.strip().upper()
        if u_id not in self.routers or v_id not in self.routers or u_id == v_id:
            return False
        if v_id in self.adjacency[u_id]:
            return False
        if weight < 0:
            return False
        self.adjacency[u_id].append(v_id)
        self.adjacency[v_id].append(u_id)
        pair = tuple(sorted((u_id, v_id)))
        self.weights[pair] = float(weight)
        return True

    def remove_connection(self, u: str, v: str) -> bool:
        """Removes the transmission link between routers u and v."""
        u_id, v_id = u.strip().upper(), v.strip().upper()
        if u_id in self.adjacency and v_id in self.adjacency[u_id]:
            self.adjacency[u_id].remove(v_id)
            self.adjacency[v_id].remove(u_id)
            pair = tuple(sorted((u_id, v_id)))
            self.weights.pop(pair, None)
            self.failed_edges.discard(pair)
            return True
        return False

    def get_neighbors(self, router_id: str) -> List[str]:
        """Returns sorted list of neighbor router IDs for a given router."""
        rid = router_id.strip().upper()
        return sorted(self.adjacency.get(rid, []))

    def get_weight(self, u: str, v: str) -> float:
        """Returns the weight / cost of the link between u and v."""
        pair = tuple(sorted((u.strip().upper(), v.strip().upper())))
        return self.weights.get(pair, 1.0)

    def set_weight(self, u: str, v: str, weight: float) -> bool:
        """Sets the weight of an existing connection."""
        if weight < 0:
            return False
        u_id, v_id = u.strip().upper(), v.strip().upper()
        if u_id not in self.routers or v_id not in self.routers:
            return False
        pair = tuple(sorted((u_id, v_id)))
        if v_id not in self.adjacency.get(u_id, []):
            return False
        self.weights[pair] = float(weight)
        return True

    def toggle_edge_failure(self, u: str, v: str) -> Optional[bool]:
        """Toggles link active/failed state for testing. Returns True if active, False if failed."""
        u_id, v_id = u.strip().upper(), v.strip().upper()
        if u_id not in self.routers or v_id not in self.routers:
            return None
        pair = tuple(sorted((u_id, v_id)))
        if v_id not in self.adjacency.get(u_id, []):
            return None
        if pair in self.failed_edges:
            self.failed_edges.remove(pair)
            return True
        else:
            self.failed_edges.add(pair)
            return False

    def is_edge_active(self, u: str, v: str) -> bool:
        """Checks if link between u and v is active."""
        pair = tuple(sorted((u.strip().upper(), v.strip().upper())))
        return pair not in self.failed_edges

    def toggle_router_status(self, router_id: str) -> Optional[bool]:
        """Toggles router online/offline state."""
        rid = router_id.strip().upper()
        if rid in self.routers:
            self.routers[rid].is_online = not self.routers[rid].is_online
            return self.routers[rid].is_online
        return None

    def set_router_status(self, router_id: str, is_online: bool) -> bool:
        """Sets a router explicitly to online or offline."""
        rid = router_id.strip().upper()
        if rid in self.routers:
            self.routers[rid].is_online = bool(is_online)
            return True
        return False

    def get_edges(self) -> List[Tuple[str, str]]:
        """Returns sorted list of unique undirected edges (u, v)."""
        edge_set = set()
        for u, neighbors in self.adjacency.items():
            for v in neighbors:
                edge_set.add(tuple(sorted((u, v))))
        return sorted(list(edge_set))

    def get_adjacency_list(self) -> Dict[str, List[str]]:
        """Returns sorted Adjacency List O(V + E)."""
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
                    if (nbr in self.routers and self.routers[nbr].is_online 
                            and self.is_edge_active(curr, nbr) and nbr not in visited):
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
        """Checks if a reachable path exists between online src and dst across active links."""
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
                if (nbr in self.routers and self.routers[nbr].is_online 
                        and self.is_edge_active(curr, nbr) and nbr not in visited):
                    visited.add(nbr)
                    queue.append(nbr)
        return False

    def generate_routing_table(self, source_id: str) -> List[Dict[str, Any]]:
        """
        Generates the traditional forwarding/routing table for the selected source router.
        
        Demonstrates the contrast between graph-based on-demand route discovery
        and traditional hop-by-hop routing table lookups:
        - Destination: Target router ID
        - Next Hop: The immediate neighbor to which packets for Destination must be forwarded
        - Hop Count: Minimum number of hops to reach Destination
        - Status: Local, Direct Neighbor, Reachable, or Unreachable
        """
        src = source_id.strip().upper()
        if src not in self.routers or not self.routers[src].is_online:
            table: List[Dict[str, Any]] = []
            for dest in sorted(self.routers.keys()):
                table.append({
                    "destination": dest,
                    "next_hop": "None",
                    "hops": -1,
                    "status": "Source Offline" if src in self.routers else "Source Not Found"
                })
            return table

        parents: Dict[str, Optional[str]] = {src: None}
        queue = deque([src])
        visited = {src}

        while queue:
            curr = queue.popleft()
            for nbr in sorted(self.adjacency.get(curr, [])):
                if (nbr in self.routers and 
                        self.routers[nbr].is_online and 
                        self.is_edge_active(curr, nbr) and 
                        nbr not in visited):
                    visited.add(nbr)
                    parents[nbr] = curr
                    queue.append(nbr)

        table = []
        for dest in sorted(self.routers.keys()):
            if dest == src:
                table.append({
                    "destination": dest,
                    "next_hop": src,
                    "hops": 0,
                    "status": "Local (Self)"
                })
            elif dest in parents:
                path: List[str] = []
                curr_node: Optional[str] = dest
                while curr_node is not None:
                    path.append(curr_node)
                    curr_node = parents.get(curr_node)
                path.reverse()
                next_hop = path[1] if len(path) > 1 else dest
                hops = len(path) - 1
                status = "Direct Neighbor" if hops == 1 else "Reachable"
                table.append({
                    "destination": dest,
                    "next_hop": next_hop,
                    "hops": hops,
                    "status": status
                })
            else:
                table.append({
                    "destination": dest,
                    "next_hop": "None",
                    "hops": -1,
                    "status": "Unreachable"
                })

        return table

    def clear(self):
        """Clears all routers, connections, weights, and failure states."""
        self.routers.clear()
        self.adjacency.clear()
        self.weights.clear()
        self.failed_edges.clear()

    @classmethod
    def from_preset(cls, preset_name: str) -> "Graph":
        """Factory method to construct a Graph initialized with a preset."""
        g = cls()
        g.load_preset(preset_name)
        return g

    def load_preset(self, preset_name: str):
        """Loads educational topology presets."""
        self.clear()
        p = preset_name.lower().strip()

        if p in ("reference", "default"):
            # Reference 7-Node WAN
            ref_file = os.path.join(os.path.dirname(__file__), "data", "reference_network.json")
            if os.path.exists(ref_file):
                try:
                    with open(ref_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ok, _ = self.load_from_dict(data)
                    if ok:
                        return
                except Exception:
                    pass

            nodes = [
                ("N1", "Server A (Src)", 100.0, 220.0),
                ("N2", "Router 1", 230.0, 140.0),
                ("N3", "Router 2", 230.0, 300.0),
                ("N4", "Router 3", 380.0, 140.0),
                ("N5", "Router 4", 380.0, 300.0),
                ("N6", "Switch B", 510.0, 220.0),
                ("N7", "Server B (Dst)", 630.0, 220.0)
            ]
            for rid, name, x, y in nodes:
                self.add_router(rid, name=name, x=x, y=y)
            links = [
                ("N1", "N2", 4.0), ("N1", "N3", 8.0), ("N2", "N3", 3.0),
                ("N2", "N4", 10.0), ("N3", "N5", 2.0), ("N4", "N5", 5.0),
                ("N4", "N6", 4.0), ("N5", "N6", 7.0), ("N6", "N7", 1.0)
            ]
            for u, v, w in links:
                self.add_connection(u, v, weight=w)

        elif p in ("ring", "cyclic"):
            # 6-Node Circular Ring Network: R1 to R6 in a circle
            cx, cy, r = 360.0, 210.0, 140.0
            for i in range(6):
                rid = f"R{i+1}"
                angle = (2 * math.pi * i) / 6 - (math.pi / 2)
                x = round(cx + r * math.cos(angle), 1)
                y = round(cy + r * math.sin(angle), 1)
                self.add_router(rid, name=f"Node {rid}", x=x, y=y)
            
            ring_links = [("R1", "R2"), ("R2", "R3"), ("R3", "R4"), ("R4", "R5"), ("R5", "R6"), ("R6", "R1")]
            for u, v in ring_links:
                self.add_connection(u, v, weight=1.0)

        elif p in ("mesh", "sample", "full_mesh"):
            # 6-Node Interconnected Mesh Network
            sample_file = os.path.join(os.path.dirname(__file__), "data", "sample_network.json")
            if os.path.exists(sample_file):
                try:
                    with open(sample_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ok, _ = self.load_from_dict(data)
                    if ok:
                        return
                except Exception:
                    pass

            nodes = [
                ("R1", "Router R1", 120.0, 120.0),
                ("R2", "Router R2", 320.0, 80.0),
                ("R3", "Router R3", 520.0, 140.0),
                ("R4", "Router R4", 180.0, 300.0),
                ("R5", "Router R5", 380.0, 320.0),
                ("R6", "Router R6", 580.0, 300.0)
            ]
            for rid, name, x, y in nodes:
                self.add_router(rid, name=name, x=x, y=y)
            mesh_links = [
                ("R1", "R2"), ("R1", "R4"), ("R2", "R3"), ("R2", "R5"),
                ("R3", "R6"), ("R4", "R5"), ("R5", "R6"), ("R2", "R4")
            ]
            for u, v in mesh_links:
                self.add_connection(u, v, weight=1.0)

        elif p == "disconnected":
            # Two isolated subnets: (R1-R2-R3) and (R4-R5-R6)
            nodes = [
                ("R1", "Subnet A (R1)", 140.0, 130.0),
                ("R2", "Subnet A (R2)", 260.0, 90.0),
                ("R3", "Subnet A (R3)", 200.0, 270.0),
                ("R4", "Subnet B (R4)", 440.0, 130.0),
                ("R5", "Subnet B (R5)", 560.0, 90.0),
                ("R6", "Subnet B (R6)", 500.0, 270.0)
            ]
            for rid, name, x, y in nodes:
                self.add_router(rid, name=name, x=x, y=y)
            for u, v in [("R1", "R2"), ("R2", "R3"), ("R1", "R3"), ("R4", "R5"), ("R5", "R6"), ("R4", "R6")]:
                self.add_connection(u, v, weight=1.0)

        elif p == "direct":
            # Linear chain for testing: R1 - R2 - R3 - R4
            nodes = [("R1", 120.0, 200.0), ("R2", 260.0, 200.0), ("R3", 400.0, 200.0), ("R4", 540.0, 200.0)]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y)
            for u, v in [("R1", "R2"), ("R2", "R3"), ("R3", "R4")]:
                self.add_connection(u, v, weight=1.0)

        elif p == "multi_route":
            # Spine-leaf test network: upper path 3 hops, lower path 4 hops
            nodes = [
                ("R1", 100.0, 180.0), ("R2", 260.0, 90.0), ("R3", 420.0, 90.0),
                ("R4", 220.0, 270.0), ("R5", 340.0, 270.0), ("R6", 460.0, 270.0),
                ("R7", 580.0, 180.0)
            ]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y)
            links = [
                ("R1", "R2"), ("R2", "R3"), ("R3", "R7"),
                ("R1", "R4"), ("R4", "R5"), ("R5", "R6"), ("R6", "R7")
            ]
            for u, v in links:
                self.add_connection(u, v, weight=1.0)

        elif p == "offline_router":
            # R2 is offline on bridge R1-R2-R3. Bypass via R4 exists
            nodes = [
                ("R1", 120.0, 180.0), ("R2", 280.0, 120.0), ("R3", 440.0, 180.0),
                ("R4", 280.0, 250.0), ("R5", 560.0, 180.0)
            ]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y, is_online=(rid != "R2"))
            for u, v in [("R1", "R2"), ("R2", "R3"), ("R1", "R4"), ("R4", "R3"), ("R3", "R5")]:
                self.add_connection(u, v, weight=1.0)

        else:
            # Fallback to reference network
            self.load_preset("reference")

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

    def to_dict(self) -> Dict[str, Any]:
        """Serializes topology to a portable dictionary format."""
        return {
            "routers": [r.to_dict() for r in self.routers.values()],
            "edges": [[u, v, self.get_weight(u, v)] for (u, v) in self.get_edges()],
            "failed_edges": [list(e) for e in self.failed_edges]
        }

    def load_from_dict(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Loads and strictly validates a topology from a dictionary without corrupting existing state on failure."""
        if not isinstance(data, dict):
            return False, "Invalid topology format: JSON root must be an object."
        if "routers" not in data or not isinstance(data["routers"], list):
            return False, "Invalid topology format: 'routers' list is required."
        if "edges" not in data or not isinstance(data["edges"], list):
            return False, "Invalid topology format: 'edges' list is required."

        temp_g = Graph()
        seen_rids = set()

        for idx, rdata in enumerate(data["routers"]):
            if not isinstance(rdata, dict) or "id" not in rdata:
                return False, f"Router entry at index {idx} must be an object with an 'id' property."
            raw_id = str(rdata["id"]).strip().upper()
            ok_id, msg_id = validate_router_id(raw_id)
            if not ok_id:
                return False, f"Invalid router ID '{raw_id}' at index {idx}: {msg_id}"
            if raw_id in seen_rids:
                return False, f"Duplicate router ID '{raw_id}' in topology."
            seen_rids.add(raw_id)

            try:
                rx = float(rdata.get("x", 200.0))
                ry = float(rdata.get("y", 200.0))
            except (ValueError, TypeError):
                rx, ry = 200.0, 200.0

            rname = str(rdata.get("name", "")).strip() or f"Router {raw_id}"
            ronline = bool(rdata.get("is_online", True))
            temp_g.add_router(raw_id, name=rname, x=rx, y=ry, is_online=ronline)

        for idx, edge in enumerate(data["edges"]):
            if not isinstance(edge, (list, tuple)) or len(edge) < 2:
                return False, f"Edge entry at index {idx} must contain at least [u, v]."
            u = str(edge[0]).strip().upper()
            v = str(edge[1]).strip().upper()
            if u not in temp_g.routers:
                return False, f"Edge ({u}, {v}) references non-existent router '{u}'."
            if v not in temp_g.routers:
                return False, f"Edge ({u}, {v}) references non-existent router '{v}'."
            if u == v:
                return False, f"Self-loop edge ({u}, {u}) is not allowed."
            w = 1.0
            if len(edge) >= 3:
                try:
                    w = float(edge[2])
                    if w < 0:
                        return False, f"Edge ({u}, {v}) has negative weight {w}."
                except (ValueError, TypeError):
                    w = 1.0
            temp_g.add_connection(u, v, weight=w)

        failed_list = data.get("failed_edges", [])
        if isinstance(failed_list, list):
            for fe in failed_list:
                if isinstance(fe, (list, tuple)) and len(fe) >= 2:
                    fu = str(fe[0]).strip().upper()
                    fv = str(fe[1]).strip().upper()
                    if fu in temp_g.routers and fv in temp_g.routers:
                        temp_g.failed_edges.add(tuple(sorted((fu, fv))))

        # Transactionally commit changes to self
        self.routers = temp_g.routers
        self.adjacency = temp_g.adjacency
        self.weights = temp_g.weights
        self.failed_edges = temp_g.failed_edges
        return True, f"Successfully loaded {len(self.routers)} routers and {len(self.get_edges())} connections."


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
