# NetRoute — Interactive Network Packet-Routing Simulator (BFS & DFS)

An interactive, educational network packet-routing web application developed using **Python**, **Streamlit**, and **Plotly**. NetRoute visualizes graph-based routing algorithms, genuine step-by-step queue and stack execution, dynamic network topology editing, and hop-by-hop packet transmission.

NetRoute aligns directly with **CO1**, **CO2**, and **CO5** of the Data Structures and Algorithms (DSA) engineering curriculum.

---

## 1. Academic Course Outcome Mapping

### CO1 — Stack and Queue Data Structures
- **Queue-Based BFS:** Implements genuine Breadth-First Search using a First-In-First-Out (FIFO) queue (`collections.deque`). Demonstrates level-by-level exploration to discover the unweighted shortest-hop path between source and destination routers.
- **Stack-Based DFS:** Implements genuine Depth-First Search using an explicit Last-In-First-Out (LIFO) stack (`list`). Demonstrates deep branch exploration and explicit backtracking, showing that DFS discovers valid reachable paths without guaranteeing minimum hops.
- **Live Queue/Stack Inspector:** Displays live internal data structure states at each execution step, including FIFO Front/Rear indicators, LIFO Top/Bottom markers, push/pop/enqueue/dequeue counts, and maximum structure size.

### CO2 — Dynamic Data Structures
- **Dynamic Adjacency List $O(V + E)$:** Serves as the primary dynamic graph representation. Routers (vertices) and connections (edges) are inserted, renamed, toggled, and deleted dynamically.
- **Dynamic Topology Editing:** Real-time adding/removing of routers and links with instant synchronization to the visual graph and data structures. Automatic cascading deletion of links upon router removal.
- **Validation:** Input sanitation, duplicate router ID prevention, duplicate link prevention, and self-loop rejection.

### CO5 — Graph Structures, Traversal & Routing
- **Dual Synchronized Representations:** Maintains real-time synchronization between the Adjacency List $O(V + E)$ and the Adjacency Matrix $O(V^2)$.
- **Traversal Trees & Routes:** Reconstructs the shortest-hop or discovered path using parent pointers; renders traversal tree edges recorded during discovery.
- **Network Reachability & Diagnostics:** Analyzes connected components, destination reachability from the active source, and simulated hardware failures (online/offline toggle).
- **Packet Transmission:** Animates packet delivery hop-by-hop along the discovered route with interactive playback (Step Forward, Auto-Stream, Reset).

---

## 2. Project Structure

```
NetRoute/
├── main.py              # Streamlit page layout, Plotly graph visualizer, metrics, and inspector tabs
├── network.py           # Router and Graph models, dynamic editing, presets, and validation
├── algorithms.py        # Genuine BFS and DFS engines with granular step-by-step state recording
├── simulation.py        # Session state management, playback progression, and packet animation
├── theme.py             # Curated light palette, CSS styling, and badge/metric renderers
├── requirements.txt     # Minimal dependencies (streamlit, plotly, pandas)
├── .gitignore           # Git ignore patterns
├── README.md            # Comprehensive project documentation
├── data/
│   └── sample_network.json  # Sample 6-router topology JSON
└── tests/
    ├── test_network.py  # Graph operations, validation, matrix/list sync tests
    ├── test_bfs.py      # BFS shortest path, queue mechanics, edge cases
    ├── test_dfs.py      # DFS path discovery, stack mechanics, backtracking
    └── test_simulation.py # Step navigation, packet hop progression, state reset
```

---

## 3. Computational Complexity

| Algorithm / Representation | Time Complexity | Auxiliary Space Complexity | Key Invariant |
| :--- | :--- | :--- | :--- |
| **BFS Routing** | $O(V + E)$ | $O(V)$ | Guaranteed shortest-hop route in unweighted graphs |
| **DFS Routing** | $O(V + E)$ | $O(V)$ | Deepest unvisited branch prioritized; explicit backtracking |
| **Adjacency List** | $O(V + E)$ build | $O(V + E)$ | Memory-efficient for sparse dynamic networks |
| **Adjacency Matrix** | $O(V^2)$ build | $O(V^2)$ | Constant-time $O(1)$ edge-lookup matrix |

*Note: $V$ is the number of vertices (routers) and $E$ is the number of edges (transmission links).*

---

## 4. Built-in Topologies & Presets

1. **Sample (Default):** Balanced 6-router interconnected mesh.
2. **Direct Route:** Linear 4-node chain demonstrating sequential forwarding.
3. **Multiple Routes (Spine/Leaf):** Dual-path topology demonstrating why BFS chooses the 3-hop path while DFS may traverse the 4-hop branch.
4. **Cyclic Network:** Multi-loop mesh demonstrating visited-set loop avoidance.
5. **Disconnected Subnets:** Segmented network demonstrating partition detection and reachability failure.
6. **Offline Router Barrier:** Network with a disabled bridge router demonstrating dynamic detour routing.
7. **Random Generators:** Generates connected or disconnected random networks ($3 \le V \le 10$).

---

## 5. Installation & Execution

### Prerequisites
- Python 3.9+ installed.

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Launch the Application
```bash
streamlit run main.py
```
Open your browser at `http://localhost:8501`.

### Run Automated Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
All 21 unit tests verify graph operations, BFS, DFS, and simulation state.
