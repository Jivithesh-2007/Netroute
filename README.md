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

## 2. Computational Complexity Matrix

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
├── network.py                  # Router and Graph models, adjacency list/matrix, and generate_routing_table()
├── algorithms.py               # BFS, DFS, Dijkstra, linear_search, binary_search, bubble_sort, insertion_sort, build_traversal_tree
├── simulation.py               # Playback engine, packet stepper, history, and simulate_table_forwarding()
├── theme.py                    # Design system, high-contrast light theme CSS tokens, and card components
├── tests/                      # Automated unit test suite (81 tests)
│   ├── test_co3_searching_sorting.py   # Tests for linear/binary search & bubble/insertion sort
│   ├── test_co4_traversal_tree.py      # Tests for traversal tree invariants, root, and acyclic property
│   ├── test_co5_table_routing.py       # Tests for routing tables and table forwarding simulation
│   ├── test_bfs.py                     # BFS unweighted shortest path tests
│   ├── test_dfs.py                     # DFS path validity tests
│   ├── test_dijkstra.py                # Dijkstra weighted path tests
│   ├── test_network.py                 # Graph data structure & dynamic editing tests
│   ├── test_simulation.py              # Simulation state and invalidation tests
│   ├── test_failure_lab.py             # Network failure and recovery tests
│   ├── test_comparison.py              # Dual BFS vs DFS comparison tests
│   ├── test_challenge.py               # DSA challenge mode tests
│   └── test_history_and_report.py      # History recording & report export tests
└── README.md                   # Project documentation and faculty demonstration guide
```

---

## 4. Installation and Execution

### Step 1: Clone or Navigate to Directory
```bash
cd /Users/Jivithesh/Desktop/S3_MP/Netroute
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `streamlit`, `plotly`, `pandas`)*

### Step 3: Run Automated Test Suite
Verify that all 81 automated tests pass:
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
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
