import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from theme import Theme
from network_ui import NetworkSimulatorView
from labs_ui import SearchingSortingLabView, HashingLabView, PerformanceDashboardView, LearningOutcomesView
from tree_ui import TreeLabView


class SidebarNav(ttk.Frame):
    MODULES = [
        ("network", "🌐 Network Simulator", "CO5 Graph Routing"),
        ("search_sort", "📊 Searching & Sorting", "CO3 Search & Sort"),
        ("hashing", "⚡ Hash Table Lab", "CO3 Hashing & Probing"),
        ("trees", "🌲 Tree Structures Lab", "CO4 BST, AVL, Heap, B-Tree"),
        ("performance", "📈 Performance Dashboard", "Empirical Benchmarking"),
        ("learning", "📘 Learning Outcomes", "Course Mapping & Docs")
    ]

    def __init__(self, parent, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(parent, style="Sidebar.TFrame", width=230, **kwargs)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.active_tab = "network"
        self.buttons = {}

        right_border = tk.Frame(self, bg=Theme.BORDER_COLOR, width=1)
        right_border.pack(side="right", fill="y")

        brand_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=(16, 20, 16, 14))
        brand_frame.pack(fill="x")

        title_lbl = tk.Label(
            brand_frame,
            text="NetRoute",
            font=(Theme.FONT_FAMILY, 20, "bold"),
            bg=Theme.BG_SIDEBAR,
            fg=Theme.ACCENT_BLUE,
            anchor="w"
        )
        title_lbl.pack(fill="x")

        subtitle_lbl = tk.Label(
            brand_frame,
            text="Interactive DSA & Network Routing Simulator",
            font=Theme.FONT_SMALL_BOLD,
            bg=Theme.BG_SIDEBAR,
            fg=Theme.TEXT_MUTED,
            anchor="w",
            wraplength=190,
            justify="left"
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

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16, pady=6)

        nav_container = ttk.Frame(self, style="Sidebar.TFrame")
        nav_container.pack(fill="both", expand=True, pady=6)

        for mod_key, label, desc in self.MODULES:
            btn = ttk.Button(
                nav_container,
                text=label,
                style="Nav.TButton",
                command=lambda k=mod_key: self._select_tab(k)
            )
            btn.pack(fill="x", pady=2, padx=8)
            self.buttons[mod_key] = btn

        footer_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=(16, 12))
        footer_frame.pack(side="bottom", fill="x")

        ttk.Separator(footer_frame, orient="horizontal").pack(fill="x", pady=(0, 8))

        status_box = tk.Frame(footer_frame, bg=Theme.BG_CARD_ALT, padx=8, pady=6, highlightbackground=Theme.BORDER_COLOR, highlightthickness=1)
        status_box.pack(fill="x")

        dot_label = tk.Label(
            status_box,
            text="●",
            font=(Theme.FONT_FAMILY, 8),
            bg=Theme.BG_CARD_ALT,
            fg=Theme.COLOR_SUCCESS
        )
        dot_label.pack(side="left", padx=(0, 4))

        status_text = tk.Label(
            status_box,
            text="Offline Engine • v2.5",
            font=Theme.FONT_SMALL_BOLD,
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_MUTED
        )
        status_text.pack(side="left")

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
        self.geometry("1280x820")
        self.minsize(1024, 700)
        self.configure(bg=Theme.BG_DARK)

        Theme.setup_styles(self)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = SidebarNav(self, on_navigate=self.show_module)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_container = ttk.Frame(self, style="TFrame")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=14, pady=10)

        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

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

        self.views = {}
        self.views["network"] = NetworkSimulatorView(self.content_container, app=self)
        self.views["search_sort"] = SearchingSortingLabView(self.content_container, app=self)
        self.views["hashing"] = HashingLabView(self.content_container, app=self)
        self.views["trees"] = TreeLabView(self.content_container, app=self)
        self.views["performance"] = PerformanceDashboardView(self.content_container, app=self)
        self.views["learning"] = LearningOutcomesView(self.content_container, app=self)

        for view in self.views.values():
            view.grid(row=1, column=0, sticky="nsew")

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

        self.active_module_key: Optional[str] = None
        self.show_module("network")

    def show_module(self, module_key: str):
        if module_key not in self.views:
            return

        if self.active_module_key and self.active_module_key in self.views:
            prev_view = self.views[self.active_module_key]
            if hasattr(prev_view, "on_hide"):
                try:
                    prev_view.on_hide()
                except Exception:
                    pass

        self.active_module_key = module_key

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

    def show_view(self, view_key: str):
        self.show_module(view_key)
