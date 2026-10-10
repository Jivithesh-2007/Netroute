"""
MODULE E — LEARNING OUTCOMES AND PROJECT INFORMATION
Comprehensive documentation detailing course outcome mapping (CO3, CO4, CO5),
practicum requirements (PrO-7 to PrO-15), problem statement, and demonstration guide.
"""
import tkinter as tk
from tkinter import ttk

from app.theme import Theme
from app.widgets import CardFrame


class LearningOutcomesView(ttk.Frame):
    """Learning Outcomes & Project Documentation View."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_card = CardFrame(self, padding=16)
        main_card.grid(row=0, column=0, sticky="nsew")

        text_frame = ttk.Frame(main_card, style="Card.TFrame")
        text_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.text = tk.Text(
            text_frame,
            bg="#FFFFFF",
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_BODY,
            relief="solid",
            bd=1,
            wrap="word",
            yscrollcommand=scrollbar.set,
            padx=16,
            pady=16
        )
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text.yview)

        self._populate_documentation()
        self.text.config(state="disabled")

    def _populate_documentation(self):
        doc = """
================================================================================
  NETROUTE — INTERACTIVE DSA AND NETWORK ROUTING SIMULATOR
  Academic Micro-Project for Course: Data Structures and Algorithms (25CS306)
================================================================================

1. COURSE OUTCOMES (CO) COVERAGE
--------------------------------------------------------------------------------
• CO3: Evaluate the performance of searching and sorting algorithms for solving
       engineering problems.
       Implemented in: Module B (Searching & Sorting Lab) and Module B.3 (Hash Table Lab).
       Features: Linear, Binary (iterative/recursive), and Interpolation Search;
       Bubble, Insertion, Selection, and Merge Sort; Hash Table with Separate Chaining
       and Open Addressing (Linear Probing).

• CO4: Develop tree structures for solving engineering problems.
       Implemented in: Module C (Tree Structures Lab).
       Features: Binary Tree Traversals (Inorder, Preorder, Postorder, Level-order);
       Binary Search Tree (BST) with 3-case deletion; Self-balancing AVL Tree with LL,
       RR, LR, RL rotations; Binary Min/Max Heap with dual array & tree visualization;
       B-Tree multi-key node splitting visualizer.

• CO5: Evaluate the applicability of graph data structures and traversal techniques
       for solving engineering problems.
       Implemented in: Module A (Network Routing Simulator).
       Features: Interactive Canvas graph editor with drag-and-drop nodes;
       BFS shortest-path routing with Queue state visualizer; DFS path exploration
       with Stack state visualizer; Adjacency List O(V+E) & Adjacency Matrix O(V²) views;
       Packet transmission animation along route; Router offline status toggling;
       Grid-Maze 2D pathfinding demonstration.


2. PRACTICUM OUTCOMES (PrO) MAPPING
--------------------------------------------------------------------------------
• PrO-7: Hash table with collision resolution.
  -> Demonstrated in Module B.3 via Separate Chaining & Linear Probing with tombstone markers.

• PrO-8: Search algorithm performance on large datasets.
  -> Demonstrated in Module B & D via Linear, Binary, and Interpolation Search benchmarking.

• PrO-9: Sorting technique for a scheduling problem.
  -> Demonstrated in Module B & D via empirical comparisons of Bubble, Insertion, Selection, and Merge Sort.

• PrO-10: Evaluate tree structures for data management.
  -> Demonstrated in Module C & D by contrasting BST, AVL, Heap, and B-Tree structures.

• PrO-11: Store and retrieve hierarchical data using a suitable tree.
  -> Demonstrated in Module C via Binary Tree Traversals and BST lookup/insertion.

• PrO-12: Evaluate balanced trees for search and update operations.
  -> Demonstrated in Module C & D via self-balancing AVL rotations guaranteeing O(log N).

• PrO-13: Adjacency Matrix and Adjacency List graph representations.
  -> Demonstrated in Module A with real-time synchronized Adjacency List and Matrix tables.

• PrO-14: Choose a suitable graph representation for specific engineering problems.
  -> Demonstrated in Module A & D by comparing space O(V+E) vs O(V²) and edge lookup efficiency.

• PrO-15: Graph-based connectivity or routing applications.
  -> Demonstrated in Module A via network packet routing simulations and grid-maze connectivity analysis.


3. SYSTEM ARCHITECTURE & ENGINEERING DESIGN
--------------------------------------------------------------------------------
• Built using 100% native Python 3 standard library and Tkinter / TTK GUI widgets.
• Completely self-contained and operates 100% offline without external web dependencies,
  browser wrappers, or AI inference APIs.
• Uses Tkinter's non-blocking event-driven scheduling (.after()) for animation playback.
• Algorithms are decoupled into pure Python modules in the algorithms/ package, making
  them independently unit-testable without launching the GUI.


4. DEMONSTRATION GUIDE
--------------------------------------------------------------------------------
1) Module A (Network Routing):
   - Select Source (e.g. R1) and Destination (e.g. R6).
   - Click "▶ Play" to watch BFS enqueue nodes and discover the shortest hop path.
   - Watch the pink packet animate node-by-node along the reconstructed route.
   - Click "Toggle Offline" on a core router (e.g. R2) and rerun BFS to see dynamic rerouting.

2) Module B (Searching & Sorting Lab):
   - Select "Sorting Algorithms" -> "Merge Sort".
   - Click "▶ Play" to observe bar chart comparisons and array merge writes.
   - Switch to "Searching Algorithms" -> "Interpolation Search" to see probe calculations.

3) Module B.3 (Hash Table Lab):
   - Enter keys into Separate Chaining and Linear Probing.
   - Observe collision counters, probe counts, tombstone markers ("DEL"), and load factor (α).

4) Module C (Tree Structures Lab):
   - Select "AVL Tree" and insert sequential numbers (10, 20, 30).
   - Observe automatic LL / RR rotations rebalancing the tree height.
   - Switch to "Tree Traversals" and run "Inorder" to view sorted traversal sequence.

5) Module D (Performance Dashboard):
   - Click "▶ Run Benchmarks" to execute real empirical algorithms on generated datasets.
   - View measured runtimes (ms) and comparison counts rendered on custom canvas charts.
"""
        self.text.insert("1.0", doc.strip())
