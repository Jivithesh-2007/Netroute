import json
import time
from typing import Dict, Any, List, Set, Tuple, Optional
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from network import Graph, validate_router_id
from algorithms import bfs, dfs, dijkstra, linear_search, binary_search, bubble_sort, insertion_sort, build_traversal_tree, compare_bfs_dfs, compare_routing_strategies, find_bridges, find_articulation_points, simulate_failure, generate_benchmark_graph, run_benchmark_suite, generate_simulation_report, generate_comparison_report
from report import export_simulation_metrics_csv, export_comparison_metrics_csv, export_resilience_csv, export_failure_scenario_csv, export_benchmark_csv
import simulation as sim
from visualizer import build_network_figure, build_traversal_tree_figure, build_algo_result_figure, render_plotly, export_figure_png
from theme import render_path_pills, render_step_card, PRIMARY, PRIMARY_DARK, CYAN, PURPLE, SUCCESS, WARNING, ERROR, TEXT_MAIN, TEXT_MUTED, BORDER

def get_adaptive_datasets(graph: Graph) -> Tuple[List[str], List[str]]:
    nodes = sorted(list(graph.routers.keys()))
    if not nodes:
        return ([], [])
    n = len(nodes)
    if n <= 2:
        unsorted_list = list(reversed(nodes))
    else:
        indices = []
        left, right = (0, n - 1)
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
            unsorted_list[0], unsorted_list[-1] = (unsorted_list[-1], unsorted_list[0])
    return (unsorted_list, nodes)

def render_dashboard(graph: Graph):
    st.markdown('## Network Dashboard')
    st.markdown('*Real-time status overview of active network topology, connectivity metrics, and simulation state.*')
    summary = graph.get_summary()
    sim_status = sim.get_simulation_status()
    sim_res = st.session_state.get('sim_res')
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid {PRIMARY};"><div class="metric-card-label">Active Routers</div><div class="metric-card-val">{summary['total_routers']}</div><div style="font-size:0.80rem; color:{TEXT_MUTED};">{summary['online_routers']} Online | {summary['offline_routers']} Offline</div></div>""", unsafe_allow_html=True)
    with c2:
        failed_count = len(graph.failed_edges)
        active_count = summary['total_edges'] - failed_count
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid {CYAN};"><div class="metric-card-label">Transmission Links</div><div class="metric-card-val">{summary['total_edges']}</div><div style="font-size:0.80rem; color:{TEXT_MUTED};">{active_count} Active | {failed_count} Severed</div></div>""", unsafe_allow_html=True)
    with c3:
        conn_text = 'Fully Connected' if summary['is_connected'] else f"{summary['component_count']} Subnets (Partitioned)"
        conn_color = SUCCESS if summary['is_connected'] else WARNING
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid {conn_color};"><div class="metric-card-label">Topology Connectivity</div><div class="metric-card-val" style="font-size:1.15rem; color:{conn_color};">{conn_text}</div><div style="font-size:0.80rem; color:{TEXT_MUTED};">Preset: {st.session_state.get('selected_preset', 'custom').title()}</div></div>""", unsafe_allow_html=True)
    with c4:
        status_color = SUCCESS if sim_status == 'Completed' else PRIMARY if sim_status == 'Running' else TEXT_MUTED
        route_info = ''
        if sim_res and sim_res.get('success'):
            route_info = f"{sim_res.get('hops', 0)} hops | {len(sim_res.get('visited', []))} visited"
        elif sim_res and (not sim_res.get('success')):
            route_info = 'Destination unreachable'
        else:
            route_info = 'Ready to simulate'
        st.markdown(f'<div class="metric-card" style="border-top:3px solid {status_color};"><div class="metric-card-label">Simulation Engine</div><div class="metric-card-val" style="font-size:1.20rem; color:{status_color};">{sim_status}</div><div style="font-size:0.80rem; color:{TEXT_MUTED};">{route_info}</div></div>', unsafe_allow_html=True)
    st.write('')
    st.markdown('### Active Network Topology')
    active_state = sim.get_active_state(graph)
    src_id = st.session_state.get('source_id', 'N1')
    dst_id = st.session_state.get('dest_id', 'N7')
    fig = build_network_figure(graph, active_state, src_id, dst_id, height=430)
    render_plotly(fig, key='dashboard_graph')
    st.markdown('### Quick Actions')
    for col, (label, target, is_p) in zip(st.columns(4), [('Topology Studio', 'Topology Studio', False), ('Traversal Simulator', 'Traversal Simulator', True), ('BFS vs DFS Comparison', 'BFS vs DFS Comparison', False), ('Routing Table Simulator', 'Routing Table Simulator', False)]):
        with col:
            if st.button(label, width='stretch', key=f'dash_btn_{target}', type='primary' if is_p else 'secondary'):
                st.session_state['nav_page'] = target
                st.rerun()
    st.write('')
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown('#### Routers Inventory')
        if graph.routers:
            r_rows = []
            for rid in sorted(graph.routers.keys()):
                r = graph.routers[rid]
                r_rows.append({'ID': r.id, 'Name': r.name, 'Status': 'ONLINE' if r.is_online else 'OFFLINE', 'Degree': len(graph.adjacency.get(rid, [])), 'Position': f'({r.x}, {r.y})'})
            st.dataframe(pd.DataFrame(r_rows), width='stretch', hide_index=True)
        else:
            st.info('No routers present in topology.')
    with t_col2:
        st.markdown('#### Transmission Links')
        edges = graph.get_edges()
        if edges:
            e_rows = []
            for u, v in edges:
                e_rows.append({'Link': f'{u} <—> {v}', 'Weight / Metric': graph.get_weight(u, v), 'State': 'ACTIVE' if graph.is_edge_active(u, v) else 'SEVERED (Failed)'})
            st.dataframe(pd.DataFrame(e_rows), width='stretch', hide_index=True)
        else:
            st.info('No connections present in topology.')

def render_topology_studio(graph: Graph):
    st.markdown('## Topology Studio')
    st.markdown('*Interactive graph editor: add, delete, rename, and reposition routers; configure link costs and simulate link failures.*')
    router_keys = sorted(list(graph.routers.keys()))
    src_id = st.session_state.get('source_id', router_keys[0] if router_keys else 'N1')
    dst_id = st.session_state.get('dest_id', router_keys[-1] if router_keys else 'N7')
    tb1, tb2, tb3, tb4 = st.columns([2.5, 1.2, 1.2, 1.5])
    try:
        from topology_registry import get_topology_registry
        reg = get_topology_registry()
        preset_options = reg.get_preset_options()
        if not preset_options:
            raise ValueError('Empty registry')
    except Exception:
        preset_options = {'reference': 'Reference 7-Node WAN', 'ring': 'Ring Network (Cyclic)', 'mesh': 'Mesh Network', 'disconnected': 'Disconnected Subnets', 'direct': 'Linear Chain', 'multi_route': 'Multi-Path Spine-Leaf', 'offline_router': 'Offline Router Topology'}
    with tb1:
        current_preset = st.session_state.get('selected_preset', 'reference')
        if current_preset not in preset_options:
            current_preset = 'reference'
        sel_preset = st.selectbox('Load Topology Preset', options=list(preset_options.keys()), format_func=lambda k: preset_options[k], index=list(preset_options.keys()).index(current_preset), key='studio_preset_select')
        if sel_preset != st.session_state.get('selected_preset'):
            st.session_state['selected_preset'] = sel_preset
            st.session_state['graph'] = Graph.from_preset(sel_preset)
            sim.invalidate_simulation()
            g_nodes = sorted(list(st.session_state['graph'].routers.keys()))
            st.session_state['source_id'] = g_nodes[0] if g_nodes else 'N1'
            st.session_state['dest_id'] = g_nodes[-1] if g_nodes else 'N7'
            st.rerun()
    with tb2:
        st.write('')
        st.write('')
        if st.button('Auto Layout', width='stretch', icon=':material/hub:', key='studio_btn_autolayout'):
            graph.auto_layout()
            st.rerun()
    with tb3:
        st.write('')
        st.write('')
        if st.button('Reset Graph', width='stretch', icon=':material/refresh:', key='studio_btn_reset'):
            st.session_state['graph'] = Graph.from_preset(st.session_state.get('selected_preset', 'reference'))
            sim.invalidate_simulation()
            st.rerun()
    with tb4:
        st.write('')
        st.write('')
        confirm_clear = st.checkbox('Confirm clear', key='confirm_clear_chk')
        if st.button('Clear All', width='stretch', icon=':material/delete_forever:', key='studio_btn_clear', disabled=not confirm_clear):
            graph.clear()
            sim.invalidate_simulation()
            st.rerun()
    st.write('')
    col_graph, col_ctrl = st.columns([1.35, 1.0])
    with col_graph:
        st.markdown('#### Live Network Diagram')
        active_state = sim.get_active_state(graph)
        fig = build_network_figure(graph, active_state, src_id, dst_id, height=480)
        render_plotly(fig, key='studio_graph')
        summary = graph.get_summary()
        st.caption(f"""**Graph Metrics:** {summary['total_routers']} Routers ({summary['online_routers']} online) | {summary['total_edges']} Edges ({len(graph.failed_edges)} severed) | Connectivity: {('Connected' if summary['is_connected'] else f"{summary['component_count']} Subnets")}""")
    with col_ctrl:
        tab_routers, tab_links, tab_props = st.tabs(['Routers', 'Connections', 'Endpoints'])
        with tab_routers:
            st.markdown('##### Add Router')
            ar_c1, ar_c2 = st.columns([1, 1.5])
            new_rid = ar_c1.text_input('Router ID', placeholder='e.g. R8', max_chars=8, key='ts_add_rid').strip().upper()
            new_rname = ar_c2.text_input('Router Name', placeholder='e.g. Core Gateway', key='ts_add_rname').strip()
            ar_c3, ar_c4, ar_c5 = st.columns([1, 1, 1.2])
            pos_x = ar_c3.number_input('X Coord', value=360.0, step=20.0, key='ts_add_x')
            pos_y = ar_c4.number_input('Y Coord', value=220.0, step=20.0, key='ts_add_y')
            with ar_c5:
                st.write('')
                st.write('')
                add_r_btn = st.button('Add Router', width='stretch', type='primary', key='ts_btn_add_router')
            if add_r_btn:
                ok_id, msg_id = validate_router_id(new_rid)
                if not ok_id:
                    st.error(msg_id)
                elif new_rid in graph.routers:
                    st.error(f"Router '{new_rid}' already exists.")
                else:
                    graph.add_router(new_rid, name=new_rname or f'Router {new_rid}', x=pos_x, y=pos_y)
                    sim.invalidate_simulation()
                    st.success(f'Added Router {new_rid}')
                    st.rerun()
            st.markdown('---')
            st.markdown('##### Manage Router')
            if router_keys:
                sel_manage_r = st.selectbox('Select Router to Edit', options=router_keys, key='ts_manage_r_select')
                r_obj = graph.routers[sel_manage_r]
                mr_c1, mr_c2 = st.columns([1.5, 1])
                renamed_name = mr_c1.text_input('Name', value=r_obj.name, key='ts_edit_name')
                if mr_c2.button('Rename', key='ts_btn_rename', width='stretch'):
                    if renamed_name.strip():
                        graph.rename_router(sel_manage_r, renamed_name)
                        st.success(f"Renamed router to '{renamed_name}'")
                        st.rerun()
                mr_c3, mr_c4 = st.columns([1, 1])
                curr_status = r_obj.is_online
                new_status_btn = mr_c3.button(f"Set {('OFFLINE' if curr_status else 'ONLINE')}", width='stretch', key='ts_btn_toggle_status')
                if new_status_btn:
                    graph.toggle_router_status(sel_manage_r)
                    sim.invalidate_simulation()
                    st.rerun()
                del_r_btn = mr_c4.button('Delete Router', width='stretch', key='ts_btn_del_r')
                if del_r_btn:
                    rem_nodes = [r for r in router_keys if r != sel_manage_r]
                    if st.session_state.get('source_id') == sel_manage_r:
                        st.session_state['source_id'] = rem_nodes[0] if rem_nodes else 'N1'
                    if st.session_state.get('dest_id') == sel_manage_r:
                        st.session_state['dest_id'] = rem_nodes[-1] if rem_nodes else 'N7'
                    for key_name in ['src_select', 'dst_select', 'ts_manage_r_select']:
                        if key_name in st.session_state and st.session_state[key_name] == sel_manage_r:
                            del st.session_state[key_name]
                    graph.remove_router(sel_manage_r)
                    sim.invalidate_simulation()
                    st.success(f'Deleted router {sel_manage_r}')
                    st.rerun()
                st.markdown('###### Position Adjustment')
                pos_c1, pos_c2, pos_c3 = st.columns([1, 1, 1])
                edit_x = pos_c1.number_input('X', value=r_obj.x, step=15.0, key='ts_edit_x')
                edit_y = pos_c2.number_input('Y', value=r_obj.y, step=15.0, key='ts_edit_y')
                with pos_c3:
                    st.write('')
                    st.write('')
                    if st.button('Save Pos', width='stretch', key='ts_btn_save_pos'):
                        r_obj.x = edit_x
                        r_obj.y = edit_y
                        st.rerun()
            else:
                st.info('No routers to manage. Add a router above.')
        with tab_links:
            st.markdown('##### Add Connection')
            if len(router_keys) >= 2:
                ac_c1, ac_c2, ac_c3 = st.columns([1, 1, 1])
                u_node = ac_c1.selectbox('Router U', options=router_keys, index=0, key='ts_conn_u')
                v_candidates = [r for r in router_keys if r != u_node]
                v_node = ac_c2.selectbox('Router V', options=v_candidates, index=0, key='ts_conn_v')
                link_weight = ac_c3.number_input('Cost / Weight', min_value=0.0, value=1.0, step=0.5, key='ts_conn_w')
                if st.button('Add Transmission Link', width='stretch', type='primary', key='ts_btn_add_link'):
                    if v_node in graph.adjacency.get(u_node, []):
                        st.warning(f'Connection between {u_node} and {v_node} already exists.')
                    else:
                        graph.add_connection(u_node, v_node, weight=link_weight)
                        sim.invalidate_simulation()
                        st.success(f'Connected {u_node} <—> {v_node} with cost {link_weight}')
                        st.rerun()
            else:
                st.info('Need at least 2 routers to add connections.')
            st.markdown('---')
            st.markdown('##### Manage Existing Links')
            edges = graph.get_edges()
            if edges:
                edge_labels = [f'{u} <—> {v}' for u, v in edges]
                sel_edge_idx = st.selectbox('Select Link', options=list(range(len(edges))), format_func=lambda i: edge_labels[i], key='ts_edge_select')
                sel_u, sel_v = edges[sel_edge_idx]
                curr_w = graph.get_weight(sel_u, sel_v)
                curr_active = graph.is_edge_active(sel_u, sel_v)
                el_c1, el_c2, el_c3 = st.columns([1.2, 1, 1])
                new_w = el_c1.number_input('New Cost', min_value=0.0, value=curr_w, step=0.5, key='ts_edit_w')
                with el_c2:
                    st.write('')
                    st.write('')
                    if st.button('Update Cost', width='stretch', key='ts_btn_update_w'):
                        graph.set_weight(sel_u, sel_v, new_w)
                        sim.invalidate_simulation()
                        st.rerun()
                with el_c3:
                    st.write('')
                    st.write('')
                    toggle_txt = 'Restore' if not curr_active else 'Sever Link'
                    if st.button(toggle_txt, width='stretch', key='ts_btn_toggle_edge'):
                        graph.toggle_edge_failure(sel_u, sel_v)
                        sim.invalidate_simulation()
                        st.rerun()
                if st.button('Remove Link', width='stretch', key='ts_btn_remove_edge'):
                    graph.remove_connection(sel_u, sel_v)
                    sim.invalidate_simulation()
                    st.success(f'Removed connection ({sel_u} <—> {sel_v})')
                    st.rerun()
            else:
                st.info('No connections present in network.')
        with tab_props:
            st.markdown('##### Global Routing Endpoints')
            if router_keys:
                ep_c1, ep_c2 = st.columns(2)
                cur_src = st.session_state.get('source_id', router_keys[0])
                cur_dst = st.session_state.get('dest_id', router_keys[-1])
                s_idx = router_keys.index(cur_src) if cur_src in router_keys else 0
                d_idx = router_keys.index(cur_dst) if cur_dst in router_keys else len(router_keys) - 1
                new_src = ep_c1.selectbox('Source Router', options=router_keys, index=s_idx, key='ts_ep_src')
                new_dst = ep_c2.selectbox('Destination Router', options=router_keys, index=d_idx, key='ts_ep_dst')
                if new_src != st.session_state.get('source_id') or new_dst != st.session_state.get('dest_id'):
                    st.session_state['source_id'] = new_src
                    st.session_state['dest_id'] = new_dst
                    sim.invalidate_simulation()
                    st.rerun()
                st.caption(f'Packets will route from **{new_src}** ({graph.routers[new_src].name}) to **{new_dst}** ({graph.routers[new_dst].name}).')

def render_traversal_simulator(graph: Graph):
    st.markdown('## Traversal Simulator')
    st.markdown('*Step-by-step interactive simulation of network packet discovery using BFS (FIFO Queue) or DFS (LIFO Stack).*')
    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning('Network graph is empty. Please add routers in Topology Studio or load a preset.')
        return
    cfg1, cfg2, cfg3, cfg4, cfg5, cfg6 = st.columns([1.5, 1.5, 2.0, 1.1, 1.5, 1.0])
    cur_src = st.session_state.get('source_id', router_keys[0])
    cur_dst = st.session_state.get('dest_id', router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    if cur_src not in router_keys:
        cur_src = router_keys[0]
    if cur_dst not in router_keys:
        cur_dst = router_keys[-1]
    st.session_state['source_id'] = cur_src
    st.session_state['dest_id'] = cur_dst

    def _on_sim_endpoints_changed():
        n_s = st.session_state.get('sim_sel_src')
        n_d = st.session_state.get('sim_sel_dst')
        n_a = st.session_state.get('sim_sel_algo')
        if n_s in router_keys and n_d in router_keys:
            st.session_state['source_id'] = n_s
            st.session_state['dest_id'] = n_d
            st.session_state['selected_algo'] = n_a
            st.session_state['sb_src_selector'] = n_s
            st.session_state['sb_dst_selector'] = n_d
            st.session_state['cmp_bar_src'] = n_s
            st.session_state['cmp_bar_dst'] = n_d
            sim.invalidate_simulation()

    if st.session_state.get('sim_sel_src') not in router_keys or st.session_state.get('sim_sel_src') != cur_src:
        st.session_state['sim_sel_src'] = cur_src
    if st.session_state.get('sim_sel_dst') not in router_keys or st.session_state.get('sim_sel_dst') != cur_dst:
        st.session_state['sim_sel_dst'] = cur_dst
    with cfg1:
        sel_src = st.selectbox('Source', options=router_keys, key='sim_sel_src', on_change=_on_sim_endpoints_changed)
    with cfg2:
        sel_dst = st.selectbox('Destination', options=router_keys, key='sim_sel_dst', on_change=_on_sim_endpoints_changed)
    with cfg3:
        algo_options = ['BFS (Breadth-First Search)', 'DFS (Depth-First Search)', 'Dijkstra (Weighted Shortest Path)']
        cur_algo = st.session_state.get('selected_algo', algo_options[0])
        a_idx = 2 if 'DIJKSTRA' in str(cur_algo).upper() else 1 if 'DFS' in str(cur_algo).upper() else 0
        if st.session_state.get('sim_sel_algo') not in algo_options:
            st.session_state['sim_sel_algo'] = algo_options[a_idx]
        sel_algo = st.selectbox('Algorithm', options=algo_options, key='sim_sel_algo', on_change=_on_sim_endpoints_changed)
    with cfg4:
        st.write('')
        st.write('')
        sim_autoplay_val = st.checkbox('Autoplay', value=st.session_state.get('sim_autoplay', True), key='sim_autoplay_cb')
        st.session_state['sim_autoplay'] = sim_autoplay_val
    with cfg5:
        st.write('')
        st.write('')
        run_btn = st.button('Run Simulation', width='stretch', type='primary', key='sim_btn_run')
    with cfg6:
        st.write('')
        st.write('')
        reset_btn = st.button('Reset', width='stretch', key='sim_btn_reset')
    if reset_btn:
        sim.reset_simulation()
        st.rerun()
    if run_btn:
        if sel_src not in graph.routers or sel_dst not in graph.routers:
            st.error('Selected source or destination router does not exist in network.')
            return
        if not graph.routers[sel_src].is_online:
            st.error(f"Source router '{sel_src}' is OFFLINE. Cannot initiate packet traversal.")
            return
        if not graph.routers[sel_dst].is_online:
            st.error(f"Destination router '{sel_dst}' is OFFLINE. Cannot reach endpoint.")
            return
        sim.execute_routing(graph, sel_algo, sel_src, sel_dst)
        st.session_state['step_idx'] = 0
        if sim_autoplay_val:
            st.session_state['is_playing'] = True
            st.session_state['is_paused'] = False
        else:
            st.session_state['is_playing'] = False
            st.session_state['is_paused'] = False
        st.rerun()
    sim_res = st.session_state.get('sim_res')
    if not sim_res and sel_src in graph.routers and sel_dst in graph.routers:
        if graph.routers[sel_src].is_online and graph.routers[sel_dst].is_online:
            sim_res = sim.execute_routing(graph, sel_algo, sel_src, sel_dst)
            st.session_state['step_idx'] = 0
            if sim_autoplay_val:
                st.session_state['is_playing'] = True
                st.session_state['is_paused'] = False
    if not sim_res:
        st.info('Select online routers and click **Run Simulation** to generate the step-by-step traversal trace.')
        active_state = sim.get_active_state(graph)
        fig = build_network_figure(graph, active_state, sel_src, sel_dst, height=430)
        render_plotly(fig, key='sim_graph_idle')
        return
    steps = sim_res.get('steps', [])
    total_steps = len(steps)
    step_idx = st.session_state.get('step_idx', 0)
    is_playing = st.session_state.get('is_playing', False)
    is_paused = st.session_state.get('is_paused', False)
    st.write('')
    ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4, ctrl_c5, ctrl_c6 = st.columns([1.2, 1, 1, 1, 1.4, 1.8])
    with ctrl_c1:
        if is_playing:
            if st.button('⏸ Pause', width='stretch', key='sim_btn_pause', help='Pause traversal'):
                sim.sim_pause()
                st.rerun()
        elif is_paused and 0 < step_idx < total_steps - 1:
            if st.button('▶ Resume', width='stretch', type='primary', key='sim_btn_resume', help='Resume traversal'):
                sim.sim_resume()
                st.rerun()
        elif st.button('▶ Play', width='stretch', type='primary', key='sim_btn_play', help='Play traversal'):
            sim.sim_play()
            st.rerun()
    with ctrl_c2:
        if st.button('◀ Prev', width='stretch', key='sim_btn_prev', help='Previous Step'):
            sim.step_backward()
            st.rerun()
    with ctrl_c3:
        if st.button('Next ▶', width='stretch', key='sim_btn_next', help='Next Step'):
            sim.step_forward()
            st.rerun()
    with ctrl_c4:
        if st.button('↺ Restart', width='stretch', key='sim_btn_restart', help='Restart from Step 1'):
            sim.sim_restart()
            st.rerun()
    with ctrl_c5:
        if st.button('⏭ Run to End', width='stretch', key='sim_btn_completion', help='Run directly to completion'):
            sim.sim_run_to_completion()
            st.rerun()
    with ctrl_c6:
        speed_map = {'Fast (0.2s)': 0.2, 'Normal (0.5s)': 0.5, 'Slow (1.0s)': 1.0}
        cur_spd_val = st.session_state.get('sim_speed', 0.5)
        speed_labels = list(speed_map.keys())
        default_spd_idx = 1
        for idx_spd, (k, v) in enumerate(speed_map.items()):
            if abs(v - cur_spd_val) < 0.05:
                default_spd_idx = idx_spd
                break
        sel_spd_label = st.selectbox('Playback Speed', options=speed_labels, index=default_spd_idx, key='sim_speed_sel', label_visibility='collapsed')
        st.session_state['sim_speed'] = speed_map[sel_spd_label]
    if total_steps > 1:
        cur_slider_val = min(step_idx + 1, total_steps)

        def _on_sim_scrub():
            val = st.session_state.get('sim_scrubber', cur_slider_val)
            sim.jump_to_step(val - 1)
        if is_playing or 'sim_scrubber' not in st.session_state or st.session_state.get('sim_scrubber') != cur_slider_val:
            st.session_state['sim_scrubber'] = cur_slider_val
        st.slider('Execution Step', min_value=1, max_value=total_steps, key='sim_scrubber', on_change=_on_sim_scrub, label_visibility='collapsed')
    curr_s = steps[step_idx] if steps and step_idx < len(steps) else {}
    active_edge_s = curr_s.get('active_edge')
    curr_node_s = curr_s.get('current_node')
    if active_edge_s:
        sim_event_text = f'Examining connection {active_edge_s[0]} → {active_edge_s[1]}'
    elif curr_node_s:
        sim_event_text = f'Processing router {curr_node_s}'
    else:
        sim_event_text = curr_s.get('description', 'Frontier active')
    sim_badge_text = 'PLAYING' if is_playing else 'PAUSED' if is_paused else 'COMPLETED' if step_idx >= total_steps - 1 else 'READY'
    sim_badge_bg = '#DCFCE7' if is_playing else '#FEF3C7' if is_paused else '#F1F5F9'
    sim_badge_c = '#15803D' if is_playing else '#B45309' if is_paused else '#475569'
    st.markdown(f'\n        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-left:4px solid #0284C7; border-radius:6px; padding:8px 14px; margin:6px 0 10px 0; display:flex; justify-content:space-between; align-items:center;">\n            <div>\n                <span style="font-weight:700; color:#1E293B; font-size:0.95rem;">Step {step_idx + 1} / {max(1, total_steps)}</span>\n                <span style="color:#64748B; margin:0 8px;">—</span>\n                <span style="color:#334155; font-size:0.9rem;">{sim_event_text}</span>\n            </div>\n            <div>\n                <span style="background:{sim_badge_bg}; color:{sim_badge_c}; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;">\n                    {sim_badge_text}\n                </span>\n            </div>\n        </div>\n        ', unsafe_allow_html=True)
    v_col1, v_col2 = st.columns([1.4, 1.0])
    active_state = sim.get_active_state(graph)
    current_step = active_state.get('step')
    with v_col1:
        fig = build_network_figure(graph, active_state, sel_src, sel_dst, height=440)
        render_plotly(fig, key='sim_graph_active')
        st.markdown("<div style='display:flex; flex-wrap:wrap; gap:12px; font-size:0.78rem; color:#475569; margin-top:4px;'><span><span style='color:#10B981;'>●</span> Source</span><span><span style='color:#F59E0B;'>●</span> Destination</span><span><span style='color:#7C3AED;'>●</span> Active Processing</span><span><span style='color:#0891B2;'>●</span> Discovered</span><span><span style='color:#38BDF8;'>●</span> Visited</span><span><span style='color:#059669;'>●</span> Discovered Route</span><span><span style='color:#94A3B8;'>●</span> Offline</span></div>", unsafe_allow_html=True)
    with v_col2:
        is_bfs = 'BFS' in sim_res.get('algorithm', '')
        is_dijkstra = 'Dijkstra' in sim_res.get('algorithm', '')
        if is_bfs:
            ds_title = 'FIFO Queue (BFS)'
            ds_badge = 'FRONT -> REAR'
        elif is_dijkstra:
            ds_title = 'Min-Priority Queue (Dijkstra)'
            ds_badge = 'MIN DIST -> REAR'
        else:
            ds_title = 'LIFO Stack (DFS)'
            ds_badge = 'TOP -> BOTTOM'
        st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'><span style='font-weight:700; color:{PRIMARY};'>{ds_title}</span><span style='background:#E2E8F0; color:#475569; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>{ds_badge}</span></div>", unsafe_allow_html=True)
        struct_items = current_step.get('structure', []) if current_step else []
        if struct_items:
            pill_html = ' '.join([f"<span class='path-pill'>{item}</span>" for item in struct_items])
            st.markdown(f"<div class='path-pill-container'>{pill_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#1E293B; color:#94A3B8; padding:10px 14px; border-radius:8px; font-style:italic;'>[Structure is Empty]</div>", unsafe_allow_html=True)
        sm1, sm2, sm3 = st.columns(3)
        if is_bfs or is_dijkstra:
            sm1.metric('Enqueues', current_step.get('enqueues', 0) if current_step else 0)
            sm2.metric('Dequeues', current_step.get('dequeues', 0) if current_step else 0)
            sm3.metric('Peak Structure', sim_res.get('max_structure', 0))
        else:
            sm1.metric('Pushes', current_step.get('pushes', 0) if current_step else 0)
            sm2.metric('Pops', current_step.get('pops', 0) if current_step else 0)
            sm3.metric('Peak Stack', sim_res.get('max_structure', 0))
        if current_step:
            nbr_str = f"<b>Neighbor Examined:</b> {current_step.get('neighbor')} (Status: {current_step.get('neighbor_status', 'examined')})" if current_step.get('neighbor') else ''
            route_str = ' -> '.join(current_step.get('current_path', [])) if current_step.get('current_path') else ''
            card_color = PRIMARY if is_bfs else CYAN if is_dijkstra else PURPLE
            st.markdown(render_step_card(step_num=current_step.get('step', step_idx + 1), operation=current_step.get('operation', 'EXPLORE'), description=current_step.get('description', ''), color=card_color, why=current_step.get('why', ''), neighbor_info=nbr_str, route_info=route_str), unsafe_allow_html=True)
        if sim_res.get('success') and sim_res.get('path'):
            st.markdown('##### Packet Forwarding Animation')
            pf_c1, pf_c2 = st.columns(2)
            if pf_c1.button('Step Packet Forward', width='stretch', key='sim_btn_pkt_step'):
                sim.packet_step_forward()
                st.rerun()
            if pf_c2.button('Reset Packet', width='stretch', key='sim_btn_pkt_reset'):
                sim.reset_packet()
                st.rerun()
            st.caption(f"**Status:** {active_state.get('packet_status', '')}")
    st.write('')
    st.markdown('### Traversal Results & Engineering Metrics')
    res_c1, res_c2 = st.columns([1.5, 1])
    with res_c1:
        if sim_res.get('success'):
            st.success(f"Route Discovered: {sim_res.get('message', '')}")
            st.markdown(render_path_pills(sim_res.get('path', [])), unsafe_allow_html=True)
        else:
            st.error(f"Routing Failed: {sim_res.get('message', 'Destination unreachable.')}")
        cost_line = f"• <b>Total Path Cost:</b> <code>{sim_res.get('path_cost', 0.0):.1f}</code><br>" if 'path_cost' in sim_res else ''
        st.markdown(f"<div style='font-size:0.88rem; color:#334155; line-height:1.7;'>• <b>Discovered Path:</b> <code>{(' -> '.join(sim_res.get('path', [])) if sim_res.get('path') else 'None')}</code><br>• <b>Hop Count:</b> <code>{sim_res.get('hops', 0)} hops</code><br>{cost_line}• <b>Traversal Order:</b> <code>{', '.join(sim_res.get('visited', []))}</code><br>• <b>Explored Connections:</b> <code>{sim_res.get('explored_edges_count', 0)}</code><br>• <b>Execution Time:</b> <code>{sim_res.get('execution_time_ms', 0.0):.3f} ms</code></div>", unsafe_allow_html=True)
    with res_c2:
        st.markdown('##### Theoretical Complexity')
        t_comp = 'O((V + E) log V)' if is_dijkstra else 'O(V + E)'
        t_desc = 'Dijkstra extracts minimum tentative distances using a binary heap priority queue.' if is_dijkstra else 'Each online router is queued/stacked at most once, and each incident link is examined at most twice.'
        st.markdown(f'\n            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:14px; font-size:0.86rem;">\n                <b>Time Complexity:</b> <code>{t_comp}</code><br>\n                <span style="color:#64748B;">{t_desc}</span><br><br>\n                <b>Auxiliary Space:</b> <code>O(V)</code><br>\n                <span style="color:#64748B;">For the visited set, parent pointers, and traversal frontier data structure.</span>\n            </div>\n            ', unsafe_allow_html=True)
        full_rep = generate_simulation_report(graph, sim_res, sel_src, sel_dst)
        report_json = json.dumps(full_rep, indent=2)
        report_csv = export_simulation_metrics_csv(full_rep)
        dl_c1, dl_c2, dl_c3 = st.columns(3)
        with dl_c1:
            st.download_button(label='JSON Report', data=report_json, file_name=f'netroute_report_{sel_algo[:3].lower()}_{sel_src}_{sel_dst}.json', mime='application/json', width='stretch', key='sim_dl_report_btn')
        with dl_c2:
            st.download_button(label='CSV Metrics', data=report_csv, file_name=f'netroute_metrics_{sel_algo[:3].lower()}_{sel_src}_{sel_dst}.csv', mime='text/csv', width='stretch', key='sim_dl_csv_btn')
        with dl_c3:
            png_bytes = export_figure_png(fig)
            if png_bytes:
                st.download_button(label='Graph PNG', data=png_bytes, file_name=f'netroute_graph_{sel_algo[:3].lower()}_{sel_src}_{sel_dst}.png', mime='image/png', width='stretch', key='sim_dl_png_btn')
            else:
                st.caption('PNG export requires Kaleido.')
    if st.session_state.get('is_playing', False):
        if step_idx < total_steps - 1:
            delay = st.session_state.get('sim_speed', 0.5)
            time.sleep(delay)
            st.session_state['step_idx'] = step_idx + 1
            st.rerun()
        else:
            st.session_state['is_playing'] = False
            st.session_state['is_paused'] = False
            st.rerun()

def render_bfs_dfs_comparison(graph: Graph):
    st.markdown('## BFS vs. DFS Dual Simulation & Comparison')
    st.markdown('*Synchronized, side-by-side execution of Breadth-First Search and Depth-First Search on the identical network topology snapshot.*')
    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning('Network graph is empty. Please load a topology preset in Topology Studio.')
        return
    cur_src = st.session_state.get('source_id', router_keys[0])
    cur_dst = st.session_state.get('dest_id', router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    if cur_src not in router_keys:
        cur_src = router_keys[0]
    if cur_dst not in router_keys:
        cur_dst = router_keys[-1] if len(router_keys) > 1 else router_keys[0]

    def _on_cmp_endpoints_changed():
        n_s = st.session_state.get('cmp_bar_src')
        n_d = st.session_state.get('cmp_bar_dst')
        if n_s in router_keys and n_d in router_keys:
            st.session_state['source_id'] = n_s
            st.session_state['dest_id'] = n_d
            st.session_state['sb_src_selector'] = n_s
            st.session_state['sb_dst_selector'] = n_d
            st.session_state['sim_sel_src'] = n_s
            st.session_state['sim_sel_dst'] = n_d
            st.session_state['cmp_res'] = None
            st.session_state['cmp_step_idx'] = 0
            st.session_state['cmp_is_playing'] = False
            st.session_state['cmp_is_paused'] = False

    if st.session_state.get('cmp_bar_src') not in router_keys or st.session_state.get('cmp_bar_src') != cur_src:
        st.session_state['cmp_bar_src'] = cur_src
    if st.session_state.get('cmp_bar_dst') not in router_keys or st.session_state.get('cmp_bar_dst') != cur_dst:
        st.session_state['cmp_bar_dst'] = cur_dst
    c_bar1, c_bar2, c_bar3, c_bar4, c_bar5 = st.columns([1.8, 1.8, 1.3, 1.8, 1.1])
    with c_bar1:
        sel_src = st.selectbox('Source Router', options=router_keys, key='cmp_bar_src', on_change=_on_cmp_endpoints_changed)
    with c_bar2:
        sel_dst = st.selectbox('Destination Router', options=router_keys, key='cmp_bar_dst', on_change=_on_cmp_endpoints_changed)
    with c_bar3:
        st.write('')
        st.write('')
        cmp_autoplay_val = st.checkbox('Autoplay on Run', value=st.session_state.get('cmp_autoplay', True), key='cmp_autoplay_cb')
        st.session_state['cmp_autoplay'] = cmp_autoplay_val
    with c_bar4:
        st.write('')
        st.write('')
        run_both = st.button('Run Both Algorithms', width='stretch', type='primary', key='cmp_btn_run_both')
    with c_bar5:
        st.write('')
        st.write('')
        reset_both = st.button('Reset Both', width='stretch', key='cmp_btn_reset_both')
    if reset_both:
        sim.cmp_reset()
        st.rerun()
    if run_both:
        if sel_src not in graph.routers or sel_dst not in graph.routers:
            st.error('Selected source or destination router does not exist in network.')
            return
        if not graph.routers[sel_src].is_online:
            st.error(f"Source router '{sel_src}' is OFFLINE. Cannot initiate packet traversal.")
            return
        if not graph.routers[sel_dst].is_online:
            st.error(f"Destination router '{sel_dst}' is OFFLINE. Cannot reach endpoint.")
            return
        sim.execute_dual_comparison(graph, sel_src, sel_dst)
        st.session_state['cmp_step_idx'] = 0
        st.session_state['cmp_is_playing'] = bool(cmp_autoplay_val)
        st.session_state['cmp_is_paused'] = False
        st.rerun()
    cmp_res = st.session_state.get('cmp_res')
    if not cmp_res and sel_src in graph.routers and sel_dst in graph.routers:
        if graph.routers[sel_src].is_online and graph.routers[sel_dst].is_online:
            cmp_res = sim.execute_dual_comparison(graph, sel_src, sel_dst)
            st.session_state['cmp_step_idx'] = 0
            if cmp_autoplay_val:
                st.session_state['cmp_is_playing'] = True
                st.session_state['cmp_is_paused'] = False
    if not cmp_res:
        st.info('Select online routers and click **Run Both Algorithms** to initiate synchronized comparison.')
        idle_visual = sim.get_step_visual_state(graph, None, 0)
        c_idle1, c_idle2 = st.columns(2)
        with c_idle1:
            fig_b_idle = build_network_figure(graph, idle_visual, sel_src, sel_dst, height=390, title='BFS Topology Snapshot')
            render_plotly(fig_b_idle, key='cmp_idle_bfs')
        with c_idle2:
            fig_d_idle = build_network_figure(graph, idle_visual, sel_src, sel_dst, height=390, title='DFS Topology Snapshot')
            render_plotly(fig_d_idle, key='cmp_idle_dfs')
        return
    bfs_res = cmp_res['bfs']
    dfs_res = cmp_res['dfs']
    bfs_steps = bfs_res.get('steps', [])
    dfs_steps = dfs_res.get('steps', [])
    max_steps = max(len(bfs_steps), len(dfs_steps))
    cmp_idx = st.session_state.get('cmp_step_idx', 0)
    is_playing = st.session_state.get('cmp_is_playing', False)
    is_paused = st.session_state.get('cmp_is_paused', False)
    st.write('')
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5, ctrl_col6 = st.columns([1.2, 1, 1, 1, 1.4, 1.8])
    with ctrl_col1:
        if is_playing:
            if st.button('⏸ Pause', width='stretch', key='cmp_nav_pause', help='Pause animated traversal'):
                sim.cmp_pause()
                st.rerun()
        elif is_paused and 0 < cmp_idx < max_steps - 1:
            if st.button('▶ Resume', width='stretch', type='primary', key='cmp_nav_resume', help='Resume animated traversal'):
                sim.cmp_resume()
                st.rerun()
        elif st.button('▶ Play', width='stretch', type='primary', key='cmp_nav_play', help='Play animated traversal'):
            sim.cmp_play()
            st.rerun()
    with ctrl_col2:
        if st.button('◀ Prev', width='stretch', key='cmp_nav_prev', help='Previous Step'):
            sim.cmp_step_backward()
            st.rerun()
    with ctrl_col3:
        if st.button('Next ▶', width='stretch', key='cmp_nav_next', help='Next Step'):
            sim.cmp_step_forward()
            st.rerun()
    with ctrl_col4:
        if st.button('↺ Restart', width='stretch', key='cmp_nav_restart', help='Restart from Step 1'):
            sim.cmp_restart()
            st.rerun()
    with ctrl_col5:
        if st.button('⏭ Run to End', width='stretch', key='cmp_nav_last', help='Run traversal to completion'):
            sim.cmp_run_to_completion()
            st.rerun()
    with ctrl_col6:
        speed_map = {'Fast (0.2s)': 0.2, 'Normal (0.5s)': 0.5, 'Slow (1.0s)': 1.0}
        cur_spd_val = st.session_state.get('cmp_speed', 0.5)
        speed_labels = list(speed_map.keys())
        default_spd_idx = 1
        for idx_spd, (k, v) in enumerate(speed_map.items()):
            if abs(v - cur_spd_val) < 0.05:
                default_spd_idx = idx_spd
                break
        sel_spd_label = st.selectbox('Playback Speed', options=speed_labels, index=default_spd_idx, key='cmp_speed_sel', label_visibility='collapsed')
        st.session_state['cmp_speed'] = speed_map[sel_spd_label]
    if max_steps > 1:
        cmp_slider_val = min(cmp_idx + 1, max_steps)

        def _on_cmp_scrub():
            val = st.session_state.get('cmp_scrubber', cmp_slider_val)
            sim.cmp_jump_to_step(val - 1)
        if is_playing or 'cmp_scrubber' not in st.session_state or st.session_state.get('cmp_scrubber') != cmp_slider_val:
            st.session_state['cmp_scrubber'] = cmp_slider_val
        st.slider('Synchronized Step Scrubber', min_value=1, max_value=max_steps, key='cmp_scrubber', on_change=_on_cmp_scrub, label_visibility='collapsed')
    bfs_step_idx = min(cmp_idx, len(bfs_steps) - 1) if bfs_steps else 0
    dfs_step_idx = min(cmp_idx, len(dfs_steps) - 1) if dfs_steps else 0
    bfs_s = bfs_steps[bfs_step_idx] if bfs_steps else {}
    dfs_s = dfs_steps[dfs_step_idx] if dfs_steps else {}
    active_edge_bfs = bfs_s.get('active_edge')
    active_edge_dfs = dfs_s.get('active_edge')
    curr_node_bfs = bfs_s.get('current_node')
    curr_node_dfs = dfs_s.get('current_node')
    if active_edge_bfs and active_edge_dfs and (tuple(sorted(active_edge_bfs)) == tuple(sorted(active_edge_dfs))):
        event_text = f'Examining connection {active_edge_bfs[0]} → {active_edge_bfs[1]}'
    elif active_edge_bfs:
        event_text = f'Examining connection {active_edge_bfs[0]} → {active_edge_bfs[1]} (BFS)'
    elif active_edge_dfs:
        event_text = f'Examining connection {active_edge_dfs[0]} → {active_edge_dfs[1]} (DFS)'
    elif curr_node_bfs or curr_node_dfs:
        event_text = f'Processing router {curr_node_bfs or curr_node_dfs}'
    else:
        event_text = bfs_s.get('description', 'Frontier active')
    status_badge_text = 'PLAYING' if is_playing else 'PAUSED' if is_paused else 'COMPLETED' if cmp_idx >= max_steps - 1 else 'READY'
    status_badge_bg = '#DCFCE7' if is_playing else '#FEF3C7' if is_paused else '#F1F5F9'
    status_badge_c = '#15803D' if is_playing else '#B45309' if is_paused else '#475569'
    st.markdown(f'\n        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-left:4px solid #2563EB; border-radius:6px; padding:8px 14px; margin:6px 0 10px 0; display:flex; justify-content:space-between; align-items:center;">\n            <div>\n                <span style="font-weight:700; color:#1E293B; font-size:0.95rem;">Step {cmp_idx + 1} / {max(1, max_steps)}</span>\n                <span style="color:#64748B; margin:0 8px;">—</span>\n                <span style="color:#334155; font-size:0.9rem;">{event_text}</span>\n            </div>\n            <div>\n                <span style="background:{status_badge_bg}; color:{status_badge_c}; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;">\n                    {status_badge_text}\n                </span>\n            </div>\n        </div>\n        ', unsafe_allow_html=True)
    st.markdown('\n        <div style="display:flex; flex-wrap:wrap; gap:12px; font-size:0.78rem; color:#475569; margin-bottom:10px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:6px; padding:6px 12px;">\n            <span><span style="color:#10B981; font-size:1rem;">●</span> Source</span>\n            <span><span style="color:#F59E0B; font-size:1rem;">●</span> Destination</span>\n            <span><span style="color:#7C3AED; font-size:1rem;">●</span> Active Router</span>\n            <span><span style="color:#0891B2; font-size:1rem;">●</span> Discovered Router</span>\n            <span><span style="color:#38BDF8; font-size:1rem;">●</span> Visited Router</span>\n            <span><span style="color:#059669; font-size:1rem;">●</span> Final Route Router</span>\n            <span><span style="color:#94A3B8; font-size:1rem;">●</span> Offline Router</span>\n            <span style="border-left:1px solid #CBD5E1; margin:0 4px;"></span>\n            <span><span style="color:#7C3AED; font-weight:bold;">―</span> Examining Link</span>\n            <span><span style="color:#38BDF8; font-weight:bold;">―</span> Explored Link</span>\n            <span><span style="color:#059669; font-weight:bold; font-size:1rem;">―</span> Route Link</span>\n            <span><span style="color:#EF4444; font-weight:bold;">┄</span> Offline Link</span>\n        </div>\n        ', unsafe_allow_html=True)
    bfs_visual = sim.get_step_visual_state(graph, bfs_res, bfs_step_idx)
    dfs_visual = sim.get_step_visual_state(graph, dfs_res, dfs_step_idx)
    st.write('')
    col_bfs, col_dfs = st.columns(2)
    with col_bfs:
        st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'><span style='font-weight:700; color:#2563EB; font-size:1.05rem;'>Breadth-First Search (BFS)</span><span style='background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>FIFO QUEUE</span></div>", unsafe_allow_html=True)
        fig_bfs = build_network_figure(graph, bfs_visual, sel_src, sel_dst, height=390, title='BFS Traversal Frontier')
        render_plotly(fig_bfs, key='cmp_graph_bfs')
        bfs_curr_step = bfs_visual.get('step') or {}
        bfs_struct = bfs_curr_step.get('structure', [])
        st.markdown("<div style='font-weight:600; font-size:0.85rem; color:#1E293B; margin-top:8px;'>Live Queue Inspector (FIFO):</div>", unsafe_allow_html=True)
        if bfs_struct:
            pills = []
            for q_i, q_item in enumerate(bfs_struct):
                tag = ''
                if q_i == 0 and len(bfs_struct) > 1:
                    tag = " <span style='font-size:0.65rem; color:#1E40AF;'>(Front)</span>"
                elif q_i == 0 and len(bfs_struct) == 1:
                    tag = " <span style='font-size:0.65rem; color:#1E40AF;'>(Front/Rear)</span>"
                elif q_i == len(bfs_struct) - 1:
                    tag = " <span style='font-size:0.65rem; color:#1E40AF;'>(Rear)</span>"
                pills.append(f"<span class='path-pill' style='background:#EFF6FF; border:1px solid #BFDBFE; color:#1E40AF;'>{q_item}{tag}</span>")
            st.markdown(f"<div class='path-pill-container'>{' '.join(pills)}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#F8FAFC; border:1px solid #E2E8F0; color:#94A3B8; padding:6px 12px; border-radius:6px; font-size:0.82rem; font-style:italic;'>[Queue Empty]</div>", unsafe_allow_html=True)
        bq1, bq2, bq3 = st.columns(3)
        bq1.metric('Enqueues', bfs_curr_step.get('enqueues', 0))
        bq2.metric('Dequeues', bfs_curr_step.get('dequeues', 0))
        bq3.metric('Peak Queue', bfs_res.get('max_structure', 0))
        bfs_visited = bfs_curr_step.get('visited', [])
        bfs_parents = bfs_curr_step.get('parents', {})
        with st.expander('BFS Traversal State (Visited & Parents)', expanded=False):
            v_pills = ' '.join([f"<span class='path-pill' style='background:#F0FDF4; border:1px solid #BBF7D0; color:#166534;'>{v}</span>" for v in bfs_visited]) if bfs_visited else 'None'
            st.markdown(f'<b>Visited Routers:</b> {v_pills}', unsafe_allow_html=True)
            par_entries = [f"<b>{child}</b> ← {(par if par else 'None (Source)')}" for child, par in sorted(bfs_parents.items())]
            st.markdown(f"<b>Parent Mapping:</b> {(', '.join(par_entries) if par_entries else 'None')}", unsafe_allow_html=True)
        if bfs_curr_step:
            nbr_info = f"<b>Neighbor Examined:</b> {bfs_curr_step.get('neighbor')} ({bfs_curr_step.get('neighbor_status', '')})" if bfs_curr_step.get('neighbor') else ''
            route_info = ' -> '.join(bfs_curr_step.get('current_path', [])) if bfs_curr_step.get('current_path') else ''
            st.markdown(render_step_card(step_num=bfs_step_idx + 1, operation=bfs_curr_step.get('operation', 'EXPLORE'), description=bfs_curr_step.get('description', ''), color='#2563EB', why=bfs_curr_step.get('why', ''), neighbor_info=nbr_info, route_info=route_info), unsafe_allow_html=True)
        if bfs_visual.get('is_completed'):
            if bfs_res.get('success'):
                path_str = ' → '.join(bfs_res.get('path', []))
                st.success(f"**BFS Route Found:** {path_str} ({bfs_res.get('hops', 0)} hops — Guaranteed Minimum)")
            else:
                st.error('**BFS Result:** Destination unreachable from source.')
    with col_dfs:
        st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'><span style='font-weight:700; color:#7C3AED; font-size:1.05rem;'>Depth-First Search (DFS)</span><span style='background:#EDE9FE; color:#5B21B6; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>LIFO STACK</span></div>", unsafe_allow_html=True)
        fig_dfs = build_network_figure(graph, dfs_visual, sel_src, sel_dst, height=390, title='DFS Traversal Frontier')
        render_plotly(fig_dfs, key='cmp_graph_dfs')
        dfs_curr_step = dfs_visual.get('step') or {}
        dfs_struct = dfs_curr_step.get('structure', [])
        st.markdown("<div style='font-weight:600; font-size:0.85rem; color:#1E293B; margin-top:8px;'>Live Stack Inspector (LIFO):</div>", unsafe_allow_html=True)
        if dfs_struct:
            pills = []
            for s_i, s_item in enumerate(dfs_struct):
                tag = ''
                if s_i == len(dfs_struct) - 1 and len(dfs_struct) > 1:
                    tag = " <span style='font-size:0.65rem; color:#5B21B6;'>(Top)</span>"
                elif s_i == 0 and len(dfs_struct) == 1:
                    tag = " <span style='font-size:0.65rem; color:#5B21B6;'>(Top/Bottom)</span>"
                elif s_i == 0:
                    tag = " <span style='font-size:0.65rem; color:#5B21B6;'>(Bottom)</span>"
                pills.append(f"<span class='path-pill' style='background:#F5F3FF; border:1px solid #DDD6FE; color:#5B21B6;'>{s_item}{tag}</span>")
            st.markdown(f"<div class='path-pill-container'>{' '.join(pills)}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#F8FAFC; border:1px solid #E2E8F0; color:#94A3B8; padding:6px 12px; border-radius:6px; font-size:0.82rem; font-style:italic;'>[Stack Empty]</div>", unsafe_allow_html=True)
        dq1, dq2, dq3 = st.columns(3)
        dq1.metric('Pushes', dfs_curr_step.get('pushes', 0))
        dq2.metric('Pops', dfs_curr_step.get('pops', 0))
        dq3.metric('Peak Stack', dfs_res.get('max_structure', 0))
        dfs_visited = dfs_curr_step.get('visited', [])
        dfs_parents = dfs_curr_step.get('parents', {})
        with st.expander('DFS Traversal State (Visited, Parents & Backtracks)', expanded=False):
            v_pills = ' '.join([f"<span class='path-pill' style='background:#F0FDF4; border:1px solid #BBF7D0; color:#166534;'>{v}</span>" for v in dfs_visited]) if dfs_visited else 'None'
            st.markdown(f'<b>Visited Routers:</b> {v_pills}', unsafe_allow_html=True)
            par_entries = [f"<b>{child}</b> ← {(par if par else 'None (Source)')}" for child, par in sorted(dfs_parents.items())]
            st.markdown(f"<b>Parent Mapping:</b> {(', '.join(par_entries) if par_entries else 'None')}", unsafe_allow_html=True)
            st.markdown(f"<b>Backtrack Event:</b> {('Active (Dead End Backtracking)' if dfs_curr_step.get('is_backtrack') else 'None')}")
        if dfs_curr_step:
            nbr_info = f"<b>Neighbor Examined:</b> {dfs_curr_step.get('neighbor')} ({dfs_curr_step.get('neighbor_status', '')})" if dfs_curr_step.get('neighbor') else ''
            route_info = ' -> '.join(dfs_curr_step.get('current_path', [])) if dfs_curr_step.get('current_path') else ''
            st.markdown(render_step_card(step_num=dfs_step_idx + 1, operation=dfs_curr_step.get('operation', 'EXPLORE'), description=dfs_curr_step.get('description', ''), color='#7C3AED', why=dfs_curr_step.get('why', ''), neighbor_info=nbr_info, route_info=route_info), unsafe_allow_html=True)
        if dfs_visual.get('is_completed'):
            if dfs_res.get('success'):
                path_str = ' → '.join(dfs_res.get('path', []))
                st.info(f"**DFS Route Found:** {path_str} ({dfs_res.get('hops', 0)} hops — Not Guaranteed Shortest)")
            else:
                st.error('**DFS Result:** Destination unreachable from source.')
    st.write('')
    st.markdown('### Comparative Performance Metrics')
    metrics_data = [{'Metric': 'Discovered Path', 'BFS (Breadth-First)': ' -> '.join(bfs_res.get('path', [])) or 'No path', 'DFS (Depth-First)': ' -> '.join(dfs_res.get('path', [])) or 'No path'}, {'Metric': 'Hop Count (Hops)', 'BFS (Breadth-First)': f"{bfs_res.get('hops', 0)} hops (Guaranteed Shortest)", 'DFS (Depth-First)': f"{dfs_res.get('hops', 0)} hops"}, {'Metric': 'Hop Delta', 'BFS (Breadth-First)': '0 (Baseline Minimum)', 'DFS (Depth-First)': f"+{cmp_res.get('hop_delta', 0)} extra hops" if cmp_res.get('hop_delta', 0) > 0 else '0 (Identical hops)'}, {'Metric': 'Routers Visited', 'BFS (Breadth-First)': f"{len(bfs_res.get('visited', []))} of {len(graph.routers)}", 'DFS (Depth-First)': f"{len(dfs_res.get('visited', []))} of {len(graph.routers)}"}, {'Metric': 'Explored Edges', 'BFS (Breadth-First)': str(bfs_res.get('explored_edges_count', 0)), 'DFS (Depth-First)': str(dfs_res.get('explored_edges_count', 0))}, {'Metric': 'Data Structure Operations', 'BFS (Breadth-First)': f"{bfs_res.get('total_enqueues', 0)} Enqueues / {bfs_res.get('total_dequeues', 0)} Dequeues", 'DFS (Depth-First)': f"{dfs_res.get('total_pushes', 0)} Pushes / {dfs_res.get('total_pops', 0)} Pops"}, {'Metric': 'Peak Frontier Depth', 'BFS (Breadth-First)': f"{bfs_res.get('max_structure', 0)} (Max Queue)", 'DFS (Depth-First)': f"{dfs_res.get('max_structure', 0)} (Max Stack)"}, {'Metric': 'Total Simulation Events', 'BFS (Breadth-First)': str(len(bfs_steps)), 'DFS (Depth-First)': str(len(dfs_steps))}, {'Metric': 'Execution Time', 'BFS (Breadth-First)': f"{bfs_res.get('execution_time_ms', 0.0):.3f} ms", 'DFS (Depth-First)': f"{dfs_res.get('execution_time_ms', 0.0):.3f} ms"}, {'Metric': 'Theoretical Time Complexity', 'BFS (Breadth-First)': 'O(V + E)', 'DFS (Depth-First)': 'O(V + E)'}, {'Metric': 'Theoretical Space Complexity', 'BFS (Breadth-First)': 'O(V)', 'DFS (Depth-First)': 'O(V)'}]
    st.dataframe(pd.DataFrame(metrics_data), width='stretch', hide_index=True)
    st.markdown('### Engineering Verdict')
    st.markdown(f"""\n        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-left:5px solid {cmp_res.get('verdict_color', PRIMARY)}; border-radius:8px; padding:16px; margin-bottom:12px;">\n            <div style="font-weight:700; font-size:1.1rem; color:{cmp_res.get('verdict_color', PRIMARY)}; margin-bottom:4px;">\n                {cmp_res.get('verdict_title', '')}\n            </div>\n            <div style="font-size:0.92rem; color:{TEXT_MAIN}; line-height:1.5;">\n                {cmp_res.get('verdict_summary', '')}\n            </div>\n        </div>\n        """, unsafe_allow_html=True)
    with st.expander('Route Strategy Comparison (BFS vs. DFS vs. Dijkstra)', expanded=False):
        st.markdown('*Evaluation of unweighted shortest hops (BFS), branch exploration (DFS), and weighted least-cost paths (Dijkstra).*')
        strat_res = compare_routing_strategies(graph, sel_src, sel_dst)
        b_run = strat_res['bfs']
        d_run = strat_res['dfs']
        dj_run = strat_res['dijkstra']
        strat_table = [{'Property': 'Guaranteed Property', 'BFS (Breadth-First)': 'Minimum Hops (Unweighted)', 'DFS (Depth-First)': 'Deep Branch Exploration', 'Dijkstra (Priority Queue)': 'Minimum Total Cost (Weighted)'}, {'Property': 'Discovered Path', 'BFS (Breadth-First)': ' -> '.join(b_run.get('path', [])) or 'No path', 'DFS (Depth-First)': ' -> '.join(d_run.get('path', [])) or 'No path', 'Dijkstra (Priority Queue)': ' -> '.join(dj_run.get('path', [])) or 'No path'}, {'Property': 'Hop Count', 'BFS (Breadth-First)': f"{b_run.get('hops', 0)} hops", 'DFS (Depth-First)': f"{d_run.get('hops', 0)} hops", 'Dijkstra (Priority Queue)': f"{dj_run.get('hops', 0)} hops"}, {'Property': 'Total Accumulated Cost', 'BFS (Breadth-First)': f"{b_run.get('path_cost', 0.0):.1f}", 'DFS (Depth-First)': f"{d_run.get('path_cost', 0.0):.1f}", 'Dijkstra (Priority Queue)': f"{dj_run.get('path_cost', 0.0):.1f} (Least Cost)"}, {'Property': 'Routers Visited', 'BFS (Breadth-First)': str(len(b_run.get('visited', []))), 'DFS (Depth-First)': str(len(d_run.get('visited', []))), 'Dijkstra (Priority Queue)': str(len(dj_run.get('visited', [])))}, {'Property': 'Execution Time (ms)', 'BFS (Breadth-First)': f"{b_run.get('execution_time_ms', 0.0):.3f} ms", 'DFS (Depth-First)': f"{d_run.get('execution_time_ms', 0.0):.3f} ms", 'Dijkstra (Priority Queue)': f"{dj_run.get('execution_time_ms', 0.0):.3f} ms"}, {'Property': 'Theoretical Time Complexity', 'BFS (Breadth-First)': 'O(V + E)', 'DFS (Depth-First)': 'O(V + E)', 'Dijkstra (Priority Queue)': 'O((V + E) log V)'}, {'Property': 'Auxiliary Space Complexity', 'BFS (Breadth-First)': 'O(V)', 'DFS (Depth-First)': 'O(V)', 'Dijkstra (Priority Queue)': 'O(V)'}]
        st.dataframe(pd.DataFrame(strat_table), width='stretch', hide_index=True)
        st.info('Notice: BFS optimizes hop count across unweighted edges, whereas Dijkstra minimizes cumulative link weights. DFS does not guarantee either optimality property.')
    comp_rep = generate_comparison_report(graph, cmp_res, sel_src, sel_dst)
    report_json = json.dumps(comp_rep, indent=2)
    report_csv = export_comparison_metrics_csv(comp_rep)
    dl_c1, dl_c2, dl_c3, dl_c4 = st.columns(4)
    with dl_c1:
        st.download_button(label='Download JSON Report', data=report_json, file_name=f'netroute_comparison_bfs_vs_dfs_{sel_src}_{sel_dst}.json', mime='application/json', width='stretch', key='cmp_dl_report_btn')
    with dl_c2:
        st.download_button(label='Download CSV Metrics', data=report_csv, file_name=f'netroute_comparison_{sel_src}_{sel_dst}.csv', mime='text/csv', width='stretch', key='cmp_dl_csv_btn')
    with dl_c3:
        bfs_png = export_figure_png(fig_bfs)
        if bfs_png:
            st.download_button(label='BFS Graph PNG', data=bfs_png, file_name=f'netroute_bfs_graph_{sel_src}_{sel_dst}.png', mime='image/png', width='stretch', key='cmp_dl_bfs_png')
        else:
            st.caption('BFS PNG requires Kaleido.')
    with dl_c4:
        dfs_png = export_figure_png(fig_dfs)
        if dfs_png:
            st.download_button(label='DFS Graph PNG', data=dfs_png, file_name=f'netroute_dfs_graph_{sel_src}_{sel_dst}.png', mime='image/png', width='stretch', key='cmp_dl_dfs_png')
        else:
            st.caption('DFS PNG requires Kaleido.')
    if st.session_state.get('cmp_is_playing', False):
        if cmp_idx < max_steps - 1:
            delay = st.session_state.get('cmp_speed', 0.5)
            time.sleep(delay)
            st.session_state['cmp_step_idx'] = cmp_idx + 1
            st.rerun()
        else:
            st.session_state['cmp_is_playing'] = False
            st.session_state['cmp_is_paused'] = False
            st.rerun()

def render_network_failure_lab(graph: Graph):
    st.markdown('## Network Failure Lab')
    st.markdown('*Interactive sandbox for multi-router and link failure simulation on a reversible scenario clone, measuring reachability and route divergence.*')
    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning('Network graph is empty. Please configure routers first.')
        return
    edges = graph.get_edges()
    edge_str_map = {f'{u} <—> {v}': (u, v) for u, v in edges}
    edge_options = list(edge_str_map.keys())
    cur_src = st.session_state.get('source_id', router_keys[0])
    cur_dst = st.session_state.get('dest_id', router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    s_idx = router_keys.index(cur_src) if cur_src in router_keys else 0
    d_idx = router_keys.index(cur_dst) if cur_dst in router_keys else len(router_keys) - 1
    fl_c1, fl_c2 = st.columns(2)
    with fl_c1:
        sel_src = st.selectbox('Source (Origin)', options=router_keys, index=s_idx, key='fl_sel_src')
    with fl_c2:
        sel_dst = st.selectbox('Destination (Target)', options=router_keys, index=d_idx, key='fl_sel_dst')
    f_in1, f_in2 = st.columns(2)
    with f_in1:
        failed_routers_sel = st.multiselect('Select Routers to Take Offline', options=router_keys, default=st.session_state.get('fl_selected_routers', []), help='Routers marked offline will reject all incoming and outgoing packet transmissions.', key='fl_routers_multi')
    with f_in2:
        failed_links_sel = st.multiselect('Select Transmission Links to Sever', options=edge_options, default=st.session_state.get('fl_selected_links', []), help='Severed links will be impassable for packet routing.', key='fl_links_multi')
    clean_failed_edges = [edge_str_map[s] for s in failed_links_sel if s in edge_str_map]
    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1.5, 1.2, 1.2, 2])
    with btn_c1:
        sim_btn = st.button('Apply Failure Scenario', type='primary', width='stretch', key='fl_btn_simulate')
    with btn_c2:
        reset_btn = st.button('Reset Scenario', width='stretch', key='fl_btn_reset')
    with btn_c3:
        restore_btn = st.button('Restore Baseline', width='stretch', key='fl_btn_restore')
    with btn_c4:
        commit_btn = st.button('Commit Scenario to Active Topology', width='stretch', key='fl_btn_commit', help='Permanently applies the offline router states and severed link states to the active network graph.')
    if reset_btn or restore_btn:
        st.session_state['fl_selected_routers'] = []
        st.session_state['fl_selected_links'] = []
        st.session_state.pop('fl_scenario_data', None)
        st.rerun()
    if commit_btn:
        for r in failed_routers_sel:
            if r in graph.routers:
                graph.routers[r].is_online = False
        for u, v in clean_failed_edges:
            graph.failed_edges.add(tuple(sorted((u, v))))
        sim.invalidate_simulation()
        st.success(f'Permanently committed {len(failed_routers_sel)} router outages and {len(clean_failed_edges)} link severances to active network.')
        st.rerun()
    scenario_data = simulate_failure(graph, failed_routers_sel, clean_failed_edges, sel_src, sel_dst)
    st.session_state['fl_scenario_data'] = scenario_data
    impact = scenario_data['impact_analysis']
    base_info = scenario_data['baseline']
    scen_info = scenario_data['failure_scenario']
    scen_graph: Graph = scenario_data['scenario_graph']
    st.write('')
    if impact.get('destination_became_unreachable'):
        st.error(f'**CRITICAL ROUTE SEVERANCE**: Destination router **{sel_dst}** became completely unreachable from **{sel_src}**! The selected failures severed all path redundancies.')
    elif impact.get('route_survived'):
        hop_delta = impact.get('hop_delta', 0)
        cost_delta = impact.get('cost_delta', 0.0)
        delta_str = ''
        if hop_delta and hop_delta > 0:
            delta_str = f'Route diverted (+{hop_delta} extra hops, cost delta: +{cost_delta:.1f}).'
        else:
            delta_str = 'Route remained identical or equivalent.'
        st.success(f'**ROUTE SURVIVED**: Packets can still reach **{sel_dst}** from **{sel_src}**! {delta_str}')
    else:
        st.info('Baseline and Scenario evaluated.')
    if impact.get('disconnected_routers'):
        st.warning(f"**Isolated Routers**: Outages isolated `{', '.join(impact['disconnected_routers'])}` from origin {sel_src}.")
    st.write('')
    g_c1, g_c2 = st.columns(2)
    with g_c1:
        st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'><span style='font-weight:700; color:#2563EB; font-size:1.05rem;'>Baseline Topology</span><span style='background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>PRE-FAILURE</span></div>", unsafe_allow_html=True)
        base_bfs = base_info.get('bfs') or {}
        base_vis = {'is_completed': True, 'route_nodes': base_bfs.get('path', []), 'route_edges': [(base_bfs.get('path')[i], base_bfs.get('path')[i + 1]) for i in range(len(base_bfs.get('path', [])) - 1)] if base_bfs.get('path') else []}
        fig_base = build_network_figure(graph, base_vis, sel_src, sel_dst, height=390, title='Baseline Network & Active Route')
        render_plotly(fig_base, key='fl_base_graph')
        if base_bfs.get('path'):
            st.caption(f"**Baseline Route:** `{' -> '.join(base_bfs['path'])}` ({base_bfs.get('hops', 0)} hops)")
        else:
            st.caption('No route existed in baseline.')
    with g_c2:
        st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'><span style='font-weight:700; color:#EF4444; font-size:1.05rem;'>Simulated Failure Scenario</span><span style='background:#FEE2E2; color:#991B1B; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;'>SCENARIO CLONE</span></div>", unsafe_allow_html=True)
        scen_bfs = scen_info.get('bfs') or {}
        scen_vis = {'is_completed': True, 'route_nodes': scen_bfs.get('path', []), 'route_edges': [(scen_bfs.get('path')[i], scen_bfs.get('path')[i + 1]) for i in range(len(scen_bfs.get('path', [])) - 1)] if scen_bfs.get('path') else []}
        fig_scen = build_network_figure(scen_graph, scen_vis, sel_src, sel_dst, height=390, title='Failure Scenario & Rerouted Path')
        render_plotly(fig_scen, key='fl_scen_graph')
        if scen_bfs.get('path'):
            st.caption(f"**Scenario Route:** `{' -> '.join(scen_bfs['path'])}` ({scen_bfs.get('hops', 0)} hops)")
        else:
            st.caption('**Scenario Route:** None (Unreachable)')
    st.write('')
    st.markdown('### Before vs. After Failure Scenario Metrics')
    b_dijk = base_info.get('dijkstra') or {}
    s_dijk = scen_info.get('dijkstra') or {}
    comp_rows = [{'Property': 'Connected Subnets (Components)', 'Baseline (Pre-Failure)': str(base_info.get('component_count', 1)), 'Failure Scenario (Post-Failure)': str(scen_info.get('component_count', 1)), 'Delta': f"+{impact.get('component_delta', 0)} Subnets" if impact.get('component_delta', 0) > 0 else '0 (No split)'}, {'Property': 'Destination Reachability', 'Baseline (Pre-Failure)': 'REACHABLE' if base_bfs and base_bfs.get('success') else 'UNREACHABLE', 'Failure Scenario (Post-Failure)': 'REACHABLE' if scen_bfs and scen_bfs.get('success') else 'UNREACHABLE', 'Delta': 'Severed' if impact.get('destination_became_unreachable') else 'Survived' if impact.get('route_survived') else 'Unchanged'}, {'Property': 'Discovered Route', 'Baseline (Pre-Failure)': ' -> '.join(base_bfs.get('path', [])) or 'None', 'Failure Scenario (Post-Failure)': ' -> '.join(scen_bfs.get('path', [])) or 'None', 'Delta': 'Diverted' if base_bfs.get('path') != scen_bfs.get('path') else 'Identical'}, {'Property': 'Hop Count', 'Baseline (Pre-Failure)': f"{base_bfs.get('hops', 0)} hops", 'Failure Scenario (Post-Failure)': f"{scen_bfs.get('hops', 0)} hops" if scen_bfs.get('success') else 'N/A', 'Delta': f"{impact.get('hop_delta'):+d} hops" if impact.get('hop_delta') is not None else 'N/A'}, {'Property': 'Least-Cost Route Weight', 'Baseline (Pre-Failure)': f"{b_dijk.get('path_cost', 0.0):.1f}", 'Failure Scenario (Post-Failure)': f"{s_dijk.get('path_cost', 0.0):.1f}" if s_dijk.get('success') else 'N/A', 'Delta': f"{impact.get('cost_delta'):+.1f}" if impact.get('cost_delta') is not None else 'N/A'}, {'Property': 'Critical Bridges Remaining', 'Baseline (Pre-Failure)': str(len(base_info.get('bridges', []))), 'Failure Scenario (Post-Failure)': str(len(scen_info.get('bridges', []))), 'Delta': str(len(scen_info.get('bridges', [])) - len(base_info.get('bridges', [])))}, {'Property': 'Articulation Points Remaining', 'Baseline (Pre-Failure)': str(len(base_info.get('articulation_points', []))), 'Failure Scenario (Post-Failure)': str(len(scen_info.get('articulation_points', []))), 'Delta': str(len(scen_info.get('articulation_points', [])) - len(base_info.get('articulation_points', [])))}]
    st.dataframe(pd.DataFrame(comp_rows), width='stretch', hide_index=True)
    st.write('')
    scen_export_dict = {'report_type': 'NetRoute Failure Scenario Report', 'schema_version': '1.0', 'timestamp': scenario_data['timestamp'], 'topology_name': graph.name, 'failed_routers': failed_routers_sel, 'failed_edges': [list(e) for e in clean_failed_edges], 'endpoints': {'source': sel_src, 'destination': sel_dst}, 'impact_analysis': impact, 'baseline': {'component_count': base_info['component_count'], 'route': base_bfs.get('path', []), 'hops': base_bfs.get('hops', 0), 'cost': b_dijk.get('path_cost', 0.0)}, 'failure_scenario': {'component_count': scen_info['component_count'], 'route': scen_bfs.get('path', []), 'hops': scen_bfs.get('hops', 0), 'cost': s_dijk.get('path_cost', 0.0)}}
    scen_json = json.dumps(scen_export_dict, indent=2)
    scen_csv = export_failure_scenario_csv(scenario_data)
    dl_f1, dl_f2, dl_f3 = st.columns(3)
    with dl_f1:
        st.download_button(label='Download Failure Scenario JSON', data=scen_json, file_name=f'netroute_failure_scenario_{sel_src}_{sel_dst}.json', mime='application/json', width='stretch', key='fl_dl_json')
    with dl_f2:
        st.download_button(label='Download Scenario CSV', data=scen_csv, file_name=f'netroute_failure_scenario_{sel_src}_{sel_dst}.csv', mime='text/csv', width='stretch', key='fl_dl_csv')
    with dl_f3:
        scen_png = export_figure_png(fig_scen)
        if scen_png:
            st.download_button(label='Scenario Graph PNG', data=scen_png, file_name=f'netroute_failure_scenario_{sel_src}_{sel_dst}.png', mime='image/png', width='stretch', key='fl_dl_png')
        else:
            st.caption('PNG requires Kaleido.')

def render_data_structures_inspector(graph: Graph):
    st.markdown('## Data Structures Inspector')
    st.markdown('*Inspect live graph representations, traversal queue/stack internal states, and algorithm evaluations.*')
    tab_graph, tab_struct, tab_search_sort = st.tabs(['Graph Representations', 'Traversal Queue & Stack', 'Searching & Sorting Algorithms'])
    with tab_graph:
        st.markdown('### Adjacency List & Adjacency Matrix')
        gr_c1, gr_c2 = st.columns(2)
        with gr_c1:
            st.markdown('#### Adjacency List O(V + E)')
            adj_list = graph.get_adjacency_list()
            adj_rows = [{'Router': r, 'Neighbors (Degree)': f"{(', '.join(nbrs) if nbrs else 'None')} ({len(nbrs)})"} for r, nbrs in adj_list.items()]
            st.dataframe(pd.DataFrame(adj_rows), width='stretch', hide_index=True)
        with gr_c2:
            st.markdown('#### Adjacency Matrix O(V²)')
            nodes, matrix = graph.get_adjacency_matrix()
            if nodes:
                df_matrix = pd.DataFrame(matrix, index=nodes, columns=nodes)
                st.dataframe(df_matrix, width='stretch')
            else:
                st.info('Network is empty.')
    with tab_struct:
        st.markdown('### Traversal Queue & Stack State')
        sim_res = st.session_state.get('sim_res')
        if sim_res and sim_res.get('steps'):
            st.caption(f"Displaying data structure progression for **{sim_res.get('algorithm', '')}**")
            step_rows = []
            for s in sim_res['steps']:
                step_rows.append({'Step': s.get('step'), 'Operation': s.get('operation'), 'Active Router': s.get('current_node'), 'Front / Top': s.get('front', s.get('top')), 'Structure Contents': f"[{', '.join(s.get('structure', []))}]", 'Size': len(s.get('structure', []))})
            st.dataframe(pd.DataFrame(step_rows), width='stretch', hide_index=True)
        else:
            st.info('Run a simulation in the Traversal Simulator to populate the live queue/stack state trace.')
    with tab_search_sort:
        st.markdown('### Searching & Sorting Demonstration')
        sub_search, sub_sort = st.tabs(['Linear vs. Binary Search', 'Bubble vs. Insertion Sort'])
        with sub_search:
            st.markdown('#### Searching Evaluation: Linear vs. Binary Search')
            unsorted_dataset, sorted_dataset = get_adaptive_datasets(graph)
            search_target = st.text_input('Search Target Router ID', value=sorted_dataset[0] if sorted_dataset else 'N1', key='ds_search_target').strip().upper()
            if st.button('Evaluate Search Algorithms', type='primary', key='ds_btn_run_search'):
                lin_res = linear_search(sorted_dataset, search_target)
                bin_res = binary_search(sorted_dataset, search_target)
                st.session_state['search_eval'] = {'linear': lin_res, 'binary': bin_res}
            search_eval = st.session_state.get('search_eval')
            if search_eval:
                l_res = search_eval['linear']
                b_res = search_eval['binary']
                s_res1, s_res2 = st.columns(2)
                with s_res1:
                    st.markdown('##### Linear Search O(n)')
                    st.markdown(f"• **Found:** {l_res.get('found')} at index {l_res.get('index')}")
                    st.markdown(f"• **Comparisons:** {l_res.get('comparisons')}")
                    st.markdown(f"• **Time:** {l_res.get('execution_time_ms', 0.0):.4f} ms")
                    st.caption('Checks elements sequentially from index 0.')
                with s_res2:
                    st.markdown('##### Binary Search O(log n)')
                    st.markdown(f"• **Found:** {b_res.get('found')} at index {b_res.get('index')}")
                    st.markdown(f"• **Comparisons:** {b_res.get('comparisons')}")
                    st.markdown(f"• **Time:** {b_res.get('execution_time_ms', 0.0):.4f} ms")
                    st.caption('Requires sorted array; halves search space per iteration.')
        with sub_sort:
            st.markdown('#### Sorting Evaluation: Bubble Sort vs. Insertion Sort')
            unsorted_dataset, _ = get_adaptive_datasets(graph)
            st.caption(f'Input Dataset: `{unsorted_dataset}`')
            if st.button('Evaluate Sorting Algorithms', type='primary', key='ds_btn_run_sort'):
                bub_res = bubble_sort(unsorted_dataset)
                ins_res = insertion_sort(unsorted_dataset)
                st.session_state['sort_eval'] = {'bubble': bub_res, 'insertion': ins_res}
            sort_eval = st.session_state.get('sort_eval')
            if sort_eval:
                bu_res = sort_eval['bubble']
                in_res = sort_eval['insertion']
                st_res1, st_res2 = st.columns(2)
                with st_res1:
                    st.markdown('##### Bubble Sort O(n²)')
                    st.markdown(f"• **Comparisons:** {bu_res.get('comparisons')}")
                    st.markdown(f"• **Swaps:** {bu_res.get('swaps')}")
                    st.markdown(f"• **Time:** {bu_res.get('execution_time_ms', 0.0):.4f} ms")
                    st.caption(f"Sorted output: `{bu_res.get('sorted_dataset')}`")
                with st_res2:
                    st.markdown('##### Insertion Sort O(n²)')
                    st.markdown(f"• **Comparisons:** {in_res.get('comparisons')}")
                    st.markdown(f"• **Shifts:** {in_res.get('shifts')}")
                    st.markdown(f"• **Time:** {in_res.get('execution_time_ms', 0.0):.4f} ms")
                    st.caption(f"Sorted output: `{in_res.get('sorted_dataset')}`")

def render_traversal_tree(graph: Graph):
    st.markdown('## Routing Traversal Tree')
    st.markdown('*Hierarchical spanning tree derived from traversal parent pointers, with structural invariant verification.*')
    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning('Network graph is empty.')
        return
    cur_src = st.session_state.get('source_id', router_keys[0])
    cur_dst = st.session_state.get('dest_id', router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    t_c1, t_c2, t_c3 = st.columns([2, 2, 1.5])
    with t_c1:
        tree_src = st.selectbox('Root Router (Source)', options=router_keys, index=router_keys.index(cur_src) if cur_src in router_keys else 0, key='tree_src_sel')
    with t_c2:
        tree_dst = st.selectbox('Target Router (Destination)', options=router_keys, index=router_keys.index(cur_dst) if cur_dst in router_keys else len(router_keys) - 1, key='tree_dst_sel')
    with t_c3:
        st.write('')
        st.write('')
        run_tree = st.button('Build Traversal Tree', width='stretch', type='primary', key='tree_btn_build')
    cached_tree = st.session_state.get('tree_data')
    if run_tree or not cached_tree or cached_tree.get('root') != tree_src:
        bfs_res = bfs(graph, tree_src, tree_dst)
        parents = bfs_res.get('parents', {})
        tree_data = build_traversal_tree(parents, tree_src, tree_dst)
        st.session_state['tree_data'] = tree_data
    else:
        tree_data = cached_tree
    st.write('')
    tree_col1, tree_col2 = st.columns([1.4, 1.0])
    with tree_col1:
        st.markdown('#### Spanning Tree Visualization')
        fig = build_traversal_tree_figure(tree_data, tree_src, tree_dst, height=450)
        render_plotly(fig, key='tree_plot')
        st.caption('Root router is positioned at the top; child routers descend by distance level. Discovered path highlighted in green.')
    with tree_col2:
        st.markdown('#### Mathematical Invariants')
        inv = tree_data.get('invariants', {})
        v_tree = inv.get('num_vertices', 0)
        e_tree = inv.get('num_edges', 0)
        is_valid = inv.get('is_valid_tree', False)
        st.markdown(f"""\n            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-left:4px solid {('#10B981' if is_valid else '#EF4444')}; border-radius:6px; padding:12px; margin-bottom:12px;">\n                <div style="font-weight:700; color:{('#10B981' if is_valid else '#EF4444')};">\n                    {('VALID ROOTED TREE' if is_valid else 'INVALID SPANNING TREE')}\n                </div>\n                <div style="font-size:0.86rem; color:#334155; margin-top:4px;">\n                    • <b>Tree Vertices (V_tree):</b> {v_tree}<br>\n                    • <b>Tree Edges (E_tree):</b> {e_tree} (Must equal V_tree - 1)<br>\n                    • <b>Acyclic Property:</b> {inv.get('is_acyclic', True)}<br>\n                    • <b>Connected Component:</b> {inv.get('is_connected', True)}\n                </div>\n            </div>\n            """, unsafe_allow_html=True)
        unreachable = tree_data.get('unreachable_nodes', [])
        if unreachable:
            st.warning(f"Unreachable Nodes ({len(unreachable)}): {', '.join(unreachable)}")
        else:
            st.success('All network routers are spanned by the traversal tree.')
        st.markdown('##### Predecessor Pointers')
        levels = tree_data.get('levels', {})
        p_rows = []
        for node in tree_data.get('nodes', []):
            p_rows.append({'Router': node, 'Parent': tree_data.get('parents', {}).get(node, 'Root (None)'), 'Depth Level': levels.get(node, 0)})
        st.dataframe(pd.DataFrame(p_rows), width='stretch', hide_index=True)

def render_routing_table_simulator(graph: Graph):
    st.markdown('## Routing Table Simulator')
    st.markdown('*Simulate hop-by-hop packet forwarding using local router routing tables, detecting loops, offline routers, and link severances.*')
    router_keys = sorted(list(graph.routers.keys()))
    if not router_keys:
        st.warning('Network graph is empty.')
        return
    cur_src = st.session_state.get('source_id', router_keys[0])
    cur_dst = st.session_state.get('dest_id', router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    f_col1, f_col2, f_col3 = st.columns([2, 2, 1.5])
    with f_col1:
        fwd_src = st.selectbox('Source Router', options=router_keys, index=router_keys.index(cur_src) if cur_src in router_keys else 0, key='fwd_src_sel')
    with f_col2:
        fwd_dst = st.selectbox('Destination Router', options=router_keys, index=router_keys.index(cur_dst) if cur_dst in router_keys else len(router_keys) - 1, key='fwd_dst_sel')
    with f_col3:
        st.write('')
        st.write('')
        run_fwd = st.button('Simulate Forwarding', width='stretch', type='primary', key='fwd_btn_run')
    if run_fwd or st.session_state.get('table_fwd_res') is None:
        fwd_res = sim.simulate_table_forwarding(graph, fwd_src, fwd_dst)
        st.session_state['table_fwd_res'] = fwd_res
    fwd_res = st.session_state.get('table_fwd_res')
    st.write('')
    if fwd_res:
        if fwd_res.get('success'):
            st.success(f"Forwarding Succeeded: {fwd_res.get('message', '')}")
            st.markdown(render_path_pills(fwd_res.get('path', [])), unsafe_allow_html=True)
        else:
            st.error(f"Forwarding Failed: {fwd_res.get('message', '')}")
        st.markdown('### Hop-by-Hop Forwarding Log')
        fwd_steps = fwd_res.get('steps', [])
        if fwd_steps:
            trace_rows = []
            for s in fwd_steps:
                entry = s.get('table_entry', {})
                trace_rows.append({'Hop': s.get('step'), 'Current Router': s.get('current_router'), 'Action': s.get('action'), 'Next Hop': s.get('next_hop'), 'Metric': entry.get('hops', '-'), 'Description': s.get('description')})
            st.dataframe(pd.DataFrame(trace_rows), width='stretch', hide_index=True)
    st.write('')
    st.markdown('### Router Routing Table Inspector')
    insp_r = st.selectbox('Inspect Local Routing Table For Router', options=router_keys, key='fwd_inspect_r')
    r_table = graph.generate_routing_table(insp_r)
    if r_table:
        st.dataframe(pd.DataFrame(r_table), width='stretch', hide_index=True)

def render_network_analysis(graph: Graph):
    st.markdown('## Network Analysis & Resilience')
    st.markdown('*Comprehensive graph topology diagnostics, router degree distribution, Tarjan resilience analysis (Bridges & Articulation Points), and reachability analysis.*')
    summary = graph.get_summary()
    bridges = find_bridges(graph)
    aps = find_articulation_points(graph)
    na1, na2, na3, na4, na5, na6 = st.columns(6)
    na1.metric('Total Routers', summary['total_routers'], f"{summary['online_routers']} online")
    na2.metric('Total Links', summary['total_edges'], f'{len(graph.failed_edges)} failed')
    na3.metric('Components', summary['component_count'])
    na4.metric('Connected', 'YES' if summary['is_connected'] else 'NO')
    na5.metric('Critical Bridges', len(bridges), 'Cut Edges' if bridges else 'Biconnected')
    na6.metric('Articulation Points', len(aps), 'Cut Vertices' if aps else 'Resilient')
    st.write('')
    st.markdown('### Topology Resilience Map')
    st.caption('Bridges (amber dashed connections with ⚡Bridge badges) and Articulation Points (amber routers with [AP] badges) represent single points of failure.')
    cur_src = st.session_state.get('source_id', 'N1')
    cur_dst = st.session_state.get('dest_id', 'N7')
    empty_vis = {'is_completed': False}
    fig_resil = build_network_figure(graph, empty_vis, cur_src, cur_dst, height=420, title='Network Resilience Map (Critical Bridges & Articulation Points)', highlight_bridges=set(bridges), highlight_aps=set(aps))
    render_plotly(fig_resil, key='na_resilience_fig')
    st.write('')
    res_tab1, res_tab2 = st.columns(2)
    with res_tab1:
        st.markdown('#### Critical Bridges (Cut Edges)')
        if bridges:
            b_rows = []
            for u, v in bridges:
                test_g = graph.clone()
                test_g.failed_edges.add(tuple(sorted((u, v))))
                test_comps = test_g.get_connected_components()
                b_rows.append({'Bridge Link': f'{u} <—> {v}', 'Cost': str(graph.get_weight(u, v)), 'Subnets After Removal': str(len(test_comps)), 'Impact': f'Partitions network into {len(test_comps)} isolated components'})
            st.dataframe(pd.DataFrame(b_rows), width='stretch', hide_index=True)
        else:
            st.success('No critical bridges detected. Network links exhibit 2-edge-connected cyclic redundancy.')
    with res_tab2:
        st.markdown('#### Critical Articulation Points (Cut Vertices)')
        if aps:
            ap_rows = []
            for node in aps:
                test_g = graph.clone()
                if node in test_g.routers:
                    test_g.routers[node].is_online = False
                test_comps = test_g.get_connected_components()
                ap_rows.append({'Router ID': node, 'Name': graph.routers[node].name, 'Degree': str(len(graph.adjacency.get(node, []))), 'Subnets After Outage': str(len(test_comps)), 'Impact': f'Outage isolates remaining routers into {len(test_comps)} subnets'})
            st.dataframe(pd.DataFrame(ap_rows), width='stretch', hide_index=True)
        else:
            st.success('No critical articulation points detected. Network topology is 2-vertex-connected.')
    st.write('')
    with st.expander('Interactive Resilience Removal Experiment', expanded=False):
        st.markdown('*Select a critical bridge or articulation point to simulate its removal and observe the instant connectivity impact.*')
        exp_c1, exp_c2, exp_c3 = st.columns([2, 2, 1.5])
        sim_options = []
        for u, v in bridges:
            sim_options.append(f'Bridge: {u} <—> {v}')
        for a in aps:
            sim_options.append(f'Articulation Point: {a} ({graph.routers[a].name})')
        if sim_options:
            with exp_c1:
                sel_failure = st.selectbox('Element to Remove', options=sim_options, key='na_sel_failure')
            with exp_c2:
                eval_src = st.selectbox('Origin Router', options=sorted(list(graph.routers.keys())), key='na_eval_src')
            with exp_c3:
                st.write('')
                st.write('')
                run_test = st.button('Simulate Removal', type='primary', width='stretch', key='na_btn_sim_remove')
            if run_test or 'na_sim_result' in st.session_state:
                if run_test:
                    test_g = graph.clone()
                    if sel_failure.startswith('Bridge:'):
                        b_str = sel_failure.replace('Bridge:', '').strip()
                        u_part, v_part = [p.strip() for p in b_str.split('<—>')]
                        test_g.failed_edges.add(tuple(sorted((u_part, v_part))))
                    else:
                        ap_id = sel_failure.split(':')[1].split('(')[0].strip()
                        if ap_id in test_g.routers:
                            test_g.routers[ap_id].is_online = False
                    new_comps = test_g.get_connected_components()
                    reach_nodes = test_g.get_reachable_nodes(eval_src)
                    all_nodes = set(graph.routers.keys())
                    lost_nodes = sorted(list(all_nodes - set(reach_nodes)))
                    st.session_state['na_sim_result'] = {'element': sel_failure, 'origin': eval_src, 'new_comps_count': len(new_comps), 'new_comps': [sorted(list(c)) for c in new_comps], 'reachable_count': len(reach_nodes), 'lost_nodes': lost_nodes}
                res_info = st.session_state.get('na_sim_result')
                if res_info:
                    st.warning(f"**Simulated Removal of {res_info['element']}**: Network split into **{res_info['new_comps_count']} components**! Routers reachable from {res_info['origin']}: `{res_info['reachable_count']}` of {len(graph.routers)}. Isolated routers: `{(', '.join(res_info['lost_nodes']) if res_info['lost_nodes'] else 'None')}`.")
        else:
            st.info('The network has no bridges or articulation points; it is fully resilient against single link or router failures.')
    resilience_payload = {'online_routers': [r for r, obj in graph.routers.items() if obj.is_online], 'active_edges': [e for e in graph.get_edges() if graph.is_edge_active(e[0], e[1])], 'component_count': summary['component_count'], 'bridges': bridges, 'articulation_points': aps}
    res_csv = export_resilience_csv(resilience_payload)
    dl_rc1, dl_rc2 = st.columns([1, 3])
    with dl_rc1:
        st.download_button(label='Download Resilience CSV', data=res_csv, file_name=f"netroute_resilience_{graph.name.lower().replace(' ', '_')}.csv", mime='text/csv', width='stretch', key='na_dl_resilience_csv')
    st.write('')
    st.markdown('### Router Degree Distribution')
    router_degrees = []
    for rid in sorted(graph.routers.keys()):
        nbrs = graph.adjacency.get(rid, [])
        router_degrees.append({'Router ID': rid, 'Name': graph.routers[rid].name, 'Degree (Connections)': len(nbrs), 'Status': 'ONLINE' if graph.routers[rid].is_online else 'OFFLINE', 'Neighbors': ', '.join(sorted(nbrs))})
    st.dataframe(pd.DataFrame(router_degrees), width='stretch', hide_index=True)
    st.markdown('### Connected Subnets (Components)')
    comps = summary['components']
    for idx, comp in enumerate(comps):
        st.markdown(f"• **Component {idx + 1} ({len(comp)} routers):** `{', '.join(comp)}`")
    st.write('')
    st.markdown('### Reachability Matrix from Source')
    router_keys = sorted(list(graph.routers.keys()))
    if router_keys:
        reach_src = st.selectbox('Evaluate Reachability From', options=router_keys, key='na_reach_src')
        reach_rows = []
        for target in router_keys:
            is_reach = graph.is_reachable(reach_src, target)
            reach_rows.append({'Target Router': target, 'Name': graph.routers[target].name, 'Reachable from ' + reach_src: 'YES' if is_reach else 'NO', 'Target Status': 'ONLINE' if graph.routers[target].is_online else 'OFFLINE'})
        st.dataframe(pd.DataFrame(reach_rows), width='stretch', hide_index=True)

def render_benchmark_lab(graph: Graph):
    st.markdown('## Algorithm Benchmark Lab')
    st.markdown('*Empirical evaluation of BFS, DFS, and Dijkstra on synthetic graphs of varying scale and density with high-resolution execution timing.*')
    st.caption('Benchmark execution uses monotonic high-resolution timing (`time.perf_counter()`) to measure pure algorithmic execution time, strictly excluding Streamlit UI rendering, Plotly layout generation, and network serialization.')
    bc1, bc2, bc3 = st.columns([2, 1.5, 1.5])
    with bc1:
        router_options = [5, 10, 15, 20, 30, 40, 50, 75, 100]
        sel_counts = st.multiselect('Router Counts (V) to Evaluate', options=router_options, default=[5, 10, 20, 30, 50], key='bm_router_counts')
    with bc2:
        sel_density = st.slider('Network Edge Density', min_value=0.1, max_value=0.8, value=0.25, step=0.05, key='bm_density')
    with bc3:
        sel_algos = st.multiselect('Algorithms to Benchmark', options=['BFS', 'DFS', 'Dijkstra'], default=['BFS', 'DFS', 'Dijkstra'], key='bm_algos')
    bc4, bc5, bc6 = st.columns([1.5, 1.5, 2])
    with bc4:
        sel_reps = st.number_input('Repetitions per Test Point', min_value=1, max_value=20, value=5, step=1, key='bm_repetitions')
    with bc5:
        sel_seed = st.number_input('Random Seed (Reproducibility)', min_value=1, max_value=999999, value=42, step=1, key='bm_seed')
    with bc6:
        st.write('')
        st.write('')
        run_bm_btn = st.button('Execute Benchmark Suite', type='primary', width='stretch', key='bm_btn_run')
    if run_bm_btn:
        if not sel_counts:
            st.warning('Please select at least one router count to benchmark.')
        elif not sel_algos:
            st.warning('Please select at least one algorithm to benchmark.')
        else:
            with st.spinner('Generating reproducible synthetic topologies and measuring algorithm runtimes...'):
                suite = run_benchmark_suite(router_counts=sel_counts, density=sel_density, algos=sel_algos, repetitions=sel_reps, seed=sel_seed)
                st.session_state['benchmark_suite'] = suite
            st.success(f"Benchmark completed successfully! Evaluated {len(suite.get('records', []))} test points across {len(sel_counts)} network scales.")
    suite = st.session_state.get('benchmark_suite')
    if suite and suite.get('records'):
        records = suite['records']
        st.write('')
        st.markdown('### Measured Algorithm Scaling')
        fig_bm = go.Figure()
        algo_colors = {'BFS': '#2563EB', 'DFS': '#7C3AED', 'Dijkstra': '#D97706'}
        algo_symbols = {'BFS': 'circle', 'DFS': 'square', 'Dijkstra': 'diamond'}
        for algo in sel_algos:
            algo_recs = [r for r in records if r['algorithm'] == algo]
            algo_recs.sort(key=lambda x: x['routers'])
            if algo_recs:
                x_vals = [r['routers'] for r in algo_recs]
                y_vals = [r['mean_time_ms'] for r in algo_recs]
                fig_bm.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name=f'{algo} (Mean ms)', line=dict(color=algo_colors.get(algo, '#0F172A'), width=2.5), marker=dict(symbol=algo_symbols.get(algo, 'circle'), size=8)))
        fig_bm.update_layout(title='Algorithm Execution Time vs. Network Size (Routers V)', xaxis_title='Number of Routers (V)', yaxis_title='Mean Execution Time (milliseconds)', paper_bgcolor='#FFFFFF', plot_bgcolor='#F8FAFC', height=400, margin=dict(l=50, r=30, t=50, b=50), hovermode='x unified', xaxis=dict(gridcolor='#E2E8F0'), yaxis=dict(gridcolor='#E2E8F0'))
        render_plotly(fig_bm, key='bm_chart')
        st.write('')
        st.markdown('### Benchmark Experimental Data')
        table_rows = []
        for r in records:
            table_rows.append({'Routers (V)': str(r.get('routers')), 'Edges (E)': str(r.get('edges')), 'Algorithm': r.get('algorithm'), 'Mean Time (ms)': f"{r.get('mean_time_ms', 0.0):.4f}", 'Min Time (ms)': f"{r.get('min_time_ms', 0.0):.4f}", 'Max Time (ms)': f"{r.get('max_time_ms', 0.0):.4f}", 'Hops': str(r.get('hops', 0)), 'Path Cost': f"{r.get('path_cost', 0.0):.1f}", 'Visited': str(r.get('visited_count', 0)), 'Explored Edges': str(r.get('explored_edges', 0)), 'Theoretical Time': r.get('theoretical_time', ''), 'Theoretical Space': r.get('theoretical_space', '')})
        st.dataframe(pd.DataFrame(table_rows), width='stretch', hide_index=True)
        st.write('')
        bm_csv = export_benchmark_csv(records)
        bm_json = json.dumps(suite, indent=2)
        bm_dl1, bm_dl2, bm_dl3 = st.columns(3)
        with bm_dl1:
            st.download_button(label='Download Benchmark CSV', data=bm_csv, file_name=f'netroute_benchmark_suite_density_{int(sel_density * 100)}.csv', mime='text/csv', width='stretch', key='bm_dl_csv')
        with bm_dl2:
            st.download_button(label='Download Benchmark JSON', data=bm_json, file_name=f'netroute_benchmark_suite_density_{int(sel_density * 100)}.json', mime='application/json', width='stretch', key='bm_dl_json')
        with bm_dl3:
            bm_png = export_figure_png(fig_bm)
            if bm_png:
                st.download_button(label='Benchmark Chart PNG', data=bm_png, file_name=f'netroute_benchmark_chart.png', mime='image/png', width='stretch', key='bm_dl_png')
            else:
                st.caption('PNG export requires Kaleido.')

def render_import_simulation(graph: Graph):
    st.markdown('## Import & Simulation')
    st.markdown('*Manage topology data exchange, import network configurations, and inspect simulation history.*')
    tab_hist, tab_imp, tab_exp = st.tabs(['Simulation History & Reports', 'Import Topology', 'Export Topology'])
    with tab_hist:
        history = st.session_state.get('simulation_history', [])
        h_col1, h_col2 = st.columns([3, 1])
        with h_col2:
            if st.button('Clear History', width='stretch', icon=':material/delete_sweep:', key='hist_clear_btn'):
                sim.clear_history()
                st.rerun()
        if not history:
            st.info('No completed simulations recorded in this session yet.')
        else:
            table_rows = [{'ID': r.get('id'), 'Timestamp': r.get('timestamp'), 'Type': r.get('type'), 'Algorithm': r.get('algorithm'), 'Route': f"{r.get('source')} -> {r.get('destination')}", 'Status': 'SUCCESS' if r.get('success') else 'FAILED', 'Hops': r.get('hops', 0), 'Steps': r.get('steps_count', 0), 'Time (ms)': r.get('execution_time_ms', 0.0)} for r in history]
            st.dataframe(pd.DataFrame(table_rows), width='stretch', hide_index=True)
            sel_run_id = st.selectbox('Select Run ID to Inspect', options=[r['id'] for r in history], key='hist_run_select')
            rec = next((r for r in history if r['id'] == sel_run_id), None)
            if rec:
                st.json(rec)
                if rec.get('report'):
                    st.download_button(label=f'Download JSON Report for {sel_run_id}', data=json.dumps(rec['report'], indent=2), file_name=f'netroute_report_{sel_run_id}.json', mime='application/json', width='stretch', key=f'hist_dl_{sel_run_id}')
        st.write('')
        st.markdown('##### Latest Session Reports')
        sim_res = st.session_state.get('sim_res')
        cmp_res = st.session_state.get('cmp_res')
        src_id, dst_id = st.session_state.get('source_id', 'N1'), st.session_state.get('dest_id', 'N7')
        rc1, rc2 = st.columns(2)
        with rc1:
            if sim_res:
                st.download_button('Download Single Traversal JSON Report', data=json.dumps(generate_simulation_report(graph, sim_res, src_id, dst_id), indent=2), file_name=f'netroute_traversal_report_{src_id}_{dst_id}.json', mime='application/json', width='stretch', key='ie_dl_single_rep')
            else:
                st.caption('No single traversal run yet.')
        with rc2:
            if cmp_res:
                st.download_button('Download Comparison JSON Report', data=json.dumps(generate_comparison_report(graph, cmp_res, src_id, dst_id), indent=2), file_name=f'netroute_comparison_report_{src_id}_{dst_id}.json', mime='application/json', width='stretch', key='ie_dl_cmp_rep')
            else:
                st.caption('No dual comparison run yet.')
    with tab_imp:
        st.markdown('### Import Topology JSON')
        uploaded_file = st.file_uploader('Choose a JSON topology file', type=['json'], key='ie_file_uploader')
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                if st.button('Validate and Load Topology', type='primary', width='stretch', key='ie_btn_load_file'):
                    ok, msg = graph.load_from_dict(data)
                    if ok:
                        st.success(f'Topology imported successfully! {msg}')
                        st.session_state['selected_preset'] = 'custom'
                        g_nodes = sorted(list(graph.routers.keys()))
                        if g_nodes:
                            st.session_state['source_id'] = g_nodes[0]
                            st.session_state['dest_id'] = g_nodes[-1]
                        sim.invalidate_simulation()
                        st.rerun()
                    else:
                        st.error(f'Import Failed: {msg}')
            except Exception as e:
                st.error(f'Failed to parse JSON file: {str(e)}')
    with tab_exp:
        st.markdown('### Export Active Topology')
        topo_json = json.dumps(graph.to_dict(), indent=2)
        preset_name = st.session_state.get('selected_preset', 'custom')
        st.download_button('Download Topology JSON File', data=topo_json, file_name=f'netroute_topology_{preset_name}.json', mime='application/json', type='primary', width='stretch', key='ie_btn_download_topo')
        st.code(topo_json, language='json')

render_simulation_history = render_import_simulation
render_import_export = render_import_simulation
