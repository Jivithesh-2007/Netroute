# NetRoute — Interactive Network Packet-Routing Simulator

An interactive, educational network packet-routing web application developed using **Python**, **Streamlit**, and **Plotly**. NetRoute visualizes graph-based routing algorithms, genuine step-by-step queue, stack, and priority queue execution, dynamic link-weight editing, scenario-based network failure and recovery, simulation history/replay, interactive DSA challenges, and exportable research reports.

NetRoute aligns directly with **CO1**, **CO2**, and **CO5** of the Data Structures and Algorithms (DSA) engineering curriculum.

---

## 1. Academic Course Outcome Mapping

### CO1 — Stack, Queue, and Priority Queue Data Structures
- **Queue-Based BFS:** Implements genuine Breadth-First Search using a First-In-First-Out (FIFO) queue (`collections.deque`). Demonstrates level-by-level concentric exploration to discover the unweighted shortest-hop path between source and destination routers.
- **Stack-Based DFS:** Implements genuine Depth-First Search using an explicit Last-In-First-Out (LIFO) stack (`list`). Demonstrates deep branch exploration and explicit backtracking, showing that DFS discovers valid reachable paths without guaranteeing minimum hops.
- **Min-Heap Dijkstra:** Implements genuine Dijkstra's algorithm using a Min-Heap Priority Queue (`heapq`). Demonstrates greedy edge relaxation and tentative distance reduction, proving how Dijkstra minimizes cumulative link costs rather than hop count.
- **Live Data Structure Inspector:** Displays live internal data structure states at each execution step, including FIFO Front/Rear indicators, LIFO Top/Bottom markers, Min-Heap root tags, push/pop/enqueue/dequeue counts, edge relaxations, and peak capacity.

### CO2 — Dynamic Graphs & Link-Weight Management
- **Dynamic Adjacency List $O(V + E)$:** Serves as the primary dynamic graph representation. Routers (vertices) and transmission links (edges) are inserted, renamed, toggled, and deleted dynamically.
- **Interactive Link-Weight Editor:** Allows users to modify transmission link costs ($w \ge 0$) in real time with immediate recalculation and cache invalidation.
- **Dual Synchronized Representations:** Maintains real-time synchronization between the dynamic Adjacency List $O(V + E)$ and the Adjacency Matrix $O(V^2)$.
- **Component Failure States:** Supports independent toggling of router hardware faults (online/offline) and physical link severing (cut/repaired).

### CO5 — Graph Traversals, Shortest Paths, & Fault Tolerance
- **Algorithm Comparison:** Clearly separates BFS (minimum hops in unweighted graphs), DFS (arbitrary path via deep exploration), and Dijkstra (minimum total weight in non-negative weighted graphs).
- **Route Reconstruction via Parent Pointers:** Reconstructs the exact optimal path backward from the destination router to the source router using predecessor pointers.
- **Network Failure & Recovery Lab:** Dedicated scenario-based failure lab comparing baseline routes against detour routes and diagnosing network partitions when destinations become isolated.
- **Hop-by-Hop Packet Forwarding:** Animates packet delivery along discovered routes with interactive stepper and auto-stream playback.

---

## 2. Advanced Features Overview

### Feature A: Weighted Shortest-Path Routing with Dijkstra
- Implemented in `algorithms.py` using Python's standard `heapq`.
- Records step-by-step min-heap states, tentative distances, edge relaxations, and predecessor updates.
- Validates that edge weights are non-negative ($w \ge 0$).
- Handles cycles, offline router avoidance, severed links, and unreachable destinations.

### Feature B: Interactive Link-Weight Editor
- Allows selecting any connection and updating its transmission cost ($w \ge 0$).
- Outdated simulations are immediately invalidated and routes re-evaluated.
- Includes a dedicated `weighted_diff` preset demonstrating where BFS chooses $N1 \rightarrow N2 \rightarrow N4$ (2 hops, cost 13) while Dijkstra chooses $N1 \rightarrow N2 \rightarrow N3 \rightarrow N4$ (3 hops, cost 4).

### Feature C: Network Failure & Recovery Lab
- Dedicated scenario-based tab for simulating router power failure and link cuts.
- Real-time comparison between reference baseline routes and active detour routes.
- Displays hop differences, cost changes, active failure lists, and partition alerts.
- Single-click "Restore All Failures" functionality.

### Feature D: Simulation History & Traversal Replay
- Records completed routing runs in Streamlit session state with unique run IDs, timestamps, algorithm, path, hops, cost, and visited count.
- Side-by-side run comparison of two historical runs.
- Traversal replay: loads saved execution steps back into the live stepper engine.

### Feature E: DSA Challenge Mode
- Educational quizzes with 4 interactive scenarios:
  1. BFS Minimum-Hop Routing Prediction
  2. DFS Deep Exploration & Backtracking
  3. Network Partition & Unreachable Destination
  4. Dijkstra Minimum-Cost vs BFS Minimum-Hop
- Evaluates answers against actual graph and algorithm results with detailed pedagogical explanations and a "Watch Algorithm Execution" button.

### Feature F: Exportable Experiment Report
- Generates structured research and viva reports containing topology statistics, algorithm metrics, discovered routes, theoretical complexities, and explanations.
- Downloadable in clean JSON (`netroute_experiment_report.json`) and CSV (`netroute_experiment_report.csv`).

### Feature G: Dual Algorithm Live Arena (BFS vs. DFS Side-by-Side)
- Side-by-side visualization of BFS (FIFO Queue) and DFS (LIFO Stack) executing concurrently on the identical network topology.
- Real-time quantitative delta computation:
  - Route discovered & path differential.
  - Hop count differential ($\Delta = \text{DFS hops} - \text{BFS hops}$).
  - Path weight and link cost differential ($\Delta = \text{DFS cost} - \text{BFS cost}$).
  - Total execution latency differential ($\Delta = \text{DFS ms} - \text{BFS ms}$).
  - Total traversal steps differential (accounting for DFS dead-end backtracking pops).
  - Search sequence comparison and data structure operation metrics (enqueues/dequeues vs pushes/pops/backtracks).
- Exportable side-by-side comparison tables in CSV and JSON formats.

---

## 3. Computational Complexity

| Algorithm / Structure | Time Complexity | Auxiliary Space Complexity | Optimality Guarantee |
| :--- | :--- | :--- | :--- |
| **BFS Routing** | $O(V + E)$ | $O(V)$ | Guaranteed minimum-hop route in unweighted graphs |
| **DFS Routing** | $O(V + E)$ | $O(V)$ | No guarantee (finds valid reachable path; may take long detours) |
| **Dijkstra Routing** | $O((V + E) \log V)$ | $O(V)$ | Guaranteed minimum-total-cost route ($w \ge 0$) |
| **Adjacency List** | $O(V + E)$ build | $O(V + E)$ | Memory-efficient for sparse dynamic networks |
| **Adjacency Matrix** | $O(V^2)$ build | $O(V^2)$ | Constant-time $O(1)$ edge-lookup matrix |

*Note: $V$ is the number of routers (vertices) and $E$ is the number of transmission links (edges).*

---

## 4. Project Directory Structure

```
NetRoute/
├── main.py                     # Streamlit dashboard, Plotly network canvas, mode drawer, and 9 tabs
├── network.py                  # Router and Graph models, dynamic editing, weights, presets, and validation
├── algorithms.py               # Genuine BFS, DFS, and Dijkstra engines with granular step-by-step recording
├── simulation.py               # State management, history recording, failure lab, and challenges
├── theme.py                    # Curated high-contrast palette, CSS styling, and telemetry card renderers
├── requirements.txt            # Minimal dependencies (streamlit, plotly, pandas)
├── README.md                   # Comprehensive project documentation
└── tests/
    ├── test_network.py         # Graph operations, validation, matrix/list sync tests
    ├── test_algorithms.py      # BFS and DFS shortest path, queue/stack mechanics, edge cases
    ├── test_dijkstra.py        # Dijkstra min-cost, BFS vs Dijkstra diff, non-negative weight checks
    ├── test_failure_lab.py     # Router and link failure, recovery, and detour comparison
    ├── test_history_and_report.py # History recording, comparison, replay, and JSON/CSV export
    ├── test_challenge.py       # DSA challenge evaluation against actual algorithm results
    ├── test_comparison.py      # Dual Algorithm Arena BFS vs. DFS comparative tests
    ├── test_simulation.py      # Step navigation, packet hop progression, state reset
    └── test_router.py          # Router dataclass and coordinates
```

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
python3 -m unittest discover -s tests -p "test_*.py" -v
```

**Test Results:**
- 57 unit tests across 9 test suites passing in `0.017s`.
- 100% test pass rate with zero regressions.

---

## 6. How to Demonstrate Key Features

1. **Demonstrate BFS vs. Dijkstra Divergence:**
   - In the Mode Bar, select Preset: `Weighted Demo (BFS != Dijkstra)` and click **Load Preset**.
   - Select algorithm **BFS (Breadth First)** and click **Run Route Analysis**. Discovered route is `N1 -> N2 -> N4` (2 hops, cost 13).
   - Select algorithm **Dijkstra (Minimum-Cost)** and click **Run Route Analysis**. Discovered route is `N1 -> N2 -> N3 -> N4` (3 hops, cost 4).
   - Explain to the examiner that BFS optimizes hop count while Dijkstra optimizes cumulative link cost.

2. **Demonstrate Link-Weight Editing:**
   - In the Mode Bar, click **Edit Weight**.
   - Select link `N2 <-> N4`, change its cost from 12 to 1, and click **Apply New Weight**.
   - Observe that Dijkstra immediately switches to `N1 -> N2 -> N4` because its cost is now $1 + 1 = 2 < 4$.

3. **Demonstrate Network Failure & Recovery:**
   - Navigate to Tab 2: **Failure & Recovery Lab**.
   - Click **Set Current as Baseline**.
   - Select Router `N2` or Link `N1 <-> N2` and click **Sever Link / Cut Power**.
   - Observe the network visualization turn the link into a red dotted line labeled `CUT` and observe the dynamic detour route recalculation.
   - Click **Restore All Failures** to restore the network.

4. **Demonstrate Data Structure Mechanics (CO1):**
   - In Tab 1, switch between BFS, DFS, and Dijkstra.
   - For BFS, observe the FIFO Queue front/rear pointers and enqueue/dequeue operations.
   - For DFS, observe the LIFO Stack top/bottom pointers and backtracking.
   - For Dijkstra, observe the Min-Heap priority queue ordering and tentative distances table.

5. **Demonstrate History & Report Export:**
   - In Tab 3, view previous simulation runs and click **Replay Recorded Run**.
   - In Tab 5, inspect the experiment summary and click **Download Experiment Report (JSON)** or **(CSV)**.
