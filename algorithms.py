"""
algorithms.py — Routing Traversal, Searching, Sorting, and Tree Structure Algorithms.

Integrated Course Outcomes:
- CO3: Searching (Linear vs. Binary) and Sorting (Bubble vs. Insertion) Algorithm Evaluation.
- CO4: Routing Traversal Spanning Tree Structure from Parent Pointers.
- CO5: Graph Traversals (BFS, DFS, Dijkstra) and Route Reconstruction.
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


# =============================================================================
# CO3: SEARCHING ALGORITHM EVALUATION
# =============================================================================

def linear_search(dataset: List[str], target: str) -> Dict[str, Any]:
    """
    Performs Linear Search on an unsorted or sorted list of router IDs.
    
    Theoretical Time Complexity: O(n) worst/average, O(1) best case.
    Space Complexity: O(1) auxiliary space.
    
    Examines each element sequentially from index 0 to n - 1 until the
    target router ID is found or the end of the dataset is reached.
    """
    start_time = time.perf_counter()
    target_clean = str(target).strip().upper()
    comparisons = 0
    found = False
    found_idx = -1
    steps: List[Dict[str, Any]] = []

    for i, item in enumerate(dataset):
        comparisons += 1
        curr_val = str(item).strip().upper()
        is_match = (curr_val == target_clean)
        steps.append({
            "step": i + 1,
            "index": i,
            "value": curr_val,
            "target": target_clean,
            "matched": is_match,
            "comparisons": comparisons,
            "description": f"Index {i}: Compared '{curr_val}' with target '{target_clean}' -> {'MATCH' if is_match else 'NO MATCH'}"
        })
        if is_match:
            found = True
            found_idx = i
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "algorithm": "Linear Search",
        "dataset_size": len(dataset),
        "target": target_clean,
        "found": found,
        "index": found_idx,
        "comparisons": comparisons,
        "execution_time_ms": elapsed_ms,
        "theoretical_complexity": "O(n)",
        "best_case": "O(1)",
        "worst_case": "O(n)",
        "requires_sorted": False,
        "steps": steps,
        "message": f"Target '{target_clean}' {'found at index ' + str(found_idx) if found else 'not found'} in {comparisons} comparison(s)."
    }


def binary_search(sorted_dataset: List[str], target: str, verify_sorted: bool = True) -> Dict[str, Any]:
    """
    Performs Binary Search on a sorted list of router IDs.
    
    Theoretical Time Complexity: O(log n) worst/average, O(1) best case.
    Space Complexity: O(1) auxiliary space.
    
    Requires data to be sorted because it uses divide-and-conquer:
    comparing the target with the middle element eliminates half of the
    remaining search space in every step.
    """
    start_time = time.perf_counter()
    target_clean = str(target).strip().upper()
    comparisons = 0
    found = False
    found_idx = -1
    steps: List[Dict[str, Any]] = []

    # Format list values cleanly for consistent comparison
    clean_data = [str(x).strip().upper() for x in sorted_dataset]

    # Verify sorted precondition
    is_sorted = True
    if verify_sorted and len(clean_data) > 1:
        for i in range(len(clean_data) - 1):
            if clean_data[i] > clean_data[i + 1]:
                is_sorted = False
                break

    if not is_sorted:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "algorithm": "Binary Search",
            "dataset_size": len(clean_data),
            "target": target_clean,
            "found": False,
            "index": -1,
            "comparisons": 0,
            "execution_time_ms": elapsed_ms,
            "theoretical_complexity": "O(log n)",
            "best_case": "O(1)",
            "worst_case": "O(log n)",
            "requires_sorted": True,
            "steps": [],
            "error": "Dataset is not sorted. Binary search requires sorted input to eliminate halves deterministically.",
            "message": "Error: Binary Search failed because input dataset is unsorted."
        }

    low = 0
    high = len(clean_data) - 1
    step_num = 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = clean_data[mid]
        comparisons += 1

        if mid_val == target_clean:
            found = True
            found_idx = mid
            steps.append({
                "step": step_num,
                "low": low,
                "high": high,
                "mid": mid,
                "mid_value": mid_val,
                "action": "MATCH",
                "comparisons": comparisons,
                "description": f"Step {step_num}: Mid index {mid} ('{mid_val}') matches target '{target_clean}'."
            })
            break
        elif mid_val < target_clean:
            steps.append({
                "step": step_num,
                "low": low,
                "high": high,
                "mid": mid,
                "mid_value": mid_val,
                "action": "GO_RIGHT",
                "comparisons": comparisons,
                "description": f"Step {step_num}: Mid '{mid_val}' < target '{target_clean}'. Eliminating left half; moving low to {mid + 1}."
            })
            low = mid + 1
        else:
            steps.append({
                "step": step_num,
                "low": low,
                "high": high,
                "mid": mid,
                "mid_value": mid_val,
                "action": "GO_LEFT",
                "comparisons": comparisons,
                "description": f"Step {step_num}: Mid '{mid_val}' > target '{target_clean}'. Eliminating right half; moving high to {mid - 1}."
            })
            high = mid - 1
        step_num += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "algorithm": "Binary Search",
        "dataset_size": len(clean_data),
        "target": target_clean,
        "found": found,
        "index": found_idx,
        "comparisons": comparisons,
        "execution_time_ms": elapsed_ms,
        "theoretical_complexity": "O(log n)",
        "best_case": "O(1)",
        "worst_case": "O(log n)",
        "requires_sorted": True,
        "steps": steps,
        "message": f"Target '{target_clean}' {'found at sorted index ' + str(found_idx) if found else 'not found'} in {comparisons} comparison(s)."
    }


# =============================================================================
# CO3: SORTING ALGORITHM EVALUATION
# =============================================================================

def bubble_sort(dataset: List[str]) -> Dict[str, Any]:
    """
    Performs Bubble Sort on a list of router IDs.
    
    Theoretical Time Complexity: O(n^2) worst/average, O(n) best case (with early exit).
    Space Complexity: O(1) auxiliary space (in-place on copy).
    
    Repeatedly steps through the list, compares adjacent elements, and swaps
    them if they are in the wrong order until no swaps are needed.
    """
    start_time = time.perf_counter()
    arr = [str(x).strip().upper() for x in dataset]
    n = len(arr)
    comparisons = 0
    swaps = 0
    pass_logs: List[Dict[str, Any]] = []

    for i in range(n):
        swapped_in_pass = False
        for j in range(0, n - i - 1):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped_in_pass = True
        pass_logs.append({
            "pass": i + 1,
            "array_state": list(arr),
            "swapped": swapped_in_pass
        })
        if not swapped_in_pass:
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    expected_sorted = sorted([str(x).strip().upper() for x in dataset])
    is_correct = (arr == expected_sorted)

    return {
        "algorithm": "Bubble Sort",
        "input_size": n,
        "original_data": [str(x).strip().upper() for x in dataset],
        "sorted_data": arr,
        "comparisons": comparisons,
        "swaps": swaps,
        "passes": len(pass_logs),
        "execution_time_ms": elapsed_ms,
        "theoretical_complexity": "O(n²)",
        "best_case": "O(n)",
        "worst_case": "O(n²)",
        "is_correct": is_correct,
        "pass_logs": pass_logs,
        "message": f"Bubble Sort completed in {comparisons} comparisons and {swaps} swaps. Correctness verified: {is_correct}."
    }


def insertion_sort(dataset: List[str]) -> Dict[str, Any]:
    """
    Performs Insertion Sort on a list of router IDs.
    
    Theoretical Time Complexity: O(n^2) worst/average, O(n) best case (for already sorted data).
    Space Complexity: O(1) auxiliary space (in-place on copy).
    
    Builds the sorted array one item at a time by picking the next element
    and shifting larger elements one position to the right to insert it.
    """
    start_time = time.perf_counter()
    arr = [str(x).strip().upper() for x in dataset]
    n = len(arr)
    comparisons = 0
    shifts = 0
    pass_logs: List[Dict[str, Any]] = []

    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                shifts += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
        pass_logs.append({
            "iteration": i,
            "inserted_key": key,
            "inserted_at": j + 1,
            "array_state": list(arr)
        })

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    expected_sorted = sorted([str(x).strip().upper() for x in dataset])
    is_correct = (arr == expected_sorted)

    return {
        "algorithm": "Insertion Sort",
        "input_size": n,
        "original_data": [str(x).strip().upper() for x in dataset],
        "sorted_data": arr,
        "comparisons": comparisons,
        "shifts": shifts,
        "swaps": shifts,
        "iterations": len(pass_logs),
        "execution_time_ms": elapsed_ms,
        "theoretical_complexity": "O(n²)",
        "best_case": "O(n)",
        "worst_case": "O(n²)",
        "is_correct": is_correct,
        "pass_logs": pass_logs,
        "message": f"Insertion Sort completed in {comparisons} comparisons and {shifts} shifts. Correctness verified: {is_correct}."
    }


# =============================================================================
# CO4: ROUTING TRAVERSAL TREE STRUCTURE
# =============================================================================

def build_traversal_tree(parents: Dict[str, Optional[str]], src: str, dst: Optional[str] = None) -> Dict[str, Any]:
    """
    Constructs a genuine Traversal Spanning Tree from the parent relationships
    recorded during BFS or DFS graph traversal.
    
    CO4 Properties Satisfied:
    1. Exactly one root node: the source router 'src'.
    2. Each reachable non-root router has exactly one parent in the tree.
    3. Traversal tree is strictly acyclic (no cycles) even if the network graph has cycles.
    4. Unreachable vertices are completely excluded from the tree.
    5. Tree edges represent the exact discovery transitions during traversal.
    6. Reconstructs root-to-destination path along tree edges.
    """
    src_clean = str(src).strip().upper()
    dst_clean = str(dst).strip().upper() if dst else None

    if not parents or src_clean not in parents:
        return {
            "root": src_clean,
            "nodes": [],
            "edges": [],
            "levels": {},
            "children": {},
            "path_to_dest": [],
            "is_acyclic": True,
            "node_count": 0,
            "edge_count": 0,
            "reachable": False,
            "message": f"Source '{src_clean}' has no recorded traversal parent data."
        }

    children_map: Dict[str, List[str]] = {node: [] for node in parents.keys()}
    edges: List[Tuple[str, str]] = []
    
    for child, parent in parents.items():
        if parent is not None:
            if parent in children_map:
                children_map[parent].append(child)
            else:
                children_map[parent] = [child]
            edges.append((parent, child))

    levels: Dict[str, int] = {src_clean: 0}
    q = deque([src_clean])
    visited_in_tree = {src_clean}
    has_cycle = False

    while q:
        curr = q.popleft()
        curr_level = levels[curr]
        for ch in children_map.get(curr, []):
            if ch in visited_in_tree:
                has_cycle = True
            else:
                visited_in_tree.add(ch)
                levels[ch] = curr_level + 1
                q.append(ch)

    dest_path: List[str] = []
    if dst_clean and dst_clean in parents:
        curr_dest = dst_clean
        while curr_dest is not None:
            dest_path.append(curr_dest)
            curr_dest = parents.get(curr_dest)
        dest_path.reverse()

    nodes_list = sorted(list(visited_in_tree), key=lambda x: (levels.get(x, 999), x))

    return {
        "root": src_clean,
        "nodes": nodes_list,
        "edges": edges,
        "levels": levels,
        "children": children_map,
        "path_to_dest": dest_path,
        "is_acyclic": not has_cycle,
        "node_count": len(nodes_list),
        "edge_count": len(edges),
        "reachable": bool(dst_clean in visited_in_tree) if dst_clean else True,
        "max_depth": max(levels.values()) if levels else 0,
        "message": f"Constructed traversal tree with root '{src_clean}', {len(nodes_list)} nodes, and {len(edges)} tree edges."
    }


