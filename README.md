# NetRoute — Network Packet Routing

**Micro Project 06**  
**Industry Focus:** Networking and Telecommunications  
**Integrated Course Outcomes:** **CO3, CO4, CO5**  
**Project Scope:** Implement graph-based routing algorithms for network packet transmission. Use DFS and BFS traversal to determine optimal paths. Compare graph-based routing approaches with traditional table-based routing.

Developed using **Python**, **Streamlit**, and **Plotly**.

---

## 1. Official Course Outcome Mapping

### CO3 — Searching and Sorting Algorithm Evaluation
**Official Outcome:** *Evaluate the performance of searching and sorting algorithms for solving engineering problems.*

- **Searching Evaluation (Linear vs. Binary Search):**
  - **Dataset:** Router IDs and routing records from the active network graph.
  - **Linear Search $O(n)$:** Scans sequentially from index 0 to $n-1$ on unsorted router lists; tracks genuine comparison counts and execution time.
  - **Binary Search $O(\log n)$:** Utilizes divide-and-conquer on sorted router records; eliminates half of the remaining search space per step; explains why sorted input is a mandatory prerequisite; gracefully handles absent router IDs and empty datasets.
- **Sorting Evaluation (Bubble Sort vs. Insertion Sort):**
  - **Bubble Sort $O(n^2)$:** Repeatedly compares and swaps adjacent inverted elements; tracks comparisons and swaps; includes early-exit optimization ($O(n)$ best case).
  - **Insertion Sort $O(n^2)$ / $O(n)$:** Iteratively builds a sorted array by picking elements and shifting larger items rightward; demonstrates $O(n)$ best case for already sorted data.
  - **Correctness Verification:** Automatically verifies sorted outputs against Python's canonical `sorted()` order.
- **Evaluation Display:** Compact comparison table detailing Algorithm, Input Size ($n$), Result Correctness, Actual Comparisons, Swaps/Shifts, Measured Time (ms), and Theoretical Time Complexity. Operation counts serve as the primary educational metric.

---

### CO4 — Tree Structures
**Official Outcome:** *Develop tree structures for solving engineering problems.*

- **Routing Traversal Tree:**
  - Constructs a genuine rooted Traversal Spanning Tree derived directly from the parent pointers recorded during Breadth-First Search (BFS) routing.
  - **Unique Root:** The source router serves as the tree root (Level 0 / Depth 0).
  - **Parent-Child Hierarchy:** Each reachable non-root router has exactly one parent in the tree.
  - **Directed Tree Edges:** Visualized using a dedicated hierarchical Plotly tree visualizer, highlighting tree edges from parent to child.
  - **Destination Path Highlight:** Clearly highlights the reconstructed root-to-destination path within the tree.
  - **Unreachable Node Exclusion:** Vertices disconnected from the source are strictly excluded from the tree.
  - **Acyclic Invariant:** Traversal tree is mathematically guaranteed to be cycle-free ($0$ loops), satisfying the tree invariant:
    $$\text{Tree Edges } E_{tree} = V_{tree} - 1$$
- **Engineering Comparison (Network Graph vs. Traversal Tree):**
  - Details why the physical network graph contains arbitrary cycles and redundant loops for fault tolerance ($E \ge V$), while the routing traversal tree is an acyclic spanning tree ($E = V' - 1$) used to resolve a single deterministic forwarding path.

---

### CO5 — Graph-Based Packet Routing vs. Traditional Routing Table Comparison
**Official Outcome:** *Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems.*

- **Graph-Based Packet Routing:**
  - Network graph representation: Routers as vertices ($V$), transmission links as edges ($E$).
  - **BFS Routing:** FIFO queue (`collections.deque`); discovers the minimum-hop route in unweighted networks.
  - **DFS Routing:** LIFO stack (`list`); discovers valid reachable routes without minimum-hop guarantee.
  - **Route Reconstruction:** Traces predecessor pointers backward from destination to source in $O(L)$ time.
  - **Interactive Packet Stepper:** Animates hop-by-hop packet movement along discovered routes.
- **Traditional Forwarding Table Comparison:**
  - Generates router forwarding tables for each router displaying **Destination**, **Next Hop**, **Hop Count (Metric)**, and **Reachability Status**.
  - **Hop-by-Hop Table Forwarding Simulation (`simulate_table_forwarding`):** Simulates distributed packet transmission where each intermediate router independently looks up the packet's destination in its local table to determine the Next Hop.
  - **Failure Detection:** Detects and reports forwarding failures upon link severance, offline intermediate routers, routing loops, or missing destination entries without silently falling back to global search.
  - **Comparative Dimension Table:** Contrasts centralized on-demand graph traversal discovery against distributed $O(1)$ table forwarding.

---

### Supporting Implementation Foundations (CO1 & CO2)
- **CO1 (Data Structures):** Queue (`collections.deque`), Stack (`list`), and Min-Heap Priority Queue (`heapq`) live inspector with front/rear, top/bottom pointers and operation counters.
- **CO2 (Dynamic Representations):** Real-time synchronization between the dynamic Adjacency List $O(V + E)$ and the Adjacency Matrix $O(V^2)$.

---

## 3. Computational Complexity Matrix

| Algorithm | Category | Best Case | Average Case | Worst Case | Space Complexity | Engineering Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Linear Search** | Searching (CO3) | $O(1)$ | $O(n)$ | $O(n)$ | $O(1)$ auxiliary | Sequential lookup on unsorted router lists |
| **Binary Search** | Searching (CO3) | $O(1)$ | $O(\log n)$ | $O(\log n)$ | $O(1)$ auxiliary | Divide-and-conquer on sorted router records |
| **Bubble Sort** | Sorting (CO3) | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ auxiliary | Adjacent comparison with early-exit flag |
| **Insertion Sort** | Sorting (CO3) | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ auxiliary | Incremental insertion; fast on nearly-sorted data |
| **Traversal Tree** | Trees (CO4) | $O(V)$ | $O(V)$ | $O(V)$ | $O(V)$ | Acyclic rooted spanning tree ($E = V - 1$) |
| **BFS Routing** | Graph (CO5) | $O(V + E)$ | $O(V + E)$ | $O(V + E)$ | $O(V)$ | Guaranteed minimum-hop route discovery |
| **DFS Routing** | Graph (CO5) | $O(V + E)$ | $O(V + E)$ | $O(V + E)$ | $O(V)$ | Deep branch exploration with backtracking |
| **Table Lookup** | Forwarding (CO5)| $O(1)$ | $O(1)$ | $O(1)$ | $O(V)$ per router | Hop-by-hop Next Hop lookup at intermediate nodes |

---

## 3. Project File Structure

```
Netroute/
├── main.py                     # Streamlit application UI, dashboard, Plotly tree & graph engines, and tabs
├── network.py                  # Router and Graph models, JSON export/import validation, and generate_routing_table()
├── topology_registry.py        # Centralized data-driven registry discovering JSON topologies in data/
├── report.py                   # Dynamic JSON simulation report generation engine adhering to ISO-8601 schema
├── algorithms.py               # BFS, DFS, linear_search, binary_search, bubble_sort, insertion_sort, build_traversal_tree
├── simulation.py               # Playback engine, packet stepper, table forwarding simulation, and state invalidation
├── theme.py                    # Design system, high-contrast light theme CSS tokens, and card components
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
├── tests/                      # Automated unit test suite (101 tests, 100% pass)
│   ├── test_co3_searching_sorting.py   # Tests for linear/binary search & bubble/insertion sort
│   ├── test_co4_traversal_tree.py      # Tests for traversal tree invariants, root, and acyclic property
│   ├── test_co5_table_routing.py       # Tests for routing tables and table forwarding simulation
│   ├── test_bfs.py                     # BFS unweighted shortest path tests
│   ├── test_dfs.py                     # DFS path validity & stack mechanics tests
│   ├── test_bfs_dfs_comparison.py      # BFS vs DFS comparative evaluation engine tests
│   ├── test_network.py                 # Graph data structure & dynamic editing tests
│   ├── test_simulation.py              # Simulation state and invalidation tests
│   ├── test_topology_import_export.py  # JSON export, import, round-trip, & schema validation tests
│   ├── test_topology_registry.py       # Data-driven topology registry discovery & fallback tests
│   ├── test_simulation_report.py       # Authoritative JSON simulation report generation tests
│   └── test_edge_cases.py              # Tests covering 20 comprehensive graph & routing edge cases
└── README.md                   # Project documentation and faculty demonstration guide
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

## 6. Installation and Execution

### Step 1: Clone or Navigate to Directory
```bash
cd "/Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My Drive/my_project/Netroute"
```

### Step 2: Activate Environment & Install Dependencies
```bash
source .venv/bin/activate
pip install -r requirements.txt
```
*(Your prompt will display `(.venv)`).*

### Step 3: Run Automated Test Suite
Run with `pytest`:
```bash
pytest -v
```
Or run with Python's built-in `unittest` runner:
```bash
python3 -m unittest discover tests -v
```

### Step 4: Launch the Streamlit Web Application
```bash
streamlit run main.py
```
Open your browser at `http://localhost:8501`.

---

## 5. Faculty Viva Voce Demonstration Guide

When presenting the project to faculty, follow this structured demonstration:

### Demonstrating CO3 — Searching and Sorting
1. Click on the **"CO3: Searching & Sorting Evaluation"** tab.
2. In the **Searching Evaluation** panel:
   - Search for an existing router ID (e.g., `N4`): observe that **Linear Search** takes 4 comparisons while **Binary Search** takes only 1–2 comparisons ($O(\log n)$).
   - Search for an absent router ID (e.g., `N99`): observe that Linear Search scans all elements, whereas Binary Search quickly terminates.
   - Highlight the explanation of why Binary Search requires sorted data (divide-and-conquer half elimination).
3. In the **Sorting Evaluation** panel:
   - Select the **"Reverse-Sorted Worst Case"** input: observe that both Bubble Sort and Insertion Sort execute $O(n^2)$ comparisons.
   - Switch to the **"Already Sorted Best Case"** input: observe that Insertion Sort finishes with 0 shifts and $n-1$ comparisons, proving its optimal $O(n)$ best-case behavior.
   - Note the **Compact CO3 Comparison Table** summarizing operation counts and theoretical complexities.

### Demonstrating CO4 — Tree Structures
1. Click on the **"CO4: Routing Traversal Tree Inspector"** tab.
2. View the **Traversal Spanning Tree** Plotly figure:
   - Point out that **Source Router `N1`** is the unique **Root** (Level 0 / Depth 0).
   - Point out that all discovered routers appear as child nodes placed strictly by traversal level/depth.
   - Highlight that the path from Root to Destination (`N7`) is traced along tree edges in green.
3. Review the **Tree Invariants Card**:
   - Verify the Single Root condition.
   - Verify the edge count invariant: $E_{tree} = V_{tree} - 1$.
   - Verify that the traversal tree is strictly **Acyclic** ($0$ cycles), even though the physical network graph contains cycles.
4. Review the **Engineering Distinction Table** explaining how a cycle-free traversal spanning tree differs from a mesh network graph with redundant links.

### Demonstrating CO5 — Graph Routing vs. Traditional Routing Table Comparison
1. Click on the **"CO5: Packet Routing & Routing Table Comparison"** tab.
2. Under **Traditional Router Routing Table**:
   - Inspect the forwarding table generated for Router `N1`: Destination, Next Hop, Hop Count, and Status.
   - Explain how a physical router looks up the Next Hop for incoming packets.
3. Under **Hop-by-Hop Table Forwarding Simulation**:
   - Observe the step-by-step forwarding log as the packet moves from router to router based on local table lookups.
   - Go to the Failure Lab or cut a link along the route: demonstrate that table forwarding reports a forwarding failure (`LINK_SEVERED` or `NO_ROUTE_TO_HOST`) without silently falling back to a global graph traversal.
4. Review the **Architectural Dimension Comparison Table** contrasting centralized on-demand graph search (BFS) with distributed hop-by-hop forwarding tables.

---

### Demonstrating BFS vs. DFS Algorithm Comparison
1. Click on the **"BFS vs. DFS Comparison"** tab.
2. Observe the **Executive KPI Scorecard**:
   - Compares **Hop Counts** ($H_{BFS}$ vs $H_{DFS}$), highlighting the provable optimality of BFS.
   - Compares **Exploration Coverage** (number and % of visited routers).
   - Compares **Peak Auxiliary Structure Footprint** (FIFO Queue size vs LIFO Stack depth).
3. Review the **Side-by-Side Dual Network Figures**:
   - Left canvas shows the concentric radial breadth exploration of BFS and its optimal shortest route in solid blue.
   - Right canvas shows the deep-branch probe and backtracking behavior of DFS in purple.
4. Review the **"Which Algorithm is Best?" Authoritative Verdict**:
   - Explains why BFS is strictly best for packet forwarding (minimizes latency, conserves bandwidth, predictable concentric frontier).
   - Explains the specific scenarios where DFS is preferred (STP loop/cycle detection, Tarjan's single point of failure analysis, topological sorting, memory-constrained IoT nodes).
5. Explore the **Interactive Scenario Selector** to see real-world recommendations across 6 engineering challenges.
6. Review the **Professional Engineering Suggestions & Architectural Guidelines** covering production protocol deployment, cycle detection, IDDFS, and TTL guardrails.

---

## 6. Manual Execution Guide

To launch and run NetRoute manually from the terminal:

```bash
# 1. Navigate to the project root directory
cd "/Users/jeslinjp/Library/CloudStorage/GoogleDrive-jeslin3379@gmail.com/My Drive/my_project/Netroute"

# 2. Ensure dependencies are installed
python3 -m pip install -r requirements.txt

# 3. Launch the Streamlit application
python3 -m streamlit run main.py

# 4. Access the web dashboard in your browser at:
# http://localhost:8501
```

