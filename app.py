"""Module 7: app.py - Main Desktop Application Window & Navigation."""
import tkinter as tk
from theme import BG_MAIN, BG_CARD, BG_SIDEBAR, PRIMARY, TEXT_LIGHT, FONT_TITLE, FONT_HEADING, FONT_NORMAL, FONT_SMALL
from network_ui import NetworkView
from labs_ui import LabsFrame
from tree_ui import TreeFrame

class NetRouteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NetRoute - DSA & Network Routing Simulator")
        self.geometry("960x600")
        self.minsize(800, 500)
        self.configure(bg=BG_MAIN)

        # Main Layout: Sidebar on Left, Content on Right
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Header
        tk.Label(self.sidebar, text="NetRoute", bg=BG_SIDEBAR, fg="white", font=FONT_TITLE).pack(anchor="w", padx=16, pady=(20, 2))
        tk.Label(self.sidebar, text="DSA & Network Simulator", bg=BG_SIDEBAR, fg="#94A3B8", font=FONT_SMALL).pack(anchor="w", padx=16)
        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill="x", padx=12, pady=15)

        # Navigation Buttons
        self.buttons = {}
        nav_items = [
            ("network", "🌐  Network Routing"),
            ("labs", "📊  Search, Sort & Hash"),
            ("trees", "🌲  Binary Search Tree")
        ]
        for key, text in nav_items:
            b = tk.Button(
                self.sidebar, text=text, bg=BG_SIDEBAR, fg=TEXT_LIGHT, font=FONT_NORMAL,
                bd=0, activebackground=PRIMARY, activeforeground="white",
                anchor="w", padx=12, pady=8, command=lambda k=key: self.show_view(k)
            )
            b.pack(fill="x", padx=8, pady=3)
            self.buttons[key] = b

        # Status indicator at bottom of sidebar
        tk.Label(self.sidebar, text="● Offline Mode | College Project", bg=BG_SIDEBAR, fg="#10B981", font=FONT_SMALL).pack(side="bottom", anchor="w", padx=16, pady=15)

        # Content Area
        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        # Header Title in Content Area
        self.header_title = tk.Label(self.container, text="", bg=BG_MAIN, fg="#0F172A", font=FONT_HEADING)
        self.header_title.pack(anchor="w", pady=(0, 6))

        # View Frames
        self.views = {
            "network": (NetworkView(self.container), "Network Routing Simulator (BFS & DFS)"),
            "labs": (LabsFrame(self.container), "Searching, Sorting & Hash Table Lab"),
            "trees": (TreeFrame(self.container), "Binary Search Tree (BST) Lab")
        }
        for view, _ in self.views.values():
            view.pack(fill="both", expand=True)
            view.pack_forget()

        # Show initial view
        self.show_view("network")

    def show_view(self, key):
        for k, (view, title) in self.views.items():
            if k == key:
                view.pack(fill="both", expand=True)
                self.header_title.config(text=title)
                self.buttons[k].config(bg=PRIMARY)
            else:
                view.pack_forget()
                self.buttons[k].config(bg=BG_SIDEBAR)
