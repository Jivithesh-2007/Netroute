import math
import random
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Any


class Router:
    def __init__(self, router_id: str, name: str = "", x: float = 100.0, y: float = 100.0, is_online: bool = True):
        self.id = router_id.strip().upper()
        self.name = name.strip() or f"Router {self.id}"
        self.x = float(x)
        self.y = float(y)
        self.is_online = is_online

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
            x=data.get("x", 100.0),
            y=data.get("y", 100.0),
            is_online=data.get("is_online", True)
        )


class Graph:
    def __init__(self, directed: bool = False):
        self.directed = directed
        self.routers: Dict[str, Router] = {}
        self.edges: Dict[Tuple[str, str], float] = {}
        self.adjacency: Dict[str, List[Tuple[str, float]]] = {}

    def _edge_key(self, u: str, v: str) -> Tuple[str, str]:
        return (u, v) if self.directed else tuple(sorted((u, v)))

    def add_router(self, router_id: str, name: str = "", x: float = 100.0, y: float = 100.0, is_online: bool = True) -> bool:
        rid = router_id.strip().upper()
        if not rid or rid in self.routers:
            return False
        self.routers[rid] = Router(rid, name, x, y, is_online)
        self.adjacency[rid] = []
        return True

    def remove_router(self, router_id: str) -> bool:
        rid = router_id.strip().upper()
        if rid not in self.routers:
            return False
        del self.routers[rid]
        if rid in self.adjacency:
            del self.adjacency[rid]
        to_del = [e for e in self.edges if rid in e]
        for e in to_del:
            del self.edges[e]
        for k in self.adjacency:
            self.adjacency[k] = [entry for entry in self.adjacency[k] if entry[0] != rid]
        return True

    def rename_router(self, router_id: str, new_name: str) -> bool:
        rid = router_id.strip().upper()
        if rid in self.routers and new_name.strip():
            self.routers[rid].name = new_name.strip()
            return True
        return False

    def add_edge(self, u: str, v: str, weight: float = 1.0) -> bool:
        u_id, v_id = u.strip().upper(), v.strip().upper()
        if u_id not in self.routers or v_id not in self.routers or u_id == v_id:
            return False
        key = self._edge_key(u_id, v_id)
        if key in self.edges:
            return False
        self.edges[key] = weight
        if not any(item[0] == v_id for item in self.adjacency[u_id]):
            self.adjacency[u_id].append((v_id, weight))
        if not self.directed:
            if not any(item[0] == u_id for item in self.adjacency[v_id]):
                self.adjacency[v_id].append((u_id, weight))
        return True

    def remove_edge(self, u: str, v: str) -> bool:
        u_id, v_id = u.strip().upper(), v.strip().upper()
        key = self._edge_key(u_id, v_id)
        if key not in self.edges:
            return False
        del self.edges[key]
        if u_id in self.adjacency:
            self.adjacency[u_id] = [entry for entry in self.adjacency[u_id] if entry[0] != v_id]
        if not self.directed and v_id in self.adjacency:
            self.adjacency[v_id] = [entry for entry in self.adjacency[v_id] if entry[0] != u_id]
        return True

    def toggle_router_status(self, router_id: str) -> Optional[bool]:
        rid = router_id.strip().upper()
        if rid in self.routers:
            self.routers[rid].is_online = not self.routers[rid].is_online
            return self.routers[rid].is_online
        return None

    def set_router_position(self, router_id: str, x: float, y: float):
        rid = router_id.strip().upper()
        if rid in self.routers:
            self.routers[rid].x = float(x)
            self.routers[rid].y = float(y)

    def auto_layout(self):
        nodes = sorted(self.routers.keys())
        n = len(nodes)
        if n == 0:
            return
        cx, cy = 300.0, 200.0
        radius = min(220.0, max(80.0, 30.0 * n))
        for i, rid in enumerate(nodes):
            angle = (2 * math.pi * i) / n - (math.pi / 2)
            self.routers[rid].x = round(cx + radius * math.cos(angle), 1)
            self.routers[rid].y = round(cy + radius * math.sin(angle), 1)

    def clear(self):
        self.routers.clear()
        self.edges.clear()
        self.adjacency.clear()

    def get_adjacency_list(self) -> Dict[str, List[str]]:
        res = {}
        for rid in sorted(self.routers.keys()):
            neighbors = sorted([entry[0] for entry in self.adjacency.get(rid, [])])
            res[rid] = neighbors
        return res

    def get_adjacency_matrix(self) -> Tuple[List[str], List[List[float]]]:
        nodes = sorted(self.routers.keys())
        idx_map = {rid: i for i, rid in enumerate(nodes)}
        n = len(nodes)
        matrix = [[0.0] * n for _ in range(n)]
        for (u, v), w in self.edges.items():
            if u in idx_map and v in idx_map:
                i, j = idx_map[u], idx_map[v]
                matrix[i][j] = w
                if not self.directed:
                    matrix[j][i] = w
        return nodes, matrix

    def get_connected_components(self) -> List[Set[str]]:
        visited = set()
        components = []
        for rid in sorted(self.routers.keys()):
            if not self.routers[rid].is_online or rid in visited:
                continue
            comp = set()
            q = deque([rid])
            visited.add(rid)
            comp.add(rid)
            while q:
                curr = q.popleft()
                for neighbor, _ in self.adjacency.get(curr, []):
                    if neighbor in self.routers and self.routers[neighbor].is_online:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            comp.add(neighbor)
                            q.append(neighbor)
            components.append(comp)
        return components

    def is_connected(self) -> bool:
        online_routers = [r for r in self.routers.values() if r.is_online]
        if len(online_routers) <= 1:
            return True
        comps = self.get_connected_components()
        return len(comps) == 1 and len(comps[0]) == len(online_routers)

    def get_reachable_routers(self, start_id: str) -> Set[str]:
        sid = start_id.strip().upper()
        if sid not in self.routers or not self.routers[sid].is_online:
            return set()
        visited = {sid}
        q = deque([sid])
        while q:
            curr = q.popleft()
            for neighbor, _ in self.adjacency.get(curr, []):
                if neighbor in self.routers and self.routers[neighbor].is_online:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
        return visited

    def load_preset(self, preset_type: str):
        self.clear()
        ptype = preset_type.lower()
        if ptype == "direct":
            nodes = [
                ("R1", "Source Router", 120.0, 180.0),
                ("R2", "Transit Router 1", 260.0, 180.0),
                ("R3", "Transit Router 2", 400.0, 180.0),
                ("R4", "Destination Gateway", 540.0, 180.0)
            ]
            for rid, name, x, y in nodes:
                self.add_router(rid, name, x, y)
            for u, v in [("R1", "R2"), ("R2", "R3"), ("R3", "R4")]:
                self.add_edge(u, v)

        elif ptype == "multi_route":
            nodes = [
                ("R1", "Source Gateway R1", 100.0, 180.0),
                ("R2", "Upper Spine R2", 260.0, 90.0),
                ("R3", "Upper Leaf R3", 420.0, 90.0),
                ("R4", "Lower Spine R4", 220.0, 270.0),
                ("R5", "Lower Transit R5", 340.0, 270.0),
                ("R6", "Lower Leaf R6", 460.0, 270.0),
                ("R7", "Destination Router R7", 580.0, 180.0)
            ]
            for rid, name, x, y in nodes:
                self.add_router(rid, name, x, y)
            links = [
                ("R1", "R2"), ("R2", "R3"), ("R3", "R7"),
                ("R1", "R4"), ("R4", "R5"), ("R5", "R6"), ("R6", "R7")
            ]
            for u, v in links:
                self.add_edge(u, v)

        elif ptype == "cyclic":
            nodes = [
                ("R1", "Gateway R1", 140.0, 130.0),
                ("R2", "Core Node R2", 300.0, 80.0),
                ("R3", "Border Node R3", 460.0, 130.0),
                ("R4", "Switch R4", 460.0, 250.0),
                ("R5", "Distributor R5", 300.0, 300.0),
                ("R6", "Access Node R6", 140.0, 250.0)
            ]
            for rid, name, x, y in nodes:
                self.add_router(rid, name, x, y)
            links = [
                ("R1", "R2"), ("R2", "R3"), ("R3", "R4"),
                ("R4", "R5"), ("R5", "R6"), ("R6", "R1"),
                ("R2", "R5"), ("R2", "R4"), ("R1", "R5")
            ]
            for u, v in links:
                self.add_edge(u, v)

        elif ptype == "disconnected":
            nodes = [
                ("R1", "Subnet-A Router 1", 120.0, 120.0),
                ("R2", "Subnet-A Router 2", 240.0, 90.0),
                ("R3", "Subnet-A Router 3", 200.0, 240.0),
                ("R4", "Subnet-B Router 4", 440.0, 120.0),
                ("R5", "Subnet-B Router 5", 560.0, 90.0),
                ("R6", "Subnet-B Router 6", 500.0, 240.0)
            ]
            for rid, name, x, y in nodes:
                self.add_router(rid, name, x, y)
            links = [
                ("R1", "R2"), ("R2", "R3"), ("R1", "R3"),
                ("R4", "R5"), ("R5", "R6"), ("R4", "R6")
            ]
            for u, v in links:
                self.add_edge(u, v)

        elif ptype == "offline_router":
            nodes = [
                ("R1", "Source R1", 120.0, 180.0),
                ("R2", "Bridge R2 (OFFLINE)", 280.0, 120.0),
                ("R3", "Core Switch R3", 440.0, 180.0),
                ("R4", "Bypass Router R4", 280.0, 250.0),
                ("R5", "Destination R5", 560.0, 180.0)
            ]
            for rid, name, x, y in nodes:
                self.add_router(rid, name, x, y, is_online=(rid != "R2"))
            links = [
                ("R1", "R2"), ("R2", "R3"),
                ("R1", "R4"), ("R4", "R3"),
                ("R3", "R5")
            ]
            for u, v in links:
                self.add_edge(u, v)

        else:
            samples = [
                ("R1", "Core Gateway R1", 120.0, 110.0),
                ("R2", "Distribution R2", 300.0, 70.0),
                ("R3", "Edge Switch R3", 480.0, 110.0),
                ("R4", "Branch Router R4", 170.0, 250.0),
                ("R5", "Data Center R5", 350.0, 260.0),
                ("R6", "Border Gateway R6", 520.0, 250.0)
            ]
            for rid, name, x, y in samples:
                self.add_router(rid, name, x, y)
            links = [
                ("R1", "R2"), ("R1", "R4"),
                ("R2", "R3"), ("R2", "R5"),
                ("R3", "R6"), ("R4", "R5"),
                ("R5", "R6")
            ]
            for u, v in links:
                self.add_edge(u, v)

    def generate_connected(self, num_routers: int = 6):
        self.clear()
        names = [f"R{i+1}" for i in range(num_routers)]
        cx, cy = 330.0, 180.0
        angle_step = (2 * math.pi) / num_routers
        for i, name in enumerate(names):
            x = cx + 180.0 * math.cos(i * angle_step)
            y = cy + 110.0 * math.sin(i * angle_step)
            self.add_router(name, f"Router {name}", round(x, 1), round(y, 1))

        for i in range(num_routers - 1):
            self.add_edge(names[i], names[i + 1])
        if num_routers > 2:
            self.add_edge(names[num_routers - 1], names[0])
            for _ in range(num_routers // 2):
                u, v = random.sample(names, 2)
                self.add_edge(u, v)

    def generate_disconnected(self, num_routers: int = 6):
        self.clear()
        names = [f"R{i+1}" for i in range(num_routers)]
        half = max(2, num_routers // 2)
        group1 = names[:half]
        group2 = names[half:]

        for i, name in enumerate(group1):
            x = 120.0 + (i % 2) * 110.0
            y = 100.0 + (i // 2) * 120.0
            self.add_router(name, f"Subnet-A {name}", x, y)

        for i, name in enumerate(group2):
            x = 420.0 + (i % 2) * 110.0
            y = 100.0 + (i // 2) * 120.0
            self.add_router(name, f"Subnet-B {name}", x, y)

        for i in range(len(group1) - 1):
            self.add_edge(group1[i], group1[i + 1])
        if len(group1) > 2:
            self.add_edge(group1[-1], group1[0])

        for i in range(len(group2) - 1):
            self.add_edge(group2[i], group2[i + 1])
        if len(group2) > 2:
            self.add_edge(group2[-1], group2[0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "directed": self.directed,
            "routers": [r.to_dict() for r in self.routers.values()],
            "edges": [[u, v, w] for (u, v), w in self.edges.items()]
        }

    def load_from_dict(self, data: Dict[str, Any]):
        self.clear()
        self.directed = data.get("directed", False)
        for rdata in data.get("routers", []):
            self.routers[rdata["id"]] = Router.from_dict(rdata)
            self.adjacency[rdata["id"]] = []
        for item in data.get("edges", []):
            if len(item) >= 2:
                u, v = item[0], item[1]
                w = float(item[2]) if len(item) > 2 else 1.0
                self.add_edge(u, v, w)


def validate_router_id(router_id: str) -> Tuple[bool, str]:
    rid = router_id.strip().upper()
    if not rid:
        return False, "Router ID cannot be empty."
    if len(rid) > 8:
        return False, "Router ID cannot exceed 8 characters."
    if not rid.isalnum():
        return False, "Router ID must be alphanumeric (e.g. R1, GW2)."
    return True, rid
