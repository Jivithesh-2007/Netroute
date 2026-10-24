import tkinter as tk
from tkinter import ttk
from theme import Theme
from network_ui import NetworkSimulatorView

class NetRouteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NetRoute — Interactive Network Packet-Routing Simulator (BFS & DFS)")
        self.geometry("1380x880")
        self.minsize(1080, 720)
        self.configure(bg=Theme.BG_APP)

        Theme.setup_styles(self)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()

        self.workspace = NetworkSimulatorView(self, app=self)
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 6))

        self._build_status_bar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=Theme.BG_CARD, padx=16, pady=10, highlightbackground=Theme.BORDER, highlightthickness=1)
        hdr.grid(row=0, column=0, sticky="ew")

        left = tk.Frame(hdr, bg=Theme.BG_CARD)
        left.pack(side="left")

        title = tk.Label(
            left,
            text="NetRoute",
            font=Theme.FONT_TITLE,
            bg=Theme.BG_CARD,
            fg=Theme.PRIMARY
        )
        title.pack(side="left")

        sep = tk.Label(left, text="•", font=(Theme.FONT_FAMILY, 14), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        sep.pack(side="left", padx=10)

        subtitle = tk.Label(
            left,
            text="Interactive Network Packet-Routing Simulator (BFS & DFS Traversal)",
            font=Theme.FONT_PAGE_HEAD,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN
        )
        subtitle.pack(side="left")

        right = tk.Frame(hdr, bg=Theme.BG_CARD)
        right.pack(side="right")

        badges = [
            ("CO1 STACK / QUEUE", Theme.PRIMARY),
            ("CO2 DYNAMIC GRAPH", Theme.SECONDARY),
            ("CO5 NETWORK ROUTING", Theme.SUCCESS)
        ]
        for text, color in badges:
            b = tk.Label(
                right,
                text=text,
                font=Theme.FONT_SMALL_BOLD,
                bg=Theme.BG_PANEL_ALT,
                fg=color,
                padx=10,
                pady=3,
                highlightbackground=Theme.BORDER,
                highlightthickness=1
            )
            b.pack(side="left", padx=4)

    def _build_status_bar(self):
        st_bar = tk.Frame(self, bg=Theme.BG_CARD, padx=14, pady=5, highlightbackground=Theme.BORDER, highlightthickness=1)
        st_bar.grid(row=2, column=0, sticky="ew")

        self.lbl_status = tk.Label(
            st_bar,
            text="System Ready • Dynamic Adjacency List O(V + E) • Shortest-Hop BFS & Path Discovery DFS",
            font=Theme.FONT_STATUS,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED
        )
        self.lbl_status.pack(side="left")

        right_info = tk.Label(
            st_bar,
            text="Standard Library Python 3 • Native Tkinter & Canvas • Zero External APIs",
            font=Theme.FONT_STATUS,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED
        )
        right_info.pack(side="right")

    def set_status(self, text: str):
        self.lbl_status.config(text=text)
