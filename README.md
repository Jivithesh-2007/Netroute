# NetRoute — Network Packet Routing Simulator

**Micro Project 06** | **Industry Focus:** Computer Networking & Telecommunications  
**Integrated Course Outcomes:** **CO1, CO2, CO3, CO4, CO5**  
**Core Technologies:** Python 3.10+, Streamlit, Plotly, Pandas, Pytest (101 Automated Tests, 100% Passing)

---

## Executive Project Overview

**NetRoute** is an interactive, production-grade network packet routing simulator and educational laboratory designed to bridge theoretical computer science data structures with real-world telecommunications engineering. 

The platform simulates how network packets traverse modern telecommunication graphs, contrasting **centralized graph traversal algorithms** (Software-Defined Networking / Path Computation Elements) with **traditional distributed hop-by-hop routing table forwarding** (IP/OSPF/BGP routing). It features interactive step-by-step traversal playback, dynamic link/router failure injection, customizable network topologies, tree invariant validation, and automated ISO-8601 simulation report generation.

---

## 1. Comprehensive Course Outcome (CO) Explanations

NetRoute provides direct, mathematically rigorous, and fully test-verified implementations for all five core Computer Science & Engineering Course Outcomes (**CO1 through CO5**):

```
                                  NETROUTE CO ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  CO1: Linear Data Structures       │  Queue (FIFO: BFS), Stack (LIFO: DFS), Heap (QoS) │
├────────────────────────────────────┼───────────────────────────────────────────────────┤
│  CO2: Non-Linear Dynamic Graphs    │  Adjacency List O(V+E) ⇄ Adjacency Matrix O(V²)   │
├────────────────────────────────────┼───────────────────────────────────────────────────┤
│  CO3: Searching & Sorting          │  Linear vs. Binary Search & Bubble vs. Insertion  │
├────────────────────────────────────┼───────────────────────────────────────────────────┤
│  CO4: Tree Structures              │  BFS Traversal Spanning Tree (E = V - 1, Acyclic) │
├────────────────────────────────────┼───────────────────────────────────────────────────┤
│  CO5: Graph Routing vs. Tables     │  Centralized Traversal vs. Distributed Forwarding │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### CO1 — Linear Data Structures (Queues, Stacks, Priority Queues)

> **Official Course Outcome:**  
> *Implement and analyze linear data structures (Stack, Queue, Priority Queue) for solving engineering problems.*

#### 1. Engineering Motivation in Telecommunications
- **FIFO Queue:** Real-world network switches and routers maintain FIFO packet buffers (e.g., ring buffers and output interface queues) to forward incoming packets in arrival order without packet starvation.
- **LIFO Stack:** Deep routing exploration, recursive packet backtracking, and Call Stack tracking in network diagnostic probes (e.g., Traceroute, route poison reverse).
- **Min-Heap Priority Queue:** Used in Quality-of-Service (QoS) traffic class scheduling, weighted fair queuing, and Dijkstra's link-state shortest path calculation.

#### 2. Technical Implementation in NetRoute
- **Queue Implementation:** Implemented via `collections.deque` inside `bfs()` in [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py#L33-L120). Operates in strictly $O(1)$ amortized time for `append()` (enqueue) and `popleft()` (dequeue).
- **Stack Implementation:** Implemented via Python dynamic array `list` inside `dfs()` in [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py#L336-L430). Operates in $O(1)$ amortized time for `append()` (push) and `pop()` (pop).
- **Live Memory & Pointer Telemetry:** Tracks peak memory footprint, queue front/rear pointers, stack top/bottom pointers, and genuine operation counters (`total_enqueues`, `total_dequeues`, `total_pushes`, `total_pops`, `max_structure`).

#### 3. Verification & UI Tab
- **Interactive UI:** Displayed in the **"Network Routing"** step inspector and **"BFS vs. DFS Comparison"** executive scorecard.
- **Automated Tests:** Verified in [`test_bfs.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_bfs.py) and [`test_dfs.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_dfs.py).

---

### CO2 — Non-Linear Dynamic Graph Representations

> **Official Course Outcome:**  
> *Implement and analyze non-linear dynamic data structures (Adjacency List, Adjacency Matrix) and graph operations for engineering systems.*

#### 1. Engineering Motivation in Telecommunications
Modern telecommunication networks are dynamic mesh graphs $G = (V, E)$, where routers are vertices $V$ and physical links (fiber optic, Ethernet, microwave) are edges $E$. Links can fail due to fiber cuts, and routers can go offline due to power failure or maintenance. The underlying graph data structure must support dynamic edge insertion, vertex deletion, weight adjustments, and status toggles without corrupting topology integrity.

#### 2. Technical Implementation in NetRoute
- **Graph Model:** Implemented in `Graph` within [`network.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/network.py#L45-L263).
- **Dual Representation Synchronization:**
  - **Adjacency List:** `Dict[str, List[str]]` providing optimal space efficiency $O(V + E)$ and rapid neighbor lookups $O(\text{deg}(v))$ for sparse networks.
  - **Adjacency Matrix:** 2D binary matrix $O(V^2)$ generated via `get_adjacency_matrix()` for instant $O(1)$ link existence queries.
- **Dynamic Topology Mutation:**
  - Cascading deletion: Removing a router safely cascades to purge all incident links and active routes.
  - Failure Lab: Allows live toggling of router power (`is_online`) and link severance (`failed_edges`) without graph rebuilds.
  - Candidate Graph Isolation: JSON topology imports are validated in an isolated candidate graph before updating active memory.

#### 3. Verification & UI Tab
- **Interactive UI:** Managed via the **Sidebar Topology Controls** and **Network Graph Canvas**.
- **Automated Tests:** Verified in [`test_network.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_network.py) and [`test_topology_import_export.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_topology_import_export.py).

---

### CO3 — Searching and Sorting Algorithm Evaluation

> **Official Course Outcome:**  
> *Evaluate the performance of searching and sorting algorithms for solving engineering problems.*

#### 1. Engineering Motivation in Telecommunications
- **Searching in Routing:** Routers continuously search large routing information bases (RIB) and forwarding information bases (FIB) to locate next-hop gateways for incoming IP addresses.
- **Sorting in Routing:** Routers sort candidate routes based on metric costs (hop count, link latency, bandwidth) to select best paths and compute backup routes.

#### 2. Technical Implementation in NetRoute
Implemented in [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py#L659-L928) with dynamic topology extraction (`get_adaptive_datasets()` in [`main.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/main.py#L48-L75)):

- **Searching Evaluation:**
  - **Linear Search $O(n)$:** Scans router records sequentially; tracks real comparison counts; works on unsorted inputs.
  - **Binary Search $O(\log n)$:** Divide-and-conquer algorithm eliminating half of remaining search space per step. Demonstrates why sorted data is a mandatory precondition; handles absent targets and empty datasets gracefully.
- **Sorting Evaluation:**
  - **Bubble Sort $O(n^2)$:** Adjacent pair comparison and swap algorithm with an early-exit flag achieving $O(n)$ best-case on already-sorted arrays.
  - **Insertion Sort $O(n^2)$ / $O(n)$:** Incremental element insertion with rightward shifting. Achieves optimal $O(n)$ time with 0 shifts on sorted arrays.
  - **Automated Correctness Proof:** Compares output against canonical Python `sorted()` results.

#### 3. Complexity & Empirical Metric Summary

| Algorithm | Best Case | Average Case | Worst Case | Space | Primary Tracked Metric |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Linear Search** | $O(1)$ | $O(n)$ | $O(n)$ | $O(1)$ | Element Comparisons |
| **Binary Search** | $O(1)$ | $O(\log n)$ | $O(\log n)$ | $O(1)$ | Midpoint Divisions & Range Narrowing |
| **Bubble Sort** | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Adjacent Swaps & Pass Flags |
| **Insertion Sort**| $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Shifts & Element Insertions |

#### 4. Verification & UI Tab
- **Interactive UI:** Dedicated **"CO3: Searching & Sorting"** tab with sub-tabs for Searching and Sorting, preset worst/best case dataset selectors, and interactive target query inputs.
- **Automated Tests:** Verified in [`test_co3_searching_sorting.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_co3_searching_sorting.py) (9 unit tests).

---

### CO4 — Tree Structures & Traversal Spanning Trees

> **Official Course Outcome:**  
> *Develop tree structures for solving engineering problems.*

#### 1. Engineering Motivation in Telecommunications
Physical mesh networks contain redundant loops and cycles to guarantee survivability. However, transmitting data over cyclic networks without loop avoidance causes catastrophic broadcast storms. Network protocols like **STP (Spanning Tree Protocol - IEEE 802.1D)** and **RSTP** prune cyclic network graphs into acyclic spanning trees to guarantee loop-free forwarding.

#### 2. Technical Implementation in NetRoute
Implemented via `build_traversal_tree()` in [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py#L929-L1008):

- **Rooted Spanning Tree Generation:**
  - Built dynamically from the parent predecessor pointers recorded during Breadth-First Search (BFS) routing.
  - **Unique Root:** The selected source router serves as the root (Level 0 / Depth 0).
  - **Parent-Child Hierarchy:** Every reachable node has exactly one parent pointer ($parents[u] = p$).
  - **Cycle-Free (Acyclic) Invariant:** Mathematically guaranteed to contain $0$ loops.
  - **Edge-to-Vertex Invariant:** Satisfies the fundamental tree theorem:
    $$\text{Tree Edges } E_{tree} = V_{reachable} - 1$$
  - **Destination Path Highlight:** Highlights the unique root-to-destination branch within the tree.
  - **Unreachable Node Exclusion:** Vertices partitioned from the source are strictly excluded from the tree.

#### 3. Engineering Contrast: Network Graph vs. Traversal Tree

| Property | Physical Network Graph $G=(V,E)$ | Routing Traversal Tree $T=(V',E')$ |
| :--- | :--- | :--- |
| **Topology** | Mesh, Ring, or Spine-Leaf | Strictly Rooted Hierarchical Tree |
| **Cycle Invariant** | Contains cycles for fault-tolerance ($E \ge V$) | Strictly Acyclic ($0$ cycles, $E' = V' - 1$) |
| **Path Multiplicity** | Multiple redundant paths exist between pairs | Exactly one unique simple path from Root to any node |
| **Network Role** | Physical infrastructure layout | Loop-free deterministic packet forwarding path |

#### 4. Verification & UI Tab
- **Interactive UI:** Dedicated **"CO4: Routing Traversal Tree"** tab featuring a hierarchical Plotly tree visualizer, root-to-destination branch highlights, and live tree invariant metrics.
- **Automated Tests:** Verified in [`test_co4_traversal_tree.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_co4_traversal_tree.py) (5 comprehensive tests).

---

### CO5 — Graph-Based Packet Routing vs. Traditional Routing Table Comparison

> **Official Course Outcome:**  
> *Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems.*

#### 1. Engineering Motivation in Telecommunications
- **Centralized Graph Traversal:** In **Software-Defined Networking (SDN)** and **OpenFlow**, a centralized controller maintains the global network graph, computes paths using traversal algorithms (BFS/Dijkstra), and programs forwarding tables into switches.
- **Distributed Table-Based Forwarding:** In traditional IP networks (**OSPF, BGP, RIP**), each autonomous router maintains a local routing table. When a packet arrives, the router inspects the destination IP, performs a local table lookup, and pushes the packet out to the designated **Next Hop**.

#### 2. Technical Implementation in NetRoute
Implemented across [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py#L33-L430), [`network.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/network.py#L264-L330), and [`simulation.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/simulation.py#L264-L350):

- **Graph-Based Packet Routing:**
  - **BFS Routing:** Explores the network radially level-by-level; provably guarantees the minimum-hop route in unweighted graphs in $O(V + E)$ time.
  - **DFS Routing:** Explores deep paths along branches before backtracking using a LIFO stack in $O(V + E)$ time; demonstrates path discovery without shortest-hop guarantees.
  - **Route Reconstruction:** Backtracks predecessor pointers from destination to source in $O(L)$ time, where $L$ is the hop count.
- **Traditional Forwarding Table Simulation:**
  - Generates router forwarding tables via `generate_routing_table()`, displaying **Destination**, **Next Hop**, **Hop Metric**, and **Reachability Status**.
  - **Hop-by-Hop Table Forwarding Simulation (`simulate_table_forwarding`):** Simulates distributed packet transmission where each intermediate router independently looks up the packet's destination in its local table.
  - **Failure Handling:** Detects and reports forwarding failures upon link severance, offline intermediate routers, routing loops, or missing destination entries without silently falling back to global search.

#### 3. Architectural Comparison: Graph Traversal vs. Table Forwarding

| Architectural Dimension | Graph Traversal Routing (SDN / Centralized) | Traditional Table Forwarding (Distributed IP) |
| :--- | :--- | :--- |
| **Control Model** | Centralized controller with global graph visibility | Autonomous distributed routers with local visibility |
| **Forwarding Decision** | Pre-computed complete end-to-end route | Hop-by-hop local next-hop table lookup |
| **Per-Packet Lookup Cost** | $O(L)$ route traversal | $O(1)$ hash table or $O(\log n)$ trie lookup |
| **Failure Reaction** | Controller recomputes global graph traversal | Link failure triggers distributed convergence (LSA/BGP update) |
| **Memory Footprint** | Controller stores complete adjacency matrix $O(V^2)$ | Each router stores only local forwarding table $O(V)$ |

#### 4. Verification & UI Tab
- **Interactive UI:** Dedicated **"CO5: Routing Table Forwarding"** tab with router forwarding table inspector, step-by-step table forwarding simulation, failure detection, and architectural comparison matrix.
- **Automated Tests:** Verified in [`test_co5_table_routing.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_co5_table_routing.py) (6 tests) and [`test_bfs_dfs_comparison.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_bfs_dfs_comparison.py).

---

## 2. Integrated Course Outcomes Summary Matrix

| CO ID | Formal Course Outcome Title | Bloom's Level | Core Data Structures | Implementation Files | Streamlit UI Tab | Automated Test Suite |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CO1** | Linear Data Structures & Operations | Apply / Analyze (L3/L4) | FIFO Queue (`deque`), LIFO Stack (`list`), Min-Heap (`heapq`) | [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py) | Network Routing & BFS/DFS Compare | [`test_bfs.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_bfs.py), [`test_dfs.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_dfs.py) |
| **CO2** | Non-Linear Dynamic Graph Representations | Apply / Create (L3/L6) | Adjacency List `Dict[str, List]`, Adjacency Matrix $O(V^2)$ | [`network.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/network.py) | Sidebar Controls & Network Canvas | [`test_network.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_network.py), [`test_topology_import_export.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_topology_import_export.py) |
| **CO3** | Searching & Sorting Algorithm Evaluation | Evaluate (L5) | Arrays, Dynamic Lists, Divide-and-Conquer pointers | [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py), [`main.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/main.py) | CO3: Searching & Sorting | [`test_co3_searching_sorting.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_co3_searching_sorting.py) |
| **CO4** | Tree Structures & Invariants | Create / Evaluate (L6/L5) | Rooted Spanning Tree, Parent Pointer Dicts | [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py), [`main.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/main.py) | CO4: Routing Traversal Tree | [`test_co4_traversal_tree.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_co4_traversal_tree.py) |
| **CO5** | Graph Routing vs. Table Forwarding | Evaluate / Analyze (L5/L4) | Graph Traversals, Router Forwarding Tables | [`algorithms.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/algorithms.py), [`network.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/network.py), [`simulation.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/simulation.py) | CO5: Routing Table Forwarding | [`test_co5_table_routing.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_co5_table_routing.py), [`test_edge_cases.py`](file:///Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My%20Drive/my_project/Netroute/tests/test_edge_cases.py) |

---

## 3. Computational Complexity Matrix

| Algorithm | Category | Best Case | Average Case | Worst Case | Auxiliary Space | Engineering Role in Telecommunications |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Linear Search** | Searching (CO3) | $O(1)$ | $O(n)$ | $O(n)$ | $O(1)$ | Unsorted routing table lookup; sequential ACL rule evaluation |
| **Binary Search** | Searching (CO3) | $O(1)$ | $O(\log n)$ | $O(\log n)$ | $O(1)$ | Binary prefix search; divide-and-conquer on sorted IP route tables |
| **Bubble Sort** | Sorting (CO3) | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Baseline sorting; adjacent inverted swap metric with early-exit flag |
| **Insertion Sort** | Sorting (CO3) | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Online routing updates; high efficiency on nearly-sorted route tables |
| **Traversal Tree** | Trees (CO4) | $O(V)$ | $O(V)$ | $O(V)$ | $O(V)$ | Acyclic rooted spanning tree ($E = V - 1$) for loop-free broadcast |
| **BFS Routing** | Graph (CO5) | $O(V + E)$ | $O(V + E)$ | $O(V + E)$ | $O(V)$ | Guaranteed minimum-hop shortest route discovery in unweighted graphs |
| **DFS Routing** | Graph (CO5) | $O(V + E)$ | $O(V + E)$ | $O(V + E)$ | $O(V)$ | Deep branch exploration, cycle detection, and connectivity testing |
| **Table Lookup** | Forwarding (CO5) | $O(1)$ | $O(1)$ | $O(1)$ | $O(V)$ per router | Hop-by-hop Next Hop lookup at intermediate router line-cards |

---

## 4. Project Architecture & File Hierarchy

```
Netroute/
├── main.py                     # Streamlit web UI, Plotly visualizers, tabs, and dashboard layout
├── network.py                  # Router & Graph models, adjacency structures, table generator, JSON I/O
├── algorithms.py               # BFS, DFS, Linear/Binary Search, Bubble/Insertion Sort, Traversal Tree
├── simulation.py               # Simulation playback, packet stepper, table forwarding engine, state management
├── report.py                   # Dynamic ISO-8601 compliant JSON simulation execution report generator
├── topology_registry.py        # Centralized data-driven discovery engine for network presets in data/
├── theme.py                    # Design tokens, high-contrast theme CSS, and reusable UI components
├── pytest.ini                  # Pytest configuration with pythonpath set to project root
├── requirements.txt            # Python dependencies (streamlit, plotly, pandas, pytest)
├── start.md                    # Quick-start terminal instructions
├── data/                       # Validated JSON network topology presets
│   ├── reference_network.json  # Reference 7-Node WAN topology
│   ├── sample_network.json     # 6-Node Interconnected Mesh network
│   ├── ring_network.json       # 6-Node Circular Ring topology
│   ├── disconnected_network.json # Disconnected LAN with two isolated subnets
│   ├── direct_network.json     # Linear chain network (R1-R2-R3-R4)
│   ├── multi_route_network.json # Multi-route spine-leaf network
│   └── offline_router_network.json # Bridge router offline bypass scenario
└── tests/                      # Automated test suite (12 files, 101 tests, 100% pass)
    ├── test_co3_searching_sorting.py   # Searching (Linear/Binary) & Sorting (Bubble/Insertion) tests
    ├── test_co4_traversal_tree.py      # Tree invariants, single root, acyclic property tests
    ├── test_co5_table_routing.py       # Routing table generation & hop-by-hop forwarding tests
    ├── test_bfs.py                     # BFS minimum-hop & queue mechanics tests
    ├── test_dfs.py                     # DFS path validity & stack mechanics tests
    ├── test_bfs_dfs_comparison.py      # BFS vs DFS comparative scorecards & metrics tests
    ├── test_network.py                 # Graph data structures, adjacency sync, auto-layout tests
    ├── test_simulation.py              # Simulation state, playback, and invalidation tests
    ├── test_topology_import_export.py  # JSON export, import, round-trip, & schema validation tests
    ├── test_topology_registry.py       # Data-driven registry discovery & fallback tests
    ├── test_simulation_report.py       # Authoritative ISO-8601 simulation report generation tests
    └── test_edge_cases.py              # 20 exhaustive edge cases covering disconnections, loops, etc.
```

---

## 5. Topology JSON Schema and Safe Import/Export

NetRoute supports standardized serialization, round-trip export, and safe import of network topologies via JSON:

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

### Safety Guarantees & Invariants:
1. **Candidate Graph Isolation:** Topologies are loaded into a temporary candidate graph first. If validation fails, active memory remains untouched.
2. **Endpoint Integrity:** All edge endpoints must exist in the vertex set.
3. **No Self-Loops:** Connections from a router to itself are strictly prohibited.
4. **Weights:** Validated to be non-negative finite numeric floats ($\ge 0.0$).
5. **Router ID Validation:** 1–8 alphanumeric characters. Duplicate IDs are rejected.

---

## 6. Authoritative Simulation Execution Report Schema (ISO-8601)

Following any BFS or DFS simulation run, users can export an authoritative JSON simulation execution report compliant with ISO-8601 timestamping:

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
    "routers": [...],
    "edges": [...]
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
    "traversal_steps": [...],
    "queue_or_stack_states": [...],
    "explored_edges": [...],
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

## 7. Installation and Quick Start

### 1. Open Terminal and Navigate to Project
```bash
cd "/Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My Drive/my_project/Netroute"
```

### 2. Activate Virtual Environment
```bash
source .venv/bin/activate
```
*(Your prompt will display `(.venv)`).*

### 3. Run Automated Test Suite
Verify that all 101 tests pass across 12 test modules:
```bash
pytest -v
# or: python3 -m unittest discover tests -v
```

### 4. Launch the Streamlit Web Application
```bash
streamlit run main.py
```
Open your browser at:
```
http://localhost:8501
```

---

## 8. Faculty Viva Voce Demonstration Guide

When presenting NetRoute for academic evaluation, follow this structured walkthrough:

### Part 1: Demonstrating CO1 & CO2 (Foundational Data Structures)
1. In the **Network Routing** tab, execute a BFS traversal:
   - Expand the **"Queue State Inspector"** below the network graph.
   - Point out the FIFO enqueue/dequeue operations and the queue front/rear pointers.
2. In the **Sidebar Controls**:
   - Toggle an edge off or mark a router offline in the **Failure Lab**.
   - Show how the **Dynamic Adjacency List** updates immediately without full-page reloads.

### Part 2: Demonstrating CO3 (Searching & Sorting Performance Evaluation)
1. Click the **"CO3: Searching & Sorting"** tab.
2. Under **Searching Evaluation**:
   - Search for an existing router ID (e.g., `N4`): observe that **Linear Search** requires 4 comparisons, while **Binary Search** requires only 1–2 comparisons ($O(\log n)$).
   - Search for an absent router ID (e.g., `N99`): observe that Linear Search scans all $n$ elements, whereas Binary Search terminates in $\lfloor \log_2 n \rfloor + 1$ steps.
   - Highlight why sorted data is a mandatory precondition for Binary Search (divide-and-conquer half elimination).
3. Under **Sorting Evaluation**:
   - Select the **"Reverse-Sorted Worst Case"** input: observe that both Bubble Sort and Insertion Sort execute $O(n^2)$ comparisons.
   - Select the **"Already-Sorted Best Case"** input: observe that Insertion Sort finishes with 0 shifts and $n-1$ comparisons, demonstrating its optimal $O(n)$ best-case behavior.
   - Review the **CO3 Evaluation Table** summarizing operations, shifts, and theoretical complexities.

### Part 3: Demonstrating CO4 (Tree Structures & Invariants)
1. Click the **"CO4: Routing Traversal Tree"** tab.
2. Inspect the **Traversal Spanning Tree** Plotly figure:
   - Point out that the Source Router (`N1`) is the unique **Root** (Level 0 / Depth 0).
   - Show that all reachable nodes are arranged strictly by traversal level/depth.
   - Highlight the green highlighted branch tracing the deterministic path from Root to Destination (`N7`).
3. Review the **Tree Invariants Card**:
   - Verify the Single Root property.
   - Verify the tree edge formula: $E_{tree} = V_{tree} - 1$.
   - Verify that the traversal tree is strictly **Acyclic** ($0$ cycles), contrasting it with the physical mesh graph containing loops.

### Part 4: Demonstrating CO5 (Graph Routing vs. Traditional Routing Tables)
1. Click the **"CO5: Routing Table Forwarding"** tab.
2. Inspect the **Traditional Router Routing Table** generated for Router `N1`:
   - Point out Destination, Next Hop, Hop Count, and Reachability Status.
   - Explain how physical routers consult this table for $O(1)$ packet forwarding decisions.
3. In the **Hop-by-Hop Table Forwarding Simulation**:
   - Click **"Simulate Table Forwarding"** to trace the packet hop-by-hop through intermediate router tables.
   - Sever a link along the route in the Failure Lab: observe that table forwarding correctly reports `LINK_SEVERED` or `NO_ROUTE_TO_HOST` without silently falling back to global search.
4. Review the **Architectural Dimension Table** contrasting centralized SDN graph traversal against distributed hop-by-hop forwarding tables.

### Part 5: Demonstrating BFS vs. DFS Comparative Analysis
1. Click the **"BFS vs. DFS Comparison"** tab.
2. Review the **Executive KPI Scorecard**:
   - Compare **Hop Counts** ($H_{BFS} \le H_{DFS}$), showing provable BFS optimality for unweighted shortest paths.
   - Compare **Exploration Coverage** (% of network explored).
   - Compare **Peak Auxiliary Footprint** (FIFO Queue size vs LIFO Stack depth).
3. Review the **Authoritative Verdict**:
   - Explain why BFS is strictly superior for packet transmission (minimizes delay and bandwidth).
   - Explain where DFS is preferred in networking (STP loop/cycle detection, Tarjan's bridge/articulation point analysis, topological sorting).

---

## 9. Automated Test Suite & Edge Case Coverage

NetRoute includes a comprehensive test suite of **101 unit and integration tests** with 100% pass rate:

```bash
$ pytest -v
============================= 101 passed in 0.25s ==============================
```

### Edge Cases Verified in `test_edge_cases.py` (20 Exhaustive Scenarios):
1. **Source Equals Destination:** Path contains single node, 0 hops, 0 traversed edges.
2. **Reachable Destination:** Successful path discovery and valid parent mapping.
3. **Unreachable Destination:** Graceful failure reporting with no partial corruptions.
4. **Empty Graph:** Handled with clear user error message.
5. **Invalid Source / Destination:** Validated before algorithm execution.
6. **Offline Source Router:** Routing aborted immediately with descriptive error.
7. **Offline Destination Router:** Routing aborted immediately with descriptive error.
8. **Offline Intermediate Router:** Correctly bypassed to find alternative viable paths.
9. **Failed Direct Connection:** Automatically reroutes via alternative multi-hop path.
10. **Multiple Alternative Routes:** BFS deterministically picks the shortest-hop route.
11. **Cycles in Graph:** Visited sets prevent infinite loops in both BFS and DFS.
12. **Duplicate Connection Rejection:** Adding an existing edge is safely rejected.
13. **Invalid Connection Endpoints:** Connections referencing non-existent nodes rejected.
14. **Invalid Weights:** Negative or non-numeric edge weights rejected.
15. **Self-Links Prohibited:** Connections from a node to itself ($u \to u$) rejected.
16. **Topology Mutation Invalidation:** Mutating graph clears stale simulation results.
17. **Malformed JSON Import:** Invalid schema or corrupt syntax safely rejected.
18. **Routing Table Loops:** Loop detection prevents infinite ping-pong packet forwarding.
19. **Missing Forwarding Entries:** Handled gracefully as `NO_ROUTE_TO_HOST`.
20. **Disconnected Graphs:** BFS and DFS strictly explore only connected components.

---

## 10. Authors & Course Information

- **Project:** NetRoute — Network Packet Routing Simulator (Micro Project 06)
- **Course Focus:** Data Structures and Algorithms / Computer Networks
- **Target Outcome:** Full Integration and Evaluation of **CO1, CO2, CO3, CO4, and CO5**
- **License:** Open Academic Educational Resource
