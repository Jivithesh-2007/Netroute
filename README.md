# NetRoute – Interactive Data Structures & Network Routing Simulator

**Course:** Data Structures and Algorithms  
**Course Code:** 25CS306  
**Academic Level:** Micro-Project (CO3, CO4, CO5)  
**Implementation:** Standalone Native Python 3 Desktop Application (Tkinter, ttk, Tkinter Canvas)

---

## 1. Project Overview

**NetRoute** is a comprehensive offline Python desktop application for visualizing data structures and algorithm simulations with a focus on computer networking and routing applications. 

It replaces obsolete web-based implementations with a modular, responsive desktop GUI featuring professional dark navy graphics, step-by-step data structure animations, real algorithm execution, interactive topology editing, and empirical performance benchmarking.

---

## 2. Problem Statement

Network packet routing and algorithm design are foundational concepts in computer science. Traditional static descriptions often fail to provide students with intuitive mental models of how queue data structures manage Breadth-First Search (BFS) shortest paths, how stack memory handles Depth-First Search (DFS) exploration, how self-balancing trees (AVL) maintain height balance under dynamic updates, and how collision resolution strategies behave in hash tables.

NetRoute bridges this gap by providing an interactive GUI simulator that combines theoretical rigor with empirical execution visualizers.

---

## 3. Key Objectives

1. **CO5 Graph Routing & Connectivity:** Provide an interactive network topology editor to run genuine BFS and DFS traversals, visualize queue/stack operations, animate packet transmission, and switch between Adjacency List $O(V+E)$ and Adjacency Matrix $O(V^2)$ graph representations.
2. **CO3 Searching, Sorting & Hashing:** Implement Linear, Binary (iterative/recursive), and Interpolation Search; Bubble, Insertion, Selection, and Merge Sort; and Hash Tables using Separate Chaining and Open Addressing with Linear Probing (including tombstone markers).
3. **CO4 Tree Structures:** Develop interactive tree renderers for Binary Search Trees (BST with 3-case deletion), self-balancing AVL Trees (with LL/RR/LR/RL rotations), Min/Max Binary Heaps with priority queue dual view, and B-Trees with multi-key node splitting.
4. **Empirical Benchmarking:** Measure real Python execution runtimes and operation counts across varying dataset sizes without reliance on fabricated numbers.

---

## 4. Course Outcomes & Practicum Mapping

### Course Outcomes (CO) Coverage
- **CO3:** Evaluate the performance of searching and sorting algorithms for solving engineering problems.
- **CO4:** Develop tree structures for solving engineering problems.
- **CO5:** Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems.

### Practicum Outcomes (PrO) Mapping
| Practicum ID | Description | NetRoute Implementation Feature |
| :--- | :--- | :--- |
| **PrO-7** | Hash table with collision resolution | Module B.3 Separate Chaining & Linear Probing with tombstone markers |
| **PrO-8** | Search algorithm performance on large datasets | Module B & D Linear, Binary, and Interpolation Search visualizer & benchmark |
| **PrO-9** | Sorting technique for a scheduling problem | Module B & D Bubble, Insertion, Selection, and Merge Sort visualizer & comparison |
| **PrO-10** | Evaluate tree structures for data management | Module C & D Structural comparisons between BST, AVL, Heap, and B-Tree |
| **PrO-11** | Store and retrieve hierarchical data using a tree | Module C Binary Tree Traversals (Pre/In/Post/Level) and BST lookups |
| **PrO-12** | Evaluate balanced trees for search and update | Module C & D AVL Tree rotations guaranteeing $O(\log N)$ worst-case bounds |
| **PrO-13** | Adjacency Matrix and Adjacency List graph views | Module A Live synchronized Adjacency List $O(V+E)$ and Matrix $O(V^2)$ tables |
| **PrO-14** | Choose a suitable graph representation | Module A & D Analytical comparison of space and neighbor lookup efficiency |
| **PrO-15** | Graph-based connectivity or routing applications | Module A Network packet routing simulator and 2D grid-maze pathfinding |

---

## 5. Technology Stack

- **Language:** Python 3 (Tested on Python 3.10+)
- **GUI Engine:** Standard Python `tkinter`, `tkinter.ttk`, and `tkinter.Canvas`
- **Architecture:** Object-Oriented MVC (Models, Views, Services, Algorithms)
- **External Dependencies:** None (100% standard library)
- **Testing:** Python `unittest` framework

---

## 6. Project Structure

```
NetRoute/
├── main.py                     # Main application entry point
├── requirements.txt            # Package dependencies (pure standard library)
├── README.md                   # Comprehensive documentation
├── .gitignore                  # Git ignore rules
├── assets/                     # Icons and graphics
├── app/                        # Application shell & theme system
│   ├── __init__.py
│   ├── application.py          # NetRouteApp main window shell
│   ├── theme.py                # Dark Navy design system & TTK styling
│   ├── navigation.py           # Sidebar navigation panel
│   └── widgets.py              # Reusable cards, stat boxes, control bar, console
├── algorithms/                 # Core algorithm implementations (Independent of GUI)
│   ├── __init__.py
│   ├── graph_algorithms.py     # BFS, DFS, Connected Components, Grid Maze
│   ├── searching.py            # Linear, Binary, Interpolation Search
│   ├── sorting.py              # Bubble, Insertion, Selection, Merge Sort
│   ├── hashing.py              # Separate Chaining & Linear Probing Hash Tables
│   ├── binary_search_tree.py   # BST with 3-case deletion
│   ├── avl_tree.py             # AVL Tree with LL/RR/LR/RL rotations
│   ├── heap.py                 # Min-Heap and Max-Heap priority queues
│   ├── b_tree.py               # B-Tree multi-key node splitting
│   └── tree_traversals.py      # Preorder, Inorder, Postorder, Level-order
├── models/                     # Data models
│   ├── __init__.py
│   ├── router.py               # Router node model
│   ├── graph.py                # Graph data structure model
│   └── simulation.py           # Simulation step & result models
├── ui/                         # Desktop GUI Module Views
│   ├── __init__.py
│   ├── network_simulator.py    # Module A: Network Routing Simulator
│   ├── searching_sorting_lab.py# Module B: Searching & Sorting Lab
│   ├── hashing_lab.py          # Module B.3: Hash Table Lab
│   ├── tree_lab.py             # Module C: Tree Structures Lab
│   ├── performance_dashboard.py# Module D: Performance Comparison Dashboard
│   ├── learning_outcomes.py    # Module E: Course Mapping & Guide
│   └── dialogs.py              # Modal dialogs for inputs
├── services/                   # Application services
│   ├── __init__.py
│   ├── simulation_service.py   # Non-blocking playback controller (.after scheduling)
│   ├── benchmark_service.py    # Empirical algorithm benchmark runner
│   └── history_service.py      # Local JSON log persistence
├── utils/                      # Helper utilities
│   ├── __init__.py
│   ├── validation.py           # Input validation helpers
│   └── complexity.py           # Theoretical complexity metadata
├── data/                       # Sample data & presets
│   └── sample_network.json     # Default network topology JSON
└── tests/                      # Automated unit test suite
    ├── test_graph_algorithms.py
    ├── test_searching.py
    ├── test_sorting.py
    ├── test_hashing.py
    ├── test_bst.py
    ├── test_avl.py
    ├── test_heap.py
    └── test_b_tree.py
```

---

## 7. Installation & Setup Guide

### macOS
1. Open Terminal.
2. Verify Python 3 and Tkinter:
   ```bash
   python3 -c "import tkinter; print(tkinter.TkVersion)"
   ```
3. If Tkinter is missing:
   ```bash
   brew install python-tk
   ```

### Windows
1. Download Python 3.10+ from python.org.
2. Ensure **"tcl/tk and IDLE"** checkbox is checked during installation.

---

## 8. Running the Application

Launch the desktop application using python3:

```bash
python3 main.py
```

---

## 9. Running Automated Tests

Run the complete test suite to verify algorithm implementations:

```bash
python3 -m unittest discover -s tests
```

---

## 10. Time & Space Complexity Reference Table

| Algorithm / Structure | Best Case Time | Average Case Time | Worst Case Time | Space Complexity |
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

---

## 11. Known Limitations

- Graphics rendering relies on native Tkinter Canvas primitives.
- Large datasets ($N > 500$) in visualizers are scaled down to ensure UI responsiveness.

---

## 12. Future Enhancements

- Exporting custom topology network diagrams as SVG/PNG images.
- Dijkstra's Algorithm with link edge cost weights.
