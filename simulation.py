from typing import Dict, Any, Optional, Set, List, Tuple
from datetime import datetime, timezone
import streamlit as st
from network import Graph
from algorithms import bfs, dfs, compare_bfs_dfs, generate_simulation_report

def init_session():
    if 'graph' not in st.session_state:
        g = Graph()
        g.load_preset('reference')
        st.session_state['graph'] = g
    if 'selected_preset' not in st.session_state:
        st.session_state['selected_preset'] = 'reference'
    if 'nav_page' not in st.session_state:
        st.session_state['nav_page'] = 'Dashboard'
    if 'sim_res' not in st.session_state:
        st.session_state['sim_res'] = None
    if 'step_idx' not in st.session_state:
        st.session_state['step_idx'] = 0
    if 'is_playing' not in st.session_state:
        st.session_state['is_playing'] = False
    if 'packet_hop' not in st.session_state:
        st.session_state['packet_hop'] = 0
    if 'packet_auto' not in st.session_state:
        st.session_state['packet_auto'] = False
    if 'selected_algo' not in st.session_state:
        st.session_state['selected_algo'] = 'BFS (Breadth-First)'
    if 'search_res' not in st.session_state:
        st.session_state['search_res'] = None
    if 'search_step_idx' not in st.session_state:
        st.session_state['search_step_idx'] = 0
    if 'sort_res' not in st.session_state:
        st.session_state['sort_res'] = None
    if 'table_fwd_res' not in st.session_state:
        st.session_state['table_fwd_res'] = None
    if 'cmp_res' not in st.session_state:
        st.session_state['cmp_res'] = None
    if 'bfs_dfs_comp_res' not in st.session_state:
        st.session_state['bfs_dfs_comp_res'] = None
    if 'cmp_step_idx' not in st.session_state:
        st.session_state['cmp_step_idx'] = 0
    if 'cmp_is_playing' not in st.session_state:
        st.session_state['cmp_is_playing'] = False
    if 'cmp_is_paused' not in st.session_state:
        st.session_state['cmp_is_paused'] = False
    if 'cmp_speed' not in st.session_state:
        st.session_state['cmp_speed'] = 0.6
    if 'cmp_autoplay' not in st.session_state:
        st.session_state['cmp_autoplay'] = True
    if 'is_paused' not in st.session_state:
        st.session_state['is_paused'] = False
    if 'sim_speed' not in st.session_state:
        st.session_state['sim_speed'] = 0.6
    if 'sim_autoplay' not in st.session_state:
        st.session_state['sim_autoplay'] = True
    if 'simulation_history' not in st.session_state:
        st.session_state['simulation_history'] = []
    g_nodes = list(st.session_state['graph'].routers.keys())
    if 'source_id' not in st.session_state or st.session_state['source_id'] not in st.session_state['graph'].routers:
        st.session_state['source_id'] = 'N1' if 'N1' in st.session_state['graph'].routers else g_nodes[0] if g_nodes else 'N1'
    if 'dest_id' not in st.session_state or st.session_state['dest_id'] not in st.session_state['graph'].routers:
        st.session_state['dest_id'] = 'N7' if 'N7' in st.session_state['graph'].routers else g_nodes[-1] if g_nodes else 'N7'

def get_simulation_status() -> str:
    res = st.session_state.get('sim_res')
    if not res:
        return 'Ready'
    if st.session_state.get('is_playing', False):
        return 'Running'
    if not res.get('success', False):
        return 'No Route'
    steps = res.get('steps', [])
    if steps and st.session_state.get('step_idx', 0) == len(steps) - 1:
        return 'Completed'
    return 'Paused'

def invalidate_simulation():
    st.session_state['sim_res'] = None
    st.session_state['step_idx'] = 0
    st.session_state['is_playing'] = False
    st.session_state['is_paused'] = False
    st.session_state['packet_hop'] = 0
    st.session_state['packet_auto'] = False
    st.session_state['search_res'] = None
    st.session_state['search_step_idx'] = 0
    st.session_state['sort_res'] = None
    st.session_state['table_fwd_res'] = None
    st.session_state['bfs_dfs_comp_res'] = None
    st.session_state['cmp_res'] = None
    st.session_state['cmp_step_idx'] = 0
    st.session_state['cmp_is_playing'] = False
    st.session_state['cmp_is_paused'] = False
    st.session_state.pop('sim_scrubber', None)
    st.session_state.pop('cmp_scrubber', None)

def add_to_history(record: Dict[str, Any]):
    if 'simulation_history' not in st.session_state:
        st.session_state['simulation_history'] = []
    st.session_state['simulation_history'].insert(0, record)

def clear_history():
    st.session_state['simulation_history'] = []

def execute_routing(graph: Graph, algo: str, src: str, dst: str) -> Dict[str, Any]:
    algo_upper = algo.upper()
    if 'DIJKSTRA' in algo_upper:
        from algorithms import dijkstra
        res = dijkstra(graph, src, dst)
    elif 'DFS' in algo_upper:
        res = dfs(graph, src, dst)
    else:
        res = bfs(graph, src, dst)
    st.session_state['sim_res'] = res
    st.session_state['step_idx'] = 0
    st.session_state['is_playing'] = False
    st.session_state['packet_hop'] = 0
    st.session_state['packet_auto'] = False
    st.session_state.pop('sim_scrubber', None)
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    record = {'id': f'sim_{int(datetime.now(timezone.utc).timestamp())}', 'timestamp': now_str, 'type': 'Single Traversal', 'algorithm': res.get('algorithm', algo), 'source': src, 'destination': dst, 'success': res.get('success', False), 'path': list(res.get('path', [])), 'hops': res.get('hops', 0), 'visited_count': len(res.get('visited', [])), 'explored_edges_count': res.get('explored_edges_count', 0), 'steps_count': len(res.get('steps', [])), 'execution_time_ms': round(float(res.get('execution_time_ms', 0.0)), 4), 'topology_summary': graph.get_summary(), 'report': generate_simulation_report(graph, res, src, dst)}
    add_to_history(record)
    return res

def execute_dual_comparison(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    cmp_res = compare_bfs_dfs(graph, src, dst)
    st.session_state['cmp_res'] = cmp_res
    st.session_state['cmp_step_idx'] = 0
    st.session_state.pop('cmp_scrubber', None)
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    record = {'id': f'cmp_{int(datetime.now(timezone.utc).timestamp())}', 'timestamp': now_str, 'type': 'Dual Comparison (BFS vs DFS)', 'algorithm': 'BFS vs DFS', 'source': src, 'destination': dst, 'success': cmp_res.get('both_success', False), 'path': list(cmp_res.get('bfs', {}).get('path', [])), 'hops': cmp_res.get('bfs_hops', 0), 'visited_count': cmp_res.get('bfs_visited_count', 0), 'explored_edges_count': cmp_res.get('bfs', {}).get('explored_edges_count', 0), 'steps_count': max(len(cmp_res.get('bfs', {}).get('steps', [])), len(cmp_res.get('dfs', {}).get('steps', []))), 'execution_time_ms': round(float(cmp_res.get('bfs', {}).get('execution_time_ms', 0.0) + cmp_res.get('dfs', {}).get('execution_time_ms', 0.0)), 4), 'topology_summary': graph.get_summary(), 'verdict': cmp_res.get('verdict_badge', '')}
    add_to_history(record)
    return cmp_res

def cmp_play():
    cmp_res = st.session_state.get('cmp_res')
    if cmp_res:
        bfs_steps = len(cmp_res.get('bfs', {}).get('steps', []))
        dfs_steps = len(cmp_res.get('dfs', {}).get('steps', []))
        max_steps = max(bfs_steps, dfs_steps)
        if st.session_state.get('cmp_step_idx', 0) >= max_steps - 1:
            st.session_state['cmp_step_idx'] = 0
        st.session_state['cmp_is_playing'] = True
        st.session_state['cmp_is_paused'] = False

def cmp_pause():
    st.session_state['cmp_is_playing'] = False
    st.session_state['cmp_is_paused'] = True

def cmp_resume():
    st.session_state['cmp_is_playing'] = True
    st.session_state['cmp_is_paused'] = False

def cmp_restart():
    st.session_state['cmp_step_idx'] = 0
    st.session_state['cmp_is_playing'] = False
    st.session_state['cmp_is_paused'] = False

def cmp_run_to_completion():
    cmp_res = st.session_state.get('cmp_res')
    if cmp_res:
        bfs_steps = len(cmp_res.get('bfs', {}).get('steps', []))
        dfs_steps = len(cmp_res.get('dfs', {}).get('steps', []))
        max_steps = max(bfs_steps, dfs_steps)
        if max_steps > 0:
            st.session_state['cmp_step_idx'] = max_steps - 1
    st.session_state['cmp_is_playing'] = False
    st.session_state['cmp_is_paused'] = False

def cmp_step_forward():
    st.session_state['cmp_is_playing'] = False
    cmp_res = st.session_state.get('cmp_res')
    if cmp_res:
        bfs_steps = len(cmp_res.get('bfs', {}).get('steps', []))
        dfs_steps = len(cmp_res.get('dfs', {}).get('steps', []))
        max_steps = max(bfs_steps, dfs_steps)
        if max_steps > 0 and st.session_state.get('cmp_step_idx', 0) < max_steps - 1:
            st.session_state['cmp_step_idx'] += 1

def cmp_step_backward():
    st.session_state['cmp_is_playing'] = False
    if st.session_state.get('cmp_step_idx', 0) > 0:
        st.session_state['cmp_step_idx'] -= 1

def cmp_first_step():
    st.session_state['cmp_step_idx'] = 0
    st.session_state['cmp_is_playing'] = False

def cmp_last_step():
    st.session_state['cmp_is_playing'] = False
    cmp_res = st.session_state.get('cmp_res')
    if cmp_res:
        bfs_steps = len(cmp_res.get('bfs', {}).get('steps', []))
        dfs_steps = len(cmp_res.get('dfs', {}).get('steps', []))
        max_steps = max(bfs_steps, dfs_steps)
        if max_steps > 0:
            st.session_state['cmp_step_idx'] = max_steps - 1

def cmp_jump_to_step(idx: int):
    st.session_state['cmp_is_playing'] = False
    cmp_res = st.session_state.get('cmp_res')
    if cmp_res:
        bfs_steps = len(cmp_res.get('bfs', {}).get('steps', []))
        dfs_steps = len(cmp_res.get('dfs', {}).get('steps', []))
        max_steps = max(bfs_steps, dfs_steps)
        if max_steps > 0:
            st.session_state['cmp_step_idx'] = max(0, min(idx, max_steps - 1))

def cmp_reset():
    st.session_state['cmp_step_idx'] = 0
    st.session_state['cmp_is_playing'] = False
    st.session_state['cmp_is_paused'] = False

def sim_play():
    res = st.session_state.get('sim_res')
    if res and res.get('steps'):
        if st.session_state.get('step_idx', 0) >= len(res['steps']) - 1:
            st.session_state['step_idx'] = 0
        st.session_state['is_playing'] = True
        st.session_state['is_paused'] = False

def sim_pause():
    st.session_state['is_playing'] = False
    st.session_state['is_paused'] = True

def sim_resume():
    st.session_state['is_playing'] = True
    st.session_state['is_paused'] = False

def sim_restart():
    st.session_state['step_idx'] = 0
    st.session_state['is_playing'] = False
    st.session_state['is_paused'] = False

def sim_run_to_completion():
    res = st.session_state.get('sim_res')
    if res and res.get('steps'):
        st.session_state['step_idx'] = len(res['steps']) - 1
    st.session_state['is_playing'] = False
    st.session_state['is_paused'] = False

def step_forward():
    st.session_state['is_playing'] = False
    res = st.session_state.get('sim_res')
    if res and res.get('steps'):
        if st.session_state['step_idx'] < len(res['steps']) - 1:
            st.session_state['step_idx'] += 1

def step_backward():
    st.session_state['is_playing'] = False
    if st.session_state.get('step_idx', 0) > 0:
        st.session_state['step_idx'] -= 1

def first_step():
    st.session_state['step_idx'] = 0
    st.session_state['is_playing'] = False

def last_step():
    st.session_state['is_playing'] = False
    res = st.session_state.get('sim_res')
    if res and res.get('steps'):
        st.session_state['step_idx'] = len(res['steps']) - 1

def jump_to_step(idx: int):
    st.session_state['is_playing'] = False
    res = st.session_state.get('sim_res')
    if res and res.get('steps'):
        st.session_state['step_idx'] = max(0, min(idx, len(res['steps']) - 1))

def reset_playback():
    st.session_state['step_idx'] = 0
    st.session_state['is_playing'] = False
    st.session_state['is_paused'] = False

def reset_simulation():
    invalidate_simulation()

def packet_step_forward():
    res = st.session_state.get('sim_res')
    if res and res.get('success') and res.get('path'):
        path = res['path']
        curr_hop = st.session_state.get('packet_hop', 0)
        if curr_hop < len(path) - 1:
            st.session_state['packet_hop'] = curr_hop + 1

def reset_packet():
    st.session_state['packet_hop'] = 0
    st.session_state['packet_auto'] = False

def get_step_visual_state(graph: Graph, res: Optional[Dict[str, Any]], step_idx: int) -> Dict[str, Any]:
    if not res or not res.get('steps'):
        return {'step': None, 'res': res, 'is_completed': False, 'active_node': None, 'active_edge': None, 'action_target': None, 'visited_nodes': set(), 'visited_sequence': [], 'explored_edges': set(), 'tree_edges': [], 'route_nodes': set(), 'route_edges': [], 'packet_node': None, 'next_packet_node': None, 'packet_status': 'No active simulation.'}
    steps = res['steps']
    tot_steps = len(steps)
    idx = max(0, min(step_idx, tot_steps - 1))
    current_step = steps[idx]
    is_completed = idx == tot_steps - 1
    active_node = current_step.get('current_node')
    active_edge = current_step.get('active_edge')
    action_target = current_step.get('action_target')
    visited_sequence = list(current_step.get('visited', []))
    visited_nodes: Set[str] = set(visited_sequence)
    if active_node and active_node in graph.routers:
        visited_nodes.add(active_node)
    explored_edges: Set[Tuple[str, str]] = set()
    for s in steps[:idx + 1]:
        if s.get('active_edge'):
            explored_edges.add(tuple(sorted(s['active_edge'])))
    tree_edges: List[Tuple[str, str]] = []
    for child, par in current_step.get('parents', {}).items():
        if par is not None:
            tree_edges.append(tuple(sorted((par, child))))
    route_nodes: Set[str] = set()
    route_edges: List[Tuple[str, str]] = []
    if res.get('success') and res.get('path') and is_completed:
        path = res['path']
        route_nodes = set(path)
        for i in range(len(path) - 1):
            route_edges.append(tuple(sorted((path[i], path[i + 1]))))
    return {'step': current_step, 'res': res, 'is_completed': is_completed, 'active_node': active_node, 'active_edge': active_edge, 'action_target': action_target, 'visited_nodes': visited_nodes, 'visited_sequence': visited_sequence, 'explored_edges': explored_edges, 'tree_edges': tree_edges, 'route_nodes': route_nodes, 'route_edges': route_edges, 'packet_node': active_node, 'next_packet_node': None, 'packet_status': 'Simulation in progress.' if not is_completed else 'Traversal finished.'}

def get_active_state(graph: Graph) -> Dict[str, Any]:
    res = st.session_state.get('sim_res')
    step_idx = st.session_state.get('step_idx', 0)
    state = get_step_visual_state(graph, res, step_idx)
    if res and res.get('success') and res.get('path'):
        path = res['path']
        p_hop = st.session_state.get('packet_hop', 0)
        if 0 <= p_hop < len(path):
            packet_node = path[p_hop]
            next_packet_node = path[p_hop + 1] if p_hop + 1 < len(path) else None
            if not graph.routers.get(packet_node) or not graph.routers[packet_node].is_online:
                packet_status = f"Transmission BLOCKED: Router '{packet_node}' is offline."
            elif p_hop == 0:
                packet_status = f"Packet buffered at Source '{packet_node}' (Hop 0). Ready for transmission."
            elif p_hop == len(path) - 1:
                packet_status = f"Packet DELIVERED to Destination '{packet_node}' in {len(path) - 1} hops."
            else:
                packet_status = f"In Transit: Hop {p_hop}/{len(path) - 1} | At '{packet_node}' -> Next: '{next_packet_node}'"
            state['packet_node'] = packet_node
            state['next_packet_node'] = next_packet_node
            state['packet_status'] = packet_status
    elif state.get('active_node'):
        state['packet_node'] = state.get('active_node')
    return state

def simulate_table_forwarding(graph: Graph, src: str, dst: str, max_hops: int=25) -> Dict[str, Any]:
    src_clean = str(src).strip().upper()
    dst_clean = str(dst).strip().upper()
    if not graph or not graph.routers:
        return {'success': False, 'status': 'EMPTY_GRAPH', 'path': [], 'hops': 0, 'steps': [], 'message': 'Network graph is empty.'}
    if src_clean not in graph.routers:
        return {'success': False, 'status': 'SOURCE_NOT_FOUND', 'path': [], 'hops': 0, 'steps': [], 'message': f"Source router '{src_clean}' does not exist in the network."}
    if dst_clean not in graph.routers:
        return {'success': False, 'status': 'DEST_NOT_FOUND', 'path': [], 'hops': 0, 'steps': [], 'message': f"Destination router '{dst_clean}' does not exist in the network."}
    if not graph.routers[src_clean].is_online:
        return {'success': False, 'status': 'SOURCE_OFFLINE', 'path': [src_clean], 'hops': 0, 'steps': [], 'message': f"Source router '{src_clean}' is offline. Cannot initiate packet transmission."}
    if not graph.routers[dst_clean].is_online:
        return {'success': False, 'status': 'DEST_OFFLINE', 'path': [src_clean], 'hops': 0, 'steps': [], 'message': f"Destination router '{dst_clean}' is offline."}
    if src_clean == dst_clean:
        return {'success': True, 'status': 'DELIVERED_LOCAL', 'path': [src_clean], 'hops': 0, 'steps': [{'step': 1, 'current_router': src_clean, 'next_hop': src_clean, 'action': 'LOCAL_DELIVERY', 'table_entry': {'destination': dst_clean, 'next_hop': src_clean, 'hops': 0, 'status': 'Local (Self)'}, 'description': f"Source '{src_clean}' is identical to destination. Packet processed locally."}], 'message': f"Packet processed locally at router '{src_clean}' (0 hops)."}
    curr = src_clean
    path: List[str] = [curr]
    steps: List[Dict[str, Any]] = []
    visited_set: Set[str] = {curr}
    step_num = 1
    success = False
    status = 'IN_PROGRESS'
    failure_message = ''
    while curr != dst_clean and step_num <= max_hops:
        curr_table = graph.generate_routing_table(curr)
        matching_entry = next((e for e in curr_table if e['destination'] == dst_clean), None)
        if not matching_entry or matching_entry['next_hop'] in ('None', None) or matching_entry['hops'] < 0:
            status = 'NO_ROUTE_TO_HOST'
            failure_message = f"Router '{curr}' routing table has NO ROUTE to destination '{dst_clean}'."
            steps.append({'step': step_num, 'current_router': curr, 'next_hop': 'None', 'action': 'FORWARDING_FAILED', 'table_entry': matching_entry or {'destination': dst_clean, 'next_hop': 'None', 'hops': -1, 'status': 'Unreachable'}, 'description': failure_message})
            break
        nxt = matching_entry['next_hop']
        if nxt not in graph.routers or not graph.routers[nxt].is_online:
            status = 'NEXT_HOP_OFFLINE'
            failure_message = f"Forwarding failure at '{curr}': Next Hop router '{nxt}' is offline."
            steps.append({'step': step_num, 'current_router': curr, 'next_hop': nxt, 'action': 'NEXT_HOP_DOWN', 'table_entry': matching_entry, 'description': failure_message})
            break
        if not graph.is_edge_active(curr, nxt):
            status = 'LINK_SEVERED'
            failure_message = f"Forwarding failure at '{curr}': Physical link ({curr} <-> {nxt}) is severed."
            steps.append({'step': step_num, 'current_router': curr, 'next_hop': nxt, 'action': 'LINK_DOWN', 'table_entry': matching_entry, 'description': failure_message})
            break
        if nxt in visited_set:
            status = 'ROUTING_LOOP'
            failure_message = f"Routing loop detected: packet forwarded back to visited router '{nxt}'."
            steps.append({'step': step_num, 'current_router': curr, 'next_hop': nxt, 'action': 'LOOP_DETECTED', 'table_entry': matching_entry, 'description': failure_message})
            break
        steps.append({'step': step_num, 'current_router': curr, 'next_hop': nxt, 'action': 'FORWARD', 'table_entry': matching_entry, 'description': f"Hop {step_num}: Router '{curr}' looked up destination '{dst_clean}' -> Next Hop '{nxt}' ({matching_entry['hops']} metric hops)."})
        curr = nxt
        path.append(curr)
        visited_set.add(curr)
        step_num += 1
        if curr == dst_clean:
            success = True
            status = 'DELIVERED'
            steps.append({'step': step_num, 'current_router': curr, 'next_hop': 'None', 'action': 'DELIVERY_COMPLETE', 'table_entry': {'destination': dst_clean, 'next_hop': curr, 'hops': 0, 'status': 'Delivered'}, 'description': f"Packet successfully reached destination router '{dst_clean}' in {len(path) - 1} hops."})
            break
    if not success and status == 'IN_PROGRESS':
        status = 'TTL_EXPIRED'
        failure_message = f'Forwarding terminated: exceeded maximum hop limit of {max_hops}.'
    hops_count = len(path) - 1 if len(path) > 1 else 0
    return {'success': success, 'status': status, 'path': path, 'hops': hops_count, 'steps': steps, 'final_router': curr, 'message': f"Table forwarding {('succeeded: ' + ' -> '.join(path) if success else 'failed: ' + failure_message)}"}
