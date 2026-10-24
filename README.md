# NetRoute – Educational DSA & Network Routing Simulator

**Course:** Data Structures & Algorithms  
**Academic Level:** College Micro-Project  
**Implementation:** Native Python 3 Desktop App (Tkinter)  
**Dependencies:** Zero external dependencies (Standard Library only)

---

## 1. Project Overview

**NetRoute** is a lightweight, educational desktop simulator demonstrating key Data Structures and Algorithms with simple computer networking applications:
1. **Network Routing:** Graph representation with Breadth-First Search (BFS shortest-hop routing) and Depth-First Search (DFS route discovery).
2. **Searching & Sorting:** Linear Search, Binary Search, Bubble Sort, Selection Sort, and Insertion Sort.
3. **Hashing:** Hash Table with Separate Chaining collision handling.
4. **Trees:** Binary Search Tree (BST) insertion, search, and Inorder/Preorder/Postorder traversals.

---

## 2. Modular Architecture (Exactly 8 Modules, Max 100 Lines Each)

The entire project is structured into **8 clean, readable modules**, each written using standard beginner-friendly Python syntax and strictly under 100 lines:

| Module | Purpose | Lines of Code | Key Functions / Classes |
| :--- | :--- | :---: | :--- |
| **`main.py`** | Application Entry Point | ~15 | `main()` |
| **`theme.py`** | Color Palette & Font Styles | ~23 | `BG_MAIN`, `PRIMARY`, `FONT_NORMAL` |
| **`network.py`** | Graph Model & Routing Algorithms | ~72 | `Graph`, `bfs()`, `dfs()`, `load_sample()` |
| **`algorithms.py`** | Searching, Sorting & Hashing Logic | ~91 | `linear_search()`, `binary_search()`, `bubble_sort()`, `HashTable` |
| **`network_ui.py`** | Network Visualizer & Routing Canvas | ~94 | `NetworkView` (Node & Link drawing, path highlight) |
| **`labs_ui.py`** | UI for Search, Sort & Hash Table | ~83 | `LabsFrame` (Array sorting, target search, bucket list) |
| **`tree_ui.py`** | BST Visualizer & Tree Logic | ~96 | `BSTNode`, `BST`, `TreeFrame` (Recursive canvas drawing) |
| **`app.py`** | Main Application Window & Sidebar | ~74 | `NetRouteApp` (Sidebar navigation & view switcher) |

---

## 3. How to Run

Run the application directly using standard Python 3:

```bash
python3 main.py
```

---

## 4. Viva / Explanation Cheat Sheet for College Presentation

### Graph & Routing (`network.py`)
- **BFS (Breadth-First Search):** Uses a **FIFO Queue** (`pop(0)`). Discovers level-by-level to guarantee the **shortest hop path** in an unweighted network. Time Complexity: $O(V + E)$.
- **DFS (Depth-First Search):** Uses a **LIFO Stack** (`pop()`). Explores deep into network branches first. Time Complexity: $O(V + E)$.

### Searching & Sorting (`algorithms.py`)
- **Linear Search:** Checks each element sequentially. $O(N)$ worst case.
- **Binary Search:** Divides the sorted array in half each time. $O(\log N)$ worst case.
- **Bubble Sort:** Swaps adjacent elements if out of order. $O(N^2)$ worst case.
- **Selection Sort:** Finds minimum element and moves it to the front. $O(N^2)$ worst case.
- **Insertion Sort:** Inserts each element into the correct sorted position. $O(N^2)$ worst case.
- **Hash Table (Chaining):** Maps `key % size` to a bucket. Uses linked lists/arrays per bucket to handle collisions cleanly. Average lookup: $O(1)$.

### Binary Search Tree (`tree_ui.py`)
- **BST Property:** For every node, left child values are smaller and right child values are greater.
- **Inorder Traversal:** Left $\to$ Root $\to$ Right (always prints values in sorted ascending order).
- **Preorder Traversal:** Root $\to$ Left $\to$ Right.
- **Postorder Traversal:** Left $\to$ Right $\to$ Root.
