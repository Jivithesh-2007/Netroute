"""
simulation.py — Simulation State, Playback Progression, and Packet Transmission Engine.

Maintains a single source of truth in Streamlit session state for:
- Algorithm execution results.
- Granular step-by-step playback progression (play/pause/scrub).
- Hop-by-hop packet transmission along discovered routes.
- Invalidation of outdated simulation data upon topology modification.
"""

import time
import json
from typing import Dict, Any, Optional, Set, List, Tuple
import streamlit as st
from network import Graph
from algorithms import bfs, dfs, dijkstra


def init_session():
    """Initializes standard session state variables if not already initialized."""
    if "graph" not in st.session_state:
        g = Graph()
        g.load_preset("reference")
        st.session_state["graph"] = g

    if "sim_res" not in st.session_state:
        st.session_state["sim_res"] = None

    if "step_idx" not in st.session_state:
        st.session_state["step_idx"] = 0

    if "is_playing" not in st.session_state:
        st.session_state["is_playing"] = False

    if "playback_speed" not in st.session_state:
        st.session_state["playback_speed"] = "Normal"

    if "packet_hop" not in st.session_state:
        st.session_state["packet_hop"] = 0

    if "packet_auto" not in st.session_state:
        st.session_state["packet_auto"] = False

    if "selected_algo" not in st.session_state:
        st.session_state["selected_algo"] = "BFS (Breadth First)"

    if "source_id" not in st.session_state:
        st.session_state["source_id"] = "N1" if "N1" in st.session_state["graph"].routers else ("R1" if "R1" in st.session_state["graph"].routers else (list(st.session_state["graph"].routers.keys())[0] if st.session_state["graph"].routers else "N1"))

    if "dest_id" not in st.session_state:
        st.session_state["dest_id"] = "N7" if "N7" in st.session_state["graph"].routers else ("R6" if "R6" in st.session_state["graph"].routers else (list(st.session_state["graph"].routers.keys())[-1] if st.session_state["graph"].routers else "N7"))

    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "failure_lab_baseline" not in st.session_state:
        st.session_state["failure_lab_baseline"] = None


def get_simulation_status() -> str:
    """Returns the current high-level status of the simulator."""
    res = st.session_state.get("sim_res")
    if not res:
        return "Ready"
    if st.session_state.get("is_playing", False):
        return "Running"
    if not res.get("success", False):
        return "No Route"
    steps = res.get("steps", [])
    if steps and st.session_state.get("step_idx", 0) == len(steps) - 1:
        return "Completed"
    return "Paused"


def invalidate_simulation():
    """Invalidates stale simulation results when topology or endpoints change."""
    st.session_state["sim_res"] = None
    st.session_state["step_idx"] = 0
    st.session_state["is_playing"] = False
    st.session_state["packet_hop"] = 0
    st.session_state["packet_auto"] = False


def execute_routing(graph: Graph, algo: str, src: str, dst: str) -> Dict[str, Any]:
    """Runs genuine BFS, DFS, or Dijkstra, stores steps, records history, and starts playback from step 0."""
    if "Dijkstra" in algo or "Minimum-Cost" in algo or "Weighted" in algo:
        res = dijkstra(graph, src, dst)
    elif "DFS" in algo:
        res = dfs(graph, src, dst)
    else:
        res = bfs(graph, src, dst)

    st.session_state["sim_res"] = res
    st.session_state["step_idx"] = 0
    st.session_state["is_playing"] = False
    st.session_state["packet_hop"] = 0
    st.session_state["packet_auto"] = False

    record_history_entry(res, graph, algo, src, dst)
    return res


def step_forward():
    """Advances one algorithm execution step forward."""
    res = st.session_state.get("sim_res")
    if res and res.get("steps"):
        if st.session_state["step_idx"] < len(res["steps"]) - 1:
            st.session_state["step_idx"] += 1
        else:
            st.session_state["is_playing"] = False


def step_backward():
    """Moves one algorithm execution step backward."""
    if st.session_state.get("step_idx", 0) > 0:
        st.session_state["step_idx"] -= 1
        st.session_state["is_playing"] = False


def first_step():
    """Jumps to the initial step (Step 1)."""
    st.session_state["step_idx"] = 0
    st.session_state["is_playing"] = False


def last_step():
    """Jumps to the final step."""
    res = st.session_state.get("sim_res")
    if res and res.get("steps"):
        st.session_state["step_idx"] = len(res["steps"]) - 1
        st.session_state["is_playing"] = False


def jump_to_step(idx: int):
    """Jumps directly to a specific step index safely."""
    res = st.session_state.get("sim_res")
    if res and res.get("steps"):
        st.session_state["step_idx"] = max(0, min(idx, len(res["steps"]) - 1))


def toggle_playback():
    """Toggles play / pause state."""
    res = st.session_state.get("sim_res")
    if res and res.get("steps"):
        # If already at the end, restart from step 0
        if st.session_state["step_idx"] >= len(res["steps"]) - 1:
            st.session_state["step_idx"] = 0
        st.session_state["is_playing"] = not st.session_state.get("is_playing", False)


def reset_playback():
    """Resets visualizer to step 0."""
    st.session_state["step_idx"] = 0
    st.session_state["is_playing"] = False


def reset_simulation():
    """Completely resets playback and packet states."""
    st.session_state["step_idx"] = 0
    st.session_state["is_playing"] = False
    st.session_state["packet_hop"] = 0
    st.session_state["packet_auto"] = False


# Packet Transmission Controls
def packet_step_forward():
    """Advances packet one hop along the discovered route."""
    res = st.session_state.get("sim_res")
    if res and res.get("success") and res.get("path"):
        if st.session_state["packet_hop"] < len(res["path"]) - 1:
            st.session_state["packet_hop"] += 1
        else:
            st.session_state["packet_auto"] = False


def toggle_packet_stream():
    """Toggles automatic packet streaming along the route."""
    res = st.session_state.get("sim_res")
    if res and res.get("success") and res.get("path"):
        if st.session_state["packet_hop"] >= len(res["path"]) - 1:
            st.session_state["packet_hop"] = 0
        st.session_state["packet_auto"] = not st.session_state.get("packet_auto", False)


def reset_packet():
    """Resets packet position to the source router."""
    st.session_state["packet_hop"] = 0
    st.session_state["packet_auto"] = False


def get_delay_seconds(speed_label: str) -> float:
    """Maps speed setting to seconds delay."""
    speed_map = {
        "Slow": 0.75,
        "Normal": 0.35,
        "Fast": 0.12
    }
    return speed_map.get(speed_label, 0.35)


def get_active_state(graph: Graph) -> Dict[str, Any]:
    """
    Extracts visual elements and state information corresponding
    to the active execution step and packet hop position.
    """
    res = st.session_state.get("sim_res")
    current_step = None
    active_node = None
    active_edge = None
    action_target = None
    visited_nodes: Set[str] = set()
    visited_sequence: List[str] = []
    explored_edges: Set[Tuple[str, str]] = set()
    tree_edges: List[Tuple[str, str]] = []
    route_nodes: Set[str] = set()
    route_edges: List[Tuple[str, str]] = []
    packet_node = None
    next_packet_node = None
    packet_status = "No route discovered."
    is_completed = False

    if res and res.get("steps"):
        tot_steps = len(res["steps"])
        idx = max(0, min(st.session_state.get("step_idx", 0), tot_steps - 1))
        current_step = res["steps"][idx]
        is_completed = (idx == tot_steps - 1)

        active_node = current_step.get("current_node")
        active_edge = current_step.get("active_edge")
        action_target = current_step.get("action_target")
        visited_sequence = list(current_step.get("visited", []))
        visited_nodes = set(visited_sequence)
        if active_node and active_node in graph.routers:
            visited_nodes.add(active_node)

        # Accumulate explored edges up to this step
        for s in res["steps"][:idx + 1]:
            if s.get("active_edge"):
                explored_edges.add(tuple(sorted(s["active_edge"])))

        # Tree edges up to this step from parent map
        for child, par in current_step.get("parents", {}).items():
            if par is not None:
                tree_edges.append(tuple(sorted((par, child))))

    # Only activate the full reconstructed route when traversal has completed!
    if res and res.get("success") and res.get("path") and is_completed:
        path = res["path"]
        route_nodes = set(path)
        for i in range(len(path) - 1):
            route_edges.append(tuple(sorted((path[i], path[i + 1]))))

    # Packet handling
    if res and res.get("success") and res.get("path"):
        path = res["path"]
        p_hop = st.session_state.get("packet_hop", 0)
        if 0 <= p_hop < len(path):
            packet_node = path[p_hop]
            if p_hop + 1 < len(path):
                next_packet_node = path[p_hop + 1]

            # Verify if router became offline
            if not graph.routers.get(packet_node) or not graph.routers[packet_node].is_online:
                packet_status = f"Transmission BLOCKED: Router '{packet_node}' is offline! Rerun algorithm."
            elif p_hop == 0:
                packet_status = f"Packet buffered at Source '{packet_node}'. Ready for transmission."
            elif p_hop == len(path) - 1:
                packet_status = f"Packet successfully DELIVERED at Destination '{packet_node}'! ({len(path) - 1} hops)."
            else:
                packet_status = f"In Transit: Hop {p_hop}/{len(path) - 1} | At '{packet_node}' -> Next: '{next_packet_node}'"
    elif current_step and current_step.get("current_node"):
        packet_node = current_step.get("current_node")

    return {
        "step": current_step,
        "res": res,
        "is_completed": is_completed,
        "active_node": active_node,
        "active_edge": active_edge,
        "action_target": action_target,
        "visited_nodes": visited_nodes,
        "visited_sequence": visited_sequence,
        "explored_edges": explored_edges,
        "tree_edges": tree_edges,
        "route_nodes": route_nodes,
        "route_edges": route_edges,
        "packet_node": packet_node,
        "next_packet_node": next_packet_node,
        "packet_status": packet_status
    }


# -------------------------------------------------------------
# ADVANCED FEATURES ENGINE: HISTORY, FAILURE LAB, REPORTS & CHALLENGES
# -------------------------------------------------------------

def record_history_entry(res: Dict[str, Any], graph: Graph, algo: str, src: str, dst: str):
    """Records completed routing run into lightweight session state history."""
    if not res:
        return
    history = st.session_state.setdefault("history", [])

    algo_clean = "Dijkstra" if "Dijkstra" in algo else ("DFS" if "DFS" in algo else "BFS")
    ops_count = (
        res.get("total_enqueues", 0) if "BFS" in algo_clean
        else (res.get("total_pushes", 0) if "DFS" in algo_clean
        else res.get("total_relaxations", 0))
    )

    entry = {
        "run_id": len(history) + 1,
        "timestamp": time.strftime("%H:%M:%S"),
        "algorithm": algo_clean,
        "source": src,
        "dest": dst,
        "destination": dst,
        "topology": f"{len(graph.routers)} Routers, {len(graph.get_edges())} Links",
        "path": list(res.get("path", [])),
        "route": list(res.get("path", [])),
        "route_str": " -> ".join(res.get("path", [])) if res.get("path") else "No Route",
        "hops": res.get("hops", 0),
        "cost": float(res.get("path_cost", 0.0)),
        "visited": list(res.get("visited", [])),
        "visited_count": len(res.get("visited", [])),
        "operations": ops_count,
        "success": bool(res.get("success", False)),
        "steps_count": len(res.get("steps", [])),
        "execution_time_ms": float(res.get("execution_time_ms", 0.0)),
        "full_res": res
    }
    history.append(entry)


def get_history() -> List[Dict[str, Any]]:
    """Returns the recorded session history."""
    return st.session_state.get("history", [])


def clear_history():
    """Clears all session history entries."""
    st.session_state["history"] = []


def replay_history_run(run_id: int) -> bool:
    """Loads a previous recorded run's execution steps into session state for playback."""
    history = st.session_state.get("history", [])
    for entry in history:
        if entry["run_id"] == run_id:
            st.session_state["sim_res"] = entry["full_res"]
            st.session_state["source_id"] = entry["source"]
            st.session_state["dest_id"] = entry["destination"]
            st.session_state["step_idx"] = 0
            st.session_state["is_playing"] = True
            return True
    return False


def capture_baseline_route(graph: Graph, algo: str, src: str, dst: str) -> Dict[str, Any]:
    """Computes and caches the baseline healthy route for Failure & Recovery Lab."""
    if "Dijkstra" in algo or "Minimum-Cost" in algo or "Weighted" in algo:
        res = dijkstra(graph, src, dst)
    elif "DFS" in algo:
        res = dfs(graph, src, dst)
    else:
        res = bfs(graph, src, dst)

    baseline = {
        "algorithm": algo,
        "source": src,
        "destination": dst,
        "success": res.get("success", False),
        "path": list(res.get("path", [])),
        "hops": res.get("hops", 0),
        "cost": float(res.get("path_cost", 0.0))
    }
    st.session_state["failure_lab_baseline"] = baseline
    return baseline


def compare_failure_routes(*args, **kwargs) -> Dict[str, Any]:
    """
    Compares baseline route vs failure route to provide precise recovery analytics.
    Supports:
      - compare_failure_routes(baseline_dict, current_res_dict)
      - compare_failure_routes(graph, algo, src, dst)
    """
    failed_routers = []
    failed_connections = []

    if len(args) >= 1 and isinstance(args[0], Graph):
        graph = args[0]
        algo = args[1] if len(args) > 1 else kwargs.get("algo", "BFS")
        src = args[2] if len(args) > 2 else kwargs.get("src", "N1")
        dst = args[3] if len(args) > 3 else kwargs.get("dst", "N7")

        baseline = st.session_state.get("failure_lab_baseline")
        if not baseline:
            baseline = capture_baseline_route(graph, algo, src, dst)

        if "Dijkstra" in algo or "Minimum-Cost" in algo or "Weighted" in algo:
            current_res = dijkstra(graph, src, dst)
        elif "DFS" in algo:
            current_res = dfs(graph, src, dst)
        else:
            current_res = bfs(graph, src, dst)

        failed_routers = [r for r, obj in graph.routers.items() if not obj.is_online]
        failed_connections = [f"{u} <-> {v}" for u, v in getattr(graph, "failed_edges", set())]
    else:
        baseline = args[0] if len(args) > 0 else kwargs.get("baseline")
        current_res = args[1] if len(args) > 1 else kwargs.get("current_res", {})

    b_path = list(baseline.get("path", [])) if baseline else []
    b_hops = baseline.get("hops", 0) if baseline else 0
    b_cost = float(baseline.get("cost", 0.0)) if baseline else 0.0

    c_success = current_res.get("success", False) if current_res else False
    c_path = list(current_res.get("path", [])) if current_res else []
    c_hops = current_res.get("hops", 0) if current_res else 0
    c_cost = float(current_res.get("path_cost", 0.0)) if current_res else 0.0

    detour_hops = c_hops - b_hops
    detour_cost = c_cost - b_cost
    route_changed = (b_path != c_path)

    if not baseline:
        status = "No Baseline"
        summary = "Capture a baseline route before simulating failures."
    elif not c_success:
        status = "Unreachable / Partitioned"
        summary = "Destination is completely unreachable! Network partition occurred."
    elif b_path == c_path:
        status = "Original Optimal Route Active"
        summary = "No detour needed. Current route matches healthy baseline."
    else:
        status = "Detour Discovered"
        summary = f"Rerouted around failure (+{detour_hops} hops, +{int(detour_cost) if detour_cost.is_integer() else detour_cost} cost)."

    return {
        "status": status,
        "original_path": b_path,
        "current_path": c_path,
        "baseline_path": b_path,
        "baseline_hops": b_hops,
        "baseline_cost": b_cost,
        "current_hops": c_hops,
        "current_cost": c_cost,
        "detour_hops": detour_hops,
        "detour_cost": detour_cost,
        "is_reachable": c_success,
        "failed_routers": failed_routers,
        "failed_connections": failed_connections,
        "route_changed": route_changed,
        "summary": summary
    }


def export_experiment_report(*args, **kwargs) -> Any:
    """
    Generates an exportable CSV, JSON, or dict report based strictly on actual simulation metrics.
    Supports:
      - export_experiment_report(res, graph, algo, src, dst, format_type="json")
      - export_experiment_report(graph, res, algo, src, dst, format_type="dict")
    """
    if len(args) >= 1 and isinstance(args[0], Graph):
        graph = args[0]
        res = args[1] if len(args) > 1 else kwargs.get("res", {})
        algo = args[2] if len(args) > 2 else kwargs.get("algo", "BFS")
        src = args[3] if len(args) > 3 else kwargs.get("src", "N1")
        dst = args[4] if len(args) > 4 else kwargs.get("dst", "N7")
        default_fmt = "dict"
    else:
        res = args[0] if len(args) > 0 else kwargs.get("res")
        graph = args[1] if len(args) > 1 else kwargs.get("graph")
        algo = args[2] if len(args) > 2 else kwargs.get("algo", "BFS")
        src = args[3] if len(args) > 3 else kwargs.get("src", "N1")
        dst = args[4] if len(args) > 4 else kwargs.get("dst", "N7")
        default_fmt = "json"

    format_type = kwargs.get("format_type", default_fmt)
    if len(args) >= 6:
        format_type = args[5]

    if not res:
        if format_type == "json":
            return "{}"
        elif format_type == "csv":
            return "Metric,Value\nStatus,No simulation results recorded"
        else:
            return {
                "title": "Network Routing Experiment Report",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": src,
                "destination": dst,
                "algorithm": algo,
                "route": [],
                "hops": 0,
                "total_weight": 0.0,
                "visited_count": 0,
                "reachability": "No Simulation",
                "theoretical_complexity": {"time": "N/A", "space": "N/A"},
                "explanation": "No simulation results recorded.",
                "topology": {
                    "total_routers": len(graph.routers) if graph else 0,
                    "active_routers": sum(1 for r in graph.routers.values() if r.is_online) if graph else 0,
                    "total_connections": len(graph.get_edges()) if graph else 0
                }
            }

    algo_name = res.get("algorithm", algo)
    path = res.get("path", [])
    hops = res.get("hops", 0)
    cost = res.get("path_cost", 0.0)
    visited = res.get("visited", [])
    success = res.get("success", False)
    elapsed = res.get("execution_time_ms", 0.0)

    if "BFS" in algo_name:
        time_comp = "O(V + E)"
        space_comp = "O(V) [Queue Capacity]"
        ds_name = "FIFO Queue (collections.deque)"
        rationale = "BFS guarantees minimum hops by expanding level by level."
    elif "DFS" in algo_name:
        time_comp = "O(V + E)"
        space_comp = "O(V) [Stack Depth]"
        ds_name = "LIFO Stack (list)"
        rationale = "DFS traverses deep branches with backtracking; valid path without hop guarantee."
    else:
        time_comp = "O((V + E) log V)"
        space_comp = "O(V) [Priority Queue]"
        ds_name = "Min-Heap Priority Queue (heapq)"
        rationale = "Dijkstra minimizes cumulative edge weights using greedy relaxation."

    report_data = {
        "project": "NetRoute — Interactive Network Routing Simulator",
        "title": "Network Routing Experiment Report",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": src,
        "destination": dst,
        "algorithm": algo_name,
        "core_data_structure": ds_name,
        "success": success,
        "reachability": "Reachable" if success else "Unreachable",
        "route": path,
        "route_nodes": path,
        "route_discovered": " -> ".join(path) if path else "None (Unreachable)",
        "hops": hops,
        "hop_count": hops,
        "total_cost": cost,
        "total_weight": cost,
        "total_visited_routers": len(visited),
        "visited_count": len(visited),
        "visited_sequence": visited,
        "total_execution_steps": len(res.get("steps", [])),
        "execution_latency_ms": round(elapsed, 3),
        "time_complexity": time_comp,
        "auxiliary_space_complexity": space_comp,
        "theoretical_complexity": {
            "time": time_comp,
            "space": space_comp
        },
        "topology": {
            "total_routers": len(graph.routers) if graph else 0,
            "active_routers": sum(1 for r in graph.routers.values() if r.is_online) if graph else 0,
            "total_connections": len(graph.get_edges()) if graph else 0,
            "failed_connections": len(graph.failed_edges) if hasattr(graph, "failed_edges") else 0
        },
        "network_topology": {
            "total_routers": len(graph.routers) if graph else 0,
            "online_routers": sum(1 for r in graph.routers.values() if r.is_online) if graph else 0,
            "total_connections": len(graph.get_edges()) if graph else 0,
            "failed_connections": len(graph.failed_edges) if hasattr(graph, "failed_edges") else 0
        },
        "explanation": rationale,
        "algorithmic_explanation": rationale
    }

    if format_type.lower() == "csv":
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Project", report_data["project"]])
        writer.writerow(["Timestamp", report_data["timestamp"]])
        writer.writerow(["Source Node", report_data["source"]])
        writer.writerow(["Destination Node", report_data["destination"]])
        writer.writerow(["Algorithm", report_data["algorithm"]])
        writer.writerow(["Data Structure", report_data["core_data_structure"]])
        writer.writerow(["Route Discovered", report_data["route_discovered"]])
        writer.writerow(["Hop Count", report_data["hop_count"]])
        writer.writerow(["Total Path Cost", report_data["total_cost"]])
        writer.writerow(["Visited Routers Count", report_data["total_visited_routers"]])
        writer.writerow(["Visited Sequence", " -> ".join(visited)])
        writer.writerow(["Total Steps", report_data["total_execution_steps"]])
        writer.writerow(["Time Complexity", report_data["time_complexity"]])
        writer.writerow(["Space Complexity", report_data["auxiliary_space_complexity"]])
        writer.writerow(["Outcome", report_data["algorithmic_explanation"]])
        return output.getvalue()
    elif format_type.lower() == "json":
        return json.dumps(report_data, indent=2)

    return report_data


CHALLENGES = [
    {
        "id": 1,
        "title": "Challenge 1: Queue Mechanics & Minimum Hops (CO1 & CO5)",
        "difficulty": "Beginner",
        "description": "Analyze FIFO queue level-by-level concentric expansion on the standard 7-node network.",
        "question": "On the Reference LAN/WAN topology, which route from N1 to N7 will BFS discover first using its FIFO Queue?",
        "options": [
            "N1 -> N2 -> N4 -> N6 -> N7 (4 hops)",
            "N1 -> N3 -> N5 -> N6 -> N7 (4 hops)",
            "N1 -> N2 -> N3 -> N5 -> N6 -> N7 (5 hops)",
            "N1 -> N1 (0 hops)"
        ],
        "correct_option": "N1 -> N2 -> N4 -> N6 -> N7 (4 hops)",
        "preset": "reference",
        "src": "N1",
        "dst": "N7",
        "source": "N1",
        "dest": "N7",
        "algo": "BFS",
        "explanation": "BFS uses a FIFO queue and visits neighbors in sorted alphabetical order. From N1, N2 is enqueued before N3. Therefore, N2's branch (N2 -> N4 -> N6 -> N7) reaches N7 at level 4 before the bottom branch is finalized."
    },
    {
        "id": 2,
        "title": "Challenge 2: Min-Hop vs. Min-Cost (Dijkstra vs. BFS)",
        "difficulty": "Intermediate",
        "description": "Compare minimum-hop unweighted routing against minimum-total-cost weighted routing.",
        "question": "On the Weighted Comparison network, what is the key difference between the route chosen by BFS vs. Dijkstra from S to D?",
        "options": [
            "BFS chooses S -> A -> D (2 hops, cost 13); Dijkstra chooses S -> A -> B -> D (3 hops, cost 4)",
            "Both BFS and Dijkstra choose the exact same 2-hop route S -> A -> D",
            "Dijkstra chooses S -> A -> D because it has fewer hops than S -> A -> B -> D",
            "BFS chooses S -> C -> B -> D with cost 6"
        ],
        "correct_option": "BFS chooses S -> A -> D (2 hops, cost 13); Dijkstra chooses S -> A -> B -> D (3 hops, cost 4)",
        "preset": "weighted_diff",
        "src": "S",
        "dst": "D",
        "source": "S",
        "dest": "D",
        "algo": "Dijkstra",
        "explanation": "BFS only minimizes edge hops, picking the 2-hop path S-A-D despite its heavy link cost of 12 (total: 13). Dijkstra computes cumulative edge weights (1 + 1 + 2 = 4), selecting the 3-hop path because 4 < 13."
    },
    {
        "id": 3,
        "title": "Challenge 3: Network Topology & Articulation Points",
        "difficulty": "Advanced",
        "description": "Determine how component failure affects reachability and graph cut articulation.",
        "question": "On the Reference topology, if Switch B (N6) suffers a hardware failure, can Server A (N1) reach Server B (N7)?",
        "options": [
            "No, N6 is an articulation bridge for N7; N7 becomes completely unreachable",
            "Yes, packets will automatically detour through Router 4 (N5)",
            "Yes, packets will detour through Router 3 (N4)",
            "Yes, via cyclic DFS backtracking"
        ],
        "correct_option": "No, N6 is an articulation bridge for N7; N7 becomes completely unreachable",
        "preset": "reference",
        "src": "N1",
        "dst": "N7",
        "source": "N1",
        "dest": "N7",
        "algo": "BFS",
        "explanation": "Switch B (N6) is the single gateway connected to Server B (N7). Disabling N6 isolates N7 into a disconnected component of size 1, making packet delivery impossible."
    },
    {
        "id": 4,
        "title": "Challenge 4: LIFO Stack Mechanics & Backtracking (CO1)",
        "difficulty": "Intermediate",
        "description": "Analyze LIFO stack backtracking mechanics when a dead end is reached.",
        "question": "During iterative Depth-First Search (DFS), what happens when the algorithm reaches a router with zero unvisited neighbors (a dead end)?",
        "options": [
            "It triggers backtracking by popping the top element of the LIFO stack to resume from the predecessor",
            "It resets the visited array to allow cyclic loops",
            "It terminates execution immediately with failure",
            "It switches to BFS queue mode"
        ],
        "correct_option": "It triggers backtracking by popping the top element of the LIFO stack to resume from the predecessor",
        "preset": "reference",
        "src": "N1",
        "dst": "N7",
        "source": "N1",
        "dest": "N7",
        "algo": "DFS",
        "explanation": "In LIFO stack exploration, when a branch terminates at a dead end, DFS backtracks by popping stack entries until it uncovers a node with remaining unvisited edges."
    }
]


def evaluate_challenge_answer(challenge_id: int, user_answer: str) -> Tuple[bool, str]:
    """Validates user's answer against the actual challenge definition and algorithmic rules."""
    for ch in CHALLENGES:
        if ch["id"] == challenge_id:
            is_correct = (user_answer.strip() == ch["correct_option"].strip())
            return is_correct, ch["explanation"]
    return False, "Challenge not found."


def compare_bfs_and_dfs(graph: Graph, src: str, dst: str) -> Dict[str, Any]:
    """
    Performs comparative dual analysis of BFS (FIFO Queue) vs. DFS (LIFO Stack)
    on the identical network topology between specified source and destination.
    Computes exact differentials in path, hops, cost, execution latency, visited nodes,
    steps, operations, and data structure footprints.
    """
    b_res = bfs(graph, src, dst)
    d_res = dfs(graph, src, dst)

    b_path = list(b_res.get("path", []))
    d_path = list(d_res.get("path", []))
    b_hops = b_res.get("hops", 0)
    d_hops = d_res.get("hops", 0)
    b_cost = float(b_res.get("path_cost", 0.0))
    d_cost = float(d_res.get("path_cost", 0.0))
    b_time = float(b_res.get("execution_time_ms", 0.0))
    d_time = float(d_res.get("execution_time_ms", 0.0))
    b_steps = len(b_res.get("steps", []))
    d_steps = len(d_res.get("steps", []))
    b_visited = list(b_res.get("visited", []))
    d_visited = list(d_res.get("visited", []))
    b_max_ds = b_res.get("max_structure", 0)
    d_max_ds = d_res.get("max_structure", 0)

    # Active Plotly state structures for side-by-side visualization
    b_active = {
        "is_completed": True,
        "route_nodes": set(b_path),
        "route_edges": [tuple(sorted((b_path[i], b_path[i+1]))) for i in range(len(b_path)-1)],
        "visited_nodes": set(b_visited),
        "explored_edges": b_res.get("tree_edges", [])
    }
    d_active = {
        "is_completed": True,
        "route_nodes": set(d_path),
        "route_edges": [tuple(sorted((d_path[i], d_path[i+1]))) for i in range(len(d_path)-1)],
        "visited_nodes": set(d_visited),
        "explored_edges": d_res.get("tree_edges", [])
    }

    # Differentials
    hop_delta = d_hops - b_hops
    cost_delta = round(d_cost - b_cost, 2)
    time_delta = round(d_time - b_time, 3)
    steps_delta = d_steps - b_steps
    visited_delta = len(d_visited) - len(b_visited)

    if b_path == d_path:
        route_status = "Identical Path Discovered"
        hop_comparison = f"Both found identical {b_hops}-hop path"
    elif b_hops < d_hops:
        route_status = f"BFS Shorter by {hop_delta} Hop{'s' if hop_delta > 1 else ''}"
        hop_comparison = f"BFS is {hop_delta} hop(s) shorter (BFS: {b_hops} hops vs DFS: {d_hops} hops)"
    else:
        route_status = f"DFS Discovered Alternative Route ({d_hops} hops)"
        hop_comparison = f"DFS {d_hops} hops vs BFS {b_hops} hops"

    comparison_table = [
        {
            "Performance Metric": "Discovered Route",
            "BFS (FIFO Queue)": " -> ".join(b_path) if b_path else "Unreachable",
            "DFS (LIFO Stack)": " -> ".join(d_path) if d_path else "Unreachable",
            "Differential (DFS vs. BFS)": "Identical" if b_path == d_path else "Different Paths",
            "Engineering Takeaway": "BFS guarantees shortest hops; DFS finds arbitrary reachable branch."
        },
        {
            "Performance Metric": "Hop Count",
            "BFS (FIFO Queue)": f"{b_hops} hops",
            "DFS (LIFO Stack)": f"{d_hops} hops",
            "Differential (DFS vs. BFS)": f"{'+' if hop_delta > 0 else ''}{hop_delta} hops",
            "Engineering Takeaway": "BFS guarantees minimum hops in unweighted graphs." if hop_delta > 0 else "Both discovered paths of equal hop length."
        },
        {
            "Performance Metric": "Total Path Cost / Weight",
            "BFS (FIFO Queue)": f"{int(b_cost) if b_cost.is_integer() else b_cost}",
            "DFS (LIFO Stack)": f"{int(d_cost) if d_cost.is_integer() else d_cost}",
            "Differential (DFS vs. BFS)": f"{'+' if cost_delta > 0 else ''}{cost_delta}",
            "Engineering Takeaway": "Neither unweighted BFS nor DFS optimizes for link cost."
        },
        {
            "Performance Metric": "Execution Latency",
            "BFS (FIFO Queue)": f"{b_time:.3f} ms",
            "DFS (LIFO Stack)": f"{d_time:.3f} ms",
            "Differential (DFS vs. BFS)": f"{'+' if time_delta > 0 else ''}{time_delta:.3f} ms",
            "Engineering Takeaway": "Both operate in O(V + E) time; latency depends on branch depth."
        },
        {
            "Performance Metric": "Total Traversal Steps",
            "BFS (FIFO Queue)": f"{b_steps} steps",
            "DFS (LIFO Stack)": f"{d_steps} steps",
            "Differential (DFS vs. BFS)": f"{'+' if steps_delta > 0 else ''}{steps_delta} steps",
            "Engineering Takeaway": "DFS includes extra pop operations during dead-end backtracking."
        },
        {
            "Performance Metric": "Total Visited Routers",
            "BFS (FIFO Queue)": f"{len(b_visited)} routers",
            "DFS (LIFO Stack)": f"{len(d_visited)} routers",
            "Differential (DFS vs. BFS)": f"{'+' if visited_delta > 0 else ''}{visited_delta} nodes",
            "Engineering Takeaway": "BFS explores level-by-level; DFS dives deep along the first branch."
        },
        {
            "Performance Metric": "Core Structure Operations",
            "BFS (FIFO Queue)": f"{b_res.get('total_enqueues', 0)} enqueues / {b_res.get('total_dequeues', 0)} dequeues",
            "DFS (LIFO Stack)": f"{d_res.get('total_pushes', 0)} pushes / {d_res.get('total_pops', 0)} pops ({d_res.get('backtrack_count', 0)} backtracks)",
            "Differential (DFS vs. BFS)": "FIFO Queue vs. LIFO Stack",
            "Engineering Takeaway": "Queue enqueues at rear / dequeues at front; Stack pushes / pops at top."
        },
        {
            "Performance Metric": "Peak Structure Footprint",
            "BFS (FIFO Queue)": f"{b_max_ds} nodes in Queue",
            "DFS (LIFO Stack)": f"{d_max_ds} nodes in Stack",
            "Differential (DFS vs. BFS)": f"{d_max_ds - b_max_ds:+d} nodes",
            "Engineering Takeaway": "Queue size bounded by graph bandwidth; Stack size bounded by max depth."
        }
    ]

    return {
        "bfs_res": b_res,
        "dfs_res": d_res,
        "b_path": b_path,
        "d_path": d_path,
        "b_hops": b_hops,
        "d_hops": d_hops,
        "b_cost": b_cost,
        "d_cost": d_cost,
        "b_time": b_time,
        "d_time": d_time,
        "b_steps": b_steps,
        "d_steps": d_steps,
        "b_visited": b_visited,
        "d_visited": d_visited,
        "b_active": b_active,
        "d_active": d_active,
        "hop_delta": hop_delta,
        "cost_delta": cost_delta,
        "time_delta": time_delta,
        "steps_delta": steps_delta,
        "visited_delta": visited_delta,
        "route_status": route_status,
        "hop_comparison": hop_comparison,
        "comparison_table": comparison_table
    }


# =============================================================================
# CO5: TRADITIONAL ROUTING TABLE FORWARDING ENGINE
# =============================================================================

def simulate_table_forwarding(graph: Graph, src: str, dst: str, max_hops: int = 25) -> Dict[str, Any]:
    """
    Simulates traditional hop-by-hop packet forwarding using local router routing tables.
    
    Demonstrates the fundamental networking distinction required by CO5:
    - Graph-Based Routing: Centralized end-to-end path computation using graph traversal (BFS/DFS).
    - Table-Based Forwarding: Distributed hop-by-hop forwarding where each router independently
      looks up the packet's destination in its local routing table to determine the Next Hop.
    """
    src_clean = str(src).strip().upper()
    dst_clean = str(dst).strip().upper()

    if not graph or not graph.routers:
        return {
            "success": False,
            "status": "EMPTY_GRAPH",
            "path": [],
            "hops": 0,
            "steps": [],
            "message": "Network graph is empty."
        }

    if src_clean not in graph.routers:
        return {
            "success": False,
            "status": "SOURCE_NOT_FOUND",
            "path": [],
            "hops": 0,
            "steps": [],
            "message": f"Source router '{src_clean}' does not exist in the network."
        }

    if dst_clean not in graph.routers:
        return {
            "success": False,
            "status": "DEST_NOT_FOUND",
            "path": [],
            "hops": 0,
            "steps": [],
            "message": f"Destination router '{dst_clean}' does not exist in the network."
        }

    if not graph.routers[src_clean].is_online:
        return {
            "success": False,
            "status": "SOURCE_OFFLINE",
            "path": [src_clean],
            "hops": 0,
            "steps": [],
            "message": f"Source router '{src_clean}' is offline. Cannot initiate packet transmission."
        }

    if not graph.routers[dst_clean].is_online:
        return {
            "success": False,
            "status": "DEST_OFFLINE",
            "path": [src_clean],
            "hops": 0,
            "steps": [],
            "message": f"Destination router '{dst_clean}' is offline."
        }

    # Handle immediate local delivery (source equals destination)
    if src_clean == dst_clean:
        return {
            "success": True,
            "status": "DELIVERED_LOCAL",
            "path": [src_clean],
            "hops": 0,
            "steps": [{
                "step": 1,
                "current_router": src_clean,
                "next_hop": src_clean,
                "action": "LOCAL_DELIVERY",
                "table_entry": {"destination": dst_clean, "next_hop": src_clean, "hops": 0, "status": "Local (Self)"},
                "description": f"Source '{src_clean}' is the destination. Packet processed locally."
            }],
            "message": f"Packet processed locally at router '{src_clean}' (0 hops)."
        }

    curr = src_clean
    path: List[str] = [curr]
    steps: List[Dict[str, Any]] = []
    visited_set: Set[str] = {curr}
    step_num = 1
    success = False
    status = "IN_PROGRESS"
    failure_message = ""

    while curr != dst_clean and step_num <= max_hops:
        # Inspect current router's local routing table
        curr_table = graph.generate_routing_table(curr)
        matching_entry = next((e for e in curr_table if e["destination"] == dst_clean), None)

        if not matching_entry or matching_entry["next_hop"] in ("None", None) or matching_entry["hops"] < 0:
            status = "NO_ROUTE_TO_HOST"
            failure_message = f"Router '{curr}' routing table has NO ROUTE to destination '{dst_clean}'."
            steps.append({
                "step": step_num,
                "current_router": curr,
                "next_hop": "None",
                "action": "FORWARDING_FAILED",
                "table_entry": matching_entry or {"destination": dst_clean, "next_hop": "None", "hops": -1, "status": "Unreachable"},
                "description": failure_message
            })
            break

        nxt = matching_entry["next_hop"]

        # Verify next hop router is online
        if nxt not in graph.routers or not graph.routers[nxt].is_online:
            status = "NEXT_HOP_OFFLINE"
            failure_message = f"Forwarding failure at '{curr}': Next Hop router '{nxt}' is offline."
            steps.append({
                "step": step_num,
                "current_router": curr,
                "next_hop": nxt,
                "action": "NEXT_HOP_DOWN",
                "table_entry": matching_entry,
                "description": failure_message
            })
            break

        # Verify link (curr, nxt) is active in topology
        if not graph.is_edge_active(curr, nxt):
            status = "LINK_SEVERED"
            failure_message = f"Forwarding failure at '{curr}': Physical link ({curr} <-> {nxt}) is failed/severed."
            steps.append({
                "step": step_num,
                "current_router": curr,
                "next_hop": nxt,
                "action": "LINK_DOWN",
                "table_entry": matching_entry,
                "description": failure_message
            })
            break

        # Check for routing loop
        if nxt in visited_set:
            status = "ROUTING_LOOP"
            failure_message = f"Routing loop detected: packet forwarded back to previously visited router '{nxt}'."
            steps.append({
                "step": step_num,
                "current_router": curr,
                "next_hop": nxt,
                "action": "LOOP_DETECTED",
                "table_entry": matching_entry,
                "description": failure_message
            })
            break

        # Advance packet to next hop
        steps.append({
            "step": step_num,
            "current_router": curr,
            "next_hop": nxt,
            "action": "FORWARD",
            "table_entry": matching_entry,
            "description": f"Hop {step_num}: Router '{curr}' looked up destination '{dst_clean}' in its routing table -> forwarded to Next Hop '{nxt}' ({matching_entry['hops']} metric hops)."
        })

        curr = nxt
        path.append(curr)
        visited_set.add(curr)
        step_num += 1

        if curr == dst_clean:
            success = True
            status = "DELIVERED"
            steps.append({
                "step": step_num,
                "current_router": curr,
                "next_hop": "None",
                "action": "DELIVERY_COMPLETE",
                "table_entry": {"destination": dst_clean, "next_hop": curr, "hops": 0, "status": "Delivered"},
                "description": f"Packet successfully reached destination router '{dst_clean}' in {len(path) - 1} hops."
            })
            break

    if not success and status == "IN_PROGRESS":
        status = "TTL_EXPIRED"
        failure_message = f"Forwarding terminated: exceeded maximum hop limit of {max_hops}."

    hops_count = len(path) - 1 if len(path) > 1 else 0

    return {
        "success": success,
        "status": status,
        "path": path,
        "hops": hops_count,
        "steps": steps,
        "final_router": curr,
        "message": f"Table forwarding {'succeeded: ' + ' -> '.join(path) if success else 'failed: ' + failure_message}"
    }


