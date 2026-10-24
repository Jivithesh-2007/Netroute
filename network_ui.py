"""Module 6: network_ui.py - Network Topology Visualizer & Routing UI."""
import tkinter as tk
from theme import BG_CARD, PRIMARY, SUCCESS, DANGER, ROUTE_COLOR, FONT_BOLD, FONT_NORMAL, FONT_SMALL
from network import Graph

class NetworkView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        self.g = Graph()
        self.g.load_sample()
        self.active_path = []

        ctrl = tk.Frame(self, bg=BG_CARD)
        ctrl.pack(fill="x", padx=10, pady=5)
        tk.Label(ctrl, text="Src:", bg=BG_CARD, font=FONT_SMALL).pack(side="left")
        self.src_ent = tk.Entry(ctrl, width=4, font=FONT_NORMAL)
        self.src_ent.insert(0, "R1")
        self.src_ent.pack(side="left", padx=2)

        tk.Label(ctrl, text="Dst:", bg=BG_CARD, font=FONT_SMALL).pack(side="left", padx=(4, 0))
        self.dst_ent = tk.Entry(ctrl, width=4, font=FONT_NORMAL)
        self.dst_ent.insert(0, "R5")
        self.dst_ent.pack(side="left", padx=2)

        tk.Button(ctrl, text="BFS (Shortest)", bg=PRIMARY, fg="white", font=FONT_SMALL, command=self.run_bfs).pack(side="left", padx=3)
        tk.Button(ctrl, text="DFS", bg=SUCCESS, fg="white", font=FONT_SMALL, command=self.run_dfs).pack(side="left", padx=3)

        tk.Label(ctrl, text="Add Router:", bg=BG_CARD, font=FONT_SMALL).pack(side="left", padx=(6, 0))
        self.new_node = tk.Entry(ctrl, width=4, font=FONT_NORMAL)
        self.new_node.pack(side="left", padx=2)
        tk.Button(ctrl, text="+", bg=PRIMARY, fg="white", font=FONT_SMALL, command=self.on_add_router).pack(side="left", padx=1)

        tk.Label(ctrl, text="Link (u,v):", bg=BG_CARD, font=FONT_SMALL).pack(side="left", padx=(4, 0))
        self.new_link = tk.Entry(ctrl, width=6, font=FONT_NORMAL)
        self.new_link.pack(side="left", padx=2)
        tk.Button(ctrl, text="Link", bg=PRIMARY, fg="white", font=FONT_SMALL, command=self.on_add_link).pack(side="left", padx=1)
        tk.Button(ctrl, text="Reset", bg="#64748B", fg="white", font=FONT_SMALL, command=self.on_reset).pack(side="left", padx=4)

        self.info_lbl = tk.Label(self, text="Click BFS or DFS to discover route.", bg=BG_CARD, font=FONT_NORMAL, fg=PRIMARY)
        self.info_lbl.pack(fill="x", padx=10, pady=2)

        self.canvas = tk.Canvas(self, bg="#F8FAFC", height=320, highlightthickness=1, highlightbackground="#CBD5E1")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=4)
        self.draw_network()

    def run_bfs(self):
        s, d = self.src_ent.get(), self.dst_ent.get()
        self.active_path = self.g.bfs(s, d)
        hops = len(self.active_path) - 1 if self.active_path else 0
        self.info_lbl.config(text=f"BFS Route: {' -> '.join(self.active_path)} ({hops} hops)" if self.active_path else f"No path between {s} and {d}")
        self.draw_network()

    def run_dfs(self):
        s, d = self.src_ent.get(), self.dst_ent.get()
        self.active_path = self.g.dfs(s, d)
        self.info_lbl.config(text=f"DFS Discovery: {' -> '.join(self.active_path)}" if self.active_path else f"No path between {s} and {d}")
        self.draw_network()

    def on_add_router(self):
        r = self.new_node.get().strip().upper()
        if self.g.add_node(r, 200, 150):
            self.new_node.delete(0, tk.END)
            self.draw_network()

    def on_add_link(self):
        parts = self.new_link.get().split(",")
        if len(parts) == 2 and self.g.add_edge(parts[0], parts[1]):
            self.new_link.delete(0, tk.END)
            self.draw_network()

    def on_reset(self):
        self.g.load_sample()
        self.active_path = []
        self.info_lbl.config(text="Network reset to sample topology.")
        self.draw_network()

    def draw_network(self):
        self.canvas.delete("all")
        path_edges = set(zip(self.active_path, self.active_path[1:])) | set(zip(self.active_path[1:], self.active_path))
        drawn_links = set()
        for u, neighbors in self.g.edges.items():
            for v in neighbors:
                link = tuple(sorted((u, v)))
                if link not in drawn_links and u in self.g.nodes and v in self.g.nodes:
                    drawn_links.add(link)
                    x1, y1 = self.g.nodes[u]
                    x2, y2 = self.g.nodes[v]
                    is_p = (u, v) in path_edges
                    self.canvas.create_line(x1, y1, x2, y2, fill=ROUTE_COLOR if is_p else "#94A3B8", width=3 if is_p else 1)
        for name, (x, y) in self.g.nodes.items():
            is_active = name in self.active_path
            fill_c = ROUTE_COLOR if is_active else "#2563EB"
            self.canvas.create_oval(x-18, y-18, x+18, y+18, fill=fill_c, outline="#1E293B", width=2)
            self.canvas.create_text(x, y, text=name, fill="white", font=FONT_BOLD)
