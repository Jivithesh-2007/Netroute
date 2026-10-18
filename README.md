# NetRoute – Interactive Data Structures & Network Routing Simulator

**Course:** Data Structures and Algorithms  
**Course Code:** 25CS306  
**Academic Level:** Final Micro-Project (CO3, CO4, CO5)  
**Implementation:** Standalone Native Python 3 Desktop Application (Tkinter, ttk, Tkinter Canvas)

---

## 1. Project Overview

**NetRoute** is an educational Python desktop application designed to visualize and explore core Data Structures and Algorithms with a focus on computer networking and routing.

Built with a clean, modern, professional white aesthetic (`#F5F7FB` application background, `#FFFFFF` cards and sidebar, `#2563EB` primary blue, `#172033` high-contrast typography, and `#15803D` success green), NetRoute provides real algorithm execution, interactive topology editing, step-by-step queue/stack animation, packet routing, and empirical performance benchmarking.

---

## 2. Key Objectives & Features

1. **CO5 Graph Routing & Connectivity:**
   - Interactive network topology canvas with pan, zoom, fit-to-view, and drag-and-drop node placement.
   - Dynamic router addition, router deletion, link creation, link removal, and online/offline status toggling.
   - Shortest-hop Breadth-First Search (BFS) routing with queue step visualization.
   - Depth-First Search (DFS) path discovery with call-stack step visualization.
   - Animated packet movement along actual discovered paths.
   - Live synchronized Adjacency List $O(V+E)$ and Adjacency Matrix $O(V^2)$ representations.
   - Reachability analysis, connected component identification, topology presets, and JSON import/export.
   - 2D grid-maze pathfinding demonstration for spatial graph traversals.

2. **CO3 Searching, Sorting & Hashing:**
   - **Searching:** Linear Search, iterative and recursive Binary Search, and Interpolation Search with element highlights and step logs.
   - **Sorting:** Bubble Sort, Insertion Sort, Selection Sort, and Merge Sort with color-coded comparison/swap state animations.
   - **Hashing:** Separate Chaining (linked lists per bucket) and Open Addressing via Linear Probing with tombstone marker support for safe deletions.
   - Dynamic insert, search, and delete operations with real collision and probe metrics.

3. **CO4 Tree Structures:**
   - **Binary Search Tree (BST):** Insertion, search, and 3-case deletion (leaf, single child, two children with inorder successor replacement).
   - **Self-Balancing AVL Tree:** Rotations (LL, RR, LR, RL) with height and balance factor tracking.
   - **Binary Heap:** Min-Heap and Max-Heap with array/tree representations and priority queue extract/peek operations.
   - **B-Tree:** Multi-key node insertion with proactive splitting and deletion.
   - Preorder, Inorder, Postorder, and Level-order tree traversals with visual visit highlights.

4. **Empirical Benchmarking & Learning Outcomes:**
   - Real runtime measurements and operation counters across user-configured dataset sizes.
   - Theoretical Big-O complexity references across best, average, and worst cases.
   - Interactive mapping to course outcomes (CO3, CO4, CO5) and laboratory practicums.

---

## 3. Course Outcomes & Practicum Mapping

### Course Outcomes (CO)
- **CO3:** Evaluate the performance of searching, sorting, and hashing algorithms for solving engineering problems.
- **CO4:** Develop and evaluate tree structures (BST, AVL, Heaps, B-Trees) for hierarchical data management.
- **CO5:** Evaluate graph data structures and traversal techniques (BFS, DFS) for network routing and connectivity.

### Practicum Outcomes (PrO)
| Practicum ID | Description | NetRoute Implementation Feature |
| :--- | :--- | :--- |
| **PrO-7** | Hash table with collision resolution | Separate Chaining & Linear Probing with tombstone markers |
| **PrO-8** | Search algorithm performance on large datasets | Linear, Binary, and Interpolation Search visualizer & benchmark |
| **PrO-9** | Sorting technique for a scheduling problem | Bubble, Insertion, Selection, and Merge Sort visualizer & comparison |
| **PrO-10** | Evaluate tree structures for data management | Structural comparisons between BST, AVL, Heap, and B-Tree |
| **PrO-11** | Store and retrieve hierarchical data using a tree | Tree Traversals (Pre/In/Post/Level) and BST lookups |
| **PrO-12** | Evaluate balanced trees for search and update | AVL Tree rotations guaranteeing $O(\log N)$ worst-case bounds |
| **PrO-13** | Adjacency Matrix and Adjacency List graph views | Live synchronized Adjacency List $O(V+E)$ and Matrix $O(V^2)$ tables |
| **PrO-14** | Choose a suitable graph representation | Space and neighbor lookup efficiency comparisons |
| **PrO-15** | Graph-based connectivity or routing applications | Network packet routing simulator and 2D grid-maze pathfinding |

---

## 4. Simplified Project Structure

The project has been refactored into a clean, flat architecture with zero external dependencies and student-level readable Python:

```
NetRoute/
├── main.py                 # Application launch entry point
├── app.py                  # Main window shell, navigation, page layout, and shared state
├── network_ui.py           # Network simulator UI, canvas, topology editing, routing, packet animation
├── labs_ui.py              # Searching, Sorting, Hashing, Benchmarks, and Learning Outcomes UI
├── tree_ui.py              # Tree structures lab UI (BST, AVL, Heap, B-Tree)
├── algorithms.py           # Searching, sorting, hashing, and tree algorithm implementations
├── network.py              # Graph model, router model, BFS/DFS routing, and topology validation
├── theme.py                # Cohesive white design system, TTK styling, and reusable UI components
├── requirements.txt        # Standard library dependencies (no external pip packages needed)
├── README.md               # User documentation and project guide
├── .gitignore              # Git ignore rules
├── data/
│   └── sample_network.json # Example 6-router network topology preset
└── tests/
    └── test_all.py         # Consolidated automated test suite covering all modules
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.10 or higher.
- Native `tkinter` support.

### macOS
Verify Python and Tkinter installation:
```bash
python3 -c "import tkinter; print(tkinter.TkVersion)"
```
If Tkinter is missing:
```bash
brew install python-tk
```

### Windows & Linux
- **Windows:** Standard Python installers from [python.org](https://www.python.org) include Tkinter automatically (ensure "tcl/tk and IDLE" is checked).
- **Linux (Ubuntu/Debian):** `sudo apt-get install python3-tk`

---

## 6. Running the Application

Launch the desktop GUI:

```bash
python3 main.py
```

On Windows:
```cmd
python main.py
```

---

## 7. Running Automated Tests

Run the full automated test suite:

```bash
python3 -m unittest discover -s tests -v
```

Or verify compilation:
```bash
python3 -m compileall -q .
```

---

## 8. Theoretical Complexity Reference

| Algorithm / Structure | Best Time | Average Time | Worst Time | Space |
| :--- | :--- | :--- | :--- | :--- |
| **BFS Routing** | $O(V + E)$ | $O(V + E)$ | $O(V + E)$ | $O(V)$ |
| **DFS Routing** | $O(V + E)$ | $O(V + E)$ | $O(V + E)$ | $O(V)$ |
| **Linear Search** | $O(1)$ | $O(N)$ | $O(N)$ | $O(1)$ |
| **Binary Search** | $O(1)$ | $O(\log N)$ | $O(\log N)$ | $O(1)$ |
| **Interpolation Search** | $O(1)$ | $O(\log \log N)$ | $O(N)$ | $O(1)$ |
| **Bubble Sort** | $O(N)$ | $O(N^2)$ | $O(N^2)$ | $O(1)$ |
| **Insertion Sort** | $O(N)$ | $O(N^2)$ | $O(N^2)$ | $O(1)$ |
| **Selection Sort** | $O(N^2)$ | $O(N^2)$ | $O(N^2)$ | $O(1)$ |
| **Merge Sort** | $O(N \log N)$ | $O(N \log N)$ | $O(N \log N)$ | $O(N)$ |
| **Separate Chaining** | $O(1)$ | $O(1 + \alpha)$ | $O(N)$ | $O(M + N)$ |
| **Linear Probing** | $O(1)$ | $O(1)$ | $O(N)$ | $O(M)$ |
| **BST** | $O(\log N)$ | $O(\log N)$ | $O(N)$ | $O(N)$ |
| **AVL Tree** | $O(\log N)$ | $O(\log N)$ | $O(\log N)$ | $O(N)$ |
| **Binary Heap** | $O(1)$ | $O(\log N)$ | $O(\log N)$ | $O(N)$ |
| **B-Tree** | $O(\log N)$ | $O(\log N)$ | $O(\log N)$ | $O(N)$ |
