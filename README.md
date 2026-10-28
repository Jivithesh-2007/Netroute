# NetRoute v3 — Network Packet Routing Simulator

**Industry Focus:** Networking, Telecommunications, and Distributed Systems  
**Architecture:** Simulation-First Python / Streamlit Application  
**Visualization:** Interactive Plotly Network Diagrams & Spanning Trees  

NetRoute v3 is a professional, interactive, simulation-first network routing and resilience analysis application. Designed for network engineers, telecommunications specialists, researchers, and students, NetRoute demonstrates unweighted hop-based routing (BFS), deep branch path discovery (DFS), and weighted least-cost routing (Dijkstra) alongside graph resilience diagnostics (Tarjan's Bridges & Articulation Points), an interactive Failure Lab sandbox, and an empirical high-resolution Benchmark Lab.

---

## 1. Application Navigation & Core Features

NetRoute v3 features a clean sidebar navigation system with 13 specialized sections:

1. **Dashboard:** High-level network status, KPI metric cards (Active Routers, Transmission Links, Connectivity State, Simulation Engine Status), interactive topology preview, and quick-action launchers.
2. **Topology Studio:** Full visual graph editor supporting:
   - Adding, deleting, renaming, and repositioning routers ($X, Y$ coordinates).
   - Toggling router availability (Online / Offline).
   - Adding and removing transmission links with custom weights / costs.
   - Simulating physical link failures (Sever Link / Restore Link).
   - Balanced circular auto-layout and topology presets (Reference WAN, Ring, Mesh, Disconnected, Linear Chain, Multi-Route, Offline Router).
   - Clear network operation with explicit confirmation safety.
3. **Traversal Simulator (Explainable Engine):** Interactive simulation engine for BFS, DFS, and Dijkstra:
   - Source and destination endpoint selection.
   - Algorithm selection: Breadth-First Search (BFS), Depth-First Search (DFS), or Dijkstra (Weighted Shortest Path).
   - Step-by-step playback controls: First Step (`|<<`), Previous (`<`), Next (`>`), Last (`>>|`), and interactive step scrubber slider.
   - Explainable reasoning card for every event: router action, why the action occurred, neighbor examined, neighbor visited status, parent pointer assignment, and current route reconstruction state.
   - Dedicated live Queue (BFS), Stack (DFS), and Priority Queue (Dijkstra) inspectors displaying current contents, front/rear/top pointers, operation counters, and peak frontier depths.
   - Downloadable JSON report, CSV metrics, and high-resolution PNG graph diagrams.
4. **BFS vs. DFS Comparison:** Dual-simulation comparative analysis page:
   - Synchronized side-by-side visual graphs running on identical graph snapshots and endpoints.
   - Synchronized playback controls advancing both algorithms in lockstep.
   - Simultaneous live BFS Queue and DFS Stack inspectors.
   - 3-Way Route Strategy Comparison expander comparing BFS (min hops), DFS (branching), and Dijkstra (least cost).
   - Authoritative engineering verdict explaining why BFS minimizes hop count in unweighted topologies while Dijkstra minimizes accumulated link costs.
   - Multi-format exports: Comparison JSON report, CSV metrics table, and PNG graphs.
5. **Network Failure Lab:** Sandbox for multi-failure network experimentations:
   - Evaluates router outages and link severances on an isolated scenario clone without modifying the baseline graph.
   - Multi-select routers to take offline and links to sever.
   - Side-by-side before-and-after topology visualization with offline nodes and severed links clearly highlighted.
   - Comparative metrics: Component count, route survival status, hop delta, least-cost delta, disconnected router lists.
   - Controls: Apply Failure Scenario, Reset Scenario, Restore Baseline, and Commit Scenario to Active Topology.
   - Multi-format export: Download scenario JSON report, scenario CSV, and scenario PNG graph.
6. **Data Structures Inspector:** Live inspection of internal data structures:
   - Graph representations: Adjacency List $O(V + E)$ and Adjacency Matrix $O(V^2)$.
   - Queue, Stack, and Priority Queue progression traces.
   - Searching evaluation (Linear Search $O(n)$ vs. Binary Search $O(\log n)$) on adaptive network datasets.
   - Sorting evaluation (Bubble Sort $O(n^2)$ vs. Insertion Sort $O(n^2)$) with operation counts and correctness verification.
7. **Traversal Tree:** Spanning tree analysis:
   - Hierarchical Plotly tree visualizer derived directly from algorithm predecessor / parent pointers.
   - Tree root at source router with children descending by distance levels.
   - Root-to-destination path highlighted within the tree.
   - Mathematical invariant verification: $E_{tree} = V_{tree} - 1$, acyclic check, connected component check, and exclusion of unreachable nodes.
8. **Routing Table Simulator:** Traditional distributed hop-by-hop packet forwarding:
   - Generates local forwarding tables for every router displaying Destination, Next Hop, Metric Hops, and Reachability.
   - Simulates hop-by-hop forwarding where each router independently consults its own local routing table.
   - Failure detection: missing destination entries, offline intermediate routers, severed links, routing loops, and TTL expiration.
9. **Network Analysis & Resilience:** Graph topology diagnostics and single-point-of-failure analysis:
   - Tarjan's Bridge detection ($O(V + E)$) highlighting cut edges on the topology map.
   - Tarjan's Articulation Point detection ($O(V + E)$) highlighting cut vertices.
   - Interactive Resilience Removal Experiment: simulate taking down a bridge or articulation point to observe resulting subnets and lost reachability.
   - Router degree distribution and connected subnet partition analysis.
   - Download Resilience CSV summary.
10. **Algorithm Benchmark Lab:** High-resolution empirical performance testbed:
    - Generates synthetic, connected topologies across configurable router counts ($V \in [5, 100]$) and edge densities ($\rho \in [0.10, 0.80]$).
    - Reproducible graph generation via deterministic random seed.
    - Pure algorithmic execution runtime measurement using `time.perf_counter()` over configurable repetitions, strictly excluding UI and Plotly rendering overhead.
    - Plotly scaling chart comparing mean execution times across network scales.
    - Export benchmark dataset as CSV and JSON.
11. **Simulation History:** Session log of all executed single traversals and dual comparisons:
    - Summary table with timestamps, endpoints, algorithms, hop counts, and step counts.
    - Historical run inspector with full JSON preview and one-click report download.
12. **Import / Export:** Robust data interchange:
    - Export active topology as JSON preserving router coordinates, weights, and failure flags.
    - Import topology JSON with transactional schema validation (rejection of duplicate IDs, self-loops, negative weights, and missing endpoints without corrupting the active graph).
    - Download latest single simulation and dual comparison JSON reports.
13. **Settings / Help:** User guide, theoretical algorithm foundations, time and space complexity matrix, and application state factory reset.

---

## 2. Computational Complexity Matrix

| Algorithm / Operation | Data Structure | Time Complexity | Auxiliary Space | Optimality Property |
| :--- | :--- | :--- | :--- | :--- |
| **BFS Traversal** | FIFO Queue (`deque`) | $O(V + E)$ | $O(V)$ | **Guaranteed Minimum Hops** (Unweighted) |
| **DFS Traversal** | LIFO Stack (`list`) | $O(V + E)$ | $O(V)$ | **Deep Exploration** (No optimality guarantee) |
| **Dijkstra Routing** | Min-Priority Queue (`heapq`) | $O((V + E) \log V)$ | $O(V)$ | **Guaranteed Minimum Cost** (Non-negative weights) |
| **Tarjan's Bridges** | DFS Discovery/Low Values | $O(V + E)$ | $O(V)$ | Identifies all critical cut edges |
| **Tarjan's Articulation Points** | DFS Discovery/Low Values | $O(V + E)$ | $O(V)$ | Identifies all critical cut vertices |
| **Adjacency List** | Hash Map of Lists | $O(V + E)$ space | $O(V + E)$ | Optimal for sparse network graphs |
| **Adjacency Matrix** | 2D Array | $O(V^2)$ space | $O(V^2)$ | Optimal for dense edge query lookups |
| **Traversal Tree** | Rooted Spanning Tree | $O(V)$ | $O(V)$ | Verified ($E = V - 1$, Acyclic) |
| **Table Lookup** | Local Forwarding Table | $O(1)$ per hop | $O(V)$ per router | Dependent on routing table convergence |
| **Linear Search** | Sequential Array | $O(n)$ | $O(1)$ | No pre-sorting required |
| **Binary Search** | Sorted Array | $O(\log n)$ | $O(1)$ | Requires monotonically sorted keys |
| **Bubble Sort** | Array | $O(n^2)$ | $O(1)$ | Stable exchange sort |
| **Insertion Sort** | Array | $O(n^2)$ | $O(1)$ | Efficient for small or partially sorted lists |

---

## 3. Project Architecture

```
Netroute/
├── main.py                     # Streamlit entrypoint & sidebar navigation router (13 sections)
├── views.py                    # Modular view renderers (Failure Lab, Benchmark Lab, Resilience, etc.)
├── visualizer.py               # Plotly network graphs, spanning trees, bridge/AP badges, Kaleido PNG export
├── network.py                  # Router model, Graph representations, cloning sandbox, routing tables
├── algorithms.py               # BFS, DFS, Dijkstra, Tarjan Bridges/APs, Benchmark Suite, Reports
├── simulation.py               # Playback scrubbing, dual comparison, forwarding, history
├── topology_registry.py        # Centralized data-driven registry discovering JSON topologies in data/
├── report.py                   # Multi-format report generation (JSON, CSV for simulations, failures, benchmarks)
├── theme.py                    # High-contrast light-theme CSS tokens, badges, and step cards
├── start.sh                    # Quick-start launcher script
├── pytest.ini                  # Pytest configuration with pythonpath set to project root
├── data/                       # Validated JSON topology presets
│   ├── reference_network.json  # Reference 7-Node WAN topology
│   ├── sample_network.json     # 6-Node Interconnected Mesh network
│   ├── ring_network.json       # 6-Node Circular Ring topology
│   ├── disconnected_network.json # Disconnected LAN with two isolated subnets
│   ├── direct_network.json     # Linear chain network (R1-R2-R3-R4)
│   ├── multi_route_network.json # Multi-route spine-leaf network
│   └── offline_router_network.json # Bridge router offline bypass scenario
├── tests/                      # Automated unit test suite (145 tests, 100% pass)
│   ├── test_v3_features.py     # Comprehensive tests for Failure Lab, Dijkstra, Resilience, Benchmarks, Exports
│   ├── test_bfs.py             # BFS unweighted shortest path tests
│   ├── test_dfs.py             # DFS path validity & stack mechanics tests
│   ├── test_bfs_dfs_comparison.py # Comparative evaluation engine tests
│   ├── test_network.py         # Graph data structure & dynamic editing tests
│   ├── test_simulation.py      # Simulation state and invalidation tests
│   ├── test_reports_and_features.py # Traversal, comparison, report and visualizer tests
│   ├── test_topology_import_export.py # JSON export, import, round-trip, & schema validation tests
│   ├── test_topology_registry.py # Data-driven topology registry discovery & fallback tests
│   ├── test_simulation_report.py # Authoritative JSON simulation report generation tests
│   ├── test_edge_cases.py      # Graph & routing edge case tests
│   ├── test_co3_searching_sorting.py # Searching and sorting utility tests
│   ├── test_co4_traversal_tree.py # Traversal tree invariant verification tests
│   └── test_co5_table_routing.py # Routing table hop-by-hop forwarding tests
├── requirements.txt            # Project dependencies (streamlit, plotly, pandas, pytest, kaleido)
└── README.md                   # Documentation & setup guide
```

---

## 4. Setup and Execution

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Virtual environment (recommended)

### Installation
```bash
git clone <repository-url>
cd Netroute
pip install -r requirements.txt
```
*(Dependencies: `streamlit`, `plotly`, `pandas`, `pytest`, `kaleido`)*

### Running Automated Tests
```bash
python3 -m pytest
```
Or run with verbose output:
```bash
python3 -m pytest -v
```

### Launching the Application
You can launch the app directly:
```bash
streamlit run main.py
```
Or use the quick-launch script:
```bash
chmod +x start.sh
./start.sh
```

Open your browser at `http://localhost:8501` to use NetRoute v3.
