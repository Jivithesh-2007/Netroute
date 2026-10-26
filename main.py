"""
main.py — NetRoute SaaS-Style Interactive Network Packet-Routing Simulator.

A professional, educational web application built with Streamlit and Plotly.
Maps network routing to Data Structures and Algorithms curriculum:
- CO1: Stack and Queue Data Structures (BFS FIFO Queue vs. DFS LIFO Stack).
- CO2: Dynamic Data Structures (Router insertion/deletion, cascading link removal).
- CO5: Graph Structures, Traversal Trees, Reachability, and Shortest-Hop Routing.
"""

import time
import json
from typing import Dict, Any, List, Set, Tuple

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import (
    CUSTOM_CSS, render_stat_card,
    PRIMARY, CYAN, PURPLE, SUCCESS, WARNING, ERROR, TEXT_MAIN, TEXT_MUTED, BORDER,
    COLOR_NODE_DEFAULT, COLOR_NODE_BORDER, COLOR_NODE_SOURCE, COLOR_NODE_DEST,
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
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
sim.init_session()
graph: Graph = st.session_state["graph"]


# -------------------------------------------------------------
# 2. INTERACTIVE PLOTLY NETWORK VISUALIZER
# -------------------------------------------------------------
def build_network_figure(graph: Graph, active: Dict[str, Any], src_id: str, dst_id: str) -> go.Figure:
    """Builds an interactive, high-performance Plotly graph of the network."""
    fig = go.Figure()

    if not graph.routers:
        fig.add_annotation(
            text="Network is empty. Add routers or load a preset from the sidebar.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=TEXT_MUTED)
        )
        fig.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=450,
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

    # C. Draw Discovered Route Links
    rt_x, rt_y = [], []
    for u, v in route_edges:
        if u in graph.routers and v in graph.routers:
            rt_x.extend([graph.routers[u].x, graph.routers[v].x, None])
            rt_y.extend([graph.routers[u].y, graph.routers[v].y, None])

    if rt_x:
        fig.add_trace(go.Scatter(
            x=rt_x, y=rt_y, mode="lines",
            line=dict(color=COLOR_EDGE_ROUTE, width=5),
            hoverinfo="none", name="Active Route", showlegend=True
        ))

    # D. Draw Current Active Step Edge (Link currently traversed)
    if active_edge:
        u, v = active_edge
        if u in graph.routers and v in graph.routers:
            fig.add_trace(go.Scatter(
                x=[graph.routers[u].x, graph.routers[v].x],
                y=[graph.routers[u].y, graph.routers[v].y],
                mode="lines",
                line=dict(color=COLOR_EDGE_ACTIVE, width=5),
                hoverinfo="none", name="Current Hop Link", showlegend=True
            ))

    # E. Draw Routers (Nodes)
    nodes = sorted(graph.routers.keys())
    node_x, node_y, node_labels, node_colors, border_colors, hover_texts = [], [], [], [], [], []

    for rid in nodes:
        r = graph.routers[rid]
        node_x.append(r.x)
        node_y.append(r.y)
        node_labels.append(rid)

        # Color hierarchy
        if not r.is_online:
            fill_c = COLOR_NODE_OFFLINE
            border_c = "#475569"
        elif rid == active_node:
            fill_c = COLOR_NODE_ACTIVE
            border_c = "#9A3412"
        elif rid == src_id:
            fill_c = COLOR_NODE_SOURCE
            border_c = "#1E3A8A"
        elif rid == dst_id:
            fill_c = COLOR_NODE_DEST
            border_c = "#4C1D95"
        elif rid in route_nodes:
            fill_c = COLOR_NODE_ROUTE
            border_c = "#14532D"
        elif rid in visited_nodes:
            fill_c = COLOR_NODE_VISITED
            border_c = "#2563EB"
        else:
            fill_c = COLOR_NODE_DEFAULT
            border_c = COLOR_NODE_BORDER

        node_colors.append(fill_c)
        border_colors.append(border_c)

        status_str = "🟢 Online" if r.is_online else "🔴 Offline"
        nbrs = sorted(graph.adjacency.get(rid, []))
        nbr_str = ", ".join(nbrs) if nbrs else "None"
        ht = (
            f"<b>Router {rid}</b> ({r.name})<br>"
            f"Status: {status_str}<br>"
            f"Degree: {len(nbrs)}<br>"
            f"Neighbors: {nbr_str}"
        )
        hover_texts.append(ht)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=32, color=node_colors, line=dict(color=border_colors, width=2.5)),
        text=node_labels,
        textposition="middle center",
        textfont=dict(
            family="-apple-system, BlinkMacSystemFont, sans-serif",
            size=11,
            color=["#FFFFFF" if c not in ("#FFFFFF", COLOR_NODE_VISITED) else TEXT_MAIN for c in node_colors]
        ),
        hoverinfo="text", hovertext=hover_texts, name="Routers", showlegend=False
    ))

    # F. Packet Position Overlay (when packet animation is active)
    if packet_node and packet_node in graph.routers:
        pr = graph.routers[packet_node]
        fig.add_trace(go.Scatter(
            x=[pr.x], y=[pr.y],
            mode="markers+text",
            marker=dict(size=44, symbol="circle-open", color=COLOR_PACKET, line=dict(color=COLOR_PACKET, width=3.5)),
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
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=450,
        margin=dict(l=20, r=20, t=30, b=20), hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=TEXT_MUTED)),
        xaxis=dict(range=[min_x - dx * 0.15, max_x + dx * 0.15], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[max_y + dy * 0.18, min_y - dy * 0.18], showgrid=False, zeroline=False, showticklabels=False)
    )
    return fig


# -------------------------------------------------------------
# 3. APPLICATION HEADER & BRANDING
# -------------------------------------------------------------
hdr_col1, hdr_col2 = st.columns([7, 3])
with hdr_col1:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap: 10px; margin-bottom: 2px;">
            <h1 style="margin:0; font-size:1.8rem; font-weight:800; color:{PRIMARY};">NetRoute</h1>
            <span style="font-size:1.2rem; color:{BORDER};">•</span>
            <span style="font-size:1.05rem; font-weight:600; color:{TEXT_MAIN};">Interactive Network Packet-Routing Simulator</span>
        </div>
        <div style="font-size:0.83rem; color:{TEXT_MUTED}; margin-bottom: 10px;">
            Graph Algorithm Visualizer (BFS & DFS) • Live Queue / Stack Inspector • Dynamic Topology Management
        </div>
        """,
        unsafe_allow_html=True
    )
with hdr_col2:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:flex-end; align-items:center; gap:6px; margin-top:8px;">
            <span class="co-badge" style="color:{PRIMARY}; border-color:#93C5FD;">CO1: STACK & QUEUE</span>
            <span class="co-badge" style="color:{CYAN}; border-color:#A5F3FC;">CO2: DYNAMIC GRAPH</span>
            <span class="co-badge" style="color:{SUCCESS}; border-color:#86EFAC;">CO5: ROUTING</span>
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------------------------------------
# 4. SIDEBAR CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Simulation Controls")
    router_ids = sorted(graph.routers.keys())

    # Algorithm Selection
    algo = st.radio(
        "Routing Algorithm",
        options=["BFS (Shortest-Hop)", "DFS (Path Discovery)"],
        index=0 if "BFS" in st.session_state["selected_algo"] else 1,
        help="BFS uses a FIFO Queue to find shortest-hop paths. DFS uses a LIFO Stack for deep branch exploration."
    )
    if algo != st.session_state["selected_algo"]:
        st.session_state["selected_algo"] = algo
        sim.invalidate_simulation()

    # Endpoints Selection
    col_src, col_dst = st.columns(2)
    with col_src:
        default_src_idx = router_ids.index(st.session_state["source_id"]) if st.session_state["source_id"] in router_ids else 0
        src = st.selectbox("Source", options=router_ids, index=default_src_idx if router_ids else 0)
        if src != st.session_state["source_id"]:
            st.session_state["source_id"] = src
            sim.invalidate_simulation()

    with col_dst:
        default_dst_idx = router_ids.index(st.session_state["dest_id"]) if st.session_state["dest_id"] in router_ids else (len(router_ids) - 1 if router_ids else 0)
        dst = st.selectbox("Destination", options=router_ids, index=default_dst_idx if router_ids else 0)
        if dst != st.session_state["dest_id"]:
            st.session_state["dest_id"] = dst
            sim.invalidate_simulation()

    # Run Algorithm Button
    if st.button("🚀 Run Routing Algorithm", type="primary", width="stretch"):
        sim.execute_routing(graph, algo, src, dst)

    sim_res = st.session_state.get("sim_res")

    # Step-by-Step Playback Controls
    if sim_res and sim_res.get("steps"):
        st.markdown("---")
        total_steps = len(sim_res["steps"])
        curr_step_idx = st.session_state.get("step_idx", 0)
        st.markdown(f"**Step Navigation ({curr_step_idx + 1} / {total_steps})**")

        step_c1, step_c2, step_c3, step_c4 = st.columns(4)
        if step_c1.button("⏮ First", width="stretch"):
            sim.reset_playback()
        if step_c2.button("◀ Back", width="stretch"):
            sim.step_backward()
        if step_c3.button("Next ▶", width="stretch"):
            sim.step_forward()
        if step_c4.button("End ⏭", width="stretch"):
            sim.jump_to_step(total_steps - 1)

        new_step = st.slider(
            "Scrub Step", min_value=0, max_value=total_steps - 1,
            value=curr_step_idx, label_visibility="collapsed"
        )
        if new_step != curr_step_idx:
            sim.jump_to_step(new_step)

        # Auto-Play Settings
        play_c1, play_c2 = st.columns([1, 1])
        with play_c1:
            auto_play = st.checkbox("Auto-Play", value=st.session_state.get("auto_play", False))
            st.session_state["auto_play"] = auto_play
        with play_c2:
            step_delay = st.slider("Delay (s)", min_value=0.1, max_value=1.5, value=0.4, step=0.1)

        # Packet Transmission Animation
        if sim_res.get("success") and sim_res.get("path"):
            st.markdown("---")
            path = sim_res["path"]
            p_hop = st.session_state.get("packet_hop", 0)
            st.markdown(f"**📦 Packet Transmission**")
            st.caption(f"Hop {p_hop} / {len(path) - 1} • Router: **{path[p_hop]}**")

            pkt_c1, pkt_c2, pkt_c3 = st.columns(3)
            if pkt_c1.button("Step ➡️", width="stretch"):
                sim.packet_step_forward()
            with pkt_c2:
                pkt_auto = st.checkbox("Stream 📦", value=st.session_state.get("packet_auto", False))
                st.session_state["packet_auto"] = pkt_auto
            if pkt_c3.button("Reset ↺", width="stretch"):
                sim.reset_packet()

    # Predefined Topologies
    st.markdown("---")
    with st.expander("🌐 Presets & Topologies", expanded=False):
        preset_choice = st.selectbox(
            "Load Predefined Network",
            options=["Sample Mesh (Default)", "Direct Route (Linear)", "Multiple Routes (Spine/Leaf)", "Cyclic Network (Loops)", "Disconnected Subnets", "Offline Router Barrier"]
        )
        if st.button("Load Preset", width="stretch"):
            mapping = {
                "Sample Mesh (Default)": "sample",
                "Direct Route (Linear)": "direct",
                "Multiple Routes (Spine/Leaf)": "multi_route",
                "Cyclic Network (Loops)": "cyclic",
                "Disconnected Subnets": "disconnected",
                "Offline Router Barrier": "offline_router"
            }
            graph.load_preset(mapping[preset_choice])
            sim.invalidate_simulation()
            st.rerun()

        if st.button("Arrange Circle Layout", width="stretch"):
            graph.auto_layout()
            st.rerun()

        st.markdown("##### Random Generators")
        gen_n = st.slider("Number of Routers", min_value=3, max_value=10, value=6)
        rc1, rc2 = st.columns(2)
        if rc1.button("Connected", width="stretch"):
            graph.generate_random_connected(gen_n)
            sim.invalidate_simulation()
            st.rerun()
        if rc2.button("Disconnected", width="stretch"):
            graph.generate_random_disconnected(gen_n)
            sim.invalidate_simulation()
            st.rerun()

    # Dynamic Topology Editor (CO2)
    with st.expander("🛠️ Dynamic Graph Editor (CO2)", expanded=False):
        st.markdown("##### Add Router")
        ac1, ac2 = st.columns([1, 2])
        new_rid = ac1.text_input("ID", placeholder="R7", max_chars=8).upper()
        new_rname = ac2.text_input("Name", placeholder="Distribution Switch")
        if st.button("Add Router", width="stretch"):
            valid, msg = validate_router_id(new_rid)
            if not valid:
                st.error(msg)
            elif new_rid in graph.routers:
                st.error(f"Router '{new_rid}' already exists.")
            else:
                graph.add_router(new_rid, new_rname)
                graph.auto_layout()
                sim.invalidate_simulation()
                st.success(f"Added Router {new_rid}")
                st.rerun()

        st.markdown("##### Delete Router")
        del_r = st.selectbox("Select Router to Delete", options=["-- Select --"] + router_ids, key="del_r_select")
        if st.button("Delete Router", width="stretch"):
            if del_r != "-- Select --":
                graph.remove_router(del_r)
                sim.invalidate_simulation()
                st.success(f"Removed {del_r}")
                st.rerun()

        st.markdown("##### Add Connection")
        if len(router_ids) >= 2:
            cc1, cc2 = st.columns(2)
            u_conn = cc1.selectbox("From", options=router_ids, key="u_conn")
            v_conn = cc2.selectbox("To", options=[r for r in router_ids if r != u_conn], key="v_conn")
            if st.button("Connect Routers", width="stretch"):
                if graph.add_connection(u_conn, v_conn):
                    sim.invalidate_simulation()
                    st.success(f"Connected {u_conn} <-> {v_conn}")
                    st.rerun()
                else:
                    st.warning("Connection already exists or is invalid.")

        st.markdown("##### Remove Connection")
        edges_list = [f"{u} <-> {v}" for (u, v) in graph.get_edges()]
        if edges_list:
            rem_edge_str = st.selectbox("Select Connection", options=edges_list)
            if st.button("Remove Connection", width="stretch"):
                u_sel, v_sel = [x.strip() for x in rem_edge_str.split("<->")]
                graph.remove_connection(u_sel, v_sel)
                sim.invalidate_simulation()
                st.success(f"Removed connection {rem_edge_str}")
                st.rerun()

        st.markdown("##### Toggle Online / Offline Power")
        tog_r = st.selectbox("Select Router", options=router_ids, key="tog_r_select")
        if st.button("Toggle Power State", width="stretch"):
            new_state = graph.toggle_router_status(tog_r)
            sim.invalidate_simulation()
            st.info(f"Router {tog_r} is now {'🟢 Online' if new_state else '🔴 Offline'}")
            st.rerun()

    # JSON Topology Export & Import
    with st.expander("💾 Export & Import JSON", expanded=False):
        topo_data = json.dumps(graph.to_dict(), indent=2)
        st.download_button(
            label="Download Topology JSON", data=topo_data,
            file_name="network_topology.json", mime="application/json", width="stretch"
        )
        uploaded = st.file_uploader("Import Topology JSON", type=["json"])
        if uploaded is not None:
            try:
                data = json.load(uploaded)
                success, msg = graph.load_from_dict(data)
                if success:
                    sim.invalidate_simulation()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            except Exception as e:
                st.error(f"Error parsing JSON: {e}")


# -------------------------------------------------------------
# 5. MAIN WORKSPACE: ACTIVE SIMULATION STATE & METRICS
# -------------------------------------------------------------
active_state = sim.get_active_state(graph)
current_step = active_state.get("step")
sim_res = active_state.get("res")

# Metrics calculations
total_v = len(graph.routers)
online_v = sum(1 for r in graph.routers.values() if r.is_online)
offline_v = total_v - online_v
total_e = len(graph.get_edges())
comps = graph.get_connected_components()
comp_count = len(comps)

route_hops = f"{sim_res['hops']} hops" if (sim_res and sim_res.get("success")) else "—"
max_struct = str(sim_res.get("max_structure", "—")) if sim_res else "—"
tot_steps = str(len(sim_res.get("steps", []))) if (sim_res and sim_res.get("steps")) else "Ready"
reachability_str = "Reachable 🟢" if (sim_res and sim_res.get("success")) else ("Unreachable 🔴" if sim_res else "Pending")

# Render Compact SaaS Statistic Cards
m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
with m1:
    st.markdown(render_stat_card("Routers", f"{total_v}", f"{online_v} on, {offline_v} off", PRIMARY), unsafe_allow_html=True)
with m2:
    st.markdown(render_stat_card("Links", f"{total_e}", "Undirected edges", CYAN), unsafe_allow_html=True)
with m3:
    st.markdown(render_stat_card("Components", f"{comp_count}", "1 = Connected" if comp_count == 1 else "Partitioned", SUCCESS if comp_count == 1 else WARNING), unsafe_allow_html=True)
with m4:
    st.markdown(render_stat_card("Destination", reachability_str, f"Target: {dst}", SUCCESS if (sim_res and sim_res.get("success")) else WARNING), unsafe_allow_html=True)
with m5:
    st.markdown(render_stat_card("Route Hops", route_hops, "Shortest" if (sim_res and "BFS" in sim_res.get("algorithm", "")) else "Discovered", SUCCESS if (sim_res and sim_res.get("success")) else TEXT_MUTED), unsafe_allow_html=True)
with m6:
    st.markdown(render_stat_card("Max Struct", max_struct, "Queue / Stack", PURPLE), unsafe_allow_html=True)
with m7:
    curr_idx_disp = f"Step {st.session_state.get('step_idx', 0) + 1}" if sim_res else "Ready"
    st.markdown(render_stat_card("Total Steps", tot_steps, curr_idx_disp, PRIMARY), unsafe_allow_html=True)

st.write("")

# Render Plotly Graph Visualization
network_fig = build_network_figure(graph, active_state, st.session_state["source_id"], st.session_state["dest_id"])
st.plotly_chart(network_fig, width="stretch", config={"displayModeBar": True, "scrollZoom": True})

# Step / Packet Message Banner
if current_step:
    st.info(f"**Step {current_step['step']} [{current_step['operation']}]:** {current_step['description']}")
elif sim_res:
    if sim_res.get("success"):
        st.success(f"**Execution Completed:** {sim_res.get('message')}")
    else:
        st.error(f"**Routing Failed:** {sim_res.get('message')}")

if active_state.get("packet_status") and sim_res and sim_res.get("success"):
    st.caption(f"**📦 Packet Status:** {active_state['packet_status']}")


# -------------------------------------------------------------
# 6. EDUCATIONAL INSPECTOR TABS
# -------------------------------------------------------------
tab_inspect, tab_repr, tab_tree, tab_compare, tab_trace, tab_learn = st.tabs([
    "🔍 Live Queue / Stack Inspector (CO1)",
    "📊 Graph Representations (CO2 & CO5)",
    "🌲 Traversal Tree & Route (CO5)",
    "⚖️ Algorithm Comparison (BFS vs DFS)",
    "📜 Execution Trace Log",
    "📚 Learning & Viva Guide (CO1, CO2, CO5)"
])

# ----------------- TAB 1: LIVE QUEUE / STACK INSPECTOR -----------------
with tab_inspect:
    is_bfs = "BFS" in st.session_state.get("selected_algo", "")
    struct_name = "FIFO Queue" if is_bfs else "LIFO Stack"
    st.markdown(f"#### Live {struct_name} Inspector")

    if current_step:
        items = current_step.get("structure", [])
        st.write(f"**Current Operation:** `{current_step.get('operation')}` • **Active Router:** `{current_step.get('current_node') or 'None'}` • **Structure Size:** `{len(items)}`")

        if not items:
            st.caption(f"*The {struct_name} is currently empty.*")
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
                st.caption("**FIFO Invariant:** Routers are dequeued from the **FRONT** and enqueued at the **REAR**.")
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
                st.caption("**LIFO Invariant:** Stack is shown from Bottom (left) to Top (right). Elements are pushed and popped at the **TOP**.")

        # Visited Sequence & Parent Map
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown("##### Visited Sequence (Order of Exploration):")
            visited_list = current_step.get("visited", [])
            if visited_list:
                v_chips = [f'<span class="chip chip-visited">{n}</span>' for n in visited_list]
                st.markdown(f'<div>{" ➔ ".join(v_chips)}</div>', unsafe_allow_html=True)
            else:
                st.caption("*No routers marked visited yet.*")

        with ic2:
            st.markdown("##### Predecessor / Parent Map:")
            parent_dict = current_step.get("parents", {})
            if parent_dict:
                pm_df = pd.DataFrame([
                    {"Router": node, "Parent": par if par is not None else "None (Source)"}
                    for node, par in sorted(parent_dict.items())
                ])
                st.dataframe(pm_df, width="stretch", height=150)
            else:
                st.caption("*Parent map unpopulated.*")
    else:
        st.info("Run an algorithm (BFS or DFS) from the sidebar to inspect live queue or stack transitions.")

# ----------------- TAB 2: GRAPH REPRESENTATIONS -----------------
with tab_repr:
    gr_c1, gr_c2 = st.columns(2)
    with gr_c1:
        st.markdown("#### Dynamic Adjacency List")
        st.caption("Primary graph representation. Stores adjacent incident neighbors per vertex. Space complexity: **O(V + E)**.")
        adj_list = graph.get_adjacency_list()
        for rid, neighbors in adj_list.items():
            r = graph.routers.get(rid)
            status_dot = "🟢" if (r and r.is_online) else "🔴"
            nbr_tags = "".join([f'<span class="chip chip-item">{n}</span>' for n in neighbors]) if neighbors else '<span style="color:#94A3B8; font-style:italic;">No neighbors</span>'
            st.markdown(f"**{status_dot} {rid}** ➔ {nbr_tags}", unsafe_allow_html=True)

    with gr_c2:
        st.markdown("#### Synchronized Adjacency Matrix")
        st.caption("2D matrix representation where cell (u, v) = 1 denotes a connection. Space complexity: **O(V²)**.")
        nodes, matrix = graph.get_adjacency_matrix()
        if nodes:
            mat_df = pd.DataFrame(matrix, index=nodes, columns=nodes)
            st.dataframe(mat_df, width="stretch", height=240)
        else:
            st.caption("*Network is empty.*")

# ----------------- TAB 3: TRAVERSAL TREE & ROUTE -----------------
with tab_tree:
    if sim_res:
        tr_c1, tr_c2 = st.columns(2)
        with tr_c1:
            st.markdown("#### Discovered Route")
            if sim_res.get("success") and sim_res.get("path"):
                st.success(f"**Route Path:** {' ➔ '.join(sim_res['path'])}")
                st.write(f"- **Total Hops:** {sim_res.get('hops')}")
                st.write(f"- **Algorithm Used:** {sim_res.get('algorithm')}")
                st.write(f"- **Execution Time:** {sim_res.get('execution_time_ms', 0):.3f} ms")
                if "BFS" in sim_res.get("algorithm", ""):
                    st.caption("BFS explores level-by-level, guaranteeing the **minimum number of hops** in unweighted networks.")
                else:
                    st.caption("DFS dives deeply along branches. It discovers a **valid reachable path**, but does not guarantee minimum hops.")
            else:
                st.error(sim_res.get("message"))

        with tr_c2:
            st.markdown("#### Traversal Tree Edges")
            st.caption("Parent-child relationships established when discovering unvisited nodes.")
            tree_edges = sim_res.get("tree_edges", [])
            if tree_edges:
                tree_df = pd.DataFrame([
                    {"Parent (From)": u, "Child (Discovered)": v}
                    for u, v in tree_edges
                ])
                st.dataframe(tree_df, width="stretch", height=200)
            else:
                st.caption("*No traversal tree edges recorded.*")
    else:
        st.info("Run an algorithm to display route details and traversal tree edges.")

# ----------------- TAB 4: ALGORITHM COMPARISON (BFS VS DFS) -----------------
with tab_compare:
    st.markdown("#### Comparative Benchmark: BFS vs. DFS on Current Graph")
    st.caption("Side-by-side execution of both algorithms using the currently selected source and destination.")

    if st.session_state["source_id"] in graph.routers and st.session_state["dest_id"] in graph.routers:
        bfs_bench = bfs(graph, st.session_state["source_id"], st.session_state["dest_id"])
        dfs_bench = dfs(graph, st.session_state["source_id"], st.session_state["dest_id"])

        comp_data = [
            {
                "Metric / Feature": "Data Structure",
                "BFS (Breadth-First)": "FIFO Queue (`collections.deque`)",
                "DFS (Depth-First)": "LIFO Stack (`list`)"
            },
            {
                "Metric / Feature": "Route Found?",
                "BFS (Breadth-First)": "Yes 🟢" if bfs_bench["success"] else "No 🔴",
                "DFS (Depth-First)": "Yes 🟢" if dfs_bench["success"] else "No 🔴"
            },
            {
                "Metric / Feature": "Discovered Path",
                "BFS (Breadth-First)": " ➔ ".join(bfs_bench["path"]) if bfs_bench["path"] else "None",
                "DFS (Depth-First)": " ➔ ".join(dfs_bench["path"]) if dfs_bench["path"] else "None"
            },
            {
                "Metric / Feature": "Route Hop Count",
                "BFS (Breadth-First)": f"{bfs_bench['hops']} hops (Guaranteed Shortest)",
                "DFS (Depth-First)": f"{dfs_bench['hops']} hops (Valid Path)"
            },
            {
                "Metric / Feature": "Total Recorded Steps",
                "BFS (Breadth-First)": f"{len(bfs_bench['steps'])} steps",
                "DFS (Depth-First)": f"{len(dfs_bench['steps'])} steps"
            },
            {
                "Metric / Feature": "Maximum Structure Size",
                "BFS (Breadth-First)": f"{bfs_bench['max_structure']} nodes in Queue",
                "DFS (Depth-First)": f"{dfs_bench['max_structure']} nodes in Stack"
            },
            {
                "Metric / Feature": "Time Complexity",
                "BFS (Breadth-First)": "O(V + E)",
                "DFS (Depth-First)": "O(V + E)"
            },
            {
                "Metric / Feature": "Space Complexity",
                "BFS (Breadth-First)": "O(V)",
                "DFS (Depth-First)": "O(V)"
            }
        ]
        st.dataframe(pd.DataFrame(comp_data), width="stretch", height=320)
    else:
        st.info("Select valid source and destination routers to view algorithm comparison.")

# ----------------- TAB 5: EXECUTION TRACE LOG -----------------
with tab_trace:
    st.markdown("#### Chronological Step Trace Log")
    if sim_res and sim_res.get("steps"):
        trace_data = []
        for s in sim_res["steps"]:
            trace_data.append({
                "Step #": s["step"],
                "Operation": s["operation"],
                "Current Router": s["current_node"] or "—",
                "Active Link": f"{s['active_edge'][0]} <-> {s['active_edge'][1]}" if s.get("active_edge") else "—",
                "Structure Snapshot": ", ".join(s["structure"]) if s["structure"] else "[Empty]",
                "Description": s["description"]
            })
        st.dataframe(pd.DataFrame(trace_data), width="stretch", height=300)
    else:
        st.info("Step trace log will populate after running BFS or DFS.")

# ----------------- TAB 6: LEARNING & VIVA GUIDE -----------------
with tab_co:
    st.markdown("### 🎓 Academic Curriculum & Viva Guide")

    st.markdown(
        """
        #### **CO1 — Stack and Queue Data Structures**
        - **Breadth-First Search (BFS):** Implemented using a **First-In-First-Out (FIFO) Queue** (`collections.deque`). Routers are enqueued at the rear and dequeued from the front. Guarantees level-order exploration and shortest-hop routing in unweighted networks.
        - **Depth-First Search (DFS):** Implemented using an explicit **Last-In-First-Out (LIFO) Stack** (`list`). Routers are pushed and popped from the top of the stack. Explores deep branches until dead ends, triggering explicit backtracking.
        - **Inspector Proof:** Live visual chips clearly mark FRONT/REAR for queues and TOP/BOTTOM for stacks.

        ---

        #### **CO2 — Dynamic Data Structures**
        - **Dynamic Memory Allocation:** Routers (vertices) and links (edges) can be dynamically inserted, renamed, and deleted during runtime without requiring application reboots.
        - **Cascading Integrity:** Deleting a router automatically cascades to remove all incident connections from the adjacency list, preventing dangling pointers or orphaned graph references.
        - **Failure Simulation:** Simulates hardware equipment downtime via online/offline toggling.

        ---

        #### **CO5 — Graph Structures, Traversal & Routing**
        - **Adjacency List:** Primary graph representation with **$O(V + E)$** storage efficiency, optimal for sparse networks.
        - **Adjacency Matrix:** Synchronized **$O(V^2)$** representation providing constant-time **$O(1)$** link lookups.
        - **Packet Transmission:** Valid discovered routes are simulated hop-by-hop, mimicking real-world IP packet forwarding from source gateway to destination host.
        - **Computational Complexity:**
          - **Time Complexity:** $O(V + E)$ for both BFS and DFS when traversing adjacency lists.
          - **Auxiliary Space:** $O(V)$ for visited sets, predecessor maps, and queue/stack storage.
        """
    )


# -------------------------------------------------------------
# 7. AUTOMATIC PLAYBACK & PACKET STREAMING RUNNER
# -------------------------------------------------------------
if st.session_state.get("auto_play", False) and sim_res and sim_res.get("steps"):
    total_steps = len(sim_res["steps"])
    if st.session_state.get("step_idx", 0) < total_steps - 1:
        time.sleep(step_delay)
        st.session_state["step_idx"] += 1
        st.rerun()
    else:
        st.session_state["auto_play"] = False
        st.rerun()

if st.session_state.get("packet_auto", False) and sim_res and sim_res.get("success") and sim_res.get("path"):
    path = sim_res["path"]
    if st.session_state.get("packet_hop", 0) < len(path) - 1:
        time.sleep(step_delay)
        st.session_state["packet_hop"] += 1
        st.rerun()
    else:
        st.session_state["packet_auto"] = False
        st.rerun()
