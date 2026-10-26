import json
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import CSS, PRIMARY, CYAN, PURPLE, SUCCESS, WARNING, TEXT_MUTED, BORDER
from network import Graph
import simulation as sim

st.set_page_config(page_title="NetRoute — Packet Routing Simulator", page_icon="🌐", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

sim.init()
graph: Graph = st.session_state.graph


# --- PLOTLY GRAPH BUILDER ---
def draw_graph(graph: Graph, active: dict, src: str, dst: str):
    fig = go.Figure()
    if not graph.nodes:
        fig.add_annotation(text="Graph is empty.", showarrow=False)
        return fig

    # 1. Links
    edges = graph.get_edges()
    route_edges = []
    res = active.get("res")
    if res and res.get("path"):
        p = res["path"]
        route_edges = [tuple(sorted((p[i], p[i+1]))) for i in range(len(p)-1)]

    for u, v in edges:
        e = tuple(sorted((u, v)))
        is_route = e in route_edges
        is_active = active.get("active_edge") and e == tuple(sorted(active["active_edge"]))
        color = SUCCESS if is_route else (CYAN if is_active else BORDER)
        width = 4 if is_route else (3.5 if is_active else 2)

        fig.add_trace(go.Scatter(
            x=[graph.nodes[u]["x"], graph.nodes[v]["x"]],
            y=[graph.nodes[u]["y"], graph.nodes[v]["y"]],
            mode="lines",
            line=dict(color=color, width=width),
            hoverinfo="none",
            showlegend=False
        ))

    # 2. Routers (Nodes)
    nodes = sorted(graph.nodes.keys())
    x_vals, y_vals, colors, labels = [], [], [], []
    for nid in nodes:
        node = graph.nodes[nid]
        x_vals.append(node["x"])
        y_vals.append(node["y"])
        labels.append(nid)

        if not node["online"]:
            c = "#94A3B8"
        elif nid == active.get("active_node"):
            c = WARNING
        elif nid == src:
            c = PRIMARY
        elif nid == dst:
            c = PURPLE
        elif nid in active.get("route", set()):
            c = SUCCESS
        elif nid in active.get("visited", set()):
            c = "#93C5FD"
        else:
            c = "#FFFFFF"
        colors.append(c)

    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode="markers+text",
        marker=dict(size=32, color=colors, line=dict(color="#1E3A8A", width=2)),
        text=labels,
        textposition="middle center",
        textfont=dict(size=12, color=["white" if c not in ("#FFFFFF", "#93C5FD") else "#172033" for c in colors]),
        hoverinfo="text",
        hovertext=[f"Router {n} ({graph.nodes[n]['name']})<br>Online: {graph.nodes[n]['online']}" for n in nodes],
        showlegend=False
    ))

    # 3. Packet Position
    p_node = active.get("packet_node")
    if p_node and p_node in graph.nodes:
        fig.add_trace(go.Scatter(
            x=[graph.nodes[p_node]["x"]], y=[graph.nodes[p_node]["y"]],
            mode="markers+text",
            marker=dict(size=44, symbol="circle-open", color="#E11D48", line=dict(width=3)),
            text=["📦"], textposition="top center", textfont=dict(size=18),
            hoverinfo="none", showlegend=False
        ))

    fig.update_layout(
        height=420, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, autorange="reversed")
    )
    return fig


# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### ⚙️ NetRoute Controls")
    router_ids = sorted(graph.nodes.keys())

    algo = st.radio("Algorithm", ["BFS (Shortest-Hop)", "DFS (Path Discovery)"])
    c1, c2 = st.columns(2)
    with c1:
        src = st.selectbox("Source", router_ids, index=0 if router_ids else 0)
    with c2:
        dst = st.selectbox("Destination", router_ids, index=len(router_ids)-1 if router_ids else 0)

    if st.button("🚀 Run Algorithm", type="primary", use_container_width=True):
        sim.run(graph, algo, src, dst)

    res = st.session_state.get("res")
    if res and res.get("steps"):
        st.markdown("---")
        st.markdown(f"**Step Navigation ({st.session_state.step_idx + 1} / {len(res['steps'])})**")
        sc1, sc2, sc3, sc4 = st.columns(4)
        if sc1.button("⏮ First"):
            sim.reset_steps()
        if sc2.button("◀ Back"):
            sim.step_backward()
        if sc3.button("Next ▶"):
            sim.step_forward()
        if sc4.button("End ⏭"):
            st.session_state.step_idx = len(res["steps"]) - 1

        new_idx = st.slider("Step", 0, len(res["steps"]) - 1, st.session_state.step_idx, label_visibility="collapsed")
        if new_idx != st.session_state.step_idx:
            st.session_state.step_idx = new_idx

        if res.get("success") and res.get("path"):
            st.markdown("---")
            st.markdown(f"**📦 Packet Hop: {st.session_state.packet_hop} / {len(res['path']) - 1}**")
            pc1, pc2 = st.columns(2)
            if pc1.button("Step Packet ➡️", use_container_width=True):
                sim.packet_step()
            if pc2.button("Reset Packet ↺", use_container_width=True):
                sim.packet_reset()

    # Presets
    st.markdown("---")
    with st.expander("🌐 Presets & Layout", expanded=False):
        preset = st.selectbox("Built-in Topologies", ["Sample (Default)", "Direct Route", "Multiple Routes", "Cyclic Network", "Disconnected Subnets", "Offline Router Barrier"])
        if st.button("Load Preset", use_container_width=True):
            p_map = {"Sample (Default)": "sample", "Direct Route": "direct", "Multiple Routes": "multi_route", "Cyclic Network": "cyclic", "Disconnected Subnets": "disconnected", "Offline Router Barrier": "offline_router"}
            graph.load_preset(p_map[preset])
            sim.invalidate()
            st.rerun()
        if st.button("Fit & Circle Layout", use_container_width=True):
            graph.auto_layout()
            st.rerun()

    # Dynamic Editing
    with st.expander("🛠️ Edit Graph (CO2)", expanded=False):
        st.caption("Add Router")
        an1, an2 = st.columns([1, 2])
        new_id = an1.text_input("ID", placeholder="R7", max_chars=6).upper()
        new_name = an2.text_input("Name", placeholder="Switch")
        if st.button("Add Router", use_container_width=True):
            if new_id and graph.add_node(new_id, new_name):
                graph.auto_layout()
                sim.invalidate()
                st.rerun()

        st.caption("Delete Router")
        del_r = st.selectbox("Delete", ["--"] + router_ids, key="del_r")
        if st.button("Delete Router", use_container_width=True) and del_r != "--":
            graph.remove_node(del_r)
            sim.invalidate()
            st.rerun()

        st.caption("Connect Routers")
        if len(router_ids) >= 2:
            cu1, cu2 = st.columns(2)
            u_add = cu1.selectbox("From", router_ids, key="u_add")
            v_add = cu2.selectbox("To", [x for x in router_ids if x != u_add], key="v_add")
            if st.button("Connect", use_container_width=True):
                graph.add_edge(u_add, v_add)
                sim.invalidate()
                st.rerun()

        st.caption("Toggle Online / Offline")
        tog_r = st.selectbox("Toggle", router_ids, key="tog_r")
        if st.button("Toggle Status", use_container_width=True):
            graph.toggle_node(tog_r)
            sim.invalidate()
            st.rerun()

    # JSON File
    with st.expander("💾 Save / Load JSON", expanded=False):
        st.download_button("Download JSON", json.dumps(graph.to_dict(), indent=2), "network.json", "application/json", use_container_width=True)
        up_file = st.file_uploader("Upload JSON", type=["json"])
        if up_file:
            graph.load_from_dict(json.load(up_file))
            sim.invalidate()
            st.rerun()


# --- MAIN WORKSPACE ---
active = sim.get_active(graph)
curr_step = active.get("step")
sim_res = active.get("res")

# Header
h1, h2 = st.columns([7, 3])
with h1:
    st.markdown(f"## 🌐 NetRoute: Interactive Network Routing Simulator")
with h2:
    st.markdown('<span class="badge">CO1: STACK / QUEUE</span><span class="badge">CO2: DYNAMIC GRAPH</span><span class="badge">CO5: ROUTING</span>', unsafe_allow_html=True)

# Metrics
online = sum(1 for r in graph.nodes.values() if r["online"])
comps = len(graph.get_components())
hops = f"{sim_res['hops']} hops" if (sim_res and sim_res.get("success")) else "—"

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Routers", len(graph.nodes), f"{online} online")
m2.metric("Links", len(graph.get_edges()), "Undirected")
m3.metric("Components", comps, "Connected" if comps == 1 else "Split")
m4.metric("Visited", len(active.get("visited", [])))
m5.metric("Route", hops)
m6.metric("Steps", f"{st.session_state.step_idx + 1} / {len(sim_res['steps'])}" if sim_res else "Ready")

# Graph Visualization
st.plotly_chart(draw_graph(graph, active, src, dst), use_container_width=True)

# Step Message
if curr_step:
    st.info(f"**Step {curr_step['step']} [{curr_step['type']}]:** {curr_step['msg']}")


# --- TABS ---
tab_inspect, tab_repr, tab_route, tab_log, tab_co = st.tabs([
    "🔍 Queue / Stack Inspector (CO1)",
    "📊 Graph Representations (CO2 & CO5)",
    "🌲 Traversal Tree & Route (CO5)",
    "📜 Step Execution Log",
    "🎓 Course Outcome Mapping"
])

with tab_inspect:
    is_bfs = "BFS" in algo
    name = "FIFO Queue" if is_bfs else "LIFO Stack"
    st.markdown(f"#### Live {name} State")
    if curr_step:
        items = curr_step["structure"]
        st.write(f"**Current Size:** {len(items)}")
        if not items:
            st.caption(f"The {name} is empty.")
        else:
            chips = []
            if is_bfs:
                for i, it in enumerate(items):
                    tag = "chip-front" if i == 0 else ("chip-rear" if i == len(items)-1 else "chip-item")
                    lbl = f"FRONT: {it}" if i == 0 else (f"REAR: {it}" if i == len(items)-1 else it)
                    chips.append(f'<span class="chip {tag}">{lbl}</span>')
                st.markdown(" ➔ ".join(chips), unsafe_allow_html=True)
                st.caption("FIFO: Enqueued at REAR, dequeued from FRONT.")
            else:
                for i, it in enumerate(items):
                    tag = "chip-top" if i == len(items)-1 else ("chip-bot" if i == 0 else "chip-item")
                    lbl = f"TOP: {it}" if i == len(items)-1 else (f"BOT: {it}" if i == 0 else it)
                    chips.append(f'<span class="chip {tag}">{lbl}</span>')
                st.markdown(" ➔ ".join(chips), unsafe_allow_html=True)
                st.caption("LIFO: Pushed and popped at TOP.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Visited Sequence")
            st.write(" ➔ ".join(curr_step["visited"]) or "None yet.")
        with c2:
            st.markdown("##### Parent Pointer Map")
            st.dataframe(pd.DataFrame([{"Router": k, "Parent": v or "None"} for k, v in curr_step["parents"].items()]), use_container_width=True, height=140)
    else:
        st.info("Run an algorithm to inspect the live data structure.")

with tab_repr:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Adjacency List O(V + E)")
        for n, nbrs in graph.adj.items():
            status = "🟢" if graph.nodes[n]["online"] else "🔴"
            st.write(f"**{status} {n}** ➔ {', '.join(sorted(nbrs)) or 'None'}")
    with c2:
        st.markdown("#### Adjacency Matrix O(V²)")
        nodes, mat = graph.get_matrix()
        if nodes:
            st.dataframe(pd.DataFrame(mat, index=nodes, columns=nodes), use_container_width=True)

with tab_route:
    if sim_res:
        if sim_res.get("success"):
            st.success(f"**Discovered Route:** {' ➔ '.join(sim_res['path'])} ({sim_res['hops']} hops)")
        else:
            st.error(sim_res.get("msg"))
        if sim_res.get("tree_edges"):
            st.markdown("##### Traversal Tree Edges")
            st.dataframe(pd.DataFrame([{"Parent": u, "Discovered Child": v} for u, v in sim_res["tree_edges"]]), use_container_width=True, height=180)
    else:
        st.info("Run an algorithm to see route and tree edges.")

with tab_log:
    if sim_res and sim_res.get("steps"):
        log_text = "\n".join([f"Step {s['step']:02d} [{s['type']}]: {s['msg']}" for s in sim_res["steps"]])
        st.text_area("Execution Log", log_text, height=220)
    else:
        st.info("Log will appear after running BFS or DFS.")

with tab_co:
    st.markdown("""
    ### Course Outcome (CO) Mapping:
    - **CO1 (Stack & Queue):** Queue-based BFS (`collections.deque`) guarantees shortest hops. Stack-based DFS (`list`) discovers deep routes with backtracking. Live inspection of front/rear and top/bottom pointers.
    - **CO2 (Dynamic Data Structures):** Dynamic router and link insertion/deletion. Automatic adjacency list updates. Cascading deletion of links.
    - **CO5 (Graph Structures & Routing):** Dual representation with Adjacency List $O(V+E)$ and Matrix $O(V^2)$. Network reachability, offline router detour, and packet transmission animation.
    """)
