"""
algorithms.py — Routing Traversal, Searching, Sorting, and Tree Structure Algorithms.

Integrated Course Outcomes:
- CO3: Searching (Linear vs. Binary) and Sorting (Bubble vs. Insertion) Algorithm Evaluation.
- CO4: Routing Traversal Spanning Tree Structure from Parent Pointers.
- CO5: Graph Traversals (BFS and DFS) and Route Reconstruction.
"""

import time
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Any
from network import Graph


def reconstruct_route_from_parents(parents: Dict[str, Optional[str]], dst: str) -> List[str]:
    """
    Reconstructs the discovered route from destination back to source
    using parent pointers recorded during traversal in O(L) time,
    where L is the number of hops.
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
            "message": "Network graph is empty.",
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

    if not graph.routers[src].is_online or not graph.routers[dst].is_online:
        offline_node = src if not graph.routers[src].is_online else dst
        return {
            "algorithm": "BFS (FIFO Queue)",
            "success": False,
            "message": f"Router '{offline_node}' is OFFLINE. Cannot transmit packets.",
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
            "description": f"Dequeued router '{curr}' from queue front. Examining its adjacent links."
        })

        if curr == dst:
            found = True
            break

        for nbr in sorted(graph.adjacency.get(curr, [])):
            if nbr not in graph.routers or not graph.routers[nbr].is_online:
                continue
            if not graph.is_edge_active(curr, nbr):
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
                    "description": f"Discovered unvisited neighbor '{nbr}' via ({curr} <-> {nbr}). Enqueued; set parent[{nbr}] = '{curr}'."
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
                        "description": f"Destination router '{dst}' discovered! BFS guarantees minimum hops in unweighted graphs."
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
            "description": f"Queue exhausted. Destination '{dst}' is unreachable from '{src}'."
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
        "description": f"BFS shortest route reconstructed: {' -> '.join(path)} ({len(path) - 1} hops)."
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
    DFS discovers a valid reachable path, but does NOT guarantee minimum hops.
    """
    start_time = time.perf_counter()
    src, dst = src.strip().upper(), dst.strip().upper()

    # Pre-condition validations
    if not graph.routers:
        return {
            "algorithm": "DFS (LIFO Stack)",
            "success": False,
            "message": "Network graph is empty.",
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

    if not graph.routers[src].is_online or not graph.routers[dst].is_online:
        offline_node = src if not graph.routers[src].is_online else dst
        return {
            "algorithm": "DFS (LIFO Stack)",
            "success": False,
            "message": f"Router '{offline_node}' is OFFLINE. Cannot transmit packets.",
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

    # Stack stores (router_id, current_path)
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
            "description": f"Popped router '{curr}' from stack top (Depth {len(path) - 1})."
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
                "description": f"Destination router '{dst}' reached via DFS path!"
            })
            break

        valid_nbrs = [
            n for n in sorted(graph.adjacency.get(curr, []), reverse=True)
            if n in graph.routers and graph.routers[n].is_online and n not in visited and graph.is_edge_active(curr, n)
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
                    "description": f"Pushed unvisited neighbor '{nbr}' onto DFS stack top via ({curr} <-> {nbr})."
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
                "description": f"Dead end reached at '{curr}'. Backtracking to: '{next_top}'."
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
        "description": f"DFS route discovered: {' -> '.join(found_path)} ({len(found_path) - 1} hops)."
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


# =============================================================================
# CO3: SEARCHING ALGORITHM EVALUATION
# =============================================================================

def linear_search(dataset: List[str], target: str) -> Dict[str, Any]:
    """
    Performs Linear Search on an unsorted or sorted list of router IDs.
    Theoretical Time Complexity: O(n) worst/average, O(1) best case.
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
    Requires data to be sorted (divide-and-conquer).
    """
    start_time = time.perf_counter()
    target_clean = str(target).strip().upper()
    comparisons = 0
    found = False
    found_idx = -1
    steps: List[Dict[str, Any]] = []

    clean_data = [str(x).strip().upper() for x in sorted_dataset]

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
                "description": f"Step {step_num}: Mid '{mid_val}' < '{target_clean}'. Eliminating left half; moving low to {mid + 1}."
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
                "description": f"Step {step_num}: Mid '{mid_val}' > '{target_clean}'. Eliminating right half; moving high to {mid - 1}."
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
        "message": f"Bubble Sort completed in {comparisons} comparisons and {swaps} swaps. Correctness: {is_correct}."
    }


def insertion_sort(dataset: List[str]) -> Dict[str, Any]:
    """
    Performs Insertion Sort on a list of router IDs.
    Theoretical Time Complexity: O(n^2) worst/average, O(n) best case.
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
        "message": f"Insertion Sort completed in {comparisons} comparisons and {shifts} shifts. Correctness: {is_correct}."
    }


# =============================================================================
# CO4: ROUTING TRAVERSAL TREE STRUCTURE
# =============================================================================

def build_traversal_tree(parents: Dict[str, Optional[str]], src: str, dst: Optional[str] = None) -> Dict[str, Any]:
    """
    Constructs a genuine Traversal Spanning Tree from parent relationships
    recorded during graph traversal.
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


# =============================================================================
# CO5 / ALGORITHM COMPARISON: BFS VS. DFS DUAL EVALUATION ENGINE
# =============================================================================

def compare_bfs_dfs(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    """
    Performs synchronized, dual-execution comparative analysis of Breadth-First Search (BFS)
    and Depth-First Search (DFS) on the active network topology between endpoints src and dst.

    Computes exhaustive side-by-side engineering metrics:
    - Path discovery, hop counts, and optimality delta.
    - Exploration efficiency (nodes visited, edges evaluated).
    - Peak memory footprint (Queue size vs Stack depth).
    - Structural operations (Enqueues/Dequeues vs Pushes/Pops/Backtracks).
    - Latency benchmarking with high-resolution performance timers.
    - Authoritative engineering verdict: determining which algorithm is best for network routing
      and computer science problem domains, backed by rigorous algorithmic theory.
    - Professional engineering suggestions and architectural best practices.
    """
    src_clean = str(src).strip().upper()
    dst_clean = str(dst).strip().upper()

    # Execute both algorithms
    bfs_res = bfs(graph, src_clean, dst_clean)
    dfs_res = dfs(graph, src_clean, dst_clean)

    both_success = bfs_res.get("success", False) and dfs_res.get("success", False)
    bfs_hops = bfs_res.get("hops", 0)
    dfs_hops = dfs_res.get("hops", 0)
    hop_delta = dfs_hops - bfs_hops
    same_path = (bfs_res.get("path") == dfs_res.get("path")) and both_success

    total_routers = len(graph.routers)
    bfs_visited_count = len(bfs_res.get("visited", []))
    dfs_visited_count = len(dfs_res.get("visited", []))

    bfs_coverage_pct = round((bfs_visited_count / total_routers * 100.0), 1) if total_routers > 0 else 0.0
    dfs_coverage_pct = round((dfs_visited_count / total_routers * 100.0), 1) if total_routers > 0 else 0.0

    # Determine Verdict & Best Algorithm
    if not bfs_res.get("success", False) and not dfs_res.get("success", False):
        verdict_title = "Mutually Consistent: Destination Unreachable"
        verdict_badge = "DESTINATION UNREACHABLE"
        verdict_color = "#EF4444"
        winner = "Neither (Target Unreachable)"
        verdict_summary = (
            f"Both BFS and DFS correctly confirmed that destination router '{dst_clean}' "
            f"cannot be reached from source router '{src_clean}' under the current network state. "
            "Graph traversal verified partition isolation."
        )
    elif bfs_hops < dfs_hops:
        verdict_title = "BFS is Strictly Superior (Discovered Guaranteed Minimum Hops)"
        verdict_badge = "BFS IS BEST FOR ROUTING"
        verdict_color = "#10B981"
        winner = "BFS (Breadth-First Search)"
        verdict_summary = (
            f"BFS discovered the optimal path in {bfs_hops} hops, whereas DFS discovered a sub-optimal "
            f"circuitous path in {dfs_hops} hops (+{hop_delta} extra hops, a {round(hop_delta / bfs_hops * 100, 1) if bfs_hops > 0 else 0}% hop penalty). "
            "In telecommunications, each extra router hop adds transmission, propagation, and queueing latency. "
            "BFS is mathematically guaranteed to find the minimum-hop path in unweighted graphs."
        )
    elif same_path:
        verdict_title = "BFS and DFS Converged on the Same Path (BFS Recommended)"
        verdict_badge = "BFS RECOMMENDED (PROVABLE GUARANTEE)"
        verdict_color = "#2563EB"
        winner = "BFS (Provable Guarantee)"
        verdict_summary = (
            f"Both algorithms discovered identical {bfs_hops}-hop paths (`{' -> '.join(bfs_res.get('path', []))}`). "
            "However, BFS guarantees this minimum-hop property across all arbitrary network topologies, "
            "whereas DFS only arrived at the shortest path by coincidence of neighbor traversal ordering."
        )
    else:
        # Same hop count but different path
        verdict_title = "Equal Hop Count with Alternative Routing Paths"
        verdict_badge = "BFS PREFERRED (DETERMINISTIC FRONTIER)"
        verdict_color = "#2563EB"
        winner = "BFS (Deterministic Breadth Frontier)"
        verdict_summary = (
            f"Both algorithms found distinct paths of {bfs_hops} hops. "
            "BFS explored symmetrically in concentric distance rings, ensuring deterministic minimum-latency delivery."
        )

    # Professional Engineering Suggestions
    suggestions = [
        {
            "category": "Packet Forwarding in Telecommunications",
            "title": "Use BFS / Dijkstra for Production Packet Forwarding",
            "recommendation": (
                "For packet routing across physical or virtual switches, always deploy BFS (for unweighted networks) "
                "or Dijkstra's Algorithm (Priority Queue BFS for weighted links like OSPF and IS-IS). DFS should NEVER "
                "be used for raw data packet forwarding because its meandering paths cause unpredictable latency, packet jitter, "
                "and link congestion."
            ),
            "applicable_algo": "BFS / Dijkstra",
            "impact": "High (Guarantees Minimum Latency)"
        },
        {
            "category": "Network Topology Auditing & Loop Prevention",
            "title": "Use DFS for Cycle Detection & Critical Failure Analysis",
            "recommendation": (
                "DFS is the gold standard for control-plane topology analysis. Use DFS back-edges to detect routing loops "
                "(analogous to Spanning Tree Protocol / STP) and to compute Articulation Points (critical single-router points "
                "of failure) and Bridges (critical transmission links) in linear O(V + E) time using Tarjan's algorithm."
            ),
            "applicable_algo": "DFS",
            "impact": "High (Fault-Tolerance & Resilience)"
        },
        {
            "category": "Memory-Constrained Systems & Sensor Networks",
            "title": "Evaluate Iterative Deepening (IDDFS) for Extreme Scale or Tiny RAM",
            "recommendation": (
                "When operating in resource-starved IoT microcontrollers (e.g., 2KB-8KB RAM Zigbee/LoRa nodes) or graphs "
                "with massive branching factors where BFS queue storage O(b^d) threatens to exhaust system memory, use "
                "Iterative Deepening Search (IDDFS). IDDFS provides BFS's shortest-path guarantee while using only DFS's O(d) memory."
            ),
            "applicable_algo": "IDDFS (Hybrid)",
            "impact": "Medium (Memory Optimization)"
        },
        {
            "category": "Network Protection & Resource Guardrails",
            "title": "Enforce Time-To-Live (TTL) & Hop-Count Guardrails",
            "recommendation": (
                "Both graph-based routing algorithms and distributed table forwarding must strictly enforce an IP Header "
                "TTL (Time-To-Live) / Hop Limit field. If transient topological flapping causes a routing loop, the decremented "
                "TTL ensures packets are discarded before consuming link capacity."
            ),
            "applicable_algo": "Network Layer Protocol",
            "impact": "Critical (Prevents Congestion Collapse)"
        }
    ]

    # Pre-computed Scenarios for Interactive Recommendation Engine
    scenario_guide = [
        {
            "scenario": "Unweighted Shortest-Hop Packet Routing (LAN / Data Center switching)",
            "best_choice": "BFS (Breadth-First Search)",
            "rationale": "FIFO queue explores level-by-level; provably guarantees minimum forwarding hops.",
            "complexity": "Time: O(V + E) | Space: O(V)",
            "industry_example": "Layer-2 Spanning Tree shortest path, Software-Defined Network (SDN) Controller route provisioning."
        },
        {
            "scenario": "Weighted Latency / Cost Metric Routing (Internet Core & Enterprise WAN)",
            "best_choice": "Dijkstra (Weighted BFS with Min-Priority Queue)",
            "rationale": "Generalizes BFS from unweighted unit hops to variable bandwidth, delay, and financial cost link weights.",
            "complexity": "Time: O((V + E) log V) | Space: O(V)",
            "industry_example": "OSPF (Open Shortest Path First), IS-IS (Intermediate System to Intermediate System)."
        },
        {
            "scenario": "Topology Loop & Cycle Detection",
            "best_choice": "DFS (Depth-First Search)",
            "rationale": "Recursion stack instantly flags back-edges to ancestors in O(V + E) time without exploring unnecessary branches.",
            "complexity": "Time: O(V + E) | Space: O(V)",
            "industry_example": "Ethernet STP (802.1D Spanning Tree Protocol), BGP AS-Path loop suppression."
        },
        {
            "scenario": "Critical Single Point of Failure (SPOF) Identification",
            "best_choice": "DFS (Tarjan's Articulation Points & Bridges Algorithm)",
            "rationale": "Tracks discovery times and lowest reachable ancestor times (low values) to find routers whose severance isolates subnets.",
            "complexity": "Time: O(V + E) | Space: O(V)",
            "industry_example": "Network reliability auditor, automated disaster-recovery redundancy analyzers."
        },
        {
            "scenario": "Firewall Rule Chaining & Network Task Dependency Ordering",
            "best_choice": "DFS (Topological Sort)",
            "rationale": "Produces a linear sequence where every predecessor rule or virtual network function precedes its consumer.",
            "complexity": "Time: O(V + E) | Space: O(V)",
            "industry_example": "Kubernetes service dependency graphs, Linux iptables policy compiler."
        },
        {
            "scenario": "Memory-Constrained Wireless Sensor Networks (IoT microcontrollers)",
            "best_choice": "IDDFS (Iterative Deepening Search) or DFS Reachability",
            "rationale": "Maintains stack size proportional to maximum depth O(d), preventing RAM out-of-memory crashes on embedded nodes.",
            "complexity": "Time: O(b^d) | Space: O(d)",
            "industry_example": "Zigbee/Thread mesh route discovery under 4KB RAM budgets."
        }
    ]

    return {
        "source": src_clean,
        "destination": dst_clean,
        "both_success": both_success,
        "same_path": same_path,
        "bfs": bfs_res,
        "dfs": dfs_res,
        "bfs_hops": bfs_hops,
        "dfs_hops": dfs_hops,
        "hop_delta": hop_delta,
        "bfs_visited_count": bfs_visited_count,
        "dfs_visited_count": dfs_visited_count,
        "bfs_coverage_pct": bfs_coverage_pct,
        "dfs_coverage_pct": dfs_coverage_pct,
        "verdict_title": verdict_title,
        "verdict_badge": verdict_badge,
        "verdict_color": verdict_color,
        "winner": winner,
        "verdict_summary": verdict_summary,
        "suggestions": suggestions,
        "scenario_guide": scenario_guide
    }

