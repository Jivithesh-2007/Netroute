"""
main.py — NetRoute: Interactive Network Packet-Routing Simulator.

A professional educational SaaS simulator demonstrating:
- CO1: Stack and Queue Data Structures (Queue BFS vs. Stack DFS).
- CO2: Dynamic Graph Operations (Insertion, Deletion, Status Toggle).
- CO5: Graph Traversals, Traversal Trees, and Shortest-Hop Routing.
"""

import time
import json
from typing import Dict, Any, List, Set, Tuple

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import (
    CUSTOM_CSS, render_metric_card,
    PRIMARY, CYAN, PURPLE, SUCCESS, WARNING, ERROR, TEXT_MAIN, TEXT_MUTED, BORDER,
    COLOR_NODE_DEFAULT, COLOR_NODE_SOURCE, COLOR_NODE_DEST,
    COLOR_NODE_VISITED, COLOR_NODE_ACTIVE, COLOR_NODE_ROUTE, COLOR_NODE_OFFLINE, COLOR_PACKET,
    COLOR_EDGE_DEFAULT, COLOR_EDGE_EXPLORED, COLOR_EDGE_ROUTE, COLOR_EDGE_ACTIVE, COLOR_EDGE_TREE
)
from network import Graph, Router, validate_router_id
from algorithms import bfs, dfs
import simulation as sim

# -------------------------------------------------------------
# 1. PAGE SETUP & THEME CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="NetRoute — Network Packet-Routing Simulator",
    page_icon="🌐",
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
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=420,
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

    # B. Draw Explored Links (Explored during algorithm steps)
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

    # D. Draw Current Active Step Edge (Hop link currently being explored)
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

        # Visual hierarchy
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

        status_str = "🟢 Online" if r.is_online else "🔴 Offline"
        nbrs = sorted(graph.adjacency.get(rid, []))
        nbr_str = ", ".join(nbrs) if nbrs else "None"
        ht = (
            f"<b>Router {rid}</b> ({r.name})<br>"
            f"Status: {status_str}<br>"
            f"Connections: {len(nbrs)}<br>"
            f"Neighbors: {nbr_str}"
        )
        hover_texts.append(ht)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=34, color=node_colors, line=dict(color=border_colors, width=2.5)),
        text=node_labels,
        textposition="middle center",
        textfont=dict(
            family="-apple-system, BlinkMacSystemFont, sans-serif",
            size=11,
            color=["#FFFFFF" if c not in ("#FFFFFF", COLOR_NODE_VISITED) else TEXT_MAIN for c in node_colors]
        ),
        hoverinfo="text", hovertext=hover_texts, name="Routers", showlegend=False
    ))

    # F. Draw Current Packet Marker (When packet animation is active)
    if packet_node and packet_node in graph.routers:
        pr = graph.routers[packet_node]
        fig.add_trace(go.Scatter(
            x=[pr.x], y=[pr.y],
            mode="markers+text",
            marker=dict(size=46, symbol="circle-open", color=COLOR_PACKET, line=dict(color=COLOR_PACKET, width=3.5)),
            text=["📦"], textposition="top center", textfont=dict(size=18),
            hoverinfo="text", hovertext=f"<b>Packet In-Transit</b><br>Currently at Router {packet_node}",
            name="Packet (📦)", showlegend=True
        ))

    # Set boundaries with padding
    all_x = [r.x for r in graph.routers.values()]
    all_y = [r.y for r in graph.routers.values()]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    dx = max(80.0, max_x - min_x)
    dy = max(80.0, max_y - min_y)

    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=420,
        margin=dict(l=20, r=20, t=30, b=20), hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=TEXT_MUTED)),
        xaxis=dict(range=[min_x - dx * 0.15, max_x + dx * 0.15], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[max_y + dy * 0.18, min_y - dy * 0.18], showgrid=False, zeroline=False, showticklabels=False)
    )
    return fig


# -------------------------------------------------------------
# 3. COMPACT TOP HEADER BAR
# -------------------------------------------------------------
sim_status = sim.get_simulation_status()
status_class = {
    "Ready": "badge-status-ready",
    "Running": "badge-status-running",
    "Paused": "badge-status-running",
    "Completed": "badge-status-completed",
    "No Route": "badge-status-blocked"
}.get(sim_status, "badge-status-ready")

h_col1, h_col2 = st.columns([7, 3])
with h_col1:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px;">
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:{PRIMARY};">🌐 NetRoute</h2>
            <span style="color:{BORDER};">•</span>
            <span style="font-size:0.95rem; font-weight:600; color:{TEXT_MUTED};">Network Packet-Routing Simulator</span>
            <span class="badge-pill {status_class}" style="margin-left:6px;">● {sim_status.upper()}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
with h_col2:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:flex-end; align-items:center; gap:6px;">
            <span class="badge-pill" style="color:{PRIMARY};">CO1: QUEUE / STACK</span>
            <span class="badge-pill" style="color:{CYAN};">CO2: DYNAMIC GRAPH</span>
            <span class="badge-pill" style="color:{SUCCESS};">CO5: ROUTING</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# -------------------------------------------------------------
# 4. TOP-LEVEL SAAS WORKSPACE NAVIGATION
# -------------------------------------------------------------
nav_sim, nav_topo, nav_compare, nav_explorer, nav_learn = st.tabs([
    "🚀 Live Simulator",
    "🛠️ Topology Editor",
    "⚖️ Algorithm Comparison",
    "📊 Graph Explorer",
    "📚 Learning Centre"
])


# =============================================================
# TAB 1: LIVE SIMULATOR WORKSPACE (MAIN FOCUS)
# =============================================================
with nav_sim:
    router_ids = sorted(graph.routers.keys())

    # Control Bar
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5 = st.columns([2.5, 1.8, 1.8, 2.2, 1.7])
    with ctrl_col1:
        algo_choice = st.selectbox(
            "Algorithm",
            options=["BFS (Shortest-Hop)", "DFS (Path Discovery)"],
            index=0 if "BFS" in st.session_state["selected_algo"] else 1,
            label_visibility="collapsed"
        )
        if algo_choice != st.session_state["selected_algo"]:
            st.session_state["selected_algo"] = algo_choice
            sim.invalidate_simulation()

    with ctrl_col2:
        def_src = router_ids.index(st.session_state["source_id"]) if st.session_state["source_id"] in router_ids else 0
        src_sel = st.selectbox("Source", options=router_ids, index=def_src if router_ids else 0, label_visibility="collapsed")
        if src_sel != st.session_state["source_id"]:
            st.session_state["source_id"] = src_sel
            sim.invalidate_simulation()

    with ctrl_col3:
        def_dst = router_ids.index(st.session_state["dest_id"]) if st.session_state["dest_id"] in router_ids else (len(router_ids) - 1 if router_ids else 0)
        dst_sel = st.selectbox("Destination", options=router_ids, index=def_dst if router_ids else 0, label_visibility="collapsed")
        if dst_sel != st.session_state["dest_id"]:
            st.session_state["dest_id"] = dst_sel
            sim.invalidate_simulation()

    with ctrl_col4:
        if st.button("🚀 Run Simulation", type="primary", width="stretch"):
            sim.execute_routing(graph, algo_choice, src_sel, dst_sel)

    with ctrl_col5:
        speed_sel = st.selectbox(
            "Speed",
            options=["Slow", "Normal", "Fast"],
            index=["Slow", "Normal", "Fast"].index(st.session_state.get("playback_speed", "Normal")),
            label_visibility="collapsed"
        )
        st.session_state["playback_speed"] = speed_sel

    # Active State & Metrics
    active_state = sim.get_active_state(graph)
    current_step = active_state.get("step")
    sim_res = active_state.get("res")

    total_v = len(graph.routers)
    online_v = sum(1 for r in graph.routers.values() if r.is_online)
    total_e = len(graph.get_edges())
    visited_v = len(active_state.get("visited_nodes", []))
    route_hops_str = f"{sim_res['hops']} hops" if (sim_res and sim_res.get("success")) else "—"
    steps_total = len(sim_res.get("steps", [])) if (sim_res and sim_res.get("steps")) else 0
    curr_step_idx = st.session_state.get("step_idx", 0)

    # Metric Cards Row
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.markdown(render_metric_card("Routers", f"{total_v}", f"{online_v} online", PRIMARY), unsafe_allow_html=True)
    with m2:
        st.markdown(render_metric_card("Links", f"{total_e}", "Undirected links", CYAN), unsafe_allow_html=True)
    with m3:
        st.markdown(render_metric_card("Visited", f"{visited_v}", f"of {total_v} routers", CYAN), unsafe_allow_html=True)
    with m4:
        st.markdown(render_metric_card("Route Hops", route_hops_str, "Shortest" if (sim_res and "BFS" in sim_res.get("algorithm", "")) else "Discovered", SUCCESS if (sim_res and sim_res.get("success")) else TEXT_MUTED), unsafe_allow_html=True)
    with m5:
        max_str = str(sim_res.get("max_structure", "—")) if sim_res else "—"
        st.markdown(render_metric_card("Max Struct", max_str, "Queue / Stack peak", PURPLE), unsafe_allow_html=True)
    with m6:
        progress_str = f"Step {curr_step_idx + 1} / {steps_total}" if steps_total else "Ready"
        st.markdown(render_metric_card("Progress", progress_str, sim_status, SUCCESS if sim_status == "Completed" else PRIMARY), unsafe_allow_html=True)

    st.write("")

    # Interactive Network Graph
    fig = build_network_figure(graph, active_state, st.session_state["source_id"], st.session_state["dest_id"])
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": True, "scrollZoom": True})

    # Playback Toolbar (Below Graph)
    if sim_res and sim_res.get("steps"):
        pb_col1, pb_col2, pb_col3, pb_col4, pb_col5, pb_col6, pb_col7 = st.columns([1, 1, 1.4, 1, 1, 1, 3.5])
        with pb_col1:
            if st.button("⏮ First", width="stretch", disabled=(curr_step_idx == 0)):
                sim.first_step()
        with pb_col2:
            if st.button("◀ Back", width="stretch", disabled=(curr_step_idx == 0)):
                sim.step_backward()
        with pb_col3:
            play_label = "⏸ Pause" if st.session_state.get("is_playing", False) else "▶ Play"
            if st.button(play_label, width="stretch", type="primary" if not st.session_state.get("is_playing") else "secondary"):
                sim.toggle_playback()
                st.rerun()
        with pb_col4:
            if st.button("Next ▶", width="stretch", disabled=(curr_step_idx == steps_total - 1)):
                sim.step_forward()
        with pb_col5:
            if st.button("End ⏭", width="stretch", disabled=(curr_step_idx == steps_total - 1)):
                sim.last_step()
        with pb_col6:
            if st.button("↺ Reset", width="stretch"):
                sim.reset_simulation()
                st.rerun()
        with pb_col7:
            scrub_idx = st.slider(
                "Scrub Step", min_value=0, max_value=steps_total - 1,
                value=curr_step_idx, label_visibility="collapsed"
            )
            if scrub_idx != curr_step_idx:
                sim.jump_to_step(scrub_idx)

    # Bottom Inspection Grid (3 Columns)
    st.markdown("---")
    bot_c1, bot_c2, bot_c3 = st.columns([3.2, 3.8, 3.0])

    # Left Column: Step & Operation Banner
    with bot_c1:
        st.markdown("##### 📌 Current Step & Operation")
        if current_step:
            st.info(f"**Step {current_step['step']} [{current_step['operation']}]:** {current_step['description']}")
            if current_step.get("active_edge"):
                u, v = current_step["active_edge"]
                st.caption(f"Active Link Traversed: **{u} <-> {v}**")
        elif sim_res:
            if sim_res.get("success"):
                st.success(f"**Discovered Route:** {' ➔ '.join(sim_res['path'])} ({sim_res['hops']} hops)")
            else:
                st.error(sim_res.get("message"))
        else:
            st.caption("Click **Run Simulation** above to begin step-by-step traversal.")

    # Center Column: Queue / Stack Live Inspector
    with bot_c2:
        is_bfs = "BFS" in st.session_state.get("selected_algo", "")
        struct_name = "FIFO Queue" if is_bfs else "LIFO Stack"
        st.markdown(f"##### 🔍 Live {struct_name} (CO1)")

        if current_step:
            items = current_step.get("structure", [])
            st.caption(f"Current Size: **{len(items)}** • Max Size: **{sim_res.get('max_structure', 0)}**")

            if not items:
                st.caption(f"*{struct_name} is currently empty.*")
            else:
                chips_html = []
                if is_bfs:
                    for i, it in enumerate(items):
                        if i == 0 and len(items) == 1:
                            chips_html.append(f'<span class="chip chip-front">FRONT & REAR: {it}</span>')
                        elif i == 0:
                            chips_html.append(f'<span class="chip chip-front">FRONT: {it}</span>')
                        elif i == len(items) - 1:
                            chips_html.append(f'<span class="chip chip-rear">REAR: {it}</span>')
                        else:
                            chips_html.append(f'<span class="chip chip-item">{it}</span>')
                    st.markdown(f'<div>{" ➔ ".join(chips_html)}</div>', unsafe_allow_html=True)
                else:
                    for i, it in enumerate(items):
                        if i == len(items) - 1 and len(items) == 1:
                            chips_html.append(f'<span class="chip chip-top">TOP & BOTTOM: {it}</span>')
                        elif i == len(items) - 1:
                            chips_html.append(f'<span class="chip chip-top">TOP: {it}</span>')
                        elif i == 0:
                            chips_html.append(f'<span class="chip chip-bot">BOTTOM: {it}</span>')
                        else:
                            chips_html.append(f'<span class="chip chip-item">{it}</span>')
                    st.markdown(f'<div>{" ➔ ".join(chips_html)}</div>', unsafe_allow_html=True)

            # Visited Sequence
            visited_list = current_step.get("visited", [])
            if visited_list:
                v_chips = [f'<span class="chip chip-visited">{n}</span>' for n in visited_list]
                st.markdown(f'<div style="margin-top:6px;"><b>Visited:</b> {" ➔ ".join(v_chips)}</div>', unsafe_allow_html=True)
        else:
            st.caption(f"Waiting for simulation run...")

    # Right Column: Packet Transmission Animation
    with bot_c3:
        st.markdown("##### 📦 Packet Transmission (CO5)")
        if sim_res and sim_res.get("success") and sim_res.get("path"):
            path = sim_res["path"]
            p_hop = st.session_state.get("packet_hop", 0)

            pkt_btn1, pkt_btn2, pkt_btn3 = st.columns(3)
            with pkt_btn1:
                if st.button("Hop ➡️", width="stretch", disabled=(p_hop >= len(path) - 1)):
                    sim.packet_step_forward()
            with pkt_btn2:
                stream_label = "⏸ Pause" if st.session_state.get("packet_auto") else "Stream 📦"
                if st.button(stream_label, width="stretch"):
                    sim.toggle_packet_stream()
                    st.rerun()
            with pkt_btn3:
                if st.button("Reset ↺", width="stretch"):
                    sim.reset_packet()

            st.caption(f"**Hop {p_hop} / {len(path) - 1}:** {active_state.get('packet_status')}")
            # Progress bar for packet
            pkt_progress = p_hop / max(1, len(path) - 1)
            st.progress(pkt_progress)
        else:
            st.caption("Packet transmission activates once a valid route is discovered.")


# =============================================================
# TAB 2: TOPOLOGY EDITOR WORKSPACE (SECTION 11)
# =============================================================
with nav_topo:
    st.markdown("### 🛠️ Dedicated Topology Editor")
    st.caption("Add, remove, configure routers and links, load presets, and manage JSON topologies without cluttering the live simulator.")

    topo_c1, topo_c2 = st.columns(2)

    with topo_c1:
        st.markdown("#### 1. Presets & Generators")
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
            st.success(f"Loaded '{preset_choice}' successfully!")
            st.rerun()

        st.markdown("##### Random Topology Generators")
        rg_col1, rg_col2 = st.columns(2)
        with rg_col1:
            gen_count = st.slider("Router Count (V)", min_value=3, max_value=10, value=6)
        with rg_col2:
            st.write("")
            rc1, rc2 = st.columns(2)
            if rc1.button("Connected", width="stretch"):
                graph.generate_random_connected(gen_count)
                sim.invalidate_simulation()
                st.rerun()
            if rc2.button("Disconnected", width="stretch"):
                graph.generate_random_disconnected(gen_count)
                sim.invalidate_simulation()
                st.rerun()

        st.markdown("#### 2. Layout & Auto-Arrangement")
        if st.button("Arrange in Circle Layout", width="stretch"):
            graph.auto_layout()
            st.success("Routers arranged in deterministic circular layout.")
            st.rerun()

        st.markdown("#### 3. Save / Load JSON Topology")
        json_data = json.dumps(graph.to_dict(), indent=2)
        st.download_button(
            "Download Current Topology (JSON)", data=json_data,
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

    with topo_c2:
        st.markdown("#### 4. Add / Delete Routers")
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

        del_r = st.selectbox("Select Router to Delete", options=["-- Select --"] + sorted(graph.routers.keys()))
        if st.button("Delete Selected Router", width="stretch") and del_r != "-- Select --":
            graph.remove_router(del_r)
            sim.invalidate_simulation()
            st.success(f"Deleted {del_r} and associated links.")
            st.rerun()

        st.markdown("#### 5. Add / Remove Connections")
        r_list = sorted(graph.routers.keys())
        if len(r_list) >= 2:
            cn_c1, cn_c2 = st.columns(2)
            u_conn = cn_c1.selectbox("Endpoint A", options=r_list, key="u_cn")
            v_conn = cn_c2.selectbox("Endpoint B", options=[r for r in r_list if r != u_conn], key="v_cn")
            if st.button("Connect Routers", width="stretch"):
                if graph.add_connection(u_conn, v_conn):
                    sim.invalidate_simulation()
                    st.success(f"Connected {u_conn} <-> {v_conn}")
                    st.rerun()
                else:
                    st.warning("Connection already exists or is invalid.")

        active_edges = [f"{u} <-> {v}" for (u, v) in graph.get_edges()]
        if active_edges:
            rem_edge = st.selectbox("Select Connection to Remove", options=active_edges)
            if st.button("Remove Connection", width="stretch"):
                u_rem, v_rem = [x.strip() for x in rem_edge.split("<->")]
                graph.remove_connection(u_rem, v_rem)
                sim.invalidate_simulation()
                st.success(f"Removed {rem_edge}")
                st.rerun()

        st.markdown("#### 6. Toggle Router Online / Offline Status")
        if r_list:
            tog_r = st.selectbox("Select Router to Toggle", options=r_list, key="tog_r")
            curr_state = "🟢 Online" if graph.routers[tog_r].is_online else "🔴 Offline"
            st.caption(f"Current status: **{curr_state}**")
            if st.button("Toggle Power Status", width="stretch"):
                new_status = graph.toggle_router_status(tog_r)
                sim.invalidate_simulation()
                st.info(f"Router {tog_r} is now {'🟢 Online' if new_status else '🔴 Offline'}")
                st.rerun()


# =============================================================
# TAB 3: ALGORITHM COMPARISON (SECTION 10)
# =============================================================
with nav_compare:
    st.markdown("### ⚖️ Algorithm Benchmark: BFS vs. DFS on Identical Topology")
    st.caption("Runs both BFS and DFS side-by-side using the identical source and destination routers to illustrate algorithmic differences.")

    if st.session_state["source_id"] in graph.routers and st.session_state["dest_id"] in graph.routers:
        b_res = bfs(graph, st.session_state["source_id"], st.session_state["dest_id"])
        d_res = dfs(graph, st.session_state["source_id"], st.session_state["dest_id"])

        comp_rows = [
            {"Property / Metric": "Core Data Structure", "BFS (Breadth-First Search)": "FIFO Queue (`collections.deque`)", "DFS (Depth-First Search)": "LIFO Stack (`list`)"},
            {"Property / Metric": "Traversal Strategy", "BFS (Breadth-First Search)": "Level-by-level exploration (radiating outward)", "DFS (Depth-First Search)": "Deep branch exploration with backtracking"},
            {"Property / Metric": "Route Discovered?", "BFS (Breadth-First Search)": "Yes 🟢" if b_res["success"] else "No 🔴", "DFS (Depth-First Search)": "Yes 🟢" if d_res["success"] else "No 🔴"},
            {"Property / Metric": "Reconstructed Path", "BFS (Breadth-First Search)": " ➔ ".join(b_res["path"]) if b_res["path"] else "None", "DFS (Depth-First Search)": " ➔ ".join(d_res["path"]) if d_res["path"] else "None"},
            {"Property / Metric": "Route Hop Count", "BFS (Breadth-First Search)": f"{b_res['hops']} hops (Shortest Route)", "DFS (Depth-First Search)": f"{d_res['hops']} hops (Valid Path)"},
            {"Property / Metric": "Shortest Path Guarantee", "BFS (Breadth-First Search)": "Guaranteed minimum hops in unweighted graphs", "DFS (Depth-First Search)": "NOT guaranteed (may return deeper branch)"},
            {"Property / Metric": "Total Execution Steps", "BFS (Breadth-First Search)": f"{len(b_res['steps'])} steps", "DFS (Depth-First Search)": f"{len(d_res['steps'])} steps"},
            {"Property / Metric": "Peak Structure Size", "BFS (Breadth-First Search)": f"{b_res['max_structure']} nodes in Queue", "DFS (Depth-First Search)": f"{d_res['max_structure']} nodes in Stack"},
            {"Property / Metric": "Time Complexity", "BFS (Breadth-First Search)": "O(V + E) with Adjacency List", "DFS (Depth-First Search)": "O(V + E) with Adjacency List"},
            {"Property / Metric": "Auxiliary Space Complexity", "BFS (Breadth-First Search)": "O(V) for Queue & Parent Map", "DFS (Depth-First Search)": "O(V) for Stack & Parent Map"}
        ]
        st.dataframe(pd.DataFrame(comp_rows), width="stretch", height=380)
    else:
        st.info("Select valid source and destination routers in the Live Simulator to view benchmark.")


# =============================================================
# TAB 4: GRAPH EXPLORER (CO2 & CO5)
# =============================================================
with nav_explorer:
    st.markdown("### 📊 Graph Representations & Traversal Tree")
    st.caption("Demonstrating dual synchronized graph representations and traversal trees.")

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.markdown("#### Dynamic Adjacency List")
        st.caption("Primary graph representation. Space complexity: **O(V + E)**.")
        adj_list = graph.get_adjacency_list()
        for rid, nbrs in adj_list.items():
            r = graph.routers.get(rid)
            st_dot = "🟢" if (r and r.is_online) else "🔴"
            nbr_chips = "".join([f'<span class="chip chip-item">{n}</span>' for n in nbrs]) if nbrs else '<span style="color:#94A3B8; font-style:italic;">No connections</span>'
            st.markdown(f"**{st_dot} {rid}** ({r.name if r else ''}) ➔ {nbr_chips}", unsafe_allow_html=True)

    with exp_col2:
        st.markdown("#### Synchronized Adjacency Matrix")
        st.caption("2D matrix representation. Space complexity: **O(V²)**.")
        nodes, matrix = graph.get_adjacency_matrix()
        if nodes:
            mat_df = pd.DataFrame(matrix, index=nodes, columns=nodes)
            st.dataframe(mat_df, width="stretch", height=240)
        else:
            st.caption("No routers present.")

    # Traversal Tree Table
    st.markdown("---")
    st.markdown("#### Traversal Tree Edges")
    st.caption("Recorded parent-child discovery relationships from the algorithm execution.")
    if sim_res and sim_res.get("tree_edges"):
        tree_df = pd.DataFrame([
            {"Parent Router (Discovered From)": u, "Child Router (Newly Discovered)": v}
            for u, v in sim_res["tree_edges"]
        ])
        st.dataframe(tree_df, width="stretch", height=180)
    else:
        st.caption("Run an algorithm to record traversal tree edges.")


# =============================================================
# TAB 5: LEARNING CENTRE (CO1, CO2, CO5 VIVA GUIDE)
# =============================================================
with nav_learn:
    st.markdown("### 📚 DSA Academic Curriculum & Viva Guide")

    st.markdown(
        """
        #### **CO1 — Stack and Queue Data Structures**
        - **Breadth-First Search (BFS):**
          - Uses a **First-In-First-Out (FIFO) Queue** (`collections.deque`).
          - Discovered routers are enqueued at the rear; the next router to explore is dequeued from the front.
          - In an unweighted graph, exploring level-by-level guarantees the **shortest path in terms of hop count**.
        - **Depth-First Search (DFS):**
          - Uses an explicit **Last-In-First-Out (LIFO) Stack** (`list`).
          - Explores a single branch as deeply as possible until a dead end is reached, triggering explicit backtracking.
          - Discovers a **valid reachable path**, but does *not* guarantee shortest hops.

        ---

        #### **CO2 — Dynamic Data Structures**
        - **Dynamic Vertex/Edge Allocation:**
          - Routers (vertices) and transmission links (edges) can be dynamically added, renamed, or deleted at runtime.
          - Avoids fixed-size static allocations.
        - **Cascading Integrity:**
          - Deleting a router automatically cascades to remove all incident connections from the adjacency list, preventing dangling pointers.
        - **Hardware Failure Simulation:**
          - Routers can be toggled Online or Offline, causing the algorithms to route packets around the failure.

        ---

        #### **CO5 — Graph Representations & Network Routing**
        - **Adjacency List ($O(V + E)$):** Stores lists of adjacent neighbors. Space-efficient for sparse networks.
        - **Adjacency Matrix ($O(V^2)$):** 2D boolean/weight matrix. Constant-time $O(1)$ edge query.
        - **Packet Transmission:** Discovered routes are executed hop-by-hop, mimicking internet packet forwarding.
        - **Complexity Formulas:**
          - Time Complexity: $O(V + E)$ when traversing adjacency lists.
          - Space Complexity: $O(V)$ auxiliary space for visited sets, predecessor maps, and queue/stack storage.
        """
    )


# -------------------------------------------------------------
# 5. AUTOMATIC PLAYBACK & PACKET STREAMING RUNNER
# -------------------------------------------------------------
delay_sec = sim.get_delay_seconds(st.session_state.get("playback_speed", "Normal"))

if st.session_state.get("is_playing", False) and sim_res and sim_res.get("steps"):
    total_steps = len(sim_res["steps"])
    if st.session_state.get("step_idx", 0) < total_steps - 1:
        time.sleep(delay_sec)
        st.session_state["step_idx"] += 1
        st.rerun()
    else:
        st.session_state["is_playing"] = False
        st.rerun()

if st.session_state.get("packet_auto", False) and sim_res and sim_res.get("success") and sim_res.get("path"):
    path = sim_res["path"]
    if st.session_state.get("packet_hop", 0) < len(path) - 1:
        time.sleep(delay_sec)
        st.session_state["packet_hop"] += 1
        st.rerun()
    else:
        st.session_state["packet_auto"] = False
        st.rerun()
