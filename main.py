"""
main.py — NetRoute: Network Packet-Routing Simulator.

A clean, modern, educational network packet routing simulator.
Integrated Course Outcomes:
- CO3: Searching and Sorting Algorithm Evaluation (Linear vs. Binary Search, Bubble vs. Insertion Sort).
- CO4: Routing Traversal Tree Structures (BFS Traversal Spanning Tree and Invariants).
- CO5: Graph-Based Packet Routing vs. Traditional Hop-by-Hop Routing Table Forwarding.
"""

from typing import Dict, Any, List, Set, Tuple
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import (
    CUSTOM_CSS, render_path_pills, render_step_card,
    PRIMARY, PRIMARY_DARK, CYAN, PURPLE, SUCCESS, WARNING, ERROR, TEXT_MAIN, TEXT_MUTED, BORDER
)
from network import Graph
from algorithms import (
    bfs, dfs, linear_search, binary_search, bubble_sort, insertion_sort, build_traversal_tree
)
import simulation as sim

# -------------------------------------------------------------
# 1. PAGE SETUP & CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="NetRoute — Network Packet Routing",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
sim.init_session()
graph: Graph = st.session_state["graph"]

# Initial auto-run so dashboard is populated on launch
if st.session_state.get("sim_res") is None:
    src_init = st.session_state.get("source_id", "N1")
    dst_init = st.session_state.get("dest_id", "N7")
    if src_init in graph.routers and dst_init in graph.routers:
        res_init = sim.execute_routing(graph, st.session_state.get("selected_algo", "BFS (Breadth-First)"), src_init, dst_init)
        if res_init.get("steps"):
            st.session_state["step_idx"] = len(res_init["steps"]) - 1

# -------------------------------------------------------------
# 2. PLOTLY GRAPH & TREE VISUALIZATIONS
# -------------------------------------------------------------
def build_network_figure(graph: Graph, active: Dict[str, Any], src_id: str, dst_id: str, height: int = 420) -> go.Figure:
    """Renders an interactive network graph with real-time traversal and packet animations."""
    fig = go.Figure()

    if not graph.routers:
        fig.add_annotation(
            text="Network is empty. Please select a topology preset.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=TEXT_MUTED)
        )
        fig.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=height,
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

        if not graph.is_edge_active(u, v):
            line_color = "#EF4444"
            line_width = 2.4
            line_dash = "dot"
        elif active_edge and e == tuple(sorted(active_edge)):
            line_color = "#7C3AED"
            line_width = 4.0
            line_dash = "solid"
        elif is_completed and e in route_edges:
            line_color = "#10B981"
            line_width = 3.8
            line_dash = "solid"
        elif e in explored_edges:
            line_color = "#F59E0B"
            line_width = 2.2
            line_dash = "solid"
        else:
            line_color = "#CBD5E1"
            line_width = 1.8
            line_dash = "solid"

        fig.add_trace(go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode="lines",
            line=dict(color=line_color, width=line_width, dash=line_dash),
            hoverinfo="none",
            showlegend=False
        ))

        # Weight badge on link
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0
        w_text = str(int(weight) if weight.is_integer() else weight)

        fig.add_annotation(
            x=mid_x, y=mid_y,
            text=f"<b>{w_text}</b>",
            showarrow=False,
            font=dict(size=10, color="#475569"),
            bgcolor="#FFFFFF",
            bordercolor="#CBD5E1",
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

        if not r.is_online:
            fill_c = "#94A3B8"
            border_c = "#475569"
            txt_c = "#FFFFFF"
        elif is_completed:
            if rid == dst_id:
                fill_c = "#F59E0B"
                border_c = "#D97706"
                txt_c = "#FFFFFF"
            elif rid == src_id:
                fill_c = "#10B981"
                border_c = "#059669"
                txt_c = "#FFFFFF"
            elif rid in route_nodes:
                fill_c = "#059669"
                border_c = "#047857"
                txt_c = "#FFFFFF"
            elif rid in visited_nodes:
                fill_c = "#38BDF8"
                border_c = "#0284C7"
                txt_c = "#FFFFFF"
            else:
                fill_c = "#FFFFFF"
                border_c = "#94A3B8"
                txt_c = "#475569"
        else:
            if rid == active_node:
                fill_c = "#7C3AED"
                border_c = "#5B21B6"
                txt_c = "#FFFFFF"
            elif rid == action_target:
                fill_c = "#0891B2"
                border_c = "#0E7490"
                txt_c = "#FFFFFF"
            elif rid == src_id:
                fill_c = "#10B981"
                border_c = "#059669"
                txt_c = "#FFFFFF"
            elif rid == dst_id:
                fill_c = "#F59E0B"
                border_c = "#D97706"
                txt_c = "#FFFFFF"
            elif rid in visited_nodes:
                fill_c = "#38BDF8"
                border_c = "#0284C7"
                txt_c = "#FFFFFF"
            else:
                fill_c = "#FFFFFF"
                border_c = "#CBD5E1"
                txt_c = "#64748B"

        node_colors.append(fill_c)
        border_colors.append(border_c)
        text_colors.append(txt_c)

        sub_text = r.name
        if rid == src_id and "(Src)" not in sub_text:
            sub_text += " (Src)"
        elif rid == dst_id and "(Dst)" not in sub_text:
            sub_text += " (Dst)"

        sub_color = "#10B981" if rid == src_id else ("#F59E0B" if rid == dst_id else "#1E293B")

        fig.add_annotation(
            x=r.x, y=r.y - 26,
            text=f"<b>{sub_text}</b>",
            showarrow=False,
            font=dict(size=10, color=sub_color),
            xanchor="center", yanchor="bottom"
        )

        nbrs = sorted(graph.adjacency.get(rid, []))
        hover_texts.append(
            f"<b>Router {rid}</b> ({r.name})<br>"
            f"Status: {'Online' if r.is_online else 'Offline'}<br>"
            f"Neighbors: {', '.join(nbrs) if nbrs else 'None'}"
        )

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=34, color=node_colors, line=dict(color=border_colors, width=2.5)),
        text=node_labels,
        textposition="middle center",
        textfont=dict(size=11, color=text_colors, family="-apple-system, sans-serif"),
        hoverinfo="text", hovertext=hover_texts, showlegend=False
    ))

    # C. Active node ring
    if not is_completed and active_node and active_node in graph.routers:
        ar = graph.routers[active_node]
        fig.add_trace(go.Scatter(
            x=[ar.x], y=[ar.y],
            mode="markers",
            marker=dict(size=50, symbol="circle-open", color="#7C3AED", line=dict(color="#7C3AED", width=3.0)),
            hoverinfo="none", showlegend=False
        ))

    # D. Packet marker
    if packet_node and packet_node in graph.routers:
        pr = graph.routers[packet_node]
        fig.add_trace(go.Scatter(
            x=[pr.x], y=[pr.y],
            mode="markers+text",
            marker=dict(size=46, symbol="circle-open", color="#DC2626", line=dict(color="#DC2626", width=3.2)),
            text=["PKT"], textposition="top center",
            textfont=dict(size=10, color="#DC2626"),
            hoverinfo="text", hovertext=f"Packet at {packet_node}", showlegend=False
        ))

    all_x = [r.x for r in graph.routers.values()]
    all_y = [r.y for r in graph.routers.values()]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    dx = max(80.0, max_x - min_x)
    dy = max(80.0, max_y - min_y)

    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=height,
        margin=dict(l=30, r=30, t=35, b=30), hovermode="closest",
        xaxis=dict(range=[min_x - dx * 0.12, max_x + dx * 0.12], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[max_y + dy * 0.22, min_y - dy * 0.22], showgrid=False, zeroline=False, showticklabels=False)
    )
    return fig


def build_traversal_tree_figure(tree_data: Dict[str, Any], src_id: str, dst_id: str, height: int = 400) -> go.Figure:
    """Renders a hierarchical Plotly figure of the BFS Traversal Tree (CO4)."""
    fig = go.Figure()
    if not tree_data or not tree_data.get("nodes"):
        fig.add_annotation(
            text="No traversal tree available. Run routing to generate the tree.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=TEXT_MUTED)
        )
        fig.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=height,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig

    levels = tree_data.get("levels", {})
    edges = tree_data.get("edges", [])
    path_list = tree_data.get("path_to_dest", [])
    path_nodes = set(path_list)

    path_edges = set()
    for i in range(len(path_list) - 1):
        path_edges.add((path_list[i], path_list[i + 1]))

    nodes_by_level: Dict[int, List[str]] = {}
    for node, lvl in levels.items():
        nodes_by_level.setdefault(lvl, []).append(node)

    pos: Dict[str, Tuple[float, float]] = {}
    max_lvl = max(nodes_by_level.keys()) if nodes_by_level else 0
    y_step = 280.0 / max(1, max_lvl) if max_lvl > 0 else 100.0

    for lvl, n_list in nodes_by_level.items():
        sorted_nodes = sorted(n_list)
        y_val = 360.0 - (lvl * y_step)
        k = len(sorted_nodes)
        for idx, node in enumerate(sorted_nodes):
            x_val = 100.0 + (500.0 / (k + 1)) * (idx + 1)
            pos[node] = (x_val, y_val)

    # Draw tree edges
    for parent, child in edges:
        if parent in pos and child in pos:
            x1, y1 = pos[parent]
            x2, y2 = pos[child]
            is_path_edge = (parent, child) in path_edges
            line_color = "#10B981" if is_path_edge else "#8B5CF6"
            line_width = 3.5 if is_path_edge else 2.0

            fig.add_trace(go.Scatter(
                x=[x1, x2], y=[y1, y2],
                mode="lines",
                line=dict(color=line_color, width=line_width),
                hoverinfo="none", showlegend=False
            ))

    # Draw tree nodes
    tx, ty, tlabels, tcolors, tborders, ttexts = [], [], [], [], [], []
    for node in tree_data.get("nodes", []):
        if node in pos:
            x, y = pos[node]
            tx.append(x)
            ty.append(y)
            tlabels.append(node)

            if node == src_id:
                tcolors.append("#10B981")
                tborders.append("#059669")
                ttexts.append("#FFFFFF")
            elif node == dst_id:
                tcolors.append("#F59E0B")
                tborders.append("#D97706")
                ttexts.append("#FFFFFF")
            elif node in path_nodes:
                tcolors.append("#059669")
                tborders.append("#047857")
                ttexts.append("#FFFFFF")
            else:
                tcolors.append("#EDE9FE")
                tborders.append("#8B5CF6")
                ttexts.append("#5B21B6")

    fig.add_trace(go.Scatter(
        x=tx, y=ty,
        mode="markers+text",
        marker=dict(size=34, color=tcolors, line=dict(color=tborders, width=2.5)),
        text=tlabels,
        textposition="middle center",
        textfont=dict(size=11, color=ttexts, family="-apple-system, sans-serif"),
        hoverinfo="text", hovertext=[f"Router {l} (Depth {levels.get(l, 0)})" for l in tlabels],
        showlegend=False
    ))

    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=height,
        margin=dict(l=30, r=30, t=30, b=30),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    return fig


# -------------------------------------------------------------
# 3. STREAMLIT SIDEBAR
# -------------------------------------------------------------
st.sidebar.title("NetRoute")
st.sidebar.markdown("*Network Packet Routing Simulator*")
st.sidebar.caption("Graph-based routing algorithms (BFS & DFS) and routing-table-based forwarding.")
st.sidebar.markdown("---")

# Section 1: Network Topology
st.sidebar.subheader("Network Topology")
preset_options = {
    "reference": "Reference 7-Node WAN",
    "ring": "Ring Network",
    "mesh": "Mesh Network",
    "disconnected": "Disconnected LAN"
}

current_preset = st.session_state.get("selected_preset", "reference")
if current_preset not in preset_options:
    current_preset = "reference"

selected_preset_key = st.sidebar.selectbox(
    "Select Topology Preset",
    options=list(preset_options.keys()),
    format_func=lambda k: preset_options[k],
    index=list(preset_options.keys()).index(current_preset),
    key="topology_selectbox"
)

# Handle Topology Change
if selected_preset_key != st.session_state.get("selected_preset"):
    st.session_state["selected_preset"] = selected_preset_key
    st.session_state["graph"] = Graph.from_preset(selected_preset_key)
    graph = st.session_state["graph"]
    
    g_nodes = sorted(list(graph.routers.keys()))
    st.session_state["source_id"] = g_nodes[0] if g_nodes else "N1"
    st.session_state["dest_id"] = g_nodes[-1] if g_nodes else "N7"
    
    sim.invalidate_simulation()
    sim.execute_routing(
        graph,
        st.session_state.get("selected_algo", "BFS (Breadth-First)"),
        st.session_state["source_id"],
        st.session_state["dest_id"]
    )
    if st.session_state.get("sim_res", {}).get("steps"):
        st.session_state["step_idx"] = len(st.session_state["sim_res"]["steps"]) - 1
    st.rerun()

graph = st.session_state["graph"]
router_keys = sorted(list(graph.routers.keys()))

# Section 2: Routing Configuration
st.sidebar.markdown("---")
st.sidebar.subheader("Routing Configuration")

if st.session_state.get("source_id") not in router_keys:
    st.session_state["source_id"] = router_keys[0] if router_keys else "N1"
if st.session_state.get("dest_id") not in router_keys:
    st.session_state["dest_id"] = router_keys[-1] if router_keys else "N7"

src_idx = router_keys.index(st.session_state["source_id"]) if st.session_state["source_id"] in router_keys else 0
dst_idx = router_keys.index(st.session_state["dest_id"]) if st.session_state["dest_id"] in router_keys else (len(router_keys) - 1 if router_keys else 0)

selected_src = st.sidebar.selectbox("Source Router", options=router_keys, index=src_idx, key="src_select")
selected_dst = st.sidebar.selectbox("Destination Router", options=router_keys, index=dst_idx, key="dst_select")

st.session_state["source_id"] = selected_src
st.session_state["dest_id"] = selected_dst

algo_options = ["BFS (Breadth-First)", "DFS (Depth-First)"]
algo_idx = 0 if "BFS" in st.session_state.get("selected_algo", "BFS") else 1
selected_algo = st.sidebar.selectbox("Algorithm", options=algo_options, index=algo_idx, key="algo_select")
st.session_state["selected_algo"] = selected_algo

btn_col1, btn_col2 = st.sidebar.columns(2)
with btn_col1:
    if st.button("Run Routing", type="primary", use_container_width=True):
        sim.execute_routing(graph, selected_algo, selected_src, selected_dst)
        st.rerun()

with btn_col2:
    if st.button("Reset", use_container_width=True):
        sim.reset_simulation()
        st.rerun()

# Section 3: Network Information
st.sidebar.markdown("---")
st.sidebar.subheader("Network Information")
info_c1, info_c2 = st.sidebar.columns(2)
info_c1.metric("Routers", len(graph.routers))
info_c2.metric("Connections", len(graph.get_edges()))
st.sidebar.caption(f"Topology: **{preset_options.get(st.session_state.get('selected_preset', 'reference'))}**")


# -------------------------------------------------------------
# 4. MAIN PAGE CONTENT & TABS
# -------------------------------------------------------------
st.title("NetRoute — Network Packet Routing")
st.markdown("*Interactive Network Packet Routing Simulator demonstrating BFS, DFS, Traversal Trees, and Next-Hop Forwarding.*")

tab_routing, tab_co3, tab_co4, tab_co5 = st.tabs([
    "Network Routing",
    "CO3: Search & Sort",
    "CO4: Traversal Tree",
    "CO5: Routing Table"
])

# =============================================================
# TAB 1: NETWORK ROUTING
# =============================================================
with tab_routing:
    active_state = sim.get_active_state(graph)
    sim_res = st.session_state.get("sim_res")
    current_step = active_state.get("step")
    is_completed = active_state.get("is_completed", False)

    # Main Network Graph
    fig = build_network_figure(graph, active_state, st.session_state["source_id"], st.session_state["dest_id"], height=440)
    st.plotly_chart(fig, use_container_width=True)

    # Legend
    st.markdown(
        "<div style='text-align:center; font-size:0.85rem; color:#475569; margin-top:-10px; margin-bottom:15px;'>"
        "<span style='color:#10B981;'>●</span> Source &nbsp;|&nbsp; "
        "<span style='color:#F59E0B;'>●</span> Destination &nbsp;|&nbsp; "
        "<span style='color:#7C3AED;'>●</span> Current Router &nbsp;|&nbsp; "
        "<span style='color:#38BDF8;'>●</span> Visited &nbsp;|&nbsp; "
        "<span style='color:#059669;'>●</span> Discovered Route &nbsp;|&nbsp; "
        "<span style='color:#DC2626;'>●</span> Packet"
        "</div>",
        unsafe_allow_html=True
    )

    # Traversal Playback Bar
    ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4, ctrl_c5, ctrl_c6 = st.columns([1, 1, 1, 1, 1.6, 1.2])
    with ctrl_c1:
        if st.button("⏮ First", use_container_width=True):
            sim.first_step()
            st.rerun()
    with ctrl_c2:
        if st.button("◀ Prev", use_container_width=True):
            sim.step_backward()
            st.rerun()
    with ctrl_c3:
        if st.button("Next ▶", use_container_width=True):
            sim.step_forward()
            st.rerun()
    with ctrl_c4:
        if st.button("⏭ Last", use_container_width=True):
            sim.last_step()
            st.rerun()
    with ctrl_c5:
        if st.button("🚀 Transmit Packet", type="primary", use_container_width=True):
            sim.packet_step_forward()
            st.rerun()
    with ctrl_c6:
        if st.button("🔄 Reset Pkt", use_container_width=True):
            sim.reset_packet()
            st.rerun()

    # Step slider if steps exist
    if sim_res and sim_res.get("steps"):
        total_steps = len(sim_res["steps"])
        curr_idx = st.session_state.get("step_idx", 0)
        new_step = st.slider(
            "Traversal Step",
            min_value=1,
            max_value=total_steps,
            value=curr_idx + 1,
            format="Step %d"
        )
        if new_step - 1 != curr_idx:
            sim.jump_to_step(new_step - 1)
            st.rerun()

    # Results & Status Bar
    st.write("")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-card-label">Algorithm</div>'
            f'<div class="metric-card-val" style="font-size:1.1rem; color:#2563EB;">{st.session_state.get("selected_algo")}</div>'
            f'</div>', unsafe_allow_html=True
        )

    with m_col2:
        status_text = "Route Discovered" if sim_res and sim_res.get("success") else ("No Route Found" if sim_res else "Ready")
        status_color = "#10B981" if sim_res and sim_res.get("success") else ("#EF4444" if sim_res else "#475569")
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-card-label">Routing Status</div>'
            f'<div class="metric-card-val" style="font-size:1.1rem; color:{status_color};">{status_text}</div>'
            f'</div>', unsafe_allow_html=True
        )

    with m_col3:
        hops_val = str(sim_res.get("hops", 0)) if sim_res and sim_res.get("success") else "—"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-card-label">Total Hops</div>'
            f'<div class="metric-card-val">{hops_val}</div>'
            f'</div>', unsafe_allow_html=True
        )

    with m_col4:
        visited_count = len(sim_res.get("visited", [])) if sim_res else 0
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-card-label">Routers Visited</div>'
            f'<div class="metric-card-val">{visited_count}</div>'
            f'</div>', unsafe_allow_html=True
        )

    # Discovered Path
    st.write("")
    if sim_res and sim_res.get("success"):
        st.markdown("##### Discovered Route")
        st.markdown(render_path_pills(sim_res.get("path", [])), unsafe_allow_html=True)
    elif sim_res and not sim_res.get("success"):
        st.error(f"Destination router '{st.session_state['dest_id']}' is UNREACHABLE from '{st.session_state['source_id']}' in this topology.")

    # Packet Transmission Status
    if active_state.get("packet_status"):
        st.info(f"**Packet Transmission:** {active_state['packet_status']}")

    # Traversal Log Card
    if current_step:
        st.write("")
        st.markdown("##### Current Traversal State")
        struct_name = "FIFO Queue" if "BFS" in st.session_state.get("selected_algo", "BFS") else "LIFO Stack"
        struct_items = current_step.get("structure", [])
        struct_display = f"{struct_name}: {struct_items}" if struct_items else f"{struct_name}: (empty)"
        desc = current_step.get("description", "")
        op = current_step.get("operation", "STEP")
        step_num = current_step.get("step", 1)

        st.markdown(render_step_card(step_num, f"{op} — {struct_display}", desc), unsafe_allow_html=True)


# =============================================================
# TAB 2: CO3 SEARCH & SORT
# =============================================================
with tab_co3:
    st.markdown("### CO3 — Searching and Sorting Algorithm Evaluation")
    st.caption("Demonstrating Linear Search, Binary Search, Bubble Sort, and Insertion Sort using network router data.")

    # Dataset setup
    dataset_source = sorted(list(graph.routers.keys()))
    if len(dataset_source) < 5:
        dataset_source = ["N1", "N2", "N3", "N4", "N5", "N6", "N7"]

    unsorted_sample = ["N4", "N1", "N7", "N2", "N6", "N3", "N5"]
    sorted_sample = sorted(unsorted_sample)

    co3_subtab1, co3_subtab2 = st.tabs(["Searching Evaluation (Linear vs. Binary)", "Sorting Evaluation (Bubble vs. Insertion)"])

    # --- Subtab 1: Searching ---
    with co3_subtab1:
        st.markdown("#### Searching Evaluation")
        s_c1, s_c2 = st.columns([3, 1])
        with s_c1:
            target_router = st.selectbox("Select Target Router to Search", options=sorted_sample + ["N99"], index=1)
        with s_c2:
            st.write("")
            st.write("")
            run_search_btn = st.button("Execute Search", type="primary", use_container_width=True)

        res_linear = linear_search(unsorted_sample, target_router)
        res_binary = binary_search(sorted_sample, target_router, verify_sorted=True)

        col_lin, col_bin = st.columns(2)
        with col_lin:
            st.markdown("##### Linear Search")
            st.markdown(f"**Input Dataset (Unsorted):** `{unsorted_sample}`")
            st.markdown(f"**Target:** `{target_router}`")
            st.markdown(f"**Status:** {'Found at index ' + str(res_linear['index']) if res_linear['found'] else 'Not Found (-1)'}")
            st.markdown(f"**Comparisons:** `{res_linear['comparisons']}`")
            st.markdown(f"**Theoretical Complexity:** $O(n)$")
            st.markdown(f"**Requires Sorted Data:** No")

        with col_bin:
            st.markdown("##### Binary Search")
            st.markdown(f"**Input Dataset (Sorted):** `{sorted_sample}`")
            st.markdown(f"**Target:** `{target_router}`")
            st.markdown(f"**Status:** {'Found at index ' + str(res_binary['index']) if res_binary['found'] else 'Not Found (-1)'}")
            st.markdown(f"**Comparisons:** `{res_binary['comparisons']}`")
            st.markdown(f"**Theoretical Complexity:** $O(\\log n)$")
            st.markdown(f"**Requires Sorted Data:** Yes (Verified)")

        st.write("")
        st.markdown("##### Complexity Comparison")
        comp_df = pd.DataFrame([
            {"Algorithm": "Linear Search", "Best Case": "O(1)", "Average Case": "O(n)", "Worst Case": "O(n)", "Space": "O(1)", "Condition": "Unsorted or Sorted"},
            {"Algorithm": "Binary Search", "Best Case": "O(1)", "Average Case": "O(log n)", "Worst Case": "O(log n)", "Space": "O(1)", "Condition": "Strictly Sorted"}
        ])
        st.dataframe(comp_df, hide_index=True, use_container_width=True)

    # --- Subtab 2: Sorting ---
    with co3_subtab2:
        st.markdown("#### Sorting Evaluation")
        st.markdown(f"**Unsorted Router Array:** `{unsorted_sample}`")

        res_bubble = bubble_sort(unsorted_sample)
        res_insertion = insertion_sort(unsorted_sample)

        sort_c1, sort_c2 = st.columns(2)
        with sort_c1:
            st.markdown("##### Bubble Sort")
            st.markdown(f"**Sorted Output:** `{res_bubble['sorted_data']}`")
            st.markdown(f"**Comparisons:** `{res_bubble['comparisons']}`")
            st.markdown(f"**Swaps:** `{res_bubble['swaps']}`")
            st.markdown(f"**Passes Completed:** `{res_bubble['passes']}`")
            st.markdown(f"**Correctness:** Verified `{res_bubble['is_correct']}`")
            st.markdown(f"**Theoretical Complexity:** $O(n^2)$")

        with sort_c2:
            st.markdown("##### Insertion Sort")
            st.markdown(f"**Sorted Output:** `{res_insertion['sorted_data']}`")
            st.markdown(f"**Comparisons:** `{res_insertion['comparisons']}`")
            st.markdown(f"**Shifts:** `{res_insertion['shifts']}`")
            st.markdown(f"**Iterations:** `{res_insertion['iterations']}`")
            st.markdown(f"**Correctness:** Verified `{res_insertion['is_correct']}`")
            st.markdown(f"**Theoretical Complexity:** $O(n^2)$")

        st.write("")
        st.markdown("##### Sorting Complexity Reference")
        sort_df = pd.DataFrame([
            {"Algorithm": "Bubble Sort", "Best Case": "O(n)", "Average Case": "O(n²)", "Worst Case": "O(n²)", "Space": "O(1)", "Stable": "Yes"},
            {"Algorithm": "Insertion Sort", "Best Case": "O(n)", "Average Case": "O(n²)", "Worst Case": "O(n²)", "Space": "O(1)", "Stable": "Yes"}
        ])
        st.dataframe(sort_df, hide_index=True, use_container_width=True)


# =============================================================
# TAB 3: CO4 TRAVERSAL TREE
# =============================================================
with tab_co4:
    st.markdown("### CO4 — Routing Traversal Tree Structures")
    st.caption("A Traversal Spanning Tree generated directly from BFS parent relationships.")

    src_node = st.session_state.get("source_id", "N1")
    dst_node = st.session_state.get("dest_id", "N7")

    # Run BFS to obtain true parent pointers
    bfs_res = bfs(graph, src_node, dst_node)
    tree_data = build_traversal_tree(bfs_res.get("parents", {}), src_node, dst_node)

    # Invariants metrics
    inv_c1, inv_c2, inv_c3, inv_c4 = st.columns(4)
    inv_c1.metric("Tree Root", tree_data.get("root", "None"))
    inv_c2.metric("Tree Vertices (V)", tree_data.get("node_count", 0))
    inv_c3.metric("Tree Edges (E = V - 1)", tree_data.get("edge_count", 0))
    inv_c4.metric("Strictly Acyclic", "Yes (0 Cycles)" if tree_data.get("is_acyclic") else "No")

    # Tree Visualization
    fig_tree = build_traversal_tree_figure(tree_data, src_node, dst_node, height=380)
    st.plotly_chart(fig_tree, use_container_width=True)

    # Parent-child table
    st.markdown("##### Traversal Tree Node Hierarchy")
    tree_records = []
    levels = tree_data.get("levels", {})
    parents_map = bfs_res.get("parents", {})
    path_set = set(tree_data.get("path_to_dest", []))

    for node in tree_data.get("nodes", []):
        parent_val = parents_map.get(node)
        tree_records.append({
            "Router": node,
            "Parent Router": parent_val if parent_val else "(Root — No Parent)",
            "Depth Level": levels.get(node, 0),
            "On Path to Destination": "Yes" if node in path_set else "No"
        })

    if tree_records:
        st.dataframe(pd.DataFrame(tree_records), hide_index=True, use_container_width=True)


# =============================================================
# TAB 4: CO5 ROUTING TABLE
# =============================================================
with tab_co5:
    st.markdown("### CO5 — Graph-Based Routing vs. Traditional Routing Table Forwarding")
    st.caption("Demonstrating the difference between on-demand graph search and next-hop forwarding tables.")

    src_fwd = st.session_state.get("source_id", "N1")
    dst_fwd = st.session_state.get("dest_id", "N7")

    st.markdown(f"#### 1. Routing Table for Source Router `{src_fwd}`")
    routing_table = graph.generate_routing_table(src_fwd)
    df_table = pd.DataFrame(routing_table)
    df_table.columns = ["Destination", "Next Hop", "Hop Count", "Status"]
    st.dataframe(df_table, hide_index=True, use_container_width=True)

    st.write("")
    st.markdown(f"#### 2. Hop-by-Hop Table Forwarding Simulation (`{src_fwd}` ➔ `{dst_fwd}`)")

    # Execute genuine table-based forwarding
    table_fwd_res = sim.simulate_table_forwarding(graph, src_fwd, dst_fwd)

    fwd_c1, fwd_c2, fwd_c3 = st.columns(3)
    fwd_c1.metric("Delivery Status", table_fwd_res.get("status", "UNKNOWN"))
    fwd_c2.metric("Forwarding Hops", table_fwd_res.get("hops", 0))
    fwd_c3.metric("Final Router Reached", table_fwd_res.get("final_router", "None"))

    if table_fwd_res.get("success"):
        st.markdown(render_path_pills(table_fwd_res.get("path", [])), unsafe_allow_html=True)
    else:
        st.warning(table_fwd_res.get("message", "Forwarding failed."))

    # Step-by-step table forwarding details
    if table_fwd_res.get("steps"):
        fwd_steps_data = []
        for s in table_fwd_res["steps"]:
            entry = s.get("table_entry", {})
            fwd_steps_data.append({
                "Hop Step": s.get("step"),
                "Current Router": s.get("current_router"),
                "Table Lookup Target": dst_fwd,
                "Next Hop Forwarded": s.get("next_hop"),
                "Metric Hops": entry.get("hops", "—"),
                "Action": s.get("action")
            })
        st.dataframe(pd.DataFrame(fwd_steps_data), hide_index=True, use_container_width=True)

    st.write("")
    st.markdown("#### 3. Architectural Comparison: Graph Routing vs. Table Forwarding")
    comparison_data = [
        {"Dimension": "Routing Paradigm", "Graph-Based Routing (BFS/DFS)": "Centralized on-demand path computation", "Table-Based Forwarding": "Distributed hop-by-hop local lookup"},
        {"Dimension": "Topology Knowledge", "Graph-Based Routing (BFS/DFS)": "Requires complete global graph (V and E)", "Table-Based Forwarding": "Requires only local Next-Hop routing table"},
        {"Dimension": "Per-Hop Complexity", "Graph-Based Routing (BFS/DFS)": "O(V + E) for global graph traversal", "Table-Based Forwarding": "O(1) hash or array lookup per hop"},
        {"Dimension": "Failure Handling", "Graph-Based Routing (BFS/DFS)": "Re-runs full traversal from source", "Table-Based Forwarding": "Reroutes immediately if alternative Next Hop exists"},
        {"Dimension": "Packet Header State", "Graph-Based Routing (BFS/DFS)": "Carries full source route or recomputes", "Table-Based Forwarding": "Carries only Destination IP and TTL"}
    ]
    st.dataframe(pd.DataFrame(comparison_data), hide_index=True, use_container_width=True)
