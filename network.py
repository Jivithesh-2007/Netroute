import math
from collections import deque
from typing import Dict, List, Set, Tuple


class Graph:
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        self.adj: Dict[str, List[str]] = {}

    def add_node(self, nid: str, name: str = "", x: float = 200.0, y: float = 200.0, online: bool = True) -> bool:
        nid = nid.strip().upper()
        if not nid or nid in self.nodes:
            return False
        self.nodes[nid] = {"name": name or f"Router {nid}", "x": float(x), "y": float(y), "online": online}
        self.adj[nid] = []
        return True

    def remove_node(self, nid: str) -> bool:
        nid = nid.strip().upper()
        if nid not in self.nodes:
            return False
        del self.nodes[nid]
        del self.adj[nid]
        for u in self.adj:
            self.adj[u] = [v for v in self.adj[u] if v != nid]
        return True

    def add_edge(self, u: str, v: str) -> bool:
        u, v = u.strip().upper(), v.strip().upper()
        if u not in self.nodes or v not in self.nodes or u == v:
            return False
        if v not in self.adj[u]:
            self.adj[u].append(v)
        if u not in self.adj[v]:
            self.adj[v].append(u)
        return True

    def remove_edge(self, u: str, v: str) -> bool:
        u, v = u.strip().upper(), v.strip().upper()
        if u in self.adj and v in self.adj[u]:
            self.adj[u].remove(v)
            self.adj[v].remove(u)
            return True
        return False

    def toggle_node(self, nid: str) -> bool:
        nid = nid.strip().upper()
        if nid in self.nodes:
            self.nodes[nid]["online"] = not self.nodes[nid]["online"]
            return self.nodes[nid]["online"]
        return False

    def get_edges(self) -> List[Tuple[str, str]]:
        edges = set()
        for u, nbrs in self.adj.items():
            for v in nbrs:
                edges.add(tuple(sorted((u, v))))
        return sorted(list(edges))

    def get_matrix(self) -> Tuple[List[str], List[List[int]]]:
        nodes = sorted(self.nodes.keys())
        idx = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        mat = [[0] * n for _ in range(n)]
        for u, nbrs in self.adj.items():
            for v in nbrs:
                if u in idx and v in idx:
                    mat[idx[u]][idx[v]] = 1
        return nodes, mat

    def get_components(self) -> List[Set[str]]:
        visited = set()
        comps = []
        for n, data in sorted(self.nodes.items()):
            if not data["online"] or n in visited:
                continue
            comp = set()
            q = deque([n])
            visited.add(n)
            while q:
                curr = q.popleft()
                comp.add(curr)
                for nbr in self.adj.get(curr, []):
                    if self.nodes[nbr]["online"] and nbr not in visited:
                        visited.add(nbr)
                        q.append(nbr)
            comps.append(comp)
        return comps

    def auto_layout(self):
        nodes = sorted(self.nodes.keys())
        n = len(nodes)
        if n == 0:
            return
        cx, cy, r = 320.0, 200.0, min(200.0, max(90.0, 30.0 * n))
        for i, nid in enumerate(nodes):
            angle = (2 * math.pi * i) / n - (math.pi / 2)
            self.nodes[nid]["x"] = round(cx + r * math.cos(angle), 1)
            self.nodes[nid]["y"] = round(cy + r * math.sin(angle), 1)

    def load_preset(self, name: str):
        self.nodes.clear()
        self.adj.clear()
        presets = {
            "sample": (
                [("R1", 120, 110), ("R2", 300, 70), ("R3", 480, 110), ("R4", 170, 250), ("R5", 350, 260), ("R6", 520, 250)],
                [("R1", "R2"), ("R1", "R4"), ("R2", "R3"), ("R2", "R5"), ("R3", "R6"), ("R4", "R5"), ("R5", "R6")],
                []
            ),
            "direct": (
                [("R1", 120, 180), ("R2", 260, 180), ("R3", 400, 180), ("R4", 540, 180)],
                [("R1", "R2"), ("R2", "R3"), ("R3", "R4")],
                []
            ),
            "multi_route": (
                [("R1", 100, 180), ("R2", 260, 90), ("R3", 420, 90), ("R4", 220, 270), ("R5", 340, 270), ("R6", 460, 270), ("R7", 580, 180)],
                [("R1", "R2"), ("R2", "R3"), ("R3", "R7"), ("R1", "R4"), ("R4", "R5"), ("R5", "R6"), ("R6", "R7")],
                []
            ),
            "cyclic": (
                [("R1", 140, 130), ("R2", 300, 80), ("R3", 460, 130), ("R4", 460, 250), ("R5", 300, 300), ("R6", 140, 250)],
                [("R1", "R2"), ("R2", "R3"), ("R3", "R4"), ("R4", "R5"), ("R5", "R6"), ("R6", "R1"), ("R2", "R5")],
                []
            ),
            "disconnected": (
                [("R1", 140, 120), ("R2", 240, 90), ("R3", 200, 240), ("R4", 440, 120), ("R5", 540, 90), ("R6", 500, 240)],
                [("R1", "R2"), ("R2", "R3"), ("R1", "R3"), ("R4", "R5"), ("R5", "R6"), ("R4", "R6")],
                []
            ),
            "offline_router": (
                [("R1", 120, 180), ("R2", 280, 120), ("R3", 440, 180), ("R4", 280, 250), ("R5", 560, 180)],
                [("R1", "R2"), ("R2", "R3"), ("R1", "R4"), ("R4", "R3"), ("R3", "R5")],
                ["R2"]
            )
        }
        data = presets.get(name, presets["sample"])
        for nid, x, y in data[0]:
            self.add_node(nid, x=x, y=y, online=(nid not in data[2]))
        for u, v in data[1]:
            self.add_edge(u, v)

    def to_dict(self) -> dict:
        return {
            "nodes": [{"id": k, **v} for k, v in self.nodes.items()],
            "edges": self.get_edges()
        }

    def load_from_dict(self, data: dict):
        self.nodes.clear()
        self.adj.clear()
        for item in data.get("nodes", []):
            self.add_node(item["id"], item.get("name", ""), item.get("x", 200), item.get("y", 200), item.get("online", True))
        for u, v in data.get("edges", []):
            self.add_edge(u, v)
