"""
report.py — Dynamic JSON Simulation Report Generation Engine.

Produces authoritative, standardized JSON execution reports for network routing simulations,
recording topology snapshots, traversal metrics, queue/stack execution traces, and theoretical complexity.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from network import Graph


def generate_simulation_report(
    graph: Graph,
    sim_res: Optional[Dict[str, Any]],
    source: str,
    destination: str,
    algo_name: str = "BFS",
    topology_name: str = ""
) -> Dict[str, Any]:
    """
    Constructs a comprehensive, schema-compliant simulation report derived authoritatively
    from the active graph state and the executed routing simulation.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    src_clean = str(source).strip().upper()
    dst_clean = str(destination).strip().upper()
    active_topo_name = topology_name.strip() or getattr(graph, "name", "") or "Active Network Topology"

    # Topology snapshot
    online_routers = [rid for rid, r in sorted(graph.routers.items()) if r.is_online]
    offline_routers = [rid for rid, r in sorted(graph.routers.items()) if not r.is_online]
    edges_with_weights = [[u, v, graph.get_weight(u, v)] for (u, v) in graph.get_edges()]
    failed_edges_list = [list(e) for e in sorted(graph.failed_edges)]

    topology_section = {
        "name": active_topo_name,
        "router_count": len(graph.routers),
        "connection_count": len(graph.get_edges()),
        "online_routers_count": len(online_routers),
        "offline_routers_count": len(offline_routers),
        "online_routers": online_routers,
        "offline_routers": offline_routers,
        "failed_links_count": len(failed_edges_list),
        "failed_edges": failed_edges_list,
        "routers": [r.to_dict() for r in graph.routers.values()],
        "edges": edges_with_weights
    }

    # Determine status and extract execution data
    if not graph.routers or src_clean not in graph.routers or dst_clean not in graph.routers:
        status = "invalid_input"
        route: List[str] = []
        hop_count = 0
        visited_order: List[str] = []
        parent_mapping: Dict[str, Optional[str]] = {}
        traversal_steps: List[Dict[str, Any]] = []
        queue_or_stack_states: List[Dict[str, Any]] = []
        explored_edges: List[List[str]] = []
        execution_time_ms = 0.0
        message = "Simulation failed: source or destination router does not exist in the active graph."
    elif not graph.routers[src_clean].is_online or not graph.routers[dst_clean].is_online:
        status = "unreachable"
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
        status = "failed_execution"
        route = []
        hop_count = 0
        visited_order = []
        parent_mapping = {}
        traversal_steps = []
        queue_or_stack_states = []
        explored_edges = []
        execution_time_ms = 0.0
        message = "No simulation execution data available."
    else:
        is_success = bool(sim_res.get("success", False))
        if is_success:
            status = "success"
            route = list(sim_res.get("path", []))
            hop_count = int(sim_res.get("hops", max(0, len(route) - 1)))
        else:
            status = "unreachable"
            route = []
            hop_count = 0

        visited_order = list(sim_res.get("visited", []))
        parent_mapping = {k: v for k, v in sim_res.get("parents", {}).items()}
        steps = sim_res.get("steps", [])
        traversal_steps = steps
        execution_time_ms = round(float(sim_res.get("execution_time_ms", 0.0)), 4)
        message = str(sim_res.get("message", ""))

        queue_or_stack_states = []
        explored_set = set()
        for s in steps:
            q_state = {
                "step": s.get("step"),
                "operation": s.get("operation"),
                "current_node": s.get("current_node"),
                "data_structure": s.get("structure", []),
                "action_target": s.get("action_target")
            }
            queue_or_stack_states.append(q_state)
            if s.get("active_edge"):
                ae = tuple(sorted(s["active_edge"]))
                explored_set.add(ae)
        explored_edges = [list(e) for e in sorted(explored_set)]

    # Normalized algorithm label
    is_dfs = "DFS" in algo_name.upper()
    algo_label = "DFS (Depth-First Search)" if is_dfs else "BFS (Breadth-First Search)"

    if is_dfs:
        complexity = {
            "time": "O(V + E)",
            "auxiliary_space": "O(V)",
            "explanation": (
                "DFS visits every reachable router and traverses each incident link at most twice using a LIFO stack. "
                "Auxiliary space is bounded by O(V) for the stack and visited set. Note that DFS does not guarantee "
                "the minimum-hop route."
            )
        }
    else:
        complexity = {
            "time": "O(V + E)",
            "auxiliary_space": "O(V)",
            "explanation": (
                "BFS explores the network level-by-level using a FIFO queue. In an unweighted graph, exploring distance k "
                "before k + 1 mathematically guarantees discovering the minimum-hop route in O(V + E) time with O(V) queue space."
            )
        }

    report = {
        "report_type": "NetRoute Simulation Report",
        "schema_version": "1.0",
        "generated_at": timestamp,
        "topology": topology_section,
        "simulation": {
            "algorithm": algo_label,
            "source": src_clean,
            "destination": dst_clean,
            "status": status,
            "route": route,
            "hop_count": hop_count,
            "visited_order": visited_order,
            "parent_mapping": parent_mapping,
            "traversal_steps_count": len(traversal_steps),
            "traversal_steps": traversal_steps,
            "queue_or_stack_states": queue_or_stack_states,
            "explored_edges": explored_edges,
            "execution_time_ms": execution_time_ms,
            "message": message
        },
        "complexity": complexity
    }

    return report


def export_simulation_report_json(report_data: Dict[str, Any]) -> str:
    """Serializes the report dictionary to a pretty-printed JSON string."""
    return json.dumps(report_data, indent=2)


def generate_comparison_report(
    graph: Graph,
    cmp_res: Dict[str, Any],
    source: str,
    destination: str
) -> Dict[str, Any]:
    """Constructs an authoritative combined dual-simulation comparison JSON report."""
    from algorithms import generate_comparison_report as _algo_cmp_rep
    return _algo_cmp_rep(graph, cmp_res, source, destination)


def export_comparison_report_json(report_data: Dict[str, Any]) -> str:
    """Serializes the comparison report to pretty-printed JSON."""
    return json.dumps(report_data, indent=2)
