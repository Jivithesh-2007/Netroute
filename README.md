# NetRoute — Network Packet Routing Simulator

**Industry Focus:** Networking, Telecommunications, and Distributed Systems  
**Architecture:** Simulation-First Python / Streamlit Application  
**Visualization:** Interactive Plotly Network Diagrams & Spanning Trees  

NetRoute is a professional, interactive, simulation-first network routing application. It allows network engineers, computer science students, and researchers to design and edit network topologies, observe step-by-step BFS and DFS packet traversals with live data structure states, compare both algorithms through synchronized simulations, analyze graph theoretical properties, inspect routing tables, and export standardized JSON simulation reports.

---

## 1. Application Navigation & Core Features

NetRoute uses a clean, compact Streamlit sidebar navigation system structured into 11 specialized sections:

1. **Dashboard:** High-level network status, KPI metric cards (Active Routers, Transmission Links, Connectivity State, Simulation Engine Status), interactive topology preview, and quick-action launchers.
2. **Topology Studio:** Full visual graph editor supporting:
   - Adding, deleting, renaming, and repositioning routers ($X, Y$ coordinates).
   - Toggling router availability (Online / Offline).
   - Adding and removing transmission links with custom weights / costs.
   - Simulating physical link failures (Sever Link / Restore Link).
   - Balanced circular auto-layout and topology presets (Reference WAN, Ring, Mesh, Disconnected, Linear Chain, Multi-Route, Offline Router).
   - Clear network operation with explicit confirmation safety.
3. **Traversal Simulator:** Primary interactive simulation engine:
   - Source and destination endpoint selection.
   - Algorithm selection: Breadth-First Search (BFS) or Depth-First Search (DFS).
   - Step-by-step playback controls: First Step (`|<<`), Previous (`<`), Next (`>`), Last (`>>|`), and interactive step scrubber slider.
   - Distinct visual node and edge states: Source, Destination, Active Processing Router, Discovered Neighbors, Visited Routers, Explored Edges, Discovered Route, Offline Routers, Severed Links.
   - Dedicated live Queue (BFS) and Stack (DFS) inspectors displaying current contents, front/rear and top pointers, operation counters, and peak frontier depths.
   - Step execution cards explaining every internal event.
   - Hop-by-hop packet forwarding animation along discovered routes.
   - Downloadable JSON Simulation Report containing full runtime data, topology snapshot, and step trace.
4. **BFS vs. DFS Comparison:** Dedicated dual-simulation comparative analysis page:
   - Synchronized side-by-side visual graphs running on the identical graph snapshot and endpoints.
   - Synchronized playback controls advancing both algorithms in lockstep.
   - Displays live BFS Queue state and DFS Stack state simultaneously.
   - Comprehensive metrics comparison table (Hop Count, Routers Visited, Explored Edges, Enqueues/Pushes, Peak Memory, Execution Time).
   - Authoritative engineering verdict explaining why BFS guarantees minimal latency in unweighted networks while DFS explores deep branches.
   - Downloadable combined comparison JSON report.
5. **Data Structures Inspector:** Live inspection of internal data structures:
   - Graph representations: Adjacency List $O(V + E)$ and Adjacency Matrix $O(V^2)$.
   - Queue and Stack evolution tables.
   - Searching evaluation (Linear Search $O(n)$ vs. Binary Search $O(\log n)$) on adaptive network datasets.
   - Sorting evaluation (Bubble Sort $O(n^2)$ vs. Insertion Sort $O(n^2)$) with operation counts and correctness verification.
6. **Traversal Tree:** Spanning tree analysis:
   - Hierarchical Plotly tree visualizer derived directly from algorithm predecessor / parent pointers.
   - Tree root at source router with children descending by distance levels.
   - Root-to-destination path highlighted within the tree.
   - Mathematical invariant verification: $E_{tree} = V_{tree} - 1$, acyclic check, connected component check, and exclusion of unreachable nodes.
7. **Routing Table Simulator:** Traditional distributed hop-by-hop packet forwarding:
   - Generates local forwarding tables for every router displaying Destination, Next Hop, Metric Hops, and Reachability.
   - Simulates hop-by-hop forwarding where each router independently consults its own local routing table.
   - Real failure detection: missing destination entries, offline intermediate routers, severed links, routing loops, and TTL expiration.
8. **Network Analysis:** Graph topology diagnostics:
   - Router degree distribution (in/out/total degree, min/max/average degree).
   - Connected subnets (components) identification.
   - Source reachability matrix across all target routers.
9. **Simulation History:** Session log of all executed single traversals and dual comparisons:
   - Summary table with timestamps, endpoints, algorithms, hop counts, and step counts.
   - Historical run inspector with full JSON preview and one-click report download.
10. **Import / Export:** Robust data interchange:
    - Export active topology as JSON preserving router coordinates, weights, and failure flags.
    - Import topology JSON with transactional schema validation (rejection of duplicate IDs, self-loops, negative weights, and missing endpoints without corrupting the active graph).
    - Download latest single simulation and dual comparison JSON reports.
11. **Settings / Help:** User guide, theoretical algorithm foundations, time and space complexity matrix, and application state factory reset.

---

## 2. Computational Complexity Matrix

| Algorithm / Operation | Data Structure | Time Complexity | Auxiliary Space | Shortest Hop Guarantee? |
| :--- | :--- | :--- | :--- | :--- |
| **BFS Traversal** | FIFO Queue (`deque`) | $O(V + E)$ | $O(V)$ | **Yes** (Unweighted networks) |
| **DFS Traversal** | LIFO Stack (`list`) | $O(V + E)$ | $O(V)$ | **No** (Explores branches deeply) |
| **Adjacency List** | Hash Map of Lists | $O(V + E)$ space | $O(V + E)$ | N/A |
| **Adjacency Matrix** | 2D Array | $O(V^2)$ space | $O(V^2)$ | N/A |
| **Traversal Tree** | Rooted Spanning Tree | $O(V)$ | $O(V)$ | Verified ($E = V - 1$, Acyclic) |
| **Table Lookup** | Local Forwarding Table | $O(1)$ per hop | $O(V)$ per router | Dependent on routing table |
| **Linear Search** | Sequential Array | $O(n)$ | $O(1)$ | N/A |
| **Binary Search** | Sorted Array | $O(\log n)$ | $O(1)$ | N/A |
| **Bubble Sort** | Array | $O(n^2)$ | $O(1)$ | N/A |
| **Insertion Sort** | Array | $O(n^2)$ | $O(1)$ | N/A |

---

## 3. Project Architecture

```
Netroute/
├── main.py                     # Streamlit application entrypoint & sidebar navigation router
├── views.py                    # Modular view renderers for all 11 application sections
├── visualizer.py               # Plotly network graph and tree visualization engines
├── network.py                  # Router model, Graph representation, adjacency list/matrix, routing tables
├── algorithms.py               # BFS, DFS, searching, sorting, traversal tree, comparison & reports
├── simulation.py               # Playback state, scrubbing, dual comparison, history, table forwarding
├── topology_registry.py        # Centralized data-driven registry discovering JSON topologies in data/
├── report.py                   # Dynamic JSON simulation report generation engine adhering to ISO-8601 schema
├── theme.py                    # High-contrast light-theme CSS tokens, badges, and UI components
├── pytest.ini                  # Pytest configuration with pythonpath set to project root
├── data/                       # Validated JSON topology presets
│   ├── reference_network.json  # Reference 7-Node WAN topology
│   ├── sample_network.json     # 6-Node Interconnected Mesh network
│   ├── ring_network.json       # 6-Node Circular Ring topology
│   ├── disconnected_network.json # Disconnected LAN with two isolated subnets
│   ├── direct_network.json     # Linear chain network (R1-R2-R3-R4)
│   ├── multi_route_network.json # Multi-route spine-leaf network
│   └── offline_router_network.json # Bridge router offline bypass scenario
├── tests/                      # Automated unit test suite (100% pass)
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
├── requirements.txt            # Project dependencies
└── README.md                   # Documentation & setup guide
```

---

## 4. Topology JSON Schema and Import/Export

NetRoute supports full serialization, round-trip export, and safe import of network topologies via standardized JSON:

```json
{
  "directed": false,
  "name": "Reference 7-Node WAN",
  "description": "Standard 7-node reference WAN topology with redundant paths and weighted links.",
  "routers": [
    { "id": "N1", "name": "Server A (Src)", "x": 100.0, "y": 220.0, "is_online": true },
    { "id": "N2", "name": "Router 1", "x": 230.0, "y": 140.0, "is_online": true },
    { "id": "N3", "name": "Router 2", "x": 230.0, "y": 300.0, "is_online": true },
    { "id": "N4", "name": "Router 3", "x": 380.0, "y": 140.0, "is_online": true },
    { "id": "N5", "name": "Router 4", "x": 380.0, "y": 300.0, "is_online": true },
    { "id": "N6", "name": "Switch B", "x": 510.0, "y": 220.0, "is_online": true },
    { "id": "N7", "name": "Server B (Dst)", "x": 630.0, "y": 220.0, "is_online": true }
  ],
  "edges": [
    ["N1", "N2", 4.0],
    ["N1", "N3", 8.0],
    ["N2", "N3", 3.0],
    ["N2", "N4", 10.0],
    ["N3", "N5", 2.0],
    ["N4", "N5", 5.0],
    ["N4", "N6", 4.0],
    ["N5", "N6", 7.0],
    ["N6", "N7", 1.0]
  ],
  "failed_edges": []
}
```

### Schema Invariants & Safety Guarantees:
- **Router ID Validation:** 1–8 alphanumeric characters. Duplicate router IDs are strictly rejected.
- **Coordinates:** Numeric, finite coordinates $(x, y)$.
- **Strict Endpoint Integrity:** All edge endpoints must exist in the vertex set.
- **No Self-Loops:** Connections from a router to itself are prohibited.
- **Weights:** Finite, non-negative numeric floats ($\ge 0.0$).
- **Candidate Graph Isolation:** Validated into a temporary candidate graph first; the active graph is never left in a partially modified state if validation fails.

---

## 5. Dynamic Simulation Execution Report Schema

After executing BFS or DFS, users can download an authoritative JSON execution report capturing the current network state, execution trace, and complexity analysis:

```json
{
  "report_type": "NetRoute Simulation Report",
  "schema_version": "1.0",
  "generated_at": "2026-10-28T08:35:00.000000+00:00",
  "topology": {
    "name": "Reference 7-Node WAN",
    "router_count": 7,
    "connection_count": 9,
    "online_routers_count": 7,
    "offline_routers_count": 0,
    "online_routers": ["N1", "N2", "N3", "N4", "N5", "N6", "N7"],
    "offline_routers": [],
    "failed_links_count": 0,
    "failed_edges": [],
    "routers": [],
    "edges": []
  },
  "simulation": {
    "algorithm": "BFS (Breadth-First Search)",
    "source": "N1",
    "destination": "N7",
    "status": "success",
    "route": ["N1", "N2", "N4", "N6", "N7"],
    "hop_count": 4,
    "visited_order": ["N1", "N2", "N3", "N4", "N5", "N6", "N7"],
    "parent_mapping": { "N1": null, "N2": "N1", "N3": "N1", "N4": "N2", "N5": "N3", "N6": "N4", "N7": "N6" },
    "traversal_steps_count": 16,
    "traversal_steps": [],
    "queue_or_stack_states": [],
    "explored_edges": [],
    "execution_time_ms": 0.45,
    "message": "Valid route discovered: N1 -> N2 -> N4 -> N6 -> N7 (4 hops)."
  },
  "complexity": {
    "time": "O(V + E)",
    "auxiliary_space": "O(V)",
    "explanation": "BFS explores the network level-by-level using a FIFO queue..."
  }
}
```

---

## 6. Setup and Execution

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Virtual environment (recommended)

### Installation
```bash
git clone <repository-url>
cd Netroute
pip install -r requirements.txt
```
*(Dependencies: `streamlit`, `plotly`, `pandas`, `pytest`)*

### Running Automated Tests
```bash
python3 -m pytest
```
Or run with verbose output:
```bash
python3 -m pytest -v
```

### Launching the Application
```bash
streamlit run main.py
```
Open your browser at `http://localhost:8501` to use NetRoute.
