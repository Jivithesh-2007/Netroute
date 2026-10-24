import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from theme import Theme
from network_ui import NetworkSimulatorView
from labs_ui import SearchingSortingLabView, HashingLabView, PerformanceDashboardView, LearningOutcomesView
from tree_ui import TreeLabView

class SidebarNav(ttk.Frame):
    MODULES = [
        ("network", "🌐  Network Simulator", "CO5 Graph Routing"),
        ("search_sort", "📊  Searching & Sorting", "CO3 Search & Sort"),
        ("hashing", "⚡  Hash Table Lab", "CO3 Hashing & Probing"),
        ("trees", "🌲  Tree Structures", "CO4 BST, AVL, Heap, B-Tree"),
        ("performance", "📈  Performance Dashboard", "Empirical Benchmarking"),
        ("learning", "📘  Learning Outcomes", "Course Mapping & Docs")
    ]

    def __init__(self, parent, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(parent, style="Sidebar.TFrame", width=225, **kwargs)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.active_tab = "network"
        self.buttons = {}

        right_border = tk.Frame(self, bg=Theme.BORDER, width=1)
        right_border.pack(side="right", fill="y")

        brand_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=(16, 18, 16, 12))
        brand_frame.pack(fill="x")

        title_lbl = tk.Label(
            brand_frame,
            text="NetRoute",
            font=(Theme.FONT_FAMILY, 18, "bold"),
            bg=Theme.BG_SIDEBAR,
            fg=Theme.PRIMARY,
            anchor="w"
        )
        title_lbl.pack(fill="x")

        subtitle_lbl = tk.Label(
            brand_frame,
            text="DSA & Network Simulator",
            font=Theme.FONT_SMALL_BOLD,
            bg=Theme.BG_SIDEBAR,
            fg=Theme.TEXT_MUTED,
            anchor="w"
        )
        subtitle_lbl.pack(fill="x", pady=(2, 0))

        course_lbl = tk.Label(
            brand_frame,
            text="Course: 25CS306",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_SIDEBAR,
            fg=Theme.TEXT_DISABLED,
            anchor="w"
        )
        course_lbl.pack(fill="x", pady=(1, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=14, pady=6)

        nav_container = ttk.Frame(self, style="Sidebar.TFrame")
        nav_container.pack(fill="both", expand=True, pady=4)

        for mod_key, label, desc in self.MODULES:
            btn = ttk.Button(
                nav_container,
                text=label,
                style="Nav.TButton",
                command=lambda k=mod_key: self._select_tab(k)
            )
            btn.pack(fill="x", pady=2, padx=8)
            self.buttons[mod_key] = btn

        footer = ttk.Frame(self, style="Sidebar.TFrame", padding=(14, 12))
        footer.pack(side="bottom", fill="x")

        ttk.Separator(footer, orient="horizontal").pack(fill="x", pady=(0, 6))
        status_box = tk.Frame(footer, bg=Theme.BG_PANEL, padx=8, pady=4, highlightbackground=Theme.BORDER, highlightthickness=1)
        status_box.pack(fill="x")

        dot = tk.Label(status_box, text="●", font=(Theme.FONT_FAMILY, 8), bg=Theme.BG_PANEL, fg=Theme.SUCCESS)
        dot.pack(side="left", padx=(0, 4))
        st_text = tk.Label(status_box, text="Offline Engine • v2.5", font=Theme.FONT_SMALL_BOLD, bg=Theme.BG_PANEL, fg=Theme.TEXT_MUTED)
        st_text.pack(side="left")

        self._highlight_active()

    def _select_tab(self, key: str):
        self.active_tab = key
        self._highlight_active()
        self.on_navigate(key)

    def _highlight_active(self):
        for key, btn in self.buttons.items():
            if key == self.active_tab:
                btn.state(["selected"])
            else:
                btn.state(["!selected"])

class NetRouteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NetRoute — Interactive DSA & Network Routing Simulator")
        self.geometry("1260x800")
        self.minsize(1020, 680)
        self.configure(bg=Theme.BG_APP)

        Theme.setup_styles(self)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = SidebarNav(self, on_navigate=self.show_module)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_container = ttk.Frame(self, style="TFrame")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=12, pady=10)
        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        self.header_frame = ttk.Frame(self.content_container, style="TFrame")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self.title_lbl = ttk.Label(self.header_frame, text="Network Routing Simulator", style="Header.TLabel")
        self.title_lbl.pack(side="left")

        self.badge_lbl = tk.Label(
            self.header_frame,
            text="CO5 GRAPH",
            font=Theme.FONT_SMALL_BOLD,
            bg=Theme.BG_SELECTED,
            fg=Theme.PRIMARY,
            padx=8,
            pady=2
        )
        self.badge_lbl.pack(side="left", padx=(10, 0))

        self.subtitle_lbl = ttk.Label(
            self.header_frame,
            text="CO5: Graph Routing, BFS & DFS Traversal, Packet Animation, Topology Editing",
            style="Subtitle.TLabel"
        )
        self.subtitle_lbl.pack(side="left", padx=(10, 0), pady=(2, 0))

        self.views = {
            "network": NetworkSimulatorView(self.content_container, app=self),
            "search_sort": SearchingSortingLabView(self.content_container, app=self),
            "hashing": HashingLabView(self.content_container, app=self),
            "trees": TreeLabView(self.content_container, app=self),
            "performance": PerformanceDashboardView(self.content_container, app=self),
            "learning": LearningOutcomesView(self.content_container, app=self)
        }

        for view in self.views.values():
            view.grid(row=1, column=0, sticky="nsew")

        self.status_bar = tk.Frame(
            self.content_container,
            bg=Theme.BG_PANEL,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=10,
            pady=4
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        self.status_lbl = tk.Label(
            self.status_bar,
            text="System Ready. Deterministic Python 3 Execution Engine.",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_PANEL,
            fg=Theme.TEXT_MUTED
        )
        self.status_lbl.pack(side="left")

        self.status_mode_lbl = tk.Label(
            self.status_bar,
            text="Standard Library • 100% Native Tkinter & Canvas",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_PANEL,
            fg=Theme.TEXT_DISABLED
        )
        self.status_mode_lbl.pack(side="right")

        self.active_module_key: Optional[str] = None
        self.show_module("network")

    def show_module(self, module_key: str):
        if module_key not in self.views:
            return

        if self.active_module_key and self.active_module_key in self.views:
            prev = self.views[self.active_module_key]
            if hasattr(prev, "on_hide"):
                try:
                    prev.on_hide()
                except Exception:
                    pass

        self.active_module_key = module_key

        headers = {
            "network": ("Network Routing Simulator", "CO5: Graph Routing, BFS & DFS Traversal, Packet Animation, Topology Editing", "CO5 GRAPH", Theme.PRIMARY),
            "search_sort": ("Searching & Sorting Lab", "CO3: Linear, Binary, Interpolation Search & Sorting Visualizer with Task Scheduling (PrO-9)", "CO3 SEARCH/SORT", Theme.PURPLE),
            "hashing": ("Hash Table Lab", "CO3: Separate Chaining & Linear Probing with Collision & Tombstone Probes", "CO3 HASHING", Theme.TEAL),
            "trees": ("Tree Structures Lab", "CO4: BST, Self-Balancing AVL Rotations, Min/Max Heap Priority Queue & B-Tree", "CO4 TREES", Theme.SUCCESS),
            "performance": ("Performance Dashboard", "Empirical Benchmarking Across Operation Counts & Theoretical Complexities", "BENCHMARKS", Theme.WARNING),
            "learning": ("Learning Outcomes & Documentation", "Course Outcome Mapping CO3, CO4, CO5 & Laboratory Practicum Guide", "ACADEMIC DOCS", Theme.SECONDARY)
        }

        title, subtitle, badge, color = headers.get(module_key, ("NetRoute", "", "DSA", Theme.PRIMARY))
        self.title_lbl.config(text=title)
        self.subtitle_lbl.config(text=subtitle)
        self.badge_lbl.config(text=badge, fg=color)

        view = self.views[module_key]
        view.tkraise()

        if hasattr(view, "on_show"):
            try:
                view.on_show()
            except Exception:
                pass

        self.set_status(f"Active Module: {title}")

    def set_status(self, text: str):
        self.status_lbl.config(text=text)
