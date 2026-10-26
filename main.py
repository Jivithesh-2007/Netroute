import time
import json
from typing import Dict, List, Set, Tuple, Optional, Any

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import Theme, CUSTOM_CSS, render_metric
from network import Graph, Router, validate_router_id
from algorithms import SimulationStep, SimulationResult
import simulation as sim


st.set_page_config(
    page_title="NetRoute — Network Packet-Routing Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
sim.init_session_state()
graph: Graph = st.session_state.graph


# -------------------------------------------------------------
# GRAPH VISUALIZATION ENGINE (Plotly)
# -------------------------------------------------------------
def build_network_figure(graph: Graph, active_data: Dict[str, Any], src_id: str, dst_id: str) -> go.Figure:
    fig = go.Figure()

    if not graph.routers:
        fig.add_annotation(
            text="Network is empty. Add routers or load a preset from the sidebar.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=Theme.TEXT_MUTED)
        )
        fig.update_layout(
            paper_bgcolor=Theme.BG_SURFACE,
            plot_bgcolor=Theme.BG_SURFACE,
            height=460,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig

    active_router = active_data.get("active_router")
    active_edge = active_data.get("active_edge")
    visited_routers = active_data.get("visited_routers", set())
    explored_edges = active_data.get("explored_edges", set())
    route_routers = active_data.get("route_routers", set())
    final_route_edges = active_data.get("final_route_edges", [])
    packet_node = active_data.get("packet_node")

    # 1. Base Edges
    norm_x, norm_y = [], []
    for (u, v) in graph.edges.keys():
        e = tuple(sorted((u, v)))
        if e not in final_route_edges and e not in explored_edges and e != active_edge:
            if u in graph.routers and v in graph.routers:
                norm_x.extend([graph.routers[u].x, graph.routers[v].x, None])
                norm_y.extend([graph.routers[u].y, graph.routers[v].y, None])

    if norm_x:
        fig.add_trace(go.Scatter(
            x=norm_x, y=norm_y,
            mode="lines",
            line=dict(color=Theme.COLOR_DEFAULT_EDGE, width=2),
            hoverinfo="none",
            name="Normal Link",
            showlegend=True
        ))

    # 2. Explored Edges
    exp_x, exp_y = [], []
    for (u, v) in explored_edges:
        e = tuple(sorted((u, v)))
        if e not in final_route_edges and e != active_edge:
            if u in graph.routers and v in graph.routers:
                exp_x.extend([graph.routers[u].x, graph.routers[v].x, None])
                exp_y.extend([graph.routers[u].y, graph.routers[v].y, None])

    if exp_x:
        fig.add_trace(go.Scatter(
            x=exp_x, y=exp_y,
            mode="lines",
            line=dict(color=Theme.COLOR_EXPLORE_EDGE, width=3, dash="dot"),
            hoverinfo="none",
            name="Explored Link",
            showlegend=True
        ))

    # 3. Final Route Edges
    rt_x, rt_y = [], []
    for (u, v) in final_route_edges:
        if u in graph.routers and v in graph.routers:
            rt_x.extend([graph.routers[u].x, graph.routers[v].x, None])
            rt_y.extend([graph.routers[u].y, graph.routers[v].y, None])

    if rt_x:
        fig.add_trace(go.Scatter(
            x=rt_x, y=rt_y,
            mode="lines",
            line=dict(color=Theme.COLOR_ROUTE_EDGE, width=5),
            hoverinfo="none",
            name="Active Route",
            showlegend=True
        ))

    # 4. Current Active Step Edge
    if active_edge:
        u, v = active_edge
        if u in graph.routers and v in graph.routers:
            fig.add_trace(go.Scatter(
                x=[graph.routers[u].x, graph.routers[v].x],
                y=[graph.routers[u].y, graph.routers[v].y],
                mode="lines",
                line=dict(color=Theme.CYAN, width=5),
                hoverinfo="none",
                name="Current Hop Link",
                showlegend=True
            ))

    # 5. Nodes Layer
    nodes = sorted(graph.routers.keys())
    node_x, node_y, node_text, node_colors, border_colors, hover_texts, border_widths = [], [], [], [], [], [], []

    for rid in nodes:
        r = graph.routers[rid]
        node_x.append(r.x)
        node_y.append(r.y)
        node_text.append(rid)

        # Determine color priority
        if not r.is_online:
            color = Theme.COLOR_OFFLINE_NODE
            border = "#64748B"
            b_width = 2
        elif rid == active_router:
            color = Theme.COLOR_EXPLORE_NODE
            border = "#9A3412"
            b_width = 3.5
        elif rid == src_id:
            color = Theme.COLOR_SOURCE_NODE
            border = "#1E3A8A"
            b_width = 3
        elif rid == dst_id:
            color = Theme.COLOR_DEST_NODE
            border = "#4C1D95"
            b_width = 3
        elif rid in route_routers:
            color = Theme.COLOR_ROUTE_NODE
            border = "#14532D"
            b_width = 3
        elif rid in visited_routers:
            color = Theme.COLOR_VISITED_NODE
            border = "#2563EB"
            b_width = 2
        else:
            color = "#FFFFFF"
            border = Theme.COLOR_DEFAULT_NODE
            b_width = 2.5

        node_colors.append(color)
        border_colors.append(border)
        border_widths.append(b_width)

        status_str = "🟢 Online" if r.is_online else "🔴 Offline"
        nbrs = [entry[0] for entry in graph.adjacency.get(rid, [])]
        nbr_str = ", ".join(sorted(nbrs)) if nbrs else "None"
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
        marker=dict(
            size=30,
            color=node_colors,
            line=dict(color=border_colors, width=border_widths)
        ),
        text=node_text,
        textposition="middle center",
        textfont=dict(
            family="Helvetica, Arial, sans-serif",
            size=11,
            color=["#FFFFFF" if c != "#FFFFFF" and c != Theme.COLOR_VISITED_NODE else Theme.TEXT_MAIN for c in node_colors]
        ),
        hoverinfo="text",
        hovertext=hover_texts,
        name="Routers",
        showlegend=False
    ))

    # 6. Current Packet Position Overlay
    if packet_node and packet_node in graph.routers:
        pr = graph.routers[packet_node]
        fig.add_trace(go.Scatter(
            x=[pr.x], y=[pr.y],
            mode="markers+text",
            marker=dict(
                size=44,
                symbol="circle-open",
                color=Theme.COLOR_PACKET,
                line=dict(color=Theme.COLOR_PACKET, width=3.5)
            ),
            text=["📦"],
            textposition="top center",
            textfont=dict(size=18),
            hoverinfo="text",
            hovertext=f"<b>Packet In-Transit</b><br>Currently at {packet_node}",
            name="Packet (📦)",
            showlegend=True
        ))

    # Calculate graph boundaries with padding
    all_x = [r.x for r in graph.routers.values()]
    all_y = [r.y for r in graph.routers.values()]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    dx = max(80.0, max_x - min_x)
    dy = max(80.0, max_y - min_y)
    pad_x = dx * 0.15
    pad_y = dy * 0.18

    fig.update_layout(
        paper_bgcolor=Theme.BG_SURFACE,
        plot_bgcolor=Theme.BG_SURFACE,
        height=480,
        margin=dict(l=24, r=24, t=28, b=24),
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=Theme.TEXT_MUTED)
        ),
        xaxis=dict(
            range=[min_x - pad_x, max_x + pad_x],
            showgrid=False, zeroline=False, showticklabels=False
        ),
        yaxis=dict(
            range=[max_y + pad_y, min_y - pad_y],  # Inverted so Y grows downward matching canvas coordinates
            showgrid=False, zeroline=False, showticklabels=False
        )
    )
    return fig


# -------------------------------------------------------------
# APPLICATION HEADER
# -------------------------------------------------------------
header_col1, header_col2 = st.columns([7, 3])
with header_col1:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap: 12px; margin-bottom: 4px;">'
        f'<h1 style="margin:0; font-size:1.85rem; font-weight:800; color:{Theme.PRIMARY};">NetRoute</h1>'
        f'<span style="font-size:1.2rem; color:{Theme.BORDER};">•</span>'
        f'<span style="font-size:1.05rem; font-weight:600; color:{Theme.TEXT_MAIN};">Interactive Network Packet-Routing Simulator</span>'
        f'</div>'
        f'<div style="font-size:0.83rem; color:{Theme.TEXT_MUTED}; margin-bottom: 12px;">'
        f'Demonstrating Graph Traversal (BFS & DFS), Live Queue / Stack Inspection, Dynamic Topology Management, and Packet Routing'
        f'</div>',
        unsafe_allow_html=True
    )
with header_col2:
    st.markdown(
        f'<div style="display:flex; justify-content:flex-end; align-items:center; gap:6px; margin-top:6px;">'
        f'<span class="badge-co" style="color:{Theme.PRIMARY}; border-color:#93C5FD;">CO1: STACK & QUEUE</span>'
        f'<span class="badge-co" style="color:{Theme.CYAN}; border-color:#A5F3FC;">CO2: DYNAMIC GRAPH</span>'
        f'<span class="badge-co" style="color:{Theme.SUCCESS}; border-color:#86EFAC;">CO5: ROUTING</span>'
        f'</div>',
        unsafe_allow_html=True
    )


# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### ⚙️ Simulation & Routing")
    router_ids = sorted(graph.routers.keys())

    # Algorithm Choice
    algo = st.radio(
        "Routing Algorithm",
        options=["BFS (Shortest-Hop)", "DFS (Path Discovery)"],
        index=0 if "BFS" in st.session_state.algo_choice else 1,
        help="BFS uses a FIFO Queue to find minimum hops. DFS uses a LIFO Stack for deep branch exploration."
    )
    if algo != st.session_state.algo_choice:
        st.session_state.algo_choice = algo
        sim.invalidate_simulation()

    # Source & Destination
    col_src, col_dst = st.columns(2)
    with col_src:
        default_src_idx = router_ids.index(st.session_state.source_id) if st.session_state.source_id in router_ids else 0
        src = st.selectbox("Source", options=router_ids, index=default_src_idx if router_ids else 0)
        st.session_state.source_id = src
    with col_dst:
        default_dst_idx = router_ids.index(st.session_state.dest_id) if st.session_state.dest_id in router_ids else (len(router_ids) - 1 if router_ids else 0)
        dst = st.selectbox("Destination", options=router_ids, index=default_dst_idx if router_ids else 0)
        st.session_state.dest_id = dst

    if st.button("🚀 Run Algorithm", type="primary", use_container_width=True):
        sim.run_simulation(graph, algo, src, dst)

    # Simulation Step & Replay Controls
    res: Optional[SimulationResult] = st.session_state.get("sim_result")
    if res and res.steps:
        st.markdown("---")
        st.markdown(f"**Step Navigation ({st.session_state.step_index + 1} / {len(res.steps)})**")

        step_col1, step_col2, step_col3, step_col4 = st.columns(4)
        with step_col1:
            if st.button("⏮ First", use_container_width=True):
                sim.reset_playback()
        with step_col2:
            if st.button("◀ Back", use_container_width=True):
                sim.step_backward()
        with step_col3:
            if st.button("Forward ▶", use_container_width=True):
                sim.step_forward()
        with step_col4:
            if st.button("End ⏭", use_container_width=True):
                sim.jump_to_step(len(res.steps) - 1)

        new_step = st.slider(
            "Scrub Step",
            min_value=0,
            max_value=len(res.steps) - 1,
            value=st.session_state.step_index,
            label_visibility="collapsed"
        )
        if new_step != st.session_state.step_index:
            sim.jump_to_step(new_step)

        # Auto-play Toggle
        auto_col1, auto_col2 = st.columns([1, 1])
        with auto_col1:
            auto_play = st.checkbox("Auto-Play", value=st.session_state.auto_play)
            st.session_state.auto_play = auto_play
        with auto_col2:
            speed_delay = st.slider("Delay (s)", min_value=0.1, max_value=1.5, value=0.4, step=0.1)

        # Packet Transmission Controls
        if res.success and res.path:
            st.markdown("---")
            st.markdown(f"**📦 Packet Transmission**")
            p_hop = st.session_state.get("packet_hop", 0)
            st.caption(f"Hop {p_hop} / {len(res.path) - 1} • At Router **{res.path[p_hop]}**")

            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                if st.button("Step ➡️", use_container_width=True):
                    sim.packet_step_forward()
            with p_col2:
                p_auto = st.checkbox("Stream 📦", value=st.session_state.packet_play)
                st.session_state.packet_play = p_auto
            with p_col3:
                if st.button("Reset ↺", use_container_width=True):
                    sim.reset_packet()

    # Presets & Network Topology Management
    st.markdown("---")
    with st.expander("🌐 Presets & Topologies", expanded=False):
        preset_choice = st.selectbox(
            "Select Built-in Topology",
            options=["Sample (Default)", "Direct Route", "Multiple Routes (Spine/Leaf)", "Cyclic Network", "Disconnected Subnets", "Offline Router Barrier"]
        )
        if st.button("Load Preset", use_container_width=True):
            mapping = {
                "Sample (Default)": "sample",
                "Direct Route": "direct",
                "Multiple Routes (Spine/Leaf)": "multi_route",
                "Cyclic Network": "cyclic",
                "Disconnected Subnets": "disconnected",
                "Offline Router Barrier": "offline_router"
            }
            graph.load_preset(mapping[preset_choice])
            sim.invalidate_simulation()
            st.rerun()

        st.markdown("##### Random Generators")
        gen_n = st.slider("Number of Routers", min_value=3, max_value=12, value=6)
        gen_c1, gen_c2 = st.columns(2)
        with gen_c1:
            if st.button("Connected", use_container_width=True):
                graph.generate_connected(gen_n)
                sim.invalidate_simulation()
                st.rerun()
        with gen_c2:
            if st.button("Disconnected", use_container_width=True):
                graph.generate_disconnected(gen_n)
                sim.invalidate_simulation()
                st.rerun()

    # Topology Editor
    with st.expander("🛠️ Edit Topology (CO2)", expanded=False):
        st.markdown("##### Add Router")
        add_c1, add_c2 = st.columns([1, 2])
        with add_c1:
            new_rid = st.text_input("ID", placeholder="R7", max_chars=8).upper()
        with add_c2:
            new_rname = st.text_input("Name", placeholder="Branch Switch")
        if st.button("Add Router", use_container_width=True):
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
        del_r = st.selectbox("Select to delete", options=["-- Select --"] + router_ids, key="del_r_select")
        if st.button("Delete Router", use_container_width=True):
            if del_r != "-- Select --":
                graph.remove_router(del_r)
                sim.invalidate_simulation()
                st.success(f"Removed {del_r}")
                st.rerun()

        st.markdown("##### Add Connection")
        if len(router_ids) >= 2:
            ac1, ac2 = st.columns(2)
            with ac1:
                link_u = st.selectbox("Endpoint A", options=router_ids, key="link_u")
            with ac2:
                link_v = st.selectbox("Endpoint B", options=[r for r in router_ids if r != link_u], key="link_v")
            if st.button("Connect Routers", use_container_width=True):
                if graph.add_edge(link_u, link_v):
                    sim.invalidate_simulation()
                    st.success(f"Connected {link_u} <-> {link_v}")
                    st.rerun()
                else:
                    st.warning("Connection already exists or invalid.")

        st.markdown("##### Remove Connection")
        edge_list = [f"{u} <-> {v}" for (u, v) in sorted(graph.edges.keys())]
        if edge_list:
            rem_edge_str = st.selectbox("Select link", options=edge_list)
            if st.button("Remove Link", use_container_width=True):
                u_sel, v_sel = [x.strip() for x in rem_edge_str.split("<->")]
                graph.remove_edge(u_sel, v_sel)
                sim.invalidate_simulation()
                st.success(f"Removed {rem_edge_str}")
                st.rerun()

        st.markdown("##### Toggle Online / Offline")
        tog_r = st.selectbox("Select Router to Toggle", options=router_ids, key="tog_r")
        if st.button("Toggle Status", use_container_width=True):
            new_status = graph.toggle_router_status(tog_r)
            sim.invalidate_simulation()
            st.info(f"Router {tog_r} is now {'Online 🟢' if new_status else 'Offline 🔴'}")
            st.rerun()

        st.markdown("##### Arrange Layout")
        if st.button("Fit & Circle Layout", use_container_width=True):
            graph.auto_layout()
            st.rerun()

    # JSON Export / Import
    with st.expander("💾 Export / Import Topology", expanded=False):
        topo_json = json.dumps(graph.to_dict(), indent=2)
        st.download_button(
            label="Download JSON",
            data=topo_json,
            file_name="network_topology.json",
            mime="application/json",
            use_container_width=True
        )
        uploaded = st.file_uploader("Upload Topology JSON", type=["json"])
        if uploaded is not None:
            try:
                data = json.load(uploaded)
                graph.load_from_dict(data)
                sim.invalidate_simulation()
                st.success("Topology imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load JSON: {e}")


# -------------------------------------------------------------
# MAIN WORKSPACE: ACTIVE SIMULATION DATA
# -------------------------------------------------------------
active_data = sim.get_active_elements(graph)
current_step: Optional[SimulationStep] = active_data.get("current_step")
sim_res: Optional[SimulationResult] = active_data.get("result")

# Compact Statistics Cards
online_count = sum(1 for r in graph.routers.values() if r.is_online)
components = graph.get_connected_components()
comp_count = len(components)
visited_count = len(active_data.get("visited_routers", []))
route_hops = f"{len(sim_res.path) - 1} hops" if (sim_res and sim_res.success) else "—"
max_struct = str(sim_res.max_structure_size) if sim_res else "—"
tot_steps = str(sim_res.total_steps) if sim_res else "—"

m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
with m1:
    st.markdown(render_metric("Routers", f"{len(graph.routers)}", f"{online_count} online", Theme.PRIMARY), unsafe_allow_html=True)
with m2:
    st.markdown(render_metric("Links", f"{len(graph.edges)}", "Undirected", Theme.CYAN), unsafe_allow_html=True)
with m3:
    st.markdown(render_metric("Components", f"{comp_count}", "1 = Connected" if comp_count == 1 else "Partitioned", Theme.WARNING if comp_count > 1 else Theme.SUCCESS), unsafe_allow_html=True)
with m4:
    st.markdown(render_metric("Visited", f"{visited_count}", f"of {len(graph.routers)} routers", Theme.CYAN), unsafe_allow_html=True)
with m5:
    st.markdown(render_metric("Route Hops", route_hops, "Shortest" if (sim_res and "BFS" in sim_res.algorithm_name) else "Discovered", Theme.SUCCESS if (sim_res and sim_res.success) else Theme.TEXT_MUTED), unsafe_allow_html=True)
with m6:
    st.markdown(render_metric("Max Struct", max_struct, "Queue / Stack", Theme.PURPLE), unsafe_allow_html=True)
with m7:
    st.markdown(render_metric("Total Steps", tot_steps, f"Step {st.session_state.step_index + 1}" if sim_res else "Ready", Theme.PRIMARY), unsafe_allow_html=True)

st.write("")

# Main Network Graph View
fig = build_network_figure(graph, active_data, st.session_state.source_id, st.session_state.dest_id)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True})


# -------------------------------------------------------------
# STEP BANNER
# -------------------------------------------------------------
if current_step:
    st.info(f"**Step {current_step.step_number} [{current_step.step_type.upper()}]:** {current_step.message}")
elif sim_res:
    st.info(f"**Algorithm Result:** {sim_res.message}")


# -------------------------------------------------------------
# INSPECTORS & DETAILS TABS
# -------------------------------------------------------------
tab_inspect, tab_repr, tab_tree, tab_log, tab_co = st.tabs([
    "🔍 Queue / Stack Inspector (CO1)",
    "📊 Graph Representations (CO2 & CO5)",
    "🌲 Traversal Tree & Route (CO5)",
    "📜 Execution Trace Log",
    "🎓 Course Outcome Mapping"
])

# ----------------- TAB 1: QUEUE / STACK INSPECTOR -----------------
with tab_inspect:
    is_bfs = "BFS" in st.session_state.algo_choice
    struct_name = "FIFO Queue" if is_bfs else "LIFO Stack"
    st.markdown(f"#### Live {struct_name} State")

    if current_step:
        elements = current_step.data_structure_state
        op_col1, op_col2, op_col3 = st.columns(3)
        with op_col1:
            st.metric("Last Operation", current_step.last_op or "None")
        with op_col2:
            st.metric("Current Element", current_step.current_element or "None")
        with op_col3:
            st.metric(f"Current {struct_name} Size", len(elements))

        st.markdown(f"##### {struct_name} Contents:")
        if not elements:
            st.caption(f"*The {struct_name} is currently empty.*")
        else:
            chips_html = []
            if is_bfs:
                for i, item in enumerate(elements):
                    if i == 0 and len(elements) == 1:
                        chips_html.append(f'<span class="chip chip-front">FRONT & REAR: {item}</span>')
                    elif i == 0:
                        chips_html.append(f'<span class="chip chip-front">FRONT: {item}</span>')
                    elif i == len(elements) - 1:
                        chips_html.append(f'<span class="chip chip-rear">REAR: {item}</span>')
                    else:
                        chips_html.append(f'<span class="chip chip-normal">{item}</span>')
                st.markdown(f'<div>{" ➔ ".join(chips_html)}</div>', unsafe_allow_html=True)
                st.caption("FIFO Order: Elements are dequeued from FRONT and enqueued at REAR.")
            else:
                for i, item in enumerate(elements):
                    if i == len(elements) - 1 and len(elements) == 1:
                        chips_html.append(f'<span class="chip chip-top">TOP & BOTTOM: {item}</span>')
                    elif i == len(elements) - 1:
                        chips_html.append(f'<span class="chip chip-top">TOP: {item}</span>')
                    elif i == 0:
                        chips_html.append(f'<span class="chip chip-bottom">BOTTOM: {item}</span>')
                    else:
                        chips_html.append(f'<span class="chip chip-normal">{item}</span>')
                st.markdown(f'<div>{" ➔ ".join(chips_html)}</div>', unsafe_allow_html=True)
                st.caption("LIFO Order: Stack is displayed from Bottom (left) to Top (right). Elements are pushed and popped at TOP.")

        # Visited Routers & Parent Map
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.markdown("##### Traversal Sequence (Visited Order):")
            if current_step.visited_elements:
                v_chips = [f'<span class="chip chip-visited">{node}</span>' for node in current_step.visited_elements]
                st.markdown(f'<div>{" ➔ ".join(v_chips)}</div>', unsafe_allow_html=True)
            else:
                st.caption("*No routers marked visited yet.*")
        with v_col2:
            st.markdown("##### Parent Pointer Map:")
            if current_step.parent_map:
                pm_df = pd.DataFrame([
                    {"Router": node, "Parent": par if par is not None else "None (Source)"}
                    for node, par in sorted(current_step.parent_map.items())
                ])
                st.dataframe(pm_df, use_container_width=True, height=140)
            else:
                st.caption("*Parent map unpopulated.*")
    else:
        st.info("Run an algorithm (BFS or DFS) from the sidebar to inspect the live queue or stack.")

# ----------------- TAB 2: GRAPH REPRESENTATIONS -----------------
with tab_repr:
    rep_col1, rep_col2 = st.columns(2)
    with rep_col1:
        st.markdown("#### Dynamic Adjacency List")
        st.caption("Adjacency List stores adjacent outgoing connections per vertex. Space complexity: O(V + E).")
        adj_list = graph.get_adjacency_list()
        for rid, neighbors in adj_list.items():
            r_obj = graph.routers.get(rid)
            status_dot = "🟢" if (r_obj and r_obj.is_online) else "🔴"
            nbr_tags = "".join([f'<span class="chip chip-normal">{n}</span>' for n in neighbors]) or '<span style="color:#94A3B8; font-style:italic;">No neighbors</span>'
            st.markdown(f"**{status_dot} {rid}** ➔ {nbr_tags}", unsafe_allow_html=True)

    with rep_col2:
        st.markdown("#### Adjacency Matrix")
        st.caption("Matrix representation where entry (u, v) = 1 indicates an edge. Space complexity: O(V²).")
        nodes, matrix = graph.get_adjacency_matrix()
        if nodes:
            matrix_df = pd.DataFrame(
                [[int(val) for val in row] for row in matrix],
                index=nodes,
                columns=nodes
            )
            st.dataframe(matrix_df, use_container_width=True, height=220)
        else:
            st.caption("*No routers in network.*")

# ----------------- TAB 3: TRAVERSAL TREE & ROUTE -----------------
with tab_tree:
    if sim_res:
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown("#### Discovered Route")
            if sim_res.success and sim_res.path:
                st.success(f"Route: **{' ➔ '.join(sim_res.path)}**")
                st.write(f"- **Total Hops:** {len(sim_res.path) - 1}")
                st.write(f"- **Algorithm Type:** {sim_res.algorithm_name}")
                if "BFS" in sim_res.algorithm_name:
                    st.caption("BFS guarantees the shortest-hop route in unweighted networks because it explores level by level.")
                else:
                    st.caption("DFS explores deep branches first. It discovers a valid reachable path, but not necessarily minimum hops.")
            else:
                st.error(sim_res.message)

        with t_col2:
            st.markdown("#### Traversal Tree Edges")
            st.caption("Edges recorded when discovering new vertices during the search.")
            if sim_res.tree_edges:
                tree_df = pd.DataFrame([
                    {"Parent (Source)": u, "Child (Discovered)": v}
                    for (u, v) in sim_res.tree_edges
                ])
                st.dataframe(tree_df, use_container_width=True, height=200)
            else:
                st.caption("*No tree edges recorded.*")
    else:
        st.info("Run an algorithm to view the route and traversal tree.")

# ----------------- TAB 4: EXECUTION TRACE LOG -----------------
with tab_log:
    st.markdown("#### Complete Execution Step Log")
    if sim_res and sim_res.steps:
        log_lines = []
        for s in sim_res.steps:
            type_class = "log-success" if s.step_type == "complete" else "log-type"
            log_lines.append(
                f'<div class="log-entry">'
                f'<span class="log-step">Step {s.step_number:02d}:</span> '
                f'<span class="{type_class}">[{s.step_type.upper()}]</span> '
                f'<span class="log-msg">{s.message}</span>'
                f'</div>'
            )
        st.markdown(f'<div class="log-container">{"".join(log_lines)}</div>', unsafe_allow_html=True)
    else:
        st.info("Execution log will appear here after running BFS or DFS.")

# ----------------- TAB 5: COURSE OUTCOME MAPPING -----------------
with tab_co:
    st.markdown("### Course Outcome (CO) Mapping & Theoretical Foundations")

    st.markdown(
        """
        ##### **CO1 — Stack and Queue Data Structures**
        - **Breadth-First Search (BFS):** Operates on an explicit **FIFO Queue** (`collections.deque`). Discovered nodes are enqueued at the rear; nodes are explored from the front. Guarantees level-order exploration and minimum hop routing in unweighted graphs.
        - **Depth-First Search (DFS):** Operates on an explicit **LIFO Stack** (`list`). Deepest unvisited branch is prioritized. Pushes neighbors onto the stack top, pops from the top, and backtracks upon reaching dead ends.
        - **Real-Time Inspection:** Live front/rear and top/bottom pointers, push/pop/enqueue/dequeue counts, and maximum structure size.

        ##### **CO2 — Dynamic Data Structures**
        - **Dynamic Graph Manipulation:** Add and remove routers (vertices) and connections (edges) on the fly.
        - **Live Synchronization:** Dynamic updating of adjacency lists, adjacency matrices, and connectivity analysis without application restarts.
        - **Integrity Validation:** Prevents duplicate vertices, duplicate links, and invalid IDs. Deleting a router automatically cascades to remove its incident links.

        ##### **CO5 — Graph Structures, Traversal & Routing**
        - **Graph Representations:** Dual representation using Adjacency List and Adjacency Matrix.
        - **Routing & Packet Transmission:** Discovered routes are converted into step-by-step packet transmission hops with reachability detection and offline router avoidance.
        - **Complexity Analysis:**
          - **Time Complexity:** $O(V + E)$ for both BFS and DFS when implemented with an adjacency list, as each vertex is processed once and each incident edge is examined.
          - **Space Complexity:** $O(V)$ auxiliary space for tracking visited vertices, queue/stack structures, and parent pointers.
        """
    )


# -------------------------------------------------------------
# AUTO-PLAY / PACKET ANIMATION RUNNER
# -------------------------------------------------------------
if st.session_state.get("auto_play", False) and sim_res and sim_res.steps:
    if st.session_state.step_index < len(sim_res.steps) - 1:
        time.sleep(speed_delay)
        st.session_state.step_index += 1
        st.rerun()
    else:
        st.session_state.auto_play = False
        st.rerun()

if st.session_state.get("packet_play", False) and sim_res and sim_res.success and sim_res.path:
    if st.session_state.packet_hop < len(sim_res.path) - 1:
        time.sleep(speed_delay)
        st.session_state.packet_hop += 1
        st.rerun()
    else:
        st.session_state.packet_play = False
        st.rerun()
