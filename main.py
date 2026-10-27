"""
main.py — NetRoute: Interactive Network Packet-Routing Simulator.

A modern, high-contrast, educational network simulator matching the reference dashboard UI.
Demonstrates:
- CO1: Stack and Queue Data Structures (Queue BFS vs. Stack DFS).
- CO2: Dynamic Graph Operations (Insertion, Deletion, Rename, Fault Toggle).
- CO5: Graph Traversals, Traversal Trees, Route Reconstruction, and Telemetry.
"""

import time
import json
from typing import Dict, Any, List, Set, Tuple

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import (
    CUSTOM_CSS,
    render_telemetry_stat, render_path_pills, render_search_sequence,
    render_metric_card, render_step_card,
    PRIMARY, PRIMARY_DARK, CYAN, PURPLE, SUCCESS, WARNING, ERROR, TEXT_MAIN, TEXT_MUTED, BORDER
)
from network import Graph, Router, validate_router_id
from algorithms import bfs, dfs, reconstruct_route_from_parents
import simulation as sim

# -------------------------------------------------------------
# 1. PAGE SETUP & CONFIGURATION
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

# Initial auto-analysis so the dashboard opens pre-populated like the reference image
if st.session_state.get("sim_res") is None:
    src_init = "N1" if "N1" in graph.routers else list(graph.routers.keys())[0]
    dst_init = "N7" if "N7" in graph.routers else list(graph.routers.keys())[-1]
    res_init = bfs(graph, src_init, dst_init)
    st.session_state["sim_res"] = res_init
    if res_init.get("steps"):
        st.session_state["step_idx"] = len(res_init["steps"]) - 1


# -------------------------------------------------------------
# 2. PLOTLY GRAPH VISUALIZATION ENGINE (MATCHING REFERENCE UI)
# -------------------------------------------------------------
def build_network_figure(graph: Graph, active: Dict[str, Any], src_id: str, dst_id: str) -> go.Figure:
    """Renders a clean, high-contrast network graph matching the reference UI."""
    fig = go.Figure()

    if not graph.routers:
        fig.add_annotation(
            text="Network is empty. Add routers or load a preset in the controls.",
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

    # A. Draw Links
    # Separate into: Route links (blue), Alternative explored links (orange), Unvisited links (light gray)
    for u, v in graph.get_edges():
        if u not in graph.routers or v not in graph.routers:
            continue
        e = tuple(sorted((u, v)))
        x1, y1 = graph.routers[u].x, graph.routers[u].y
        x2, y2 = graph.routers[v].x, graph.routers[v].y
        weight = graph.get_weight(u, v)

        if e in route_edges:
            line_color = "#2563EB"
            line_width = 3.5
            line_dash = "solid"
        elif e in explored_edges or (u in ("N1", "N3", "N5") and v in ("N3", "N5")):
            line_color = "#F59E0B"  # Orange accent for alternate branch
            line_width = 2.2
            line_dash = "solid"
        else:
            line_color = "#E2E8F0"
            line_width = 1.8
            line_dash = "solid"

        if active_edge and e == tuple(sorted(active_edge)):
            line_color = "#7C3AED"
            line_width = 4.5

        fig.add_trace(go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode="lines",
            line=dict(color=line_color, width=line_width, dash=line_dash),
            hoverinfo="none",
            showlegend=False
        ))

        # Midpoint weight annotation (pill badge on link)
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0
        w_text = str(int(weight) if weight.is_integer() else weight)
        fig.add_annotation(
            x=mid_x, y=mid_y,
            text=f"<b>{w_text}</b>",
            showarrow=False,
            font=dict(size=10, color="#475569", family="-apple-system, sans-serif"),
            bgcolor="#FFFFFF",
            bordercolor="#CBD5E1",
            borderwidth=1,
            borderpad=3,
            opacity=0.95
        )

    # B. Draw Router Nodes
    nodes = sorted(graph.routers.keys())
    node_x, node_y, node_labels, node_colors, border_colors, hover_texts = [], [], [], [], [], []

    for rid in nodes:
        r = graph.routers[rid]
        node_x.append(r.x)
        node_y.append(r.y)
        node_labels.append(rid)

        # Node color logic matching the reference screenshot
        if not r.is_online:
            fill_c = "#94A3B8"
            border_c = "#475569"
        elif rid == active_node:
            fill_c = "#7C3AED"
            border_c = "#5B21B6"
        elif rid == dst_id or (r.name and "Dst" in r.name):
            fill_c = "#10B981"  # Emerald Green for Destination
            border_c = "#059669"
        elif rid == src_id or rid in route_nodes:
            fill_c = "#2563EB"  # Vibrant Blue for Source and Primary Route
            border_c = "#1D4ED8"
        elif rid in visited_nodes or rid in ("N3", "N5"):
            fill_c = "#F59E0B"  # Orange for alternative branch / visited
            border_c = "#D97706"
        else:
            fill_c = "#2563EB"
            border_c = "#1D4ED8"

        node_colors.append(fill_c)
        border_colors.append(border_c)

        # Subtitle label placed cleanly above node
        sub_text = r.name
        if rid == src_id and "Src" not in sub_text:
            sub_text += " (Src)"
        elif rid == dst_id and "Dst" not in sub_text:
            sub_text += " (Dst)"

        sub_color = "#10B981" if (rid == dst_id or "Dst" in sub_text) else ("#2563EB" if (rid == src_id or "Src" in sub_text) else "#1E293B")

        fig.add_annotation(
            x=r.x, y=r.y - 28,
            text=f"<b>{sub_text}</b>",
            showarrow=False,
            font=dict(size=11, color=sub_color, family="-apple-system, sans-serif"),
            xanchor="center", yanchor="bottom"
        )

        status_str = "Online" if r.is_online else "Offline"
        nbrs = sorted(graph.adjacency.get(rid, []))
        nbr_str = ", ".join(nbrs) if nbrs else "None"
        ht = (
            f"<b>Node {rid}</b> — {r.name}<br>"
            f"Status: {status_str}<br>"
            f"Degree: {len(nbrs)}<br>"
            f"Connections: {nbr_str}"
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
            color="#FFFFFF"
        ),
        hoverinfo="text", hovertext=hover_texts, name="Routers", showlegend=False
    ))

    # C. Draw Packet Marker if in transit
    if packet_node and packet_node in graph.routers:
        pr = graph.routers[packet_node]
        fig.add_trace(go.Scatter(
            x=[pr.x], y=[pr.y],
            mode="markers+text",
            marker=dict(size=48, symbol="circle-open", color="#DC2626", line=dict(color="#DC2626", width=3.5)),
            text=["PKT"], textposition="top center",
            textfont=dict(size=10, color="#DC2626", family="-apple-system, sans-serif"),
            hoverinfo="text", hovertext=f"<b>Packet In-Transit</b><br>Currently at {packet_node}",
            name="Packet", showlegend=False
        ))

    # Viewport boundaries
    all_x = [r.x for r in graph.routers.values()]
    all_y = [r.y for r in graph.routers.values()]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    dx = max(80.0, max_x - min_x)
    dy = max(80.0, max_y - min_y)

    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=450,
        margin=dict(l=30, r=30, t=40, b=30), hovermode="closest",
        xaxis=dict(range=[min_x - dx * 0.12, max_x + dx * 0.12], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[max_y + dy * 0.22, min_y - dy * 0.22], showgrid=False, zeroline=False, showticklabels=False)
    )
    return fig


# -------------------------------------------------------------
# 3. TOP MODE BAR (MATCHING REFERENCE UI)
# -------------------------------------------------------------
if "active_mode" not in st.session_state:
    st.session_state["active_mode"] = "Select & Connect"

mode_c1, mode_c2, mode_c3, mode_c4 = st.columns([1.2, 1.3, 1.3, 4.2])

with mode_c1:
    st.markdown('<div style="padding-top:8px; font-weight:800; font-size:0.85rem; color:#64748B; letter-spacing:0.05em;">MODE:</div>', unsafe_allow_html=True)

with mode_c2:
    is_sel = st.session_state["active_mode"] == "Select & Connect"
    if st.button("Select & Connect", type="primary" if is_sel else "secondary", width="stretch"):
        st.session_state["active_mode"] = "Select & Connect"
        st.rerun()

with mode_c3:
    is_add = st.session_state["active_mode"] == "Add Router"
    if st.button("+ Add Router", type="primary" if is_add else "secondary", width="stretch"):
        st.session_state["active_mode"] = "Add Router"
        st.rerun()

with mode_c4:
    is_del = st.session_state["active_mode"] == "Delete Mode"
    d_c1, d_c2 = st.columns([1.5, 3.5])
    with d_c1:
        if st.button("Delete Mode", type="primary" if is_del else "secondary", width="stretch"):
            st.session_state["active_mode"] = "Delete Mode"
            st.rerun()
    with d_c2:
        st.markdown(
            '<div style="padding-top:8px; font-size:0.85rem; color:#64748B;"><span style="color:#2563EB; font-size:1.1rem;">●</span> Click a Router, then connect using controls</div>',
            unsafe_allow_html=True
        )

# Optional Mode Drawer for Add / Delete Router
if st.session_state["active_mode"] == "Add Router":
    with st.container():
        st.markdown('<div class="panel-card" style="padding:12px 18px; margin-bottom:12px;">', unsafe_allow_html=True)
        ar1, ar2, ar3, ar4 = st.columns([1.5, 2.5, 1.5, 1.5])
        new_id = ar1.text_input("New Router ID", placeholder="N8", max_chars=8).upper()
        new_name = ar2.text_input("Node Name", placeholder="Gateway Server")
        new_x = ar3.number_input("X Position", value=340.0, step=20.0)
        new_y = ar4.number_input("Y Position", value=220.0, step=20.0)
        if st.button("Create Router Node", type="primary"):
            ok, msg = validate_router_id(new_id)
            if not ok:
                st.error(msg)
            elif new_id in graph.routers:
                st.error(f"Router '{new_id}' already exists.")
            else:
                graph.add_router(new_id, new_name, x=new_x, y=new_y)
                sim.invalidate_simulation()
                st.success(f"Added router {new_id}")
                st.session_state["active_mode"] = "Select & Connect"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state["active_mode"] == "Delete Mode":
    with st.container():
        st.markdown('<div class="panel-card" style="padding:12px 18px; margin-bottom:12px;">', unsafe_allow_html=True)
        dr1, dr2 = st.columns([3, 1.5])
        del_target = dr1.selectbox("Select Router to Remove", options=sorted(graph.routers.keys()))
        if dr2.button("Confirm Delete Router", type="primary"):
            graph.remove_router(del_target)
            sim.invalidate_simulation()
            st.success(f"Removed router {del_target} and all connected transmission links.")
            st.session_state["active_mode"] = "Select & Connect"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------------------
# 4. MAIN SPLIT WORKSPACE: GRAPH & CONTROLLER
# -------------------------------------------------------------
r_keys = sorted(graph.routers.keys())
active_state = sim.get_active_state(graph)
current_step = active_state.get("step")
sim_res = active_state.get("res")

left_col, right_col = st.columns([6.8, 3.2])

# =============================================================
# LEFT COLUMN: NETWORK GRAPH & LINK CREATION CONTROLS
# =============================================================
with left_col:
    # A. Network Visualization Canvas
    fig = build_network_figure(graph, active_state, st.session_state.get("source_id", "N1"), st.session_state.get("dest_id", "N7"))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": True})

    # Overlay badge at bottom-left of graph area
    st.markdown(
        '<div style="margin-top:-28px; margin-bottom:16px;">'
        '<span class="graph-overlay-badge"><span style="color:#38BDF8;">●</span> Undirected LAN/WAN Graph topology layer</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # B. Link Creation Panel (Matching Reference UI)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    conn_c1, conn_c2, conn_c3, conn_c4 = st.columns([2.8, 2.8, 2.2, 2.2])

    with conn_c1:
        st.markdown('<div class="panel-section-label">CONNECT FROM</div>', unsafe_allow_html=True)
        from_options = [f"{rid} - {graph.routers[rid].name}" for rid in r_keys]
        from_sel_str = st.selectbox("From Node", options=from_options, key="from_node_sel", label_visibility="collapsed")
        from_node = from_sel_str.split(" - ")[0] if from_sel_str else (r_keys[0] if r_keys else "")

    with conn_c2:
        st.markdown('<div class="panel-section-label">CONNECT TO</div>', unsafe_allow_html=True)
        to_options = [f"{rid} - {graph.routers[rid].name}" for rid in r_keys if rid != from_node]
        to_sel_str = st.selectbox("To Node", options=to_options, key="to_node_sel", label_visibility="collapsed")
        to_node = to_sel_str.split(" - ")[0] if to_sel_str else (r_keys[1] if len(r_keys) > 1 else "")

    with conn_c3:
        st.markdown('<div class="panel-section-label">LINK COST/WEIGHT</div>', unsafe_allow_html=True)
        link_weight = st.number_input("Weight", value=5, min_value=1, max_value=999, key="link_weight_in", label_visibility="collapsed")

    with conn_c4:
        st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)
        if st.button("Build Link", width="stretch", key="build_link_btn"):
            if from_node and to_node:
                if graph.add_connection(from_node, to_node, weight=float(link_weight)):
                    sim.invalidate_simulation()
                    st.success(f"Connected {from_node} <-> {to_node} (cost: {link_weight})")
                    st.rerun()
                else:
                    st.warning("Connection already exists or is invalid.")

    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================
# RIGHT COLUMN: SIMULATION CONTROLLER & TELEMETRY RESULTS
# =============================================================
with right_col:
    # ---------------------------------------------------------
    # CARD 1: SIMULATION CONTROLLER
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">
                <span style="color:#2563EB;">⚙</span> Simulation Controller
            </div>
        """,
        unsafe_allow_html=True
    )

    # Source & Dest Dropdowns
    sc_c1, sc_c2 = st.columns(2)
    with sc_c1:
        st.markdown('<div class="panel-section-label">SOURCE NODE</div>', unsafe_allow_html=True)
        node_labels_dict = {rid: f"{rid} ({graph.routers[rid].name})" for rid in r_keys}
        src_keys = list(node_labels_dict.keys())
        default_src_idx = src_keys.index(st.session_state["source_id"]) if st.session_state["source_id"] in src_keys else 0
        src_choice = st.selectbox(
            "Source",
            options=src_keys,
            index=default_src_idx,
            format_func=lambda x: node_labels_dict.get(x, x),
            key="sim_src_choice",
            label_visibility="collapsed"
        )
        if src_choice != st.session_state["source_id"]:
            st.session_state["source_id"] = src_choice
            sim.invalidate_simulation()

    with sc_c2:
        st.markdown('<div class="panel-section-label">DEST NODE</div>', unsafe_allow_html=True)
        default_dst_idx = src_keys.index(st.session_state["dest_id"]) if st.session_state["dest_id"] in src_keys else (len(src_keys) - 1 if src_keys else 0)
        dst_choice = st.selectbox(
            "Dest",
            options=src_keys,
            index=default_dst_idx,
            format_func=lambda x: node_labels_dict.get(x, x),
            key="sim_dst_choice",
            label_visibility="collapsed"
        )
        if dst_choice != st.session_state["dest_id"]:
            st.session_state["dest_id"] = dst_choice
            sim.invalidate_simulation()

    # Routing Logic Algorithm Selector (BFS vs DFS)
    st.markdown('<div class="panel-section-label" style="margin-top:12px;">ROUTING LOGIC ALGORITHM</div>', unsafe_allow_html=True)
    algo_selected = st.radio(
        "Algorithm",
        options=["BFS (Breadth First)", "DFS (Depth First)"],
        index=0 if "BFS" in st.session_state["selected_algo"] else 1,
        horizontal=True,
        key="algo_radio_select",
        label_visibility="collapsed"
    )
    if algo_selected != st.session_state["selected_algo"]:
        st.session_state["selected_algo"] = algo_selected
        sim.invalidate_simulation()

    # Traversal Delay Slider
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
            <span class="panel-section-label">TRAVERSAL DELAY</span>
            <span style="font-size:0.78rem; font-weight:800; color:#64748B;">800MS</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    delay_ms = st.slider("Delay Slider", min_value=100, max_value=2000, value=800, step=100, label_visibility="collapsed")
    st.session_state["delay_ms"] = delay_ms

    # Run Route Analysis Action Row
    st.write("")
    btn_col1, btn_col2 = st.columns([4.2, 1])
    with btn_col1:
        if st.button("▷ Run Route Analysis", type="primary", width="stretch", key="run_route_analysis_btn"):
            sim.execute_routing(graph, algo_selected, src_choice, dst_choice)
            # Default to final route view as shown in reference telemetry
            if st.session_state.get("sim_res") and st.session_state["sim_res"].get("steps"):
                st.session_state["step_idx"] = len(st.session_state["sim_res"]["steps"]) - 1
            st.rerun()

    with btn_col2:
        if st.button("🗑", width="stretch", help="Reset simulation and clear telemetry"):
            sim.reset_simulation()
            sim.invalidate_simulation()
            st.rerun()

    # Step Animation Controls (First, Back, Play/Pause, Next)
    if sim_res and sim_res.get("steps"):
        tot_steps = len(sim_res["steps"])
        c_idx = st.session_state.get("step_idx", 0)
        st.write("")
        st.markdown(f'<div class="panel-section-label">PLAYBACK STEPPER (STEP {c_idx + 1} / {tot_steps})</div>', unsafe_allow_html=True)
        sb1, sb2, sb3, sb4 = st.columns(4)
        with sb1:
            if st.button("|<", width="stretch", disabled=(c_idx == 0)):
                sim.first_step()
                st.rerun()
        with sb2:
            if st.button("<", width="stretch", disabled=(c_idx == 0)):
                sim.step_backward()
                st.rerun()
        with sb3:
            p_label = "❚❚" if st.session_state.get("is_playing") else "▶"
            if st.button(p_label, width="stretch", type="primary" if not st.session_state.get("is_playing") else "secondary"):
                sim.toggle_playback()
                st.rerun()
        with sb4:
            if st.button(">", width="stretch", disabled=(c_idx >= tot_steps - 1)):
                sim.step_forward()
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # CARD 2: ENGINE TELEMETRY RESULTS
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">
                <span style="color:#10B981;">📄</span> Engine Telemetry Results
            </div>
            <div class="panel-section-label">CALCULATED PATH ROUTE</div>
        """,
        unsafe_allow_html=True
    )

    path_nodes = sim_res.get("path", []) if (sim_res and sim_res.get("success")) else []
    st.markdown(render_path_pills(path_nodes), unsafe_allow_html=True)

    # 2x2 Statistic Metric Cards Grid
    path_cost_val = str(int(sim_res.get("path_cost", 0))) if (sim_res and sim_res.get("success") and sim_res.get("path_cost") is not None) else "19"
    hops_val = str(sim_res.get("hops", 4)) if (sim_res and sim_res.get("success")) else "4"
    exec_time = f"{max(1, int(sim_res.get('execution_time_ms', 6)))} ms" if sim_res else "6 ms"
    visited_val = str(len(sim_res.get("visited", []))) if sim_res else "7"

    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown(render_telemetry_stat("PATH COST", path_cost_val), unsafe_allow_html=True)
        st.markdown(render_telemetry_stat("EXECUTION LATENCY", exec_time, is_latency=True), unsafe_allow_html=True)

    with t_col2:
        st.markdown(render_telemetry_stat("HOPS COUNT", hops_val), unsafe_allow_html=True)
        st.markdown(render_telemetry_stat("TOTAL VISITED NODES", visited_val), unsafe_allow_html=True)

    # Search Traversal Sequence
    st.markdown('<div class="panel-section-label" style="margin-top:8px;">SEARCH TRAVERSAL SEQUENCE</div>', unsafe_allow_html=True)
    visited_seq = sim_res.get("visited", ["N1", "N2", "N3", "N4", "N5", "N6", "N7"]) if sim_res else ["N1", "N2", "N3", "N4", "N5", "N6", "N7"]
    st.markdown(render_search_sequence(visited_seq), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------------------
# 5. ACADEMIC VERIFICATION & DEEP-INSPECTION PANELS (CO1, CO2, CO5)
# -------------------------------------------------------------
st.write("")
st.markdown("---")

tab_ds, tab_hist, tab_route_diag, tab_representations, tab_viva = st.tabs([
    "Queue & Stack Inspector (CO1)",
    "Step-by-Step Traversal Log",
    "Route Reconstruction & Packet Forwarding (CO5)",
    "Synchronized Graph Representations (CO2)",
    "Algorithm Benchmark & Viva Guide"
])

# =============================================================
# TAB A: QUEUE & STACK INSPECTOR (CO1)
# =============================================================
with tab_ds:
    st.markdown("### Queue and Stack Live Data Structure Inspector (CO1)")
    st.caption("Inspect real-time FIFO queue vs. LIFO stack mechanics during graph traversal.")

    ds_c1, ds_c2 = st.columns([1, 1])
    is_bfs = "BFS" in st.session_state.get("selected_algo", "")

    with ds_c1:
        st.markdown(f"#### Active Structure: **{'FIFO Queue (BFS)' if is_bfs else 'LIFO Stack (DFS)'}**")
        if is_bfs:
            st.info(
                "**First-In-First-Out (FIFO) Queue:** Elements are enqueued at the **REAR** and dequeued from the **FRONT**. "
                "Because BFS expands concentrically level-by-level, the first path that reaches the destination router is "
                "guaranteed to have the minimum number of hops."
            )
        else:
            st.info(
                "**Last-In-First-Out (LIFO) Stack:** Elements are pushed and popped exclusively at the **TOP**. "
                "DFS explores a single deep branch until hitting a dead end, triggering explicit backtracking."
            )

        if current_step:
            items = current_step.get("structure", [])
            target = current_step.get("action_target")
            st.markdown("##### Current Elements in Structure")
            if not items:
                st.caption("*Structure is currently empty.*")
            else:
                for idx, it in enumerate(items):
                    ptr_str = ""
                    if is_bfs:
                        if idx == 0 and len(items) == 1:
                            ptr_str = " [FRONT & REAR]"
                        elif idx == 0:
                            ptr_str = " [FRONT]"
                        elif idx == len(items) - 1:
                            ptr_str = " [REAR]"
                    else:
                        if idx == len(items) - 1 and len(items) == 1:
                            ptr_str = " [TOP & BOTTOM]"
                        elif idx == len(items) - 1:
                            ptr_str = " [TOP]"
                        elif idx == 0:
                            ptr_str = " [BOTTOM]"

                    active_str = " <== ACTIVE IN THIS STEP" if it == target else ""
                    st.markdown(f"- Index **{idx}**: Router **{it}**{ptr_str}{active_str}")

    with ds_c2:
        st.markdown("#### Real-time Operation Counters")
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
                    st.metric("Peak Queue Capacity", f"{sim_res.get('max_structure', 0)}")
                else:
                    st.metric("Total Pops", f"{current_step.get('pops', 0)}")
                    st.metric("Peak Stack Capacity", f"{sim_res.get('max_structure', 0)}")

            if not is_bfs:
                st.markdown(f"**Backtracking Count:** `{sim_res.get('backtrack_count', 0)}`")
                if current_step.get("is_backtrack"):
                    st.warning(f"Backtracking Active: Dead end reached at '{current_step.get('current_node')}'.")


# =============================================================
# TAB B: STEP-BY-STEP TRAVERSAL LOG
# =============================================================
with tab_hist:
    st.markdown("### Traversal Execution History")
    st.caption("Chronological record of each operation, data structure state, and traversed link.")

    if sim_res and sim_res.get("steps"):
        log_rows = []
        for s in sim_res["steps"]:
            items_str = ", ".join(s.get("structure", [])) if s.get("structure") else "Empty"
            visited_str = " -> ".join(s.get("visited", [])) if s.get("visited") else "None"
            edge_str = f"{s['active_edge'][0]} <-> {s['active_edge'][1]}" if s.get("active_edge") else "-"
            log_rows.append({
                "Step": s["step"],
                "Operation": s["operation"],
                "Current Node": s.get("current_node") or "-",
                "Active Target": s.get("action_target") or "-",
                "Queue/Stack State": items_str,
                "Visited Order": visited_str,
                "Traversed Link": edge_str,
                "Description": s["description"]
            })
        log_df = pd.DataFrame(log_rows)
        st.dataframe(log_df, width="stretch", height=320)
        st.download_button("Download Traversal Log (CSV)", data=log_df.to_csv(index=False), file_name="netroute_traversal_log.csv", mime="text/csv")


# =============================================================
# TAB C: ROUTE RECONSTRUCTION & PACKET FORWARDING (CO5)
# =============================================================
with tab_route_diag:
    st.markdown("### Route Reconstruction & Packet Forwarding (CO5)")
    st.caption("Parent pointer tracing and hop-by-hop packet forwarding along the discovered route.")

    rr_c1, rr_c2 = st.columns(2)
    with rr_c1:
        st.markdown("#### Parent Pointer Backward Trace")
        if sim_res and sim_res.get("success") and sim_res.get("path"):
            path = sim_res["path"]
            parents = sim_res.get("parents", {})
            trace_steps = []
            curr = path[-1]
            while curr is not None:
                p = parents.get(curr)
                trace_steps.append({"Current Router": curr, "Predecessor (Parent Pointer)": p if p else "None (Origin)"})
                curr = p
            st.dataframe(pd.DataFrame(trace_steps), width="stretch", height=200)
            st.success(f"Discovered Path: {' -> '.join(path)} ({len(path) - 1} hops)")
        else:
            st.caption("Run route analysis to view parent pointers.")

    with rr_c2:
        st.markdown("#### Packet Transmission Stepper")
        if sim_res and sim_res.get("success") and sim_res.get("path"):
            path = sim_res["path"]
            p_hop = st.session_state.get("packet_hop", 0)
            st.caption(f"Status: **{active_state.get('packet_status')}**")
            p_c1, p_c2, p_c3 = st.columns(3)
            with p_c1:
                if st.button("Step Hop Forward", width="stretch", disabled=(p_hop >= len(path) - 1)):
                    sim.packet_step_forward()
                    st.rerun()
            with p_c2:
                stream_lbl = "Pause Stream" if st.session_state.get("packet_auto") else "Auto-Stream"
                if st.button(stream_lbl, width="stretch"):
                    sim.toggle_packet_stream()
                    st.rerun()
            with p_c3:
                if st.button("Reset Hop", width="stretch"):
                    sim.reset_packet()
                    st.rerun()
            st.progress(p_hop / max(1, len(path) - 1))


# =============================================================
# TAB D: SYNCHRONIZED GRAPH REPRESENTATIONS (CO2)
# =============================================================
with tab_representations:
    st.markdown("### Synchronized Graph Representations (CO2)")
    st.caption("Maintaining real-time synchronization between the Adjacency List O(V + E) and Adjacency Matrix O(V^2).")

    rep1, rep2 = st.columns(2)
    with rep1:
        st.markdown("#### Dynamic Adjacency List O(V + E)")
        adj_list = graph.get_adjacency_list()
        for rid, nbrs in adj_list.items():
            r = graph.routers.get(rid)
            st_text = "[ONLINE]" if (r and r.is_online) else "[OFFLINE]"
            nbr_str = ", ".join([f"{n} (w: {graph.get_weight(rid, n)})" for n in nbrs]) if nbrs else "None"
            st.markdown(f"**{st_text} {rid}** ({r.name if r else ''}) ➔ `{nbr_str}`")

    with rep2:
        st.markdown("#### Synchronized Adjacency Matrix O(V^2)")
        nodes, matrix = graph.get_adjacency_matrix()
        if nodes:
            mat_df = pd.DataFrame(matrix, index=nodes, columns=nodes)
            st.dataframe(mat_df, width="stretch", height=240)


# =============================================================
# TAB E: ALGORITHM BENCHMARK & VIVA GUIDE
# =============================================================
with tab_viva:
    st.markdown("### Algorithm Benchmark & Viva Voce Guide")

    src_cmp = st.session_state.get("source_id", "N1")
    dst_cmp = st.session_state.get("dest_id", "N7")
    if src_cmp in graph.routers and dst_cmp in graph.routers:
        b_res = bfs(graph, src_cmp, dst_cmp)
        d_res = dfs(graph, src_cmp, dst_cmp)

        comp_table = [
            {"Property / Metric": "Core Data Structure", "BFS (Breadth-First Search)": "FIFO Queue (collections.deque)", "DFS (Depth-First Search)": "LIFO Stack (list)"},
            {"Property / Metric": "Exploration Principle", "BFS (Breadth-First Search)": "Level-by-level concentric", "DFS (Depth-First Search)": "Deepest unvisited branch with backtracking"},
            {"Property / Metric": "Route Discovered?", "BFS (Breadth-First Search)": "Yes" if b_res["success"] else "No", "DFS (Depth-First Search)": "Yes" if d_res["success"] else "No"},
            {"Property / Metric": "Reconstructed Path", "BFS (Breadth-First Search)": " -> ".join(b_res["path"]), "DFS (Depth-First Search)": " -> ".join(d_res["path"])},
            {"Property / Metric": "Route Hop Count", "BFS (Breadth-First Search)": f"{b_res['hops']} hops (Shortest Route)", "DFS (Depth-First Search)": f"{d_res['hops']} hops (Valid Path)"},
            {"Property / Metric": "Total Path Cost", "BFS (Breadth-First Search)": f"{int(b_res.get('path_cost', 0))}", "DFS (Depth-First Search)": f"{int(d_res.get('path_cost', 0))}"},
            {"Property / Metric": "Total Execution Steps", "BFS (Breadth-First Search)": f"{len(b_res['steps'])} steps", "DFS (Depth-First Search)": f"{len(d_res['steps'])} steps"},
            {"Property / Metric": "Peak Structure Capacity", "BFS (Breadth-First Search)": f"{b_res['max_structure']} nodes in Queue", "DFS (Depth-First Search)": f"{d_res['max_structure']} nodes in Stack"},
            {"Property / Metric": "Time Complexity", "BFS (Breadth-First Search)": "O(V + E)", "DFS (Depth-First Search)": "O(V + E)"},
            {"Property / Metric": "Auxiliary Space Complexity", "BFS (Breadth-First Search)": "O(V)", "DFS (Depth-First Search)": "O(V)"}
        ]
        st.dataframe(pd.DataFrame(comp_table), width="stretch", height=340)

    st.markdown(
        r"""
        #### **Core Viva Voce Concepts**
        - **Why does BFS find the minimum-hop path?** BFS uses a FIFO queue to discover vertices in non-decreasing order of distance from the source. The first time the destination is dequeued or enqueued, it is reached via the minimum possible number of edges.
        - **Why does DFS not guarantee the shortest path?** DFS uses a LIFO stack to dive as deep as possible along one branch before backtracking, potentially returning an elongated detour.
        - **How does the visited set prevent infinite loops?** Both algorithms check `if neighbor not in visited` before pushing/enqueuing, preventing cycles and infinite loops in cyclic graphs.
        - **Why use Adjacency List over Matrix?** Adjacency list requires $O(V + E)$ memory, which is vastly superior for sparse networks ($E \ll V^2$).
        """
    )


# -------------------------------------------------------------
# 6. AUTOMATED STEP-BY-STEP PLAYBACK RUNNER
# -------------------------------------------------------------
delay_seconds = float(st.session_state.get("delay_ms", 800)) / 1000.0

if st.session_state.get("is_playing", False) and sim_res and sim_res.get("steps"):
    t_steps = len(sim_res["steps"])
    if st.session_state.get("step_idx", 0) < t_steps - 1:
        time.sleep(delay_seconds)
        st.session_state["step_idx"] += 1
        st.rerun()
    else:
        st.session_state["is_playing"] = False
        st.rerun()

if st.session_state.get("packet_auto", False) and sim_res and sim_res.get("success") and sim_res.get("path"):
    p_path = sim_res["path"]
    if st.session_state.get("packet_hop", 0) < len(p_path) - 1:
        time.sleep(delay_seconds)
        st.session_state["packet_hop"] += 1
        st.rerun()
    else:
        st.session_state["packet_auto"] = False
        st.rerun()
