"""
main.py — NetRoute: Interactive Network Packet-Routing Simulator.

Demonstrates:
- CO1: Stack and Queue Data Structures (FIFO Queue vs. LIFO Stack).
- CO2: Dynamic Graph Operations (Insertion, Deletion, Rename, Fault Toggle).
- CO5: Graph Traversals, Traversal Trees, Route Reconstruction, and Packet Forwarding.
"""

import time
import json
from typing import Dict, Any, List, Set, Tuple

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import (
    CUSTOM_CSS, render_metric_card, render_step_card,
    PRIMARY, PRIMARY_DARK, CYAN, PURPLE, SUCCESS, WARNING, ERROR, TEXT_MAIN, TEXT_MUTED, BORDER,
    COLOR_NODE_DEFAULT, COLOR_NODE_SOURCE, COLOR_NODE_DEST,
    COLOR_NODE_VISITED, COLOR_NODE_ACTIVE, COLOR_NODE_ROUTE, COLOR_NODE_OFFLINE, COLOR_PACKET,
    COLOR_EDGE_DEFAULT, COLOR_EDGE_EXPLORED, COLOR_EDGE_ROUTE, COLOR_EDGE_ACTIVE, COLOR_EDGE_TREE
)
from network import Graph, Router, validate_router_id
from algorithms import bfs, dfs, reconstruct_route_from_parents
import simulation as sim

# -------------------------------------------------------------
# 1. PAGE SETUP & THEME INITIALIZATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="NetRoute - Network Packet-Routing Simulator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
sim.init_session()
graph: Graph = st.session_state["graph"]


# -------------------------------------------------------------
# 2. PLOTLY GRAPH VISUALIZATION ENGINE
# -------------------------------------------------------------
def build_network_figure(graph: Graph, active: Dict[str, Any], src_id: str, dst_id: str) -> go.Figure:
    """Renders a responsive Plotly visualization of the network graph."""
    fig = go.Figure()

    if not graph.routers:
        fig.add_annotation(
            text="Network is empty. Add routers or load a preset in the Topology Editor.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=TEXT_MUTED)
        )
        fig.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=480,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig

    active_node = active.get("active_node")
    active_edge = active.get("active_edge")
    visited_nodes = active.get("visited_nodes", set())
    explored_edges = active.get("explored_edges", set())
    route_nodes = active.get("route_nodes", set())
    route_edges = active.get("route_edges", [])
    packet_node = active.get("packet_node")

    # A. Draw Normal (Unvisited) Links
    norm_x, norm_y = [], []
    for u, v in graph.get_edges():
        e = tuple(sorted((u, v)))
        if e not in route_edges and e not in explored_edges and (active_edge is None or e != tuple(sorted(active_edge))):
            if u in graph.routers and v in graph.routers:
                norm_x.extend([graph.routers[u].x, graph.routers[v].x, None])
                norm_y.extend([graph.routers[u].y, graph.routers[v].y, None])

    if norm_x:
        fig.add_trace(go.Scatter(
            x=norm_x, y=norm_y, mode="lines",
            line=dict(color=COLOR_EDGE_DEFAULT, width=2),
            hoverinfo="none", name="Normal Link", showlegend=True
        ))

    # B. Draw Explored Links (Traversed during algorithm execution)
    exp_x, exp_y = [], []
    for u, v in explored_edges:
        e = tuple(sorted((u, v)))
        if e not in route_edges and (active_edge is None or e != tuple(sorted(active_edge))):
            if u in graph.routers and v in graph.routers:
                exp_x.extend([graph.routers[u].x, graph.routers[v].x, None])
                exp_y.extend([graph.routers[u].y, graph.routers[v].y, None])

    if exp_x:
        fig.add_trace(go.Scatter(
            x=exp_x, y=exp_y, mode="lines",
            line=dict(color=COLOR_EDGE_EXPLORED, width=2.8, dash="dot"),
            hoverinfo="none", name="Explored Link", showlegend=True
        ))

    # C. Draw Discovered Route Links (Thick Vibrant Green)
    rt_x, rt_y = [], []
    for u, v in route_edges:
        if u in graph.routers and v in graph.routers:
            rt_x.extend([graph.routers[u].x, graph.routers[v].x, None])
            rt_y.extend([graph.routers[u].y, graph.routers[v].y, None])

    if rt_x:
        fig.add_trace(go.Scatter(
            x=rt_x, y=rt_y, mode="lines",
            line=dict(color=COLOR_EDGE_ROUTE, width=5),
            hoverinfo="none", name="Discovered Route", showlegend=True
        ))

    # D. Draw Current Active Hop Link (Hop currently being traversed in this step)
    if active_edge:
        u, v = active_edge
        if u in graph.routers and v in graph.routers:
            fig.add_trace(go.Scatter(
                x=[graph.routers[u].x, graph.routers[v].x],
                y=[graph.routers[u].y, graph.routers[v].y],
                mode="lines",
                line=dict(color=COLOR_EDGE_ACTIVE, width=5),
                hoverinfo="none", name="Active Hop Link", showlegend=True
            ))

    # E. Draw Router Nodes
    nodes = sorted(graph.routers.keys())
    node_x, node_y, node_labels, node_colors, border_colors, hover_texts = [], [], [], [], [], []

    for rid in nodes:
        r = graph.routers[rid]
        node_x.append(r.x)
        node_y.append(r.y)
        node_labels.append(rid)

        # Visual hierarchy for node coloring
        if not r.is_online:
            fill_c = COLOR_NODE_OFFLINE
            border_c = "#475569"
        elif rid == active_node:
            fill_c = COLOR_NODE_ACTIVE
            border_c = "#4C1D95"
        elif rid == src_id:
            fill_c = COLOR_NODE_SOURCE
            border_c = "#065F46"
        elif rid == dst_id:
            fill_c = COLOR_NODE_DEST
            border_c = "#9A3412"
        elif rid in route_nodes:
            fill_c = COLOR_NODE_ROUTE
            border_c = "#064E3B"
        elif rid in visited_nodes:
            fill_c = COLOR_NODE_VISITED
            border_c = "#0284C7"
        else:
            fill_c = COLOR_NODE_DEFAULT
            border_c = "#1E40AF"

        node_colors.append(fill_c)
        border_colors.append(border_c)

        status_str = "Online" if r.is_online else "Offline"
        nbrs = sorted(graph.adjacency.get(rid, []))
        nbr_str = ", ".join(nbrs) if nbrs else "None"
        ht = (
            f"<b>Router {rid}</b> ({r.name})<br>"
            f"Status: {status_str}<br>"
            f"Degree (Links): {len(nbrs)}<br>"
            f"Neighbors: {nbr_str}"
        )
        hover_texts.append(ht)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=36, color=node_colors, line=dict(color=border_colors, width=2.5)),
        text=node_labels,
        textposition="middle center",
        textfont=dict(
            family="-apple-system, BlinkMacSystemFont, sans-serif",
            size=11,
            color=["#FFFFFF" if c not in ("#FFFFFF", COLOR_NODE_VISITED) else TEXT_MAIN for c in node_colors]
        ),
        hoverinfo="text", hovertext=hover_texts, name="Routers", showlegend=False
    ))

    # F. Draw Packet Indicator
    if packet_node and packet_node in graph.routers:
        pr = graph.routers[packet_node]
        fig.add_trace(go.Scatter(
            x=[pr.x], y=[pr.y],
            mode="markers+text",
            marker=dict(size=48, symbol="circle-open", color=COLOR_PACKET, line=dict(color=COLOR_PACKET, width=3.5)),
            text=["PACKET"], textposition="top center",
            textfont=dict(size=10, color=COLOR_PACKET, family="-apple-system, sans-serif"),
            hoverinfo="text", hovertext=f"<b>Packet In-Transit</b><br>Currently at Router {packet_node}",
            name="Packet", showlegend=True
        ))

    # Viewport boundaries with consistent margin
    all_x = [r.x for r in graph.routers.values()]
    all_y = [r.y for r in graph.routers.values()]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    dx = max(80.0, max_x - min_x)
    dy = max(80.0, max_y - min_y)

    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=480,
        margin=dict(l=20, r=20, t=30, b=20), hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=TEXT_MUTED)),
        xaxis=dict(range=[min_x - dx * 0.15, max_x + dx * 0.15], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[max_y + dy * 0.18, min_y - dy * 0.18], showgrid=False, zeroline=False, showticklabels=False)
    )
    return fig


# -------------------------------------------------------------
# 3. TOP HEADER BAR WITH CONTROLS & STATUS
# -------------------------------------------------------------
sim_status = sim.get_simulation_status()
status_class = {
    "Ready": "badge-status-ready",
    "Running": "badge-status-running",
    "Paused": "badge-status-running",
    "Completed": "badge-status-completed",
    "No Route": "badge-status-blocked"
}.get(sim_status, "badge-status-ready")

total_r = len(graph.routers)
online_r = sum(1 for r in graph.routers.values() if r.is_online)
total_e = len(graph.get_edges())

head_c1, head_c2, head_c3 = st.columns([5, 3.2, 1.8])
with head_c1:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px;">
            <h2 style="margin:0; font-size:1.65rem; font-weight:800; color:{PRIMARY}; letter-spacing:-0.02em;">NetRoute</h2>
            <span style="color:{BORDER}; font-size:1.4rem;">|</span>
            <span style="font-size:0.95rem; font-weight:600; color:{TEXT_MUTED};">Interactive Network Routing Laboratory</span>
            <span class="badge-pill {status_class}" style="margin-left:6px;">[{sim_status.upper()}]</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with head_c2:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; align-items:center; gap:8px; padding-top:6px;">
            <span class="badge-pill" style="color:{TEXT_MAIN}; background:#F1F5F9;">{total_r} Routers ({online_r} Online)</span>
            <span class="badge-pill" style="color:{TEXT_MAIN}; background:#F1F5F9;">{total_e} Links</span>
            <span class="badge-pill" style="color:{PRIMARY};">CO1</span>
            <span class="badge-pill" style="color:{CYAN};">CO2</span>
            <span class="badge-pill" style="color:{SUCCESS};">CO5</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with head_c3:
    if st.button("Reset Simulation", width="stretch"):
        sim.reset_simulation()
        sim.invalidate_simulation()
        st.rerun()

st.write("")

# -------------------------------------------------------------
# 4. PRIMARY APPLICATION TABS (MANDATORY PANELS)
# -------------------------------------------------------------
tab_vis, tab_queue_stack, tab_log, tab_route, tab_topo, tab_compare, tab_theory = st.tabs([
    "Network Visualization",
    "Queue & Stack Inspector",
    "Traversal Log",
    "Route Analysis",
    "Topology Editor",
    "Algorithm Comparison",
    "Academic Viva Guide"
])


# =============================================================
# TAB 1: NETWORK VISUALIZATION & SIMULATION WORKSPACE
# =============================================================
with tab_vis:
    r_keys = sorted(graph.routers.keys())

    # Control Bar
    cb1, cb2, cb3, cb4, cb5 = st.columns([2.5, 1.8, 1.8, 2.2, 1.7])
    with cb1:
        algo_choice = st.selectbox(
            "Algorithm",
            options=["BFS (Shortest-Hop)", "DFS (Path Discovery)"],
            index=0 if "BFS" in st.session_state["selected_algo"] else 1,
            label_visibility="collapsed"
        )
        if algo_choice != st.session_state["selected_algo"]:
            st.session_state["selected_algo"] = algo_choice
            sim.invalidate_simulation()

    with cb2:
        def_s = r_keys.index(st.session_state["source_id"]) if st.session_state["source_id"] in r_keys else 0
        src_sel = st.selectbox("Source Router", options=r_keys, index=def_s if r_keys else 0, label_visibility="collapsed")
        if src_sel != st.session_state["source_id"]:
            st.session_state["source_id"] = src_sel
            sim.invalidate_simulation()

    with cb3:
        def_d = r_keys.index(st.session_state["dest_id"]) if st.session_state["dest_id"] in r_keys else (len(r_keys) - 1 if r_keys else 0)
        dst_sel = st.selectbox("Destination Router", options=r_keys, index=def_d if r_keys else 0, label_visibility="collapsed")
        if dst_sel != st.session_state["dest_id"]:
            st.session_state["dest_id"] = dst_sel
            sim.invalidate_simulation()

    with cb4:
        if st.button("Run Simulation", type="primary", width="stretch"):
            sim.execute_routing(graph, algo_choice, src_sel, dst_sel)
            st.rerun()

    with cb5:
        speed_sel = st.selectbox(
            "Playback Speed",
            options=["Slow", "Normal", "Fast"],
            index=["Slow", "Normal", "Fast"].index(st.session_state.get("playback_speed", "Normal")),
            label_visibility="collapsed"
        )
        st.session_state["playback_speed"] = speed_sel

    # Active State & Metrics
    active_state = sim.get_active_state(graph)
    current_step = active_state.get("step")
    sim_res = active_state.get("res")

    visited_count = len(active_state.get("visited_nodes", []))
    hops_display = f"{sim_res['hops']} hops" if (sim_res and sim_res.get("success")) else ("0 hops" if (sim_res and sim_res.get("hops") == 0) else "None")
    total_steps = len(sim_res.get("steps", [])) if (sim_res and sim_res.get("steps")) else 0
    curr_step_idx = st.session_state.get("step_idx", 0)

    # Metric Cards Row
    mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
    with mc1:
        st.markdown(render_metric_card("Routers", f"{total_r}", f"{online_r} online", PRIMARY), unsafe_allow_html=True)
    with mc2:
        st.markdown(render_metric_card("Links", f"{total_e}", "Undirected edges", CYAN), unsafe_allow_html=True)
    with mc3:
        st.markdown(render_metric_card("Visited", f"{visited_count}", f"of {total_r} vertices", CYAN), unsafe_allow_html=True)
    with mc4:
        sub_hops = "Shortest path" if (sim_res and "BFS" in sim_res.get("algorithm", "")) else "Reachable path"
        st.markdown(render_metric_card("Route Hops", hops_display, sub_hops, SUCCESS if (sim_res and sim_res.get("success")) else TEXT_MUTED), unsafe_allow_html=True)
    with mc5:
        peak_str = str(sim_res.get("max_structure", "0")) if sim_res else "0"
        st.markdown(render_metric_card("Max Capacity", peak_str, "Peak queue/stack", PURPLE), unsafe_allow_html=True)
    with mc6:
        prog_str = f"Step {curr_step_idx + 1} / {total_steps}" if total_steps else "Ready"
        st.markdown(render_metric_card("Progress", prog_str, sim_status, SUCCESS if sim_status == "Completed" else PRIMARY), unsafe_allow_html=True)

    st.write("")

    # Interactive Graph
    fig = build_network_figure(graph, active_state, st.session_state["source_id"], st.session_state["dest_id"])
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": True, "scrollZoom": True})

    # Playback Toolbar
    if sim_res and sim_res.get("steps"):
        pb1, pb2, pb3, pb4, pb5, pb6, pb7 = st.columns([1, 1, 1.4, 1, 1, 1, 3.5])
        with pb1:
            if st.button("First", width="stretch", disabled=(curr_step_idx == 0)):
                sim.first_step()
                st.rerun()
        with pb2:
            if st.button("Back", width="stretch", disabled=(curr_step_idx == 0)):
                sim.step_backward()
                st.rerun()
        with pb3:
            play_label = "Pause" if st.session_state.get("is_playing", False) else "Play"
            if st.button(play_label, width="stretch", type="primary" if not st.session_state.get("is_playing") else "secondary"):
                sim.toggle_playback()
                st.rerun()
        with pb4:
            if st.button("Next", width="stretch", disabled=(curr_step_idx >= total_steps - 1)):
                sim.step_forward()
                st.rerun()
        with pb5:
            if st.button("End", width="stretch", disabled=(curr_step_idx >= total_steps - 1)):
                sim.last_step()
                st.rerun()
        with pb6:
            if st.button("Reset", width="stretch"):
                sim.reset_simulation()
                st.rerun()
        with pb7:
            scrub_step = st.slider(
                "Scrub Algorithm Step", min_value=0, max_value=total_steps - 1,
                value=curr_step_idx, label_visibility="collapsed"
            )
            if scrub_step != curr_step_idx:
                sim.jump_to_step(scrub_step)
                st.rerun()

    # Step Explanation & Quick Inspector Row
    st.markdown("---")
    info_c1, info_c2, info_c3 = st.columns([3.2, 3.6, 3.2])

    # Left: Step Detail Box
    with info_c1:
        st.markdown("##### Current Traversal Step")
        if current_step:
            st.markdown(
                render_step_card(
                    current_step['step'],
                    current_step['operation'],
                    current_step['description'],
                    PURPLE if current_step['operation'] == 'BACKTRACK' else (SUCCESS if 'FOUND' in current_step['operation'] or 'COMPLETE' in current_step['operation'] else PRIMARY)
                ),
                unsafe_allow_html=True
            )
            if current_step.get("active_edge"):
                u_ed, v_ed = current_step["active_edge"]
                st.caption(f"Active Link Explored: **{u_ed} <-> {v_ed}**")
        elif sim_res:
            if sim_res.get("success"):
                st.success(f"Discovered Route: {' -> '.join(sim_res['path'])} ({sim_res['hops']} hops)")
            else:
                st.error(sim_res.get("message"))
        else:
            st.caption("Select endpoints and click **Run Simulation** above to begin.")

    # Center: Queue / Stack Quick View
    with info_c2:
        is_bfs = "BFS" in st.session_state.get("selected_algo", "")
        struct_title = "FIFO Queue (BFS)" if is_bfs else "LIFO Stack (DFS)"
        st.markdown(f"##### {struct_title}")

        if current_step:
            items = current_step.get("structure", [])
            target = current_step.get("action_target")
            st.caption(f"Current Items: **{len(items)}** | Peak Capacity: **{sim_res.get('max_structure', 0)}**")

            if not items:
                st.caption(f"*{struct_title} is currently empty.*")
            else:
                chips_html = []
                if is_bfs:
                    for i, it in enumerate(items):
                        extra_cls = " chip-active" if it == target else ""
                        if i == 0 and len(items) == 1:
                            chips_html.append(f'<span class="chip chip-front{extra_cls}">FRONT & REAR: {it}</span>')
                        elif i == 0:
                            chips_html.append(f'<span class="chip chip-front{extra_cls}">FRONT: {it}</span>')
                        elif i == len(items) - 1:
                            chips_html.append(f'<span class="chip chip-rear{extra_cls}">REAR: {it}</span>')
                        else:
                            chips_html.append(f'<span class="chip chip-item{extra_cls}">{it}</span>')
                    st.markdown(f'<div>{" -> ".join(chips_html)}</div>', unsafe_allow_html=True)
                else:
                    for i, it in enumerate(items):
                        extra_cls = " chip-active" if it == target else ""
                        if i == len(items) - 1 and len(items) == 1:
                            chips_html.append(f'<span class="chip chip-top{extra_cls}">TOP & BOT: {it}</span>')
                        elif i == len(items) - 1:
                            chips_html.append(f'<span class="chip chip-top{extra_cls}">TOP: {it}</span>')
                        elif i == 0:
                            chips_html.append(f'<span class="chip chip-bot{extra_cls}">BOTTOM: {it}</span>')
                        else:
                            chips_html.append(f'<span class="chip chip-item{extra_cls}">{it}</span>')
                    st.markdown(f'<div>{" | ".join(chips_html)}</div>', unsafe_allow_html=True)

            v_list = current_step.get("visited", [])
            if v_list:
                v_chips = [f'<span class="chip chip-visited">{n}</span>' for n in v_list]
                st.markdown(f'<div style="margin-top:6px;"><b>Visited Order:</b> {" -> ".join(v_chips)}</div>', unsafe_allow_html=True)
        else:
            st.caption("Awaiting simulation execution.")

    # Right: Packet Transmission Controls
    with info_c3:
        st.markdown("##### Packet Transmission Engine (CO5)")
        if sim_res and sim_res.get("success") and sim_res.get("path"):
            path = sim_res["path"]
            p_hop = st.session_state.get("packet_hop", 0)

            pkt_c1, pkt_c2, pkt_c3 = st.columns(3)
            with pkt_c1:
                if st.button("Step Hop", width="stretch", disabled=(p_hop >= len(path) - 1)):
                    sim.packet_step_forward()
                    st.rerun()
            with pkt_c2:
                stream_lbl = "Pause" if st.session_state.get("packet_auto") else "Auto-Stream"
                if st.button(stream_lbl, width="stretch"):
                    sim.toggle_packet_stream()
                    st.rerun()
            with pkt_c3:
                if st.button("Reset Hop", width="stretch"):
                    sim.reset_packet()
                    st.rerun()

            st.caption(f"**Hop {p_hop} of {len(path) - 1}:** {active_state.get('packet_status')}")
            pkt_progress = p_hop / max(1, len(path) - 1)
            st.progress(pkt_progress)
        else:
            st.caption("Packet forwarding engine unlocks when a valid route is discovered.")


# =============================================================
# TAB 2: QUEUE AND STACK INSPECTOR (CO1)
# =============================================================
with tab_queue_stack:
    st.markdown("### Queue and Stack Live Data Structure Inspector (CO1)")
    st.caption("Demonstrating real-time FIFO queue vs. LIFO stack mechanics during graph traversal.")

    active_state = sim.get_active_state(graph)
    current_step = active_state.get("step")
    sim_res = active_state.get("res")
    is_bfs = "BFS" in st.session_state.get("selected_algo", "")

    ds_c1, ds_c2 = st.columns([1, 1])

    with ds_c1:
        st.markdown(f"#### Current Data Structure: **{'FIFO Queue' if is_bfs else 'LIFO Stack'}**")
        if is_bfs:
            st.info(
                "**First-In-First-Out (FIFO) Queue:** Elements are enqueued at the **REAR** and dequeued from the **FRONT**. "
                "Because BFS explores routers layer-by-layer (distance 0, 1, 2...), the first time the destination is reached, "
                "it is mathematically guaranteed to be the minimum-hop path."
            )
        else:
            st.info(
                "**Last-In-First-Out (LIFO) Stack:** Elements are pushed and popped exclusively from the **TOP**. "
                "DFS explores as deep as possible along a single branch before hitting a dead end and backtracking. "
                "DFS discovers a valid reachable path, but does NOT guarantee minimum hops."
            )

        if current_step:
            items = current_step.get("structure", [])
            target = current_step.get("action_target")
            st.markdown("##### Internal Structure Elements")
            if not items:
                st.warning("Data structure is currently empty.")
            else:
                for idx, it in enumerate(items):
                    tag = ""
                    if is_bfs:
                        if idx == 0 and len(items) == 1:
                            tag = " [FRONT & REAR]"
                        elif idx == 0:
                            tag = " [FRONT]"
                        elif idx == len(items) - 1:
                            tag = " [REAR]"
                    else:
                        if idx == len(items) - 1 and len(items) == 1:
                            tag = " [TOP & BOTTOM]"
                        elif idx == len(items) - 1:
                            tag = " [TOP]"
                        elif idx == 0:
                            tag = " [BOTTOM]"

                    active_marker = " <-- ACTIVE TARGET" if it == target else ""
                    st.markdown(f"- Index **{idx}**: Router **{it}**{tag}{active_marker}")

    with ds_c2:
        st.markdown("#### Operation Counters & Peak Metrics")
        if current_step and sim_res:
            oc1, oc2 = st.columns(2)
            with oc1:
                if is_bfs:
                    st.metric("Total Enqueues", f"{current_step.get('enqueues', 0)}")
                    st.metric("Current Queue Size", f"{len(current_step.get('structure', []))}")
                else:
                    st.metric("Total Pushes", f"{current_step.get('pushes', 0)}")
                    st.metric("Current Stack Size", f"{len(current_step.get('structure', []))}")
            with oc2:
                if is_bfs:
                    st.metric("Total Dequeues", f"{current_step.get('dequeues', 0)}")
                    st.metric("Peak Queue Size", f"{sim_res.get('max_structure', 0)}")
                else:
                    st.metric("Total Pops", f"{current_step.get('pops', 0)}")
                    st.metric("Peak Stack Size", f"{sim_res.get('max_structure', 0)}")

            if not is_bfs:
                st.markdown("---")
                st.markdown(f"**Backtracking Occurrences:** `{sim_res.get('backtrack_count', 0)}`")
                if current_step.get("is_backtrack"):
                    st.warning(f"Backtracking Active: Dead end encountered at '{current_step.get('current_node')}'. Backtracking to next candidate on stack.")
        else:
            st.info("Run an algorithm in the Network Visualization tab to inspect live data structure operations.")

    st.markdown("---")
    st.markdown("#### Chronological Visited Order")
    if current_step and current_step.get("visited"):
        v_seq = current_step.get("visited", [])
        v_df = pd.DataFrame([
            {"Order": i + 1, "Router ID": rid, "Router Label": graph.routers[rid].name if rid in graph.routers else "N/A"}
            for i, rid in enumerate(v_seq)
        ])
        st.dataframe(v_df, width="stretch", height=200)
    else:
        st.caption("No routers visited yet.")


# =============================================================
# TAB 3: TRAVERSAL LOG
# =============================================================
with tab_log:
    st.markdown("### Step-by-Step Traversal Execution Log")
    st.caption("Comprehensive log of all operations performed during the algorithm run.")

    if sim_res and sim_res.get("steps"):
        log_rows = []
        for s in sim_res["steps"]:
            items_str = ", ".join(s.get("structure", [])) if s.get("structure") else "Empty"
            visited_str = " -> ".join(s.get("visited", [])) if s.get("visited") else "None"
            edge_str = f"{s['active_edge'][0]} <-> {s['active_edge'][1]}" if s.get("active_edge") else "-"
            log_rows.append({
                "Step": s["step"],
                "Operation": s["operation"],
                "Active Router": s.get("current_node") or "-",
                "Active Target": s.get("action_target") or "-",
                "Queue/Stack State": items_str,
                "Visited Order": visited_str,
                "Traversed Link": edge_str,
                "Description": s["description"]
            })
        log_df = pd.DataFrame(log_rows)
        st.dataframe(log_df, width="stretch", height=380)

        st.download_button(
            "Download Traversal Log (CSV)",
            data=log_df.to_csv(index=False),
            file_name=f"netroute_traversal_log_{st.session_state['selected_algo'][:3]}.csv",
            mime="text/csv",
            width="stretch"
        )
    else:
        st.info("Run a routing simulation to generate the traversal execution log.")


# =============================================================
# TAB 4: ROUTE ANALYSIS & DIAGNOSTICS (CO5)
# =============================================================
with tab_route:
    st.markdown("### Route Reconstruction & Network Diagnostics (CO5)")
    st.caption("Detailed breakdown of parent pointer reconstruction, network reachability, and packet scheduling.")

    ra_c1, ra_c2 = st.columns([1, 1])

    with ra_c1:
        st.markdown("#### 1. Route Reconstruction via Parent Pointers")
        st.caption("Parent pointers recorded during discovery allow backward tracing from Destination to Source in O(L) time.")

        if sim_res and sim_res.get("success") and sim_res.get("path"):
            path = sim_res["path"]
            parents = sim_res.get("parents", {})

            # Tracing backward
            trace_steps = []
            curr = path[-1]
            while curr is not None:
                p = parents.get(curr)
                trace_steps.append({"Current Router": curr, "Predecessor (Parent Pointer)": p if p else "None (Source)"})
                curr = p

            st.dataframe(pd.DataFrame(trace_steps), width="stretch", height=200)
            st.success(f"**Discovered Path:** {' -> '.join(path)} ({len(path) - 1} hops)")
        elif sim_res:
            st.error(sim_res.get("message"))
        else:
            st.info("Run a simulation to view route reconstruction.")

    with ra_c2:
        st.markdown("#### 2. Network Reachability & Subnet Analysis")
        comps = graph.get_connected_components()
        is_conn = graph.is_connected()

        st.markdown(f"**Connected Components (Subnets):** `{len(comps)}`")
        for i, comp in enumerate(comps):
            c_str = ", ".join(sorted(list(comp)))
            st.markdown(f"- **Subnet {i+1}:** `[{c_str}]`")

        src = st.session_state.get("source_id")
        dst = st.session_state.get("dest_id")
        if src in graph.routers and dst in graph.routers:
            reachable = graph.is_reachable(src, dst)
            if reachable:
                st.success(f"Reachable: An online path exists between '{src}' and '{dst}'.")
            else:
                st.error(f"Unreachable: No online path exists between '{src}' and '{dst}' (partitioned network or offline router barrier).")

    st.markdown("---")
    st.markdown("#### 3. Hop-by-Hop Packet Forwarding Schedule")
    if sim_res and sim_res.get("success") and sim_res.get("path"):
        path = sim_res["path"]
        fwd_schedule = []
        for h in range(len(path)):
            curr_r = path[h]
            nxt_r = path[h+1] if h+1 < len(path) else "-"
            action = "Buffered at Origin" if h == 0 else ("Delivered to Destination" if h == len(path) - 1 else f"Forwarded across Link ({curr_r} <-> {nxt_r})")
            fwd_schedule.append({
                "Hop Index": h,
                "Current Router": curr_r,
                "Next Router": nxt_r,
                "Forwarding Action": action
            })
        st.dataframe(pd.DataFrame(fwd_schedule), width="stretch", height=220)
    else:
        st.caption("Forwarding schedule available once a valid route is discovered.")


# =============================================================
# TAB 5: TOPOLOGY EDITOR (CO2)
# =============================================================
with tab_topo:
    st.markdown("### Interactive Network Topology Editor (CO2)")
    st.caption("Dynamically add, remove, and rename routers; create and remove transmission links; toggle hardware faults; and manage JSON topologies.")

    te_c1, te_c2 = st.columns([1, 1])

    with te_c1:
        st.markdown("#### 1. Topology Presets & Generators")
        preset_choice = st.selectbox(
            "Select Predefined Topology Preset",
            options=[
                "Sample Mesh (Default Interconnected 6-Router Network)",
                "Direct Route (Linear 4-Router Chain)",
                "Multiple Routes (Spine/Leaf with Short vs. Deep Paths)",
                "Cyclic Network (Interconnected Loops & Cross-Links)",
                "Disconnected Subnets (Two Isolated Partitioned Subnets)",
                "Offline Router Barrier (Bridge Router Offline, Bypass Available)"
            ]
        )
        if st.button("Load Preset Topology", width="stretch"):
            p_map = {
                "Sample Mesh (Default Interconnected 6-Router Network)": "sample",
                "Direct Route (Linear 4-Router Chain)": "direct",
                "Multiple Routes (Spine/Leaf with Short vs. Deep Paths)": "multi_route",
                "Cyclic Network (Interconnected Loops & Cross-Links)": "cyclic",
                "Disconnected Subnets (Two Isolated Partitioned Subnets)": "disconnected",
                "Offline Router Barrier (Bridge Router Offline, Bypass Available)": "offline_router"
            }
            graph.load_preset(p_map[preset_choice])
            sim.invalidate_simulation()
            st.success(f"Loaded '{preset_choice}' successfully.")
            st.rerun()

        st.markdown("##### Random Topology Generators")
        rg_col1, rg_col2 = st.columns(2)
        with rg_col1:
            gen_v = st.slider("Router Count (V)", min_value=3, max_value=10, value=6)
        with rg_col2:
            st.write("")
            rc1, rc2 = st.columns(2)
            if rc1.button("Connected", width="stretch"):
                graph.generate_random_connected(gen_v)
                sim.invalidate_simulation()
                st.rerun()
            if rc2.button("Disconnected", width="stretch"):
                graph.generate_random_disconnected(gen_v)
                sim.invalidate_simulation()
                st.rerun()

        st.markdown("#### 2. Layout Arrangement")
        if st.button("Auto-Arrange Circle Layout", width="stretch"):
            graph.auto_layout()
            st.success("Routers arranged in circular layout.")
            st.rerun()

        st.markdown("#### 3. Save / Load JSON Topology")
        json_data = json.dumps(graph.to_dict(), indent=2)
        st.download_button(
            "Download Topology (JSON)", data=json_data,
            file_name="network_topology.json", mime="application/json", width="stretch"
        )
        uploaded_topo = st.file_uploader("Upload Topology JSON", type=["json"])
        if uploaded_topo is not None:
            try:
                data = json.load(uploaded_topo)
                ok, msg = graph.load_from_dict(data)
                if ok:
                    sim.invalidate_simulation()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            except Exception as e:
                st.error(f"Malformed JSON: {e}")

    with te_c2:
        st.markdown("#### 4. Router Management (Add / Delete / Rename)")
        # Add Router
        ar_c1, ar_c2 = st.columns([1, 2])
        new_rid = ar_c1.text_input("Router ID", placeholder="R7", max_chars=8).upper()
        new_rname = ar_c2.text_input("Router Label", placeholder="Access Gateway")
        if st.button("Add Router", width="stretch"):
            ok, msg = validate_router_id(new_rid)
            if not ok:
                st.error(msg)
            elif new_rid in graph.routers:
                st.error(f"Router '{new_rid}' already exists.")
            else:
                graph.add_router(new_rid, new_rname)
                graph.auto_layout()
                sim.invalidate_simulation()
                st.success(f"Added Router {new_rid}")
                st.rerun()

        # Rename Router
        r_all = sorted(graph.routers.keys())
        if r_all:
            rn_c1, rn_c2 = st.columns([1, 2])
            rename_target = rn_c1.selectbox("Select Router to Rename", options=r_all, key="rn_tgt")
            new_label = rn_c2.text_input("New Label", placeholder="Core Switch", key="rn_lbl")
            if st.button("Rename Router", width="stretch"):
                if new_label.strip():
                    graph.rename_router(rename_target, new_label.strip())
                    st.success(f"Renamed Router {rename_target} to '{new_label.strip()}'")
                    st.rerun()
                else:
                    st.warning("Please enter a valid non-empty label.")

        # Delete Router
        if r_all:
            del_r = st.selectbox("Select Router to Delete", options=["-- Select --"] + r_all)
            if st.button("Delete Selected Router", width="stretch") and del_r != "-- Select --":
                graph.remove_router(del_r)
                sim.invalidate_simulation()
                st.success(f"Deleted {del_r} and cascaded removal of its incident links.")
                st.rerun()

        st.markdown("#### 5. Transmission Link Management")
        if len(r_all) >= 2:
            cn_c1, cn_c2 = st.columns(2)
            u_conn = cn_c1.selectbox("Endpoint A", options=r_all, key="u_cn")
            v_conn = cn_c2.selectbox("Endpoint B", options=[r for r in r_all if r != u_conn], key="v_cn")
            if st.button("Add Transmission Link", width="stretch"):
                if graph.add_connection(u_conn, v_conn):
                    sim.invalidate_simulation()
                    st.success(f"Connected {u_conn} <-> {v_conn}")
                    st.rerun()
                else:
                    st.warning("Connection already exists or is invalid.")

        active_edges = [f"{u} <-> {v}" for (u, v) in graph.get_edges()]
        if active_edges:
            rem_edge = st.selectbox("Select Link to Remove", options=active_edges)
            if st.button("Remove Transmission Link", width="stretch"):
                u_rem, v_rem = [x.strip() for x in rem_edge.split("<->")]
                graph.remove_connection(u_rem, v_rem)
                sim.invalidate_simulation()
                st.success(f"Removed link {rem_edge}")
                st.rerun()

        st.markdown("#### 6. Hardware Fault Injection (Online / Offline Toggle)")
        if r_all:
            tog_r = st.selectbox("Select Router for Status Toggle", options=r_all, key="tog_r")
            curr_state = "Online" if graph.routers[tog_r].is_online else "Offline"
            st.caption(f"Current hardware state: **{curr_state}**")
            if st.button("Toggle Power Status", width="stretch"):
                new_state = graph.toggle_router_status(tog_r)
                sim.invalidate_simulation()
                st.info(f"Router {tog_r} is now {'Online' if new_state else 'Offline'}")
                st.rerun()

    # Synchronized Graph Representations Row
    st.markdown("---")
    st.markdown("#### Synchronized Graph Representations (CO2 & CO5)")
    rep_c1, rep_c2 = st.columns(2)

    with rep_c1:
        st.markdown("##### Dynamic Adjacency List")
        st.caption("Space complexity: **O(V + E)**. Primary structure used for fast neighbor traversal.")
        adj_list = graph.get_adjacency_list()
        for rid, nbrs in adj_list.items():
            r = graph.routers.get(rid)
            st_text = "[ONLINE]" if (r and r.is_online) else "[OFFLINE]"
            nbr_chips = "".join([f'<span class="chip chip-item">{n}</span>' for n in nbrs]) if nbrs else '<span style="color:#94A3B8; font-style:italic;">No incident links</span>'
            st.markdown(f"**{st_text} {rid}** ({r.name if r else ''}) -> {nbr_chips}", unsafe_allow_html=True)

    with rep_c2:
        st.markdown("##### Synchronized Adjacency Matrix")
        st.caption("Space complexity: **O(V^2)**. Supports constant-time O(1) link lookup.")
        nodes, matrix = graph.get_adjacency_matrix()
        if nodes:
            mat_df = pd.DataFrame(matrix, index=nodes, columns=nodes)
            st.dataframe(mat_df, width="stretch", height=240)
        else:
            st.caption("No routers present.")


# =============================================================
# TAB 6: ALGORITHM COMPARISON (SECTION 6 & 10)
# =============================================================
with tab_compare:
    st.markdown("### Algorithm Benchmark: BFS vs. DFS on Identical Network")
    st.caption("Evaluates both algorithms side-by-side using the identical source and destination endpoints on the active network.")

    src_cmp = st.session_state.get("source_id")
    dst_cmp = st.session_state.get("dest_id")

    if src_cmp in graph.routers and dst_cmp in graph.routers:
        b_res = bfs(graph, src_cmp, dst_cmp)
        d_res = dfs(graph, src_cmp, dst_cmp)

        comp_metrics1, comp_metrics2 = st.columns(2)
        with comp_metrics1:
            st.markdown(f"#### BFS (FIFO Queue) — Shortest-Hop Guarantee")
            b_path_str = " -> ".join(b_res["path"]) if b_res["path"] else "No route"
            st.markdown(f"- **Route Discovered:** `{b_path_str}`")
            st.markdown(f"- **Hop Count:** `{b_res['hops']} hops` (Guaranteed minimum hops)")
            st.markdown(f"- **Routers Visited:** `{len(b_res['visited'])}`")
            st.markdown(f"- **Queue Operations:** `{b_res.get('total_enqueues', 0)} enqueues, {b_res.get('total_dequeues', 0)} dequeues`")
            st.markdown(f"- **Peak Queue Capacity:** `{b_res['max_structure']} items`")

        with comp_metrics2:
            st.markdown(f"#### DFS (LIFO Stack) — Deep Exploration")
            d_path_str = " -> ".join(d_res["path"]) if d_res["path"] else "No route"
            st.markdown(f"- **Route Discovered:** `{d_path_str}`")
            st.markdown(f"- **Hop Count:** `{d_res['hops']} hops` (Valid path; minimum hops not guaranteed)")
            st.markdown(f"- **Routers Visited:** `{len(d_res['visited'])}`")
            st.markdown(f"- **Stack Operations:** `{d_res.get('total_pushes', 0)} pushes, {d_res.get('total_pops', 0)} pops`")
            st.markdown(f"- **Peak Stack Capacity:** `{d_res['max_structure']} items`")

        st.markdown("---")
        comp_table = [
            {"Property / Metric": "Core Data Structure", "BFS (Breadth-First Search)": "FIFO Queue (collections.deque)", "DFS (Depth-First Search)": "LIFO Stack (list)"},
            {"Property / Metric": "Exploration Principle", "BFS (Breadth-First Search)": "Level-by-level outward radiating", "DFS (Depth-First Search)": "Deepest unvisited branch with backtracking"},
            {"Property / Metric": "Route Discovered?", "BFS (Breadth-First Search)": "Yes" if b_res["success"] else "No", "DFS (Depth-First Search)": "Yes" if d_res["success"] else "No"},
            {"Property / Metric": "Reconstructed Path", "BFS (Breadth-First Search)": b_path_str, "DFS (Depth-First Search)": d_path_str},
            {"Property / Metric": "Route Hop Count", "BFS (Breadth-First Search)": f"{b_res['hops']} hops (Minimum Hops)", "DFS (Depth-First Search)": f"{d_res['hops']} hops (Valid Path)"},
            {"Property / Metric": "Shortest Path Guarantee", "BFS (Breadth-First Search)": "Mathematically guaranteed for unweighted graphs", "DFS (Depth-First Search)": "NOT guaranteed (depends on branch order)"},
            {"Property / Metric": "Total Execution Steps", "BFS (Breadth-First Search)": f"{len(b_res['steps'])} steps", "DFS (Depth-First Search)": f"{len(d_res['steps'])} steps"},
            {"Property / Metric": "Peak Structure Size", "BFS (Breadth-First Search)": f"{b_res['max_structure']} routers in Queue", "DFS (Depth-First Search)": f"{d_res['max_structure']} routers in Stack"},
            {"Property / Metric": "Time Complexity", "BFS (Breadth-First Search)": "O(V + E) with Adjacency List", "DFS (Depth-First Search)": "O(V + E) with Adjacency List"},
            {"Property / Metric": "Auxiliary Space Complexity", "BFS (Breadth-First Search)": "O(V) for Queue & Parent Map", "DFS (Depth-First Search)": "O(V) for Stack & Parent Map"}
        ]
        st.dataframe(pd.DataFrame(comp_table), width="stretch", height=380)

        st.info(
            "**Runtime Measurement Limitation:** On small network graphs (e.g., 6 to 10 routers), algorithm execution finishes in microseconds. "
            "Microsecond measurements are dominated by Python interpreter dispatch overhead and timer resolution noise. "
            "Therefore, theoretical asymptotic complexity O(V + E) provides the true measure of algorithmic scalability."
        )
    else:
        st.warning("Please configure valid source and destination routers in the Network Visualization tab.")


# =============================================================
# TAB 7: ACADEMIC VIVA GUIDE & THEORY NOTES
# =============================================================
with tab_theory:
    st.markdown("### Academic DSA Curriculum & Viva Voce Guide")
    st.caption("Curated notes and demonstration talking points for college faculty evaluation.")

    st.markdown(
        r"""
        #### **CO1 — Stack and Queue Data Structures**
        - **Breadth-First Search (BFS):**
          - Implemented using a **First-In-First-Out (FIFO) Queue** (`collections.deque`).
          - Discovered routers are enqueued at the **rear**; the next router to expand is dequeued from the **front**.
          - BFS explores all vertices at hop distance $k$ before proceeding to hop distance $k + 1$.
          - In an unweighted network, this level-by-level guarantee ensures that the first time the destination router is encountered, it is via the **minimum-hop path**.
        - **Depth-First Search (DFS):**
          - Implemented using an explicit **Last-In-First-Out (LIFO) Stack** (`list`).
          - Neighbors are pushed onto the **top** of the stack; the next router explored is popped from the top.
          - DFS drives deeply down an individual branch until reaching a dead end (no unvisited online neighbors), at which point it **backtracks** to the next candidate on the stack.
          - DFS guarantees finding a valid reachable path if one exists, but does **not** guarantee the minimum-hop route.

        ---

        #### **CO2 — Dynamic Data Structures**
        - **Dynamic Graph Representation:**
          - Routers (vertices) and transmission links (edges) are dynamically allocated and deallocated at runtime without static array boundaries.
        - **Cascading Integrity on Removal:**
          - When a router is removed, the engine cascades through the adjacency list to remove all incident connections, preventing dangling references and memory leaks.
        - **Input Validation & Integrity:**
          - Rejects duplicate router IDs, empty identifiers, self-loops ($u = v$), and duplicate links.
        - **Simulated Hardware Faults:**
          - Routers can be toggled **Online** or **Offline**. When a router goes offline, the routing algorithms automatically discover alternate detour routes.

        ---

        #### **CO5 — Graph Representations & Network Routing**
        - **Adjacency List ($O(V + E)$):**
          - Maps each router ID to a list of its adjacent neighbors.
          - Ideal for real-world sparse computer networks where $E \ll V^2$.
        - **Adjacency Matrix ($O(V^2)$):**
          - A 2D matrix where `matrix[i][j] = 1` indicates an active link between router $i$ and router $j$.
          - Provides instant $O(1)$ edge-lookup queries.
        - **Route Reconstruction ($O(L)$):**
          - Parent pointers recorded during traversal track `predecessor[child] = parent`.
          - Tracing backwards from destination to source reconstructs the exact route in time proportional to path length $L$.
        - **Network Reachability & Partitions:**
          - Connected components analysis identifies whether the network is fully connected or split into isolated subnets.

        ---

        #### **Complexity Reference Table**

        | Operation / Structure | Time Complexity | Space Complexity | Description |
        | :--- | :--- | :--- | :--- |
        | **BFS Traversal** | $O(V + E)$ | $O(V)$ | Level-by-level queue exploration |
        | **Iterative DFS Traversal** | $O(V + E)$ | $O(V)$ | Deep branch exploration with stack |
        | **Adjacency List Storage** | $O(V + E)$ | $O(V + E)$ | Memory-efficient sparse network representation |
        | **Adjacency Matrix Storage** | $O(V^2)$ | $O(V^2)$ | Complete 2D connectivity grid |
        | **Adjacency Matrix Edge Lookup** | $O(1)$ | $O(1)$ | Instant link verification |
        | **Route Reconstruction** | $O(L)$ | $O(L)$ | Backward trace from destination via parent pointers |
        """
    )


# -------------------------------------------------------------
# 5. AUTOMATIC PLAYBACK & PACKET STREAMING RUNNER
# -------------------------------------------------------------
delay_sec = sim.get_delay_seconds(st.session_state.get("playback_speed", "Normal"))

if st.session_state.get("is_playing", False) and sim_res and sim_res.get("steps"):
    t_steps = len(sim_res["steps"])
    if st.session_state.get("step_idx", 0) < t_steps - 1:
        time.sleep(delay_sec)
        st.session_state["step_idx"] += 1
        st.rerun()
    else:
        st.session_state["is_playing"] = False
        st.rerun()

if st.session_state.get("packet_auto", False) and sim_res and sim_res.get("success") and sim_res.get("path"):
    p_path = sim_res["path"]
    if st.session_state.get("packet_hop", 0) < len(p_path) - 1:
        time.sleep(delay_sec)
        st.session_state["packet_hop"] += 1
        st.rerun()
    else:
        st.session_state["packet_auto"] = False
        st.rerun()
