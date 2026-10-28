import io
import csv
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from network import Graph

def generate_simulation_report(graph: Graph, sim_res: Optional[Dict[str, Any]], source: str, destination: str, algo_name: str='BFS', topology_name: str='') -> Dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    src_clean = str(source).strip().upper()
    dst_clean = str(destination).strip().upper()
    active_topo_name = topology_name.strip() or getattr(graph, 'name', '') or 'Active Network Topology'
    online_routers = [rid for rid, r in sorted(graph.routers.items()) if r.is_online]
    offline_routers = [rid for rid, r in sorted(graph.routers.items()) if not r.is_online]
    edges_with_weights = [[u, v, graph.get_weight(u, v)] for u, v in graph.get_edges()]
    failed_edges_list = [list(e) for e in sorted(graph.failed_edges)]
    topology_section = {'name': active_topo_name, 'router_count': len(graph.routers), 'connection_count': len(graph.get_edges()), 'online_routers_count': len(online_routers), 'offline_routers_count': len(offline_routers), 'online_routers': online_routers, 'offline_routers': offline_routers, 'failed_links_count': len(failed_edges_list), 'failed_edges': failed_edges_list, 'routers': [r.to_dict() for r in graph.routers.values()], 'edges': edges_with_weights}
    if not graph.routers or src_clean not in graph.routers or dst_clean not in graph.routers:
        status = 'invalid_input'
        route: List[str] = []
        hop_count = 0
        visited_order: List[str] = []
        parent_mapping: Dict[str, Optional[str]] = {}
        traversal_steps: List[Dict[str, Any]] = []
        queue_or_stack_states: List[Dict[str, Any]] = []
        explored_edges: List[List[str]] = []
        execution_time_ms = 0.0
        message = 'Simulation failed: source or destination router does not exist in the active graph.'
    elif not graph.routers[src_clean].is_online or not graph.routers[dst_clean].is_online:
        status = 'unreachable'
        route = []
        hop_count = 0
        visited_order = []
        parent_mapping = {}
        traversal_steps = []
        queue_or_stack_states = []
        explored_edges = []
        execution_time_ms = 0.0
        offline_node = src_clean if not graph.routers[src_clean].is_online else dst_clean
        message = f"Simulation terminated: router '{offline_node}' is offline."
    elif not sim_res:
        status = 'failed_execution'
        route = []
        hop_count = 0
        visited_order = []
        parent_mapping = {}
        traversal_steps = []
        queue_or_stack_states = []
        explored_edges = []
        execution_time_ms = 0.0
        message = 'No simulation execution data available.'
    else:
        is_success = bool(sim_res.get('success', False))
        if is_success:
            status = 'success'
            route = list(sim_res.get('path', []))
            hop_count = int(sim_res.get('hops', max(0, len(route) - 1)))
        else:
            status = 'unreachable'
            route = []
            hop_count = 0
        visited_order = list(sim_res.get('visited', []))
        parent_mapping = {k: v for k, v in sim_res.get('parents', {}).items()}
        steps = sim_res.get('steps', [])
        traversal_steps = steps
        execution_time_ms = round(float(sim_res.get('execution_time_ms', 0.0)), 4)
        message = str(sim_res.get('message', ''))
        queue_or_stack_states = []
        explored_set = set()
        for s in steps:
            q_state = {'step': s.get('step'), 'operation': s.get('operation'), 'current_node': s.get('current_node'), 'data_structure': s.get('structure', []), 'action_target': s.get('action_target')}
            queue_or_stack_states.append(q_state)
            if s.get('active_edge'):
                ae = tuple(sorted(s['active_edge']))
                explored_set.add(ae)
        explored_edges = [list(e) for e in sorted(explored_set)]
    is_dfs = 'DFS' in algo_name.upper()
    algo_label = 'DFS (Depth-First Search)' if is_dfs else 'BFS (Breadth-First Search)'
    if is_dfs:
        complexity = {'time': 'O(V + E)', 'auxiliary_space': 'O(V)', 'explanation': 'DFS visits every reachable router and traverses each incident link at most twice using a LIFO stack. Auxiliary space is bounded by O(V) for the stack and visited set. Note that DFS does not guarantee the minimum-hop route.'}
    else:
        complexity = {'time': 'O(V + E)', 'auxiliary_space': 'O(V)', 'explanation': 'BFS explores the network level-by-level using a FIFO queue. In an unweighted graph, exploring distance k before k + 1 mathematically guarantees discovering the minimum-hop route in O(V + E) time with O(V) queue space.'}
    report = {'report_type': 'NetRoute Simulation Report', 'schema_version': '1.0', 'generated_at': timestamp, 'topology': topology_section, 'simulation': {'algorithm': algo_label, 'source': src_clean, 'destination': dst_clean, 'status': status, 'route': route, 'hop_count': hop_count, 'visited_order': visited_order, 'parent_mapping': parent_mapping, 'traversal_steps_count': len(traversal_steps), 'traversal_steps': traversal_steps, 'queue_or_stack_states': queue_or_stack_states, 'explored_edges': explored_edges, 'execution_time_ms': execution_time_ms, 'message': message}, 'complexity': complexity}
    return report

def export_simulation_report_json(report_data: Dict[str, Any]) -> str:
    return json.dumps(report_data, indent=2)

def generate_comparison_report(graph: Graph, cmp_res: Dict[str, Any], source: str, destination: str) -> Dict[str, Any]:
    from algorithms import generate_comparison_report as _algo_cmp_rep
    return _algo_cmp_rep(graph, cmp_res, source, destination)

def export_comparison_report_json(report_data: Dict[str, Any]) -> str:
    return json.dumps(report_data, indent=2)

def export_simulation_metrics_csv(report_data: Dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Algorithm', 'Topology', 'Source', 'Destination', 'Status', 'Hop Count', 'Visited Routers Count', 'Explored Edges Count', 'Total Simulation Steps', 'Execution Time (ms)', 'Route'])
    sim = report_data.get('simulation', {})
    topo = report_data.get('topology', {})
    route_str = ' -> '.join(sim.get('route', [])) if sim.get('route') else 'None'
    writer.writerow([sim.get('algorithm', 'Unknown'), topo.get('name', 'Active Topology'), sim.get('source', ''), sim.get('destination', ''), sim.get('status', ''), sim.get('hop_count', 0), len(sim.get('visited_order', [])), len(sim.get('explored_edges', [])), sim.get('traversal_steps_count', 0), sim.get('execution_time_ms', 0.0), route_str])
    return output.getvalue()

def export_comparison_metrics_csv(cmp_report_data: Dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Algorithm', 'Source', 'Destination', 'Status', 'Hops', 'Routers Visited', 'Explored Edges', 'Data Structure Pushes/Enqueues', 'Data Structure Pops/Dequeues', 'Max Frontier Depth', 'Execution Time (ms)', 'Route'])
    endpoints = cmp_report_data.get('endpoints', {})
    src = endpoints.get('source', '')
    dst = endpoints.get('destination', '')
    for key, name in [('bfs_run', 'BFS'), ('dfs_run', 'DFS'), ('dijkstra_run', 'Dijkstra')]:
        run = cmp_report_data.get(key)
        if run:
            metrics = run.get('metrics', {})
            route_info = run.get('route', {})
            writer.writerow([name, src, dst, run.get('status', ''), route_info.get('hop_count', 0), metrics.get('visited_routers_count', 0), metrics.get('explored_edges_count', 0), metrics.get('enqueues_or_pushes', 0), metrics.get('dequeues_or_pops', 0), metrics.get('max_data_structure_depth', 0), metrics.get('execution_time_ms', 0.0), route_info.get('path_string', 'None')])
    return output.getvalue()

def export_resilience_csv(resilience_data: Dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Metric', 'Count', 'Details'])
    writer.writerow(['Active Routers', len(resilience_data.get('online_routers', [])), '; '.join(resilience_data.get('online_routers', []))])
    writer.writerow(['Active Links', len(resilience_data.get('active_edges', [])), '; '.join((f'{u}<->{v}' for u, v in resilience_data.get('active_edges', [])))])
    writer.writerow(['Connected Components', resilience_data.get('component_count', 1), f"{resilience_data.get('component_count', 1)} Subnets"])
    bridges = resilience_data.get('bridges', [])
    writer.writerow(['Critical Bridges (Cut Edges)', len(bridges), '; '.join((f'{u}<->{v}' for u, v in bridges)) if bridges else 'None (Cyclic / Redundant)'])
    aps = resilience_data.get('articulation_points', [])
    writer.writerow(['Critical Articulation Points (Cut Vertices)', len(aps), '; '.join(aps) if aps else 'None (Biconnected)'])
    return output.getvalue()

def export_failure_scenario_csv(scenario_data: Dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Phase', 'Connected Components', 'Bridges Count', 'Articulation Points Count', 'Route Found', 'Hop Count', 'Route String'])
    base = scenario_data.get('baseline', {})
    fail = scenario_data.get('failure_scenario', {})
    b_bfs = base.get('bfs') or {}
    f_bfs = fail.get('bfs') or {}
    writer.writerow(['Baseline (Pre-Failure)', base.get('component_count', 1), len(base.get('bridges', [])), len(base.get('articulation_points', [])), b_bfs.get('success', False), b_bfs.get('hops', 0), ' -> '.join(b_bfs.get('path', [])) if b_bfs.get('path') else 'None'])
    writer.writerow(['Failure Scenario (Post-Failure)', fail.get('component_count', 1), len(fail.get('bridges', [])), len(fail.get('articulation_points', [])), f_bfs.get('success', False), f_bfs.get('hops', 0), ' -> '.join(f_bfs.get('path', [])) if f_bfs.get('path') else 'None (Unreachable)'])
    return output.getvalue()

def export_benchmark_csv(benchmark_records: List[Dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Routers (V)', 'Edges (E)', 'Density', 'Algorithm', 'Mean Time (ms)', 'Min Time (ms)', 'Max Time (ms)', 'Std Dev (ms)', 'Hops', 'Path Cost', 'Visited Vertices', 'Explored Edges', 'Theoretical Time Complexity', 'Theoretical Space Complexity'])
    for rec in benchmark_records:
        writer.writerow([rec.get('routers', 0), rec.get('edges', 0), rec.get('density', 0.0), rec.get('algorithm', ''), rec.get('mean_time_ms', 0.0), rec.get('min_time_ms', 0.0), rec.get('max_time_ms', 0.0), rec.get('std_time_ms', 0.0), rec.get('hops', 0), rec.get('path_cost', 0.0), rec.get('visited_count', 0), rec.get('explored_edges', 0), rec.get('theoretical_time', ''), rec.get('theoretical_space', '')])
    return output.getvalue()
