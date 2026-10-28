import time
import math
import heapq
import random
from datetime import datetime, timezone
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Any
from network import Graph

def reconstruct_route_from_parents(parents: Dict[str, Optional[str]], dst: str) -> List[str]:
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
    start_time = time.perf_counter()
    src, dst = (src.strip().upper(), dst.strip().upper())
    if not graph.routers:
        return {'algorithm': 'BFS (FIFO Queue)', 'success': False, 'message': 'Network graph is empty.', 'steps': [], 'path': [], 'hops': 0, 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'total_enqueues': 0, 'total_dequeues': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0}
    if src not in graph.routers or dst not in graph.routers:
        return {'algorithm': 'BFS (FIFO Queue)', 'success': False, 'message': f"Endpoint router '{src}' or '{dst}' does not exist in the network.", 'steps': [], 'path': [], 'hops': 0, 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'total_enqueues': 0, 'total_dequeues': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0}
    if not graph.routers[src].is_online or not graph.routers[dst].is_online:
        offline_node = src if not graph.routers[src].is_online else dst
        return {'algorithm': 'BFS (FIFO Queue)', 'success': False, 'message': f"Router '{offline_node}' is OFFLINE. Cannot transmit packets.", 'steps': [], 'path': [], 'hops': 0, 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'total_enqueues': 0, 'total_dequeues': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0}
    steps: List[Dict[str, Any]] = []
    if src == dst:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append({'step': 1, 'operation': 'COMPLETE', 'current_node': src, 'neighbor': None, 'neighbor_visited': True, 'neighbor_status': 'complete', 'why': f"Source router '{src}' is identical to destination. Direct match with 0 hops.", 'structure': [src], 'structure_before': [], 'structure_after': [src], 'front': src, 'rear': src, 'action_target': src, 'enqueues': 1, 'dequeues': 0, 'max_structure': 1, 'visited': [src], 'parents': {src: None}, 'parent_assigned': None, 'current_path': [src], 'active_edge': None, 'description': f"Source router '{src}' is identical to destination. Direct match with 0 hops."})
        return {'algorithm': 'BFS (FIFO Queue)', 'success': True, 'path': [src], 'hops': 0, 'steps': steps, 'visited': [src], 'parents': {src: None}, 'tree_edges': [], 'max_structure': 1, 'total_pushes': 1, 'total_pops': 0, 'total_enqueues': 1, 'total_dequeues': 0, 'explored_edges_count': 0, 'execution_time_ms': elapsed, 'message': f"Direct route to '{src}' (0 hops)."}
    queue = deque([src])
    visited: Set[str] = {src}
    parents: Dict[str, Optional[str]] = {src: None}
    visited_order: List[str] = []
    tree_edges: List[Tuple[str, str]] = []
    explored_edges_set: Set[Tuple[str, str]] = set()
    total_enqueues = 1
    total_dequeues = 0
    max_queue_size = 1
    steps.append({'step': len(steps) + 1, 'operation': 'ENQUEUE', 'current_node': src, 'neighbor': None, 'neighbor_visited': False, 'neighbor_status': 'source_init', 'why': f"Initialized FIFO queue. Enqueued source router '{src}' at rear (Distance Level 0).", 'structure': list(queue), 'structure_before': [], 'structure_after': list(queue), 'front': queue[0] if queue else None, 'rear': queue[-1] if queue else None, 'action_target': src, 'enqueues': total_enqueues, 'dequeues': total_dequeues, 'max_structure': max_queue_size, 'visited': [], 'parents': dict(parents), 'parent_assigned': None, 'current_path': [src], 'active_edge': None, 'description': f"Initialized FIFO queue. Enqueued source router '{src}' at rear (Distance Level 0)."})
    found = False
    while queue:
        struct_before = list(queue)
        curr = queue.popleft()
        total_dequeues += 1
        visited_order.append(curr)
        steps.append({'step': len(steps) + 1, 'operation': 'DEQUEUE', 'current_node': curr, 'neighbor': None, 'neighbor_visited': None, 'neighbor_status': None, 'why': f"Router '{curr}' was removed from the front of the queue to process its unvisited neighbors in FIFO distance order.", 'structure': list(queue), 'structure_before': struct_before, 'structure_after': list(queue), 'front': queue[0] if queue else None, 'rear': queue[-1] if queue else None, 'action_target': curr, 'enqueues': total_enqueues, 'dequeues': total_dequeues, 'max_structure': max_queue_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(curr), 'current_path': reconstruct_route_from_parents(parents, curr), 'active_edge': None, 'description': f"Dequeued router '{curr}' from queue front. Examining its adjacent links."})
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
                struct_pre_enq = list(queue)
                visited.add(nbr)
                parents[nbr] = curr
                tree_edges.append((curr, nbr))
                queue.append(nbr)
                total_enqueues += 1
                max_queue_size = max(max_queue_size, len(queue))
                steps.append({'step': len(steps) + 1, 'operation': 'ENQUEUE', 'current_node': nbr, 'neighbor': nbr, 'neighbor_visited': False, 'neighbor_status': 'discovered', 'why': f"Router '{curr}' was removed from the queue. Its neighbor '{nbr}' has not been visited, so '{nbr}' is marked as discovered, its parent is recorded as '{curr}', and '{nbr}' is added to the queue.", 'structure': list(queue), 'structure_before': struct_pre_enq, 'structure_after': list(queue), 'front': queue[0] if queue else None, 'rear': queue[-1] if queue else None, 'action_target': nbr, 'enqueues': total_enqueues, 'dequeues': total_dequeues, 'max_structure': max_queue_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': curr, 'current_path': reconstruct_route_from_parents(parents, nbr), 'active_edge': (curr, nbr), 'description': f"Discovered unvisited neighbor '{nbr}' via ({curr} <-> {nbr}). Enqueued; set parent[{nbr}] = '{curr}'."})
                if nbr == dst:
                    found = True
                    visited_order.append(nbr)
                    steps.append({'step': len(steps) + 1, 'operation': 'DESTINATION_FOUND', 'current_node': nbr, 'neighbor': nbr, 'neighbor_visited': False, 'neighbor_status': 'target_reached', 'why': f"Destination router '{dst}' discovered! BFS guarantees minimum hops in unweighted graphs.", 'structure': list(queue), 'structure_before': list(queue), 'structure_after': list(queue), 'front': queue[0] if queue else None, 'rear': queue[-1] if queue else None, 'action_target': nbr, 'enqueues': total_enqueues, 'dequeues': total_dequeues, 'max_structure': max_queue_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': curr, 'current_path': reconstruct_route_from_parents(parents, dst), 'active_edge': (curr, nbr), 'description': f"Destination router '{dst}' discovered! BFS guarantees minimum hops in unweighted graphs."})
                    break
        if found:
            break
    elapsed = (time.perf_counter() - start_time) * 1000.0
    if not found:
        steps.append({'step': len(steps) + 1, 'operation': 'FAILED', 'current_node': None, 'neighbor': None, 'neighbor_visited': False, 'neighbor_status': 'unreachable', 'why': f"FIFO Queue exhausted. Destination '{dst}' is unreachable from '{src}'. All connected routers explored without reaching destination.", 'structure': list(queue), 'structure_before': list(queue), 'structure_after': list(queue), 'front': None, 'rear': None, 'action_target': None, 'enqueues': total_enqueues, 'dequeues': total_dequeues, 'max_structure': max_queue_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': None, 'current_path': [], 'active_edge': None, 'description': f"Queue exhausted. Destination '{dst}' is unreachable from '{src}'."})
        return {'algorithm': 'BFS (FIFO Queue)', 'success': False, 'path': [], 'hops': 0, 'steps': steps, 'visited': visited_order, 'parents': parents, 'tree_edges': tree_edges, 'max_structure': max_queue_size, 'total_pushes': total_enqueues, 'total_pops': total_dequeues, 'total_enqueues': total_enqueues, 'total_dequeues': total_dequeues, 'explored_edges_count': len(explored_edges_set), 'execution_time_ms': elapsed, 'message': f"No route found between '{src}' and '{dst}'."}
    path = reconstruct_route_from_parents(parents, dst)
    path_cost = sum((graph.get_weight(path[i], path[i + 1]) for i in range(len(path) - 1))) if len(path) > 1 else 0.0
    steps.append({'step': len(steps) + 1, 'operation': 'COMPLETE', 'current_node': dst, 'neighbor': None, 'neighbor_visited': True, 'neighbor_status': 'complete', 'why': f"BFS shortest route reconstructed: {' -> '.join(path)} ({len(path) - 1} hops). Guaranteed optimal hop count in unweighted network.", 'structure': list(queue), 'structure_before': list(queue), 'structure_after': list(queue), 'front': queue[0] if queue else None, 'rear': queue[-1] if queue else None, 'action_target': dst, 'enqueues': total_enqueues, 'dequeues': total_dequeues, 'max_structure': max_queue_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(dst), 'current_path': list(path), 'active_edge': None, 'description': f"BFS shortest route reconstructed: {' -> '.join(path)} ({len(path) - 1} hops)."})
    return {'algorithm': 'BFS (FIFO Queue)', 'success': True, 'path': path, 'hops': len(path) - 1, 'path_cost': path_cost, 'steps': steps, 'visited': visited_order, 'parents': parents, 'tree_edges': tree_edges, 'max_structure': max_queue_size, 'total_pushes': total_enqueues, 'total_pops': total_dequeues, 'total_enqueues': total_enqueues, 'total_dequeues': total_dequeues, 'explored_edges_count': len(explored_edges_set), 'execution_time_ms': elapsed, 'message': f"Shortest route discovered: {' -> '.join(path)} ({len(path) - 1} hops)."}

def dfs(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    start_time = time.perf_counter()
    src, dst = (src.strip().upper(), dst.strip().upper())
    if not graph.routers:
        return {'algorithm': 'DFS (LIFO Stack)', 'success': False, 'message': 'Network graph is empty.', 'steps': [], 'path': [], 'hops': 0, 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'backtrack_count': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0}
    if src not in graph.routers or dst not in graph.routers:
        return {'algorithm': 'DFS (LIFO Stack)', 'success': False, 'message': f"Endpoint router '{src}' or '{dst}' does not exist in the network.", 'steps': [], 'path': [], 'hops': 0, 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'backtrack_count': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0}
    if not graph.routers[src].is_online or not graph.routers[dst].is_online:
        offline_node = src if not graph.routers[src].is_online else dst
        return {'algorithm': 'DFS (LIFO Stack)', 'success': False, 'message': f"Router '{offline_node}' is OFFLINE. Cannot transmit packets.", 'steps': [], 'path': [], 'hops': 0, 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'backtrack_count': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0}
    steps: List[Dict[str, Any]] = []
    if src == dst:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append({'step': 1, 'operation': 'COMPLETE', 'current_node': src, 'neighbor': None, 'neighbor_visited': True, 'neighbor_status': 'complete', 'why': f"Source router '{src}' is identical to destination. Direct match with 0 hops.", 'structure': [src], 'structure_before': [], 'structure_after': [src], 'top': src, 'bottom': src, 'action_target': src, 'pushes': 1, 'pops': 0, 'max_structure': 1, 'is_backtrack': False, 'visited': [src], 'parents': {src: None}, 'parent_assigned': None, 'current_path': [src], 'active_edge': None, 'description': f"Source router '{src}' is identical to destination. Direct match with 0 hops."})
        return {'algorithm': 'DFS (LIFO Stack)', 'success': True, 'path': [src], 'hops': 0, 'steps': steps, 'visited': [src], 'parents': {src: None}, 'tree_edges': [], 'max_structure': 1, 'total_pushes': 1, 'total_pops': 0, 'backtrack_count': 0, 'explored_edges_count': 0, 'execution_time_ms': elapsed, 'message': f"Direct route to '{src}' (0 hops)."}
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
    steps.append({'step': len(steps) + 1, 'operation': 'PUSH', 'current_node': src, 'neighbor': None, 'neighbor_visited': False, 'neighbor_status': 'source_init', 'why': f"Initialized LIFO stack. Pushed source router '{src}' onto stack top.", 'structure': [item[0] for item in stack], 'structure_before': [], 'structure_after': [item[0] for item in stack], 'top': stack[-1][0] if stack else None, 'bottom': stack[0][0] if stack else None, 'action_target': src, 'pushes': total_pushes, 'pops': total_pops, 'max_structure': max_stack_size, 'is_backtrack': False, 'visited': [], 'parents': dict(parents), 'parent_assigned': None, 'current_path': [src], 'active_edge': None, 'description': f"Initialized LIFO stack. Pushed source router '{src}' onto stack top."})
    found_path: Optional[List[str]] = None
    while stack:
        struct_before_pop = [item[0] for item in stack]
        curr, path = stack.pop()
        total_pops += 1
        if curr in visited:
            continue
        visited.add(curr)
        visited_order.append(curr)
        steps.append({'step': len(steps) + 1, 'operation': 'POP', 'current_node': curr, 'neighbor': None, 'neighbor_visited': None, 'neighbor_status': None, 'why': f"Router '{curr}' was removed from the stack top (Depth {len(path) - 1}) to explore its unvisited neighbor branches.", 'structure': [item[0] for item in stack], 'structure_before': struct_before_pop, 'structure_after': [item[0] for item in stack], 'top': stack[-1][0] if stack else None, 'bottom': stack[0][0] if stack else None, 'action_target': curr, 'pushes': total_pushes, 'pops': total_pops, 'max_structure': max_stack_size, 'is_backtrack': False, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(curr), 'current_path': list(path), 'active_edge': None, 'description': f"Popped router '{curr}' from stack top (Depth {len(path) - 1})."})
        if curr == dst:
            found_path = path
            steps.append({'step': len(steps) + 1, 'operation': 'DESTINATION_FOUND', 'current_node': curr, 'neighbor': None, 'neighbor_visited': False, 'neighbor_status': 'target_reached', 'why': f"Destination router '{dst}' reached via DFS path! Found reachable route with {len(path) - 1} hops.", 'structure': [item[0] for item in stack], 'structure_before': [item[0] for item in stack], 'structure_after': [item[0] for item in stack], 'top': stack[-1][0] if stack else None, 'bottom': stack[0][0] if stack else None, 'action_target': curr, 'pushes': total_pushes, 'pops': total_pops, 'max_structure': max_stack_size, 'is_backtrack': False, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(curr), 'current_path': list(path), 'active_edge': None, 'description': f"Destination router '{dst}' reached via DFS path!"})
            break
        valid_nbrs = [n for n in sorted(graph.adjacency.get(curr, []), reverse=True) if n in graph.routers and graph.routers[n].is_online and (n not in visited) and graph.is_edge_active(curr, n)]
        if valid_nbrs:
            for nbr in valid_nbrs:
                struct_before_push = [item[0] for item in stack]
                edge_pair = tuple(sorted((curr, nbr)))
                explored_edges_set.add(edge_pair)
                parents[nbr] = curr
                tree_edges.append((curr, nbr))
                stack.append((nbr, path + [nbr]))
                total_pushes += 1
                max_stack_size = max(max_stack_size, len(stack))
                steps.append({'step': len(steps) + 1, 'operation': 'PUSH', 'current_node': nbr, 'neighbor': nbr, 'neighbor_visited': False, 'neighbor_status': 'discovered', 'why': f"Router '{curr}' is selected from the stack. Its unvisited neighbor '{nbr}' is discovered and pushed onto the stack, so DFS continues deeper into this branch.", 'structure': [item[0] for item in stack], 'structure_before': struct_before_push, 'structure_after': [item[0] for item in stack], 'top': stack[-1][0] if stack else None, 'bottom': stack[0][0] if stack else None, 'action_target': nbr, 'pushes': total_pushes, 'pops': total_pops, 'max_structure': max_stack_size, 'is_backtrack': False, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': curr, 'current_path': list(path + [nbr]), 'active_edge': (curr, nbr), 'description': f"Pushed unvisited neighbor '{nbr}' onto DFS stack top via ({curr} <-> {nbr})."})
        elif stack:
            backtrack_count += 1
            next_top = stack[-1][0]
            steps.append({'step': len(steps) + 1, 'operation': 'BACKTRACK', 'current_node': curr, 'neighbor': next_top, 'neighbor_visited': True, 'neighbor_status': 'backtrack', 'why': f"All neighbors of router '{curr}' are already visited or unreachable (dead end). Backtracking up the stack to '{next_top}'.", 'structure': [item[0] for item in stack], 'structure_before': [item[0] for item in stack], 'structure_after': [item[0] for item in stack], 'top': stack[-1][0] if stack else None, 'bottom': stack[0][0] if stack else None, 'action_target': curr, 'pushes': total_pushes, 'pops': total_pops, 'max_structure': max_stack_size, 'is_backtrack': True, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(next_top), 'current_path': reconstruct_route_from_parents(parents, next_top), 'active_edge': None, 'description': f"Dead end reached at '{curr}'. Backtracking to: '{next_top}'."})
    elapsed = (time.perf_counter() - start_time) * 1000.0
    if not found_path:
        steps.append({'step': len(steps) + 1, 'operation': 'FAILED', 'current_node': None, 'neighbor': None, 'neighbor_visited': False, 'neighbor_status': 'unreachable', 'why': f"DFS stack exhausted. Destination '{dst}' is unreachable from '{src}'. All connected paths explored without reaching destination.", 'structure': [item[0] for item in stack], 'structure_before': [item[0] for item in stack], 'structure_after': [item[0] for item in stack], 'top': None, 'bottom': None, 'action_target': None, 'pushes': total_pushes, 'pops': total_pops, 'max_structure': max_stack_size, 'is_backtrack': False, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': None, 'current_path': [], 'active_edge': None, 'description': f"Stack exhausted. Destination '{dst}' is unreachable from '{src}' via DFS."})
        return {'algorithm': 'DFS (LIFO Stack)', 'success': False, 'path': [], 'hops': 0, 'steps': steps, 'visited': visited_order, 'parents': parents, 'tree_edges': tree_edges, 'max_structure': max_stack_size, 'total_pushes': total_pushes, 'total_pops': total_pops, 'backtrack_count': backtrack_count, 'explored_edges_count': len(explored_edges_set), 'execution_time_ms': elapsed, 'message': f"No route found between '{src}' and '{dst}'."}
    path_cost = sum((graph.get_weight(found_path[i], found_path[i + 1]) for i in range(len(found_path) - 1))) if len(found_path) > 1 else 0.0
    steps.append({'step': len(steps) + 1, 'operation': 'COMPLETE', 'current_node': dst, 'neighbor': None, 'neighbor_visited': True, 'neighbor_status': 'complete', 'why': f"DFS route exploration complete: {' -> '.join(found_path)} ({len(found_path) - 1} hops). Valid path discovered via depth-first branch exploration.", 'structure': [item[0] for item in stack], 'structure_before': [item[0] for item in stack], 'structure_after': [item[0] for item in stack], 'top': stack[-1][0] if stack else None, 'bottom': stack[0][0] if stack else None, 'action_target': dst, 'pushes': total_pushes, 'pops': total_pops, 'max_structure': max_stack_size, 'is_backtrack': False, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(dst), 'current_path': list(found_path), 'active_edge': None, 'description': f"DFS route discovered: {' -> '.join(found_path)} ({len(found_path) - 1} hops)."})
    return {'algorithm': 'DFS (LIFO Stack)', 'success': True, 'path': found_path, 'hops': len(found_path) - 1, 'path_cost': path_cost, 'steps': steps, 'visited': visited_order, 'parents': parents, 'tree_edges': tree_edges, 'max_structure': max_stack_size, 'total_pushes': total_pushes, 'total_pops': total_pops, 'backtrack_count': backtrack_count, 'explored_edges_count': len(explored_edges_set), 'execution_time_ms': elapsed, 'message': f"Valid route discovered: {' -> '.join(found_path)} ({len(found_path) - 1} hops)."}

def linear_search(dataset: List[str], target: str) -> Dict[str, Any]:
    start_time = time.perf_counter()
    target_clean = str(target).strip().upper()
    comparisons = 0
    found = False
    found_idx = -1
    steps: List[Dict[str, Any]] = []
    for i, item in enumerate(dataset):
        comparisons += 1
        curr_val = str(item).strip().upper()
        is_match = curr_val == target_clean
        steps.append({'step': i + 1, 'index': i, 'value': curr_val, 'target': target_clean, 'matched': is_match, 'comparisons': comparisons, 'description': f"Index {i}: Compared '{curr_val}' with target '{target_clean}' -> {('MATCH' if is_match else 'NO MATCH')}"})
        if is_match:
            found = True
            found_idx = i
            break
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return {'algorithm': 'Linear Search', 'dataset_size': len(dataset), 'target': target_clean, 'found': found, 'index': found_idx, 'comparisons': comparisons, 'execution_time_ms': elapsed_ms, 'theoretical_complexity': 'O(n)', 'best_case': 'O(1)', 'worst_case': 'O(n)', 'requires_sorted': False, 'steps': steps, 'message': f"Target '{target_clean}' {('found at index ' + str(found_idx) if found else 'not found')} in {comparisons} comparison(s)."}

def binary_search(sorted_dataset: List[str], target: str, verify_sorted: bool=True) -> Dict[str, Any]:
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
        return {'algorithm': 'Binary Search', 'dataset_size': len(clean_data), 'target': target_clean, 'found': False, 'index': -1, 'comparisons': 0, 'execution_time_ms': elapsed_ms, 'theoretical_complexity': 'O(log n)', 'best_case': 'O(1)', 'worst_case': 'O(log n)', 'requires_sorted': True, 'steps': [], 'error': 'Dataset is not sorted. Binary search requires sorted input to eliminate halves deterministically.', 'message': 'Error: Binary Search failed because input dataset is unsorted.'}
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
            steps.append({'step': step_num, 'low': low, 'high': high, 'mid': mid, 'mid_value': mid_val, 'action': 'MATCH', 'comparisons': comparisons, 'description': f"Step {step_num}: Mid index {mid} ('{mid_val}') matches target '{target_clean}'."})
            break
        elif mid_val < target_clean:
            steps.append({'step': step_num, 'low': low, 'high': high, 'mid': mid, 'mid_value': mid_val, 'action': 'GO_RIGHT', 'comparisons': comparisons, 'description': f"Step {step_num}: Mid '{mid_val}' < '{target_clean}'. Eliminating left half; moving low to {mid + 1}."})
            low = mid + 1
        else:
            steps.append({'step': step_num, 'low': low, 'high': high, 'mid': mid, 'mid_value': mid_val, 'action': 'GO_LEFT', 'comparisons': comparisons, 'description': f"Step {step_num}: Mid '{mid_val}' > '{target_clean}'. Eliminating right half; moving high to {mid - 1}."})
            high = mid - 1
        step_num += 1
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return {'algorithm': 'Binary Search', 'dataset_size': len(clean_data), 'target': target_clean, 'found': found, 'index': found_idx, 'comparisons': comparisons, 'execution_time_ms': elapsed_ms, 'theoretical_complexity': 'O(log n)', 'best_case': 'O(1)', 'worst_case': 'O(log n)', 'requires_sorted': True, 'steps': steps, 'message': f"Target '{target_clean}' {('found at sorted index ' + str(found_idx) if found else 'not found')} in {comparisons} comparison(s)."}

def bubble_sort(dataset: List[str]) -> Dict[str, Any]:
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
                arr[j], arr[j + 1] = (arr[j + 1], arr[j])
                swaps += 1
                swapped_in_pass = True
        pass_logs.append({'pass': i + 1, 'array_state': list(arr), 'swapped': swapped_in_pass})
        if not swapped_in_pass:
            break
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    expected_sorted = sorted([str(x).strip().upper() for x in dataset])
    is_correct = arr == expected_sorted
    return {'algorithm': 'Bubble Sort', 'input_size': n, 'original_data': [str(x).strip().upper() for x in dataset], 'sorted_data': arr, 'comparisons': comparisons, 'swaps': swaps, 'passes': len(pass_logs), 'execution_time_ms': elapsed_ms, 'theoretical_complexity': 'O(n²)', 'best_case': 'O(n)', 'worst_case': 'O(n²)', 'is_correct': is_correct, 'pass_logs': pass_logs, 'message': f'Bubble Sort completed in {comparisons} comparisons and {swaps} swaps. Correctness: {is_correct}.'}

def insertion_sort(dataset: List[str]) -> Dict[str, Any]:
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
        pass_logs.append({'iteration': i, 'inserted_key': key, 'inserted_at': j + 1, 'array_state': list(arr)})
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    expected_sorted = sorted([str(x).strip().upper() for x in dataset])
    is_correct = arr == expected_sorted
    return {'algorithm': 'Insertion Sort', 'input_size': n, 'original_data': [str(x).strip().upper() for x in dataset], 'sorted_data': arr, 'comparisons': comparisons, 'shifts': shifts, 'swaps': shifts, 'iterations': len(pass_logs), 'execution_time_ms': elapsed_ms, 'theoretical_complexity': 'O(n²)', 'best_case': 'O(n)', 'worst_case': 'O(n²)', 'is_correct': is_correct, 'pass_logs': pass_logs, 'message': f'Insertion Sort completed in {comparisons} comparisons and {shifts} shifts. Correctness: {is_correct}.'}

def build_traversal_tree(parents: Dict[str, Optional[str]], src: str, dst: Optional[str]=None) -> Dict[str, Any]:
    src_clean = str(src).strip().upper()
    dst_clean = str(dst).strip().upper() if dst else None
    if not parents or src_clean not in parents:
        return {'root': src_clean, 'nodes': [], 'edges': [], 'levels': {}, 'children': {}, 'path_to_dest': [], 'is_acyclic': True, 'node_count': 0, 'edge_count': 0, 'reachable': False, 'message': f"Source '{src_clean}' has no recorded traversal parent data."}
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
    return {'root': src_clean, 'nodes': nodes_list, 'edges': edges, 'levels': levels, 'children': children_map, 'path_to_dest': dest_path, 'is_acyclic': not has_cycle, 'node_count': len(nodes_list), 'edge_count': len(edges), 'reachable': bool(dst_clean in visited_in_tree) if dst_clean else True, 'max_depth': max(levels.values()) if levels else 0, 'message': f"Constructed traversal tree with root '{src_clean}', {len(nodes_list)} nodes, and {len(edges)} tree edges."}

def compare_bfs_dfs(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    src_clean = str(src).strip().upper()
    dst_clean = str(dst).strip().upper()
    bfs_res = bfs(graph, src_clean, dst_clean)
    dfs_res = dfs(graph, src_clean, dst_clean)
    both_success = bfs_res.get('success', False) and dfs_res.get('success', False)
    bfs_hops = bfs_res.get('hops', 0)
    dfs_hops = dfs_res.get('hops', 0)
    hop_delta = dfs_hops - bfs_hops
    same_path = bfs_res.get('path') == dfs_res.get('path') and both_success
    total_routers = len(graph.routers)
    bfs_visited_count = len(bfs_res.get('visited', []))
    dfs_visited_count = len(dfs_res.get('visited', []))
    bfs_coverage_pct = round(bfs_visited_count / total_routers * 100.0, 1) if total_routers > 0 else 0.0
    dfs_coverage_pct = round(dfs_visited_count / total_routers * 100.0, 1) if total_routers > 0 else 0.0
    if not bfs_res.get('success', False) and (not dfs_res.get('success', False)):
        verdict_title = 'Mutually Consistent: Destination Unreachable'
        verdict_badge = 'DESTINATION UNREACHABLE'
        verdict_color = '#EF4444'
        winner = 'Neither (Target Unreachable)'
        verdict_summary = f"Both BFS and DFS correctly confirmed that destination router '{dst_clean}' cannot be reached from source router '{src_clean}' under the current network state. Graph traversal verified partition isolation."
    elif bfs_hops < dfs_hops:
        verdict_title = 'BFS is Strictly Superior (Discovered Guaranteed Minimum Hops)'
        verdict_badge = 'BFS IS BEST FOR ROUTING'
        verdict_color = '#10B981'
        winner = 'BFS (Breadth-First Search)'
        verdict_summary = f'BFS discovered the optimal path in {bfs_hops} hops, whereas DFS discovered a sub-optimal circuitous path in {dfs_hops} hops (+{hop_delta} extra hops, a {(round(hop_delta / bfs_hops * 100, 1) if bfs_hops > 0 else 0)}% hop penalty). In telecommunications, each extra router hop adds transmission, propagation, and queueing latency. BFS is mathematically guaranteed to find the minimum-hop path in unweighted graphs.'
    elif same_path:
        verdict_title = 'BFS and DFS Converged on the Same Path (BFS Recommended)'
        verdict_badge = 'BFS RECOMMENDED (PROVABLE GUARANTEE)'
        verdict_color = '#2563EB'
        winner = 'BFS (Provable Guarantee)'
        verdict_summary = f"Both algorithms discovered identical {bfs_hops}-hop paths (`{' -> '.join(bfs_res.get('path', []))}`). However, BFS guarantees this minimum-hop property across all arbitrary network topologies, whereas DFS only arrived at the shortest path by coincidence of neighbor traversal ordering."
    else:
        verdict_title = 'Equal Hop Count with Alternative Routing Paths'
        verdict_badge = 'BFS PREFERRED (DETERMINISTIC FRONTIER)'
        verdict_color = '#2563EB'
        winner = 'BFS (Deterministic Breadth Frontier)'
        verdict_summary = f'Both algorithms found distinct paths of {bfs_hops} hops. BFS explored symmetrically in concentric distance rings, ensuring deterministic minimum-latency delivery.'
    suggestions = [{'category': 'Packet Forwarding in Telecommunications', 'title': 'Use BFS / Dijkstra for Production Packet Forwarding', 'recommendation': "For packet routing across physical or virtual switches, always deploy BFS (for unweighted networks) or Dijkstra's Algorithm (Priority Queue BFS for weighted links like OSPF and IS-IS). DFS should NEVER be used for raw data packet forwarding because its meandering paths cause unpredictable latency, packet jitter, and link congestion.", 'applicable_algo': 'BFS / Dijkstra', 'impact': 'High (Guarantees Minimum Latency)'}, {'category': 'Network Topology Auditing & Loop Prevention', 'title': 'Use DFS for Cycle Detection & Critical Failure Analysis', 'recommendation': "DFS is the gold standard for control-plane topology analysis. Use DFS back-edges to detect routing loops (analogous to Spanning Tree Protocol / STP) and to compute Articulation Points (critical single-router points of failure) and Bridges (critical transmission links) in linear O(V + E) time using Tarjan's algorithm.", 'applicable_algo': 'DFS', 'impact': 'High (Fault-Tolerance & Resilience)'}, {'category': 'Memory-Constrained Systems & Sensor Networks', 'title': 'Evaluate Iterative Deepening (IDDFS) for Extreme Scale or Tiny RAM', 'recommendation': "When operating in resource-starved IoT microcontrollers (e.g., 2KB-8KB RAM Zigbee/LoRa nodes) or graphs with massive branching factors where BFS queue storage O(b^d) threatens to exhaust system memory, use Iterative Deepening Search (IDDFS). IDDFS provides BFS's shortest-path guarantee while using only DFS's O(d) memory.", 'applicable_algo': 'IDDFS (Hybrid)', 'impact': 'Medium (Memory Optimization)'}, {'category': 'Network Protection & Resource Guardrails', 'title': 'Enforce Time-To-Live (TTL) & Hop-Count Guardrails', 'recommendation': 'Both graph-based routing algorithms and distributed table forwarding must strictly enforce an IP Header TTL (Time-To-Live) / Hop Limit field. If transient topological flapping causes a routing loop, the decremented TTL ensures packets are discarded before consuming link capacity.', 'applicable_algo': 'Network Layer Protocol', 'impact': 'Critical (Prevents Congestion Collapse)'}]
    scenario_guide = [{'scenario': 'Unweighted Shortest-Hop Packet Routing (LAN / Data Center switching)', 'best_choice': 'BFS (Breadth-First Search)', 'rationale': 'FIFO queue explores level-by-level; provably guarantees minimum forwarding hops.', 'complexity': 'Time: O(V + E) | Space: O(V)', 'industry_example': 'Layer-2 Spanning Tree shortest path, Software-Defined Network (SDN) Controller route provisioning.'}, {'scenario': 'Weighted Latency / Cost Metric Routing (Internet Core & Enterprise WAN)', 'best_choice': 'Dijkstra (Weighted BFS with Min-Priority Queue)', 'rationale': 'Generalizes BFS from unweighted unit hops to variable bandwidth, delay, and financial cost link weights.', 'complexity': 'Time: O((V + E) log V) | Space: O(V)', 'industry_example': 'OSPF (Open Shortest Path First), IS-IS (Intermediate System to Intermediate System).'}, {'scenario': 'Topology Loop & Cycle Detection', 'best_choice': 'DFS (Depth-First Search)', 'rationale': 'Recursion stack instantly flags back-edges to ancestors in O(V + E) time without exploring unnecessary branches.', 'complexity': 'Time: O(V + E) | Space: O(V)', 'industry_example': 'Ethernet STP (802.1D Spanning Tree Protocol), BGP AS-Path loop suppression.'}, {'scenario': 'Critical Single Point of Failure (SPOF) Identification', 'best_choice': "DFS (Tarjan's Articulation Points & Bridges Algorithm)", 'rationale': 'Tracks discovery times and lowest reachable ancestor times (low values) to find routers whose severance isolates subnets.', 'complexity': 'Time: O(V + E) | Space: O(V)', 'industry_example': 'Network reliability auditor, automated disaster-recovery redundancy analyzers.'}, {'scenario': 'Firewall Rule Chaining & Network Task Dependency Ordering', 'best_choice': 'DFS (Topological Sort)', 'rationale': 'Produces a linear sequence where every predecessor rule or virtual network function precedes its consumer.', 'complexity': 'Time: O(V + E) | Space: O(V)', 'industry_example': 'Kubernetes service dependency graphs, Linux iptables policy compiler.'}, {'scenario': 'Memory-Constrained Wireless Sensor Networks (IoT microcontrollers)', 'best_choice': 'IDDFS (Iterative Deepening Search) or DFS Reachability', 'rationale': 'Maintains stack size proportional to maximum depth O(d), preventing RAM out-of-memory crashes on embedded nodes.', 'complexity': 'Time: O(b^d) | Space: O(d)', 'industry_example': 'Zigbee/Thread mesh route discovery under 4KB RAM budgets.'}]
    return {'source': src_clean, 'destination': dst_clean, 'both_success': both_success, 'same_path': same_path, 'bfs': bfs_res, 'dfs': dfs_res, 'bfs_hops': bfs_hops, 'dfs_hops': dfs_hops, 'hop_delta': hop_delta, 'bfs_visited_count': bfs_visited_count, 'dfs_visited_count': dfs_visited_count, 'bfs_coverage_pct': bfs_coverage_pct, 'dfs_coverage_pct': dfs_coverage_pct, 'verdict_title': verdict_title, 'verdict_badge': verdict_badge, 'verdict_color': verdict_color, 'winner': winner, 'verdict_summary': verdict_summary, 'suggestions': suggestions, 'scenario_guide': scenario_guide}

def generate_simulation_report(graph: Graph, res: Optional[Dict[str, Any]], src: str, dst: str, algo_name: Optional[str]=None, topology_name: str='', **kwargs: Any) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    if res is None:
        res = {}
    algo_label = algo_name or res.get('algorithm', 'Graph Traversal')
    success = bool(res.get('success', False))
    path = list(res.get('path', []))
    hops = int(res.get('hops', 0))
    visited = list(res.get('visited', []))
    parents = {k: v for k, v in res.get('parents', {}).items()}
    steps_clean = []
    for s in res.get('steps', []):
        steps_clean.append({'step': s.get('step'), 'operation': s.get('operation'), 'current_node': s.get('current_node'), 'structure': list(s.get('structure', [])), 'front': s.get('front'), 'rear': s.get('rear'), 'top': s.get('top'), 'action_target': s.get('action_target'), 'visited': list(s.get('visited', [])), 'active_edge': list(s.get('active_edge')) if s.get('active_edge') else None, 'description': s.get('description')})
    return {'schema_version': '1.0.0', 'project': 'NetRoute — Network Packet Routing Simulator', 'generated_at': now_iso, 'endpoints': {'source': src, 'destination': dst}, 'algorithm': algo_label, 'status': 'SUCCESS' if success else 'NO_ROUTE_FOUND', 'result_message': res.get('message', ''), 'route': {'path': path, 'hop_count': hops, 'path_string': ' -> '.join(path) if path else 'None'}, 'metrics': {'execution_time_ms': round(float(res.get('execution_time_ms', 0.0)), 4), 'total_simulation_steps': len(steps_clean), 'visited_routers_count': len(visited), 'explored_edges_count': int(res.get('explored_edges_count', 0)), 'max_data_structure_depth': int(res.get('max_structure', 0)), 'enqueues_or_pushes': int(res.get('total_enqueues', res.get('total_pushes', 0))), 'dequeues_or_pops': int(res.get('total_dequeues', res.get('total_pops', 0)))}, 'traversal_order': visited, 'parent_mapping': parents, 'theoretical_complexity': {'time_complexity': 'O(V + E) for adjacency list representation', 'auxiliary_space_complexity': 'O(V) for visited set and traversal queue/stack'}, 'topology_snapshot': graph.to_dict(), 'step_by_step_trace': steps_clean}

def generate_comparison_report(graph: Graph, cmp_res: Dict[str, Any], src: str, dst: str, **kwargs: Any) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    bfs_res = cmp_res.get('bfs', {})
    dfs_res = cmp_res.get('dfs', {})
    return {'schema_version': '1.0.0', 'project': 'NetRoute — Network Packet Routing Simulator', 'report_type': 'DUAL_ALGORITHM_COMPARISON', 'generated_at': now_iso, 'endpoints': {'source': src, 'destination': dst}, 'topology_snapshot': graph.to_dict(), 'comparison_summary': {'verdict_title': cmp_res.get('verdict_title', ''), 'verdict_badge': cmp_res.get('verdict_badge', ''), 'winner': cmp_res.get('winner', ''), 'verdict_summary': cmp_res.get('verdict_summary', ''), 'both_success': cmp_res.get('both_success', False), 'same_path': cmp_res.get('same_path', False), 'hop_delta': cmp_res.get('hop_delta', 0), 'bfs_hops': cmp_res.get('bfs_hops', 0), 'dfs_hops': cmp_res.get('dfs_hops', 0)}, 'bfs_run': generate_simulation_report(graph, bfs_res, src, dst), 'dfs_run': generate_simulation_report(graph, dfs_res, src, dst), 'theoretical_complexity': {'bfs': {'time': 'O(V + E)', 'space': 'O(V)', 'property': 'Minimum hop guarantee in unweighted graphs'}, 'dfs': {'time': 'O(V + E)', 'space': 'O(V)', 'property': 'Exhaustive depth traversal; no shortest hop guarantee'}}}

def dijkstra(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    start_time = time.perf_counter()
    src, dst = (src.strip().upper(), dst.strip().upper())
    if not graph.routers:
        return {'algorithm': 'Dijkstra (Min-Priority Queue)', 'success': False, 'message': 'Network graph is empty.', 'path': [], 'hops': 0, 'path_cost': 0.0, 'steps': [], 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0, 'time_complexity': 'O((V + E) log V)', 'space_complexity': 'O(V)'}
    if src not in graph.routers or dst not in graph.routers:
        return {'algorithm': 'Dijkstra (Min-Priority Queue)', 'success': False, 'message': f"Endpoint router '{src}' or '{dst}' does not exist in the network.", 'path': [], 'hops': 0, 'path_cost': 0.0, 'steps': [], 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0, 'time_complexity': 'O((V + E) log V)', 'space_complexity': 'O(V)'}
    if not graph.routers[src].is_online or not graph.routers[dst].is_online:
        offline_node = src if not graph.routers[src].is_online else dst
        return {'algorithm': 'Dijkstra (Min-Priority Queue)', 'success': False, 'message': f"Router '{offline_node}' is OFFLINE. Cannot transmit packets.", 'path': [], 'hops': 0, 'path_cost': 0.0, 'steps': [], 'visited': [], 'parents': {}, 'tree_edges': [], 'max_structure': 0, 'total_pushes': 0, 'total_pops': 0, 'explored_edges_count': 0, 'execution_time_ms': 0.0, 'time_complexity': 'O((V + E) log V)', 'space_complexity': 'O(V)'}
    for (u, v), w in graph.weights.items():
        if w < 0.0:
            raise ValueError(f'Unsupported negative edge weight ({w}) detected on link ({u} <-> {v}). Dijkstra requires non-negative edge weights.')
    steps: List[Dict[str, Any]] = []
    if src == dst:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        steps.append({'step': 1, 'operation': 'COMPLETE', 'current_node': src, 'neighbor': None, 'neighbor_visited': False, 'neighbor_status': 'source_match', 'why': f"Source router '{src}' is identical to destination. Direct match with 0 hops and 0.0 cost.", 'structure': [src], 'structure_before': [], 'structure_after': [src], 'front': src, 'rear': src, 'action_target': src, 'enqueues': 1, 'dequeues': 0, 'max_structure': 1, 'visited': [src], 'parents': {src: None}, 'parent_assigned': None, 'current_path': [src], 'active_edge': None, 'description': f"Source router '{src}' is identical to destination. Direct match with 0 hops and 0.0 cost."})
        return {'algorithm': 'Dijkstra (Min-Priority Queue)', 'success': True, 'path': [src], 'hops': 0, 'path_cost': 0.0, 'steps': steps, 'visited': [src], 'parents': {src: None}, 'tree_edges': [], 'distances': {src: 0.0}, 'max_structure': 1, 'total_pushes': 1, 'total_pops': 0, 'explored_edges_count': 0, 'execution_time_ms': elapsed, 'time_complexity': 'O((V + E) log V)', 'space_complexity': 'O(V)', 'message': f"Direct route to '{src}' (0 hops, cost 0.0)."}
    pq: List[Tuple[float, str]] = [(0.0, src)]
    dist: Dict[str, float] = {r: float('inf') for r in graph.routers if graph.routers[r].is_online}
    dist[src] = 0.0
    parents: Dict[str, Optional[str]] = {src: None}
    visited: Set[str] = set()
    visited_order: List[str] = []
    tree_edges: List[Tuple[str, str]] = []
    explored_edges_set: Set[Tuple[str, str]] = set()
    total_pushes = 1
    total_pops = 0
    max_pq_size = 1
    steps.append({'step': len(steps) + 1, 'operation': 'ENQUEUE', 'current_node': src, 'neighbor': None, 'neighbor_visited': False, 'neighbor_status': 'source_init', 'why': f"Initialized Min-Priority Queue. Enqueued source router '{src}' with tentative distance 0.0.", 'structure': [item[1] for item in pq], 'structure_before': [], 'structure_after': [item[1] for item in pq], 'front': src, 'rear': src, 'action_target': src, 'enqueues': total_pushes, 'dequeues': total_pops, 'max_structure': max_pq_size, 'visited': [], 'parents': dict(parents), 'parent_assigned': None, 'current_path': [src], 'active_edge': None, 'description': f"Initialized Min-Priority Queue with source router '{src}' (distance 0.0)."})
    found = False
    while pq:
        struct_before_pop = [item[1] for item in pq]
        d, curr = heapq.heappop(pq)
        total_pops += 1
        if curr in visited:
            continue
        visited.add(curr)
        visited_order.append(curr)
        steps.append({'step': len(steps) + 1, 'operation': 'DEQUEUE', 'current_node': curr, 'neighbor': None, 'neighbor_visited': None, 'neighbor_status': None, 'why': f"Extracted router '{curr}' from priority queue with minimum tentative distance {d:.1f}. Examining outgoing links.", 'structure': [item[1] for item in pq], 'structure_before': struct_before_pop, 'structure_after': [item[1] for item in pq], 'front': pq[0][1] if pq else None, 'rear': pq[-1][1] if pq else None, 'action_target': curr, 'enqueues': total_pushes, 'dequeues': total_pops, 'max_structure': max_pq_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(curr), 'current_path': reconstruct_route_from_parents(parents, curr), 'active_edge': None, 'description': f"Extracted router '{curr}' from priority queue (min distance: {d:.1f})."})
        if curr == dst:
            found = True
            steps.append({'step': len(steps) + 1, 'operation': 'DESTINATION_FOUND', 'current_node': curr, 'neighbor': None, 'neighbor_visited': False, 'neighbor_status': 'target_reached', 'why': f"Destination router '{dst}' extracted with confirmed minimal cost of {d:.1f}!", 'structure': [item[1] for item in pq], 'structure_before': [item[1] for item in pq], 'structure_after': [item[1] for item in pq], 'front': pq[0][1] if pq else None, 'rear': pq[-1][1] if pq else None, 'action_target': curr, 'enqueues': total_pushes, 'dequeues': total_pops, 'max_structure': max_pq_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(curr), 'current_path': reconstruct_route_from_parents(parents, dst), 'active_edge': None, 'description': f"Destination router '{dst}' reached with minimal cost {d:.1f}."})
            break
        for nbr in sorted(graph.adjacency.get(curr, [])):
            if nbr not in graph.routers or not graph.routers[nbr].is_online:
                continue
            if not graph.is_edge_active(curr, nbr):
                continue
            edge_pair = tuple(sorted((curr, nbr)))
            explored_edges_set.add(edge_pair)
            weight = graph.get_weight(curr, nbr)
            if nbr in visited:
                continue
            new_dist = d + weight
            if new_dist < dist.get(nbr, float('inf')):
                struct_pre_push = [item[1] for item in pq]
                dist[nbr] = new_dist
                parents[nbr] = curr
                tree_edges.append((curr, nbr))
                heapq.heappush(pq, (new_dist, nbr))
                total_pushes += 1
                max_pq_size = max(max_pq_size, len(pq))
                steps.append({'step': len(steps) + 1, 'operation': 'ENQUEUE', 'current_node': nbr, 'neighbor': nbr, 'neighbor_visited': False, 'neighbor_status': 'relaxed', 'why': f"Relaxed link ({curr} <-> {nbr}) with weight {weight:.1f}. Updated tentative distance to '{nbr}' to {new_dist:.1f} (predecessor = '{curr}').", 'structure': [item[1] for item in pq], 'structure_before': struct_pre_push, 'structure_after': [item[1] for item in pq], 'front': pq[0][1] if pq else None, 'rear': pq[-1][1] if pq else None, 'action_target': nbr, 'enqueues': total_pushes, 'dequeues': total_pops, 'max_structure': max_pq_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': curr, 'current_path': reconstruct_route_from_parents(parents, nbr), 'active_edge': (curr, nbr), 'description': f"Relaxed edge ({curr} -> {nbr}) [wt: {weight:.1f}]. New distance to '{nbr}': {new_dist:.1f}."})
    elapsed = (time.perf_counter() - start_time) * 1000.0
    if not found or dst not in parents:
        steps.append({'step': len(steps) + 1, 'operation': 'FAILED', 'current_node': None, 'neighbor': None, 'neighbor_visited': None, 'neighbor_status': None, 'why': f"Priority queue exhausted. Destination '{dst}' is unreachable from '{src}'.", 'structure': [], 'structure_before': [], 'structure_after': [], 'front': None, 'rear': None, 'action_target': None, 'enqueues': total_pushes, 'dequeues': total_pops, 'max_structure': max_pq_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': None, 'current_path': [], 'active_edge': None, 'description': f"Priority queue exhausted. Destination '{dst}' is unreachable from '{src}'."})
        return {'algorithm': 'Dijkstra (Min-Priority Queue)', 'success': False, 'path': [], 'hops': 0, 'path_cost': 0.0, 'steps': steps, 'visited': visited_order, 'parents': parents, 'tree_edges': tree_edges, 'distances': {k: v for k, v in dist.items() if math.isfinite(v)}, 'max_structure': max_pq_size, 'total_pushes': total_pushes, 'total_pops': total_pops, 'explored_edges_count': len(explored_edges_set), 'execution_time_ms': elapsed, 'time_complexity': 'O((V + E) log V)', 'space_complexity': 'O(V)', 'message': f"No reachable path from '{src}' to '{dst}'."}
    path = reconstruct_route_from_parents(parents, dst)
    path_cost = dist[dst]
    hops = len(path) - 1
    steps.append({'step': len(steps) + 1, 'operation': 'COMPLETE', 'current_node': dst, 'neighbor': None, 'neighbor_visited': None, 'neighbor_status': None, 'why': f"Dijkstra least-cost path confirmed: {' -> '.join(path)} (cost {path_cost:.1f}, {hops} hops).", 'structure': [item[1] for item in pq], 'structure_before': [item[1] for item in pq], 'structure_after': [item[1] for item in pq], 'front': pq[0][1] if pq else None, 'rear': pq[-1][1] if pq else None, 'action_target': dst, 'enqueues': total_pushes, 'dequeues': total_pops, 'max_structure': max_pq_size, 'visited': list(visited_order), 'parents': dict(parents), 'parent_assigned': parents.get(dst), 'current_path': path, 'active_edge': None, 'description': f"Least-cost path reconstructed: {' -> '.join(path)} (cost {path_cost:.1f}, {hops} hops)."})
    return {'algorithm': 'Dijkstra (Min-Priority Queue)', 'success': True, 'path': path, 'hops': hops, 'path_cost': round(path_cost, 2), 'steps': steps, 'visited': visited_order, 'parents': parents, 'tree_edges': tree_edges, 'distances': {k: v for k, v in dist.items() if math.isfinite(v)}, 'max_structure': max_pq_size, 'total_pushes': total_pushes, 'total_pops': total_pops, 'explored_edges_count': len(explored_edges_set), 'execution_time_ms': elapsed, 'time_complexity': 'O((V + E) log V)', 'space_complexity': 'O(V)', 'message': f"Least-cost route discovered: {' -> '.join(path)} ({hops} hops, total cost {path_cost:.1f})."}

def find_bridges(graph: Graph) -> List[Tuple[str, str]]:
    tin: Dict[str, int] = {}
    low: Dict[str, int] = {}
    visited: Set[str] = set()
    timer = 0
    bridges: List[Tuple[str, str]] = []
    online_routers = {rid for rid, r in graph.routers.items() if r.is_online}

    def dfs_bridge(u: str, parent: Optional[str]=None):
        nonlocal timer
        visited.add(u)
        tin[u] = low[u] = timer
        timer += 1
        for v in sorted(graph.adjacency.get(u, [])):
            if v not in online_routers or not graph.is_edge_active(u, v):
                continue
            if v == parent:
                continue
            if v in visited:
                low[u] = min(low[u], tin[v])
            else:
                dfs_bridge(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > tin[u]:
                    pair = tuple(sorted((u, v)))
                    bridges.append(pair)
    for r in sorted(online_routers):
        if r not in visited:
            dfs_bridge(r)
    return sorted(list(set(bridges)))

def find_articulation_points(graph: Graph) -> List[str]:
    tin: Dict[str, int] = {}
    low: Dict[str, int] = {}
    visited: Set[str] = set()
    timer = 0
    is_ap: Set[str] = set()
    online_routers = {rid for rid, r in graph.routers.items() if r.is_online}

    def dfs_ap(u: str, parent: Optional[str]=None):
        nonlocal timer
        visited.add(u)
        tin[u] = low[u] = timer
        timer += 1
        children = 0
        for v in sorted(graph.adjacency.get(u, [])):
            if v not in online_routers or not graph.is_edge_active(u, v):
                continue
            if v == parent:
                continue
            if v in visited:
                low[u] = min(low[u], tin[v])
            else:
                children += 1
                dfs_ap(v, u)
                low[u] = min(low[u], low[v])
                if parent is not None and low[v] >= tin[u]:
                    is_ap.add(u)
        if parent is None and children > 1:
            is_ap.add(u)
    for r in sorted(online_routers):
        if r not in visited:
            dfs_ap(r)
    return sorted(list(is_ap))

def simulate_failure(graph: Graph, failed_routers: Optional[List[str]]=None, failed_edges: Optional[List[Tuple[str, str]]]=None, src: Optional[str]=None, dst: Optional[str]=None) -> Dict[str, Any]:
    failed_routers = [r.strip().upper() for r in failed_routers or [] if r.strip().upper() in graph.routers]
    clean_failed_edges: List[Tuple[str, str]] = []
    for edge in failed_edges or []:
        if len(edge) >= 2:
            u, v = (str(edge[0]).strip().upper(), str(edge[1]).strip().upper())
            if u in graph.routers and v in graph.routers:
                clean_failed_edges.append(tuple(sorted((u, v))))
    base_comps = graph.get_connected_components()
    base_bridges = find_bridges(graph)
    base_aps = find_articulation_points(graph)
    base_bfs = bfs(graph, src, dst) if src and dst else None
    base_dfs = dfs(graph, src, dst) if src and dst else None
    base_dijkstra = dijkstra(graph, src, dst) if src and dst else None
    scen_graph = graph.clone()
    scen_graph.name = f'{graph.name} (Simulated Failure Scenario)'
    for r in failed_routers:
        if r in scen_graph.routers:
            scen_graph.routers[r].is_online = False
    for u, v in clean_failed_edges:
        scen_graph.failed_edges.add((u, v))
    fail_comps = scen_graph.get_connected_components()
    fail_bridges = find_bridges(scen_graph)
    fail_aps = find_articulation_points(scen_graph)
    fail_bfs = bfs(scen_graph, src, dst) if src and dst else None
    fail_dfs = dfs(scen_graph, src, dst) if src and dst else None
    fail_dijkstra = dijkstra(scen_graph, src, dst) if src and dst else None
    reachable_before = set(graph.get_reachable_nodes(src)) if src else set()
    reachable_after = set(scen_graph.get_reachable_nodes(src)) if src else set()
    disconnected_nodes = sorted(list(reachable_before - reachable_after))
    route_survived = bool(fail_bfs and fail_bfs.get('success', False))
    return {'timestamp': datetime.now(timezone.utc).isoformat(), 'original_topology_name': graph.name, 'failed_routers': failed_routers, 'failed_edges': clean_failed_edges, 'endpoints': {'source': src, 'destination': dst}, 'baseline': {'component_count': len(base_comps), 'components': [sorted(list(c)) for c in base_comps], 'bridges': base_bridges, 'articulation_points': base_aps, 'bfs': base_bfs, 'dfs': base_dfs, 'dijkstra': base_dijkstra}, 'failure_scenario': {'component_count': len(fail_comps), 'components': [sorted(list(c)) for c in fail_comps], 'bridges': fail_bridges, 'articulation_points': fail_aps, 'bfs': fail_bfs, 'dfs': fail_dfs, 'dijkstra': fail_dijkstra}, 'impact_analysis': {'component_delta': len(fail_comps) - len(base_comps), 'route_survived': route_survived, 'destination_became_unreachable': bool(base_bfs and base_bfs.get('success') and (not route_survived)), 'hop_delta': fail_bfs.get('hops', 0) - base_bfs.get('hops', 0) if base_bfs and fail_bfs and base_bfs.get('success') and fail_bfs.get('success') else None, 'cost_delta': fail_dijkstra.get('path_cost', 0.0) - base_dijkstra.get('path_cost', 0.0) if base_dijkstra and fail_dijkstra and base_dijkstra.get('success') and fail_dijkstra.get('success') else None, 'disconnected_routers': disconnected_nodes}, 'scenario_graph': scen_graph}

def generate_benchmark_graph(num_routers: int, density: float=0.3, seed: Optional[int]=42) -> Graph:
    rng = random.Random(seed)
    n = max(3, int(num_routers))
    g = Graph(name=f'Benchmark_{n}N_{int(density * 100)}D')
    cx, cy = (400.0, 250.0)
    radius = min(220.0, max(80.0, 20.0 * n))
    for i in range(1, n + 1):
        rid = f'N{i}'
        angle = 2 * math.pi * (i - 1) / n - math.pi / 2
        x = round(cx + radius * math.cos(angle), 1)
        y = round(cy + radius * math.sin(angle), 1)
        g.add_router(rid, name=f'Node {rid}', x=x, y=y)
    nodes = [f'N{i}' for i in range(1, n + 1)]
    for i in range(1, n):
        parent_idx = rng.randint(0, i - 1)
        u = nodes[i]
        v = nodes[parent_idx]
        wt = round(rng.uniform(1.0, 10.0), 1)
        g.add_connection(u, v, weight=wt)
    existing_edges = set(g.get_edges())
    all_possible = []
    for i in range(n):
        for j in range(i + 1, n):
            pair = tuple(sorted((nodes[i], nodes[j])))
            if pair not in existing_edges:
                all_possible.append(pair)
    rng.shuffle(all_possible)
    max_extra = len(all_possible)
    num_extra = int(max_extra * max(0.0, min(1.0, density)))
    for u, v in all_possible[:num_extra]:
        wt = round(rng.uniform(1.0, 10.0), 1)
        g.add_connection(u, v, weight=wt)
    return g

def benchmark_algorithm(algo_name: str, graph: Graph, src: str, dst: str, repetitions: int=5) -> Dict[str, Any]:
    algo_clean = algo_name.strip().upper()
    timings_ms: List[float] = []
    result: Optional[Dict[str, Any]] = None
    for _ in range(max(1, repetitions)):
        t0 = time.perf_counter()
        if 'BFS' in algo_clean:
            res = bfs(graph, src, dst)
        elif 'DFS' in algo_clean:
            res = dfs(graph, src, dst)
        elif 'DIJKSTRA' in algo_clean:
            res = dijkstra(graph, src, dst)
        else:
            res = bfs(graph, src, dst)
        t1 = time.perf_counter()
        timings_ms.append((t1 - t0) * 1000.0)
        result = res
    mean_ms = sum(timings_ms) / len(timings_ms)
    min_ms = min(timings_ms)
    max_ms = max(timings_ms)
    variance = sum(((x - mean_ms) ** 2 for x in timings_ms)) / len(timings_ms)
    std_ms = math.sqrt(variance)
    return {'algorithm': algo_name, 'repetitions': max(1, repetitions), 'mean_time_ms': round(mean_ms, 4), 'min_time_ms': round(min_ms, 4), 'max_time_ms': round(max_ms, 4), 'std_time_ms': round(std_ms, 4), 'success': result.get('success', False) if result else False, 'hops': result.get('hops', 0) if result else 0, 'path_cost': result.get('path_cost', 0.0) if result else 0.0, 'visited_count': len(result.get('visited', [])) if result else 0, 'explored_edges_count': result.get('explored_edges_count', 0) if result else 0, 'route_str': ' -> '.join(result.get('path', [])) if result and result.get('path') else 'No Route'}

def run_benchmark_suite(router_counts: List[int], density: float=0.3, algos: Optional[List[str]]=None, repetitions: int=5, seed: int=42) -> Dict[str, Any]:
    algos = algos or ['BFS', 'DFS', 'Dijkstra']
    records: List[Dict[str, Any]] = []
    for n in sorted(router_counts):
        g = generate_benchmark_graph(num_routers=n, density=density, seed=seed)
        src = 'N1'
        dst = f'N{n}'
        for algo in algos:
            bench = benchmark_algorithm(algo, g, src, dst, repetitions=repetitions)
            records.append({'routers': n, 'edges': len(g.get_edges()), 'density': round(density, 2), 'algorithm': algo, 'mean_time_ms': bench['mean_time_ms'], 'min_time_ms': bench['min_time_ms'], 'max_time_ms': bench['max_time_ms'], 'std_time_ms': bench['std_time_ms'], 'hops': bench['hops'], 'path_cost': bench['path_cost'], 'visited_count': bench['visited_count'], 'explored_edges': bench['explored_edges_count'], 'theoretical_time': 'O(V + E)' if algo in ('BFS', 'DFS') else 'O((V + E) log V)', 'theoretical_space': 'O(V)'})
    return {'timestamp': datetime.now(timezone.utc).isoformat(), 'seed': seed, 'density': density, 'repetitions': repetitions, 'algorithms': algos, 'scales': router_counts, 'records': records}

def compare_routing_strategies(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    bfs_res = bfs(graph, src, dst)
    dfs_res = dfs(graph, src, dst)
    dijkstra_res = dijkstra(graph, src, dst)
    return {'source': src, 'destination': dst, 'bfs': bfs_res, 'dfs': dfs_res, 'dijkstra': dijkstra_res, 'bfs_hops': bfs_res.get('hops', 0), 'dfs_hops': dfs_res.get('hops', 0), 'dijkstra_hops': dijkstra_res.get('hops', 0), 'dijkstra_cost': dijkstra_res.get('path_cost', 0.0), 'bfs_cost': bfs_res.get('path_cost', 0.0), 'dfs_cost': dfs_res.get('path_cost', 0.0), 'verdict': 'BFS finds the minimum hops for unweighted links. Dijkstra finds the minimum total cost for weighted links. DFS explores branch depths without hop or cost optimality guarantees.'}