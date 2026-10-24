import json
import time
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any

@dataclass
class SimulationStep:
    step_type: str
    current_element: Optional[Any] = None
    data_structure_state: Optional[List[Any]] = None
    visited_elements: List[Any] = field(default_factory=list)
    active_path: List[Any] = field(default_factory=list)
    message: str = ""
    highlight_indices: List[int] = field(default_factory=list)
    secondary_indices: List[int] = field(default_factory=list)
    extra_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SimulationResult:
    algorithm_name: str
    success: bool
    path: List[Any] = field(default_factory=list)
    visited_order: List[Any] = field(default_factory=list)
    total_steps: int = 0
    total_comparisons: int = 0
    total_swaps: int = 0
    execution_time_ms: float = 0.0
    steps: List[SimulationStep] = field(default_factory=list)
    message: str = ""
    extra_info: Dict[str, Any] = field(default_factory=dict)

class Router:
    def __init__(self, router_id: str, name: str, x: float, y: float, is_online: bool = True):
        self.id = router_id
        self.name = name
        self.x = x
        self.y = y
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
    def from_dict(cls, data: Dict[str, Any]) -> 'Router':
        return cls(
            router_id=data["id"],
            name=data["name"],
            x=data["x"],
            y=data["y"],
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
        rname = name.strip() or f"Router {rid}"
        self.routers[rid] = Router(rid, rname, x, y, is_online)
        self.adjacency[rid] = []
        return True

    def remove_router(self, router_id: str) -> bool:
        rid = router_id.strip().upper()
        if rid not in self.routers:
            return False
        del self.routers[rid]
        del self.adjacency[rid]
        to_del = [e for e in self.edges if rid in e]
        for e in to_del:
            del self.edges[e]
        for k in self.adjacency:
            self.adjacency[k] = [entry for entry in self.adjacency[k] if entry[0] != rid]
        return True

    def add_edge(self, u: str, v: str, weight: float = 1.0) -> bool:
        u_id, v_id = u.strip().upper(), v.strip().upper()
        if u_id not in self.routers or v_id not in self.routers or u_id == v_id:
            return False
        key = self._edge_key(u_id, v_id)
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
            self.routers[rid].x = x
            self.routers[rid].y = y

    def clear(self):
        self.routers.clear()
        self.edges.clear()
        self.adjacency.clear()

    def load_sample_topology(self):
        self.clear()
        samples = [
            ("R1", "Core Gateway R1", 120.0, 100.0),
            ("R2", "Distribution R2", 300.0, 60.0),
            ("R3", "Edge Switch R3", 480.0, 100.0),
            ("R4", "Branch Router R4", 180.0, 240.0),
            ("R5", "Data Center R5", 360.0, 250.0),
            ("R6", "Border Gateway R6", 520.0, 240.0)
        ]
        for rid, name, x, y in samples:
            self.add_router(rid, name, x, y)
        links = [
            ("R1", "R2", 1.0),
            ("R1", "R4", 1.0),
            ("R2", "R3", 1.0),
            ("R2", "R5", 1.0),
            ("R3", "R6", 1.0),
            ("R4", "R5", 1.0),
            ("R5", "R6", 1.0)
        ]
        for u, v, w in links:
            self.add_edge(u, v, w)

    def generate_random(self, num_routers: int = 6):
        self.clear()
        names = [f"R{i+1}" for i in range(num_routers)]
        center_x, center_y = 320.0, 180.0
        import math
        angle_step = (2 * math.pi) / num_routers
        for i, name in enumerate(names):
            x = center_x + 180.0 * math.cos(i * angle_step)
            y = center_y + 110.0 * math.sin(i * angle_step)
            self.add_router(name, f"Router {name}", round(x, 1), round(y, 1))
        for i in range(num_routers):
            self.add_edge(names[i], names[(i + 1) % num_routers], 1.0)
        for _ in range(num_routers // 2):
            u, v = random.sample(names, 2)
            if u != v:
                self.add_edge(u, v, 1.0)

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
                    if self.routers.get(neighbor) and self.routers[neighbor].is_online:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            comp.add(neighbor)
                            q.append(neighbor)
            components.append(comp)
        return components

    def is_connected(self) -> bool:
        online_count = sum(1 for r in self.routers.values() if r.is_online)
        if online_count <= 1:
            return True
        components = self.get_connected_components()
        return len(components) == 1

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

def bfs_path(graph: Graph, start_id: str, end_id: str) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    start_id = start_id.strip().upper()
    end_id = end_id.strip().upper()

    if start_id not in graph.routers or end_id not in graph.routers:
        return SimulationResult(
            algorithm_name="BFS Routing",
            success=False,
            message="Invalid start or destination router."
        )

    if not graph.routers[start_id].is_online:
        return SimulationResult(
            algorithm_name="BFS Routing",
            success=False,
            message=f"Source router {start_id} is offline."
        )

    if not graph.routers[end_id].is_online:
        return SimulationResult(
            algorithm_name="BFS Routing",
            success=False,
            message=f"Destination router {end_id} is offline."
        )

    queue = deque([start_id])
    visited: Set[str] = {start_id}
    parent: Dict[str, Optional[str]] = {start_id: None}
    dist: Dict[str, int] = {start_id: 0}
    visited_order: List[str] = []
    step_details: List[Dict[str, Any]] = []

    steps.append(SimulationStep(
        step_type="enqueue",
        current_element=start_id,
        data_structure_state=list(queue),
        visited_elements=[],
        message=f"Source router '{start_id}' enqueued into BFS FIFO Queue (Level 0).",
        extra_info={"visited_order": [], "dist": dict(dist)}
    ))

    found = False
    comparisons = 0

    while queue:
        curr = queue.popleft()
        visited_order.append(curr)
        curr_dist = dist.get(curr, 0)

        step_details.append({
            "order": len(visited_order),
            "router": curr,
            "action": "Source Initialized" if curr == start_id else ("Target Reached" if curr == end_id else "Dequeued & Visited"),
            "level": curr_dist,
            "role": "Source" if curr == start_id else ("Destination" if curr == end_id else "Router")
        })

        steps.append(SimulationStep(
            step_type="dequeue",
            current_element=curr,
            data_structure_state=list(queue),
            visited_elements=list(visited_order),
            message=f"Visited #{len(visited_order)}: Dequeued '{curr}' (Hop {curr_dist}). Exploring unvisited neighbors.",
            extra_info={"visited_order": list(visited_order), "dist": dict(dist)}
        ))

        comparisons += 1
        if curr == end_id:
            found = True
            break

        neighbors = [entry[0] for entry in graph.adjacency.get(curr, [])]
        for neighbor in sorted(neighbors):
            if neighbor not in graph.routers or not graph.routers[neighbor].is_online:
                continue

            comparisons += 1
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                dist[neighbor] = curr_dist + 1
                queue.append(neighbor)

                steps.append(SimulationStep(
                    step_type="enqueue",
                    current_element=neighbor,
                    data_structure_state=list(queue),
                    visited_elements=list(visited_order),
                    active_path=[curr, neighbor],
                    message=f"Discovered '{neighbor}' at Hop {curr_dist + 1} via link ({curr} -> {neighbor}). Enqueued.",
                    extra_info={"visited_order": list(visited_order), "dist": dict(dist)}
                ))

    elapsed = (time.perf_counter() - start_time) * 1000.0

    if not found:
        return SimulationResult(
            algorithm_name="BFS Routing",
            success=False,
            visited_order=visited_order,
            total_steps=len(steps),
            total_comparisons=comparisons,
            execution_time_ms=elapsed,
            steps=steps,
            message=f"No route found between {start_id} and {end_id} (Network disconnected or offline).",
            extra_info={"traversal_order": list(visited_order), "dist": dist, "step_details": step_details}
        )

    path = []
    curr_back = end_id
    while curr_back is not None:
        path.append(curr_back)
        curr_back = parent.get(curr_back)
    path.reverse()

    steps.append(SimulationStep(
        step_type="complete",
        current_element=end_id,
        data_structure_state=[],
        visited_elements=visited_order,
        active_path=path,
        message=f"BFS discovered shortest-hop route: {' -> '.join(path)} ({len(path)-1} hops). Traversal Sequence: {' -> '.join(visited_order)}.",
        extra_info={"visited_order": list(visited_order), "dist": dict(dist)}
    ))

    return SimulationResult(
        algorithm_name="BFS Routing",
        success=True,
        path=path,
        visited_order=visited_order,
        total_steps=len(steps),
        total_comparisons=comparisons,
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Shortest path discovered: {' -> '.join(path)} ({len(path)-1} hops).",
        extra_info={"traversal_order": list(visited_order), "dist": dist, "step_details": step_details}
    )

def dfs_path(graph: Graph, start_id: str, end_id: str) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    start_id = start_id.strip().upper()
    end_id = end_id.strip().upper()

    if start_id not in graph.routers or end_id not in graph.routers:
        return SimulationResult(
            algorithm_name="DFS Routing",
            success=False,
            message="Invalid start or destination router."
        )

    if not graph.routers[start_id].is_online:
        return SimulationResult(
            algorithm_name="DFS Routing",
            success=False,
            message=f"Source router {start_id} is offline."
        )

    if not graph.routers[end_id].is_online:
        return SimulationResult(
            algorithm_name="DFS Routing",
            success=False,
            message=f"Destination router {end_id} is offline."
        )

    stack: List[Tuple[str, List[str]]] = [(start_id, [start_id])]
    visited: Set[str] = set()
    visited_order: List[str] = []
    depth_map: Dict[str, int] = {start_id: 0}
    step_details: List[Dict[str, Any]] = []

    steps.append(SimulationStep(
        step_type="push",
        current_element=start_id,
        data_structure_state=[s[0] for s in stack],
        visited_elements=[],
        message=f"Source router '{start_id}' pushed onto DFS LIFO Stack.",
        extra_info={"visited_order": [], "dist": dict(depth_map)}
    ))

    found = False
    final_path: List[str] = []
    comparisons = 0

    while stack:
        curr, path = stack.pop()

        if curr in visited:
            continue

        visited.add(curr)
        visited_order.append(curr)
        depth = len(path) - 1
        depth_map[curr] = depth

        step_details.append({
            "order": len(visited_order),
            "router": curr,
            "action": "Source Initialized" if curr == start_id else ("Target Reached" if curr == end_id else "Popped & Visited"),
            "level": depth,
            "role": "Source" if curr == start_id else ("Destination" if curr == end_id else "Router")
        })

        steps.append(SimulationStep(
            step_type="pop",
            current_element=curr,
            data_structure_state=[s[0] for s in stack],
            visited_elements=list(visited_order),
            active_path=list(path),
            message=f"Visited #{len(visited_order)}: Popped '{curr}' (Depth {depth}). Exploring deepest unvisited branch.",
            extra_info={"visited_order": list(visited_order), "dist": dict(depth_map)}
        ))

        comparisons += 1
        if curr == end_id:
            found = True
            final_path = path
            break

        neighbors = [entry[0] for entry in graph.adjacency.get(curr, [])]
        for neighbor in sorted(neighbors, reverse=True):
            if neighbor not in graph.routers or not graph.routers[neighbor].is_online:
                continue

            comparisons += 1
            if neighbor not in visited:
                depth_map[neighbor] = depth + 1
                stack.append((neighbor, path + [neighbor]))

                steps.append(SimulationStep(
                    step_type="push",
                    current_element=neighbor,
                    data_structure_state=[s[0] for s in stack],
                    visited_elements=list(visited_order),
                    active_path=[curr, neighbor],
                    message=f"Pushed unvisited neighbor '{neighbor}' onto DFS Stack.",
                    extra_info={"visited_order": list(visited_order), "dist": dict(depth_map)}
                ))

    elapsed = (time.perf_counter() - start_time) * 1000.0

    if not found:
        return SimulationResult(
            algorithm_name="DFS Routing",
            success=False,
            visited_order=visited_order,
            total_steps=len(steps),
            total_comparisons=comparisons,
            execution_time_ms=elapsed,
            steps=steps,
            message=f"No route found between {start_id} and {end_id} using DFS.",
            extra_info={"traversal_order": list(visited_order), "dist": depth_map, "step_details": step_details}
        )

    steps.append(SimulationStep(
        step_type="complete",
        current_element=end_id,
        data_structure_state=[],
        visited_elements=visited_order,
        active_path=final_path,
        message=f"DFS discovered valid path: {' -> '.join(final_path)} ({len(final_path)-1} hops). Traversal Sequence: {' -> '.join(visited_order)}.",
        extra_info={"visited_order": list(visited_order), "dist": dict(depth_map)}
    ))

    return SimulationResult(
        algorithm_name="DFS Routing",
        success=True,
        path=final_path,
        visited_order=visited_order,
        total_steps=len(steps),
        total_comparisons=comparisons,
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Path discovered: {' -> '.join(final_path)} ({len(final_path)-1} hops).",
        extra_info={"traversal_order": list(visited_order), "dist": depth_map, "step_details": step_details}
    )

def validate_router_id(router_id: str) -> Tuple[bool, str]:
    rid = router_id.strip().upper()
    if not rid:
        return False, "Router ID cannot be empty."
    if len(rid) > 8:
        return False, "Router ID cannot exceed 8 characters."
    if not rid.isalnum():
        return False, "Router ID must be alphanumeric (e.g. R1, GW2)."
    return True, rid
