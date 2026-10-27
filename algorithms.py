"""
algorithms.py — Genuine BFS and DFS Graph Routing Algorithms.

Demonstrates:
- CO1: Stack and Queue Data Structures (FIFO Queue vs. LIFO Stack).
- CO5: Graph Traversal, Traversal Trees, and Shortest-Hop Routing.

Both algorithms record step-by-step internal states for the interactive visualizer.
"""

import time
import heapq
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Any
from network import Graph


def reconstruct_route_from_parents(parents: Dict[str, Optional[str]], dst: str) -> List[str]:
    """
    Reconstructs the discovered route from destination back to source
    using parent pointers recorded during traversal in O(L) time,
    where L is the number of hops in the route.
    """
    if dst not in parents:
        return []
    path: List[str] = []
    curr: Optional[str] = dst
    while curr is not None:
        path.append(curr)
        curr = parents.get(curr)
    path.reverse()
    return path


def bfs(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    """
    Breadth-First Search routing using a genuine FIFO queue (collections.deque).
    Guarantees the shortest-hop route in an unweighted graph because it explores
    all routers at distance k before exploring routers at distance k + 1.
    """
    start_time = time.perf_counter()
    src, dst = src.strip().upper(), dst.strip().upper()

    # Pre-condition validations
    if not graph.routers:
        return {
            "algorithm": "BFS (FIFO Queue)",
            "success": False,
            "message": "Network graph is empty. Please add routers or load a preset.",
            "steps": [],
            "path": [],
            "hops": 0,
            "visited": [],
            "parents": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "total_enqueues": 0,
            "total_dequeues": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    if src not in graph.routers or dst not in graph.routers:
        return {
            "algorithm": "BFS (FIFO Queue)",
            "success": False,
            "message": f"Endpoint router '{src}' or '{dst}' does not exist in the network.",
            "steps": [],
            "path": [],
            "hops": 0,
            "visited": [],
            "parents": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "total_enqueues": 0,
            "total_dequeues": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    if not graph.routers[src].is_online:
        return {
            "algorithm": "BFS (FIFO Queue)",
            "success": False,
            "message": f"Source router '{src}' is OFFLINE. Cannot transmit packets from offline hardware.",
            "steps": [],
            "path": [],
            "hops": 0,
            "visited": [],
            "parents": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "total_enqueues": 0,
            "total_dequeues": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    if not graph.routers[dst].is_online:
        return {
            "algorithm": "BFS (FIFO Queue)",
            "success": False,
            "message": f"Destination router '{dst}' is OFFLINE. Packets cannot be delivered.",
            "steps": [],
            "path": [],
            "hops": 0,
            "visited": [],
            "parents": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "total_enqueues": 0,
            "total_dequeues": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    steps: List[Dict[str, Any]] = []

    # Handle trivial case: Source == Destination
    if src == dst:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append({
            "step": 1,
            "operation": "COMPLETE",
            "current_node": src,
            "structure": [src],
            "front": src,
            "rear": src,
            "action_target": src,
            "enqueues": 1,
            "dequeues": 0,
            "max_structure": 1,
            "visited": [src],
            "parents": {src: None},
            "active_edge": None,
            "description": f"Source router '{src}' is identical to destination. Direct match with 0 hops."
        })
        return {
            "algorithm": "BFS (FIFO Queue)",
            "success": True,
            "path": [src],
            "hops": 0,
            "steps": steps,
            "visited": [src],
            "parents": {src: None},
            "tree_edges": [],
            "max_structure": 1,
            "total_pushes": 1,
            "total_pops": 0,
            "total_enqueues": 1,
            "total_dequeues": 0,
            "explored_edges_count": 0,
            "execution_time_ms": elapsed,
            "message": f"Direct route to '{src}' (0 hops)."
        }

    queue = deque([src])
    visited: Set[str] = {src}
    parents: Dict[str, Optional[str]] = {src: None}
    visited_order: List[str] = []
    tree_edges: List[Tuple[str, str]] = []
    explored_edges_set: Set[Tuple[str, str]] = set()

    total_enqueues = 1
    total_dequeues = 0
    max_queue_size = 1

    steps.append({
        "step": len(steps) + 1,
        "operation": "ENQUEUE",
        "current_node": src,
        "structure": list(queue),
        "front": queue[0] if queue else None,
        "rear": queue[-1] if queue else None,
        "action_target": src,
        "enqueues": total_enqueues,
        "dequeues": total_dequeues,
        "max_structure": max_queue_size,
        "visited": [],
        "parents": dict(parents),
        "active_edge": None,
        "description": f"Initialized FIFO queue. Enqueued source router '{src}' at rear (Distance Level 0)."
    })

    found = False
    while queue:
        curr = queue.popleft()
        total_dequeues += 1
        visited_order.append(curr)

        steps.append({
            "step": len(steps) + 1,
            "operation": "DEQUEUE",
            "current_node": curr,
            "structure": list(queue),
            "front": queue[0] if queue else None,
            "rear": queue[-1] if queue else None,
            "action_target": curr,
            "enqueues": total_enqueues,
            "dequeues": total_dequeues,
            "max_structure": max_queue_size,
            "visited": list(visited_order),
            "parents": dict(parents),
            "active_edge": None,
            "description": f"Dequeued router '{curr}' from queue front. Examining its adjacent transmission links."
        })

        if curr == dst:
            found = True
            break

        # Explore neighbors in sorted alphabetical order for deterministic behavior
        for nbr in sorted(graph.adjacency.get(curr, [])):
            if nbr not in graph.routers or not graph.routers[nbr].is_online:
                continue
            if hasattr(graph, "is_edge_active") and not graph.is_edge_active(curr, nbr):
                continue

            edge_pair = tuple(sorted((curr, nbr)))
            explored_edges_set.add(edge_pair)

            if nbr not in visited:
                visited.add(nbr)
                parents[nbr] = curr
                tree_edges.append((curr, nbr))
                queue.append(nbr)
                total_enqueues += 1
                max_queue_size = max(max_queue_size, len(queue))

                steps.append({
                    "step": len(steps) + 1,
                    "operation": "ENQUEUE",
                    "current_node": nbr,
                    "structure": list(queue),
                    "front": queue[0] if queue else None,
                    "rear": queue[-1] if queue else None,
                    "action_target": nbr,
                    "enqueues": total_enqueues,
                    "dequeues": total_dequeues,
                    "max_structure": max_queue_size,
                    "visited": list(visited_order),
                    "parents": dict(parents),
                    "active_edge": (curr, nbr),
                    "description": f"Discovered unvisited neighbor '{nbr}' via link ({curr} <-> {nbr}). Enqueued at rear; set parent[{nbr}] = '{curr}'."
                })

                if nbr == dst:
                    found = True
                    visited_order.append(nbr)
                    steps.append({
                        "step": len(steps) + 1,
                        "operation": "DESTINATION_FOUND",
                        "current_node": nbr,
                        "structure": list(queue),
                        "front": queue[0] if queue else None,
                        "rear": queue[-1] if queue else None,
                        "action_target": nbr,
                        "enqueues": total_enqueues,
                        "dequeues": total_dequeues,
                        "max_structure": max_queue_size,
                        "visited": list(visited_order),
                        "parents": dict(parents),
                        "active_edge": (curr, nbr),
                        "description": f"Destination router '{dst}' discovered! BFS guarantees minimum-hop route in unweighted graphs."
                    })
                    break

        if found:
            break

    elapsed = (time.perf_counter() - start_time) * 1000.0

    if not found:
        steps.append({
            "step": len(steps) + 1,
            "operation": "FAILED",
            "current_node": None,
            "structure": list(queue),
            "front": None,
            "rear": None,
            "action_target": None,
            "enqueues": total_enqueues,
            "dequeues": total_dequeues,
            "max_structure": max_queue_size,
            "visited": list(visited_order),
            "parents": dict(parents),
            "active_edge": None,
            "description": f"Queue exhausted. Destination '{dst}' is unreachable from '{src}' (network disconnected or blocked by offline routers)."
        })
        return {
            "algorithm": "BFS (FIFO Queue)",
            "success": False,
            "path": [],
            "hops": 0,
            "steps": steps,
            "visited": visited_order,
            "parents": parents,
            "tree_edges": tree_edges,
            "max_structure": max_queue_size,
            "total_pushes": total_enqueues,
            "total_pops": total_dequeues,
            "total_enqueues": total_enqueues,
            "total_dequeues": total_dequeues,
            "explored_edges_count": len(explored_edges_set),
            "execution_time_ms": elapsed,
            "message": f"No route found between '{src}' and '{dst}'."
        }

    # Reconstruct shortest path using parent pointers
    path = reconstruct_route_from_parents(parents, dst)
    path_cost = sum(graph.get_weight(path[i], path[i+1]) for i in range(len(path) - 1)) if len(path) > 1 else 0.0

    steps.append({
        "step": len(steps) + 1,
        "operation": "COMPLETE",
        "current_node": dst,
        "structure": list(queue),
        "front": queue[0] if queue else None,
        "rear": queue[-1] if queue else None,
        "action_target": dst,
        "enqueues": total_enqueues,
        "dequeues": total_dequeues,
        "max_structure": max_queue_size,
        "visited": list(visited_order),
        "parents": dict(parents),
        "active_edge": None,
        "description": f"BFS shortest route reconstructed via parent pointers: {' -> '.join(path)} ({len(path) - 1} hops, cost: {int(path_cost) if path_cost.is_integer() else path_cost})."
    })

    return {
        "algorithm": "BFS (FIFO Queue)",
        "success": True,
        "path": path,
        "hops": len(path) - 1,
        "path_cost": path_cost,
        "steps": steps,
        "visited": visited_order,
        "parents": parents,
        "tree_edges": tree_edges,
        "max_structure": max_queue_size,
        "total_pushes": total_enqueues,
        "total_pops": total_dequeues,
        "total_enqueues": total_enqueues,
        "total_dequeues": total_dequeues,
        "explored_edges_count": len(explored_edges_set),
        "execution_time_ms": elapsed,
        "message": f"Shortest route discovered: {' -> '.join(path)} ({len(path) - 1} hops)."
    }


def dfs(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    """
    Depth-First Search routing using an explicit LIFO stack (list).
    Explores a single branch as deeply as possible before backtracking.
    Important: DFS discovers a valid reachable path, but does NOT guarantee minimum hops.
    """
    start_time = time.perf_counter()
    src, dst = src.strip().upper(), dst.strip().upper()

    # Pre-condition validations
    if not graph.routers:
        return {
            "algorithm": "DFS (LIFO Stack)",
            "success": False,
            "message": "Network graph is empty. Please add routers or load a preset.",
            "steps": [],
            "path": [],
            "hops": 0,
            "visited": [],
            "parents": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "backtrack_count": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    if src not in graph.routers or dst not in graph.routers:
        return {
            "algorithm": "DFS (LIFO Stack)",
            "success": False,
            "message": f"Endpoint router '{src}' or '{dst}' does not exist in the network.",
            "steps": [],
            "path": [],
            "hops": 0,
            "visited": [],
            "parents": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "backtrack_count": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    if not graph.routers[src].is_online:
        return {
            "algorithm": "DFS (LIFO Stack)",
            "success": False,
            "message": f"Source router '{src}' is OFFLINE. Cannot initiate transmission.",
            "steps": [],
            "path": [],
            "hops": 0,
            "visited": [],
            "parents": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "backtrack_count": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    if not graph.routers[dst].is_online:
        return {
            "algorithm": "DFS (LIFO Stack)",
            "success": False,
            "message": f"Destination router '{dst}' is OFFLINE. Packets cannot be delivered.",
            "steps": [],
            "path": [],
            "hops": 0,
            "visited": [],
            "parents": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "backtrack_count": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    steps: List[Dict[str, Any]] = []

    # Handle trivial case: Source == Destination
    if src == dst:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append({
            "step": 1,
            "operation": "COMPLETE",
            "current_node": src,
            "structure": [src],
            "top": src,
            "bottom": src,
            "action_target": src,
            "pushes": 1,
            "pops": 0,
            "max_structure": 1,
            "is_backtrack": False,
            "visited": [src],
            "parents": {src: None},
            "active_edge": None,
            "description": f"Source router '{src}' is identical to destination. Direct match with 0 hops."
        })
        return {
            "algorithm": "DFS (LIFO Stack)",
            "success": True,
            "path": [src],
            "hops": 0,
            "steps": steps,
            "visited": [src],
            "parents": {src: None},
            "tree_edges": [],
            "max_structure": 1,
            "total_pushes": 1,
            "total_pops": 0,
            "backtrack_count": 0,
            "explored_edges_count": 0,
            "execution_time_ms": elapsed,
            "message": f"Direct route to '{src}' (0 hops)."
        }

    # Explicit LIFO stack storing (router_id, current_path)
    stack: List[Tuple[str, List[str]]] = [(src, [src])]
    visited: Set[str] = set()
    visited_order: List[str] = []
    parents: Dict[str, Optional[str]] = {src: None}
    tree_edges: List[Tuple[str, str]] = []
    explored_edges_set: Set[Tuple[str, str]] = set()

    total_pushes = 1
    total_pops = 0
    backtrack_count = 0
    max_stack_size = 1

    steps.append({
        "step": len(steps) + 1,
        "operation": "PUSH",
        "current_node": src,
        "structure": [item[0] for item in stack],
        "top": stack[-1][0] if stack else None,
        "bottom": stack[0][0] if stack else None,
        "action_target": src,
        "pushes": total_pushes,
        "pops": total_pops,
        "max_structure": max_stack_size,
        "is_backtrack": False,
        "visited": [],
        "parents": dict(parents),
        "active_edge": None,
        "description": f"Initialized LIFO stack. Pushed source router '{src}' onto stack top."
    })

    found_path: Optional[List[str]] = None

    while stack:
        curr, path = stack.pop()
        total_pops += 1

        if curr in visited:
            continue
        visited.add(curr)
        visited_order.append(curr)

        steps.append({
            "step": len(steps) + 1,
            "operation": "POP",
            "current_node": curr,
            "structure": [item[0] for item in stack],
            "top": stack[-1][0] if stack else None,
            "bottom": stack[0][0] if stack else None,
            "action_target": curr,
            "pushes": total_pushes,
            "pops": total_pops,
            "max_structure": max_stack_size,
            "is_backtrack": False,
            "visited": list(visited_order),
            "parents": dict(parents),
            "active_edge": None,
            "description": f"Popped router '{curr}' from stack top (Depth {len(path) - 1}). Exploring its deepest branch."
        })

        if curr == dst:
            found_path = path
            steps.append({
                "step": len(steps) + 1,
                "operation": "DESTINATION_FOUND",
                "current_node": curr,
                "structure": [item[0] for item in stack],
                "top": stack[-1][0] if stack else None,
                "bottom": stack[0][0] if stack else None,
                "action_target": curr,
                "pushes": total_pushes,
                "pops": total_pops,
                "max_structure": max_stack_size,
                "is_backtrack": False,
                "visited": list(visited_order),
                "parents": dict(parents),
                "active_edge": None,
                "description": f"Destination router '{dst}' reached via DFS path! (Note: DFS does not guarantee minimum hops)."
            })
            break

        # Push unvisited neighbors in reverse alphabetical order so that
        # the alphabetically first neighbor lands at the top of the stack and is popped next.
        valid_nbrs = [
            n for n in sorted(graph.adjacency.get(curr, []), reverse=True)
            if n in graph.routers and graph.routers[n].is_online and n not in visited and (not hasattr(graph, "is_edge_active") or graph.is_edge_active(curr, n))
        ]

        if valid_nbrs:
            for nbr in valid_nbrs:
                edge_pair = tuple(sorted((curr, nbr)))
                explored_edges_set.add(edge_pair)
                parents[nbr] = curr
                tree_edges.append((curr, nbr))
                stack.append((nbr, path + [nbr]))
                total_pushes += 1
                max_stack_size = max(max_stack_size, len(stack))

                steps.append({
                    "step": len(steps) + 1,
                    "operation": "PUSH",
                    "current_node": nbr,
                    "structure": [item[0] for item in stack],
                    "top": stack[-1][0] if stack else None,
                    "bottom": stack[0][0] if stack else None,
                    "action_target": nbr,
                    "pushes": total_pushes,
                    "pops": total_pops,
                    "max_structure": max_stack_size,
                    "is_backtrack": False,
                    "visited": list(visited_order),
                    "parents": dict(parents),
                    "active_edge": (curr, nbr),
                    "description": f"Pushed unvisited neighbor '{nbr}' onto DFS stack top via link ({curr} <-> {nbr})."
                })
        elif stack:
            backtrack_count += 1
            next_top = stack[-1][0]
            steps.append({
                "step": len(steps) + 1,
                "operation": "BACKTRACK",
                "current_node": curr,
                "structure": [item[0] for item in stack],
                "top": stack[-1][0] if stack else None,
                "bottom": stack[0][0] if stack else None,
                "action_target": curr,
                "pushes": total_pushes,
                "pops": total_pops,
                "max_structure": max_stack_size,
                "is_backtrack": True,
                "visited": list(visited_order),
                "parents": dict(parents),
                "active_edge": None,
                "description": f"Dead end reached at '{curr}'. Backtracking to previous candidate on stack: '{next_top}'."
            })

    elapsed = (time.perf_counter() - start_time) * 1000.0

    if not found_path:
        steps.append({
            "step": len(steps) + 1,
            "operation": "FAILED",
            "current_node": None,
            "structure": [item[0] for item in stack],
            "top": None,
            "bottom": None,
            "action_target": None,
            "pushes": total_pushes,
            "pops": total_pops,
            "max_structure": max_stack_size,
            "is_backtrack": False,
            "visited": list(visited_order),
            "parents": dict(parents),
            "active_edge": None,
            "description": f"Stack exhausted. Destination '{dst}' is unreachable from '{src}' via DFS."
        })
        return {
            "algorithm": "DFS (LIFO Stack)",
            "success": False,
            "path": [],
            "hops": 0,
            "steps": steps,
            "visited": visited_order,
            "parents": parents,
            "tree_edges": tree_edges,
            "max_structure": max_stack_size,
            "total_pushes": total_pushes,
            "total_pops": total_pops,
            "backtrack_count": backtrack_count,
            "explored_edges_count": len(explored_edges_set),
            "execution_time_ms": elapsed,
            "message": f"No route found between '{src}' and '{dst}'."
        }

    path_cost = sum(graph.get_weight(found_path[i], found_path[i+1]) for i in range(len(found_path) - 1)) if len(found_path) > 1 else 0.0

    steps.append({
        "step": len(steps) + 1,
        "operation": "COMPLETE",
        "current_node": dst,
        "structure": [item[0] for item in stack],
        "top": stack[-1][0] if stack else None,
        "bottom": stack[0][0] if stack else None,
        "action_target": dst,
        "pushes": total_pushes,
        "pops": total_pops,
        "max_structure": max_stack_size,
        "is_backtrack": False,
        "visited": list(visited_order),
        "parents": dict(parents),
        "active_edge": None,
        "description": f"DFS route discovered: {' -> '.join(found_path)} ({len(found_path) - 1} hops, cost: {int(path_cost) if path_cost.is_integer() else path_cost})."
    })

    return {
        "algorithm": "DFS (LIFO Stack)",
        "success": True,
        "path": found_path,
        "hops": len(found_path) - 1,
        "path_cost": path_cost,
        "steps": steps,
        "visited": visited_order,
        "parents": parents,
        "tree_edges": tree_edges,
        "max_structure": max_stack_size,
        "total_pushes": total_pushes,
        "total_pops": total_pops,
        "backtrack_count": backtrack_count,
        "explored_edges_count": len(explored_edges_set),
        "execution_time_ms": elapsed,
        "message": f"Valid route discovered: {' -> '.join(found_path)} ({len(found_path) - 1} hops)."
    }


def dijkstra(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    """
    Dijkstra's Shortest Path Algorithm using a Min-Heap Priority Queue (heapq).
    Guarantees the minimum-total-cost route in a weighted graph with non-negative edge weights (w >= 0).
    Unlike BFS (which optimizes hop count), Dijkstra minimizes cumulative link transmission costs.
    """
    start_time = time.perf_counter()
    src, dst = src.strip().upper(), dst.strip().upper()

    # Pre-condition validation 1: Empty graph
    if not graph.routers:
        return {
            "algorithm": "Dijkstra (Priority Queue)",
            "success": False,
            "message": "Network graph is empty. Please add routers or load a preset.",
            "steps": [],
            "path": [],
            "hops": 0,
            "path_cost": 0.0,
            "visited": [],
            "parents": {},
            "distances": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "total_relaxations": 0,
            "total_heap_pushes": 0,
            "total_heap_pops": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    # Pre-condition validation 2: Router existence
    if src not in graph.routers or dst not in graph.routers:
        return {
            "algorithm": "Dijkstra (Priority Queue)",
            "success": False,
            "message": f"Endpoint router '{src}' or '{dst}' does not exist in the network.",
            "steps": [],
            "path": [],
            "hops": 0,
            "path_cost": 0.0,
            "visited": [],
            "parents": {},
            "distances": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "total_relaxations": 0,
            "total_heap_pushes": 0,
            "total_heap_pops": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    # Pre-condition validation 3: Hardware online status
    if not graph.routers[src].is_online:
        return {
            "algorithm": "Dijkstra (Priority Queue)",
            "success": False,
            "message": f"Source router '{src}' is OFFLINE. Cannot originate packets from offline hardware.",
            "steps": [],
            "path": [],
            "hops": 0,
            "path_cost": 0.0,
            "visited": [],
            "parents": {},
            "distances": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "total_relaxations": 0,
            "total_heap_pushes": 0,
            "total_heap_pops": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    if not graph.routers[dst].is_online:
        return {
            "algorithm": "Dijkstra (Priority Queue)",
            "success": False,
            "message": f"Destination router '{dst}' is OFFLINE. Packet delivery impossible.",
            "steps": [],
            "path": [],
            "hops": 0,
            "path_cost": 0.0,
            "visited": [],
            "parents": {},
            "distances": {},
            "tree_edges": [],
            "max_structure": 0,
            "total_pushes": 0,
            "total_pops": 0,
            "total_relaxations": 0,
            "total_heap_pushes": 0,
            "total_heap_pops": 0,
            "explored_edges_count": 0,
            "execution_time_ms": 0.0
        }

    # Pre-condition validation 4: Non-negative weight constraint
    for (u, v), w in graph.weights.items():
        if w < 0:
            return {
                "algorithm": "Dijkstra (Priority Queue)",
                "success": False,
                "message": f"Dijkstra requires all edge weights to be non-negative (>= 0). Found invalid weight {w} on link ({u} <-> {v}).",
                "steps": [],
                "path": [],
                "hops": 0,
                "path_cost": 0.0,
                "visited": [],
                "parents": {},
                "distances": {},
                "tree_edges": [],
                "max_structure": 0,
                "total_pushes": 0,
                "total_pops": 0,
                "total_relaxations": 0,
                "total_heap_pushes": 0,
                "total_heap_pops": 0,
                "explored_edges_count": 0,
                "execution_time_ms": 0.0
            }

    steps: List[Dict[str, Any]] = []

    # Handle trivial case: Source == Destination
    if src == dst:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append({
            "step": 1,
            "operation": "COMPLETE",
            "current_node": src,
            "current_cost": 0.0,
            "structure": [f"{src} (cost: 0)"],
            "priority_queue": [(0.0, src)],
            "tentative_distances": {src: 0.0},
            "visited": [src],
            "parents": {src: None},
            "active_edge": None,
            "action_target": src,
            "relaxations": 0,
            "heap_pushes": 1,
            "heap_pops": 0,
            "max_structure": 1,
            "description": f"Source router '{src}' is identical to destination. Minimum cost is 0 (0 hops)."
        })
        return {
            "algorithm": "Dijkstra (Priority Queue)",
            "success": True,
            "path": [src],
            "hops": 0,
            "path_cost": 0.0,
            "steps": steps,
            "visited": [src],
            "parents": {src: None},
            "distances": {src: 0.0},
            "tree_edges": [],
            "max_structure": 1,
            "total_pushes": 1,
            "total_pops": 0,
            "total_relaxations": 0,
            "total_heap_pushes": 1,
            "total_heap_pops": 0,
            "explored_edges_count": 0,
            "execution_time_ms": elapsed,
            "message": f"Direct route to '{src}' (0 hops, cost: 0)."
        }

    # Data structure initializations
    distances: Dict[str, float] = {r: float("inf") for r in graph.routers}
    distances[src] = 0.0
    parents: Dict[str, Optional[str]] = {src: None}
    visited_settled: List[str] = []
    tree_edges: List[Tuple[str, str]] = []
    explored_edges_set: Set[Tuple[str, str]] = set()

    # Min-Heap stores (cost, router_id)
    pq: List[Tuple[float, str]] = [(0.0, src)]
    total_relaxations = 0
    total_heap_pushes = 1
    total_heap_pops = 0
    max_pq_size = 1

    def format_pq_items(heap_list: List[Tuple[float, str]]) -> List[str]:
        return [f"{node} (cost: {int(c) if c.is_integer() else c})" for c, node in sorted(heap_list)]

    def get_tentative_snapshot() -> Dict[str, Any]:
        return {r: (int(distances[r]) if distances[r].is_integer() else distances[r]) if distances[r] != float("inf") else "inf" for r in sorted(graph.routers.keys())}

    # Step 1: Priority Queue Initialization
    steps.append({
        "step": len(steps) + 1,
        "operation": "INIT",
        "current_node": src,
        "current_cost": 0.0,
        "structure": format_pq_items(pq),
        "priority_queue": sorted(list(pq)),
        "tentative_distances": get_tentative_snapshot(),
        "visited": [],
        "parents": dict(parents),
        "active_edge": None,
        "action_target": src,
        "relaxations": total_relaxations,
        "heap_pushes": total_heap_pushes,
        "heap_pops": total_heap_pops,
        "max_structure": max_pq_size,
        "description": f"Initialized Dijkstra Min-Heap Priority Queue with source '{src}' at cumulative cost 0.0."
    })

    found = False
    while pq:
        cost, curr = heapq.heappop(pq)
        total_heap_pops += 1

        # Skip stale heap entries if a shorter path to curr was already settled
        if cost > distances[curr]:
            steps.append({
                "step": len(steps) + 1,
                "operation": "SKIP_OUTDATED",
                "current_node": curr,
                "current_cost": cost,
                "structure": format_pq_items(pq),
                "priority_queue": sorted(list(pq)),
                "tentative_distances": get_tentative_snapshot(),
                "visited": list(visited_settled),
                "parents": dict(parents),
                "active_edge": None,
                "action_target": curr,
                "relaxations": total_relaxations,
                "heap_pushes": total_heap_pushes,
                "heap_pops": total_heap_pops,
                "max_structure": max_pq_size,
                "description": f"Skipped outdated heap entry for '{curr}' with cost {cost} (shorter distance {distances[curr]} already finalized)."
            })
            continue

        if curr not in visited_settled:
            visited_settled.append(curr)

        steps.append({
            "step": len(steps) + 1,
            "operation": "EXTRACT_MIN",
            "current_node": curr,
            "current_cost": cost,
            "structure": format_pq_items(pq),
            "priority_queue": sorted(list(pq)),
            "tentative_distances": get_tentative_snapshot(),
            "visited": list(visited_settled),
            "parents": dict(parents),
            "active_edge": None,
            "action_target": curr,
            "relaxations": total_relaxations,
            "heap_pushes": total_heap_pushes,
            "heap_pops": total_heap_pops,
            "max_structure": max_pq_size,
            "description": f"Extracted minimum-cost router '{curr}' from priority queue with settled distance {int(cost) if cost.is_integer() else cost}."
        })

        if curr == dst:
            found = True
            break

        # Relax adjacent links in deterministic sorted order
        for nbr in sorted(graph.adjacency.get(curr, [])):
            if nbr not in graph.routers or not graph.routers[nbr].is_online:
                continue
            if hasattr(graph, "is_edge_active") and not graph.is_edge_active(curr, nbr):
                continue

            edge_pair = tuple(sorted((curr, nbr)))
            explored_edges_set.add(edge_pair)
            weight = graph.get_weight(curr, nbr)
            new_dist = cost + weight

            # Relaxation condition: discovered a strictly lower cumulative cost
            if new_dist < distances[nbr]:
                old_dist_str = "inf" if distances[nbr] == float("inf") else str(int(distances[nbr]) if distances[nbr].is_integer() else distances[nbr])
                distances[nbr] = new_dist
                parents[nbr] = curr
                tree_edges.append((curr, nbr))
                total_relaxations += 1
                heapq.heappush(pq, (new_dist, nbr))
                total_heap_pushes += 1
                max_pq_size = max(max_pq_size, len(pq))

                new_dist_str = str(int(new_dist) if new_dist.is_integer() else new_dist)
                steps.append({
                    "step": len(steps) + 1,
                    "operation": "RELAX_EDGE",
                    "current_node": curr,
                    "current_cost": cost,
                    "structure": format_pq_items(pq),
                    "priority_queue": sorted(list(pq)),
                    "tentative_distances": get_tentative_snapshot(),
                    "visited": list(visited_settled),
                    "parents": dict(parents),
                    "active_edge": (curr, nbr),
                    "action_target": nbr,
                    "relaxations": total_relaxations,
                    "heap_pushes": total_heap_pushes,
                    "heap_pops": total_heap_pops,
                    "max_structure": max_pq_size,
                    "description": f"Relaxed link ({curr} <-> {nbr}, weight: {int(weight) if weight.is_integer() else weight}). Improved distance to '{nbr}' from {old_dist_str} to {new_dist_str}. Enqueued into Min-Heap."
                })

    elapsed = (time.perf_counter() - start_time) * 1000.0

    if not found:
        steps.append({
            "step": len(steps) + 1,
            "operation": "FAILED",
            "current_node": None,
            "current_cost": None,
            "structure": format_pq_items(pq),
            "priority_queue": sorted(list(pq)),
            "tentative_distances": get_tentative_snapshot(),
            "visited": list(visited_settled),
            "parents": dict(parents),
            "active_edge": None,
            "action_target": None,
            "relaxations": total_relaxations,
            "heap_pushes": total_heap_pushes,
            "heap_pops": total_heap_pops,
            "max_structure": max_pq_size,
            "description": f"Priority queue exhausted. Destination '{dst}' is unreachable from '{src}' via available transmission links."
        })
        return {
            "algorithm": "Dijkstra (Priority Queue)",
            "success": False,
            "path": [],
            "hops": 0,
            "path_cost": 0.0,
            "steps": steps,
            "visited": visited_settled,
            "parents": parents,
            "distances": distances,
            "tree_edges": tree_edges,
            "max_structure": max_pq_size,
            "total_pushes": total_heap_pushes,
            "total_pops": total_heap_pops,
            "total_relaxations": total_relaxations,
            "total_heap_pushes": total_heap_pushes,
            "total_heap_pops": total_heap_pops,
            "explored_edges_count": len(explored_edges_set),
            "execution_time_ms": elapsed,
            "message": f"Destination '{dst}' is unreachable from '{src}'."
        }

    path = reconstruct_route_from_parents(parents, dst)
    final_cost = distances[dst]

    steps.append({
        "step": len(steps) + 1,
        "operation": "COMPLETE",
        "current_node": dst,
        "current_cost": final_cost,
        "structure": format_pq_items(pq),
        "priority_queue": sorted(list(pq)),
        "tentative_distances": get_tentative_snapshot(),
        "visited": list(visited_settled),
        "parents": dict(parents),
        "active_edge": None,
        "action_target": dst,
        "relaxations": total_relaxations,
        "heap_pushes": total_heap_pushes,
        "heap_pops": total_heap_pops,
        "max_structure": max_pq_size,
        "description": f"Dijkstra minimum-cost route verified: {' -> '.join(path)} ({len(path) - 1} hops, total cost: {int(final_cost) if final_cost.is_integer() else final_cost})."
    })

    return {
        "algorithm": "Dijkstra (Priority Queue)",
        "success": True,
        "path": path,
        "hops": len(path) - 1,
        "path_cost": final_cost,
        "steps": steps,
        "visited": visited_settled,
        "parents": parents,
        "distances": distances,
        "tree_edges": tree_edges,
        "max_structure": max_pq_size,
        "total_pushes": total_heap_pushes,
        "total_pops": total_heap_pops,
        "total_relaxations": total_relaxations,
        "total_heap_pushes": total_heap_pushes,
        "total_heap_pops": total_heap_pops,
        "explored_edges_count": len(explored_edges_set),
        "execution_time_ms": elapsed,
        "message": f"Minimum-cost route discovered: {' -> '.join(path)} (cost: {int(final_cost) if final_cost.is_integer() else final_cost}, {len(path) - 1} hops)."
    }

