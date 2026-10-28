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
├── main.py                     # Streamlit application entrypoint & sidebar navigation
├── views.py                    # Modular view renderers for all 11 application sections
├── visualizer.py               # Plotly network graph and tree visualization engines
├── network.py                  # Router model, Graph representation, adjacency list/matrix, routing tables
├── algorithms.py               # BFS, DFS, searching, sorting, traversal tree, comparison & JSON reports
├── simulation.py               # Playback state, scrubbing, dual comparison, history, table forwarding
├── theme.py                    # Light-theme CSS tokens, badges, and UI components
├── data/                       # Bundled topology presets (reference_network.json, sample_network.json)
├── tests/                      # Automated test suite (77 tests, all passing)
│   ├── test_bfs.py
│   ├── test_dfs.py
│   ├── test_bfs_dfs_comparison.py
│   ├── test_network.py
│   ├── test_simulation.py
│   ├── test_reports_and_features.py
│   ├── test_co3_searching_sorting.py
│   ├── test_co4_traversal_tree.py
│   └── test_co5_table_routing.py
├── requirements.txt            # Project dependencies
└── README.md                   # Documentation & setup guide
```

---

## 4. Setup and Execution

### Prerequisites
- Python 3.10+ (tested on Python 3.13 and Python 3.14)
- Virtual environment (recommended)

### Installation
```bash
git clone <repository-url>
cd Netroute
pip install -r requirements.txt
```

### Running Automated Tests
```bash
python3 -m pytest
```

### Launching the Application
```bash
streamlit run main.py
```
Open your browser at `http://localhost:8501` to use NetRoute.
