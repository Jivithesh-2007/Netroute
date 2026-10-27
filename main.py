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
from algorithms import bfs, dfs, dijkstra, reconstruct_route_from_parents
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
    """Renders a clean, high-contrast network graph matching the reference UI with real-time traversal animations."""
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

    is_completed = active.get("is_completed", False)
    active_node = active.get("active_node")
    active_edge = active.get("active_edge")
    action_target = active.get("action_target")
    visited_nodes = active.get("visited_nodes", set())
    explored_edges = active.get("explored_edges", set())
    route_nodes = active.get("route_nodes", set())
    route_edges = active.get("route_edges", [])
    packet_node = active.get("packet_node")

    # A. Draw Links
    for u, v in graph.get_edges():
        if u not in graph.routers or v not in graph.routers:
            continue
        e = tuple(sorted((u, v)))
        x1, y1 = graph.routers[u].x, graph.routers[u].y
        x2, y2 = graph.routers[v].x, graph.routers[v].y
        weight = graph.get_weight(u, v)

        is_edge_failed = not graph.is_edge_active(u, v) if hasattr(graph, "is_edge_active") else False
        if is_edge_failed:
            line_color = "#EF4444"  # Red for failed link
            line_width = 2.4
            line_dash = "dot"
        elif active_edge and e == tuple(sorted(active_edge)):
            line_color = "#7C3AED"  # Vibrant purple for active traversal link
            line_width = 4.8
            line_dash = "solid"
        elif is_completed and e in route_edges:
            line_color = "#2563EB"  # Solid blue for discovered route
            line_width = 3.8
            line_dash = "solid"
        elif e in explored_edges:
            line_color = "#F59E0B"  # Orange accent for explored branches
            line_width = 2.4
            line_dash = "solid"
        else:
            line_color = "#E2E8F0"  # Subtle slate for unvisited links
            line_width = 1.8
            line_dash = "solid"

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
        badge_bg = "#FEE2E2" if is_edge_failed else "#FFFFFF"
        badge_border = "#EF4444" if is_edge_failed else "#CBD5E1"
        badge_txt = f"<span style='color:#DC2626;'><b>CUT ({w_text})</b></span>" if is_edge_failed else f"<b>{w_text}</b>"

        fig.add_annotation(
            x=mid_x, y=mid_y,
            text=badge_txt,
            showarrow=False,
            font=dict(size=10, color="#475569", family="-apple-system, sans-serif"),
            bgcolor=badge_bg,
            bordercolor=badge_border,
            borderwidth=1,
            borderpad=3,
            opacity=0.95
        )

    # B. Draw Router Nodes
    nodes = sorted(graph.routers.keys())
    node_x, node_y, node_labels, node_colors, border_colors, text_colors, hover_texts = [], [], [], [], [], [], []

    for rid in nodes:
        r = graph.routers[rid]
        node_x.append(r.x)
        node_y.append(r.y)
        node_labels.append(rid)

        # Node color logic
        if not r.is_online:
            fill_c = "#94A3B8"
            border_c = "#475569"
            txt_c = "#FFFFFF"
        elif is_completed:
            # Traversal complete state matching reference screenshot
            if rid == dst_id:
                fill_c = "#7C3AED"  # Violet for Destination N7 (matching screenshot)
                border_c = "#5B21B6"
                txt_c = "#FFFFFF"
            elif rid in route_nodes:
                fill_c = "#2563EB"  # Blue for route nodes (N1, N2, N4, N6)
                border_c = "#1D4ED8"
                txt_c = "#FFFFFF"
            elif rid in visited_nodes:
                fill_c = "#F59E0B"  # Orange for explored alternative branch (N3, N5)
                border_c = "#D97706"
                txt_c = "#FFFFFF"
            else:
                fill_c = "#FFFFFF"
                border_c = "#94A3B8"
                txt_c = "#475569"
        else:
            # Traversal in-progress state: step-by-step animation
            if rid == active_node:
                fill_c = "#7C3AED"  # Purple for currently active processing router
                border_c = "#5B21B6"
                txt_c = "#FFFFFF"
            elif rid == action_target:
                fill_c = "#0891B2"  # Cyan for target router being discovered / enqueued
                border_c = "#0E7490"
                txt_c = "#FFFFFF"
            elif rid in visited_nodes:
                fill_c = "#2563EB"  # Blue for visited nodes
                border_c = "#1D4ED8"
                txt_c = "#FFFFFF"
            else:
                # Not yet reached
                fill_c = "#FFFFFF"
                border_c = "#CBD5E1"
                txt_c = "#64748B"

        node_colors.append(fill_c)
        border_colors.append(border_c)
        text_colors.append(txt_c)

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
            color=text_colors
        ),
        hoverinfo="text", hovertext=hover_texts, name="Routers", showlegend=False
    ))

    # C. Active Node Highlight Ring during In-Progress Traversal
    if not is_completed and active_node and active_node in graph.routers:
        ar = graph.routers[active_node]
        fig.add_trace(go.Scatter(
            x=[ar.x], y=[ar.y],
            mode="markers",
            marker=dict(size=52, symbol="circle-open", color="#7C3AED", line=dict(color="#7C3AED", width=3.5)),
            hoverinfo="none", showlegend=False
        ))

    # D. Draw Packet Marker
    if packet_node and packet_node in graph.routers:
        pr = graph.routers[packet_node]
        fig.add_trace(go.Scatter(
            x=[pr.x], y=[pr.y],
            mode="markers+text",
            marker=dict(size=48, symbol="circle-open", color="#DC2626", line=dict(color="#DC2626", width=3.5)),
            text=["PKT"], textposition="top center",
            textfont=dict(size=10, color="#DC2626", family="-apple-system, sans-serif"),
            hoverinfo="text", hovertext=f"<b>Packet Location</b><br>Currently at {packet_node}",
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
# 3. TOP MODE BAR & TOPOLOGY PRESETS
# -------------------------------------------------------------
if "active_mode" not in st.session_state:
    st.session_state["active_mode"] = "Select & Connect"

mode_c1, mode_c2, mode_c3, mode_c4, mode_c5, mode_c6 = st.columns([0.8, 1.4, 1.3, 1.4, 1.3, 3.8])

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
    is_wt = st.session_state["active_mode"] == "Edit Weight"
    if st.button("Edit Weight", type="primary" if is_wt else "secondary", width="stretch"):
        st.session_state["active_mode"] = "Edit Weight"
        st.rerun()

with mode_c5:
    is_del = st.session_state["active_mode"] == "Delete Mode"
    if st.button("Delete Mode", type="primary" if is_del else "secondary", width="stretch"):
        st.session_state["active_mode"] = "Delete Mode"
        st.rerun()

with mode_c6:
    pr_col1, pr_col2 = st.columns([2.5, 1.5])
    with pr_col1:
        preset_map = {
            "reference": "Reference 7-Node WAN",
            "weighted_diff": "Weighted Demo (BFS != Dijkstra)",
            "ring": "Ring Network",
            "mesh": "Full Mesh",
            "disconnected": "Disconnected LAN"
        }
        preset_choice = st.selectbox(
            "Preset Topology",
            options=list(preset_map.keys()),
            format_func=lambda k: preset_map[k],
            key="topo_preset_select",
            label_visibility="collapsed"
        )
    with pr_col2:
        if st.button("Load Preset", width="stretch"):
            st.session_state["graph"] = Graph.from_preset(preset_choice)
            g_keys = sorted(st.session_state["graph"].routers.keys())
            st.session_state["source_id"] = g_keys[0] if g_keys else "N1"
            st.session_state["dest_id"] = g_keys[-1] if g_keys else "N7"
            sim.invalidate_simulation()
            sim.execute_routing(st.session_state["graph"], st.session_state.get("selected_algo", "BFS (Breadth First)"), st.session_state["source_id"], st.session_state["dest_id"])
            st.rerun()

# Mode Drawers
if st.session_state["active_mode"] == "Add Router":
    with st.container(border=True):
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

elif st.session_state["active_mode"] == "Edit Weight":
    with st.container(border=True):
        st.markdown('<div class="panel-section-label">INTERACTIVE LINK-WEIGHT EDITOR (FEATURE B)</div>', unsafe_allow_html=True)
        edges = graph.get_edges()
        if not edges:
            st.warning("No transmission links exist in this network. Connect routers first using the controls below.")
        else:
            w_c1, w_c2, w_c3, w_c4 = st.columns([3.2, 1.8, 2.2, 2.8])
            edge_labels = [f"{u} <-> {v} (Cost: {int(graph.get_weight(u, v)) if graph.get_weight(u, v).is_integer() else graph.get_weight(u, v)})" for u, v in edges]
            selected_edge_str = w_c1.selectbox("Select Transmission Link", options=edge_labels, key="edge_weight_sel")
            parts = selected_edge_str.split(" <-> ")
            sel_u = parts[0]
            sel_v = parts[1].split(" ")[0]
            curr_w = graph.get_weight(sel_u, sel_v)

            with w_c2:
                st.metric("Current Weight", f"{int(curr_w) if curr_w.is_integer() else curr_w}")

            with w_c3:
                new_weight = st.number_input("New Weight (>= 0)", min_value=0.0, max_value=999.0, value=float(curr_w), step=1.0, key="new_weight_input")

            with w_c4:
                st.write("")
                if st.button("Apply New Weight", type="primary", width="stretch"):
                    if graph.set_weight(sel_u, sel_v, new_weight):
                        sim.invalidate_simulation()
                        if st.session_state.get("source_id") in graph.routers and st.session_state.get("dest_id") in graph.routers:
                            sim.execute_routing(graph, st.session_state["selected_algo"], st.session_state["source_id"], st.session_state["dest_id"])
                        st.success(f"Updated link ({sel_u} <-> {sel_v}) cost to {new_weight}. Outdated simulation invalidated and route re-evaluated.")
                        st.rerun()
                    else:
                        st.error("Failed to update weight. Weight must be a non-negative number (>= 0).")

        st.caption("Demonstrate BFS vs. Dijkstra divergence: In 'Weighted Demo (BFS != Dijkstra)', the 2-hop route costs 13, whereas the 3-hop route costs only 4.")

elif st.session_state["active_mode"] == "Delete Mode":
    with st.container(border=True):
        dr1, dr2 = st.columns([3, 1.5])
        del_target = dr1.selectbox("Select Router to Remove", options=sorted(graph.routers.keys()))
        if dr2.button("Confirm Delete Router", type="primary"):
            graph.remove_router(del_target)
            sim.invalidate_simulation()
            st.success(f"Removed router {del_target} and all connected transmission links.")
            st.session_state["active_mode"] = "Select & Connect"
            st.rerun()


# -------------------------------------------------------------
# 4. MAIN SPLIT WORKSPACE: GRAPH & CONTROLLER
# -------------------------------------------------------------
r_keys = sorted(graph.routers.keys())
active_state = sim.get_active_state(graph)
current_step = active_state.get("step")
sim_res = active_state.get("res")
is_completed = active_state.get("is_completed", False)
is_playing = st.session_state.get("is_playing", False)

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
        '<div style="margin-top:-28px; margin-bottom:12px;">'
        '<span class="graph-overlay-badge"><span style="color:#38BDF8;">●</span> Undirected LAN/WAN Graph topology layer</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # B. Live Step Action Banner (Explaining algorithm traversal in real time)
    if current_step:
        step_num = current_step.get("step", 1)
        total_steps = len(sim_res["steps"]) if (sim_res and sim_res.get("steps")) else 1
        op_name = current_step.get("operation", "EXPLORE")
        desc_text = current_step.get("description", "")

        if is_completed:
            status_badge = '<span class="step-live-status step-status-completed">COMPLETED</span>'
        elif is_playing:
            status_badge = '<span class="step-live-status step-status-running">RUNNING</span>'
        else:
            status_badge = '<span class="step-live-status step-status-paused">PAUSED</span>'

        st.markdown(
            f"""
            <div class="step-live-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="step-live-tag">STEP {step_num} / {total_steps} &nbsp;&bull;&nbsp; {op_name}</span>
                    {status_badge}
                </div>
                <div class="step-live-desc">{desc_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # C. Link Creation Panel (Matching Reference UI, inside clean bordered container)
    with st.container(border=True):
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


# =============================================================
# RIGHT COLUMN: SIMULATION CONTROLLER & TELEMETRY RESULTS
# =============================================================
with right_col:
    # ---------------------------------------------------------
    # CARD 1: SIMULATION CONTROLLER
    # ---------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            """
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

        # Routing Logic Algorithm Selector (BFS vs DFS vs Dijkstra)
        st.markdown('<div class="panel-section-label" style="margin-top:12px;">ROUTING LOGIC ALGORITHM</div>', unsafe_allow_html=True)
        algo_options = ["BFS (Breadth First)", "DFS (Depth First)", "Dijkstra (Minimum-Cost)"]
        curr_algo = st.session_state.get("selected_algo", "BFS (Breadth First)")
        curr_idx = 2 if "Dijkstra" in curr_algo else (1 if "DFS" in curr_algo else 0)
        algo_selected = st.radio(
            "Algorithm",
            options=algo_options,
            index=curr_idx,
            horizontal=True,
            key="algo_radio_select",
            label_visibility="collapsed"
        )
        if algo_selected != st.session_state["selected_algo"]:
            st.session_state["selected_algo"] = algo_selected
            sim.invalidate_simulation()

        # Dynamic Traversal Delay Slider
        curr_delay = st.session_state.get("delay_ms", 800)
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                <span class="panel-section-label">TRAVERSAL DELAY</span>
                <span style="font-size:0.78rem; font-weight:800; color:#64748B;">{curr_delay}MS</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        delay_ms = st.slider("Delay Slider", min_value=100, max_value=2000, value=curr_delay, step=100, label_visibility="collapsed")
        if delay_ms != curr_delay:
            st.session_state["delay_ms"] = delay_ms
            st.rerun()

        # Run Route Analysis Action Row (Starts real-time step-by-step playback from step 0)
        st.write("")
        btn_col1, btn_col2 = st.columns([4.2, 1])
        with btn_col1:
            if st.button("▷ Run Route Analysis", type="primary", width="stretch", key="run_route_analysis_btn"):
                sim.execute_routing(graph, algo_selected, src_choice, dst_choice)
                st.session_state["step_idx"] = 0
                st.session_state["is_playing"] = True
                st.rerun()

        with btn_col2:
            if st.button("🗑", width="stretch", help="Reset simulation and clear telemetry"):
                sim.reset_simulation()
                sim.invalidate_simulation()
                st.rerun()

        # Step Animation Controls (First, Back, Play/Pause, Next, End)
        if sim_res and sim_res.get("steps"):
            tot_steps = len(sim_res["steps"])
            c_idx = st.session_state.get("step_idx", 0)
            st.write("")
            st.markdown(f'<div class="panel-section-label">PLAYBACK STEPPER (STEP {c_idx + 1} / {tot_steps})</div>', unsafe_allow_html=True)
            sb1, sb2, sb3, sb4, sb5 = st.columns(5)
            with sb1:
                if st.button("|<", width="stretch", disabled=(c_idx == 0), help="Jump to start (Step 1)"):
                    sim.first_step()
                    st.rerun()
            with sb2:
                if st.button("<", width="stretch", disabled=(c_idx == 0), help="Step backward"):
                    sim.step_backward()
                    st.rerun()
            with sb3:
                p_label = "❚❚" if st.session_state.get("is_playing") else "▶"
                if st.button(p_label, width="stretch", type="primary" if not st.session_state.get("is_playing") else "secondary", help="Play / Pause traversal animation"):
                    sim.toggle_playback()
                    st.rerun()
            with sb4:
                if st.button(">", width="stretch", disabled=(c_idx >= tot_steps - 1), help="Step forward"):
                    sim.step_forward()
                    st.rerun()
            with sb5:
                if st.button(">|", width="stretch", disabled=(c_idx >= tot_steps - 1), help="Skip to complete (Final Step)"):
                    sim.last_step()
                    st.rerun()

    # ---------------------------------------------------------
    # CARD 2: ENGINE TELEMETRY RESULTS
    # ---------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            """
            <div class="panel-title">
                <span style="color:#10B981;">📄</span> Engine Telemetry Results
            </div>
            <div class="panel-section-label">CALCULATED PATH ROUTE</div>
            """,
            unsafe_allow_html=True
        )

        if is_completed and sim_res and sim_res.get("success"):
            path_nodes = sim_res.get("path", [])
            st.markdown(render_path_pills(path_nodes), unsafe_allow_html=True)
        elif sim_res and sim_res.get("success"):
            st.markdown('<div class="path-pill-container"><span class="path-pill" style="background:#2563EB;">TRAVERSING GRAPH...</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#64748B; font-style:italic;">No path discovered</div>', unsafe_allow_html=True)

        # 2x2 Statistic Metric Cards Grid
        if is_completed and sim_res and sim_res.get("success"):
            path_cost_val = str(int(sim_res.get("path_cost", 0)))
            hops_val = str(sim_res.get("hops", 4))
            exec_time = f"{max(1, int(sim_res.get('execution_time_ms', 6)))} ms"
            visited_val = str(len(sim_res.get("visited", [])))
            visited_seq = sim_res.get("visited", [])
        elif sim_res:
            step_i = active_state.get("step_idx", 0) + 1
            path_cost_val = "--"
            hops_val = "--"
            exec_time = f"{step_i * int(delay_ms)} ms (Live)"
            visited_val = str(len(active_state.get("visited_nodes", [])))
            visited_seq = active_state.get("visited_sequence", [])
        else:
            path_cost_val = "19"
            hops_val = "4"
            exec_time = "6 ms"
            visited_val = "7"
            visited_seq = ["N1", "N2", "N3", "N4", "N5", "N6", "N7"]

        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown(render_telemetry_stat("PATH COST", path_cost_val), unsafe_allow_html=True)
            st.markdown(render_telemetry_stat("EXECUTION LATENCY", exec_time, is_latency=True), unsafe_allow_html=True)

        with t_col2:
            st.markdown(render_telemetry_stat("HOPS COUNT", hops_val), unsafe_allow_html=True)
            st.markdown(render_telemetry_stat("TOTAL VISITED NODES", visited_val), unsafe_allow_html=True)

        # Search Traversal Sequence (Dynamically expanding as nodes are discovered)
        st.markdown('<div class="panel-section-label" style="margin-top:8px;">SEARCH TRAVERSAL SEQUENCE</div>', unsafe_allow_html=True)
        st.markdown(render_search_sequence(visited_seq), unsafe_allow_html=True)


# -------------------------------------------------------------
# 5. ACADEMIC VERIFICATION & DEEP-INSPECTION PANELS (CO1, CO2, CO5)
# -------------------------------------------------------------
st.write("")
st.markdown("---")

tab_ds, tab_failure, tab_history, tab_challenges, tab_report, tab_hist, tab_route_diag, tab_representations, tab_viva = st.tabs([
    "Queue, Stack & Heap Inspector (CO1)",
    "Failure & Recovery Lab (Feature C)",
    "Simulation History & Replay (Feature D)",
    "DSA Challenge Mode (Feature E)",
    "Export Experiment Report (Feature F)",
    "Step-by-Step Traversal Log",
    "Route Reconstruction & Packet Forwarding (CO5)",
    "Synchronized Graph Representations (CO2)",
    "Algorithm Benchmark & Viva Guide"
])

# =============================================================
# TAB 1: DATA STRUCTURE LIVE INSPECTOR (CO1)
# =============================================================
with tab_ds:
    st.markdown("### Data Structure Live Inspector (CO1)")
    st.caption("Inspect real-time FIFO queue, LIFO stack, and Min-Heap Priority Queue mechanics during graph traversal.")

    ds_c1, ds_c2 = st.columns([1, 1])
    is_dijkstra = "Dijkstra" in st.session_state.get("selected_algo", "")
    is_bfs = "BFS" in st.session_state.get("selected_algo", "")
    is_dfs = "DFS" in st.session_state.get("selected_algo", "")

    with ds_c1:
        if is_dijkstra:
            st.markdown("#### Active Structure: **Min-Heap Priority Queue (`heapq`)**")
            st.info(
                "**Min-Priority Queue:** Stores `(tentative_cost, router_id)`. The router with the lowest "
                "cumulative path cost is extracted from the root in $O(\\log V)$ time using Python's `heapq.heappop`. "
                "Edge relaxations decrease tentative distances and push updated pairs using `heapq.heappush`."
            )
        elif is_bfs:
            st.markdown("#### Active Structure: **FIFO Queue (`collections.deque`)**")
            st.info(
                "**First-In-First-Out (FIFO) Queue:** Elements are enqueued at the **REAR** and dequeued from the **FRONT**. "
                "Because BFS expands concentrically level-by-level, the first path that reaches the destination router is "
                "guaranteed to have the minimum number of hops."
            )
        else:
            st.markdown("#### Active Structure: **LIFO Stack (`list`)**")
            st.info(
                "**Last-In-First-Out (LIFO) Stack:** Elements are pushed and popped exclusively at the **TOP**. "
                "DFS explores a single deep branch until hitting a dead end, triggering explicit backtracking."
            )

        if current_step:
            if is_dijkstra:
                st.markdown("##### Current Elements in Min-Heap Priority Queue")
                pq_items = current_step.get("priority_queue", [])
                if not pq_items:
                    st.caption("*Priority Queue is currently empty.*")
                else:
                    sorted_pq = sorted(pq_items, key=lambda x: x[0])
                    for idx, (dist, node) in enumerate(sorted_pq):
                        root_tag = " [MIN-HEAP ROOT / NEXT EXTRACT-MIN]" if idx == 0 else ""
                        st.markdown(f"- Index **{idx}**: Router **{node}** (Tentative Cost: **{dist}**){root_tag}")

                st.markdown("##### Tentative Distances Table")
                tent_dist = current_step.get("tentative_distances", {})
                parents = current_step.get("parents", {})
                visited_set = set(current_step.get("visited", []))
                dist_rows = []
                for r in sorted(graph.routers.keys()):
                    d = tent_dist.get(r, float("inf"))
                    d_str = "0" if d == 0 else (f"{int(d) if d.is_integer() else d}" if d != float("inf") else "∞")
                    p = parents.get(r)
                    p_str = p if p else ("Origin" if d == 0 else "None")
                    settled_str = "Settled (Visited)" if r in visited_set else "Tentative"
                    dist_rows.append({"Router": r, "Tentative Cost": d_str, "Predecessor Pointer": p_str, "Status": settled_str})
                st.dataframe(pd.DataFrame(dist_rows), width="stretch", height=200)

            else:
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
                if is_dijkstra:
                    st.metric("Edge Relaxations", f"{current_step.get('relaxations', 0)}")
                    st.metric("Heap Pushes", f"{current_step.get('heap_pushes', 0)}")
                elif is_bfs:
                    st.metric("Total Enqueues", f"{current_step.get('enqueues', 0)}")
                    st.metric("Current Queue Size", f"{len(current_step.get('structure', []))}")
                else:
                    st.metric("Total Pushes", f"{current_step.get('pushes', 0)}")
                    st.metric("Current Stack Size", f"{len(current_step.get('structure', []))}")
            with oc2:
                if is_dijkstra:
                    st.metric("Heap Pops", f"{current_step.get('heap_pops', 0)}")
                    st.metric("Peak Heap Size", f"{sim_res.get('max_structure', 0)}")
                elif is_bfs:
                    st.metric("Total Dequeues", f"{current_step.get('dequeues', 0)}")
                    st.metric("Peak Queue Capacity", f"{sim_res.get('max_structure', 0)}")
                else:
                    st.metric("Total Pops", f"{current_step.get('pops', 0)}")
                    st.metric("Peak Stack Capacity", f"{sim_res.get('max_structure', 0)}")

            if is_dfs:
                st.markdown(f"**Backtracking Count:** `{sim_res.get('backtrack_count', 0)}`")
                if current_step.get("is_backtrack"):
                    st.warning(f"Backtracking Active: Dead end reached at '{current_step.get('current_node')}'.")

            if is_dijkstra:
                st.markdown(
                    """
                    > **Greedy Choice Property:** At each step, Dijkstra extracts the vertex with the lowest tentative distance.
                    > Because all link weights are non-negative ($w \\ge 0$), no subsequent edge relaxation can ever find a shorter path to an already settled vertex.
                    """
                )


# =============================================================
# TAB 2: NETWORK FAILURE & RECOVERY LAB (FEATURE C)
# =============================================================
with tab_failure:
    st.markdown("### Network Failure & Fault Recovery Lab (Feature C)")
    st.caption("Simulate link severing and router power failures. Observe dynamic rerouting, alternative path discovery, and network partition isolation.")

    f_col1, f_col2 = st.columns([1, 1])

    with f_col1:
        st.markdown("#### Hardware & Connection Fault Controls")
        rf1, rf2 = st.columns([3, 2])
        target_r = rf1.selectbox("Select Router to Fail/Restore", options=sorted(graph.routers.keys()), key="fail_router_select")
        is_r_online = graph.routers[target_r].is_online if target_r in graph.routers else True
        r_lbl = "Cut Power (Fail)" if is_r_online else "Restore Power"
        if rf2.button(r_lbl, width="stretch", key="fail_router_btn"):
            graph.toggle_router_status(target_r)
            sim.invalidate_simulation()
            sim.execute_routing(graph, st.session_state["selected_algo"], st.session_state["source_id"], st.session_state["dest_id"])
            st.rerun()

        st.write("")
        lf1, lf2 = st.columns([3, 2])
        all_edges = graph.get_edges()
        if all_edges:
            edge_opts = [f"{u} <-> {v}" for u, v in all_edges]
            target_e_str = lf1.selectbox("Select Transmission Link to Cut/Restore", options=edge_opts, key="fail_link_select")
            e_parts = target_e_str.split(" <-> ")
            e_u, e_v = e_parts[0], e_parts[1]
            is_l_active = graph.is_edge_active(e_u, e_v)
            l_lbl = "Sever Link" if is_l_active else "Repair Link"
            if lf2.button(l_lbl, width="stretch", key="fail_link_btn"):
                graph.toggle_connection_status(e_u, e_v)
                sim.invalidate_simulation()
                sim.execute_routing(graph, st.session_state["selected_algo"], st.session_state["source_id"], st.session_state["dest_id"])
                st.rerun()

        st.write("")
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("Restore All Failures", width="stretch", type="primary"):
                graph.restore_all_failures()
                sim.invalidate_simulation()
                sim.execute_routing(graph, st.session_state["selected_algo"], st.session_state["source_id"], st.session_state["dest_id"])
                st.success("Restored all routers and transmission links to online status.")
                st.rerun()
        with rc2:
            if st.button("Set Current as Baseline", width="stretch"):
                sim.capture_baseline_route(graph, st.session_state["selected_algo"], st.session_state["source_id"], st.session_state["dest_id"])
                st.success("Captured current route as reference baseline for failure comparison.")
                st.rerun()

    with f_col2:
        st.markdown("#### Route Comparison & Recovery Status")
        comp = sim.compare_failure_routes(graph, st.session_state["selected_algo"], st.session_state["source_id"], st.session_state["dest_id"])

        c_box1, c_box2 = st.columns(2)
        with c_box1:
            base_p = " -> ".join(comp["baseline_path"]) if comp["baseline_path"] else "None"
            st.metric("Baseline Route", base_p, f"{comp['baseline_hops']} hops | Cost: {comp['baseline_cost']}")
        with c_box2:
            curr_p = " -> ".join(comp["current_path"]) if comp["current_path"] else "UNREACHABLE"
            st.metric("Current Detour Route", curr_p, f"{comp['current_hops']} hops | Cost: {comp['current_cost']}")

        st.markdown(f"**Reachability Status:** `{'REACHABLE' if comp['is_reachable'] else 'NETWORK PARTITIONED (UNREACHABLE)'}`")
        if comp["failed_routers"] or comp["failed_connections"]:
            st.warning(f"**Active Faults:** Offline Routers: `{comp['failed_routers']}` | Cut Links: `{comp['failed_connections']}`")
        else:
            st.success("All network infrastructure components are healthy and operating normally.")

        if not comp["is_reachable"]:
            st.error("No alternative route exists through the surviving network infrastructure. Destination is completely isolated.")
        elif comp["route_changed"]:
            st.info(f"Dynamic Rerouting Success: Packet traffic detoured around failed components. Route changed from original path.")


# =============================================================
# TAB 3: SIMULATION HISTORY & REPLAY (FEATURE D)
# =============================================================
with tab_history:
    st.markdown("### Simulation History & Traversal Replay (Feature D)")
    st.caption("Inspect completed routing experiments, compare algorithms side-by-side, and replay recorded traversals.")

    history_records = sim.get_history()
    if not history_records:
        st.info("No completed simulation runs recorded yet. Run a route analysis to start recording history.")
    else:
        # History Table
        hist_table = []
        for r in history_records:
            hist_table.append({
                "Run ID": r["run_id"],
                "Timestamp": r.get("timestamp", "-"),
                "Algorithm": r["algorithm"],
                "Source": r["source"],
                "Dest": r["dest"],
                "Path": " -> ".join(r["path"]) if r["path"] else "Unreachable",
                "Hops": r["hops"],
                "Cost": r["cost"],
                "Visited": len(r["visited"]),
                "Status": "Success" if r["success"] else "Failed"
            })
        st.dataframe(pd.DataFrame(hist_table), width="stretch", height=240)

        h_c1, h_c2 = st.columns([1, 1])
        with h_c1:
            st.markdown("#### Replay Traversal")
            replay_ids = [r["run_id"] for r in history_records]
            selected_run = st.selectbox("Select Run ID to Replay", options=replay_ids, key="replay_run_sel")
            if st.button("Replay Recorded Run", type="primary", width="stretch"):
                if sim.replay_history_run(selected_run):
                    st.success(f"Loaded Run '{selected_run}' into live playback stepper.")
                    st.rerun()

        with h_c2:
            st.markdown("#### Compare Two Runs")
            if len(history_records) >= 2:
                rc_1, rc_2 = st.columns(2)
                run_a_id = rc_1.selectbox("Run A", options=replay_ids, index=0, key="run_a_sel")
                run_b_id = rc_2.selectbox("Run B", options=replay_ids, index=min(1, len(replay_ids) - 1), key="run_b_sel")
                run_a = next(r for r in history_records if r["run_id"] == run_a_id)
                run_b = next(r for r in history_records if r["run_id"] == run_b_id)

                comp_df = pd.DataFrame([
                    {"Metric": "Algorithm", "Run A": run_a["algorithm"], "Run B": run_b["algorithm"]},
                    {"Metric": "Endpoints", "Run A": f"{run_a['source']} -> {run_a['dest']}", "Run B": f"{run_b['source']} -> {run_b['dest']}"},
                    {"Metric": "Discovered Path", "Run A": " -> ".join(run_a["path"]), "Run B": " -> ".join(run_b["path"])},
                    {"Metric": "Hop Count", "Run A": run_a["hops"], "Run B": run_b["hops"]},
                    {"Metric": "Total Cost", "Run A": run_a["cost"], "Run B": run_b["cost"]},
                    {"Metric": "Visited Nodes", "Run A": len(run_a["visited"]), "Run B": len(run_b["visited"])},
                    {"Metric": "Execution Time", "Run A": f"{run_a['execution_time_ms']:.2f} ms", "Run B": f"{run_b['execution_time_ms']:.2f} ms"}
                ])
                st.dataframe(comp_df, width="stretch", height=240)
            else:
                st.caption("Run at least two different algorithm simulations to enable side-by-side comparison.")

        st.write("")
        cl1, cl2 = st.columns([3, 1])
        confirm_clear = cl1.checkbox("Confirm clearing all recorded history from this session")
        if cl2.button("Clear History", disabled=not confirm_clear, width="stretch"):
            sim.clear_history()
            st.success("Session history cleared.")
            st.rerun()


# =============================================================
# TAB 4: DSA CHALLENGE MODE (FEATURE E)
# =============================================================
with tab_challenges:
    st.markdown("### DSA Challenge Mode (Feature E)")
    st.caption("Interactive graph challenges to test your understanding of BFS, DFS, Dijkstra, and network reachability.")

    c_keys = [c["id"] for c in sim.CHALLENGES]
    c_titles = {c["id"]: f"{c['title']} ({c['difficulty']})" for c in sim.CHALLENGES}
    sel_c_id = st.selectbox("Select Challenge", options=c_keys, format_func=lambda k: c_titles[k], key="challenge_select")
    challenge = next(c for c in sim.CHALLENGES if c["id"] == sel_c_id)

    st.markdown(f"#### **{challenge['title']}**")
    st.info(f"**Scenario:** {challenge['description']}\n\n**Question:** {challenge['question']}")

    user_ans = st.radio("Your Answer Prediction:", options=challenge["options"], key=f"ans_{sel_c_id}")

    sub_c1, sub_c2 = st.columns(2)
    with sub_c1:
        if st.button("Submit Answer", type="primary", width="stretch", key="submit_challenge_btn"):
            eval_res = sim.evaluate_challenge_answer(sel_c_id, user_ans, graph)
            if eval_res["correct"]:
                st.success(f"**Correct!** {eval_res['explanation']}")
            else:
                st.error(f"**Incorrect.** {eval_res['explanation']}\n\nExpected: `{eval_res['expected']}`")

    with sub_c2:
        if st.button("Watch Algorithm Execution", width="stretch", key="watch_challenge_btn"):
            if challenge.get("preset"):
                st.session_state["graph"] = Graph.from_preset(challenge["preset"])
            st.session_state["source_id"] = challenge["source"]
            st.session_state["dest_id"] = challenge["dest"]
            st.session_state["selected_algo"] = challenge["algo"]
            sim.invalidate_simulation()
            sim.execute_routing(st.session_state["graph"], challenge["algo"], challenge["source"], challenge["dest"])
            st.session_state["step_idx"] = 0
            st.session_state["is_playing"] = True
            st.rerun()


# =============================================================
# TAB 5: EXPORT EXPERIMENT REPORT (FEATURE F)
# =============================================================
with tab_report:
    st.markdown("### Exportable Experiment Report (Feature F)")
    st.caption("Generate and download comprehensive research & viva reports for completed routing experiments.")

    src_rep = st.session_state.get("source_id", "N1")
    dst_rep = st.session_state.get("dest_id", "N7")
    algo_rep = st.session_state.get("selected_algo", "BFS (Breadth First)")
    report_data = sim.export_experiment_report(graph, sim_res, algo_rep, src_rep, dst_rep)

    st.markdown(f"#### Experiment: **{report_data['title']}**")
    st.caption(f"Generated at: {report_data['timestamp']} | Topology: {report_data['topology']['active_routers']}/{report_data['topology']['total_routers']} Routers Online, {report_data['topology']['total_connections']} Connections")

    rep_c1, rep_c2, rep_c3, rep_c4 = st.columns(4)
    rep_c1.metric("Algorithm", report_data["algorithm"])
    rep_c2.metric("Discovered Route", " -> ".join(report_data["route"]) if report_data["route"] else "None")
    rep_c3.metric("Hop Count", f"{report_data['hops']} hops")
    rep_c4.metric("Total Weight/Cost", f"{report_data['total_weight']}")

    st.markdown(f"**Theoretical Complexity:** Time: `{report_data['theoretical_complexity']['time']}` | Space: `{report_data['theoretical_complexity']['space']}`")
    st.markdown(f"**Explanation:** {report_data['explanation']}")

    if "algorithm_comparison" in report_data:
        st.markdown("##### Multi-Algorithm Comparison Summary")
        st.dataframe(pd.DataFrame(report_data["algorithm_comparison"]), width="stretch")

    st.write("")
    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        st.download_button(
            "Download Experiment Report (JSON)",
            data=json.dumps(report_data, indent=2),
            file_name="netroute_experiment_report.json",
            mime="application/json",
            width="stretch"
        )
    with exp_c2:
        # Create CSV summary
        flat_report = [
            {"Property": "Title", "Value": report_data["title"]},
            {"Property": "Timestamp", "Value": report_data["timestamp"]},
            {"Property": "Algorithm", "Value": report_data["algorithm"]},
            {"Property": "Source", "Value": report_data["source"]},
            {"Property": "Destination", "Value": report_data["destination"]},
            {"Property": "Route Discovered", "Value": " -> ".join(report_data["route"]) if report_data["route"] else "None"},
            {"Property": "Hop Count", "Value": report_data["hops"]},
            {"Property": "Total Weight", "Value": report_data["total_weight"]},
            {"Property": "Visited Routers", "Value": report_data["visited_count"]},
            {"Property": "Reachability", "Value": report_data["reachability"]},
            {"Property": "Time Complexity", "Value": report_data["theoretical_complexity"]["time"]},
            {"Property": "Space Complexity", "Value": report_data["theoretical_complexity"]["space"]},
            {"Property": "Outcome", "Value": report_data["explanation"]}
        ]
        csv_data = pd.DataFrame(flat_report).to_csv(index=False)
        st.download_button(
            "Download Experiment Report (CSV)",
            data=csv_data,
            file_name="netroute_experiment_report.csv",
            mime="text/csv",
            width="stretch"
        )


# =============================================================
# TAB 6: STEP-BY-STEP TRAVERSAL LOG
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
                "Data Structure State": items_str,
                "Visited Order": visited_str,
                "Traversed Link": edge_str,
                "Description": s["description"]
            })
        log_df = pd.DataFrame(log_rows)
        st.dataframe(log_df, width="stretch", height=320)
        st.download_button("Download Traversal Log (CSV)", data=log_df.to_csv(index=False), file_name="netroute_traversal_log.csv", mime="text/csv")


# =============================================================
# TAB 7: ROUTE RECONSTRUCTION & PACKET FORWARDING (CO5)
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
# TAB 8: SYNCHRONIZED GRAPH REPRESENTATIONS (CO2)
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
# TAB 9: ALGORITHM BENCHMARK & VIVA GUIDE
# =============================================================
with tab_viva:
    st.markdown("### Algorithm Benchmark & Viva Voce Guide")

    src_cmp = st.session_state.get("source_id", "N1")
    dst_cmp = st.session_state.get("dest_id", "N7")
    if src_cmp in graph.routers and dst_cmp in graph.routers:
        b_res = bfs(graph, src_cmp, dst_cmp)
        d_res = dfs(graph, src_cmp, dst_cmp)
        k_res = dijkstra(graph, src_cmp, dst_cmp)

        comp_table = [
            {"Property / Metric": "Core Data Structure", "BFS": "FIFO Queue (collections.deque)", "DFS": "LIFO Stack (list)", "Dijkstra": "Min-Heap Priority Queue (heapq)"},
            {"Property / Metric": "Exploration Principle", "BFS": "Level-by-level concentric", "DFS": "Deepest unvisited branch", "Dijkstra": "Greedy minimum-cost expansion"},
            {"Property / Metric": "Guarantees Shortest Path?", "BFS": "Yes (Minimum Hops, Unweighted)", "DFS": "No (Finds arbitrary reachable path)", "Dijkstra": "Yes (Minimum Total Weight, w >= 0)"},
            {"Property / Metric": "Route Discovered?", "BFS": "Yes" if b_res["success"] else "No", "DFS": "Yes" if d_res["success"] else "No", "Dijkstra": "Yes" if k_res["success"] else "No"},
            {"Property / Metric": "Reconstructed Path", "BFS": " -> ".join(b_res["path"]), "DFS": " -> ".join(d_res["path"]), "Dijkstra": " -> ".join(k_res["path"])},
            {"Property / Metric": "Route Hop Count", "BFS": f"{b_res['hops']} hops", "DFS": f"{d_res['hops']} hops", "Dijkstra": f"{k_res['hops']} hops"},
            {"Property / Metric": "Total Path Cost", "BFS": f"{int(b_res.get('path_cost', 0))}", "DFS": f"{int(d_res.get('path_cost', 0))}", "Dijkstra": f"{int(k_res.get('path_cost', 0))}"},
            {"Property / Metric": "Total Execution Steps", "BFS": f"{len(b_res['steps'])} steps", "DFS": f"{len(d_res['steps'])} steps", "Dijkstra": f"{len(k_res['steps'])} steps"},
            {"Property / Metric": "Peak Structure Capacity", "BFS": f"{b_res['max_structure']} in Queue", "DFS": f"{d_res['max_structure']} in Stack", "Dijkstra": f"{k_res['max_structure']} in Priority Queue"},
            {"Property / Metric": "Time Complexity", "BFS": "O(V + E)", "DFS": "O(V + E)", "Dijkstra": "O((V + E) log V)"},
            {"Property / Metric": "Auxiliary Space Complexity", "BFS": "O(V)", "DFS": "O(V)", "Dijkstra": "O(V)"}
        ]
        st.dataframe(pd.DataFrame(comp_table), width="stretch", height=380)

    st.markdown(
        r"""
        #### **Core Viva Voce Concepts**
        - **Why does BFS find the minimum-hop path?** BFS uses a FIFO queue to discover vertices in non-decreasing order of distance from the source. The first time the destination is enqueued, it is reached via the minimum possible number of edges.
        - **Why does DFS not guarantee the shortest path?** DFS uses a LIFO stack to dive as deep as possible along one branch before backtracking, potentially returning an elongated detour.
        - **How does Dijkstra find the minimum-cost path?** Dijkstra uses a Min-Heap priority queue (`heapq`) to greedily extract the router with the lowest tentative path distance and relaxes outgoing edges. With non-negative edge weights ($w \ge 0$), the tentative distance to any settled router is mathematically optimal.
        - **Why must Dijkstra's edge weights be non-negative ($w \ge 0$)?** If negative edges existed, a previously settled vertex could later have its distance reduced via a negative cycle or path, violating the greedy invariant. (Negative weights require Bellman-Ford).
        - **How does the visited set prevent infinite loops?** Checking `if neighbor not in visited` before enqueuing/pushing prevents cycling and infinite loops in cyclic graphs.
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
