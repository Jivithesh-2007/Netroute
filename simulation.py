from typing import Optional, Dict, Any, List, Set, Tuple
import streamlit as st
from network import Graph
from algorithms import SimulationResult, SimulationStep, bfs_path, dfs_path


def init_session_state():
    if "graph" not in st.session_state:
        g = Graph(directed=False)
        g.load_preset("sample")
        st.session_state.graph = g

    if "sim_result" not in st.session_state:
        st.session_state.sim_result = None

    if "step_index" not in st.session_state:
        st.session_state.step_index = 0

    if "packet_hop" not in st.session_state:
        st.session_state.packet_hop = 0

    if "auto_play" not in st.session_state:
        st.session_state.auto_play = False

    if "packet_play" not in st.session_state:
        st.session_state.packet_play = False

    if "algo_choice" not in st.session_state:
        st.session_state.algo_choice = "BFS (Shortest-Hop)"

    if "source_id" not in st.session_state:
        st.session_state.source_id = "R1"

    if "dest_id" not in st.session_state:
        st.session_state.dest_id = "R6"


def invalidate_simulation():
    st.session_state.sim_result = None
    st.session_state.step_index = 0
    st.session_state.packet_hop = 0
    st.session_state.auto_play = False
    st.session_state.packet_play = False


def run_simulation(graph: Graph, algo_name: str, source: str, dest: str) -> SimulationResult:
    if "BFS" in algo_name:
        result = bfs_path(graph, source, dest)
    else:
        result = dfs_path(graph, source, dest)

    st.session_state.sim_result = result
    st.session_state.step_index = len(result.steps) - 1 if result.steps else 0
    st.session_state.packet_hop = 0
    st.session_state.auto_play = False
    st.session_state.packet_play = False
    return result


def step_forward():
    res: Optional[SimulationResult] = st.session_state.get("sim_result")
    if res and res.steps:
        if st.session_state.step_index < len(res.steps) - 1:
            st.session_state.step_index += 1
        else:
            st.session_state.auto_play = False


def step_backward():
    res: Optional[SimulationResult] = st.session_state.get("sim_result")
    if res and res.steps:
        if st.session_state.step_index > 0:
            st.session_state.step_index -= 1


def jump_to_step(idx: int):
    res: Optional[SimulationResult] = st.session_state.get("sim_result")
    if res and res.steps:
        st.session_state.step_index = max(0, min(idx, len(res.steps) - 1))


def reset_playback():
    st.session_state.step_index = 0
    st.session_state.packet_hop = 0
    st.session_state.auto_play = False
    st.session_state.packet_play = False


def packet_step_forward():
    res: Optional[SimulationResult] = st.session_state.get("sim_result")
    if res and res.success and res.path:
        if st.session_state.packet_hop < len(res.path) - 1:
            st.session_state.packet_hop += 1
        else:
            st.session_state.packet_play = False


def reset_packet():
    st.session_state.packet_hop = 0
    st.session_state.packet_play = False


def get_current_step() -> Optional[SimulationStep]:
    res: Optional[SimulationResult] = st.session_state.get("sim_result")
    if not res or not res.steps:
        return None
    idx = max(0, min(st.session_state.get("step_index", 0), len(res.steps) - 1))
    return res.steps[idx]


def get_active_elements(graph: Graph) -> Dict[str, Any]:
    res: Optional[SimulationResult] = st.session_state.get("sim_result")
    step = get_current_step()

    active_router: Optional[str] = None
    active_edge: Optional[Tuple[str, str]] = None
    visited_routers: Set[str] = set()
    explored_edges: Set[Tuple[str, str]] = set()
    tree_edges: List[Tuple[str, str]] = []
    final_route_edges: List[Tuple[str, str]] = []
    route_routers: Set[str] = set()
    packet_node: Optional[str] = None

    if res:
        if res.success and res.path:
            route_routers = set(res.path)
            for i in range(len(res.path) - 1):
                final_route_edges.append(tuple(sorted((res.path[i], res.path[i + 1]))))

            # Current packet location
            p_hop = st.session_state.get("packet_hop", 0)
            if 0 <= p_hop < len(res.path):
                packet_node = res.path[p_hop]

        if step:
            active_router = step.current_element
            active_edge = step.active_edge
            visited_routers = set(step.visited_elements)

            # Accumulate explored edges up to current step
            curr_idx = st.session_state.get("step_index", 0)
            for s in res.steps[:curr_idx + 1]:
                if s.active_edge:
                    explored_edges.add(tuple(sorted(s.active_edge)))

            # Tree edges up to this step from parent map
            for child, par in step.parent_map.items():
                if par is not None:
                    tree_edges.append(tuple(sorted((par, child))))
        else:
            visited_routers = set(res.visited_order)
            explored_edges = set(res.explored_edges)
            tree_edges = list(res.tree_edges)

    return {
        "active_router": active_router,
        "active_edge": active_edge,
        "visited_routers": visited_routers,
        "explored_edges": explored_edges,
        "tree_edges": tree_edges,
        "route_routers": route_routers,
        "final_route_edges": final_route_edges,
        "packet_node": packet_node,
        "current_step": step,
        "result": res
    }
