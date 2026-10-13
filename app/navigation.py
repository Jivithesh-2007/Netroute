"""
Sidebar navigation panel for switching between application modules.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable
from app.theme import Theme


class SidebarNav(ttk.Frame):
    """Sidebar navigation panel with white theme styling."""

    MODULES = [
        ("network", "Network Simulator", "CO5 Graph Routing"),
        ("search_sort", "Searching & Sorting", "CO3 Search & Sort"),
        ("hashing", "Hash Table Lab", "CO3 Hashing & Probing"),
        ("trees", "Tree Structures Lab", "CO4 BST, AVL, Heap, B-Tree"),
        ("performance", "Performance Dashboard", "Empirical Benchmarking"),
        ("learning", "Learning Outcomes", "Course Mapping & Docs")
    ]

    def __init__(self, parent, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(parent, style="Sidebar.TFrame", width=230, **kwargs)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.active_tab = "network"
        self.buttons = {}

        # Right border line separating sidebar from main content
        right_border = tk.Frame(self, bg=Theme.BORDER_COLOR, width=1)
        right_border.pack(side="right", fill="y")

        # Brand / Title Banner
        brand_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=(16, 20, 16, 16))
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
            text="DSA Simulator • 25CS306",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_SIDEBAR,
            fg=Theme.TEXT_MUTED,
            anchor="w"
        )
        subtitle_lbl.pack(fill="x", pady=(2, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16, pady=8)

        # Module Navigation Buttons
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

        # Footer Version Tag
        footer_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=12)
        footer_frame.pack(side="bottom", fill="x")

        ver_lbl = tk.Label(
            footer_frame,
            text="v2.0 • Offline Desktop Engine",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_SIDEBAR,
            fg=Theme.TEXT_MUTED
        )
        ver_lbl.pack(anchor="w")

        # Set default active tab
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
