"""
simulation.py — Simulation State, Playback Progression, and Packet Transmission.

Manages Streamlit session state cleanly, separating algorithm execution from
step-by-step playback and packet animation.
"""

from typing import Dict, Any, Optional, Set, List, Tuple
import streamlit as st
from network import Graph
from algorithms import bfs, dfs


def init_session():
    """Initializes default session state variables if not already present."""
    if "graph" not in st.session_state:
        g = Graph()
        g.load_preset("sample")
        st.session_state["graph"] = g

    if "sim_res" not in st.session_state:
        st.session_state["sim_res"] = None

    if "step_idx" not in st.session_state:
        st.session_state["step_idx"] = 0

    if "packet_hop" not in st.session_state:
        st.session_state["packet_hop"] = 0

    if "auto_play" not in st.session_state:
        st.session_state["auto_play"] = False

    if "packet_auto" not in st.session_state:
        st.session_state["packet_auto"] = False

    if "selected_algo" not in st.session_state:
        st.session_state["selected_algo"] = "BFS (Shortest-Hop)"

    if "source_id" not in st.session_state:
        st.session_state["source_id"] = "R1"

    if "dest_id" not in st.session_state:
        st.session_state["dest_id"] = "R6"


def invalidate_simulation():
    """Invalidates stale simulation results when topology or endpoints change."""
    st.session_state["sim_res"] = None
    st.session_state["step_idx"] = 0
    st.session_state["packet_hop"] = 0
    st.session_state["auto_play"] = False
    st.session_state["packet_auto"] = False


def execute_routing(graph: Graph, algo: str, src: str, dst: str) -> Dict[str, Any]:
    """Executes the selected routing algorithm and resets playback to the final step."""
    if "BFS" in algo:
        res = bfs(graph, src, dst)
    else:
        res = dfs(graph, src, dst)

    st.session_state["sim_res"] = res
    st.session_state["step_idx"] = len(res["steps"]) - 1 if res.get("steps") else 0
    st.session_state["packet_hop"] = 0
    st.session_state["auto_play"] = False
    st.session_state["packet_auto"] = False
    return res


def step_forward():
    """Advances one execution step forward."""
    res = st.session_state.get("sim_res")
    if res and res.get("steps"):
        if st.session_state["step_idx"] < len(res["steps"]) - 1:
            st.session_state["step_idx"] += 1
        else:
            st.session_state["auto_play"] = False


def step_backward():
    """Moves one execution step backward."""
    if st.session_state.get("step_idx", 0) > 0:
        st.session_state["step_idx"] -= 1


def jump_to_step(idx: int):
    """Jumps directly to a specific step index safely."""
    res = st.session_state.get("sim_res")
    if res and res.get("steps"):
        st.session_state["step_idx"] = max(0, min(idx, len(res["steps"]) - 1))


def reset_playback():
    """Resets visualizer to step 0."""
    st.session_state["step_idx"] = 0
    st.session_state["auto_play"] = False


def packet_step_forward():
    """Advances packet one hop along the discovered route."""
    res = st.session_state.get("sim_res")
    if res and res.get("success") and res.get("path"):
        if st.session_state["packet_hop"] < len(res["path"]) - 1:
            st.session_state["packet_hop"] += 1
        else:
            st.session_state["packet_auto"] = False


def reset_packet():
    """Resets packet position to source."""
    st.session_state["packet_hop"] = 0
    st.session_state["packet_auto"] = False


def get_active_state(graph: Graph) -> Dict[str, Any]:
    """
    Extracts current active elements at the current playback step and packet position.
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

            if not graph.routers.get(packet_node, None) or not graph.routers[packet_node].is_online:
                packet_status = f"Transmission BLOCKED: Router '{packet_node}' is offline! Rerun algorithm."
            elif p_hop == 0:
                packet_status = f"Packet buffered at Source '{packet_node}'. Ready for transmission."
            elif p_hop == len(path) - 1:
                packet_status = f"Packet successfully DELIVERED at Destination '{packet_node}'! (Total: {len(path) - 1} hops)."
            else:
                packet_status = f"In Transit: Hop {p_hop}/{len(path) - 1} • Currently at Router '{packet_node}'."

    return {
        "step": current_step,
        "res": res,
        "active_node": active_node,
        "active_edge": active_edge,
        "visited_nodes": visited_nodes,
        "explored_edges": explored_edges,
        "tree_edges": tree_edges,
        "route_nodes": route_nodes,
        "route_edges": route_edges,
        "packet_node": packet_node,
        "packet_status": packet_status
    }
