"""
visualizer.py — Plotly visualization generators for NetRoute network graphs and traversal trees.
Provides high-contrast, clean, responsive interactive network diagrams.
"""

from typing import Dict, Any, List, Set, Tuple, Optional
import streamlit as st
import plotly.graph_objects as go
from network import Graph
from theme import (
    COLOR_NODE_DEFAULT, COLOR_NODE_SOURCE, COLOR_NODE_DEST, COLOR_NODE_ACTIVE,
    COLOR_NODE_VISITED, COLOR_NODE_ROUTE, COLOR_NODE_OFFLINE, COLOR_PACKET,
    COLOR_EDGE_DEFAULT, COLOR_EDGE_EXPLORED, COLOR_EDGE_ROUTE, COLOR_EDGE_TREE,
    COLOR_EDGE_ACTIVE, PRIMARY, PRIMARY_DARK, TEXT_MAIN, TEXT_MUTED
)


def render_plotly(fig: go.Figure, key: Optional[str] = None):
    """Renders a Plotly figure using modern width='stretch' to eliminate deprecation warnings."""
    st.plotly_chart(fig, width="stretch", key=key)


def export_figure_png(fig: go.Figure, width: int = 1000, height: int = 600, scale: float = 2.0) -> Optional[bytes]:
    """
    Exports a Plotly figure to PNG image bytes using Kaleido.
    Returns bytes on success, or None if Kaleido is unavailable or encounters an error.
    """
    try:
        return fig.to_image(format="png", width=width, height=height, scale=scale)
    except Exception:
        return None


def build_network_figure(
    graph: Graph,
    active: Dict[str, Any],
    src_id: str,
    dst_id: str,
    height: int = 430,
    title: Optional[str] = None,
    highlight_bridges: Optional[Set[Tuple[str, str]]] = None,
    highlight_aps: Optional[Set[str]] = None
) -> go.Figure:
    """Renders an interactive network graph with real-time traversal and packet indicators."""
    fig = go.Figure()

    if not graph.routers:
        fig.add_annotation(
            text="Network is empty. Please add routers or load a topology preset.",
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
    visited_nodes = set(active.get("visited_nodes", []))
    explored_edges = set(active.get("explored_edges", []))
    route_nodes = set(active.get("route_nodes", []))
    route_edges = [tuple(sorted(e)) for e in active.get("route_edges", [])]
    packet_node = active.get("packet_node")
    clean_bridges = {tuple(sorted(e)) for e in (highlight_bridges or set())}
    clean_aps = set(highlight_aps or set())

    # 1. Draw transmission links (Edges)
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
            line_color = COLOR_EDGE_ACTIVE
            line_width = 4.2
            line_dash = "solid"
        elif is_completed and e in route_edges:
            line_color = COLOR_EDGE_ROUTE
            line_width = 4.0
            line_dash = "solid"
        elif clean_bridges and e in clean_bridges:
            line_color = "#D97706"
            line_width = 3.5
            line_dash = "dash"
        elif e in explored_edges:
            line_color = COLOR_EDGE_EXPLORED
            line_width = 2.4
            line_dash = "solid"
        else:
            line_color = COLOR_EDGE_DEFAULT
            line_width = 1.8
            line_dash = "solid"

        fig.add_trace(go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode="lines",
            line=dict(color=line_color, width=line_width, dash=line_dash),
            hoverinfo="none",
            showlegend=False
        ))

        # Weight indicator on link midpoint
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0
        w_text = str(int(weight) if weight.is_integer() else weight)
        is_bridge = clean_bridges and e in clean_bridges
        badge_text = f"<b>{w_text}</b>" if not is_bridge else f"<b>{w_text} ⚡Bridge</b>"
        badge_bg = "#FEF3C7" if is_bridge else "#FFFFFF"
        badge_border = "#D97706" if is_bridge else "#CBD5E1"

        fig.add_annotation(
            x=mid_x, y=mid_y,
            text=badge_text,
            showarrow=False,
            font=dict(size=10, color="#92400E" if is_bridge else "#475569"),
            bgcolor=badge_bg,
            bordercolor=badge_border,
            borderwidth=1,
            borderpad=3,
            opacity=0.95
        )

    # 2. Draw Router Nodes
    nodes = sorted(graph.routers.keys())
    node_x, node_y, node_labels, node_colors, border_colors, text_colors, hover_texts = [], [], [], [], [], [], []

    for rid in nodes:
        r = graph.routers[rid]
        node_x.append(r.x)
        node_y.append(r.y)
        node_labels.append(rid)

        if not r.is_online:
            fill_c = COLOR_NODE_OFFLINE
            border_c = "#475569"
            txt_c = "#FFFFFF"
        elif is_completed:
            if rid == dst_id:
                fill_c = COLOR_NODE_DEST
                border_c = "#D97706"
                txt_c = "#FFFFFF"
            elif rid == src_id:
                fill_c = COLOR_NODE_SOURCE
                border_c = "#059669"
                txt_c = "#FFFFFF"
            elif rid in route_nodes:
                fill_c = COLOR_NODE_ROUTE
                border_c = "#047857"
                txt_c = "#FFFFFF"
            elif rid in visited_nodes:
                fill_c = COLOR_NODE_VISITED
                border_c = "#0284C7"
                txt_c = "#FFFFFF"
            else:
                fill_c = "#FFFFFF"
                border_c = "#94A3B8"
                txt_c = "#475569"
        else:
            if rid == active_node:
                fill_c = COLOR_NODE_ACTIVE
                border_c = "#5B21B6"
                txt_c = "#FFFFFF"
            elif rid == action_target:
                fill_c = "#0891B2"
                border_c = "#0E7490"
                txt_c = "#FFFFFF"
            elif rid == src_id:
                fill_c = COLOR_NODE_SOURCE
                border_c = "#059669"
                txt_c = "#FFFFFF"
            elif rid == dst_id:
                fill_c = COLOR_NODE_DEST
                border_c = "#D97706"
                txt_c = "#FFFFFF"
            elif rid in visited_nodes:
                fill_c = COLOR_NODE_VISITED
                border_c = "#0284C7"
                txt_c = "#FFFFFF"
            else:
                fill_c = "#FFFFFF"
                border_c = "#CBD5E1"
                txt_c = "#64748B"

        if clean_aps and rid in clean_aps:
            border_c = "#D97706"
            if fill_c == "#FFFFFF":
                fill_c = "#FEF3C7"
                txt_c = "#92400E"

        node_colors.append(fill_c)
        border_colors.append(border_c)
        text_colors.append(txt_c)

        sub_text = r.name
        if clean_aps and rid in clean_aps:
            sub_text += " [AP]"
        if rid == src_id and "(Src)" not in sub_text:
            sub_text += " (Src)"
        elif rid == dst_id and "(Dst)" not in sub_text:
            sub_text += " (Dst)"

        sub_color = "#10B981" if rid == src_id else ("#F59E0B" if rid == dst_id else ("#D97706" if (clean_aps and rid in clean_aps) else "#1E293B"))

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
            f"Status: {'ONLINE' if r.is_online else 'OFFLINE'}<br>"
            f"Neighbors: {', '.join(nbrs) if nbrs else 'None'}<br>"
            f"In Visited Set: {'Yes' if rid in visited_nodes else 'No'}<br>"
            f"In Final Route: {'Yes' if rid in route_nodes else 'No'}"
        )

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=34, color=node_colors, line=dict(color=border_colors, width=2.4)),
        text=node_labels,
        textposition="middle center",
        textfont=dict(size=10, color=text_colors, family="-apple-system, sans-serif"),
        hoverinfo="text", hovertext=hover_texts, showlegend=False
    ))

    # 3. Draw Packet indicator if packet animation is active
    if packet_node and packet_node in graph.routers:
        pr = graph.routers[packet_node]
        fig.add_trace(go.Scatter(
            x=[pr.x], y=[pr.y],
            mode="markers",
            marker=dict(size=16, color=COLOR_PACKET, symbol="diamond", line=dict(color="#FFFFFF", width=2)),
            hoverinfo="text", hovertext=f"Packet at Router {packet_node}",
            showlegend=False
        ))

    all_x = [r.x for r in graph.routers.values()]
    all_y = [r.y for r in graph.routers.values()]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    dx = max(80.0, max_x - min_x)
    dy = max(80.0, max_y - min_y)

    layout_kwargs: Dict[str, Any] = {
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "height": height,
        "margin": dict(l=25, r=25, t=35 if title else 25, b=25),
        "hovermode": "closest",
        "xaxis": dict(range=[min_x - dx * 0.12, max_x + dx * 0.12], showgrid=False, zeroline=False, showticklabels=False),
        "yaxis": dict(range=[max_y + dy * 0.22, min_y - dy * 0.22], showgrid=False, zeroline=False, showticklabels=False)
    }
    if title:
        layout_kwargs["title"] = dict(text=f"<b>{title}</b>", font=dict(size=13, color=TEXT_MAIN), x=0.03, y=0.96)

    fig.update_layout(**layout_kwargs)
    return fig


def build_traversal_tree_figure(tree_data: Dict[str, Any], src_id: str, dst_id: str, height: int = 400) -> go.Figure:
    """Renders a hierarchical Plotly tree figure derived from traversal parent pointers."""
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
    """Renders a dedicated network graph highlighting discovered path and explored nodes for an algorithm."""
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

    route_edges = set()
    for i in range(len(path) - 1):
        route_edges.add(tuple(sorted((path[i], path[i + 1]))))

    explored_edges = set()
    for u, v in res.get("tree_edges", []):
        explored_edges.add(tuple(sorted((u, v))))

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
            line_width = 2.4
            line_dash = "solid"
        else:
            line_color = "#CBD5E1"
            line_width = 1.6
            line_dash = "solid"

        fig.add_trace(go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode="lines",
            line=dict(color=line_color, width=line_width, dash=line_dash),
            hoverinfo="none", showlegend=False
        ))

        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0
        w_text = str(int(weight) if weight.is_integer() else weight)

        fig.add_annotation(
            x=mid_x, y=mid_y,
            text=f"<b>{w_text}</b>",
            showarrow=False,
            font=dict(size=9, color="#475569"),
            bgcolor="#FFFFFF", bordercolor="#CBD5E1", borderwidth=1, borderpad=2, opacity=0.9
        )

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
