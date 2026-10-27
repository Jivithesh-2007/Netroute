"""
simulation.py — Simulation State, Playback Progression, and Packet Transmission Engine.

Maintains a single source of truth in Streamlit session state for:
- Algorithm execution results.
- Granular step-by-step playback progression (play/pause/scrub).
- Hop-by-hop packet transmission along discovered routes.
- Invalidation of outdated simulation data upon topology modification.
"""

from typing import Dict, Any, Optional, Set, List, Tuple
import streamlit as st
from network import Graph
from algorithms import bfs, dfs


def init_session():
    """Initializes standard session state variables if not already initialized."""
    if "graph" not in st.session_state:
        g = Graph()
        g.load_preset("sample")
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
        st.session_state["selected_algo"] = "BFS (Shortest-Hop)"

    if "source_id" not in st.session_state:
        st.session_state["source_id"] = "R1"

    if "dest_id" not in st.session_state:
        st.session_state["dest_id"] = "R6"


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
    """Runs genuine BFS or DFS, stores steps, and starts playback from step 0."""
    if "BFS" in algo:
        res = bfs(graph, src, dst)
    else:
        res = dfs(graph, src, dst)

    st.session_state["sim_res"] = res
    # Start at step 0 so user sees initialization, or allow play through
    st.session_state["step_idx"] = 0
    st.session_state["is_playing"] = False
    st.session_state["packet_hop"] = 0
    st.session_state["packet_auto"] = False
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
    visited_nodes: Set[str] = set()
    explored_edges: Set[Tuple[str, str]] = set()
    tree_edges: List[Tuple[str, str]] = []
    route_nodes: Set[str] = set()
    route_edges: List[Tuple[str, str]] = []
    packet_node = None
    next_packet_node = None
    packet_status = "No route discovered."

    if res and res.get("steps"):
        idx = max(0, min(st.session_state.get("step_idx", 0), len(res["steps"]) - 1))
        current_step = res["steps"][idx]

        active_node = current_step.get("current_node")
        active_edge = current_step.get("active_edge")
        visited_nodes = set(current_step.get("visited", []))

        # Accumulate explored edges up to this step
        for s in res["steps"][:idx + 1]:
            if s.get("active_edge"):
                explored_edges.add(tuple(sorted(s["active_edge"])))

        # Tree edges up to this step from parent map
        for child, par in current_step.get("parents", {}).items():
            if par is not None:
                tree_edges.append(tuple(sorted((par, child))))

    if res and res.get("success") and res.get("path"):
        path = res["path"]
        route_nodes = set(path)
        for i in range(len(path) - 1):
            route_edges.append(tuple(sorted((path[i], path[i + 1]))))

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

    return {
        "step": current_step,
        "res": res,
        "active_node": active_node,
        "active_edge": active_edge,
        "action_target": current_step.get("action_target") if current_step else None,
        "visited_nodes": visited_nodes,
        "explored_edges": explored_edges,
        "tree_edges": tree_edges,
        "route_nodes": route_nodes,
        "route_edges": route_edges,
        "packet_node": packet_node,
        "next_packet_node": next_packet_node,
        "packet_status": packet_status
    }
