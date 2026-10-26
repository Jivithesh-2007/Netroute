"""
algorithms.py — Genuine BFS and DFS Graph Routing Algorithms.

Demonstrates:
- CO1: Stack and Queue Data Structures (FIFO Queue vs. LIFO Stack).
- CO5: Graph Traversal, Traversal Trees, and Shortest-Hop Routing.

Both algorithms record step-by-step internal states for the interactive visualizer.
"""

import time
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Any
from network import Graph


def bfs(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    """
    Breadth-First Search routing using a genuine FIFO queue.
    Guarantees the shortest-hop route in an unweighted graph.
    """
    start_time = time.perf_counter()
    src, dst = src.strip().upper(), dst.strip().upper()

    # Pre-condition validations
    if not graph.routers:
        return {"algorithm": "BFS (FIFO Queue)", "success": False, "message": "Network graph is empty.", "steps": [], "path": []}
    if src not in graph.routers or dst not in graph.routers:
        return {"algorithm": "BFS (FIFO Queue)", "success": False, "message": f"Endpoint router '{src}' or '{dst}' does not exist.", "steps": [], "path": []}
    if not graph.routers[src].is_online:
        return {"algorithm": "BFS (FIFO Queue)", "success": False, "message": f"Source router '{src}' is OFFLINE.", "steps": [], "path": []}
    if not graph.routers[dst].is_online:
        return {"algorithm": "BFS (FIFO Queue)", "success": False, "message": f"Destination router '{dst}' is OFFLINE.", "steps": [], "path": []}

    steps: List[Dict[str, Any]] = []

    # Handle trivial case: Source == Destination
    if src == dst:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append({
            "step": 1,
            "operation": "COMPLETE",
            "current_node": src,
            "structure": [src],
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
            "execution_time_ms": elapsed,
            "message": f"Direct route to '{src}' (0 hops)."
        }

    queue = deque([src])
    visited: Set[str] = {src}
    parents: Dict[str, Optional[str]] = {src: None}
    visited_order: List[str] = []
    tree_edges: List[Tuple[str, str]] = []

    total_enqueues = 1
    total_dequeues = 0
    max_queue_size = 1

    steps.append({
        "step": len(steps) + 1,
        "operation": "ENQUEUE",
        "current_node": src,
        "structure": list(queue),
        "visited": [],
        "parents": dict(parents),
        "active_edge": None,
        "description": f"Initialized queue. Enqueued source router '{src}' at rear (Level 0)."
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
            "visited": list(visited_order),
            "parents": dict(parents),
            "active_edge": None,
            "description": f"Dequeued router '{curr}' from queue front. Exploring adjacent connections."
        })

        if curr == dst:
            found = True
            break

        # Explore neighbors in consistent sorted alphabetical order
        for nbr in sorted(graph.adjacency.get(curr, [])):
            if nbr not in graph.routers or not graph.routers[nbr].is_online:
                continue

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
                    "visited": list(visited_order),
                    "parents": dict(parents),
                    "active_edge": (curr, nbr),
                    "description": f"Discovered unvisited neighbor '{nbr}' via link ({curr} <-> {nbr}). Enqueued at rear; set parent to '{curr}'."
                })

                if nbr == dst:
                    found = True
                    visited_order.append(nbr)
                    steps.append({
                        "step": len(steps) + 1,
                        "operation": "DESTINATION_FOUND",
                        "current_node": nbr,
                        "structure": list(queue),
                        "visited": list(visited_order),
                        "parents": dict(parents),
                        "active_edge": (curr, nbr),
                        "description": f"Destination router '{dst}' discovered! BFS guarantees minimum-hop route."
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
            "execution_time_ms": elapsed,
            "message": f"No route found between '{src}' and '{dst}'."
        }

    # Reconstruct shortest path using parent pointers
    path = []
    curr_back: Optional[str] = dst
    while curr_back is not None:
        path.append(curr_back)
        curr_back = parents.get(curr_back)
    path.reverse()

    steps.append({
        "step": len(steps) + 1,
        "operation": "COMPLETE",
        "current_node": dst,
        "structure": list(queue),
        "visited": list(visited_order),
        "parents": dict(parents),
        "active_edge": None,
        "description": f"BFS shortest route reconstructed: {' -> '.join(path)} ({len(path) - 1} hops)."
    })

    return {
        "algorithm": "BFS (FIFO Queue)",
        "success": True,
        "path": path,
        "hops": len(path) - 1,
        "steps": steps,
        "visited": visited_order,
        "parents": parents,
        "tree_edges": tree_edges,
        "max_structure": max_queue_size,
        "total_pushes": total_enqueues,
        "total_pops": total_dequeues,
        "execution_time_ms": elapsed,
        "message": f"Shortest route discovered: {' -> '.join(path)} ({len(path) - 1} hops)."
    }


def dfs(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    """
    Depth-First Search routing using an explicit LIFO stack.
    Explores deep branches before backtracking. Note: DFS does NOT guarantee shortest path.
    """
    start_time = time.perf_counter()
    src, dst = src.strip().upper(), dst.strip().upper()

    # Pre-condition validations
    if not graph.routers:
        return {"algorithm": "DFS (LIFO Stack)", "success": False, "message": "Network graph is empty.", "steps": [], "path": []}
    if src not in graph.routers or dst not in graph.routers:
        return {"algorithm": "DFS (LIFO Stack)", "success": False, "message": f"Endpoint router '{src}' or '{dst}' does not exist.", "steps": [], "path": []}
    if not graph.routers[src].is_online:
        return {"algorithm": "DFS (LIFO Stack)", "success": False, "message": f"Source router '{src}' is OFFLINE.", "steps": [], "path": []}
    if not graph.routers[dst].is_online:
        return {"algorithm": "DFS (LIFO Stack)", "success": False, "message": f"Destination router '{dst}' is OFFLINE.", "steps": [], "path": []}

    steps: List[Dict[str, Any]] = []

    # Handle trivial case: Source == Destination
    if src == dst:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append({
            "step": 1,
            "operation": "COMPLETE",
            "current_node": src,
            "structure": [src],
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
            "execution_time_ms": elapsed,
            "message": f"Direct route to '{src}' (0 hops)."
        }

    # Explicit LIFO stack storing (router_id, current_path)
    stack: List[Tuple[str, List[str]]] = [(src, [src])]
    visited: Set[str] = set()
    visited_order: List[str] = []
    parents: Dict[str, Optional[str]] = {src: None}
    tree_edges: List[Tuple[str, str]] = []

    total_pushes = 1
    total_pops = 0
    max_stack_size = 1

    steps.append({
        "step": len(steps) + 1,
        "operation": "PUSH",
        "current_node": src,
        "structure": [item[0] for item in stack],
        "visited": [],
        "parents": dict(parents),
        "active_edge": None,
        "description": f"Initialized DFS stack. Pushed source router '{src}' onto stack top."
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
            "visited": list(visited_order),
            "parents": dict(parents),
            "active_edge": None,
            "description": f"Popped router '{curr}' from stack top (Depth {len(path) - 1}). Exploring deepest unvisited branch."
        })

        if curr == dst:
            found_path = path
            steps.append({
                "step": len(steps) + 1,
                "operation": "DESTINATION_FOUND",
                "current_node": curr,
                "structure": [item[0] for item in stack],
                "visited": list(visited_order),
                "parents": dict(parents),
                "active_edge": None,
                "description": f"Destination router '{dst}' reached via DFS path! (Note: DFS does not guarantee minimum hops)."
            })
            break

        # Push unvisited neighbors in reverse alphabetical order so that
        # the alphabetically smallest neighbor is at the top of the stack and popped next!
        valid_nbrs = [
            n for n in sorted(graph.adjacency.get(curr, []), reverse=True)
            if n in graph.routers and graph.routers[n].is_online and n not in visited
        ]

        if valid_nbrs:
            for nbr in valid_nbrs:
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
                    "visited": list(visited_order),
                    "parents": dict(parents),
                    "active_edge": (curr, nbr),
                    "description": f"Pushed unvisited neighbor '{nbr}' onto DFS stack top via link ({curr} <-> {nbr})."
                })
        elif stack:
            next_top = stack[-1][0]
            steps.append({
                "step": len(steps) + 1,
                "operation": "BACKTRACK",
                "current_node": curr,
                "structure": [item[0] for item in stack],
                "visited": list(visited_order),
                "parents": dict(parents),
                "active_edge": None,
                "description": f"Dead end reached at '{curr}'. Backtracking to next available candidate on stack: '{next_top}'."
            })

    elapsed = (time.perf_counter() - start_time) * 1000.0

    if not found_path:
        steps.append({
            "step": len(steps) + 1,
            "operation": "FAILED",
            "current_node": None,
            "structure": [item[0] for item in stack],
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
            "execution_time_ms": elapsed,
            "message": f"No route found between '{src}' and '{dst}'."
        }

    steps.append({
        "step": len(steps) + 1,
        "operation": "COMPLETE",
        "current_node": dst,
        "structure": [item[0] for item in stack],
        "visited": list(visited_order),
        "parents": dict(parents),
        "active_edge": None,
        "description": f"DFS route discovered: {' -> '.join(found_path)} ({len(found_path) - 1} hops)."
    })

    return {
        "algorithm": "DFS (LIFO Stack)",
        "success": True,
        "path": found_path,
        "hops": len(found_path) - 1,
        "steps": steps,
        "visited": visited_order,
        "parents": parents,
        "tree_edges": tree_edges,
        "max_structure": max_stack_size,
        "total_pushes": total_pushes,
        "total_pops": total_pops,
        "execution_time_ms": elapsed,
        "message": f"Valid route discovered: {' -> '.join(found_path)} ({len(found_path) - 1} hops)."
    }
