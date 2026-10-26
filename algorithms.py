import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from network import Graph


@dataclass
class SimulationStep:
    step_number: int
    step_type: str  # init, enqueue, dequeue, push, pop, backtrack, destination_found, complete, failure
    current_element: Optional[str] = None
    data_structure_state: List[str] = field(default_factory=list)
    last_op: str = ""
    visited_elements: List[str] = field(default_factory=list)
    parent_map: Dict[str, Optional[str]] = field(default_factory=dict)
    active_path: List[str] = field(default_factory=list)
    active_edge: Optional[Tuple[str, str]] = None
    message: str = ""
    extra_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    algorithm_name: str
    success: bool
    path: List[str] = field(default_factory=list)
    visited_order: List[str] = field(default_factory=list)
    explored_edges: List[Tuple[str, str]] = field(default_factory=list)
    tree_edges: List[Tuple[str, str]] = field(default_factory=list)
    parent_map: Dict[str, Optional[str]] = field(default_factory=dict)
    depth_or_level: Dict[str, int] = field(default_factory=dict)
    final_data_structure_state: List[str] = field(default_factory=list)
    total_pushes_or_enqueues: int = 0
    total_pops_or_dequeues: int = 0
    max_structure_size: int = 0
    backtracking_count: int = 0
    total_steps: int = 0
    execution_time_ms: float = 0.0
    steps: List[SimulationStep] = field(default_factory=list)
    message: str = ""


def bfs_path(graph: Graph, start_id: str, end_id: str) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    start_id = start_id.strip().upper()
    end_id = end_id.strip().upper()

    if not graph.routers:
        return SimulationResult(
            algorithm_name="BFS Shortest-Hop Routing",
            success=False,
            message="Graph is empty. Please add routers before running routing."
        )

    if start_id not in graph.routers or end_id not in graph.routers:
        return SimulationResult(
            algorithm_name="BFS Shortest-Hop Routing",
            success=False,
            message=f"Router '{start_id}' or '{end_id}' does not exist in graph."
        )

    if not graph.routers[start_id].is_online:
        return SimulationResult(
            algorithm_name="BFS Shortest-Hop Routing",
            success=False,
            message=f"Source router '{start_id}' is offline."
        )

    if not graph.routers[end_id].is_online:
        return SimulationResult(
            algorithm_name="BFS Shortest-Hop Routing",
            success=False,
            message=f"Destination router '{end_id}' is offline."
        )

    if start_id == end_id:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append(SimulationStep(
            step_number=1,
            step_type="complete",
            current_element=start_id,
            data_structure_state=[start_id],
            last_op=f"Direct match: {start_id}",
            visited_elements=[start_id],
            parent_map={start_id: None},
            active_path=[start_id],
            message=f"Source '{start_id}' equals destination. Direct match with 0 hops."
        ))
        return SimulationResult(
            algorithm_name="BFS Shortest-Hop Routing",
            success=True,
            path=[start_id],
            visited_order=[start_id],
            explored_edges=[],
            tree_edges=[],
            parent_map={start_id: None},
            depth_or_level={start_id: 0},
            final_data_structure_state=[start_id],
            total_pushes_or_enqueues=1,
            total_pops_or_dequeues=0,
            max_structure_size=1,
            total_steps=1,
            execution_time_ms=elapsed,
            steps=steps,
            message=f"Direct match: {start_id} (0 hops)."
        )

    queue = deque([start_id])
    visited: Set[str] = {start_id}
    parent: Dict[str, Optional[str]] = {start_id: None}
    dist: Dict[str, int] = {start_id: 0}
    visited_order: List[str] = []
    explored_edges: List[Tuple[str, str]] = []
    tree_edges: List[Tuple[str, str]] = []

    total_enqueues = 1
    total_dequeues = 0
    max_queue_size = 1

    steps.append(SimulationStep(
        step_number=len(steps) + 1,
        step_type="init",
        current_element=start_id,
        data_structure_state=list(queue),
        last_op=f"Enqueued {start_id} (Source)",
        visited_elements=list(visited_order),
        parent_map=dict(parent),
        active_path=[start_id],
        message=f"Queue initialized. Enqueued source router '{start_id}' at rear (Hop Level 0)."
    ))

    found = False

    while queue:
        curr = queue.popleft()
        total_dequeues += 1
        visited_order.append(curr)
        curr_dist = dist[curr]

        steps.append(SimulationStep(
            step_number=len(steps) + 1,
            step_type="dequeue",
            current_element=curr,
            data_structure_state=list(queue),
            last_op=f"Dequeued {curr} (Front)",
            visited_elements=list(visited_order),
            parent_map=dict(parent),
            active_path=[curr],
            message=f"Dequeued router '{curr}' from queue front (Hop level {curr_dist}). Exploring neighbors."
        ))

        if curr == end_id:
            found = True
            break

        neighbors = [entry[0] for entry in graph.adjacency.get(curr, [])]
        for neighbor in sorted(neighbors):
            edge = tuple(sorted((curr, neighbor)))
            if edge not in explored_edges:
                explored_edges.append(edge)

            if neighbor not in graph.routers or not graph.routers[neighbor].is_online:
                continue

            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                tree_edges.append((curr, neighbor))
                dist[neighbor] = curr_dist + 1
                queue.append(neighbor)
                total_enqueues += 1
                max_queue_size = max(max_queue_size, len(queue))

                steps.append(SimulationStep(
                    step_number=len(steps) + 1,
                    step_type="enqueue",
                    current_element=neighbor,
                    data_structure_state=list(queue),
                    last_op=f"Enqueued {neighbor}",
                    visited_elements=list(visited_order),
                    parent_map=dict(parent),
                    active_path=[curr, neighbor],
                    active_edge=edge,
                    message=f"Discovered unvisited neighbor '{neighbor}' via link ({curr} <-> {neighbor}) at Hop {curr_dist + 1}. Parent set to '{curr}'. Added to queue rear."
                ))

                if neighbor == end_id:
                    found = True
                    visited_order.append(neighbor)
                    steps.append(SimulationStep(
                        step_number=len(steps) + 1,
                        step_type="destination_found",
                        current_element=neighbor,
                        data_structure_state=list(queue),
                        last_op=f"Reached Destination {neighbor}",
                        visited_elements=list(visited_order),
                        parent_map=dict(parent),
                        active_path=[curr, neighbor],
                        active_edge=edge,
                        message=f"Destination router '{end_id}' reached! BFS guarantees shortest hop route."
                    ))
                    break

        if found:
            break

    elapsed = (time.perf_counter() - start_time) * 1000.0
    final_queue_state = list(queue)

    if not found:
        steps.append(SimulationStep(
            step_number=len(steps) + 1,
            step_type="failure",
            current_element=None,
            data_structure_state=final_queue_state,
            last_op="Queue Empty / Search Failed",
            visited_elements=list(visited_order),
            parent_map=dict(parent),
            message=f"BFS queue exhausted without reaching '{end_id}'. Routers are in disconnected components or path is blocked by offline routers."
        ))
        return SimulationResult(
            algorithm_name="BFS Shortest-Hop Routing",
            success=False,
            visited_order=visited_order,
            explored_edges=explored_edges,
            tree_edges=tree_edges,
            parent_map=parent,
            depth_or_level=dist,
            final_data_structure_state=final_queue_state,
            total_pushes_or_enqueues=total_enqueues,
            total_pops_or_dequeues=total_dequeues,
            max_structure_size=max_queue_size,
            total_steps=len(steps),
            execution_time_ms=elapsed,
            steps=steps,
            message=f"No route found between '{start_id}' and '{end_id}' (Disconnected network or offline barrier)."
        )

    path = []
    curr_back: Optional[str] = end_id
    while curr_back is not None:
        path.append(curr_back)
        curr_back = parent.get(curr_back)
    path.reverse()

    steps.append(SimulationStep(
        step_number=len(steps) + 1,
        step_type="complete",
        current_element=end_id,
        data_structure_state=final_queue_state,
        last_op=f"Route: {' -> '.join(path)}",
        visited_elements=list(visited_order),
        parent_map=dict(parent),
        active_path=path,
        message=f"Shortest route discovered: {' -> '.join(path)} ({len(path) - 1} hops). Reconstructed via parent pointers."
    ))

    return SimulationResult(
        algorithm_name="BFS Shortest-Hop Routing",
        success=True,
        path=path,
        visited_order=visited_order,
        explored_edges=explored_edges,
        tree_edges=tree_edges,
        parent_map=parent,
        depth_or_level=dist,
        final_data_structure_state=final_queue_state,
        total_pushes_or_enqueues=total_enqueues,
        total_pops_or_dequeues=total_dequeues,
        max_structure_size=max_queue_size,
        total_steps=len(steps),
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Shortest path discovered: {' -> '.join(path)} ({len(path) - 1} hops)."
    )


def dfs_path(graph: Graph, start_id: str, end_id: str) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    start_id = start_id.strip().upper()
    end_id = end_id.strip().upper()

    if not graph.routers:
        return SimulationResult(
            algorithm_name="DFS Path Discovery",
            success=False,
            message="Graph is empty. Please add routers before running routing."
        )

    if start_id not in graph.routers or end_id not in graph.routers:
        return SimulationResult(
            algorithm_name="DFS Path Discovery",
            success=False,
            message=f"Router '{start_id}' or '{end_id}' does not exist in graph."
        )

    if not graph.routers[start_id].is_online:
        return SimulationResult(
            algorithm_name="DFS Path Discovery",
            success=False,
            message=f"Source router '{start_id}' is offline."
        )

    if not graph.routers[end_id].is_online:
        return SimulationResult(
            algorithm_name="DFS Path Discovery",
            success=False,
            message=f"Destination router '{end_id}' is offline."
        )

    if start_id == end_id:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append(SimulationStep(
            step_number=1,
            step_type="complete",
            current_element=start_id,
            data_structure_state=[start_id],
            last_op=f"Direct match: {start_id}",
            visited_elements=[start_id],
            parent_map={start_id: None},
            active_path=[start_id],
            message=f"Source '{start_id}' equals destination. Direct match with 0 hops."
        ))
        return SimulationResult(
            algorithm_name="DFS Path Discovery",
            success=True,
            path=[start_id],
            visited_order=[start_id],
            explored_edges=[],
            tree_edges=[],
            parent_map={start_id: None},
            depth_or_level={start_id: 0},
            final_data_structure_state=[start_id],
            total_pushes_or_enqueues=1,
            total_pops_or_dequeues=0,
            max_structure_size=1,
            total_steps=1,
            execution_time_ms=elapsed,
            steps=steps,
            message=f"Direct match: {start_id} (0 hops)."
        )

    # Explicit LIFO stack storing (router_id, path_so_far)
    stack: List[Tuple[str, List[str]]] = [(start_id, [start_id])]
    visited: Set[str] = set()
    visited_order: List[str] = []
    explored_edges: List[Tuple[str, str]] = []
    tree_edges: List[Tuple[str, str]] = []
    parent: Dict[str, Optional[str]] = {start_id: None}
    depth_map: Dict[str, int] = {start_id: 0}

    total_pushes = 1
    total_pops = 0
    max_stack_size = 1
    backtracking_count = 0

    steps.append(SimulationStep(
        step_number=len(steps) + 1,
        step_type="init",
        current_element=start_id,
        data_structure_state=[item[0] for item in stack],
        last_op=f"Pushed {start_id} (Source)",
        visited_elements=[],
        parent_map=dict(parent),
        active_path=[start_id],
        message=f"Stack initialized. Pushed source router '{start_id}' onto DFS LIFO stack (Top)."
    ))

    found = False
    final_path: List[str] = []

    while stack:
        curr, path = stack.pop()
        total_pops += 1

        if curr in visited:
            continue

        visited.add(curr)
        visited_order.append(curr)
        depth = len(path) - 1
        depth_map[curr] = depth

        steps.append(SimulationStep(
            step_number=len(steps) + 1,
            step_type="pop",
            current_element=curr,
            data_structure_state=[item[0] for item in stack],
            last_op=f"Popped {curr} (Top)",
            visited_elements=list(visited_order),
            parent_map=dict(parent),
            active_path=list(path),
            message=f"Popped router '{curr}' from stack top (Depth {depth}). Exploring deepest unvisited branch."
        ))

        if curr == end_id:
            found = True
            final_path = path
            steps.append(SimulationStep(
                step_number=len(steps) + 1,
                step_type="destination_found",
                current_element=curr,
                data_structure_state=[item[0] for item in stack],
                last_op=f"Reached Destination {curr}",
                visited_elements=list(visited_order),
                parent_map=dict(parent),
                active_path=list(path),
                message=f"Destination router '{end_id}' reached via DFS! (Note: DFS finds a reachable path, not guaranteed shortest)."
            ))
            break

        neighbors = [entry[0] for entry in graph.adjacency.get(curr, [])]
        # Sort in reverse so that alphabetically smaller neighbors are pushed last and popped FIRST
        pushed_any = False
        for neighbor in sorted(neighbors, reverse=True):
            edge = tuple(sorted((curr, neighbor)))
            if edge not in explored_edges:
                explored_edges.append(edge)

            if neighbor not in graph.routers or not graph.routers[neighbor].is_online:
                continue

            if neighbor not in visited:
                parent[neighbor] = curr
                tree_edges.append((curr, neighbor))
                depth_map[neighbor] = depth + 1
                stack.append((neighbor, path + [neighbor]))
                total_pushes += 1
                max_stack_size = max(max_stack_size, len(stack))
                pushed_any = True

                steps.append(SimulationStep(
                    step_number=len(steps) + 1,
                    step_type="push",
                    current_element=neighbor,
                    data_structure_state=[item[0] for item in stack],
                    last_op=f"Pushed {neighbor}",
                    visited_elements=list(visited_order),
                    parent_map=dict(parent),
                    active_path=[curr, neighbor],
                    active_edge=edge,
                    message=f"Pushed unvisited neighbor '{neighbor}' onto DFS Stack (Depth {depth + 1}) via link ({curr} <-> {neighbor})."
                ))

        if not pushed_any and stack:
            backtracking_count += 1
            next_top = stack[-1][0]
            steps.append(SimulationStep(
                step_number=len(steps) + 1,
                step_type="backtrack",
                current_element=curr,
                data_structure_state=[item[0] for item in stack],
                last_op=f"Backtrack from {curr}",
                visited_elements=list(visited_order),
                parent_map=dict(parent),
                active_path=list(path),
                message=f"No unvisited neighbors from '{curr}'. Backtracking to next candidate on stack top: '{next_top}'."
            ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    final_stack_state = [item[0] for item in stack]

    if not found:
        steps.append(SimulationStep(
            step_number=len(steps) + 1,
            step_type="failure",
            current_element=None,
            data_structure_state=final_stack_state,
            last_op="Stack Empty / Search Failed",
            visited_elements=list(visited_order),
            parent_map=dict(parent),
            message=f"DFS stack exhausted without reaching '{end_id}'. Routers are disconnected or partitioned by offline nodes."
        ))
        return SimulationResult(
            algorithm_name="DFS Path Discovery",
            success=False,
            visited_order=visited_order,
            explored_edges=explored_edges,
            tree_edges=tree_edges,
            parent_map=parent,
            depth_or_level=depth_map,
            final_data_structure_state=final_stack_state,
            total_pushes_or_enqueues=total_pushes,
            total_pops_or_dequeues=total_pops,
            max_structure_size=max_stack_size,
            backtracking_count=backtracking_count,
            total_steps=len(steps),
            execution_time_ms=elapsed,
            steps=steps,
            message=f"No route found between '{start_id}' and '{end_id}' using DFS."
        )

    steps.append(SimulationStep(
        step_number=len(steps) + 1,
        step_type="complete",
        current_element=end_id,
        data_structure_state=final_stack_state,
        last_op=f"Route: {' -> '.join(final_path)}",
        visited_elements=list(visited_order),
        parent_map=dict(parent),
        active_path=final_path,
        message=f"DFS discovered valid path: {' -> '.join(final_path)} ({len(final_path) - 1} hops). Traversed deep branches using LIFO stack."
    ))

    return SimulationResult(
        algorithm_name="DFS Path Discovery",
        success=True,
        path=final_path,
        visited_order=visited_order,
        explored_edges=explored_edges,
        tree_edges=tree_edges,
        parent_map=parent,
        depth_or_level=depth_map,
        final_data_structure_state=final_stack_state,
        total_pushes_or_enqueues=total_pushes,
        total_pops_or_dequeues=total_pops,
        max_structure_size=max_stack_size,
        backtracking_count=backtracking_count,
        total_steps=len(steps),
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Path discovered: {' -> '.join(final_path)} ({len(final_path) - 1} hops)."
    )
