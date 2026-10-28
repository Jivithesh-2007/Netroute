"""
views.py — Dedicated view components for NetRoute navigation sections.
Implements the 11 modular views:
1. Dashboard
2. Topology Studio
3. Traversal Simulator
4. BFS vs DFS Comparison
5. Data Structures Inspector
6. Traversal Tree
7. Routing Table Simulator
8. Network Analysis
9. Simulation History
10. Import / Export
11. Settings / Help
"""

import json
from typing import Dict, Any, List, Set, Tuple, Optional
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from network import Graph, validate_router_id
from algorithms import (
    bfs, dfs, dijkstra, linear_search, binary_search, bubble_sort, insertion_sort,
    build_traversal_tree, compare_bfs_dfs, compare_routing_strategies,
    find_bridges, find_articulation_points, simulate_failure,
    generate_benchmark_graph, run_benchmark_suite,
    generate_simulation_report, generate_comparison_report
)
from report import (
    export_simulation_metrics_csv, export_comparison_metrics_csv,
    export_resilience_csv, export_failure_scenario_csv, export_benchmark_csv
)
import simulation as sim
from visualizer import (
    build_network_figure, build_traversal_tree_figure, build_algo_result_figure,
    render_plotly, export_figure_png
)
from theme import (
    render_path_pills, render_step_card,
    PRIMARY, PRIMARY_DARK, CYAN, PURPLE, SUCCESS, WARNING, ERROR, TEXT_MAIN, TEXT_MUTED, BORDER
)


def get_adaptive_datasets(graph: Graph) -> Tuple[List[str], List[str]]:
    """Derives sorted and authentically unsorted router datasets dynamically from active topology."""
    nodes = sorted(list(graph.routers.keys()))
    if not nodes:
        return [], []
    n = len(nodes)
    if n <= 2:
        unsorted_list = list(reversed(nodes))
    else:
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


# =============================================================================
# 1. DASHBOARD VIEW
# =============================================================================
def render_dashboard(graph: Graph):
    st.markdown("## Network Dashboard")
    st.markdown("*Real-time status overview of active network topology, connectivity metrics, and simulation state.*")

    summary = graph.get_summary()
    sim_status = sim.get_simulation_status()
    sim_res = st.session_state.get("sim_res")

    # Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="metric-card" style="border-top:3px solid {PRIMARY};">'
            f'<div class="metric-card-label">Active Routers</div>'
            f'<div class="metric-card-val">{summary["total_routers"]}</div>'
            f'<div style="font-size:0.80rem; color:{TEXT_MUTED};">{summary["online_routers"]} Online | {summary["offline_routers"]} Offline</div>'
            f'</div>', unsafe_allow_html=True
        )
    with c2:
        failed_count = len(graph.failed_edges)
        active_count = summary["total_edges"] - failed_count
        st.markdown(
            f'<div class="metric-card" style="border-top:3px solid {CYAN};">'
            f'<div class="metric-card-label">Transmission Links</div>'
            f'<div class="metric-card-val">{summary["total_edges"]}</div>'
            f'<div style="font-size:0.80rem; color:{TEXT_MUTED};">{active_count} Active | {failed_count} Severed</div>'
            f'</div>', unsafe_allow_html=True
        )
    with c3:
        conn_text = "Fully Connected" if summary["is_connected"] else f"{summary['component_count']} Subnets (Partitioned)"
        conn_color = SUCCESS if summary["is_connected"] else WARNING
        st.markdown(
            f'<div class="metric-card" style="border-top:3px solid {conn_color};">'
            f'<div class="metric-card-label">Topology Connectivity</div>'
            f'<div class="metric-card-val" style="font-size:1.15rem; color:{conn_color};">{conn_text}</div>'
            f'<div style="font-size:0.80rem; color:{TEXT_MUTED};">Preset: {st.session_state.get("selected_preset", "custom").title()}</div>'
            f'</div>', unsafe_allow_html=True
        )
    with c4:
        status_color = SUCCESS if sim_status == "Completed" else (PRIMARY if sim_status == "Running" else TEXT_MUTED)
        route_info = ""
        if sim_res and sim_res.get("success"):
            route_info = f"{sim_res.get('hops', 0)} hops | {len(sim_res.get('visited', []))} visited"
        elif sim_res and not sim_res.get("success"):
            route_info = "Destination unreachable"
        else:
            route_info = "Ready to simulate"
        st.markdown(
            f'<div class="metric-card" style="border-top:3px solid {status_color};">'
            f'<div class="metric-card-label">Simulation Engine</div>'
            f'<div class="metric-card-val" style="font-size:1.20rem; color:{status_color};">{sim_status}</div>'
            f'<div style="font-size:0.80rem; color:{TEXT_MUTED};">{route_info}</div>'
            f'</div>', unsafe_allow_html=True
        )

    st.write("")

    # Topology Overview Figure
    st.markdown("### Active Network Topology")
    active_state = sim.get_active_state(graph)
    src_id = st.session_state.get("source_id", "N1")
    dst_id = st.session_state.get("dest_id", "N7")
    fig = build_network_figure(graph, active_state, src_id, dst_id, height=430)
    render_plotly(fig, key="dashboard_graph")

    # Quick Navigation Launchers
    st.markdown("### Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("Topology Studio", width="stretch", key="dash_btn_topo"):
            st.session_state["nav_page"] = "Topology Studio"
            st.rerun()
    with qa2:
        if st.button("Traversal Simulator", width="stretch", key="dash_btn_sim", type="primary"):
            st.session_state["nav_page"] = "Traversal Simulator"
            st.rerun()
    with qa3:
        if st.button("BFS vs DFS Comparison", width="stretch", key="dash_btn_cmp"):
            st.session_state["nav_page"] = "BFS vs DFS Comparison"
            st.rerun()
    with qa4:
        if st.button("Routing Table Simulator", width="stretch", key="dash_btn_rt"):
            st.session_state["nav_page"] = "Routing Table Simulator"
            st.rerun()

    st.write("")

    # Overview Tables in 2 columns
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown("#### Routers Inventory")
        if graph.routers:
            r_rows = []
            for rid in sorted(graph.routers.keys()):
                r = graph.routers[rid]
                r_rows.append({
                    "ID": r.id,
                    "Name": r.name,
                    "Status": "ONLINE" if r.is_online else "OFFLINE",
                    "Degree": len(graph.adjacency.get(rid, [])),
                    "Position": f"({r.x}, {r.y})"
                })
            st.dataframe(pd.DataFrame(r_rows), width="stretch", hide_index=True)
        else:
            st.info("No routers present in topology.")

    with t_col2:
        st.markdown("#### Transmission Links")
        edges = graph.get_edges()
        if edges:
            e_rows = []
            for u, v in edges:
                e_rows.append({
                    "Link": f"{u} <—> {v}",
                    "Weight / Metric": graph.get_weight(u, v),
                    "State": "ACTIVE" if graph.is_edge_active(u, v) else "SEVERED (Failed)"
                })
            st.dataframe(pd.DataFrame(e_rows), width="stretch", hide_index=True)
        else:
            st.info("No connections present in topology.")


# =============================================================================
# 2. TOPOLOGY STUDIO VIEW
# =============================================================================
def render_topology_studio(graph: Graph):
    st.markdown("## Topology Studio")
    st.markdown("*Interactive graph editor: add, delete, rename, and reposition routers; configure link costs and simulate link failures.*")

    router_keys = sorted(list(graph.routers.keys()))
    src_id = st.session_state.get("source_id", router_keys[0] if router_keys else "N1")
    dst_id = st.session_state.get("dest_id", router_keys[-1] if router_keys else "N7")

    # Top Toolbar
    tb1, tb2, tb3, tb4 = st.columns([2.5, 1.2, 1.2, 1.5])
    try:
        from topology_registry import get_topology_registry
        reg = get_topology_registry()
        preset_options = reg.get_preset_options()
        if not preset_options:
            raise ValueError("Empty registry")
    except Exception:
        preset_options = {
            "reference": "Reference 7-Node WAN",
            "ring": "Ring Network (Cyclic)",
            "mesh": "Mesh Network",
            "disconnected": "Disconnected Subnets",
            "direct": "Linear Chain",
            "multi_route": "Multi-Path Spine-Leaf",
            "offline_router": "Offline Router Topology"
        }

    with tb1:
        current_preset = st.session_state.get("selected_preset", "reference")
        if current_preset not in preset_options:
            current_preset = "reference"
        sel_preset = st.selectbox(
            "Load Topology Preset",
            options=list(preset_options.keys()),
            format_func=lambda k: preset_options[k],
            index=list(preset_options.keys()).index(current_preset),
            key="studio_preset_select"
        )
        if sel_preset != st.session_state.get("selected_preset"):
            st.session_state["selected_preset"] = sel_preset
            st.session_state["graph"] = Graph.from_preset(sel_preset)
            sim.invalidate_simulation()
            g_nodes = sorted(list(st.session_state["graph"].routers.keys()))
            st.session_state["source_id"] = g_nodes[0] if g_nodes else "N1"
            st.session_state["dest_id"] = g_nodes[-1] if g_nodes else "N7"
            st.rerun()

    with tb2:
        st.write("")
        st.write("")
        if st.button("Auto Layout", width="stretch", icon=":material/hub:", key="studio_btn_autolayout"):
            graph.auto_layout()
            st.rerun()

    with tb3:
        st.write("")
        st.write("")
        if st.button("Reset Graph", width="stretch", icon=":material/refresh:", key="studio_btn_reset"):
            st.session_state["graph"] = Graph.from_preset(st.session_state.get("selected_preset", "reference"))
            sim.invalidate_simulation()
            st.rerun()

    with tb4:
        st.write("")
        st.write("")
        confirm_clear = st.checkbox("Confirm clear", key="confirm_clear_chk")
        if st.button("Clear All", width="stretch", icon=":material/delete_forever:", key="studio_btn_clear", disabled=not confirm_clear):
            graph.clear()
            sim.invalidate_simulation()
            st.rerun()

    st.write("")

    # Studio 2-Column Split: Graph on left, Controls on right
    col_graph, col_ctrl = st.columns([1.35, 1.0])

    with col_graph:
        st.markdown("#### Live Network Diagram")
        active_state = sim.get_active_state(graph)
        fig = build_network_figure(graph, active_state, src_id, dst_id, height=480)
        render_plotly(fig, key="studio_graph")

        # Summary Bar
        summary = graph.get_summary()
        st.caption(
            f"**Graph Metrics:** {summary['total_routers']} Routers ({summary['online_routers']} online) | "
            f"{summary['total_edges']} Edges ({len(graph.failed_edges)} severed) | "
            f"Connectivity: {'Connected' if summary['is_connected'] else f'{summary['component_count']} Subnets'}"
        )

    with col_ctrl:
        tab_routers, tab_links, tab_props = st.tabs(["Routers", "Connections", "Endpoints"])

        # Tab 1: Routers
        with tab_routers:
            st.markdown("##### Add Router")
            ar_c1, ar_c2 = st.columns([1, 1.5])
            new_rid = ar_c1.text_input("Router ID", placeholder="e.g. R8", max_chars=8, key="ts_add_rid").strip().upper()
            new_rname = ar_c2.text_input("Router Name", placeholder="e.g. Core Gateway", key="ts_add_rname").strip()

            ar_c3, ar_c4, ar_c5 = st.columns([1, 1, 1.2])
            pos_x = ar_c3.number_input("X Coord", value=360.0, step=20.0, key="ts_add_x")
            pos_y = ar_c4.number_input("Y Coord", value=220.0, step=20.0, key="ts_add_y")
            with ar_c5:
                st.write("")
                st.write("")
                add_r_btn = st.button("Add Router", width="stretch", type="primary", key="ts_btn_add_router")

            if add_r_btn:
                ok_id, msg_id = validate_router_id(new_rid)
                if not ok_id:
                    st.error(msg_id)
                elif new_rid in graph.routers:
                    st.error(f"Router '{new_rid}' already exists.")
                else:
                    graph.add_router(new_rid, name=new_rname or f"Router {new_rid}", x=pos_x, y=pos_y)
                    sim.invalidate_simulation()
                    st.success(f"Added Router {new_rid}")
                    st.rerun()

            st.markdown("---")
            st.markdown("##### Manage Router")
            if router_keys:
                sel_manage_r = st.selectbox("Select Router to Edit", options=router_keys, key="ts_manage_r_select")
                r_obj = graph.routers[sel_manage_r]

                mr_c1, mr_c2 = st.columns([1.5, 1])
                renamed_name = mr_c1.text_input("Name", value=r_obj.name, key="ts_edit_name")
                if mr_c2.button("Rename", key="ts_btn_rename", width="stretch"):
                    if renamed_name.strip():
                        graph.rename_router(sel_manage_r, renamed_name)
                        st.success(f"Renamed router to '{renamed_name}'")
                        st.rerun()

                mr_c3, mr_c4 = st.columns([1, 1])
                curr_status = r_obj.is_online
                new_status_btn = mr_c3.button(
                    f"Set {'OFFLINE' if curr_status else 'ONLINE'}",
                    width="stretch",
                    key="ts_btn_toggle_status"
                )
                if new_status_btn:
                    graph.toggle_router_status(sel_manage_r)
                    sim.invalidate_simulation()
                    st.rerun()

                del_r_btn = mr_c4.button("Delete Router", width="stretch", key="ts_btn_del_r")
                if del_r_btn:
                    rem_nodes = [r for r in router_keys if r != sel_manage_r]
                    if st.session_state.get("source_id") == sel_manage_r:
                        st.session_state["source_id"] = rem_nodes[0] if rem_nodes else "N1"
                    if st.session_state.get("dest_id") == sel_manage_r:
                        st.session_state["dest_id"] = rem_nodes[-1] if rem_nodes else "N7"
                    for key_name in ["src_select", "dst_select", "ts_manage_r_select"]:
                        if key_name in st.session_state and st.session_state[key_name] == sel_manage_r:
                            del st.session_state[key_name]
                    graph.remove_router(sel_manage_r)
                    sim.invalidate_simulation()
                    st.success(f"Deleted router {sel_manage_r}")
                    st.rerun()

                # Coordinate adjustment
                st.markdown("###### Position Adjustment")
                pos_c1, pos_c2, pos_c3 = st.columns([1, 1, 1])
                edit_x = pos_c1.number_input("X", value=r_obj.x, step=15.0, key="ts_edit_x")
                edit_y = pos_c2.number_input("Y", value=r_obj.y, step=15.0, key="ts_edit_y")
                with pos_c3:
                    st.write("")
                    st.write("")
                    if st.button("Save Pos", width="stretch", key="ts_btn_save_pos"):
                        r_obj.x = edit_x
                        r_obj.y = edit_y
                        st.rerun()
            else:
                st.info("No routers to manage. Add a router above.")

        # Tab 2: Connections
        with tab_links:
            st.markdown("##### Add Connection")
            if len(router_keys) >= 2:
                ac_c1, ac_c2, ac_c3 = st.columns([1, 1, 1])
                u_node = ac_c1.selectbox("Router U", options=router_keys, index=0, key="ts_conn_u")
                v_candidates = [r for r in router_keys if r != u_node]
                v_node = ac_c2.selectbox("Router V", options=v_candidates, index=0, key="ts_conn_v")
                link_weight = ac_c3.number_input("Cost / Weight", min_value=0.0, value=1.0, step=0.5, key="ts_conn_w")

                if st.button("Add Transmission Link", width="stretch", type="primary", key="ts_btn_add_link"):
                    if v_node in graph.adjacency.get(u_node, []):
                        st.warning(f"Connection between {u_node} and {v_node} already exists.")
                    else:
                        graph.add_connection(u_node, v_node, weight=link_weight)
                        sim.invalidate_simulation()
                        st.success(f"Connected {u_node} <—> {v_node} with cost {link_weight}")
                        st.rerun()
            else:
                st.info("Need at least 2 routers to add connections.")

            st.markdown("---")
            st.markdown("##### Manage Existing Links")
            edges = graph.get_edges()
            if edges:
                edge_labels = [f"{u} <—> {v}" for u, v in edges]
                sel_edge_idx = st.selectbox("Select Link", options=list(range(len(edges))), format_func=lambda i: edge_labels[i], key="ts_edge_select")
                sel_u, sel_v = edges[sel_edge_idx]
                curr_w = graph.get_weight(sel_u, sel_v)
                curr_active = graph.is_edge_active(sel_u, sel_v)

                el_c1, el_c2, el_c3 = st.columns([1.2, 1, 1])
                new_w = el_c1.number_input("New Cost", min_value=0.0, value=curr_w, step=0.5, key="ts_edit_w")
                with el_c2:
                    st.write("")
                    st.write("")
                    if st.button("Update Cost", width="stretch", key="ts_btn_update_w"):
                        graph.set_weight(sel_u, sel_v, new_w)
                        sim.invalidate_simulation()
                        st.rerun()

                with el_c3:
                    st.write("")
                    st.write("")
                    toggle_txt = "Restore" if not curr_active else "Sever Link"
                    if st.button(toggle_txt, width="stretch", key="ts_btn_toggle_edge"):
                        graph.toggle_edge_failure(sel_u, sel_v)
                        sim.invalidate_simulation()
                        st.rerun()

                if st.button("Remove Link", width="stretch", key="ts_btn_remove_edge"):
                    graph.remove_connection(sel_u, sel_v)
                    sim.invalidate_simulation()
                    st.success(f"Removed connection ({sel_u} <—> {sel_v})")
                    st.rerun()
            else:
                st.info("No connections present in network.")

        # Tab 3: Endpoints
        with tab_props:
            st.markdown("##### Global Routing Endpoints")
            if router_keys:
                ep_c1, ep_c2 = st.columns(2)
                cur_src = st.session_state.get("source_id", router_keys[0])
                cur_dst = st.session_state.get("dest_id", router_keys[-1])
                s_idx = router_keys.index(cur_src) if cur_src in router_keys else 0
                d_idx = router_keys.index(cur_dst) if cur_dst in router_keys else len(router_keys) - 1

                new_src = ep_c1.selectbox("Source Router", options=router_keys, index=s_idx, key="ts_ep_src")
                new_dst = ep_c2.selectbox("Destination Router", options=router_keys, index=d_idx, key="ts_ep_dst")

                if new_src != st.session_state.get("source_id") or new_dst != st.session_state.get("dest_id"):
                    st.session_state["source_id"] = new_src
                    st.session_state["dest_id"] = new_dst
                    sim.invalidate_simulation()
                    st.rerun()

                st.caption(f"Packets will route from **{new_src}** ({graph.routers[new_src].name}) to **{new_dst}** ({graph.routers[new_dst].name}).")


# =============================================================================
# 3. TRAVERSAL SIMULATOR VIEW
# =============================================================================
def render_traversal_simulator(graph: Graph):
    st.markdown("## Traversal Simulator")
    st.markdown("*Step-by-step interactive simulation of network packet discovery using BFS (FIFO Queue) or DFS (LIFO Stack).*")

    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning("Network graph is empty. Please add routers in Topology Studio or load a preset.")
        return

    # Configuration bar
    cfg1, cfg2, cfg3, cfg4, cfg5 = st.columns([1.5, 1.5, 2, 1.2, 1])

    cur_src = st.session_state.get("source_id", router_keys[0])
    cur_dst = st.session_state.get("dest_id", router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    s_idx = router_keys.index(cur_src) if cur_src in router_keys else 0
    d_idx = router_keys.index(cur_dst) if cur_dst in router_keys else (len(router_keys) - 1)

    with cfg1:
        sel_src = st.selectbox("Source", options=router_keys, index=s_idx, key="sim_sel_src")
    with cfg2:
        sel_dst = st.selectbox("Destination", options=router_keys, index=d_idx, key="sim_sel_dst")
    with cfg3:
        algo_options = ["BFS (Breadth-First Search)", "DFS (Depth-First Search)", "Dijkstra (Weighted Shortest Path)"]
        cur_algo = st.session_state.get("selected_algo", algo_options[0])
        if "DIJKSTRA" in str(cur_algo).upper():
            a_idx = 2
        elif "DFS" in str(cur_algo).upper():
            a_idx = 1
        else:
            a_idx = 0
        sel_algo = st.selectbox("Algorithm", options=algo_options, index=a_idx, key="sim_sel_algo")
    with cfg4:
        st.write("")
        st.write("")
        run_btn = st.button("Run Simulation", width="stretch", type="primary", key="sim_btn_run")
    with cfg5:
        st.write("")
        st.write("")
        reset_btn = st.button("Reset", width="stretch", key="sim_btn_reset")

    if sel_src != cur_src or sel_dst != cur_dst:
        st.session_state["source_id"] = sel_src
        st.session_state["dest_id"] = sel_dst
        sim.invalidate_simulation()

    if sel_algo != cur_algo:
        st.session_state["selected_algo"] = sel_algo
        sim.invalidate_simulation()

    if reset_btn:
        sim.reset_simulation()
        st.rerun()

    if run_btn:
        sim.execute_routing(graph, sel_algo, sel_src, sel_dst)
        st.rerun()

    sim_res = st.session_state.get("sim_res")

    if not sim_res:
        st.info("Select parameters and click **Run Simulation** to generate the step-by-step traversal trace.")
        active_state = sim.get_active_state(graph)
        fig = build_network_figure(graph, active_state, sel_src, sel_dst, height=430)
        render_plotly(fig, key="sim_graph_idle")
        return

    # Simulation Controls & Scrubbing
    steps = sim_res.get("steps", [])
    total_steps = len(steps)
    step_idx = st.session_state.get("step_idx", 0)

    st.write("")

    ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4, ctrl_c5, ctrl_c6 = st.columns([1, 1, 1, 1, 3, 1.2])
    with ctrl_c1:
        if st.button("|<<", width="stretch", key="sim_btn_first", help="Jump to Step 1"):
            sim.first_step()
            st.rerun()
    with ctrl_c2:
        if st.button("< Prev", width="stretch", key="sim_btn_prev", help="Previous Step"):
            sim.step_backward()
            st.rerun()
    with ctrl_c3:
        if st.button("Next >", width="stretch", key="sim_btn_next", help="Next Step"):
            sim.step_forward()
            st.rerun()
    with ctrl_c4:
        if st.button(">>|", width="stretch", key="sim_btn_last", help="Jump to End"):
            sim.last_step()
            st.rerun()
    with ctrl_c5:
        if total_steps > 1:
            scrub_step = st.slider(
                "Execution Step",
                min_value=0,
                max_value=total_steps - 1,
                value=step_idx,
                format="Step %d",
                key="sim_scrubber",
                label_visibility="collapsed"
            )
            if scrub_step != step_idx:
                sim.jump_to_step(scrub_step)
                st.rerun()
        else:
            st.caption("Single step event.")
    with ctrl_c6:
        st.caption(f"**Step {step_idx + 1} of {max(1, total_steps)}**")

    # Main Visualizer Section: Graph on Left, Data Structure on Right
    v_col1, v_col2 = st.columns([1.4, 1.0])

    active_state = sim.get_active_state(graph)
    current_step = active_state.get("step")

    with v_col1:
        fig = build_network_figure(graph, active_state, sel_src, sel_dst, height=440)
        render_plotly(fig, key="sim_graph_active")

        # Color Legend
        st.markdown(
            "<div style='display:flex; flex-wrap:wrap; gap:12px; font-size:0.78rem; color:#475569; margin-top:4px;'>"
            "<span><span style='color:#10B981;'>●</span> Source</span>"
            "<span><span style='color:#F59E0B;'>●</span> Destination</span>"
            "<span><span style='color:#7C3AED;'>●</span> Active Processing</span>"
            "<span><span style='color:#0891B2;'>●</span> Discovered</span>"
            "<span><span style='color:#38BDF8;'>●</span> Visited</span>"
            "<span><span style='color:#059669;'>●</span> Discovered Route</span>"
            "<span><span style='color:#94A3B8;'>●</span> Offline</span>"
            "</div>",
            unsafe_allow_html=True
        )

    with v_col2:
        is_bfs = "BFS" in sim_res.get("algorithm", "")
        is_dijkstra = "Dijkstra" in sim_res.get("algorithm", "")

        # Live Data Structure Box
        if is_bfs:
            ds_title = "FIFO Queue (BFS)"
            ds_badge = "FRONT -> REAR"
        elif is_dijkstra:
            ds_title = "Min-Priority Queue (Dijkstra)"
            ds_badge = "MIN DIST -> REAR"
        else:
            ds_title = "LIFO Stack (DFS)"
            ds_badge = "TOP -> BOTTOM"

        st.markdown(
            f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>"
            f"<span style='font-weight:700; color:{PRIMARY};'>{ds_title}</span>"
            f"<span style='background:#E2E8F0; color:#475569; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>{ds_badge}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        struct_items = current_step.get("structure", []) if current_step else []
        if struct_items:
            pill_html = " ".join([f"<span class='path-pill'>{item}</span>" for item in struct_items])
            st.markdown(f"<div class='path-pill-container'>{pill_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#1E293B; color:#94A3B8; padding:10px 14px; border-radius:8px; font-style:italic;'>[Structure is Empty]</div>", unsafe_allow_html=True)

        # Structure Metrics
        sm1, sm2, sm3 = st.columns(3)
        if is_bfs or is_dijkstra:
            sm1.metric("Enqueues", current_step.get("enqueues", 0) if current_step else 0)
            sm2.metric("Dequeues", current_step.get("dequeues", 0) if current_step else 0)
            sm3.metric("Peak Structure", sim_res.get("max_structure", 0))
        else:
            sm1.metric("Pushes", current_step.get("pushes", 0) if current_step else 0)
            sm2.metric("Pops", current_step.get("pops", 0) if current_step else 0)
            sm3.metric("Peak Stack", sim_res.get("max_structure", 0))

        # Current Step Card with Explainable Event Rationale
        if current_step:
            nbr_str = f"<b>Neighbor Examined:</b> {current_step.get('neighbor')} (Status: {current_step.get('neighbor_status', 'examined')})" if current_step.get("neighbor") else ""
            route_str = " -> ".join(current_step.get("current_path", [])) if current_step.get("current_path") else ""
            card_color = PRIMARY if is_bfs else (CYAN if is_dijkstra else PURPLE)
            st.markdown(
                render_step_card(
                    step_num=current_step.get("step", step_idx + 1),
                    operation=current_step.get("operation", "EXPLORE"),
                    description=current_step.get("description", ""),
                    color=card_color,
                    why=current_step.get("why", ""),
                    neighbor_info=nbr_str,
                    route_info=route_str
                ),
                unsafe_allow_html=True
            )

        # Hop-by-Hop Packet Forwarding Controls
        if sim_res.get("success") and sim_res.get("path"):
            st.markdown("##### Packet Forwarding Animation")
            pf_c1, pf_c2 = st.columns(2)
            if pf_c1.button("Step Packet Forward", width="stretch", key="sim_btn_pkt_step"):
                sim.packet_step_forward()
                st.rerun()
            if pf_c2.button("Reset Packet", width="stretch", key="sim_btn_pkt_reset"):
                sim.reset_packet()
                st.rerun()
            st.caption(f"**Status:** {active_state.get('packet_status', '')}")

    st.write("")

    # Traversal Completion Card & Results
    st.markdown("### Traversal Results & Engineering Metrics")
    res_c1, res_c2 = st.columns([1.5, 1])

    with res_c1:
        if sim_res.get("success"):
            st.success(f"Route Discovered: {sim_res.get('message', '')}")
            st.markdown(render_path_pills(sim_res.get("path", [])), unsafe_allow_html=True)
        else:
            st.error(f"Routing Failed: {sim_res.get('message', 'Destination unreachable.')}")

        cost_line = f"• <b>Total Path Cost:</b> <code>{sim_res.get('path_cost', 0.0):.1f}</code><br>" if "path_cost" in sim_res else ""
        st.markdown(
            f"<div style='font-size:0.88rem; color:#334155; line-height:1.7;'>"
            f"• <b>Discovered Path:</b> <code>{' -> '.join(sim_res.get('path', [])) if sim_res.get('path') else 'None'}</code><br>"
            f"• <b>Hop Count:</b> <code>{sim_res.get('hops', 0)} hops</code><br>"
            f"{cost_line}"
            f"• <b>Traversal Order:</b> <code>{', '.join(sim_res.get('visited', []))}</code><br>"
            f"• <b>Explored Connections:</b> <code>{sim_res.get('explored_edges_count', 0)}</code><br>"
            f"• <b>Execution Time:</b> <code>{sim_res.get('execution_time_ms', 0.0):.3f} ms</code>"
            f"</div>",
            unsafe_allow_html=True
        )

    with res_c2:
        st.markdown("##### Theoretical Complexity")
        t_comp = "O((V + E) log V)" if is_dijkstra else "O(V + E)"
        t_desc = (
            "Dijkstra extracts minimum tentative distances using a binary heap priority queue."
            if is_dijkstra else
            "Each online router is queued/stacked at most once, and each incident link is examined at most twice."
        )
        st.markdown(
            f"""
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:14px; font-size:0.86rem;">
                <b>Time Complexity:</b> <code>{t_comp}</code><br>
                <span style="color:#64748B;">{t_desc}</span><br><br>
                <b>Auxiliary Space:</b> <code>O(V)</code><br>
                <span style="color:#64748B;">For the visited set, parent pointers, and traversal frontier data structure.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        full_rep = generate_simulation_report(graph, sim_res, sel_src, sel_dst, algo_name=sel_algo)
        report_json = json.dumps(full_rep, indent=2)
        report_csv = export_simulation_metrics_csv(full_rep)

        dl_c1, dl_c2, dl_c3 = st.columns(3)
        with dl_c1:
            st.download_button(
                label="JSON Report",
                data=report_json,
                file_name=f"netroute_report_{sel_algo[:3].lower()}_{sel_src}_{sel_dst}.json",
                mime="application/json",
                width="stretch",
                key="sim_dl_report_btn"
            )
        with dl_c2:
            st.download_button(
                label="CSV Metrics",
                data=report_csv,
                file_name=f"netroute_metrics_{sel_algo[:3].lower()}_{sel_src}_{sel_dst}.csv",
                mime="text/csv",
                width="stretch",
                key="sim_dl_csv_btn"
            )
        with dl_c3:
            png_bytes = export_figure_png(fig)
            if png_bytes:
                st.download_button(
                    label="Graph PNG",
                    data=png_bytes,
                    file_name=f"netroute_graph_{sel_algo[:3].lower()}_{sel_src}_{sel_dst}.png",
                    mime="image/png",
                    width="stretch",
                    key="sim_dl_png_btn"
                )
            else:
                st.caption("PNG export requires Kaleido.")


# =============================================================================
# 4. BFS VS. DFS COMPARISON SIMULATOR
# =============================================================================
def render_bfs_dfs_comparison(graph: Graph):
    st.markdown("## BFS vs. DFS Dual Simulation & Comparison")
    st.markdown("*Synchronized, side-by-side execution of Breadth-First Search and Depth-First Search on the identical network topology snapshot.*")

    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning("Network graph is empty. Please load a topology preset in Topology Studio.")
        return

    cur_src = st.session_state.get("source_id", router_keys[0])
    cur_dst = st.session_state.get("dest_id", router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    s_idx = router_keys.index(cur_src) if cur_src in router_keys else 0
    d_idx = router_keys.index(cur_dst) if cur_dst in router_keys else (len(router_keys) - 1)

    c_bar1, c_bar2, c_bar3, c_bar4 = st.columns([2, 2, 1.5, 1.2])
    with c_bar1:
        sel_src = st.selectbox("Source Router", options=router_keys, index=s_idx, key="cmp_bar_src")
    with c_bar2:
        sel_dst = st.selectbox("Destination Router", options=router_keys, index=d_idx, key="cmp_bar_dst")
    with c_bar3:
        st.write("")
        st.write("")
        run_both = st.button("Run Both Algorithms", width="stretch", type="primary", key="cmp_btn_run_both")
    with c_bar4:
        st.write("")
        st.write("")
        reset_both = st.button("Reset Both", width="stretch", key="cmp_btn_reset_both")

    if sel_src != cur_src or sel_dst != cur_dst:
        st.session_state["source_id"] = sel_src
        st.session_state["dest_id"] = sel_dst
        st.session_state["cmp_res"] = None
        st.session_state["cmp_step_idx"] = 0

    if reset_both:
        st.session_state["cmp_res"] = None
        st.session_state["cmp_step_idx"] = 0
        st.rerun()

    if run_both or st.session_state.get("cmp_res") is None:
        sim.execute_dual_comparison(graph, sel_src, sel_dst)

    cmp_res = st.session_state.get("cmp_res")
    if not cmp_res:
        st.info("Click **Run Both Algorithms** to initiate synchronized comparison.")
        return

    bfs_res = cmp_res["bfs"]
    dfs_res = cmp_res["dfs"]
    bfs_steps = bfs_res.get("steps", [])
    dfs_steps = dfs_res.get("steps", [])
    max_steps = max(len(bfs_steps), len(dfs_steps))
    cmp_idx = st.session_state.get("cmp_step_idx", 0)

    # Synchronized Playback Controls
    st.write("")
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns([1, 1, 1, 1, 3, 1.2])
    with sc1:
        if st.button("|<<", width="stretch", key="cmp_nav_first"):
            sim.cmp_first_step()
            st.rerun()
    with sc2:
        if st.button("< Prev", width="stretch", key="cmp_nav_prev"):
            sim.cmp_step_backward()
            st.rerun()
    with sc3:
        if st.button("Next >", width="stretch", key="cmp_nav_next"):
            sim.cmp_step_forward()
            st.rerun()
    with sc4:
        if st.button(">>|", width="stretch", key="cmp_nav_last"):
            sim.cmp_last_step()
            st.rerun()
    with sc5:
        if max_steps > 1:
            scrub_val = st.slider(
                "Synchronized Step",
                min_value=0,
                max_value=max_steps - 1,
                value=min(cmp_idx, max_steps - 1),
                format="Step %d",
                key="cmp_scrubber",
                label_visibility="collapsed"
            )
            if scrub_val != cmp_idx:
                sim.cmp_jump_to_step(scrub_val)
                st.rerun()
        else:
            st.caption("Single step comparison.")
    with sc6:
        st.caption(f"**Step {cmp_idx + 1} of {max(1, max_steps)}**")

    # Side-by-Side Visual Traversal
    bfs_step_idx = min(cmp_idx, len(bfs_steps) - 1) if bfs_steps else 0
    dfs_step_idx = min(cmp_idx, len(dfs_steps) - 1) if dfs_steps else 0

    bfs_visual = sim.get_step_visual_state(graph, bfs_res, bfs_step_idx)
    dfs_visual = sim.get_step_visual_state(graph, dfs_res, dfs_step_idx)

    st.write("")
    col_bfs, col_dfs = st.columns(2)

    with col_bfs:
        st.markdown(
            "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
            "<span style='font-weight:700; color:#2563EB; font-size:1.05rem;'>Breadth-First Search (BFS)</span>"
            "<span style='background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>FIFO QUEUE</span>"
            "</div>",
            unsafe_allow_html=True
        )
        fig_bfs = build_network_figure(graph, bfs_visual, sel_src, sel_dst, height=390, title="BFS Traversal Frontier")
        render_plotly(fig_bfs, key="cmp_graph_bfs")

        # BFS Queue live box
        bfs_curr_step = bfs_visual.get("step")
        bfs_struct = bfs_curr_step.get("structure", []) if bfs_curr_step else []
        if bfs_struct:
            bfs_pills = " ".join([f"<span class='path-pill'>{n}</span>" for n in bfs_struct])
            st.markdown(f"<div class='path-pill-container'>{bfs_pills}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#1E293B; color:#94A3B8; padding:8px 12px; border-radius:6px; font-size:0.85rem;'>[Queue Empty]</div>", unsafe_allow_html=True)

        if bfs_curr_step:
            st.caption(f"**Step {bfs_step_idx + 1}:** {bfs_curr_step.get('description', '')}")

    with col_dfs:
        st.markdown(
            "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
            "<span style='font-weight:700; color:#7C3AED; font-size:1.05rem;'>Depth-First Search (DFS)</span>"
            "<span style='background:#EDE9FE; color:#5B21B6; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>LIFO STACK</span>"
            "</div>",
            unsafe_allow_html=True
        )
        fig_dfs = build_network_figure(graph, dfs_visual, sel_src, sel_dst, height=390, title="DFS Traversal Frontier")
        render_plotly(fig_dfs, key="cmp_graph_dfs")

        # DFS Stack live box
        dfs_curr_step = dfs_visual.get("step")
        dfs_struct = dfs_curr_step.get("structure", []) if dfs_curr_step else []
        if dfs_struct:
            dfs_pills = " ".join([f"<span class='path-pill'>{n}</span>" for n in dfs_struct])
            st.markdown(f"<div class='path-pill-container'>{dfs_pills}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#1E293B; color:#94A3B8; padding:8px 12px; border-radius:6px; font-size:0.85rem;'>[Stack Empty]</div>", unsafe_allow_html=True)

        if dfs_curr_step:
            st.caption(f"**Step {dfs_step_idx + 1}:** {dfs_curr_step.get('description', '')}")

    st.write("")

    # Comparative Metrics Table
    st.markdown("### Comparative Performance Metrics")
    metrics_data = [
        {"Metric": "Discovered Path", "BFS (Breadth-First)": " -> ".join(bfs_res.get("path", [])) or "No path", "DFS (Depth-First)": " -> ".join(dfs_res.get("path", [])) or "No path"},
        {"Metric": "Hop Count (Hops)", "BFS (Breadth-First)": f"{bfs_res.get('hops', 0)} hops (Guaranteed Shortest)", "DFS (Depth-First)": f"{dfs_res.get('hops', 0)} hops"},
        {"Metric": "Hop Delta", "BFS (Breadth-First)": "0 (Baseline Minimum)", "DFS (Depth-First)": f"+{cmp_res.get('hop_delta', 0)} extra hops" if cmp_res.get('hop_delta', 0) > 0 else "0 (Identical hops)"},
        {"Metric": "Routers Visited", "BFS (Breadth-First)": f"{len(bfs_res.get('visited', []))} of {len(graph.routers)}", "DFS (Depth-First)": f"{len(dfs_res.get('visited', []))} of {len(graph.routers)}"},
        {"Metric": "Explored Edges", "BFS (Breadth-First)": str(bfs_res.get("explored_edges_count", 0)), "DFS (Depth-First)": str(dfs_res.get("explored_edges_count", 0))},
        {"Metric": "Data Structure Operations", "BFS (Breadth-First)": f"{bfs_res.get('total_enqueues', 0)} Enqueues / {bfs_res.get('total_dequeues', 0)} Dequeues", "DFS (Depth-First)": f"{dfs_res.get('total_pushes', 0)} Pushes / {dfs_res.get('total_pops', 0)} Pops"},
        {"Metric": "Peak Frontier Depth", "BFS (Breadth-First)": f"{bfs_res.get('max_structure', 0)} (Max Queue)", "DFS (Depth-First)": f"{dfs_res.get('max_structure', 0)} (Max Stack)"},
        {"Metric": "Total Simulation Events", "BFS (Breadth-First)": str(len(bfs_steps)), "DFS (Depth-First)": str(len(dfs_steps))},
        {"Metric": "Execution Time", "BFS (Breadth-First)": f"{bfs_res.get('execution_time_ms', 0.0):.3f} ms", "DFS (Depth-First)": f"{dfs_res.get('execution_time_ms', 0.0):.3f} ms"},
        {"Metric": "Theoretical Time Complexity", "BFS (Breadth-First)": "O(V + E)", "DFS (Depth-First)": "O(V + E)"},
        {"Metric": "Theoretical Space Complexity", "BFS (Breadth-First)": "O(V)", "DFS (Depth-First)": "O(V)"}
    ]
    st.dataframe(pd.DataFrame(metrics_data), width="stretch", hide_index=True)

    # Engineering Verdict
    st.markdown("### Engineering Verdict")
    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-left:5px solid {cmp_res.get('verdict_color', PRIMARY)}; border-radius:8px; padding:16px; margin-bottom:12px;">
            <div style="font-weight:700; font-size:1.1rem; color:{cmp_res.get('verdict_color', PRIMARY)}; margin-bottom:4px;">
                {cmp_res.get('verdict_title', '')}
            </div>
            <div style="font-size:0.92rem; color:{TEXT_MAIN}; line-height:1.5;">
                {cmp_res.get('verdict_summary', '')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3-Way Routing Strategy Comparison Expander (BFS vs DFS vs Dijkstra)
    with st.expander("Route Strategy Comparison (BFS vs. DFS vs. Dijkstra)", expanded=False):
        st.markdown("*Evaluation of unweighted shortest hops (BFS), branch exploration (DFS), and weighted least-cost paths (Dijkstra).*")
        strat_res = compare_routing_strategies(graph, sel_src, sel_dst)
        b_run = strat_res["bfs"]
        d_run = strat_res["dfs"]
        dj_run = strat_res["dijkstra"]

        strat_table = [
            {"Property": "Guaranteed Property", "BFS (Breadth-First)": "Minimum Hops (Unweighted)", "DFS (Depth-First)": "Deep Branch Exploration", "Dijkstra (Priority Queue)": "Minimum Total Cost (Weighted)"},
            {"Property": "Discovered Path", "BFS (Breadth-First)": " -> ".join(b_run.get("path", [])) or "No path", "DFS (Depth-First)": " -> ".join(d_run.get("path", [])) or "No path", "Dijkstra (Priority Queue)": " -> ".join(dj_run.get("path", [])) or "No path"},
            {"Property": "Hop Count", "BFS (Breadth-First)": f"{b_run.get('hops', 0)} hops", "DFS (Depth-First)": f"{d_run.get('hops', 0)} hops", "Dijkstra (Priority Queue)": f"{dj_run.get('hops', 0)} hops"},
            {"Property": "Total Accumulated Cost", "BFS (Breadth-First)": f"{b_run.get('path_cost', 0.0):.1f}", "DFS (Depth-First)": f"{d_run.get('path_cost', 0.0):.1f}", "Dijkstra (Priority Queue)": f"{dj_run.get('path_cost', 0.0):.1f} (Least Cost)"},
            {"Property": "Routers Visited", "BFS (Breadth-First)": str(len(b_run.get("visited", []))), "DFS (Depth-First)": str(len(d_run.get("visited", []))), "Dijkstra (Priority Queue)": str(len(dj_run.get("visited", [])))},
            {"Property": "Execution Time (ms)", "BFS (Breadth-First)": f"{b_run.get('execution_time_ms', 0.0):.3f} ms", "DFS (Depth-First)": f"{d_run.get('execution_time_ms', 0.0):.3f} ms", "Dijkstra (Priority Queue)": f"{dj_run.get('execution_time_ms', 0.0):.3f} ms"},
            {"Property": "Theoretical Time Complexity", "BFS (Breadth-First)": "O(V + E)", "DFS (Depth-First)": "O(V + E)", "Dijkstra (Priority Queue)": "O((V + E) log V)"},
            {"Property": "Auxiliary Space Complexity", "BFS (Breadth-First)": "O(V)", "DFS (Depth-First)": "O(V)", "Dijkstra (Priority Queue)": "O(V)"}
        ]
        st.dataframe(pd.DataFrame(strat_table), width="stretch", hide_index=True)
        st.info("Notice: BFS optimizes hop count across unweighted edges, whereas Dijkstra minimizes cumulative link weights. DFS does not guarantee either optimality property.")

    # Combined Multi-Format Report Downloads
    comp_rep = generate_comparison_report(graph, cmp_res, sel_src, sel_dst)
    report_json = json.dumps(comp_rep, indent=2)
    report_csv = export_comparison_metrics_csv(comp_rep)

    dl_c1, dl_c2, dl_c3, dl_c4 = st.columns(4)
    with dl_c1:
        st.download_button(
            label="Download JSON Report",
            data=report_json,
            file_name=f"netroute_comparison_bfs_vs_dfs_{sel_src}_{sel_dst}.json",
            mime="application/json",
            width="stretch",
            key="cmp_dl_report_btn"
        )
    with dl_c2:
        st.download_button(
            label="Download CSV Metrics",
            data=report_csv,
            file_name=f"netroute_comparison_{sel_src}_{sel_dst}.csv",
            mime="text/csv",
            width="stretch",
            key="cmp_dl_csv_btn"
        )
    with dl_c3:
        bfs_png = export_figure_png(fig_bfs)
        if bfs_png:
            st.download_button(
                label="BFS Graph PNG",
                data=bfs_png,
                file_name=f"netroute_bfs_graph_{sel_src}_{sel_dst}.png",
                mime="image/png",
                width="stretch",
                key="cmp_dl_bfs_png"
            )
        else:
            st.caption("BFS PNG requires Kaleido.")
    with dl_c4:
        dfs_png = export_figure_png(fig_dfs)
        if dfs_png:
            st.download_button(
                label="DFS Graph PNG",
                data=dfs_png,
                file_name=f"netroute_dfs_graph_{sel_src}_{sel_dst}.png",
                mime="image/png",
                width="stretch",
                key="cmp_dl_dfs_png"
            )
        else:
            st.caption("DFS PNG requires Kaleido.")



# =============================================================================
# 4B. NETWORK FAILURE LAB VIEW
# =============================================================================
def render_network_failure_lab(graph: Graph):
    st.markdown("## Network Failure Lab")
    st.markdown("*Interactive sandbox for multi-router and link failure simulation on a reversible scenario clone, measuring reachability and route divergence.*")

    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning("Network graph is empty. Please configure routers first.")
        return

    edges = graph.get_edges()
    edge_str_map = {f"{u} <—> {v}": (u, v) for u, v in edges}
    edge_options = list(edge_str_map.keys())

    cur_src = st.session_state.get("source_id", router_keys[0])
    cur_dst = st.session_state.get("dest_id", router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    s_idx = router_keys.index(cur_src) if cur_src in router_keys else 0
    d_idx = router_keys.index(cur_dst) if cur_dst in router_keys else len(router_keys) - 1

    # Configuration panel
    fl_c1, fl_c2 = st.columns(2)
    with fl_c1:
        sel_src = st.selectbox("Source (Origin)", options=router_keys, index=s_idx, key="fl_sel_src")
    with fl_c2:
        sel_dst = st.selectbox("Destination (Target)", options=router_keys, index=d_idx, key="fl_sel_dst")

    # Failure selection inputs
    f_in1, f_in2 = st.columns(2)
    with f_in1:
        failed_routers_sel = st.multiselect(
            "Select Routers to Take Offline",
            options=router_keys,
            default=st.session_state.get("fl_selected_routers", []),
            help="Routers marked offline will reject all incoming and outgoing packet transmissions.",
            key="fl_routers_multi"
        )
    with f_in2:
        failed_links_sel = st.multiselect(
            "Select Transmission Links to Sever",
            options=edge_options,
            default=st.session_state.get("fl_selected_links", []),
            help="Severed links will be impassable for packet routing.",
            key="fl_links_multi"
        )

    # Convert link strings back to tuples
    clean_failed_edges = [edge_str_map[s] for s in failed_links_sel if s in edge_str_map]

    # Action Controls
    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1.5, 1.2, 1.2, 2])
    with btn_c1:
        sim_btn = st.button("Apply Failure Scenario", type="primary", width="stretch", key="fl_btn_simulate")
    with btn_c2:
        reset_btn = st.button("Reset Scenario", width="stretch", key="fl_btn_reset")
    with btn_c3:
        restore_btn = st.button("Restore Baseline", width="stretch", key="fl_btn_restore")
    with btn_c4:
        commit_btn = st.button("Commit Scenario to Active Topology", width="stretch", key="fl_btn_commit", help="Permanently applies the offline router states and severed link states to the active network graph.")

    if reset_btn or restore_btn:
        st.session_state["fl_selected_routers"] = []
        st.session_state["fl_selected_links"] = []
        st.session_state.pop("fl_scenario_data", None)
        st.rerun()

    if commit_btn:
        # Commit scenario changes permanently to active graph
        for r in failed_routers_sel:
            if r in graph.routers:
                graph.routers[r].is_online = False
        for u, v in clean_failed_edges:
            graph.failed_edges.add(tuple(sorted((u, v))))
        sim.invalidate_simulation()
        st.success(f"Permanently committed {len(failed_routers_sel)} router outages and {len(clean_failed_edges)} link severances to active network.")
        st.rerun()

    # Always compute or use cached scenario data
    scenario_data = simulate_failure(graph, failed_routers_sel, clean_failed_edges, sel_src, sel_dst)
    st.session_state["fl_scenario_data"] = scenario_data

    # Scenario Summary Callouts
    impact = scenario_data["impact_analysis"]
    base_info = scenario_data["baseline"]
    scen_info = scenario_data["failure_scenario"]
    scen_graph: Graph = scenario_data["scenario_graph"]

    st.write("")
    if impact.get("destination_became_unreachable"):
        st.error(
            f"**CRITICAL ROUTE SEVERANCE**: Destination router **{sel_dst}** became completely unreachable from **{sel_src}**! "
            f"The selected failures severed all path redundancies."
        )
    elif impact.get("route_survived"):
        hop_delta = impact.get("hop_delta", 0)
        cost_delta = impact.get("cost_delta", 0.0)
        delta_str = ""
        if hop_delta and hop_delta > 0:
            delta_str = f"Route diverted (+{hop_delta} extra hops, cost delta: +{cost_delta:.1f})."
        else:
            delta_str = "Route remained identical or equivalent."
        st.success(f"**ROUTE SURVIVED**: Packets can still reach **{sel_dst}** from **{sel_src}**! {delta_str}")
    else:
        st.info("Baseline and Scenario evaluated.")

    if impact.get("disconnected_routers"):
        st.warning(f"**Isolated Routers**: Outages isolated `{', '.join(impact['disconnected_routers'])}` from origin {sel_src}.")

    # Dual Graph Visualizations
    st.write("")
    g_c1, g_c2 = st.columns(2)

    with g_c1:
        st.markdown(
            "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
            "<span style='font-weight:700; color:#2563EB; font-size:1.05rem;'>Baseline Topology</span>"
            "<span style='background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>PRE-FAILURE</span>"
            "</div>",
            unsafe_allow_html=True
        )
        base_bfs = base_info.get("bfs") or {}
        base_vis = {
            "is_completed": True,
            "route_nodes": base_bfs.get("path", []),
            "route_edges": [(base_bfs.get("path")[i], base_bfs.get("path")[i+1]) for i in range(len(base_bfs.get("path", [])) - 1)] if base_bfs.get("path") else []
        }
        fig_base = build_network_figure(graph, base_vis, sel_src, sel_dst, height=390, title="Baseline Network & Active Route")
        render_plotly(fig_base, key="fl_base_graph")
        if base_bfs.get("path"):
            st.caption(f"**Baseline Route:** `{ ' -> '.join(base_bfs['path']) }` ({base_bfs.get('hops', 0)} hops)")
        else:
            st.caption("No route existed in baseline.")

    with g_c2:
        st.markdown(
            "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
            "<span style='font-weight:700; color:#EF4444; font-size:1.05rem;'>Simulated Failure Scenario</span>"
            "<span style='background:#FEE2E2; color:#991B1B; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>SCENARIO CLONE</span>"
            "</div>",
            unsafe_allow_html=True
        )
        scen_bfs = scen_info.get("bfs") or {}
        scen_vis = {
            "is_completed": True,
            "route_nodes": scen_bfs.get("path", []),
            "route_edges": [(scen_bfs.get("path")[i], scen_bfs.get("path")[i+1]) for i in range(len(scen_bfs.get("path", [])) - 1)] if scen_bfs.get("path") else []
        }
        fig_scen = build_network_figure(scen_graph, scen_vis, sel_src, sel_dst, height=390, title="Failure Scenario & Rerouted Path")
        render_plotly(fig_scen, key="fl_scen_graph")
        if scen_bfs.get("path"):
            st.caption(f"**Scenario Route:** `{ ' -> '.join(scen_bfs['path']) }` ({scen_bfs.get('hops', 0)} hops)")
        else:
            st.caption("**Scenario Route:** None (Unreachable)")

    # Comparative Metrics Table
    st.write("")
    st.markdown("### Before vs. After Failure Scenario Metrics")
    b_dijk = base_info.get("dijkstra") or {}
    s_dijk = scen_info.get("dijkstra") or {}

    comp_rows = [
        {"Property": "Connected Subnets (Components)", "Baseline (Pre-Failure)": str(base_info.get("component_count", 1)), "Failure Scenario (Post-Failure)": str(scen_info.get("component_count", 1)), "Delta": f"+{impact.get('component_delta', 0)} Subnets" if impact.get('component_delta', 0) > 0 else "0 (No split)"},
        {"Property": "Destination Reachability", "Baseline (Pre-Failure)": "REACHABLE" if (base_bfs and base_bfs.get("success")) else "UNREACHABLE", "Failure Scenario (Post-Failure)": "REACHABLE" if (scen_bfs and scen_bfs.get("success")) else "UNREACHABLE", "Delta": "Severed" if impact.get("destination_became_unreachable") else ("Survived" if impact.get("route_survived") else "Unchanged")},
        {"Property": "Discovered Route", "Baseline (Pre-Failure)": " -> ".join(base_bfs.get("path", [])) or "None", "Failure Scenario (Post-Failure)": " -> ".join(scen_bfs.get("path", [])) or "None", "Delta": "Diverted" if base_bfs.get("path") != scen_bfs.get("path") else "Identical"},
        {"Property": "Hop Count", "Baseline (Pre-Failure)": f"{base_bfs.get('hops', 0)} hops", "Failure Scenario (Post-Failure)": f"{scen_bfs.get('hops', 0)} hops" if scen_bfs.get("success") else "N/A", "Delta": f"{impact.get('hop_delta'):+d} hops" if impact.get('hop_delta') is not None else "N/A"},
        {"Property": "Least-Cost Route Weight", "Baseline (Pre-Failure)": f"{b_dijk.get('path_cost', 0.0):.1f}", "Failure Scenario (Post-Failure)": f"{s_dijk.get('path_cost', 0.0):.1f}" if s_dijk.get("success") else "N/A", "Delta": f"{impact.get('cost_delta'):+.1f}" if impact.get('cost_delta') is not None else "N/A"},
        {"Property": "Critical Bridges Remaining", "Baseline (Pre-Failure)": str(len(base_info.get("bridges", []))), "Failure Scenario (Post-Failure)": str(len(scen_info.get("bridges", []))), "Delta": str(len(scen_info.get("bridges", [])) - len(base_info.get("bridges", [])))},
        {"Property": "Articulation Points Remaining", "Baseline (Pre-Failure)": str(len(base_info.get("articulation_points", []))), "Failure Scenario (Post-Failure)": str(len(scen_info.get("articulation_points", []))), "Delta": str(len(scen_info.get("articulation_points", [])) - len(base_info.get("articulation_points", [])))}
    ]
    st.dataframe(pd.DataFrame(comp_rows), width="stretch", hide_index=True)

    # Downloads
    st.write("")
    scen_export_dict = {
        "report_type": "NetRoute Failure Scenario Report",
        "schema_version": "1.0",
        "timestamp": scenario_data["timestamp"],
        "topology_name": graph.name,
        "failed_routers": failed_routers_sel,
        "failed_edges": [list(e) for e in clean_failed_edges],
        "endpoints": {"source": sel_src, "destination": sel_dst},
        "impact_analysis": impact,
        "baseline": {
            "component_count": base_info["component_count"],
            "route": base_bfs.get("path", []),
            "hops": base_bfs.get("hops", 0),
            "cost": b_dijk.get("path_cost", 0.0)
        },
        "failure_scenario": {
            "component_count": scen_info["component_count"],
            "route": scen_bfs.get("path", []),
            "hops": scen_bfs.get("hops", 0),
            "cost": s_dijk.get("path_cost", 0.0)
        }
    }
    scen_json = json.dumps(scen_export_dict, indent=2)
    scen_csv = export_failure_scenario_csv(scenario_data)

    dl_f1, dl_f2, dl_f3 = st.columns(3)
    with dl_f1:
        st.download_button(
            label="Download Failure Scenario JSON",
            data=scen_json,
            file_name=f"netroute_failure_scenario_{sel_src}_{sel_dst}.json",
            mime="application/json",
            width="stretch",
            key="fl_dl_json"
        )
    with dl_f2:
        st.download_button(
            label="Download Scenario CSV",
            data=scen_csv,
            file_name=f"netroute_failure_scenario_{sel_src}_{sel_dst}.csv",
            mime="text/csv",
            width="stretch",
            key="fl_dl_csv"
        )
    with dl_f3:
        scen_png = export_figure_png(fig_scen)
        if scen_png:
            st.download_button(
                label="Scenario Graph PNG",
                data=scen_png,
                file_name=f"netroute_failure_scenario_{sel_src}_{sel_dst}.png",
                mime="image/png",
                width="stretch",
                key="fl_dl_png"
            )
        else:
            st.caption("PNG requires Kaleido.")


# =============================================================================
# 5. DATA STRUCTURES INSPECTOR VIEW
# =============================================================================
def render_data_structures_inspector(graph: Graph):
    st.markdown("## Data Structures Inspector")
    st.markdown("*Inspect live graph representations, traversal queue/stack internal states, and algorithm evaluations.*")

    tab_graph, tab_struct, tab_search_sort = st.tabs([
        "Graph Representations",
        "Traversal Queue & Stack",
        "Searching & Sorting Algorithms"
    ])

    # Tab 1: Graph Representations
    with tab_graph:
        st.markdown("### Adjacency List & Adjacency Matrix")
        gr_c1, gr_c2 = st.columns(2)

        with gr_c1:
            st.markdown("#### Adjacency List O(V + E)")
            adj_list = graph.get_adjacency_list()
            adj_rows = [{"Router": r, "Neighbors (Degree)": f"{', '.join(nbrs) if nbrs else 'None'} ({len(nbrs)})"} for r, nbrs in adj_list.items()]
            st.dataframe(pd.DataFrame(adj_rows), width="stretch", hide_index=True)

        with gr_c2:
            st.markdown("#### Adjacency Matrix O(V²)")
            nodes, matrix = graph.get_adjacency_matrix()
            if nodes:
                df_matrix = pd.DataFrame(matrix, index=nodes, columns=nodes)
                st.dataframe(df_matrix, width="stretch")
            else:
                st.info("Network is empty.")

    # Tab 2: Traversal Queue & Stack State
    with tab_struct:
        st.markdown("### Traversal Queue & Stack State")
        sim_res = st.session_state.get("sim_res")
        if sim_res and sim_res.get("steps"):
            st.caption(f"Displaying data structure progression for **{sim_res.get('algorithm', '')}**")
            step_rows = []
            for s in sim_res["steps"]:
                step_rows.append({
                    "Step": s.get("step"),
                    "Operation": s.get("operation"),
                    "Active Router": s.get("current_node"),
                    "Front / Top": s.get("front", s.get("top")),
                    "Structure Contents": f"[{', '.join(s.get('structure', []))}]",
                    "Size": len(s.get("structure", []))
                })
            st.dataframe(pd.DataFrame(step_rows), width="stretch", hide_index=True)
        else:
            st.info("Run a simulation in the Traversal Simulator to populate the live queue/stack state trace.")

    # Tab 3: Searching & Sorting
    with tab_search_sort:
        st.markdown("### Searching & Sorting Demonstration")
        sub_search, sub_sort = st.tabs(["Linear vs. Binary Search", "Bubble vs. Insertion Sort"])

        with sub_search:
            st.markdown("#### Searching Evaluation: Linear vs. Binary Search")
            unsorted_dataset, sorted_dataset = get_adaptive_datasets(graph)

            search_target = st.text_input("Search Target Router ID", value=sorted_dataset[0] if sorted_dataset else "N1", key="ds_search_target").strip().upper()
            if st.button("Evaluate Search Algorithms", type="primary", key="ds_btn_run_search"):
                lin_res = linear_search(sorted_dataset, search_target)
                bin_res = binary_search(sorted_dataset, search_target)
                st.session_state["search_eval"] = {"linear": lin_res, "binary": bin_res}

            search_eval = st.session_state.get("search_eval")
            if search_eval:
                l_res = search_eval["linear"]
                b_res = search_eval["binary"]

                s_res1, s_res2 = st.columns(2)
                with s_res1:
                    st.markdown("##### Linear Search O(n)")
                    st.markdown(f"• **Found:** {l_res.get('found')} at index {l_res.get('index')}")
                    st.markdown(f"• **Comparisons:** {l_res.get('comparisons')}")
                    st.markdown(f"• **Time:** {l_res.get('execution_time_ms', 0.0):.4f} ms")
                    st.caption("Checks elements sequentially from index 0.")

                with s_res2:
                    st.markdown("##### Binary Search O(log n)")
                    st.markdown(f"• **Found:** {b_res.get('found')} at index {b_res.get('index')}")
                    st.markdown(f"• **Comparisons:** {b_res.get('comparisons')}")
                    st.markdown(f"• **Time:** {b_res.get('execution_time_ms', 0.0):.4f} ms")
                    st.caption("Requires sorted array; halves search space per iteration.")

        with sub_sort:
            st.markdown("#### Sorting Evaluation: Bubble Sort vs. Insertion Sort")
            unsorted_dataset, _ = get_adaptive_datasets(graph)
            st.caption(f"Input Dataset: `{unsorted_dataset}`")

            if st.button("Evaluate Sorting Algorithms", type="primary", key="ds_btn_run_sort"):
                bub_res = bubble_sort(unsorted_dataset)
                ins_res = insertion_sort(unsorted_dataset)
                st.session_state["sort_eval"] = {"bubble": bub_res, "insertion": ins_res}

            sort_eval = st.session_state.get("sort_eval")
            if sort_eval:
                bu_res = sort_eval["bubble"]
                in_res = sort_eval["insertion"]

                st_res1, st_res2 = st.columns(2)
                with st_res1:
                    st.markdown("##### Bubble Sort O(n²)")
                    st.markdown(f"• **Comparisons:** {bu_res.get('comparisons')}")
                    st.markdown(f"• **Swaps:** {bu_res.get('swaps')}")
                    st.markdown(f"• **Time:** {bu_res.get('execution_time_ms', 0.0):.4f} ms")
                    st.caption(f"Sorted output: `{bu_res.get('sorted_dataset')}`")

                with st_res2:
                    st.markdown("##### Insertion Sort O(n²)")
                    st.markdown(f"• **Comparisons:** {in_res.get('comparisons')}")
                    st.markdown(f"• **Shifts:** {in_res.get('shifts')}")
                    st.markdown(f"• **Time:** {in_res.get('execution_time_ms', 0.0):.4f} ms")
                    st.caption(f"Sorted output: `{in_res.get('sorted_dataset')}`")


# =============================================================================
# 6. TRAVERSAL TREE VIEW
# =============================================================================
def render_traversal_tree(graph: Graph):
    st.markdown("## Routing Traversal Tree")
    st.markdown("*Hierarchical spanning tree derived from traversal parent pointers, with structural invariant verification.*")

    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning("Network graph is empty.")
        return

    cur_src = st.session_state.get("source_id", router_keys[0])
    cur_dst = st.session_state.get("dest_id", router_keys[-1] if len(router_keys) > 1 else router_keys[0])

    t_c1, t_c2, t_c3 = st.columns([2, 2, 1.5])
    with t_c1:
        tree_src = st.selectbox("Root Router (Source)", options=router_keys, index=router_keys.index(cur_src) if cur_src in router_keys else 0, key="tree_src_sel")
    with t_c2:
        tree_dst = st.selectbox("Target Router (Destination)", options=router_keys, index=router_keys.index(cur_dst) if cur_dst in router_keys else len(router_keys) - 1, key="tree_dst_sel")
    with t_c3:
        st.write("")
        st.write("")
        run_tree = st.button("Build Traversal Tree", width="stretch", type="primary", key="tree_btn_build")

    # Generate or retrieve tree
    cached_tree = st.session_state.get("tree_data")
    if run_tree or not cached_tree or cached_tree.get("root") != tree_src:
        bfs_res = bfs(graph, tree_src, tree_dst)
        parents = bfs_res.get("parents", {})
        tree_data = build_traversal_tree(parents, tree_src, tree_dst)
        st.session_state["tree_data"] = tree_data
    else:
        tree_data = cached_tree

    st.write("")

    tree_col1, tree_col2 = st.columns([1.4, 1.0])

    with tree_col1:
        st.markdown("#### Spanning Tree Visualization")
        fig = build_traversal_tree_figure(tree_data, tree_src, tree_dst, height=450)
        render_plotly(fig, key="tree_plot")
        st.caption("Root router is positioned at the top; child routers descend by distance level. Discovered path highlighted in green.")

    with tree_col2:
        st.markdown("#### Mathematical Invariants")
        inv = tree_data.get("invariants", {})
        v_tree = inv.get("num_vertices", 0)
        e_tree = inv.get("num_edges", 0)
        is_valid = inv.get("is_valid_tree", False)

        st.markdown(
            f"""
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-left:4px solid {'#10B981' if is_valid else '#EF4444'}; border-radius:6px; padding:12px; margin-bottom:12px;">
                <div style="font-weight:700; color:{'#10B981' if is_valid else '#EF4444'};">
                    {'VALID ROOTED TREE' if is_valid else 'INVALID SPANNING TREE'}
                </div>
                <div style="font-size:0.86rem; color:#334155; margin-top:4px;">
                    • <b>Tree Vertices (V_tree):</b> {v_tree}<br>
                    • <b>Tree Edges (E_tree):</b> {e_tree} (Must equal V_tree - 1)<br>
                    • <b>Acyclic Property:</b> {inv.get('is_acyclic', True)}<br>
                    • <b>Connected Component:</b> {inv.get('is_connected', True)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        unreachable = tree_data.get("unreachable_nodes", [])
        if unreachable:
            st.warning(f"Unreachable Nodes ({len(unreachable)}): {', '.join(unreachable)}")
        else:
            st.success("All network routers are spanned by the traversal tree.")

        # Parent pointer table
        st.markdown("##### Predecessor Pointers")
        levels = tree_data.get("levels", {})
        p_rows = []
        for node in tree_data.get("nodes", []):
            p_rows.append({
                "Router": node,
                "Parent": tree_data.get("parents", {}).get(node, "Root (None)"),
                "Depth Level": levels.get(node, 0)
            })
        st.dataframe(pd.DataFrame(p_rows), width="stretch", hide_index=True)


# =============================================================================
# 7. ROUTING TABLE SIMULATOR VIEW
# =============================================================================
def render_routing_table_simulator(graph: Graph):
    st.markdown("## Routing Table Simulator")
    st.markdown("*Simulate hop-by-hop packet forwarding using local router routing tables, detecting loops, offline routers, and link severances.*")

    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning("Network graph is empty.")
        return

    cur_src = st.session_state.get("source_id", router_keys[0])
    cur_dst = st.session_state.get("dest_id", router_keys[-1] if len(router_keys) > 1 else router_keys[0])

    f_col1, f_col2, f_col3 = st.columns([2, 2, 1.5])
    with f_col1:
        fwd_src = st.selectbox("Source Router", options=router_keys, index=router_keys.index(cur_src) if cur_src in router_keys else 0, key="fwd_src_sel")
    with f_col2:
        fwd_dst = st.selectbox("Destination Router", options=router_keys, index=router_keys.index(cur_dst) if cur_dst in router_keys else len(router_keys) - 1, key="fwd_dst_sel")
    with f_col3:
        st.write("")
        st.write("")
        run_fwd = st.button("Simulate Forwarding", width="stretch", type="primary", key="fwd_btn_run")

    if run_fwd or st.session_state.get("table_fwd_res") is None:
        fwd_res = sim.simulate_table_forwarding(graph, fwd_src, fwd_dst)
        st.session_state["table_fwd_res"] = fwd_res

    fwd_res = st.session_state.get("table_fwd_res")

    st.write("")

    if fwd_res:
        if fwd_res.get("success"):
            st.success(f"Forwarding Succeeded: {fwd_res.get('message', '')}")
            st.markdown(render_path_pills(fwd_res.get("path", [])), unsafe_allow_html=True)
        else:
            st.error(f"Forwarding Failed: {fwd_res.get('message', '')}")

        # Step by step forwarding trace
        st.markdown("### Hop-by-Hop Forwarding Log")
        fwd_steps = fwd_res.get("steps", [])
        if fwd_steps:
            trace_rows = []
            for s in fwd_steps:
                entry = s.get("table_entry", {})
                trace_rows.append({
                    "Hop": s.get("step"),
                    "Current Router": s.get("current_router"),
                    "Action": s.get("action"),
                    "Next Hop": s.get("next_hop"),
                    "Metric": entry.get("hops", "-"),
                    "Description": s.get("description")
                })
            st.dataframe(pd.DataFrame(trace_rows), width="stretch", hide_index=True)

    st.write("")
    st.markdown("### Router Routing Table Inspector")
    insp_r = st.selectbox("Inspect Local Routing Table For Router", options=router_keys, key="fwd_inspect_r")
    r_table = graph.generate_routing_table(insp_r)
    if r_table:
        st.dataframe(pd.DataFrame(r_table), width="stretch", hide_index=True)


# =============================================================================
# 8. NETWORK ANALYSIS VIEW
# =============================================================================
def render_network_analysis(graph: Graph):
    st.markdown("## Network Analysis & Resilience")
    st.markdown("*Comprehensive graph topology diagnostics, router degree distribution, Tarjan resilience analysis (Bridges & Articulation Points), and reachability analysis.*")

    summary = graph.get_summary()
    bridges = find_bridges(graph)
    aps = find_articulation_points(graph)

    na1, na2, na3, na4, na5, na6 = st.columns(6)
    na1.metric("Total Routers", summary["total_routers"], f"{summary['online_routers']} online")
    na2.metric("Total Links", summary["total_edges"], f"{len(graph.failed_edges)} failed")
    na3.metric("Components", summary["component_count"])
    na4.metric("Connected", "YES" if summary["is_connected"] else "NO")
    na5.metric("Critical Bridges", len(bridges), "Cut Edges" if bridges else "Biconnected")
    na6.metric("Articulation Points", len(aps), "Cut Vertices" if aps else "Resilient")

    st.write("")

    # Topology Resilience Diagram
    st.markdown("### Topology Resilience Map")
    st.caption("Bridges (amber dashed connections with ⚡Bridge badges) and Articulation Points (amber routers with [AP] badges) represent single points of failure.")
    cur_src = st.session_state.get("source_id", "N1")
    cur_dst = st.session_state.get("dest_id", "N7")
    empty_vis = {"is_completed": False}
    fig_resil = build_network_figure(
        graph,
        empty_vis,
        cur_src,
        cur_dst,
        height=420,
        title="Network Resilience Map (Critical Bridges & Articulation Points)",
        highlight_bridges=set(bridges),
        highlight_aps=set(aps)
    )
    render_plotly(fig_resil, key="na_resilience_fig")

    # Resilience Tables
    st.write("")
    res_tab1, res_tab2 = st.columns(2)

    with res_tab1:
        st.markdown("#### Critical Bridges (Cut Edges)")
        if bridges:
            b_rows = []
            for u, v in bridges:
                # Calculate simulated component count if this bridge is severed
                test_g = graph.clone()
                test_g.failed_edges.add(tuple(sorted((u, v))))
                test_comps = test_g.get_connected_components()
                b_rows.append({
                    "Bridge Link": f"{u} <—> {v}",
                    "Cost": str(graph.get_weight(u, v)),
                    "Subnets After Removal": str(len(test_comps)),
                    "Impact": f"Partitions network into {len(test_comps)} isolated components"
                })
            st.dataframe(pd.DataFrame(b_rows), width="stretch", hide_index=True)
        else:
            st.success("No critical bridges detected. Network links exhibit 2-edge-connected cyclic redundancy.")

    with res_tab2:
        st.markdown("#### Critical Articulation Points (Cut Vertices)")
        if aps:
            ap_rows = []
            for node in aps:
                # Calculate simulated component count if this node is taken offline
                test_g = graph.clone()
                if node in test_g.routers:
                    test_g.routers[node].is_online = False
                test_comps = test_g.get_connected_components()
                ap_rows.append({
                    "Router ID": node,
                    "Name": graph.routers[node].name,
                    "Degree": str(len(graph.adjacency.get(node, []))),
                    "Subnets After Outage": str(len(test_comps)),
                    "Impact": f"Outage isolates remaining routers into {len(test_comps)} subnets"
                })
            st.dataframe(pd.DataFrame(ap_rows), width="stretch", hide_index=True)
        else:
            st.success("No critical articulation points detected. Network topology is 2-vertex-connected.")

    # Interactive Resilience Failure Removal Experiment
    st.write("")
    with st.expander("Interactive Resilience Removal Experiment", expanded=False):
        st.markdown("*Select a critical bridge or articulation point to simulate its removal and observe the instant connectivity impact.*")
        exp_c1, exp_c2, exp_c3 = st.columns([2, 2, 1.5])
        
        sim_options = []
        for u, v in bridges:
            sim_options.append(f"Bridge: {u} <—> {v}")
        for a in aps:
            sim_options.append(f"Articulation Point: {a} ({graph.routers[a].name})")

        if sim_options:
            with exp_c1:
                sel_failure = st.selectbox("Element to Remove", options=sim_options, key="na_sel_failure")
            with exp_c2:
                eval_src = st.selectbox("Origin Router", options=sorted(list(graph.routers.keys())), key="na_eval_src")
            with exp_c3:
                st.write("")
                st.write("")
                run_test = st.button("Simulate Removal", type="primary", width="stretch", key="na_btn_sim_remove")

            if run_test or "na_sim_result" in st.session_state:
                if run_test:
                    test_g = graph.clone()
                    if sel_failure.startswith("Bridge:"):
                        b_str = sel_failure.replace("Bridge:", "").strip()
                        u_part, v_part = [p.strip() for p in b_str.split("<—>")]
                        test_g.failed_edges.add(tuple(sorted((u_part, v_part))))
                    else:
                        ap_id = sel_failure.split(":")[1].split("(")[0].strip()
                        if ap_id in test_g.routers:
                            test_g.routers[ap_id].is_online = False

                    new_comps = test_g.get_connected_components()
                    reach_nodes = test_g.get_reachable_nodes(eval_src)
                    all_nodes = set(graph.routers.keys())
                    lost_nodes = sorted(list(all_nodes - set(reach_nodes)))
                    st.session_state["na_sim_result"] = {
                        "element": sel_failure,
                        "origin": eval_src,
                        "new_comps_count": len(new_comps),
                        "new_comps": [sorted(list(c)) for c in new_comps],
                        "reachable_count": len(reach_nodes),
                        "lost_nodes": lost_nodes
                    }

                res_info = st.session_state.get("na_sim_result")
                if res_info:
                    st.warning(
                        f"**Simulated Removal of {res_info['element']}**: "
                        f"Network split into **{res_info['new_comps_count']} components**! "
                        f"Routers reachable from {res_info['origin']}: `{res_info['reachable_count']}` of {len(graph.routers)}. "
                        f"Isolated routers: `{', '.join(res_info['lost_nodes']) if res_info['lost_nodes'] else 'None'}`."
                    )
        else:
            st.info("The network has no bridges or articulation points; it is fully resilient against single link or router failures.")

    # Export Resilience CSV
    resilience_payload = {
        "online_routers": [r for r, obj in graph.routers.items() if obj.is_online],
        "active_edges": [e for e in graph.get_edges() if graph.is_edge_active(e[0], e[1])],
        "component_count": summary["component_count"],
        "bridges": bridges,
        "articulation_points": aps
    }
    res_csv = export_resilience_csv(resilience_payload)
    dl_rc1, dl_rc2 = st.columns([1, 3])
    with dl_rc1:
        st.download_button(
            label="Download Resilience CSV",
            data=res_csv,
            file_name=f"netroute_resilience_{graph.name.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            width="stretch",
            key="na_dl_resilience_csv"
        )

    st.write("")
    # Degree distribution
    st.markdown("### Router Degree Distribution")
    router_degrees = []
    for rid in sorted(graph.routers.keys()):
        nbrs = graph.adjacency.get(rid, [])
        router_degrees.append({
            "Router ID": rid,
            "Name": graph.routers[rid].name,
            "Degree (Connections)": len(nbrs),
            "Status": "ONLINE" if graph.routers[rid].is_online else "OFFLINE",
            "Neighbors": ", ".join(sorted(nbrs))
        })
    st.dataframe(pd.DataFrame(router_degrees), width="stretch", hide_index=True)

    # Connected Components
    st.markdown("### Connected Subnets (Components)")
    comps = summary["components"]
    for idx, comp in enumerate(comps):
        st.markdown(f"• **Component {idx + 1} ({len(comp)} routers):** `{', '.join(comp)}`")

    # Reachability from source
    st.write("")
    st.markdown("### Reachability Matrix from Source")
    router_keys = sorted(list(graph.routers.keys()))
    if router_keys:
        reach_src = st.selectbox("Evaluate Reachability From", options=router_keys, key="na_reach_src")
        reach_rows = []
        for target in router_keys:
            is_reach = graph.is_reachable(reach_src, target)
            reach_rows.append({
                "Target Router": target,
                "Name": graph.routers[target].name,
                "Reachable from " + reach_src: "YES" if is_reach else "NO",
                "Target Status": "ONLINE" if graph.routers[target].is_online else "OFFLINE"
            })
        st.dataframe(pd.DataFrame(reach_rows), width="stretch", hide_index=True)



# =============================================================================
# 8B. ALGORITHM BENCHMARK LAB VIEW
# =============================================================================
def render_benchmark_lab(graph: Graph):
    st.markdown("## Algorithm Benchmark Lab")
    st.markdown("*Empirical evaluation of BFS, DFS, and Dijkstra on synthetic graphs of varying scale and density with high-resolution execution timing.*")

    st.caption("Benchmark execution uses monotonic high-resolution timing (`time.perf_counter()`) to measure pure algorithmic execution time, strictly excluding Streamlit UI rendering, Plotly layout generation, and network serialization.")

    bc1, bc2, bc3 = st.columns([2, 1.5, 1.5])
    with bc1:
        router_options = [5, 10, 15, 20, 30, 40, 50, 75, 100]
        sel_counts = st.multiselect(
            "Router Counts (V) to Evaluate",
            options=router_options,
            default=[5, 10, 20, 30, 50],
            key="bm_router_counts"
        )
    with bc2:
        sel_density = st.slider(
            "Network Edge Density",
            min_value=0.10,
            max_value=0.80,
            value=0.25,
            step=0.05,
            key="bm_density"
        )
    with bc3:
        sel_algos = st.multiselect(
            "Algorithms to Benchmark",
            options=["BFS", "DFS", "Dijkstra"],
            default=["BFS", "DFS", "Dijkstra"],
            key="bm_algos"
        )

    bc4, bc5, bc6 = st.columns([1.5, 1.5, 2])
    with bc4:
        sel_reps = st.number_input(
            "Repetitions per Test Point",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
            key="bm_repetitions"
        )
    with bc5:
        sel_seed = st.number_input(
            "Random Seed (Reproducibility)",
            min_value=1,
            max_value=999999,
            value=42,
            step=1,
            key="bm_seed"
        )
    with bc6:
        st.write("")
        st.write("")
        run_bm_btn = st.button("Execute Benchmark Suite", type="primary", width="stretch", key="bm_btn_run")

    if run_bm_btn:
        if not sel_counts:
            st.warning("Please select at least one router count to benchmark.")
        elif not sel_algos:
            st.warning("Please select at least one algorithm to benchmark.")
        else:
            with st.spinner("Generating reproducible synthetic topologies and measuring algorithm runtimes..."):
                suite = run_benchmark_suite(
                    router_counts=sel_counts,
                    density=sel_density,
                    algos=sel_algos,
                    repetitions=sel_reps,
                    seed=sel_seed
                )
                st.session_state["benchmark_suite"] = suite
            st.success(f"Benchmark completed successfully! Evaluated {len(suite.get('records', []))} test points across {len(sel_counts)} network scales.")

    suite = st.session_state.get("benchmark_suite")
    if suite and suite.get("records"):
        records = suite["records"]

        st.write("")
        st.markdown("### Measured Algorithm Scaling")

        # Plotly Benchmark Comparison Chart
        fig_bm = go.Figure()
        algo_colors = {
            "BFS": "#2563EB",
            "DFS": "#7C3AED",
            "Dijkstra": "#D97706"
        }
        algo_symbols = {
            "BFS": "circle",
            "DFS": "square",
            "Dijkstra": "diamond"
        }

        for algo in sel_algos:
            algo_recs = [r for r in records if r["algorithm"] == algo]
            algo_recs.sort(key=lambda x: x["routers"])
            if algo_recs:
                x_vals = [r["routers"] for r in algo_recs]
                y_vals = [r["mean_time_ms"] for r in algo_recs]
                fig_bm.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode="lines+markers",
                    name=f"{algo} (Mean ms)",
                    line=dict(color=algo_colors.get(algo, "#0F172A"), width=2.5),
                    marker=dict(symbol=algo_symbols.get(algo, "circle"), size=8)
                ))

        fig_bm.update_layout(
            title="Algorithm Execution Time vs. Network Size (Routers V)",
            xaxis_title="Number of Routers (V)",
            yaxis_title="Mean Execution Time (milliseconds)",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F8FAFC",
            height=400,
            margin=dict(l=50, r=30, t=50, b=50),
            hovermode="x unified",
            xaxis=dict(gridcolor="#E2E8F0"),
            yaxis=dict(gridcolor="#E2E8F0")
        )
        render_plotly(fig_bm, key="bm_chart")

        # Benchmark Metrics Table
        st.write("")
        st.markdown("### Benchmark Experimental Data")
        table_rows = []
        for r in records:
            table_rows.append({
                "Routers (V)": str(r.get("routers")),
                "Edges (E)": str(r.get("edges")),
                "Algorithm": r.get("algorithm"),
                "Mean Time (ms)": f"{r.get('mean_time_ms', 0.0):.4f}",
                "Min Time (ms)": f"{r.get('min_time_ms', 0.0):.4f}",
                "Max Time (ms)": f"{r.get('max_time_ms', 0.0):.4f}",
                "Hops": str(r.get("hops", 0)),
                "Path Cost": f"{r.get('path_cost', 0.0):.1f}",
                "Visited": str(r.get("visited_count", 0)),
                "Explored Edges": str(r.get("explored_edges", 0)),
                "Theoretical Time": r.get("theoretical_time", ""),
                "Theoretical Space": r.get("theoretical_space", "")
            })
        st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

        # Technical Notes & Caveats
        st.write("")
        st.markdown(
            """
            > **Performance & Complexity Notes:**
            > - **High-Resolution Timer:** Execution times are captured using `time.perf_counter()` over the designated repetitions, isolating the pure graph search logic from UI rendering or serialization.
            > - **Sub-Millisecond Measurement Noise:** For smaller network sizes ($V < 30$), execution completes in microseconds. Background OS task switching, CPU branch prediction, and memory caching can introduce micro-level noise. Asymptotic complexity ($O(V+E)$ vs $O((V+E)\log V)$) governs behavior as network scale increases.
            """
        )

        # Downloads
        st.write("")
        bm_csv = export_benchmark_csv(records)
        bm_json = json.dumps(suite, indent=2)

        bm_dl1, bm_dl2, bm_dl3 = st.columns(3)
        with bm_dl1:
            st.download_button(
                label="Download Benchmark CSV",
                data=bm_csv,
                file_name=f"netroute_benchmark_suite_density_{int(sel_density*100)}.csv",
                mime="text/csv",
                width="stretch",
                key="bm_dl_csv"
            )
        with bm_dl2:
            st.download_button(
                label="Download Benchmark JSON",
                data=bm_json,
                file_name=f"netroute_benchmark_suite_density_{int(sel_density*100)}.json",
                mime="application/json",
                width="stretch",
                key="bm_dl_json"
            )
        with bm_dl3:
            bm_png = export_figure_png(fig_bm)
            if bm_png:
                st.download_button(
                    label="Benchmark Chart PNG",
                    data=bm_png,
                    file_name=f"netroute_benchmark_chart.png",
                    mime="image/png",
                    width="stretch",
                    key="bm_dl_png"
                )
            else:
                st.caption("PNG export requires Kaleido.")


# =============================================================================
# 9. SIMULATION HISTORY VIEW
# =============================================================================
def render_simulation_history(graph: Graph):
    st.markdown("## Simulation History")
    st.markdown("*Session record of all executed routing simulations, dual comparisons, and downloadable run reports.*")

    history = st.session_state.get("simulation_history", [])

    h_col1, h_col2 = st.columns([3, 1])
    with h_col2:
        if st.button("Clear History", width="stretch", icon=":material/delete_sweep:", key="hist_clear_btn"):
            sim.clear_history()
            st.rerun()

    if not history:
        st.info("No completed simulations recorded in this session yet. Run a simulation in the Traversal Simulator or Comparison views to record history.")
        return

    # Table of past runs
    table_rows = []
    for run in history:
        table_rows.append({
            "ID": run.get("id"),
            "Timestamp": run.get("timestamp"),
            "Type": run.get("type"),
            "Algorithm": run.get("algorithm"),
            "Route": f"{run.get('source')} -> {run.get('destination')}",
            "Status": "SUCCESS" if run.get("success") else "FAILED",
            "Hops": run.get("hops", 0),
            "Steps": run.get("steps_count", 0),
            "Time (ms)": run.get("execution_time_ms", 0.0)
        })

    st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

    # Detailed Inspector for a selected run
    st.write("")
    st.markdown("### Inspect Historical Run")
    run_ids = [r["id"] for r in history]
    sel_run_id = st.selectbox("Select Run ID to Inspect", options=run_ids, key="hist_run_select")
    selected_record = next((r for r in history if r["id"] == sel_run_id), None)

    if selected_record:
        st.json(selected_record)
        report_data = selected_record.get("report")
        if report_data:
            st.download_button(
                label=f"Download JSON Report for {sel_run_id}",
                data=json.dumps(report_data, indent=2),
                file_name=f"netroute_report_{sel_run_id}.json",
                mime="application/json",
                width="stretch",
                key=f"hist_dl_{sel_run_id}"
            )


# =============================================================================
# 10. IMPORT / EXPORT VIEW
# =============================================================================
def render_import_export(graph: Graph):
    st.markdown("## Import / Export")
    st.markdown("*Export the current network topology as JSON, import external network configurations, and download simulation reports.*")

    tab_exp_topo, tab_imp_topo, tab_exp_reports = st.tabs([
        "Export Topology",
        "Import Topology",
        "Export Simulation Reports"
    ])

    with tab_exp_topo:
        st.markdown("### Export Active Topology")
        st.caption("Serializes all router objects, coordinates, availability states, connections, weights, and severed link states.")
        topo_dict = graph.to_dict()
        topo_json = json.dumps(topo_dict, indent=2)

        preset_name = st.session_state.get("selected_preset", "custom")
        st.download_button(
            label="Download Topology JSON File",
            data=topo_json,
            file_name=f"netroute_topology_{preset_name}.json",
            mime="application/json",
            type="primary",
            width="stretch",
            key="ie_btn_download_topo"
        )
        st.write("")
        st.markdown("##### Preview Serialized JSON")
        st.code(topo_json, language="json")

    with tab_imp_topo:
        st.markdown("### Import Topology JSON")
        st.caption("Upload a JSON file containing router coordinates and connection definitions. Full validation guarantees the graph remains unmodified on error.")

        uploaded_file = st.file_uploader("Choose a JSON topology file", type=["json"], key="ie_file_uploader")
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                if st.button("Validate and Load Topology", type="primary", width="stretch", key="ie_btn_load_file"):
                    ok, msg = graph.load_from_dict(data)
                    if ok:
                        st.success(f"Topology imported successfully! {msg}")
                        st.session_state["selected_preset"] = "custom"
                        g_nodes = sorted(list(graph.routers.keys()))
                        if g_nodes:
                            st.session_state["source_id"] = g_nodes[0]
                            st.session_state["dest_id"] = g_nodes[-1]
                        sim.invalidate_simulation()
                        st.rerun()
                    else:
                        st.error(f"Import Failed: {msg}")
            except Exception as e:
                st.error(f"Failed to parse JSON file: {str(e)}")

    with tab_exp_reports:
        st.markdown("### Export Current Simulation Reports")
        sim_res = st.session_state.get("sim_res")
        cmp_res = st.session_state.get("cmp_res")
        src_id = st.session_state.get("source_id", "N1")
        dst_id = st.session_state.get("dest_id", "N7")

        r_c1, r_c2 = st.columns(2)
        with r_c1:
            st.markdown("##### Latest Single Traversal Report")
            if sim_res:
                rep_data = generate_simulation_report(graph, sim_res, src_id, dst_id)
                st.download_button(
                    label="Download Single Simulation JSON Report",
                    data=json.dumps(rep_data, indent=2),
                    file_name=f"netroute_traversal_report_{src_id}_{dst_id}.json",
                    mime="application/json",
                    width="stretch",
                    key="ie_dl_single_rep"
                )
            else:
                st.info("No single traversal has been run yet.")

        with r_c2:
            st.markdown("##### Latest Dual Comparison Report")
            if cmp_res:
                cmp_rep = generate_comparison_report(graph, cmp_res, src_id, dst_id)
                st.download_button(
                    label="Download Comparison JSON Report",
                    data=json.dumps(cmp_rep, indent=2),
                    file_name=f"netroute_comparison_report_{src_id}_{dst_id}.json",
                    mime="application/json",
                    width="stretch",
                    key="ie_dl_cmp_rep"
                )
            else:
                st.info("No dual comparison has been run yet.")


# =============================================================================
# 11. SETTINGS / HELP VIEW
# =============================================================================
def render_settings_help(graph: Graph):
    st.markdown("## Settings & Technical Guide")
    st.markdown("*Algorithmic documentation, complexity reference, and simulator configuration.*")

    tab_guide, tab_theory, tab_settings = st.tabs([
        "User Guide",
        "Algorithm Reference",
        "Settings"
    ])

    with tab_guide:
        st.markdown(
            """
            ### NetRoute Quick Start Guide
            1. **Topology Studio**: Build your network graph by adding routers and connecting them with transmission links. Assign costs, reposition nodes, or toggle offline states.
            2. **Traversal Simulator**: Select Source and Destination routers. Run BFS or DFS and use step playback (`<`, `>`, slider) to inspect queue and stack dynamics.
            3. **BFS vs. DFS Comparison**: Watch synchronized side-by-side simulations to understand why BFS guarantees minimum hops while DFS explores deep branches.
            4. **Routing Table Simulator**: Experience traditional distributed hop-by-hop forwarding using local routing tables.
            5. **Import / Export**: Save and restore your network topologies as JSON files or export complete simulation logs.
            """
        )

    with tab_theory:
        st.markdown(
            """
            ### Algorithmic Foundations
            - **Breadth-First Search (BFS):** Explores all vertices at distance $k$ before proceeding to distance $k+1$. Uses a FIFO Queue (`collections.deque`). In unweighted graphs, the first time the destination is discovered, the path is guaranteed to have the minimum number of hops.
            - **Depth-First Search (DFS):** Dives aggressively along each branch until dead-ends are reached, using a LIFO Stack. Does not guarantee the shortest route.
            - **Weighted Graphs:** Standard BFS and DFS do not minimize total path weight; Dijkstra's algorithm (priority queue BFS) is required for least-cost paths.
            """
        )

        st.markdown("#### Time & Space Complexity Reference")
        st.markdown(
            """
            | Algorithm | Data Structure | Time Complexity | Auxiliary Space | Shortest Hop Guarantee? |
            | :--- | :--- | :--- | :--- | :--- |
            | **BFS** | FIFO Queue | `O(V + E)` | `O(V)` | **Yes** (Unweighted graphs) |
            | **DFS** | LIFO Stack | `O(V + E)` | `O(V)` | **No** (Explores paths deeply) |
            | **Table Forwarding** | Forwarding Table | `O(H)` hops | `O(1)` per router | Dependent on routing table |
            """
        )

    with tab_settings:
        st.markdown("### Simulator Configuration")
        if st.button("Reset Entire Application to Defaults", width="stretch", key="set_btn_factory_reset"):
            st.session_state.clear()
            sim.init_session()
            st.rerun()
        st.caption("Restores the default Reference 7-Node WAN topology and resets all simulation history.")
