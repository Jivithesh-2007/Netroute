import json
import time
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

    def __repr__(self) -> str:
        status = "Online" if self.is_online else "Offline"
        return f"Router({self.id}, '{self.name}', pos=({self.x}, {self.y}), status={status})"


class Graph:
    def __init__(self, directed: bool = False):
        self.directed = directed
        self.routers: Dict[str, Router] = {}
        self.adj_list: Dict[str, Dict[str, float]] = {}

    def add_router(self, router: Router) -> bool:
        if router.id in self.routers:
            return False
        self.routers[router.id] = router
        self.adj_list[router.id] = {}
        return True

    def remove_router(self, router_id: str) -> bool:
        if router_id not in self.routers:
            return False
        del self.routers[router_id]
        del self.adj_list[router_id]
        for u in self.adj_list:
            if router_id in self.adj_list[u]:
                del self.adj_list[u][router_id]
        return True

    def add_edge(self, u: str, v: str, weight: float = 1.0) -> bool:
        if u not in self.routers or v not in self.routers or u == v:
            return False
        self.adj_list[u][v] = weight
        if not self.directed:
            self.adj_list[v][u] = weight
        return True

    def remove_edge(self, u: str, v: str) -> bool:
        removed = False
        if u in self.adj_list and v in self.adj_list[u]:
            del self.adj_list[u][v]
            removed = True
        if not self.directed and v in self.adj_list and u in self.adj_list[v]:
            del self.adj_list[v][u]
            removed = True
        return removed

    def set_router_online_status(self, router_id: str, is_online: bool) -> bool:
        if router_id not in self.routers:
            return False
        self.routers[router_id].is_online = is_online
        return True

    def get_neighbors(self, router_id: str, include_offline: bool = False) -> List[str]:
        if router_id not in self.routers:
            return []
        neighbors = []
        for nbr in self.adj_list.get(router_id, {}):
            if include_offline or self.routers[nbr].is_online:
                neighbors.append(nbr)
        return neighbors

    def get_adjacency_list_view(self) -> Dict[str, List[str]]:
        result = {}
        for rid in sorted(self.routers.keys()):
            result[rid] = sorted(list(self.adj_list[rid].keys()))
        return result

    def get_adjacency_matrix_view(self) -> Tuple[List[str], List[List[int]]]:
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
        self.routers.clear()
        self.adj_list.clear()

    def is_reachable(self, start_id: str, end_id: str) -> bool:
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
        isolated = []
        for rid in sorted(self.routers.keys()):
            if len(self.adj_list.get(rid, {})) == 0:
                isolated.append(rid)
        return isolated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "directed": self.directed,
            "routers": [r.to_dict() for r in self.routers.values()],
            "edges": self.get_edges()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Graph':
        g = cls(directed=data.get("directed", False))
        for r_data in data.get("routers", []):
            g.add_router(Router.from_dict(r_data))
        for edge in data.get("edges", []):
            u, v = edge[0], edge[1]
            w = edge[2] if len(edge) > 2 else 1.0
            g.add_edge(u, v, w)
        return g

    def save_to_file(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Graph':
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def create_default_topology(cls) -> 'Graph':
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
        g = cls(directed=False)
        g.add_router(Router("R1", "LAN A Core", 110, 120))
        g.add_router(Router("R2", "LAN A Edge", 250, 100))
        g.add_router(Router("R3", "LAN A Host", 180, 240))
        g.add_edge("R1", "R2")
        g.add_edge("R1", "R3")
        g.add_edge("R2", "R3")

        g.add_router(Router("R4", "LAN B Core", 440, 120))
        g.add_router(Router("R5", "LAN B Edge", 580, 100))
        g.add_router(Router("R6", "LAN B Host", 510, 240))
        g.add_edge("R4", "R5")
        g.add_edge("R4", "R6")
        g.add_edge("R5", "R6")
        return g

    @classmethod
    def create_alternate_routes(cls) -> 'Graph':
        g = cls(directed=False)
        g.add_router(Router("R1", "Source R1", 100, 180))
        g.add_router(Router("R2", "Bridge R2", 280, 80))
        g.add_router(Router("R3", "Long A R3", 200, 280))
        g.add_router(Router("R4", "Long B R4", 320, 310))
        g.add_router(Router("R5", "Long C R5", 440, 280))
        g.add_router(Router("R6", "Dest R6", 520, 180))

        g.add_edge("R1", "R2")
        g.add_edge("R2", "R6")

        g.add_edge("R1", "R3")
        g.add_edge("R3", "R4")
        g.add_edge("R4", "R5")
        g.add_edge("R5", "R6")
        return g

    @classmethod
    def create_offline_scenario(cls) -> 'Graph':
        g = cls(directed=False)
        g.add_router(Router("R1", "Ingress R1", 100, 180))
        g.add_router(Router("R2", "Primary (Down)", 290, 100, is_online=False))
        g.add_router(Router("R3", "Backup R3", 290, 270))
        g.add_router(Router("R4", "Backup R4", 430, 270))
        g.add_router(Router("R5", "Egress R5", 550, 180))

        g.add_edge("R1", "R2")
        g.add_edge("R2", "R5")
        g.add_edge("R1", "R3")
        g.add_edge("R3", "R4")
        g.add_edge("R4", "R5")
        return g


def validate_router_id(router_id: str) -> Tuple[bool, str]:
    clean_id = router_id.strip()
    if not clean_id:
        return False, "Router ID cannot be empty."
    if len(clean_id) > 10:
        return False, "Router ID should be 10 characters or less."
    if not clean_id.isalnum():
        return False, "Router ID should be alphanumeric."
    return True, clean_id


def bfs_path(graph: Graph, start_id: str, end_id: str) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []

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
    visited_order: List[str] = []

    steps.append(SimulationStep(
        step_type="enqueue",
        current_element=start_id,
        data_structure_state=list(queue),
        visited_elements=list(visited),
        message=f"Source router '{start_id}' selected and enqueued into BFS Queue."
    ))

    found = False
    total_comparisons = 0

    while queue:
        curr = queue.popleft()
        visited_order.append(curr)

        steps.append(SimulationStep(
            step_type="pop",
            current_element=curr,
            data_structure_state=list(queue),
            visited_elements=list(visited),
            message=f"Dequeued router '{curr}' for exploration."
        ))

        if curr == end_id:
            found = True
            steps.append(SimulationStep(
                step_type="found",
                current_element=curr,
                data_structure_state=list(queue),
                visited_elements=list(visited),
                message=f"Destination router '{end_id}' reached!"
            ))
            break

        neighbors = graph.get_neighbors(curr, include_offline=False)
        for nbr in sorted(neighbors):
            total_comparisons += 1
            if nbr not in visited:
                visited.add(nbr)
                parent[nbr] = curr
                queue.append(nbr)
                steps.append(SimulationStep(
                    step_type="enqueue",
                    current_element=nbr,
                    data_structure_state=list(queue),
                    visited_elements=list(visited),
                    active_path=[curr, nbr],
                    message=f"Discovered online neighbor '{nbr}' from '{curr}'. Enqueued '{nbr}'."
                ))

    execution_time = (time.perf_counter() - start_time) * 1000

    if not found:
        return SimulationResult(
            algorithm_name="BFS Routing",
            success=False,
            visited_order=visited_order,
            total_steps=len(steps),
            total_comparisons=total_comparisons,
            execution_time_ms=execution_time,
            steps=steps,
            message=f"Destination router '{end_id}' is unreachable from '{start_id}'."
        )

    path = []
    curr: Optional[str] = end_id
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
    path.reverse()

    steps.append(SimulationStep(
        step_type="path_reconstruction",
        current_element=end_id,
        data_structure_state=[],
        visited_elements=list(visited),
        active_path=path,
        message=f"Reconstructed shortest route: {' -> '.join(path)} ({len(path)-1} hops)."
    ))

    return SimulationResult(
        algorithm_name="BFS Routing",
        success=True,
        path=path,
        visited_order=visited_order,
        total_steps=len(steps),
        total_comparisons=total_comparisons,
        execution_time_ms=execution_time,
        steps=steps,
        message=f"Route found from '{start_id}' to '{end_id}' in {len(path)-1} hops."
    )


def dfs_path(graph: Graph, start_id: str, end_id: str) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []

    if start_id not in graph.routers or end_id not in graph.routers:
        return SimulationResult(
            algorithm_name="DFS Routing",
            success=False,
            message="Invalid start or destination router."
        )

    if not graph.routers[start_id].is_online or not graph.routers[end_id].is_online:
        return SimulationResult(
            algorithm_name="DFS Routing",
            success=False,
            message="Source or destination router is offline."
        )

    stack: List[str] = [start_id]
    visited: Set[str] = set()
    parent: Dict[str, Optional[str]] = {start_id: None}
    visited_order: List[str] = []

    steps.append(SimulationStep(
        step_type="push",
        current_element=start_id,
        data_structure_state=list(stack),
        visited_elements=list(visited),
        message=f"Pushed source router '{start_id}' onto DFS Stack."
    ))

    found = False
    total_comparisons = 0

    while stack:
        curr = stack.pop()
        if curr in visited:
            continue

        visited.add(curr)
        visited_order.append(curr)

        steps.append(SimulationStep(
            step_type="pop",
            current_element=curr,
            data_structure_state=list(stack),
            visited_elements=list(visited),
            message=f"Popped router '{curr}' from stack. Marked as visited."
        ))

        if curr == end_id:
            found = True
            steps.append(SimulationStep(
                step_type="found",
                current_element=curr,
                data_structure_state=list(stack),
                visited_elements=list(visited),
                message=f"Destination router '{end_id}' reached via DFS!"
            ))
            break

        neighbors = graph.get_neighbors(curr, include_offline=False)
        for nbr in sorted(neighbors, reverse=True):
            total_comparisons += 1
            if nbr not in visited:
                if nbr not in parent:
                    parent[nbr] = curr
                stack.append(nbr)
                steps.append(SimulationStep(
                    step_type="push",
                    current_element=nbr,
                    data_structure_state=list(stack),
                    visited_elements=list(visited),
                    active_path=[curr, nbr],
                    message=f"Discovered online neighbor '{nbr}' from '{curr}'. Pushed '{nbr}' onto stack."
                ))

    execution_time = (time.perf_counter() - start_time) * 1000

    if not found:
        return SimulationResult(
            algorithm_name="DFS Routing",
            success=False,
            visited_order=visited_order,
            total_steps=len(steps),
            total_comparisons=total_comparisons,
            execution_time_ms=execution_time,
            steps=steps,
            message=f"Destination router '{end_id}' is unreachable via DFS from '{start_id}'."
        )

    path = []
    curr: Optional[str] = end_id
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
    path.reverse()

    steps.append(SimulationStep(
        step_type="path_reconstruction",
        current_element=end_id,
        data_structure_state=[],
        visited_elements=list(visited),
        active_path=path,
        message=f"DFS Route identified: {' -> '.join(path)} ({len(path)-1} hops)."
    ))

    return SimulationResult(
        algorithm_name="DFS Routing",
        success=True,
        path=path,
        visited_order=visited_order,
        total_steps=len(steps),
        total_comparisons=total_comparisons,
        execution_time_ms=execution_time,
        steps=steps,
        message=f"Valid path found from '{start_id}' to '{end_id}' via DFS ({len(path)-1} hops)."
    )


def grid_maze_bfs(grid: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> SimulationResult:
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    if grid[start[0]][start[1]] == 1 or grid[end[0]][end[1]] == 1:
        return SimulationResult(algorithm_name="Grid BFS", success=False, message="Start or end is blocked.")

    queue = deque([start])
    visited: Set[Tuple[int, int]] = {start}
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    visited_order = []

    while queue:
        curr = queue.popleft()
        visited_order.append(curr)
        if curr == end:
            break

        r, c = curr
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    parent[(nr, nc)] = curr
                    queue.append((nr, nc))

    if end not in parent:
        return SimulationResult(algorithm_name="Grid BFS", success=False, message="No path in grid maze.")

    path = []
    curr_cell: Optional[Tuple[int, int]] = end
    while curr_cell is not None:
        path.append(curr_cell)
        curr_cell = parent.get(curr_cell)
    path.reverse()

    return SimulationResult(
        algorithm_name="Grid BFS",
        success=True,
        path=path,
        visited_order=visited_order,
        total_steps=len(visited_order),
        message=f"Grid path found with length {len(path)-1}."
    )


def grid_maze_dfs(grid: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> SimulationResult:
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    if grid[start[0]][start[1]] == 1 or grid[end[0]][end[1]] == 1:
        return SimulationResult(algorithm_name="Grid DFS", success=False, message="Start or end is blocked.")

    stack = [start]
    visited: Set[Tuple[int, int]] = set()
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    visited_order = []

    while stack:
        curr = stack.pop()
        if curr in visited:
            continue
        visited.add(curr)
        visited_order.append(curr)

        if curr == end:
            break

        r, c = curr
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                if (nr, nc) not in visited:
                    parent[(nr, nc)] = curr
                    stack.append((nr, nc))

    if end not in parent:
        return SimulationResult(algorithm_name="Grid DFS", success=False, message="No path in grid maze.")

    path = []
    curr_cell: Optional[Tuple[int, int]] = end
    while curr_cell is not None:
        path.append(curr_cell)
        curr_cell = parent.get(curr_cell)
    path.reverse()

    return SimulationResult(
        algorithm_name="Grid DFS",
        success=True,
        path=path,
        visited_order=visited_order,
        total_steps=len(visited_order),
        message=f"Grid DFS path found with length {len(path)-1}."
    )
