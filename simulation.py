"""
simulation.py — Simulation State, Playback Progression, and Packet Transmission Engine.

Maintains session state in Streamlit for:
- Routing algorithm execution results (BFS and DFS).
- Step-by-step traversal playback.
- Hop-by-hop packet transmission along discovered routes.
- Traditional routing-table forwarding simulation (CO5).
"""

from typing import Dict, Any, Optional, Set, List, Tuple
import streamlit as st
from network import Graph
from algorithms import bfs, dfs


def init_session():
    """Initializes standard session state variables if not already initialized."""
    if "graph" not in st.session_state:
        g = Graph()
        g.load_preset("reference")
        st.session_state["graph"] = g

    if "selected_preset" not in st.session_state:
        st.session_state["selected_preset"] = "reference"

    if "sim_res" not in st.session_state:
        st.session_state["sim_res"] = None

    if "step_idx" not in st.session_state:
        st.session_state["step_idx"] = 0

    if "is_playing" not in st.session_state:
        st.session_state["is_playing"] = False

    if "packet_hop" not in st.session_state:
        st.session_state["packet_hop"] = 0

    if "packet_auto" not in st.session_state:
        st.session_state["packet_auto"] = False

    if "selected_algo" not in st.session_state:
        st.session_state["selected_algo"] = "BFS (Breadth-First)"

    if "search_res" not in st.session_state:
        st.session_state["search_res"] = None

    if "search_step_idx" not in st.session_state:
        st.session_state["search_step_idx"] = 0

    if "sort_res" not in st.session_state:
        st.session_state["sort_res"] = None

    if "table_fwd_res" not in st.session_state:
        st.session_state["table_fwd_res"] = None

    g_nodes = list(st.session_state["graph"].routers.keys())
    if "source_id" not in st.session_state or st.session_state["source_id"] not in st.session_state["graph"].routers:
        st.session_state["source_id"] = "N1" if "N1" in st.session_state["graph"].routers else (g_nodes[0] if g_nodes else "N1")

    if "dest_id" not in st.session_state or st.session_state["dest_id"] not in st.session_state["graph"].routers:
        st.session_state["dest_id"] = "N7" if "N7" in st.session_state["graph"].routers else (g_nodes[-1] if g_nodes else "N7")


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
    st.session_state["search_res"] = None
    st.session_state["search_step_idx"] = 0
    st.session_state["sort_res"] = None
    st.session_state["table_fwd_res"] = None


def execute_routing(graph: Graph, algo: str, src: str, dst: str) -> Dict[str, Any]:
    """Runs genuine BFS or DFS, stores steps, and starts playback from step 0."""
    if "DFS" in algo:
        res = dfs(graph, src, dst)
    else:
        res = bfs(graph, src, dst)

    st.session_state["sim_res"] = res
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


def reset_playback():
    """Resets playback index to step 0."""
    st.session_state["step_idx"] = 0
    st.session_state["is_playing"] = False


def reset_simulation():
    """Completely resets the simulation state."""
    invalidate_simulation()


def packet_step_forward():
    """Advances packet position one hop forward along the discovered route."""
    res = st.session_state.get("sim_res")
    if res and res.get("success") and res.get("path"):
        path = res["path"]
        curr_hop = st.session_state.get("packet_hop", 0)
        if curr_hop < len(path) - 1:
            st.session_state["packet_hop"] = curr_hop + 1


def reset_packet():
    """Resets the packet back to the source router (Hop 0)."""
    st.session_state["packet_hop"] = 0
    st.session_state["packet_auto"] = False


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

        for s in res["steps"][:idx + 1]:
            if s.get("active_edge"):
                explored_edges.add(tuple(sorted(s["active_edge"])))

        for child, par in current_step.get("parents", {}).items():
            if par is not None:
                tree_edges.append(tuple(sorted((par, child))))

    if res and res.get("success") and res.get("path") and is_completed:
        path = res["path"]
        route_nodes = set(path)
        for i in range(len(path) - 1):
            route_edges.append(tuple(sorted((path[i], path[i + 1]))))

    if res and res.get("success") and res.get("path"):
        path = res["path"]
        p_hop = st.session_state.get("packet_hop", 0)
        if 0 <= p_hop < len(path):
            packet_node = path[p_hop]
            if p_hop + 1 < len(path):
                next_packet_node = path[p_hop + 1]

            if not graph.routers.get(packet_node) or not graph.routers[packet_node].is_online:
                packet_status = f"Transmission BLOCKED: Router '{packet_node}' is offline."
            elif p_hop == 0:
                packet_status = f"Packet buffered at Source '{packet_node}' (Hop 0). Ready for transmission."
            elif p_hop == len(path) - 1:
                packet_status = f"Packet DELIVERED to Destination '{packet_node}' in {len(path) - 1} hops."
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


def simulate_table_forwarding(graph: Graph, src: str, dst: str, max_hops: int = 25) -> Dict[str, Any]:
    """
    Simulates traditional hop-by-hop packet forwarding using local router routing tables.
    
    Demonstrates CO5:
    - Graph-Based Routing: Centralized global path computation using graph traversal (BFS/DFS).
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
                "description": f"Source '{src_clean}' is identical to destination. Packet processed locally."
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

        if not graph.is_edge_active(curr, nxt):
            status = "LINK_SEVERED"
            failure_message = f"Forwarding failure at '{curr}': Physical link ({curr} <-> {nxt}) is severed."
            steps.append({
                "step": step_num,
                "current_router": curr,
                "next_hop": nxt,
                "action": "LINK_DOWN",
                "table_entry": matching_entry,
                "description": failure_message
            })
            break

        if nxt in visited_set:
            status = "ROUTING_LOOP"
            failure_message = f"Routing loop detected: packet forwarded back to visited router '{nxt}'."
            steps.append({
                "step": step_num,
                "current_router": curr,
                "next_hop": nxt,
                "action": "LOOP_DETECTED",
                "table_entry": matching_entry,
                "description": failure_message
            })
            break

        steps.append({
            "step": step_num,
            "current_router": curr,
            "next_hop": nxt,
            "action": "FORWARD",
            "table_entry": matching_entry,
            "description": f"Hop {step_num}: Router '{curr}' looked up destination '{dst_clean}' -> Next Hop '{nxt}' ({matching_entry['hops']} metric hops)."
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
