"""
Graph traversal and network routing algorithms (BFS, DFS, Connectivity, Grid Maze).
"""
import time
from collections import deque
from typing import List, Dict, Set, Tuple, Optional
from models.graph import Graph
from models.simulation import SimulationStep, SimulationResult


def bfs_path(graph: Graph, start_id: str, end_id: str) -> SimulationResult:
    """
    Breadth-First Search routing algorithm.
    Finds the shortest path in terms of number of hops in an unweighted graph.
    """
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

    # Reconstruct shortest path
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
    """
    Depth-First Search routing algorithm using an explicit stack.
    Explores paths deeply before backtracking. Does not guarantee shortest path.
    """
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
        # Push in reverse sorted order so alphabetical order is popped first
        for nbr in sorted(neighbors, reverse=True):
            total_comparisons += 1
            if nbr not in visited:
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

    # Reconstruct path
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
    """
    2D Grid Maze Shortest Path using BFS.
    grid: 0 for open cell, 1 for wall block.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    steps: List[SimulationStep] = []

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
    """
    2D Grid Maze Exploration using DFS.
    """
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
