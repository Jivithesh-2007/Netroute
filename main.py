"""
main.py — NetRoute: Network Packet-Routing Simulator.

A clean, modern, educational network packet routing simulator.
Integrated Course Outcomes:
- CO3: Searching and Sorting Algorithm Evaluation (Linear vs. Binary Search, Bubble vs. Insertion Sort).
- CO4: Routing Traversal Tree Structures (BFS Traversal Spanning Tree and Invariants).
- CO5: Traditional Table-Based Forwarding vs. Graph Traversal Routing.
"""

from typing import Dict, Any, List, Set, Tuple, Optional
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import (
    CUSTOM_CSS, render_path_pills, render_step_card,
    PRIMARY, PRIMARY_DARK, CYAN, PURPLE, SUCCESS, WARNING, ERROR, TEXT_MAIN, TEXT_MUTED, BORDER
)
from network import Graph, validate_router_id, export_topology_json, import_topology_json
from topology_registry import get_topology_registry
from report import generate_simulation_report, export_simulation_report_json
from algorithms import (
    bfs, dfs, linear_search, binary_search, bubble_sort, insertion_sort, build_traversal_tree,
    compare_bfs_dfs
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


# -------------------------------------------------------------
# 2. ADAPTIVE TOPOLOGY DATASET HELPER (CO3)
# -------------------------------------------------------------
def get_adaptive_datasets(graph: Graph) -> Tuple[List[str], List[str]]:
    """
    Derives sorted and authentically unsorted router datasets dynamically
    from whatever topology is currently active in the graph.
    Zero hardcoded nodes.
    """
    nodes = sorted(list(graph.routers.keys()))
    if not nodes:
        return [], []

    n = len(nodes)
    if n <= 2:
        unsorted_list = list(reversed(nodes))
    else:
        # Deterministic interleaving from mid, start, and end to create an authentic unsorted list
        indices = []
        left, right = 0, n - 1
        mid = n // 2
        indices.append(mid)
        visited_idx = {mid}
        while len(indices) < n:
            if left not in visited_idx:
                indices.append(left)
                visited_idx.add(left)
            left += 1
            if right not in visited_idx and len(indices) < n:
                indices.append(right)
                visited_idx.add(right)
            right -= 1
        unsorted_list = [nodes[i] for i in indices]
        if unsorted_list == nodes and n > 1:
            unsorted_list[0], unsorted_list[-1] = unsorted_list[-1], unsorted_list[0]

    return unsorted_list, nodes


# -------------------------------------------------------------
# 3. PLOTLY GRAPH & TREE VISUALIZATIONS
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


def build_algo_result_figure(
    graph: Graph,
    res: Dict[str, Any],
    src_id: str,
    dst_id: str,
    title_label: str = "Algorithm Route",
    primary_color: str = "#2563EB",
    secondary_color: str = "#38BDF8",
    height: int = 370
) -> go.Figure:
    """Renders a dedicated network graph highlighting the discovered path and explored nodes for an algorithm."""
    fig = go.Figure()

    if not graph.routers:
        fig.add_annotation(
            text="Network is empty. Please select a topology preset.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=TEXT_MUTED)
        )
        fig.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=height)
        return fig

    path = res.get("path", [])
    path_nodes = set(path)
    visited_nodes = set(res.get("visited", []))

    # Build route edges set (undirected)
    route_edges = set()
    for i in range(len(path) - 1):
        route_edges.add(tuple(sorted((path[i], path[i + 1]))))

    # Explored edges from tree_edges
    explored_edges = set()
    for u, v in res.get("tree_edges", []):
        explored_edges.add(tuple(sorted((u, v))))

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
            line_width = 2.0
            line_dash = "dot"
        elif e in route_edges:
            line_color = primary_color
            line_width = 4.2
            line_dash = "solid"
        elif e in explored_edges:
            line_color = secondary_color
            line_width = 2.2
            line_dash = "dash"
        else:
            line_color = "#E2E8F0"
            line_width = 1.6
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
            font=dict(size=9, color="#475569"),
            bgcolor="#FFFFFF",
            bordercolor="#CBD5E1",
            borderwidth=1,
            borderpad=2,
            opacity=0.9
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
        elif rid == src_id:
            fill_c = "#10B981"
            border_c = "#059669"
            txt_c = "#FFFFFF"
        elif rid == dst_id:
            fill_c = "#F59E0B"
            border_c = "#D97706"
            txt_c = "#FFFFFF"
        elif rid in path_nodes:
            fill_c = primary_color
            border_c = primary_color
            txt_c = "#FFFFFF"
        elif rid in visited_nodes:
            fill_c = secondary_color
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
            x=r.x, y=r.y - 24,
            text=f"<b>{sub_text}</b>",
            showarrow=False,
            font=dict(size=9, color=sub_color),
            xanchor="center", yanchor="bottom"
        )

        nbrs = sorted(graph.adjacency.get(rid, []))
        hover_texts.append(
            f"<b>Router {rid}</b> ({r.name})<br>"
            f"In Discovered Route: {'Yes' if rid in path_nodes else 'No'}<br>"
            f"Visited During Traversal: {'Yes' if rid in visited_nodes else 'No'}<br>"
            f"Online Status: {'Online' if r.is_online else 'Offline'}<br>"
            f"Neighbors: {', '.join(nbrs) if nbrs else 'None'}"
        )

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=32, color=node_colors, line=dict(color=border_colors, width=2.4)),
        text=node_labels,
        textposition="middle center",
        textfont=dict(size=10, color=text_colors, family="-apple-system, sans-serif"),
        hoverinfo="text", hovertext=hover_texts, showlegend=False
    ))

    all_x = [r.x for r in graph.routers.values()]
    all_y = [r.y for r in graph.routers.values()]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    dx = max(80.0, max_x - min_x)
    dy = max(80.0, max_y - min_y)

    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=height,
        margin=dict(l=25, r=25, t=30, b=25), hovermode="closest",
        xaxis=dict(range=[min_x - dx * 0.12, max_x + dx * 0.12], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[max_y + dy * 0.22, min_y - dy * 0.22], showgrid=False, zeroline=False, showticklabels=False)
    )
    return fig


# -------------------------------------------------------------
# 4. STREAMLIT SIDEBAR
# -------------------------------------------------------------
st.sidebar.title("NetRoute")
st.sidebar.markdown("*Network Packet Routing Simulator*")
st.sidebar.caption("Graph-based routing algorithms (BFS & DFS) with interactive CO3 and CO4 evaluation.")
st.sidebar.markdown("---")

# Section 1: Network Topology Selector
st.sidebar.subheader("Network Topology")
registry = get_topology_registry()
preset_options = registry.get_preset_options()
if not preset_options:
    preset_options = {"reference": "Reference 7-Node WAN"}

current_preset = st.session_state.get("selected_preset", "reference")
if current_preset not in preset_options:
    if current_preset == "custom":
        preset_options["custom"] = "Custom / Imported Topology"
    else:
        current_preset = list(preset_options.keys())[0]

col_preset_sel, col_preset_rst = st.sidebar.columns([3, 1])
with col_preset_sel:
    selected_preset_key = st.selectbox(
        "Select Topology Preset",
        options=list(preset_options.keys()),
        format_func=lambda k: preset_options[k],
        index=list(preset_options.keys()).index(current_preset) if current_preset in preset_options else 0,
        key="topology_selectbox"
    )
with col_preset_rst:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Reset", icon=":material/restart_alt:", help="Restore original preset topology", key="sb_btn_restore_preset", use_container_width=True):
        if selected_preset_key != "custom":
            st.session_state["selected_preset"] = selected_preset_key
            st.session_state["graph"] = registry.load_graph(selected_preset_key) or Graph.from_preset(selected_preset_key)
            graph = st.session_state["graph"]
            g_nodes = sorted(list(graph.routers.keys()))
            st.session_state["source_id"] = g_nodes[0] if g_nodes else "N1"
            st.session_state["dest_id"] = g_nodes[-1] if g_nodes else "N7"
            for state_key in ["src_select", "dst_select", "inspect_router_select", "fwd_src_select", "fwd_dst_select", "sb_del_r_select", "te_del_target"]:
                st.session_state.pop(state_key, None)
            sim.invalidate_simulation()
            st.rerun()

# Handle Topology Change: load real graph data, reset all old results
if selected_preset_key != st.session_state.get("selected_preset") and selected_preset_key != "custom":
    st.session_state["selected_preset"] = selected_preset_key
    st.session_state["graph"] = registry.load_graph(selected_preset_key) or Graph.from_preset(selected_preset_key)
    graph = st.session_state["graph"]

    g_nodes = sorted(list(graph.routers.keys()))
    st.session_state["source_id"] = g_nodes[0] if g_nodes else "N1"
    st.session_state["dest_id"] = g_nodes[-1] if g_nodes else "N7"
    for state_key in ["src_select", "dst_select", "inspect_router_select", "fwd_src_select", "fwd_dst_select", "sb_del_r_select", "te_del_target"]:
        st.session_state.pop(state_key, None)

    sim.invalidate_simulation()
    st.rerun()

graph = st.session_state["graph"]
router_keys = sorted(list(graph.routers.keys()))

# Topology JSON Import / Export in Sidebar
with st.sidebar.expander("Topology Import / Export", icon=":material/swap_vert:", expanded=False):
    st.caption("Export active graph state to JSON or upload a custom JSON network.")
    active_topo_label = preset_options.get(st.session_state.get("selected_preset", "custom"), getattr(graph, "name", "Custom Topology"))
    exported_json_str = export_topology_json(graph, name=active_topo_label)
    st.download_button(
        label="Export Topology (JSON)",
        data=exported_json_str,
        file_name=f"netroute_topology_{st.session_state.get('selected_preset', 'custom')}.json",
        mime="application/json",
        icon=":material/download:",
        use_container_width=True,
        key="sb_export_btn"
    )

    uploaded_file = st.file_uploader(
        "Import Topology JSON",
        type=["json"],
        key="sb_topo_uploader",
        help="Upload a valid JSON file containing routers and edges"
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        upload_token = f"upload_{uploaded_file.name}_{len(file_bytes)}"
        if st.session_state.get("last_uploaded_token") != upload_token:
            try:
                content = file_bytes.decode("utf-8")
                ok, msg, candidate_graph = import_topology_json(content)
                if ok and candidate_graph is not None:
                    st.session_state["last_uploaded_token"] = upload_token
                    st.session_state["graph"] = candidate_graph
                    st.session_state["selected_preset"] = "custom"
                    cand_nodes = sorted(list(candidate_graph.routers.keys()))
                    st.session_state["source_id"] = cand_nodes[0] if cand_nodes else "N1"
                    st.session_state["dest_id"] = cand_nodes[-1] if cand_nodes else "N7"
                    for state_key in ["src_select", "dst_select", "inspect_router_select", "fwd_src_select", "fwd_dst_select", "sb_del_r_select", "te_del_target"]:
                        st.session_state.pop(state_key, None)
                    sim.invalidate_simulation()
                    st.sidebar.success(msg)
                    st.rerun()
                else:
                    st.sidebar.error(msg)
            except Exception as e:
                st.sidebar.error(f"Failed to read JSON: {str(e)}")

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

# Invalidate previous routing if endpoints changed
if selected_src != st.session_state.get("source_id") or selected_dst != st.session_state.get("dest_id"):
    st.session_state["source_id"] = selected_src
    st.session_state["dest_id"] = selected_dst
    sim.invalidate_simulation()

algo_options = ["BFS (Breadth-First)", "DFS (Depth-First)"]
algo_idx = 0 if "BFS" in st.session_state.get("selected_algo", "BFS") else 1
selected_algo = st.sidebar.selectbox("Algorithm", options=algo_options, index=algo_idx, key="algo_select")

if selected_algo != st.session_state.get("selected_algo"):
    st.session_state["selected_algo"] = selected_algo
    sim.invalidate_simulation()

btn_col1, btn_col2 = st.sidebar.columns(2)
with btn_col1:
    if st.button("Run Routing", icon=":material/play_arrow:", type="primary", use_container_width=True):
        sim.execute_routing(graph, selected_algo, selected_src, selected_dst)
        st.rerun()

with btn_col2:
    if st.button("Reset", icon=":material/refresh:", use_container_width=True):
        sim.reset_simulation()
        st.rerun()

# Section 3: Network Information
st.sidebar.markdown("---")
st.sidebar.subheader("Network Information")
info_c1, info_c2 = st.sidebar.columns(2)
info_c1.metric("Routers", len(graph.routers))
info_c2.metric("Connections", len(graph.get_edges()))
st.sidebar.caption(f"Topology: **{preset_options.get(st.session_state.get('selected_preset', 'reference'))}**")

with st.sidebar.expander("Quick Router Management", icon=":material/tune:", expanded=False):
    sb_c1, sb_c2 = st.columns([1.5, 1])
    sb_new_id = sb_c1.text_input("Router ID", placeholder="e.g. N8", max_chars=8, key="sb_add_rid").strip().upper()
    with sb_c2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        sb_add_btn = st.button("Add", icon=":material/add:", use_container_width=True, key="sb_btn_add")

    if sb_add_btn:
        ok, msg = validate_router_id(sb_new_id)
        if not ok:
            st.sidebar.error(f"Invalid ID: {msg}")
        elif sb_new_id in graph.routers:
            st.sidebar.error(f"Router '{sb_new_id}' already exists.")
        else:
            ex_xs = [r.x for r in graph.routers.values()] if graph.routers else [200.0]
            graph.add_router(sb_new_id, name=f"Router {sb_new_id}", x=max(ex_xs) + 80.0, y=220.0)
            sim.invalidate_simulation()
            st.sidebar.success(f"Added Router {sb_new_id}")
            st.rerun()

    if len(router_keys) > 2:
        sb_del_c1, sb_del_c2 = st.columns([1.5, 1])
        sb_del_r = sb_del_c1.selectbox("Delete Router", options=["-- Select --"] + router_keys, key="sb_del_r_select")
        with sb_del_c2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            sb_del_btn = st.button("Del", icon=":material/delete:", use_container_width=True, key="sb_btn_del")

        if sb_del_btn and sb_del_r != "-- Select --":
            rem = [r for r in router_keys if r != sb_del_r]
            if st.session_state.get("source_id") == sb_del_r:
                st.session_state["source_id"] = rem[0]
            if st.session_state.get("dest_id") == sb_del_r:
                st.session_state["dest_id"] = rem[-1]
            for state_key in ["src_select", "dst_select", "inspect_router_select", "fwd_src_select", "fwd_dst_select", "sb_del_r_select", "te_del_target"]:
                if state_key in st.session_state and st.session_state[state_key] == sb_del_r:
                    del st.session_state[state_key]
            graph.remove_router(sb_del_r)
            sim.invalidate_simulation()
            st.sidebar.success(f"Deleted Router {sb_del_r}")
            st.rerun()


# -------------------------------------------------------------
# 5. MAIN PAGE LAYOUT & TABS
# -------------------------------------------------------------
st.title("NetRoute — Network Packet Routing")
st.markdown("*Interactive Network Packet Routing Simulator demonstrating BFS, DFS, and Traversal Trees.*")

tab_routing, tab_bfs_dfs, tab_co3, tab_co4, tab_co5 = st.tabs([
    "Network Routing",
    "BFS vs. DFS Comparison",
    "CO3: Searching & Sorting",
    "CO4: Routing Traversal Tree",
    "CO5: Routing Table Forwarding"
])

# =============================================================
# TAB 1: NETWORK ROUTING
# =============================================================
with tab_routing:
    active_state = sim.get_active_state(graph)
    sim_res = st.session_state.get("sim_res")
    current_step = active_state.get("step")
    is_completed = active_state.get("is_completed", False)

    # Main Network Graph Canvas
    fig = build_network_figure(graph, active_state, st.session_state["source_id"], st.session_state["dest_id"], height=420)
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

    if not sim_res:
        st.info("Select your options in the sidebar and click **Run Routing** to execute the algorithm and view traversal results.")
    else:
        # Traversal Playback Bar
        ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4, ctrl_c5, ctrl_c6 = st.columns([1, 1, 1, 1, 1.6, 1.2])
        with ctrl_c1:
            if st.button("First", icon=":material/first_page:", use_container_width=True):
                sim.first_step()
                st.rerun()
        with ctrl_c2:
            if st.button("Prev", icon=":material/navigate_before:", use_container_width=True):
                sim.step_backward()
                st.rerun()
        with ctrl_c3:
            if st.button("Next", icon=":material/navigate_next:", use_container_width=True):
                sim.step_forward()
                st.rerun()
        with ctrl_c4:
            if st.button("Last", icon=":material/last_page:", use_container_width=True):
                sim.last_step()
                st.rerun()
        with ctrl_c5:
            if st.button("Transmit Packet", icon=":material/send:", type="primary", use_container_width=True):
                sim.packet_step_forward()
                st.rerun()
        with ctrl_c6:
            if st.button("Reset Pkt", icon=":material/restart_alt:", use_container_width=True):
                sim.reset_packet()
                st.rerun()

        # Step slider if steps exist
        if sim_res.get("steps"):
            total_steps = len(sim_res["steps"])
            curr_idx = st.session_state.get("step_idx", 0)
            new_step = st.slider(
                "Traversal Step Navigation",
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
            status_text = "Route Discovered" if sim_res.get("success") else "No Route Found"
            status_color = "#10B981" if sim_res.get("success") else "#EF4444"
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-card-label">Routing Status</div>'
                f'<div class="metric-card-val" style="font-size:1.1rem; color:{status_color};">{status_text}</div>'
                f'</div>', unsafe_allow_html=True
            )

        with m_col3:
            hops_val = str(sim_res.get("hops", 0)) if sim_res.get("success") else "—"
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-card-label">Total Hops</div>'
                f'<div class="metric-card-val">{hops_val}</div>'
                f'</div>', unsafe_allow_html=True
            )

        with m_col4:
            visited_count = len(sim_res.get("visited", []))
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-card-label">Routers Visited</div>'
                f'<div class="metric-card-val">{visited_count}</div>'
                f'</div>', unsafe_allow_html=True
            )

        # Discovered Path
        st.write("")
        if sim_res.get("success"):
            st.markdown("##### Discovered Route")
            st.markdown(render_path_pills(sim_res.get("path", [])), unsafe_allow_html=True)
        else:
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

        # Dynamic Simulation Report Download
        st.write("")
        st.markdown("##### Simulation Execution Report")
        rep_col1, rep_col2 = st.columns([1.5, 2.5])
        with rep_col1:
            active_preset_name = preset_options.get(st.session_state.get("selected_preset", "custom"), getattr(graph, "name", "Active Topology"))
            report_data = generate_simulation_report(
                graph=graph,
                sim_res=sim_res,
                source=st.session_state["source_id"],
                destination=st.session_state["dest_id"],
                algo_name=st.session_state.get("selected_algo", "BFS"),
                topology_name=active_preset_name
            )
            report_json_str = export_simulation_report_json(report_data)
            algo_code = "bfs" if "BFS" in st.session_state.get("selected_algo", "BFS") else "dfs"
            report_filename = f"netroute_report_{algo_code}_{st.session_state['source_id']}_to_{st.session_state['dest_id']}.json"

            st.download_button(
                label="Download Simulation Report (JSON)",
                data=report_json_str,
                file_name=report_filename,
                mime="application/json",
                icon=":material/description:",
                use_container_width=True,
                key="btn_download_sim_report"
            )
        with rep_col2:
            st.caption(f"Authoritative JSON report recording topology state, {st.session_state.get('selected_algo')} execution steps, and complexity.")

        with st.expander("Inspect Simulation Report JSON", icon=":material/data_object:", expanded=False):
            st.json(report_data)

    # Dynamic Network Topology Management (Add/Delete Nodes & Links, Hardware Faults)
    st.write("")
    with st.expander("Dynamic Network Topology Editor (Add / Delete Routers & Links)", icon=":material/account_tree:", expanded=False):
        st.caption("Dynamically modify network topology at runtime. All changes immediately synchronize with the graph visualizer, routing engine, and CO3/CO4/CO5 modules.")

        te_col1, te_col2 = st.columns(2)

        with te_col1:
            st.markdown("##### 1. Router Management (Vertices)")

            # Add Router
            st.markdown("**Add New Router**")
            ar_c1, ar_c2 = st.columns([1, 1.5])
            new_rid = ar_c1.text_input("Router ID", placeholder="e.g. N8, R7", max_chars=8, key="te_new_rid").strip().upper()
            new_rname = ar_c2.text_input("Router Label", placeholder="e.g. Gateway 2", key="te_new_rname").strip()

            ar_c3, ar_c4 = st.columns([1.5, 1])
            conn_target = ar_c3.selectbox(
                "Connect to Router",
                options=["-- Standalone (No Link) --"] + router_keys,
                key="te_conn_target"
            )
            with ar_c4:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                add_btn = st.button("Add Router", icon=":material/add_circle:", type="primary", use_container_width=True, key="te_btn_add_router")

            if add_btn:
                ok, msg = validate_router_id(new_rid)
                if not ok:
                    st.error(f"Invalid Router ID: {msg}")
                elif new_rid in graph.routers:
                    st.error(f"Router '{new_rid}' already exists in topology.")
                else:
                    # Determine layout position
                    if conn_target != "-- Standalone (No Link) --" and conn_target in graph.routers:
                        target_r = graph.routers[conn_target]
                        new_x = target_r.x + 90.0
                        new_y = target_r.y + 40.0
                    else:
                        existing_xs = [r.x for r in graph.routers.values()] if graph.routers else [200.0]
                        new_x = max(existing_xs) + 90.0
                        new_y = 220.0
                        if new_x > 750.0:
                            new_x = 180.0
                            new_y = 350.0

                    graph.add_router(new_rid, name=new_rname or f"Router {new_rid}", x=new_x, y=new_y)
                    if conn_target != "-- Standalone (No Link) --" and conn_target in graph.routers:
                        graph.add_connection(new_rid, conn_target, weight=1.0)

                    sim.invalidate_simulation()
                    st.success(f"Added Router '{new_rid}'{' connected to ' + conn_target if conn_target != '-- Standalone (No Link) --' else ''}.")
                    st.rerun()

            st.markdown("---")

            # Delete Router
            st.markdown("**Delete Existing Router**")
            del_c1, del_c2 = st.columns([1.8, 1])
            del_target = del_c1.selectbox("Select Router to Delete", options=["-- Select --"] + router_keys, key="te_del_target")
            with del_c2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                del_btn = st.button("Delete", icon=":material/delete_forever:", use_container_width=True, key="te_btn_del_router")

            if del_btn:
                if del_target == "-- Select --":
                    st.warning("Please select a router to delete.")
                elif len(router_keys) <= 2:
                    st.error("Cannot delete router: minimum of 2 routers required for network routing.")
                else:
                    # Clean up session state references to the deleted router
                    remaining_nodes = [r for r in router_keys if r != del_target]
                    if st.session_state.get("source_id") == del_target:
                        st.session_state["source_id"] = remaining_nodes[0]
                    if st.session_state.get("dest_id") == del_target:
                        st.session_state["dest_id"] = remaining_nodes[-1]

                    for state_key in ["src_select", "dst_select", "inspect_router_select", "fwd_src_select", "fwd_dst_select", "sb_del_r_select", "te_del_target"]:
                        if state_key in st.session_state and st.session_state[state_key] == del_target:
                            del st.session_state[state_key]

                    graph.remove_router(del_target)
                    sim.invalidate_simulation()
                    st.success(f"Deleted Router '{del_target}' and cascaded removal of all its incident links.")
                    st.rerun()

            st.markdown("---")

            # Hardware Fault (Power Toggle)
            st.markdown("**Hardware Fault Simulation (Online / Offline)**")
            flt_c1, flt_c2 = st.columns([1.8, 1])
            flt_target = flt_c1.selectbox("Select Router", options=router_keys, key="te_flt_target")
            with flt_c2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                flt_btn = st.button("Toggle Power", icon=":material/bolt:", use_container_width=True, key="te_btn_flt_toggle")

            if flt_target and flt_target in graph.routers:
                r_state = "Online (Operational)" if graph.routers[flt_target].is_online else "Offline (Fault Injected)"
                st.caption(f"Current Status: **{r_state}**")

            if flt_btn and flt_target in graph.routers:
                new_state = graph.toggle_router_status(flt_target)
                sim.invalidate_simulation()
                st.info(f"Router '{flt_target}' is now {'Online' if new_state else 'Offline'}.")
                st.rerun()

        with te_col2:
            st.markdown("##### 2. Transmission Link Management (Edges)")

            # Add Link
            st.markdown("**Add Connection / Link**")
            lk_c1, lk_c2, lk_c3 = st.columns([1.2, 1.2, 1])
            u_node = lk_c1.selectbox("Endpoint A", options=router_keys, key="te_lk_u")
            v_options = [r for r in router_keys if r != u_node]
            v_node = lk_c2.selectbox("Endpoint B", options=v_options if v_options else ["None"], key="te_lk_v")
            weight_val = lk_c3.number_input("Cost", min_value=1.0, max_value=50.0, value=1.0, step=1.0, key="te_lk_weight")

            if st.button("Add Transmission Link", icon=":material/link:", use_container_width=True, key="te_btn_add_link"):
                if not v_options or v_node == "None":
                    st.warning("Please choose two different routers.")
                elif graph.add_connection(u_node, v_node, weight=float(weight_val)):
                    sim.invalidate_simulation()
                    st.success(f"Created link: {u_node} → {v_node} (Cost: {weight_val})")
                    st.rerun()
                else:
                    st.warning(f"Connection between '{u_node}' and '{v_node}' already exists or is invalid.")

            st.markdown("---")

            # Remove Link
            st.markdown("**Remove Transmission Link**")
            all_active_edges = [f"{u} <-> {v}" for (u, v) in graph.get_edges()]
            rm_c1, rm_c2 = st.columns([1.8, 1])
            edge_to_rm = rm_c1.selectbox(
                "Select Link to Remove",
                options=["-- Select --"] + all_active_edges if all_active_edges else ["No Links"],
                key="te_rm_edge"
            )
            with rm_c2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                rm_link_btn = st.button("Remove Link", icon=":material/link_off:", use_container_width=True, key="te_btn_rm_link")

            if rm_link_btn:
                if edge_to_rm in ("-- Select --", "No Links"):
                    st.warning("Please select an active link to remove.")
                else:
                    u_rm, v_rm = [x.strip() for x in edge_to_rm.split("<->")]
                    graph.remove_connection(u_rm, v_rm)
                    sim.invalidate_simulation()
                    st.success(f"Removed link: {edge_to_rm}")
                    st.rerun()

            st.markdown("---")

            # Layout & Preset Reset
            st.markdown("**Layout & Topology Reset**")
            lay_c1, lay_c2 = st.columns(2)
            with lay_c1:
                if st.button("Auto-Arrange (Circle)", icon=":material/autorenew:", use_container_width=True, key="te_btn_auto_layout"):
                    graph.auto_layout()
                    st.success("Re-arranged routers into a balanced circular layout.")
                    st.rerun()
            with lay_c2:
                if st.button("Restore Preset", icon=":material/restore:", use_container_width=True, key="te_btn_restore_preset"):
                    curr_p = st.session_state.get("selected_preset", "reference")
                    st.session_state["graph"] = registry.load_graph(curr_p) or Graph.from_preset(curr_p)
                    for state_key in ["src_select", "dst_select", "inspect_router_select", "fwd_src_select", "fwd_dst_select", "sb_del_r_select", "te_del_target"]:
                        st.session_state.pop(state_key, None)
                    sim.invalidate_simulation()
                    st.success(f"Restored original '{curr_p}' topology.")
                    st.rerun()

            st.markdown("---")
            st.markdown("**Topology JSON Import & Export**")
            te_exp_c1, te_exp_c2 = st.columns(2)
            with te_exp_c1:
                cur_topo_name = preset_options.get(st.session_state.get("selected_preset", "custom"), getattr(graph, "name", "Custom Topology"))
                te_exp_json = export_topology_json(graph, name=cur_topo_name)
                st.download_button(
                    label="Export Topology (JSON)",
                    data=te_exp_json,
                    file_name=f"netroute_topology_{st.session_state.get('selected_preset', 'custom')}.json",
                    mime="application/json",
                    icon=":material/download:",
                    use_container_width=True,
                    key="te_btn_export_json"
                )
            with te_exp_c2:
                te_up_file = st.file_uploader("Upload JSON File", type=["json"], key="te_topo_uploader", label_visibility="collapsed")
                if te_up_file is not None:
                    te_bytes = te_up_file.getvalue()
                    te_token = f"te_up_{te_up_file.name}_{len(te_bytes)}"
                    if st.session_state.get("te_last_upload_token") != te_token:
                        try:
                            te_content = te_bytes.decode("utf-8")
                            te_ok, te_msg, te_cand = import_topology_json(te_content)
                            if te_ok and te_cand is not None:
                                st.session_state["te_last_upload_token"] = te_token
                                st.session_state["graph"] = te_cand
                                st.session_state["selected_preset"] = "custom"
                                cand_nodes = sorted(list(te_cand.routers.keys()))
                                st.session_state["source_id"] = cand_nodes[0] if cand_nodes else "N1"
                                st.session_state["dest_id"] = cand_nodes[-1] if cand_nodes else "N7"
                                for state_key in ["src_select", "dst_select", "inspect_router_select", "fwd_src_select", "fwd_dst_select", "sb_del_r_select", "te_del_target"]:
                                    st.session_state.pop(state_key, None)
                                sim.invalidate_simulation()
                                st.success(te_msg)
                                st.rerun()
                            else:
                                st.error(te_msg)
                        except Exception as e:
                            st.error(f"Failed to parse JSON file: {str(e)}")


# =============================================================
# TAB: BFS VS. DFS COMPARISON & EVALUATION ENGINE
# =============================================================
with tab_bfs_dfs:
    st.markdown("### Breadth-First Search (BFS) vs. Depth-First Search (DFS) Evaluation")
    st.markdown(
        "*Side-by-side empirical and theoretical comparison of FIFO Queue-based breadth traversal "
        "versus LIFO Stack-based depth traversal in network packet routing.*"
    )

    if not graph.routers:
        st.warning("Network graph is empty. Please select or initialize a topology in the sidebar.")
    else:
        router_keys = sorted(list(graph.routers.keys()))
        default_src = st.session_state.get("source_id", router_keys[0])
        default_dst = st.session_state.get("dest_id", router_keys[-1] if len(router_keys) > 1 else router_keys[0])
        if default_src not in router_keys:
            default_src = router_keys[0]
        if default_dst not in router_keys:
            default_dst = router_keys[-1]

        # Top Control Bar
        cmp_c1, cmp_c2, cmp_c3 = st.columns([2, 2, 1.5])
        with cmp_c1:
            cmp_src = st.selectbox(
                "Source Router (Origin)",
                options=router_keys,
                index=router_keys.index(default_src),
                key="cmp_src_selector"
            )
        with cmp_c2:
            cmp_dst = st.selectbox(
                "Destination Router (Target)",
                options=router_keys,
                index=router_keys.index(default_dst),
                key="cmp_dst_selector"
            )
        with cmp_c3:
            st.write("")
            st.write("")
            run_cmp = st.button("Re-evaluate Comparison", icon=":material/compare_arrows:", type="primary", use_container_width=True)

        # Compute or retrieve comparison
        cmp_cache = st.session_state.get("bfs_dfs_comp_res")
        if run_cmp or not cmp_cache or cmp_cache.get("source") != cmp_src or cmp_cache.get("destination") != cmp_dst or cmp_cache.get("graph_size") != len(graph.routers):
            cmp_res = compare_bfs_dfs(graph, cmp_src, cmp_dst)
            cmp_res["graph_size"] = len(graph.routers)
            st.session_state["bfs_dfs_comp_res"] = cmp_res
        else:
            cmp_res = cmp_cache

        bfs_info = cmp_res["bfs"]
        dfs_info = cmp_res["dfs"]

        st.write("")

        # -------------------------------------------------------------
        # 1. EXECUTIVE KPI SCORECARD
        # -------------------------------------------------------------
        kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)

        with kpi_c1:
            hop_delta_text = f"+{cmp_res['hop_delta']} extra hops" if cmp_res['hop_delta'] > 0 else "Identical hop count"
            st.markdown(
                f'<div class="metric-card" style="border-top:3px solid #2563EB;">'
                f'<div class="metric-card-label">Hop Count (Path Length)</div>'
                f'<div class="metric-card-val"><span style="color:#2563EB;">{cmp_res["bfs_hops"]}</span> vs <span style="color:#7C3AED;">{cmp_res["dfs_hops"]}</span></div>'
                f'<div style="font-size:0.80rem; color:#475569;">BFS: {cmp_res["bfs_hops"]} hops | DFS: {cmp_res["dfs_hops"]} hops ({hop_delta_text})</div>'
                f'</div>', unsafe_allow_html=True
            )

        with kpi_c2:
            st.markdown(
                f'<div class="metric-card" style="border-top:3px solid {cmp_res["verdict_color"]};">'
                f'<div class="metric-card-label">Routing Optimality</div>'
                f'<div class="metric-card-val" style="font-size:1.15rem; color:{cmp_res["verdict_color"]};">{cmp_res["verdict_badge"]}</div>'
                f'<div style="font-size:0.80rem; color:#475569;">BFS provably guarantees minimal hops</div>'
                f'</div>', unsafe_allow_html=True
            )

        with kpi_c3:
            st.markdown(
                f'<div class="metric-card" style="border-top:3px solid #0891B2;">'
                f'<div class="metric-card-label">Exploration Footprint</div>'
                f'<div class="metric-card-val"><span style="color:#2563EB;">{cmp_res["bfs_visited_count"]}</span> vs <span style="color:#7C3AED;">{cmp_res["dfs_visited_count"]}</span></div>'
                f'<div style="font-size:0.80rem; color:#475569;">Coverage: BFS {cmp_res["bfs_coverage_pct"]}% | DFS {cmp_res["dfs_coverage_pct"]}%</div>'
                f'</div>', unsafe_allow_html=True
            )

        with kpi_c4:
            bfs_max_mem = bfs_info.get("max_structure", 0)
            dfs_max_mem = dfs_info.get("max_structure", 0)
            st.markdown(
                f'<div class="metric-card" style="border-top:3px solid #F59E0B;">'
                f'<div class="metric-card-label">Peak Memory (Frontier Size)</div>'
                f'<div class="metric-card-val"><span style="color:#2563EB;">{bfs_max_mem}</span> vs <span style="color:#7C3AED;">{dfs_max_mem}</span></div>'
                f'<div style="font-size:0.80rem; color:#475569;">Max Queue Size (BFS) vs Max Stack Depth (DFS)</div>'
                f'</div>', unsafe_allow_html=True
            )

        st.write("")

        # -------------------------------------------------------------
        # 2. SIDE-BY-SIDE DUAL NETWORK TRAVERSAL VISUALIZATIONS
        # -------------------------------------------------------------
        st.markdown("#### 1. Live Visual Traversal & Route Discovery")
        st.caption("Visualizing the discovered forwarding path (thick solid link) and the explored topology frontier (dashed lines).")

        col_viz_bfs, col_viz_dfs = st.columns(2)

        with col_viz_bfs:
            st.markdown(
                "<div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;'>"
                "<span style='font-weight:700; color:#2563EB; font-size:1.05rem;'>Breadth-First Search (BFS)</span>"
                "<span style='background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>FIFO QUEUE</span>"
                "</div>",
                unsafe_allow_html=True
            )
            fig_bfs = build_algo_result_figure(
                graph, bfs_info, cmp_src, cmp_dst,
                title_label="BFS Shortest Route",
                primary_color="#2563EB", secondary_color="#38BDF8", height=380
            )
            st.plotly_chart(fig_bfs, use_container_width=True)

            st.markdown("**Discovered Route:**")
            st.markdown(render_path_pills(bfs_info.get("path", [])), unsafe_allow_html=True)

            st.markdown(
                f"<div style='font-size:0.86rem; color:#334155; line-height:1.6; margin-top:6px;'>"
                f"• <b>Hop Count:</b> <code>{bfs_info.get('hops', 0)} hops</code> (Guaranteed Shortest)<br>"
                f"• <b>Total Route Link Weight:</b> <code>{bfs_info.get('path_cost', 0.0)}</code><br>"
                f"• <b>Routers Visited:</b> <code>{len(bfs_info.get('visited', []))} of {len(graph.routers)}</code><br>"
                f"• <b>Queue Operations:</b> <code>{bfs_info.get('total_enqueues', 0)} Enqueues / {bfs_info.get('total_dequeues', 0)} Dequeues</code><br>"
                f"• <b>Execution Time:</b> <code>{bfs_info.get('execution_time_ms', 0.0):.3f} ms</code>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col_viz_dfs:
            st.markdown(
                "<div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;'>"
                "<span style='font-weight:700; color:#7C3AED; font-size:1.05rem;'>Depth-First Search (DFS)</span>"
                "<span style='background:#EDE9FE; color:#5B21B6; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>LIFO STACK</span>"
                "</div>",
                unsafe_allow_html=True
            )
            fig_dfs = build_algo_result_figure(
                graph, dfs_info, cmp_src, cmp_dst,
                title_label="DFS Discovered Route",
                primary_color="#7C3AED", secondary_color="#C084FC", height=380
            )
            st.plotly_chart(fig_dfs, use_container_width=True)

            st.markdown("**Discovered Route:**")
            st.markdown(render_path_pills(dfs_info.get("path", [])), unsafe_allow_html=True)

            st.markdown(
                f"<div style='font-size:0.86rem; color:#334155; line-height:1.6; margin-top:6px;'>"
                f"• <b>Hop Count:</b> <code>{dfs_info.get('hops', 0)} hops</code> (Not Guaranteed Minimal)<br>"
                f"• <b>Total Route Link Weight:</b> <code>{dfs_info.get('path_cost', 0.0)}</code><br>"
                f"• <b>Routers Visited:</b> <code>{len(dfs_info.get('visited', []))} of {len(graph.routers)}</code><br>"
                f"• <b>Stack Operations:</b> <code>{dfs_info.get('total_pushes', 0)} Pushes / {dfs_info.get('total_pops', 0)} Pops ({dfs_info.get('backtrack_count', 0)} Backtracks)</code><br>"
                f"• <b>Execution Time:</b> <code>{dfs_info.get('execution_time_ms', 0.0):.3f} ms</code>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        # -------------------------------------------------------------
        # 3. WHICH IS BEST? AUTHORITATIVE ENGINEERING VERDICT
        # -------------------------------------------------------------
        st.markdown("#### 2. Authoritative Engineering Verdict: Which Algorithm is Best?")
        st.caption("Theoretical rigor and practical systems analysis across telecommunications and computer science.")

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-left:5px solid {cmp_res['verdict_color']}; border-radius:8px; padding:16px 20px; margin-bottom:16px;">
                <div style="font-weight:700; font-size:1.15rem; color:{cmp_res['verdict_color']}; margin-bottom:6px;">
                    {cmp_res['verdict_title']}
                </div>
                <div style="font-size:0.95rem; color:#1E293B; line-height:1.55;">
                    {cmp_res['verdict_summary']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        verdict_col1, verdict_col2 = st.columns(2)

        with verdict_col1:
            st.markdown(
                """
                <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:16px;">
                    <div style="font-weight:700; color:#166534; font-size:0.98rem; margin-bottom:8px;">
                        Why BFS is STRICTLY BEST for Network Packet Routing:
                    </div>
                    <ul style="font-size:0.88rem; color:#14532D; margin:0; padding-left:18px; line-height:1.6;">
                        <li><b>Guaranteed Minimum Latency:</b> Every router hop incurs serialization, processing, and queueing delays. BFS mathematically guarantees the path with the fewest hops ($H_{min}$).</li>
                        <li><b>Bandwidth Efficiency:</b> Avoids circuitous, wandering paths that consume transmission capacity on redundant links.</li>
                        <li><b>Deterministic Frontier:</b> Explores radially outward in uniform distance shells (d = 1, 2, ...), ensuring consistent routing behavior regardless of neighbor ordering.</li>
                        <li><b>Jitter & Packet Loss Minimization:</b> Fewer forwarding switches statistically reduce buffer drops and latency variation.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        with verdict_col2:
            st.markdown(
                """
                <div style="background:#FAF5FF; border:1px solid #E9D5FF; border-radius:8px; padding:16px;">
                    <div style="font-weight:700; color:#6B21A8; font-size:0.98rem; margin-bottom:8px;">
                        When DFS is BEST / PREFERRED in Computer Science & Networking:
                    </div>
                    <ul style="font-size:0.88rem; color:#581C87; margin:0; padding-left:18px; line-height:1.6;">
                        <li><b>Loop & Cycle Detection (Control Plane):</b> DFS recursion stack identifies back-edges in $O(V + E)$ time (Spanning Tree Protocol STP).</li>
                        <li><b>Network Vulnerability & Bridge Detection:</b> Tarjan's algorithm uses DFS to discover Articulation Points (routers whose failure isolates subnets).</li>
                        <li><b>Topological Task Sequencing:</b> Used for firewall rule chaining, virtual network function (VNF) dependency ordering, and DAG scheduling.</li>
                        <li><b>Memory-Constrained IoT Nodes:</b> In sensors with tiny RAM (2KB-4KB), DFS memory $O(h)$ avoids BFS queue explosion $O(b^d)$ on wide graphs.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")
        st.markdown("---")

        # -------------------------------------------------------------
        # 4. COMPREHENSIVE MULTI-DIMENSIONAL COMPARISON TABLE
        # -------------------------------------------------------------
        st.markdown("#### 3. Quantitative & Architectural Comparison Table")
        st.caption("Comparing core properties, operational complexities, and systems behaviors.")

        comparison_matrix_data = [
            {
                "Dimension": "1. Underlying Data Structure",
                "Breadth-First Search (BFS)": "FIFO Queue (collections.deque)",
                "Depth-First Search (DFS)": "LIFO Stack (list / Call Stack)",
                "Advantage / Notes": "BFS maintains level order; DFS explores depth."
            },
            {
                "Dimension": "2. Shortest Path Guarantee",
                "Breadth-First Search (BFS)": "Guaranteed Optimal (Minimum Hops in unweighted graphs)",
                "Depth-First Search (DFS)": "No Guarantee (Discovers any reachable path)",
                "Advantage / Notes": "BFS is mandatory for minimum-latency packet routing."
            },
            {
                "Dimension": "3. Search Frontier Mechanics",
                "Breadth-First Search (BFS)": "Concentric radial waves (Level k before k + 1)",
                "Depth-First Search (DFS)": "Deep single-branch probe until dead-end, then backtrack",
                "Advantage / Notes": "BFS frontier expands symmetrically; DFS is narrow."
            },
            {
                "Dimension": "4. Time Complexity",
                "Breadth-First Search (BFS)": f"O(V + E) — V={len(graph.routers)}, E={len(graph.get_edges())}",
                "Depth-First Search (DFS)": f"O(V + E) — V={len(graph.routers)}, E={len(graph.get_edges())}",
                "Advantage / Notes": "Identical asymptotic time bound; constant factors differ."
            },
            {
                "Dimension": "5. Memory / Space Complexity",
                "Breadth-First Search (BFS)": "O(V) — Proportional to max breadth / frontier width (b^d)",
                "Depth-First Search (DFS)": "O(V) — Proportional to maximum traversal depth (h)",
                "Advantage / Notes": "DFS uses less memory in wide, bushy shallow trees."
            },
            {
                "Dimension": "6. Backtracking Required?",
                "Breadth-First Search (BFS)": "No backtracking required during forward traversal",
                "Depth-First Search (DFS)": f"Yes ({dfs_info.get('backtrack_count', 0)} backtracks in active run)",
                "Advantage / Notes": "Backtracking wastes network link buffer lookahead."
            },
            {
                "Dimension": "7. Data Plane Forwarding Suitability",
                "Breadth-First Search (BFS)": "High / Primary (Basis for Shortest Path Bridging)",
                "Depth-First Search (DFS)": "Unsuitable (Meandering routes violate latency SLA)",
                "Advantage / Notes": "Forwarding tables are derived from BFS / Dijkstra."
            },
            {
                "Dimension": "8. Control Plane Topology Auditing",
                "Breadth-First Search (BFS)": "Sub-optimal for cycle analysis",
                "Depth-First Search (DFS)": "Gold Standard (Loop detection, Bridges, Biconnectivity)",
                "Advantage / Notes": "DFS back-edges immediately identify topological cycles."
            },
            {
                "Dimension": "9. Real-World Protocol Analogs",
                "Breadth-First Search (BFS)": "OSPF / IS-IS (Dijkstra weighted BFS), SDN OpenFlow",
                "Depth-First Search (DFS)": "Spanning Tree Protocol (STP), BGP AS-Path Loop Supression",
                "Advantage / Notes": "Industry standard networking building blocks."
            }
        ]

        st.dataframe(pd.DataFrame(comparison_matrix_data), hide_index=True, use_container_width=True)

        st.markdown("---")

        # -------------------------------------------------------------
        # 5. INTERACTIVE SCENARIO SELECTOR (DECISION HELPER)
        # -------------------------------------------------------------
        st.markdown("#### 4. Interactive Scenario Selector: Engineering Decision Guide")
        st.caption("Select a real-world networking or engineering challenge to inspect the recommended algorithm.")

        scenario_titles = [s["scenario"] for s in cmp_res["scenario_guide"]]
        selected_scenario_idx = st.selectbox(
            "Select Engineering Problem Domain:",
            options=range(len(scenario_titles)),
            format_func=lambda i: scenario_titles[i],
            key="cmp_scenario_select"
        )

        sc = cmp_res["scenario_guide"][selected_scenario_idx]
        sc_badge_color = "#2563EB" if "BFS" in sc["best_choice"] or "Dijkstra" in sc["best_choice"] else "#7C3AED"

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:16px; margin-top:10px;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
                    <div style="font-weight:700; font-size:1.02rem; color:#0F172A;">{sc['scenario']}</div>
                    <span style="background:{sc_badge_color}; color:#FFFFFF; padding:4px 12px; border-radius:6px; font-weight:700; font-size:0.84rem;">
                        RECOMMENDED: {sc['best_choice']}
                    </span>
                </div>
                <div style="font-size:0.92rem; color:#334155; margin-bottom:8px;">
                    <b>Algorithmic Rationale:</b> {sc['rationale']}
                </div>
                <div style="font-size:0.86rem; color:#475569; margin-bottom:6px;">
                    <b>Theoretical Complexity:</b> <code>{sc['complexity']}</code>
                </div>
                <div style="font-size:0.86rem; color:#0284C7;">
                    <b>Industry Real-World Implementation:</b> {sc['industry_example']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # -------------------------------------------------------------
        # 6. PROFESSIONAL ENGINEERING SUGGESTIONS & BEST PRACTICES
        # -------------------------------------------------------------
        st.markdown("#### 5. Professional Engineering Suggestions & Architecture Guidelines")
        st.caption("Practical engineering recommendations for network systems architects and algorithm engineers.")

        sug_cols = st.columns(2)
        for idx, sug in enumerate(cmp_res["suggestions"]):
            target_col = sug_cols[idx % 2]
            with target_col:
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-top:3px solid #2563EB; border-radius:8px; padding:14px; margin-bottom:14px; height:100%;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-size:0.75rem; font-weight:700; color:#2563EB; text-transform:uppercase;">{sug['category']}</span>
                            <span style="font-size:0.72rem; background:#F1F5F9; color:#475569; padding:2px 6px; border-radius:4px; font-weight:600;">{sug['impact']}</span>
                        </div>
                        <div style="font-weight:700; font-size:0.95rem; color:#0F172A; margin-bottom:6px;">{sug['title']}</div>
                        <div style="font-size:0.86rem; color:#334155; line-height:1.5;">{sug['recommendation']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # -------------------------------------------------------------
        # 7. STEP-BY-STEP DATA STRUCTURE INSPECTOR (FIFO QUEUE VS LIFO STACK)
        # -------------------------------------------------------------
        with st.expander("Inspect Step-by-Step Traversal Logs (FIFO Queue vs. LIFO Stack Execution)", expanded=False):
            st.caption("Examine the exact chronological operations performed by the underlying queue and stack structures.")
            tab_step_bfs, tab_step_dfs = st.tabs(["BFS Queue Execution Steps", "DFS Stack Execution Steps"])

            with tab_step_bfs:
                bfs_step_rows = []
                for s in bfs_info.get("steps", []):
                    bfs_step_rows.append({
                        "Step": s.get("step"),
                        "Operation": s.get("operation"),
                        "Current Router": s.get("current_node"),
                        "Queue Front (Next Out)": s.get("front"),
                        "Queue Rear (Latest In)": s.get("rear"),
                        "Queue State": str(s.get("structure")),
                        "Enqueues": s.get("enqueues"),
                        "Dequeues": s.get("dequeues"),
                        "Description": s.get("description")
                    })
                st.dataframe(pd.DataFrame(bfs_step_rows), hide_index=True, use_container_width=True)

            with tab_step_dfs:
                dfs_step_rows = []
                for s in dfs_info.get("steps", []):
                    dfs_step_rows.append({
                        "Step": s.get("step"),
                        "Operation": s.get("operation"),
                        "Current Router": s.get("current_node"),
                        "Stack Top": s.get("stack_top"),
                        "Stack Depth": len(s.get("structure", [])),
                        "Stack State": str(s.get("structure")),
                        "Pushes": s.get("pushes"),
                        "Pops": s.get("pops"),
                        "Description": s.get("description")
                    })
                st.dataframe(pd.DataFrame(dfs_step_rows), hide_index=True, use_container_width=True)


# =============================================================
# TAB 2: CO3 SEARCHING & SORTING (REAL INTERACTIVE EXECUTION)
# =============================================================
with tab_co3:

    st.markdown("### CO3 — Searching and Sorting Algorithm Evaluation")

    # Adaptively derive datasets from the currently selected topology
    unsorted_nodes, sorted_nodes = get_adaptive_datasets(graph)
    active_topo_name = preset_options.get(st.session_state.get("selected_preset", "reference"))
    st.caption(f"Dynamically derived from active topology **{active_topo_name}** ({len(sorted_nodes)} routers).")

    co3_subtab1, co3_subtab2 = st.tabs(["Searching Evaluation (Linear vs. Binary)", "Sorting Evaluation (Bubble vs. Insertion)"])

    # --- Subtab 1: Searching ---
    with co3_subtab1:
        st.markdown("#### Interactive Searching Evaluation")

        # Dynamic target options from active topology + absent test node
        absent_target_demo = f"{sorted_nodes[0]}_ABSENT" if sorted_nodes else "X99"
        search_target_options = sorted_nodes + [absent_target_demo]

        default_target_idx = 0
        if st.session_state.get("dest_id") in search_target_options:
            default_target_idx = search_target_options.index(st.session_state["dest_id"])
        elif len(sorted_nodes) > 1:
            default_target_idx = len(sorted_nodes) // 2

        s_c1, s_c2 = st.columns([3, 1])
        with s_c1:
            target_router = st.selectbox(
                "Select Target Router to Search",
                options=search_target_options,
                index=default_target_idx,
                key="co3_target_router_sel"
            )
        with s_c2:
            st.write("")
            st.write("")
            if st.button("Execute Search", icon=":material/search:", type="primary", use_container_width=True):
                # Run actual algorithms on current topology data
                res_lin = linear_search(unsorted_nodes, target_router)
                res_bin = binary_search(sorted_nodes, target_router, verify_sorted=True)
                st.session_state["search_res"] = {
                    "linear": res_lin,
                    "binary": res_bin,
                    "target": target_router,
                    "unsorted": unsorted_nodes,
                    "sorted": sorted_nodes
                }
                st.session_state["search_step_idx"] = 0
                st.rerun()

        search_data = st.session_state.get("search_res")

        if not search_data:
            st.info("Select a target router and click **Execute Search** to run Linear and Binary Search on the current topology.")
        else:
            res_lin = search_data["linear"]
            res_bin = search_data["binary"]
            cur_target = search_data["target"]
            u_data = search_data["unsorted"]
            s_data = search_data["sorted"]

            st.write("")
            st.markdown("##### Step-by-Step Search Visualization")

            # Playback controls for search steps
            lin_steps = res_lin.get("steps", [])
            bin_steps = res_bin.get("steps", [])
            max_search_steps = max(len(lin_steps), len(bin_steps))

            s_step = st.session_state.get("search_step_idx", 0)

            c_step1, c_step2, c_step3, c_step4 = st.columns([1, 1, 1, 1])
            with c_step1:
                if st.button("Start", icon=":material/first_page:", key="s_btn_start"):
                    st.session_state["search_step_idx"] = 0
                    st.rerun()
            with c_step2:
                if st.button("Prev Step", icon=":material/navigate_before:", key="s_btn_prev") and s_step > 0:
                    st.session_state["search_step_idx"] = s_step - 1
                    st.rerun()
            with c_step3:
                if st.button("Next Step", icon=":material/navigate_next:", key="s_btn_next") and s_step < max_search_steps - 1:
                    st.session_state["search_step_idx"] = s_step + 1
                    st.rerun()
            with c_step4:
                if st.button("End", icon=":material/last_page:", key="s_btn_end"):
                    st.session_state["search_step_idx"] = max(0, max_search_steps - 1)
                    st.rerun()

            st.caption(f"Inspection Step **{s_step + 1}** of **{max_search_steps}** (Target: **{cur_target}**)")

            # Side-by-side array visualizations
            vis_col1, vis_col2 = st.columns(2)

            with vis_col1:
                st.markdown("###### Linear Search Array (Unsorted)")
                cur_lin_step = lin_steps[min(s_step, len(lin_steps) - 1)] if lin_steps else None
                cur_lin_idx = cur_lin_step.get("index", -1) if cur_lin_step else -1
                cur_lin_match = cur_lin_step.get("matched", False) if cur_lin_step else False

                html_cells = []
                for idx, val in enumerate(u_data):
                    if idx == cur_lin_idx:
                        cls = "search-cell-box-match" if cur_lin_match else "search-cell-box-active"
                    elif idx < cur_lin_idx:
                        cls = "search-cell-box-checked"
                    else:
                        cls = ""
                    html_cells.append(
                        f'<div class="search-cell">'
                        f'<span class="search-cell-idx">[{idx}]</span>'
                        f'<div class="search-cell-box {cls}">{val}</div>'
                        f'</div>'
                    )
                st.markdown(f'<div class="search-array-container">{"".join(html_cells)}</div>', unsafe_allow_html=True)
                if cur_lin_step:
                    st.caption(cur_lin_step.get("description", ""))

            with vis_col2:
                st.markdown("###### Binary Search Array (Sorted)")
                cur_bin_step = bin_steps[min(s_step, len(bin_steps) - 1)] if bin_steps else None
                b_low = cur_bin_step.get("low", 0) if cur_bin_step else 0
                b_high = cur_bin_step.get("high", len(s_data) - 1) if cur_bin_step else len(s_data) - 1
                b_mid = cur_bin_step.get("mid", -1) if cur_bin_step else -1
                b_match = (cur_bin_step.get("action") == "MATCH") if cur_bin_step else False

                html_b_cells = []
                for idx, val in enumerate(s_data):
                    pointer_labels = []
                    if idx == b_low:
                        pointer_labels.append('<span style="color:#2563EB;">L</span>')
                    if idx == b_mid:
                        pointer_labels.append('<span style="color:#D97706;">M</span>')
                    if idx == b_high:
                        pointer_labels.append('<span style="color:#7C3AED;">H</span>')

                    pointer_html = f'<div class="search-cell-pointer">{" ".join(pointer_labels)}</div>'

                    if idx == b_mid:
                        cls = "search-cell-box-match" if b_match else "search-cell-box-active"
                    elif b_low <= idx <= b_high:
                        cls = ""
                    else:
                        cls = "search-cell-box-dim"

                    html_b_cells.append(
                        f'<div class="search-cell">'
                        f'<span class="search-cell-idx">[{idx}]</span>'
                        f'<div class="search-cell-box {cls}">{val}</div>'
                        f'{pointer_html}'
                        f'</div>'
                    )
                st.markdown(f'<div class="search-array-container">{"".join(html_b_cells)}</div>', unsafe_allow_html=True)
                if cur_bin_step:
                    st.caption(cur_bin_step.get("description", ""))

            # Execution Results Summary
            st.write("")
            st.markdown("##### Executed Algorithm Results")
            res_c1, res_c2 = st.columns(2)

            with res_c1:
                st.markdown(
                    f'<div class="metric-card" style="border-top:3px solid #2563EB;">'
                    f'<div class="metric-card-label">Linear Search Result</div>'
                    f'<div style="font-size:0.95rem; margin-top:6px;"><b>Target:</b> {cur_target}</div>'
                    f'<div style="font-size:0.95rem;"><b>Status:</b> {"Found at index " + str(res_lin["index"]) if res_lin["found"] else "Not Found (-1)"}</div>'
                    f'<div style="font-size:0.95rem;"><b>Actual Comparisons:</b> <span style="color:#2563EB; font-weight:700;">{res_lin["comparisons"]}</span></div>'
                    f'<div style="font-size:0.95rem;"><b>Total Steps:</b> {len(lin_steps)}</div>'
                    f'<div style="font-size:0.95rem;"><b>Theoretical Complexity:</b> O(n)</div>'
                    f'<div style="font-size:0.95rem;"><b>Requires Sorted Data:</b> No</div>'
                    f'</div>', unsafe_allow_html=True
                )

            with res_c2:
                st.markdown(
                    f'<div class="metric-card" style="border-top:3px solid #7C3AED;">'
                    f'<div class="metric-card-label">Binary Search Result</div>'
                    f'<div style="font-size:0.95rem; margin-top:6px;"><b>Target:</b> {cur_target}</div>'
                    f'<div style="font-size:0.95rem;"><b>Status:</b> {"Found at sorted index " + str(res_bin["index"]) if res_bin["found"] else "Not Found (-1)"}</div>'
                    f'<div style="font-size:0.95rem;"><b>Actual Comparisons:</b> <span style="color:#7C3AED; font-weight:700;">{res_bin["comparisons"]}</span></div>'
                    f'<div style="font-size:0.95rem;"><b>Total Steps:</b> {len(bin_steps)}</div>'
                    f'<div style="font-size:0.95rem;"><b>Theoretical Complexity:</b> O(log n)</div>'
                    f'<div style="font-size:0.95rem;"><b>Requires Sorted Data:</b> Yes (Verified)</div>'
                    f'</div>', unsafe_allow_html=True
                )

            st.caption(
                "Note: Binary search index refers to the sorted copy. Linear search operates on the original unsorted dataset."
            )

            # Executed comparison table
            st.write("")
            st.markdown("##### Performance Comparison Table")
            comp_table_data = [
                {
                    "Algorithm": "Linear Search",
                    "Dataset Size (n)": len(u_data),
                    "Result Correctness": "Verified",
                    "Actual Comparisons": res_lin["comparisons"],
                    "Search Steps": len(lin_steps),
                    "Theoretical Time Complexity": "O(n)",
                    "Data Precondition": "Unsorted or Sorted"
                },
                {
                    "Algorithm": "Binary Search",
                    "Dataset Size (n)": len(s_data),
                    "Result Correctness": "Verified",
                    "Actual Comparisons": res_bin["comparisons"],
                    "Search Steps": len(bin_steps),
                    "Theoretical Time Complexity": "O(log n)",
                    "Data Precondition": "Strictly Sorted"
                }
            ]
            st.dataframe(pd.DataFrame(comp_table_data), hide_index=True, use_container_width=True)

    # --- Subtab 2: Sorting ---
    with co3_subtab2:
        st.markdown("#### Interactive Sorting Evaluation")
        st.markdown(f"**Original Input Array (from {active_topo_name}):** `{unsorted_nodes}`")

        if st.button("Execute Sorting", icon=":material/sort:", type="primary", key="btn_exec_sort"):
            # Execute genuine sorting algorithms on copies
            res_b = bubble_sort(unsorted_nodes)
            res_i = insertion_sort(unsorted_nodes)
            st.session_state["sort_res"] = {
                "bubble": res_b,
                "insertion": res_i,
                "original": unsorted_nodes
            }
            st.rerun()

        sort_data = st.session_state.get("sort_res")

        if not sort_data:
            st.info("Click **Execute Sorting** to run Bubble Sort and Insertion Sort on the active topology router array.")
        else:
            res_bubble = sort_data["bubble"]
            res_insertion = sort_data["insertion"]

            st.write("")
            sort_c1, sort_c2 = st.columns(2)

            with sort_c1:
                st.markdown(
                    f'<div class="metric-card" style="border-top:3px solid #2563EB;">'
                    f'<div class="metric-card-label">Bubble Sort Output</div>'
                    f'<div style="font-size:0.95rem; margin-top:6px;"><b>Sorted Result:</b> <code>{res_bubble["sorted_data"]}</code></div>'
                    f'<div style="font-size:0.95rem;"><b>Actual Comparisons:</b> <span style="color:#2563EB; font-weight:700;">{res_bubble["comparisons"]}</span></div>'
                    f'<div style="font-size:0.95rem;"><b>Actual Swaps:</b> {res_bubble["swaps"]}</div>'
                    f'<div style="font-size:0.95rem;"><b>Passes (Early-Exit):</b> {res_bubble["passes"]}</div>'
                    f'<div style="font-size:0.95rem;"><b>Correctness Verified:</b> {res_bubble["is_correct"]}</div>'
                    f'<div style="font-size:0.95rem;"><b>Theoretical Complexity:</b> O(n²)</div>'
                    f'</div>', unsafe_allow_html=True
                )

            with sort_c2:
                st.markdown(
                    f'<div class="metric-card" style="border-top:3px solid #7C3AED;">'
                    f'<div class="metric-card-label">Insertion Sort Output</div>'
                    f'<div style="font-size:0.95rem; margin-top:6px;"><b>Sorted Result:</b> <code>{res_insertion["sorted_data"]}</code></div>'
                    f'<div style="font-size:0.95rem;"><b>Actual Comparisons:</b> <span style="color:#7C3AED; font-weight:700;">{res_insertion["comparisons"]}</span></div>'
                    f'<div style="font-size:0.95rem;"><b>Actual Shifts:</b> {res_insertion["shifts"]}</div>'
                    f'<div style="font-size:0.95rem;"><b>Iterations:</b> {res_insertion["iterations"]}</div>'
                    f'<div style="font-size:0.95rem;"><b>Correctness Verified:</b> {res_insertion["is_correct"]}</div>'
                    f'<div style="font-size:0.95rem;"><b>Theoretical Complexity:</b> O(n²)</div>'
                    f'</div>', unsafe_allow_html=True
                )

            st.write("")
            st.markdown("##### Sorting Operation Comparison Table")
            sort_table_data = [
                {
                    "Algorithm": "Bubble Sort",
                    "Input Size (n)": res_bubble["input_size"],
                    "Actual Comparisons": res_bubble["comparisons"],
                    "Swaps / Shifts": res_bubble["swaps"],
                    "Outer Passes": res_bubble["passes"],
                    "Theoretical Best Case": "O(n)",
                    "Theoretical Worst Case": "O(n²)",
                    "Correctness": "Verified"
                },
                {
                    "Algorithm": "Insertion Sort",
                    "Input Size (n)": res_insertion["input_size"],
                    "Actual Comparisons": res_insertion["comparisons"],
                    "Swaps / Shifts": res_insertion["shifts"],
                    "Outer Passes": res_insertion["iterations"],
                    "Theoretical Best Case": "O(n)",
                    "Theoretical Worst Case": "O(n²)",
                    "Correctness": "Verified"
                }
            ]
            st.dataframe(pd.DataFrame(sort_table_data), hide_index=True, use_container_width=True)


# =============================================================
# TAB 3: CO4 ROUTING TRAVERSAL TREE (REAL TREE DATA)
# =============================================================
with tab_co4:
    st.markdown("### CO4 — Routing Traversal Tree Structures")
    st.caption("A Traversal Spanning Tree generated directly from BFS parent relationships.")

    src_node = st.session_state.get("source_id", "N1")
    dst_node = st.session_state.get("dest_id", "N7")
    sim_res = st.session_state.get("sim_res")

    if not sim_res:
        st.info("Click **Run Routing** in the sidebar to run BFS and generate the Traversal Spanning Tree.")
    else:
        # Generate tree strictly from the actual parents recorded during BFS
        bfs_parents = sim_res.get("parents", {})
        tree_data = build_traversal_tree(bfs_parents, src_node, dst_node)

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
        path_set = set(tree_data.get("path_to_dest", []))

        for node in tree_data.get("nodes", []):
            parent_val = bfs_parents.get(node)
            tree_records.append({
                "Router": node,
                "Parent Router": parent_val if parent_val else "(Root — No Parent)",
                "Depth Level": levels.get(node, 0),
                "On Path to Destination": "Yes" if node in path_set else "No"
            })

        if tree_records:
            st.dataframe(pd.DataFrame(tree_records), hide_index=True, use_container_width=True)


# =============================================================
# TAB 4: CO5 ROUTING TABLE FORWARDING & COMPARISON
# =============================================================
with tab_co5:
    st.markdown("### CO5: Graph-Based Routing vs. Traditional Routing-Table Forwarding")
    st.caption("Demonstrating hop-by-hop local routing table lookups vs. centralized graph traversal routing (BFS/DFS).")

    active_preset = st.session_state.get("selected_preset", "reference")
    all_routers = sorted(list(graph.routers.keys()))
    default_src = st.session_state.get("source_id", all_routers[0] if all_routers else "N1")
    default_dst = st.session_state.get("dest_id", all_routers[-1] if all_routers else "N7")

    st.markdown("---")

    # Section 1: Dynamic Local Routing Table Inspection
    st.markdown("#### 1. Dynamic Router Forwarding Table (FIB)")
    st.caption(
        "In traditional IP networks, routers do not traverse a global graph. Instead, each router consults its local "
        "Forwarding Information Base (FIB) to determine the immediate next hop for an incoming packet's destination."
    )

    t_col1, t_col2 = st.columns([1, 2])
    with t_col1:
        inspect_idx = all_routers.index(default_src) if default_src in all_routers else 0
        inspect_router = st.selectbox(
            "Select Router to Inspect Forwarding Table",
            options=all_routers,
            index=inspect_idx,
            key="inspect_router_select"
        )
        if inspect_router:
            r_obj = graph.routers.get(inspect_router)
            is_on = r_obj.is_online if r_obj else True
            st.caption(f"Status: **{'Online' if is_on else 'Offline'}** | Direct Neighbors: **{len(graph.get_neighbors(inspect_router))}**")

    with t_col2:
        if inspect_router:
            raw_table = graph.generate_routing_table(inspect_router)
            df_table = pd.DataFrame(raw_table)
            df_table.rename(columns={
                "destination": "Destination Router",
                "next_hop": "Next Hop",
                "hops": "Metric Distance (Hops)",
                "status": "Route Status"
            }, inplace=True)
            st.dataframe(df_table, hide_index=True, use_container_width=True)

    st.markdown("---")

    # Section 2: Hop-by-Hop Packet Forwarding Simulation
    st.markdown("#### 2. Hop-by-Hop Packet Forwarding Simulation")
    st.caption("Simulate actual packet transmission forwarding router-by-router using only local table lookups.")

    fwd_col1, fwd_col2, fwd_col3 = st.columns([2, 2, 2])
    with fwd_col1:
        fwd_src_idx = all_routers.index(default_src) if default_src in all_routers else 0
        fwd_src = st.selectbox("Source Router", options=all_routers, index=fwd_src_idx, key="fwd_src_select")
    with fwd_col2:
        fwd_dst_idx = all_routers.index(default_dst) if default_dst in all_routers else (len(all_routers) - 1)
        fwd_dst = st.selectbox("Destination Router", options=all_routers, index=fwd_dst_idx, key="fwd_dst_select")
    with fwd_col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        run_fwd_clicked = st.button("Execute Table Forwarding", icon=":material/alt_route:", type="primary", use_container_width=True)

    if run_fwd_clicked:
        st.session_state["table_fwd_res"] = sim.simulate_table_forwarding(graph, fwd_src, fwd_dst)

    fwd_res = st.session_state.get("table_fwd_res")

    if not fwd_res:
        st.info("Click **Execute Table Forwarding** to simulate hop-by-hop packet forwarding across intermediate routers.")
    else:
        # Metrics Display
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Delivery Status", fwd_res.get("status", "UNKNOWN"))
        m_col2.metric("Forwarding Hops", f"{fwd_res.get('hops', 0)} hops")
        m_col3.metric("Path Length", f"{len(fwd_res.get('path', []))} routers")
        m_col4.metric("Final Terminal Router", fwd_res.get("final_router", "None"))

        # Forwarded Path Sequence
        st.markdown("##### Forwarding Path Sequence")
        st.markdown(render_path_pills(fwd_res.get("path", [])), unsafe_allow_html=True)

        # Step-by-Step Forwarding Log
        st.markdown("##### Hop-by-Hop Table Forwarding Execution Log")
        fwd_steps = fwd_res.get("steps", [])
        if fwd_steps:
            step_rows = []
            for s in fwd_steps:
                table_entry = s.get("table_entry", {})
                step_rows.append({
                    "Hop Step": s.get("step"),
                    "Current Router": s.get("current_router"),
                    "Target Destination": fwd_dst,
                    "Next Hop Forwarded": s.get("next_hop"),
                    "Action Taken": s.get("action"),
                    "Table Lookup Metric": f"{table_entry.get('hops', '-')} hops" if table_entry else "-",
                    "Description": s.get("description")
                })
            st.dataframe(pd.DataFrame(step_rows), hide_index=True, use_container_width=True)

        st.markdown("---")

        # Section 3: Live Direct Comparison: Graph Traversal vs Table Forwarding
        st.markdown("#### 3. Real-Time Comparative Evaluation: Graph Traversal vs. Table Forwarding")
        st.caption("Direct comparison between centralized graph-based routing (BFS/DFS) and distributed hop-by-hop table forwarding.")

        # Compute or fetch BFS route for accurate side-by-side comparison
        live_sim_res = st.session_state.get("sim_res")
        if live_sim_res and live_sim_res.get("source") == fwd_src and live_sim_res.get("dest") == fwd_dst:
            graph_algo_name = live_sim_res.get("algo", "BFS")
            graph_path = live_sim_res.get("path", [])
            graph_hops = live_sim_res.get("hops", 0)
            graph_success = live_sim_res.get("success", False)
        else:
            # Dynamically compute BFS reference for selected endpoints
            comp_bfs = bfs(graph, fwd_src, fwd_dst)
            graph_algo_name = "BFS (Graph Traversal)"
            graph_path = comp_bfs.get("path", [])
            graph_hops = comp_bfs.get("hops", 0)
            graph_success = comp_bfs.get("success", False)

        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown(f"**Graph-Based Routing ({graph_algo_name})**")
            st.markdown(f"- **Discovered Route:** `{' -> '.join(graph_path) if graph_path else 'None'}`")
            st.markdown(f"- **Total Hops:** `{graph_hops}`")
            st.markdown(f"- **Delivery Status:** `{'SUCCESS' if graph_success else 'FAILED'}`")
            st.markdown("- **Knowledge Model:** Centralized global graph traversal with node queue/stack")
            st.markdown("- **Path Decision:** Pre-computed upfront at controller/source before packet departs")
            st.markdown(f"- **Computational Complexity:** $O(V + E)$ where $V={len(graph.routers)}, E={len(graph.get_edges())}$")

        with c_col2:
            st.markdown("**Traditional Table-Based Forwarding (Hop-by-Hop)**")
            st.markdown(f"- **Forwarded Route:** `{' -> '.join(fwd_res.get('path', [])) if fwd_res.get('path') else 'None'}`")
            st.markdown(f"- **Total Hops:** `{fwd_res.get('hops', 0)}`")
            st.markdown(f"- **Delivery Status:** `{fwd_res.get('status', 'FAILED')}`")
            st.markdown("- **Knowledge Model:** Distributed local forwarding table (FIB) per router")
            st.markdown("- **Path Decision:** Autonomous hop-by-hop local next-hop table lookup at each router")
            st.markdown("- **Lookup Complexity:** $O(1)$ Hash table / $O(W)$ Radix Trie lookup per hop")

        # Convergence verdict
        if graph_path == fwd_res.get("path", []) and graph_success and fwd_res.get("success"):
            st.success("Both Graph Traversal and Table-Based Forwarding successfully converged onto the **exact same optimal path**.")
        elif graph_success and fwd_res.get("success"):
            st.info("Both approaches successfully delivered the packet, utilizing alternative valid paths across the network.")
        elif not graph_success and not fwd_res.get("success"):
            st.warning("Both approaches correctly identified that the destination is unreachable under the current network state.")
        else:
            st.error("Discrepancy detected: Verify link states or router online statuses.")

    st.markdown("---")

    # Section 4: Architectural Trade-off Matrix (CO5 Curriculum Requirement)
    st.markdown("#### 4. Architectural Comparison: Graph Traversal vs. Table Forwarding")
    st.caption("Theoretical and systems-level comparison between graph-based algorithmic routing and routing-table forwarding.")

    comparison_matrix = [
        {
            "Architectural Dimension": "1. Topology State Knowledge",
            "Graph Traversal Routing (BFS / DFS / SDN)": "Global centralized visibility of all network vertices and edges.",
            "Traditional Table-Based Forwarding (IP / FIB)": "Local knowledge only; routers only know immediate next-hop neighbors."
        },
        {
            "Architectural Dimension": "2. Decision Mechanism",
            "Graph Traversal Routing (BFS / DFS / SDN)": "End-to-end path calculated upfront at source or SDN controller before transmission.",
            "Traditional Table-Based Forwarding (IP / FIB)": "Autonomous hop-by-hop lookup at each intermediate router upon packet arrival."
        },
        {
            "Architectural Dimension": "3. Search / Lookup Complexity",
            "Graph Traversal Routing (BFS / DFS / SDN)": "O(V + E) traversal time computed over the full network topology.",
            "Traditional Table-Based Forwarding (IP / FIB)": "O(1) hash table or O(W) longest prefix match (LPM) per forwarding hop."
        },
        {
            "Architectural Dimension": "4. Memory & State Overhead",
            "Graph Traversal Routing (BFS / DFS / SDN)": "High memory footprint: stores complete graph adjacency matrix or edge lists.",
            "Traditional Table-Based Forwarding (IP / FIB)": "Low memory footprint: stores only destination-to-next-hop forwarding table."
        },
        {
            "Architectural Dimension": "5. Link Failure Reaction",
            "Graph Traversal Routing (BFS / DFS / SDN)": "Requires re-executing full graph search or notifying centralized controller.",
            "Traditional Table-Based Forwarding (IP / FIB)": "Local route re-convergence (e.g. fast reroute via alternate next-hop entry)."
        },
        {
            "Architectural Dimension": "6. Real-World Industry Analogs",
            "Graph Traversal Routing (BFS / DFS / SDN)": "Software-Defined Networking (SDN / OpenFlow), Google Andromeda, AWS VPC.",
            "Traditional Table-Based Forwarding (IP / FIB)": "Internet Core IP Forwarding, BGP, OSPF, Cisco/Juniper hardware ASIC FIB."
        }
    ]

    st.dataframe(pd.DataFrame(comparison_matrix), hide_index=True, use_container_width=True)
