# NetRoute — Interactive Network Packet-Routing Simulator

An interactive, educational network packet-routing desktop simulator developed with Python, Tkinter, dynamic graph data structures, and Breadth-First Search (BFS) / Depth-First Search (DFS) traversals.

NetRoute maps network routing to foundational computer science concepts, aligning directly with **CO1**, **CO2**, and **CO5** of the Data Structures and Algorithms (DSA) course curriculum.

---

## 1. Academic Course Outcome Mapping

### CO1 — Develop efficient solutions using stack and/or queue data structures
- **Queue-Based BFS:** Implements genuine Breadth-First Search using a First-In-First-Out (FIFO) queue (`collections.deque`). Demonstrates level-by-level exploration to discover the unweighted shortest-hop path between source and destination routers.
- **Stack-Based DFS:** Implements genuine Depth-First Search using an explicit Last-In-First-Out (LIFO) stack (`list`). Demonstrates deep branch exploration and explicit backtracking, showing that DFS discovers valid routes without guaranteeing the shortest path.
- **Live Queue/Stack Inspector:** Displays live internal data structure states at each execution step, including insertion, removal, and index indicators (Queue Head/Tail, Stack Top).

### CO2 — Use dynamic data structures for efficient storage and retrieval
- **Dynamic Adjacency List $O(V + E)$:** Serves as the primary dynamic graph representation. Routers (vertices) and transmission lines (edges) are inserted, retrieved, and deleted in real time.
- **Storage Efficiency:** Avoids the fixed-size quadratic memory footprint of static matrices during active topology editing.
- **Synchronized Visual Model:** Every visual node and connection on the canvas maps directly to the underlying dynamic graph model.

### CO5 — Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems
- **Real-World Engineering Modeling:** Models computer networks as graphs where vertices represent routers and edges represent network links.
- **Dual Synchronized Representations:** Maintains real-time synchronization between the Adjacency List $O(V + E)$ and the Adjacency Matrix $O(V^2)$.
- **Network Reachability & Diagnostics:** Analyzes connected components, destination reachability from the active source, and simulated hardware failures (online/offline toggle).
- **Real Packet Movement:** Animates packets along the actual discovered route hop-by-hop with playback controls (Play, Pause, Step, Reset, Speed).

### Practicum Alignments
- **PrO-13:** Represent graphs using adjacency lists and adjacency matrices.
- **PrO-14:** Select a suitable graph representation for the problem ($O(V+E)$ list for sparse dynamic topologies vs. $O(V^2)$ matrix for constant-time edge queries).
- **PrO-15:** Use graph structures to solve network connectivity, reachability, and packet routing problems.

---

## 2. Features

- **Interactive Topology Canvas:**
  - Drag routers freely with live coordinate updates.
  - Pan (middle/right-click drag) and Zoom (+/- buttons, mouse wheel, 1:1 Reset, Fit-to-View).
  - Context menu on right-click to set Source, Destination, Toggle Power, or Delete.
- **Dynamic Topology Editing:**
  - Add router with ID/name validation and duplicate prevention.
  - Delete selected router and cascade removal of associated edges.
  - Connect routers with endpoint validation and duplicate link prevention.
  - Remove existing connection.
  - Toggle router online/offline power state.
  - Save and load topologies via JSON files.
- **Built-in Demonstration Topologies:**
  1. *Default Sample Mesh:* Standard 6-router interconnected network.
  2. *Direct Route:* Linear chain demonstrating baseline traversal.
  3. *Multiple Possible Routes:* Diamond mesh highlighting the hop-count difference between BFS (shortest) and DFS (deep discovery).
  4. *Cyclic Network:* Interconnected loops demonstrating visited-set cycle prevention.
  5. *Disconnected Network:* Segmented subnets demonstrating destination unreachability and component analysis.
  6. *Network with Offline Router:* Simulates equipment failure on a transit bridge.
- **Playback & Animation Controls:**
  - Play, Pause, Step-forward, Reset, and adjustable Speed slider.
  - Real packet transmission traveling along the discovered path.
- **Inspectors & Statistics:**
  - Queue / Stack live inspector.
  - Scrollable Adjacency List & Matrix with complexity documentation.
  - Detailed Execution Trace Log with color-coded entries.
  - Compact network statistics: Total $V$, Total $E$, Reachable Routers, Explored Edges, Visited Routers, Path Hops, and Connected Components.

---

## 3. Architecture & File Structure

NetRoute uses standard Python 3 with zero external dependencies:

```
Netroute/
├── main.py                 # Application launcher
├── app.py                  # Main window shell, academic header, status bar
├── network_ui.py           # Network canvas, editing dialogs, playback, inspectors
├── algorithms.py           # Genuine BFS and DFS routing implementations
├── network.py              # Graph, Router models, presets, adjacency builders
├── theme.py                # Color palette, TTK styles, reusable UI widgets
├── data/
│   └── sample_network.json # Example 6-router topology JSON
├── requirements.txt        # Standard library declaration
└── README.md               # Project documentation
```

---

## 4. How to Run

Ensure Python 3 is installed, then launch `main.py` directly:

```bash
python3 main.py
```
