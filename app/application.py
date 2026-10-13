"""
Main application window shell for NetRoute Python Desktop Simulator.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.theme import Theme
from app.navigation import SidebarNav

# Module Views (Will be imported dynamically)
from ui.network_simulator import NetworkSimulatorView
from ui.searching_sorting_lab import SearchingSortingLabView
from ui.hashing_lab import HashingLabView
from ui.tree_lab import TreeLabView
from ui.performance_dashboard import PerformanceDashboardView
from ui.learning_outcomes import LearningOutcomesView


class NetRouteApp(tk.Tk):
    """Primary application window class."""

    def __init__(self):
        super().__init__()

        self.title("NetRoute — Interactive DSA & Network Routing Simulator (25CS306)")
        self.geometry("1280x820")
        self.minsize(1024, 700)
        self.configure(bg=Theme.BG_DARK)

        # Apply professional light theme styles
        Theme.setup_styles(self)

        # Main Layout: Sidebar on Left, Content Area on Right
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar Navigation
        self.sidebar = SidebarNav(self, on_navigate=self.show_module)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Main Content Frame
        self.content_container = ttk.Frame(self, style="TFrame")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=14, pady=10)

        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Header Title Bar
        self.header_frame = ttk.Frame(self.content_container, style="TFrame")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.title_lbl = ttk.Label(self.header_frame, text="Network Routing Simulator", style="Header.TLabel")
        self.title_lbl.pack(side="left")

        self.badge_lbl = tk.Label(
            self.header_frame,
            text="CO5 GRAPH",
            font=Theme.FONT_SMALL_BOLD,
            bg=Theme.BG_SELECTED,
            fg=Theme.ACCENT_BLUE,
            padx=6,
            pady=2
        )
        self.badge_lbl.pack(side="left", padx=(10, 0))

        self.subtitle_lbl = ttk.Label(
            self.header_frame,
            text="CO5: Graph Routing, BFS & DFS Traversal, Packet Animation, Topology Editing",
            style="Subtitle.TLabel"
        )
        self.subtitle_lbl.pack(side="left", padx=(12, 0), pady=(3, 0))

        # Views Dictionary
        self.views = {}

        # Instantiate View Frames
        self.views["network"] = NetworkSimulatorView(self.content_container, app=self)
        self.views["search_sort"] = SearchingSortingLabView(self.content_container, app=self)
        self.views["hashing"] = HashingLabView(self.content_container, app=self)
        self.views["trees"] = TreeLabView(self.content_container, app=self)
        self.views["performance"] = PerformanceDashboardView(self.content_container, app=self)
        self.views["learning"] = LearningOutcomesView(self.content_container, app=self)

        for view in self.views.values():
            view.grid(row=1, column=0, sticky="nsew")

        # Status Bar at Bottom
        self.status_bar = tk.Frame(
            self.content_container,
            bg=Theme.BG_CARD_ALT,
            highlightbackground=Theme.BORDER_COLOR,
            highlightthickness=1,
            padx=10,
            pady=4
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        self.status_lbl = tk.Label(
            self.status_bar,
            text="System Ready. Offline mode active.",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_MUTED
        )
        self.status_lbl.pack(side="left")

        self.status_mode_lbl = tk.Label(
            self.status_bar,
            text="Engine: Deterministic Standard Python 3 • 100% Offline",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_DISABLED
        )
        self.status_mode_lbl.pack(side="right")

        # Active module key tracking
        self.active_module_key: Optional[str] = None

        # Default module view
        self.show_module("network")

    def show_module(self, module_key: str):
        """Switch active module view frame and manage view lifecycle."""
        if module_key not in self.views:
            return

        # Call on_hide on previous active view if available
        if self.active_module_key and self.active_module_key in self.views:
            prev_view = self.views[self.active_module_key]
            if hasattr(prev_view, "on_hide"):
                try:
                    prev_view.on_hide()
                except Exception:
                    pass

        self.active_module_key = module_key

        # Update Header titles and Badges
        headers = {
            "network": ("Network Routing Simulator", "CO5: Graph Routing, BFS & DFS Traversal, Packet Animation, Topology Editing", "CO5 GRAPH"),
            "search_sort": ("Searching & Sorting Lab", "CO3: Linear, Binary, Interpolation Search & Bubble, Insertion, Selection, Merge Sort", "CO3 SEARCH/SORT"),
            "hashing": ("Hash Table Lab", "CO3: Separate Chaining & Open Addressing with Linear Probing", "CO3 HASHING"),
            "trees": ("Tree Structures Lab", "CO4: Binary Tree Traversals, BST, AVL Tree Rotations, Min/Max Heap, B-Tree", "CO4 TREES"),
            "performance": ("Performance Dashboard", "Empirical Benchmarking & Theoretical Complexity Analysis", "BENCHMARKS"),
            "learning": ("Learning Outcomes & Documentation", "Course Outcome Mapping CO3, CO4, CO5 & Practicum Guide", "ACADEMIC DOCS")
        }

        title, subtitle, badge = headers.get(module_key, ("NetRoute", "", "DSA"))
        self.title_lbl.config(text=title)
        self.subtitle_lbl.config(text=subtitle)
        self.badge_lbl.config(text=badge)

        # Raise active view
        view = self.views[module_key]
        view.tkraise()

        # Call view lifecycle hook if available
        if hasattr(view, "on_show"):
            try:
                view.on_show()
            except Exception:
                pass

        self.set_status(f"Active Module: {title}")

    def set_status(self, text: str):
        """Set text on application status bar."""
        self.status_lbl.config(text=text)
