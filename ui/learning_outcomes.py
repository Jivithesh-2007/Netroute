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
    """Learning Outcomes & Project Documentation View with structured tabs and styling."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_card = CardFrame(self, title="Course Outcome Mapping & Academic Documentation", subtitle="Course: Data Structures and Algorithms (25CS306)", padding=10)
        main_card.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        notebook = ttk.Notebook(main_card)
        notebook.pack(fill="both", expand=True, pady=(6, 0))

        # Tab 1: Course Outcomes (CO)
        tab_co = self._create_text_tab(notebook, self._get_co_text())
        notebook.add(tab_co, text="  Course Outcomes (CO3, CO4, CO5)  ")

        # Tab 2: Practicum Outcomes (PrO)
        tab_pro = self._create_text_tab(notebook, self._get_pro_text())
        notebook.add(tab_pro, text="  Practicum Outcomes (PrO-7 to PrO-15)  ")

        # Tab 3: Demonstration Guide
        tab_demo = self._create_text_tab(notebook, self._get_demo_text())
        notebook.add(tab_demo, text="  Lab Demonstration Guide  ")

        # Tab 4: Architecture & Verification
        tab_arch = self._create_text_tab(notebook, self._get_arch_text())
        notebook.add(tab_arch, text="  System Architecture & Offline Guarantee  ")

    def _create_text_tab(self, parent_notebook, content_str: str) -> ttk.Frame:
        tab_frame = ttk.Frame(parent_notebook, style="Card.TFrame", padding=10)

        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(
            tab_frame,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_BODY,
            relief="solid",
            bd=1,
            wrap="word",
            yscrollcommand=scrollbar.set,
            padx=16,
            pady=14
        )
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        text_widget.insert("1.0", content_str.strip())
        text_widget.config(state="disabled")
        return tab_frame

    def _get_co_text(self) -> str:
        return """
================================================================================
  1. COURSE OUTCOMES (CO) COVERAGE
================================================================================

• CO3: Evaluate the performance of searching and sorting algorithms for solving
       engineering problems.
       Implemented in: Module B (Searching & Sorting Lab) and Module B.3 (Hash Table Lab).
       Features:
       - Linear, Binary (iterative/recursive), and Interpolation Search.
       - Bubble, Insertion, Selection, and Merge Sort.
       - Hash Table with Separate Chaining and Open Addressing (Linear Probing).
       - Live comparison counters, swap tracking, and theoretical complexity matrices.

• CO4: Develop tree structures for solving engineering problems.
       Implemented in: Module C (Tree Structures Lab).
       Features:
       - Binary Tree Traversals (Inorder, Preorder, Postorder, Level-order).
       - Binary Search Tree (BST) with 3-case deletion.
       - Self-balancing AVL Tree with LL, RR, LR, RL rotations and balance factor display.
       - Binary Min/Max Heap with dual array & tree visualization.
       - B-Tree multi-key node splitting visualizer.

• CO5: Evaluate the applicability of graph data structures and traversal techniques
       for solving engineering problems.
       Implemented in: Module A (Network Routing Simulator).
       Features:
       - Interactive Canvas graph editor with drag-and-drop nodes and Fit-to-View coordinate transforms.
       - BFS shortest-path routing with FIFO Queue state visualizer.
       - DFS path exploration with LIFO Stack state visualizer.
       - Adjacency List O(V+E) & Adjacency Matrix O(V²) views synchronized in real time.
       - Packet transmission animation along route.
       - Router online/offline status toggling with dynamic rerouting.
       - 2D Grid-Maze pathfinding demonstration.
"""

    def _get_pro_text(self) -> str:
        return """
================================================================================
  2. PRACTICUM OUTCOMES (PrO) MAPPING
================================================================================

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
"""

    def _get_demo_text(self) -> str:
        return """
================================================================================
  3. LAB PRACTICUM DEMONSTRATION GUIDE
================================================================================

1) Module A (Network Routing):
   - Select Source (e.g. R1) and Destination (e.g. R6).
   - Click "▶ Run Route" to watch BFS enqueue nodes and discover the shortest hop path.
   - Watch the packet animate node-by-node along the reconstructed route.
   - Click "⚡ Toggle Offline" on a core router (e.g. R2) and rerun BFS to see dynamic rerouting.
   - Click "⚖ Compare BFS & DFS" to see side-by-side hop and step comparisons.
   - Use Zoom In, Zoom Out, or "⊡ Fit View" to automatically scale and center large topologies.

2) Module B (Searching & Sorting Lab):
   - Select "Sorting Algorithms" -> "Merge Sort".
   - Click "▶ Play" to observe bar chart comparisons and array merge writes.
   - Switch to "Searching Algorithms" -> "Interpolation Search" to see probe calculations.

3) Module B.3 (Hash Table Lab):
   - Enter keys into Separate Chaining and Linear Probing.
   - Observe collision counters, probe counts, tombstone markers ("DEL"), and load factor (α).

4) Module C (Tree Structures Lab):
   - Select "AVL Tree" and insert sequential numbers (10, 20, 30).
   - Observe automatic LL / RR rotations rebalancing the tree height and balance factors.
   - Switch to "Tree Traversals" and run "Inorder" to view sorted traversal sequence.
   - Select "Min-Heap" to inspect the linear array dual view synchronized with the binary tree.

5) Module D (Performance Dashboard):
   - Click "▶ Re-run Benchmarks" to execute real empirical algorithms on generated datasets.
   - View measured runtimes (ms) and comparison counts rendered on custom canvas charts.
   - Click "💾 Export Results..." to export benchmark tables to CSV.
"""

    def _get_arch_text(self) -> str:
        return """
================================================================================
  4. SYSTEM ARCHITECTURE & OFFLINE GUARANTEE
================================================================================

• 100% Native Desktop Implementation:
  - Built strictly in Python 3 using Tkinter, ttk, and Canvas.
  - Zero browser dependencies, zero HTML/CSS/React runtimes.
  - Complete offline functionality with no external APIs or network calls.

• Deterministic DSA Implementations:
  - No AI, machine learning, or simulated random delays.
  - All metrics, paths, and comparisons are direct outputs of real algorithms.

• Modular Separation of Concerns:
  - algorithms/ : Pure Python data structures and traversal algorithms.
  - models/     : Data models for Graph, Routers, Simulation steps and results.
  - services/   : Non-blocking step playback orchestrator and benchmarking engine.
  - ui/         : Modular view frames with ttk design tokens and Canvas renderers.
  - utils/      : Input validation and theoretical complexity definitions.
"""
