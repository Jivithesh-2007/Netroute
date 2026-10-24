# NetRoute – Interactive Data Structures & Network Routing Simulator

**Course:** Data Structures and Algorithms  
**Academic Level:** College Micro-Project (CO3, CO4, CO5)  
**Implementation:** Standalone Native Python 3 Desktop Application (Tkinter, ttk, Canvas)  
**Dependencies:** Zero external dependencies (Standard Library only)

---

## 1. Project Overview

**NetRoute** is an interactive educational desktop simulator designed to visualize and explore core Data Structures and Algorithms with a focus on computer networking and routing.

Built with a light theme (`#F4F7FC` background, `#FFFFFF` cards, `#2563EB` primary blue, `#0EA5E9` secondary cyan, `#16A34A` success green, `#EA580C` warning orange, and `#172033` high-contrast typography), NetRoute provides genuine algorithm execution, interactive topology editing, step-by-step queue/stack visualization, packet animation along discovered routes, and empirical performance benchmarking.

---

## 2. Core Academic Modules

### CO5 — Network Routing & Graph Algorithms
- **Interactive Topology Canvas:** Pan, zoom, fit-to-view, and drag-and-drop router positioning.
- **Device & Link Management:** Add/remove routers, add/remove connections, and toggle router online/offline power state.
- **Shortest-Hop Routing (BFS):** Genuine Breadth-First Search using a FIFO queue to discover optimal shortest-hop paths.
- **Path Discovery (DFS):** Depth-First Search using a LIFO stack to discover reachability through network branches.
- **Live Queue/Stack Inspection:** Shows the real-time internal state of the traversal data structure during exploration.
- **Packet Animation:** Visual packet movement along the exact route with Play, Pause, Step, and Speed controls.
- **Dual Representations (PrO-13 & PrO-14):** Live synchronized Adjacency List $O(V+E)$ and Adjacency Matrix $O(V^2)$ representations with connected components analysis.

### CO3 — Searching, Sorting & Hashing
- **Searching:** Linear Search, Iterative Binary Search, Recursive Binary Search, and Interpolation Search with real comparison counters.
- **Sorting Visualizer:** Bubble Sort, Insertion Sort, Selection Sort, and Merge Sort rendered as colorful animated bars on Canvas with comparison, swap, and write highlights.
- **Practical Scheduling (PrO-9):** Demonstration of using sorting algorithms to schedule network tasks by Priority, Deadline (Earliest Deadline First), or Duration (Shortest Job First).
- **Hashing (PrO-7):** Separate Chaining (linked lists per bucket) and Open Addressing via Linear Probing with tombstone markers for safe deletions, load-factor tracking ($\alpha$), and probe count analysis.

### CO4 — Tree Structures
- **Binary Search Tree (BST):** Insertion, search, and 3-case deletion (leaf, single child, two children with inorder successor replacement).
- **Self-Balancing AVL Tree (PrO-12):** Rotations (LL, RR, LR, RL) with height and balance factor ($BF = H_L - H_R$) tracking.
- **Binary Heap Priority Queue:** Min-Heap and Max-Heap with dual synchronized tree and 1D array views ($2i+1, 2i+2$).
- **B-Tree (Multi-Key):** Multi-key node insertion with proactive node splitting, searching, and deletion.
- **Tree Traversals (PrO-11):** Preorder, Inorder, Postorder, and Level-Order traversals.
- **BST vs AVL Evaluation:** Empirical demonstration showing how skewed inputs degrade BSTs to $O(N)$ while AVL maintains $O(\log N)$ bounds.

### Performance Dashboard & Academic Outcomes
- **Empirical Benchmarks:** Live runtime measurements and operation counters across user-configured dataset sizes.
- **Theoretical Complexity Reference:** Big-O references across best, average, and worst cases for time and space.
- **Course Mapping:** Explicit mapping to Course Outcomes (CO3, CO4, CO5) and Practicums (PrO-7 through PrO-15).

---

## 3. Project Architecture

The application is structured into native Python modules with zero external pip dependencies:

```
NetRoute/
├── main.py                 # Application launch entry point
├── app.py                  # Main window shell, navigation, header, and lifecycle management
├── network_ui.py           # Network simulator UI, canvas, topology editing, routing, packet animation
├── labs_ui.py              # Searching, Sorting, Hashing, Benchmarks, and Learning Outcomes UI
├── tree_ui.py              # Tree structures lab UI (BST, AVL, Heap, B-Tree)
├── algorithms.py           # Core DSA implementations (search, sort, hash, trees, benchmark logic)
├── network.py              # Graph model, router model, BFS/DFS routing, and topology validation
├── theme.py                # Color palette, TTK styling, UI widgets, and simulation service
├── data/
│   └── sample_network.json # Example 6-router network topology preset
├── requirements.txt        # Standard library dependencies declaration
└── README.md               # Project documentation and presentation guide
```

---

## 4. How to Run

Launch the application directly using standard Python 3:

```bash
python3 main.py
```
