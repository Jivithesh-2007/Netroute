import streamlit as st
from network import Graph
from algorithms import bfs, dfs


def init():
    if "graph" not in st.session_state:
        g = Graph()
        g.load_preset("sample")
        st.session_state.graph = g
    if "res" not in st.session_state:
        st.session_state.res = None
    if "step_idx" not in st.session_state:
        st.session_state.step_idx = 0
    if "packet_hop" not in st.session_state:
        st.session_state.packet_hop = 0


def invalidate():
    st.session_state.res = None
    st.session_state.step_idx = 0
    st.session_state.packet_hop = 0


def run(graph: Graph, algo: str, src: str, dst: str):
    res = bfs(graph, src, dst) if "BFS" in algo else dfs(graph, src, dst)
    st.session_state.res = res
    st.session_state.step_idx = len(res["steps"]) - 1 if res.get("steps") else 0
    st.session_state.packet_hop = 0
    return res


def step_forward():
    res = st.session_state.get("res")
    if res and res.get("steps") and st.session_state.step_idx < len(res["steps"]) - 1:
        st.session_state.step_idx += 1


def step_backward():
    if st.session_state.get("step_idx", 0) > 0:
        st.session_state.step_idx -= 1


def reset_steps():
    st.session_state.step_idx = 0
    st.session_state.packet_hop = 0


def packet_step():
    res = st.session_state.get("res")
    if res and res.get("path") and st.session_state.packet_hop < len(res["path"]) - 1:
        st.session_state.packet_hop += 1


def packet_reset():
    st.session_state.packet_hop = 0


def get_active(graph: Graph):
    res = st.session_state.get("res")
    step = None
    if res and res.get("steps"):
        idx = max(0, min(st.session_state.step_idx, len(res["steps"]) - 1))
        step = res["steps"][idx]

    packet_node = None
    if res and res.get("path"):
        p_hop = st.session_state.get("packet_hop", 0)
        if 0 <= p_hop < len(res["path"]):
            packet_node = res["path"][p_hop]

    return {
        "step": step,
        "res": res,
        "active_node": step["node"] if step else None,
        "active_edge": step["edge"] if step else None,
        "visited": set(step["visited"]) if step else set(),
        "route": set(res["path"]) if (res and res.get("path")) else set(),
        "packet_node": packet_node
    }
