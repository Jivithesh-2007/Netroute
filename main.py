"""
main.py — NetRoute: Network Packet Routing Simulator.

Simulation-first educational application demonstrating:
- Dynamic Graph Topology Operations & Representations
- Step-by-Step BFS & DFS Traversal Simulations with Live Queue/Stack States
- Synchronized Side-by-Side BFS vs. DFS Algorithm Comparisons
- Traversal Spanning Tree Generation & Invariant Verification
- Traditional Routing Table Generation & Hop-by-Hop Packet Forwarding
- JSON Import/Export & Comprehensive Engineering Reports
"""

import streamlit as st
from network import Graph
import simulation as sim
from theme import CUSTOM_CSS, PRIMARY, TEXT_MAIN, TEXT_MUTED

from views import (
    render_dashboard,
    render_topology_studio,
    render_traversal_simulator,
    render_bfs_dfs_comparison,
    render_data_structures_inspector,
    render_traversal_tree,
    render_routing_table_simulator,
    render_network_analysis,
    render_simulation_history,
    render_import_export,
    render_settings_help
)


# -----------------------------------------------------------------------------
# 1. PAGE SETUP & CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NetRoute — Network Packet Routing",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Clean Light-Theme Styles
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
sim.init_session()
graph: Graph = st.session_state["graph"]


# -----------------------------------------------------------------------------
# 2. SIDEBAR NAVIGATION & GLOBAL CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="padding-bottom: 6px;">
        <span style="font-size: 1.45rem; font-weight: 800; color: #0F172A; letter-spacing: -0.5px;">NetRoute</span><br>
        <span style="font-size: 0.82rem; color: #475569; font-weight: 500;">Network Packet Routing Simulator</span>
    </div>
    """,
    unsafe_allow_html=True
)

NAV_PAGES = [
    "Dashboard",
    "Topology Studio",
    "Traversal Simulator",
    "BFS vs DFS Comparison",
    "Data Structures Inspector",
    "Traversal Tree",
    "Routing Table Simulator",
    "Network Analysis",
    "Simulation History",
    "Import / Export",
    "Settings / Help"
]

current_page = st.session_state.get("nav_page", "Dashboard")
if current_page not in NAV_PAGES:
    current_page = "Dashboard"

selected_page = st.sidebar.radio(
    "Navigation",
    options=NAV_PAGES,
    index=NAV_PAGES.index(current_page),
    key="nav_radio"
)

if selected_page != st.session_state.get("nav_page"):
    st.session_state["nav_page"] = selected_page
    st.rerun()

st.sidebar.markdown("---")

# Compact Network Overview in Sidebar
st.sidebar.markdown("##### Network State")
router_keys = sorted(list(graph.routers.keys()))
summary = graph.get_summary()

sb_c1, sb_c2 = st.sidebar.columns(2)
sb_c1.metric("Routers", summary["total_routers"])
sb_c2.metric("Links", summary["total_edges"])

active_preset = st.session_state.get("selected_preset", "custom")
conn_status = "Connected" if summary["is_connected"] else f"{summary['component_count']} Subnets"
st.sidebar.caption(f"**Preset:** {active_preset.title()} | **State:** {conn_status}")

# Global Quick Endpoint Selectors
if router_keys:
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### Global Endpoints")
    cur_src = st.session_state.get("source_id", router_keys[0])
    cur_dst = st.session_state.get("dest_id", router_keys[-1] if len(router_keys) > 1 else router_keys[0])
    if cur_src not in router_keys:
        cur_src = router_keys[0]
    if cur_dst not in router_keys:
        cur_dst = router_keys[-1]

    s_idx = router_keys.index(cur_src)
    d_idx = router_keys.index(cur_dst)

    sb_src = st.sidebar.selectbox("Source (Origin)", options=router_keys, index=s_idx, key="sb_src_selector")
    sb_dst = st.sidebar.selectbox("Destination (Target)", options=router_keys, index=d_idx, key="sb_dst_selector")

    if sb_src != cur_src or sb_dst != cur_dst:
        st.session_state["source_id"] = sb_src
        st.session_state["dest_id"] = sb_dst
        sim.invalidate_simulation()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("NetRoute v2.0 • Simulation-First Engine")


# -----------------------------------------------------------------------------
# 3. ROUTE TO SELECTED PAGE VIEW
# -----------------------------------------------------------------------------
page = st.session_state.get("nav_page", "Dashboard")

if page == "Dashboard":
    render_dashboard(graph)
elif page == "Topology Studio":
    render_topology_studio(graph)
elif page == "Traversal Simulator":
    render_traversal_simulator(graph)
elif page == "BFS vs DFS Comparison":
    render_bfs_dfs_comparison(graph)
elif page == "Data Structures Inspector":
    render_data_structures_inspector(graph)
elif page == "Traversal Tree":
    render_traversal_tree(graph)
elif page == "Routing Table Simulator":
    render_routing_table_simulator(graph)
elif page == "Network Analysis":
    render_network_analysis(graph)
elif page == "Simulation History":
    render_simulation_history(graph)
elif page == "Import / Export":
    render_import_export(graph)
elif page == "Settings / Help":
    render_settings_help(graph)
