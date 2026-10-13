"""
MODULE A — NETWORK ROUTING SIMULATOR (CO5)
Interactive Network Canvas, topology editing, BFS/DFS algorithm simulations,
Queue/Stack visualizers, Adjacency List & Matrix views, Packet Transmission animation,
and Grid-Maze exploration demo.
"""
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Optional

from app.theme import Theme
from app.widgets import CardFrame, StatCard, ConsoleLog, ControlBar
from models.graph import Graph
from models.router import Router
from models.simulation import SimulationStep, SimulationResult
from algorithms.graph_algorithms import bfs_path, dfs_path, grid_maze_bfs, grid_maze_dfs
from services.simulation_service import SimulationService
from ui.dialogs import AddRouterDialog, AddLinkDialog


class NetworkSimulatorView(ttk.Frame):
    """Network Routing Simulator View module."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        # Graph Model
        self.graph = Graph(directed=False)

        # Simulation Service
        self.sim_service = SimulationService(root_widget=self)

        # Selected nodes for routing
        self.source_id: Optional[str] = "R1"
        self.dest_id: Optional[str] = "R6"
        self.selected_router_id: Optional[str] = None
        self.current_result: Optional[SimulationResult] = None

        # Dragging state
        self._drag_data = {"x": 0, "y": 0, "item": None, "router_id": None}

        # Packet animation state
        self._packet_timer = None
        self._packet_coords = (0.0, 0.0)

        # Build UI layout
        self._build_ui()

        # Load default network topology
        self.load_default_topology()

    def on_hide(self):
        """Lifecycle hook when module view is hidden."""
        self.sim_service.stop()
        if self._packet_timer:
            try:
                self.after_cancel(self._packet_timer)
            except Exception:
                pass
            self._packet_timer = None
        self.canvas.delete("packet")

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        # Main Notebook Tabs (Network Canvas vs Grid Maze Demo)
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Tab 1: Topology Canvas & Simulation
        self.canvas_tab = ttk.Frame(self.main_notebook, style="TFrame")
        self.main_notebook.add(self.canvas_tab, text="🌐 Interactive Network Topology")

        self.canvas_tab.grid_rowconfigure(1, weight=1)
        self.canvas_tab.grid_columnconfigure(0, weight=1)

        # Top Control Toolbar
        self._build_top_toolbar(self.canvas_tab)

        # Network Canvas Area
        canvas_frame = CardFrame(self.canvas_tab, padding=4)
        canvas_frame.grid(row=1, column=0, sticky="nsew", pady=6)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=Theme.BG_CANVAS,
            highlightthickness=0,
            cursor="cross"
        )
        self.canvas.pack(fill="both", expand=True)

        # Bind canvas drag events
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        # Bottom Control Bar & Console Log
        self.control_bar = ControlBar(
            self.canvas_tab,
            on_play=self.run_simulation,
            on_pause=self.sim_service.pause,
            on_step=self.sim_service.step_forward,
            on_reset=self.reset_simulation,
            on_speed_change=self.sim_service.set_speed
        )
        self.control_bar.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self.console = ConsoleLog(self.canvas_tab, height=4)
        self.console.grid(row=3, column=0, sticky="ew")

        # Tab 2: Grid-Maze Demo
        self.maze_tab = ttk.Frame(self.main_notebook, style="TFrame")
        self.main_notebook.add(self.maze_tab, text="🧩 Grid-Maze Pathfinding Demo")
        self._build_maze_tab(self.maze_tab)

        # Right Panel: Inspector, Data Structures, Stats & Representations
        right_panel = ttk.Frame(self, style="TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")

        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Stats Cards Panel
        stats_frame = CardFrame(right_panel, title="Network Statistics")
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        s_grid = ttk.Frame(stats_frame, style="Card.TFrame")
        s_grid.pack(fill="x")
        s_grid.columnconfigure((0, 1), weight=1)

        self.card_nodes = StatCard(s_grid, "Routers (V)", "0", Theme.ACCENT_CYAN)
        self.card_nodes.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.card_edges = StatCard(s_grid, "Links (E)", "0", Theme.ACCENT_BLUE)
        self.card_edges.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.card_hops = StatCard(s_grid, "Route Hops", "--", Theme.COLOR_SUCCESS)
        self.card_hops.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        self.card_steps = StatCard(s_grid, "Alg Steps", "0", Theme.COLOR_EXPLORE)
        self.card_steps.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # Data Structure Inspector Notebook (Queue/Stack, Adj List, Adj Matrix)
        inspector_card = CardFrame(right_panel, title="Data Structure Inspector & Representations")
        inspector_card.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        self.inspect_notebook = ttk.Notebook(inspector_card)
        self.inspect_notebook.pack(fill="both", expand=True)

        # Tab: Live Queue/Stack State
        self.ds_frame = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.ds_frame, text="Queue / Stack State")

        self.ds_lbl = ttk.Label(self.ds_frame, text="Current State: Empty", style="CardTitle.TLabel")
        self.ds_lbl.pack(anchor="w", pady=(0, 4))

        self.ds_listbox = tk.Listbox(
            self.ds_frame,
            bg="#FFFFFF",
            fg=Theme.TEXT_MAIN,
            selectbackground=Theme.ACCENT_BLUE,
            selectforeground="#FFFFFF",
            font=Theme.FONT_MONO,
            relief="solid",
            bd=1,
            height=6
        )
        self.ds_listbox.pack(fill="both", expand=True)

        # Tab: Adjacency List
        self.adj_list_frame = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.adj_list_frame, text="Adjacency List O(V+E)")

        self.adj_list_text = tk.Text(
            self.adj_list_frame,
            bg="#FFFFFF",
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_MONO,
            height=6,
            relief="solid",
            bd=1
        )
        self.adj_list_text.pack(fill="both", expand=True)

        # Tab: Adjacency Matrix
        self.adj_mat_frame = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.adj_mat_frame, text="Adjacency Matrix O(V²)")

        self.adj_mat_text = tk.Text(
            self.adj_mat_frame,
            bg="#FFFFFF",
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_MONO,
            height=6,
            relief="solid",
            bd=1
        )
        self.adj_mat_text.pack(fill="both", expand=True)

        # Algorithm Complexity Summary Card
        comp_card = CardFrame(right_panel, title="Algorithm Complexity")
        comp_card.grid(row=2, column=0, sticky="ew")

        self.comp_lbl = ttk.Label(
            comp_card,
            text="BFS: Shortest Path O(V + E)\nDFS: Path Exploration O(V + E)\nAdjacency List Space: O(V + E)\nAdjacency Matrix Space: O(V²)",
            style="Card.TLabel",
            font=Theme.FONT_SMALL
        )
        self.comp_lbl.pack(anchor="w")

    def _build_top_toolbar(self, parent):
        toolbar = CardFrame(parent, padding=8)
        toolbar.grid(row=0, column=0, sticky="ew")

        # Row 1: Algorithm & Route Selection
        row1 = ttk.Frame(toolbar, style="Card.TFrame")
        row1.pack(fill="x", pady=(0, 6))

        ttk.Label(row1, text="Algorithm:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.alg_combo = ttk.Combobox(row1, values=["BFS (Shortest Path)", "DFS (Depth-First)"], state="readonly", width=18)
        self.alg_combo.current(0)
        self.alg_combo.pack(side="left", padx=(0, 12))

        ttk.Label(row1, text="Source:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.src_combo = ttk.Combobox(row1, values=[], state="readonly", width=8)
        self.src_combo.pack(side="left", padx=(0, 8))
        self.src_combo.bind("<<ComboboxSelected>>", self._on_src_dest_change)

        ttk.Label(row1, text="Dest:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.dest_combo = ttk.Combobox(row1, values=[], state="readonly", width=8)
        self.dest_combo.pack(side="left", padx=(0, 12))
        self.dest_combo.bind("<<ComboboxSelected>>", self._on_src_dest_change)

        # Row 2: Topology Control Actions
        row2 = ttk.Frame(toolbar, style="Card.TFrame")
        row2.pack(fill="x")

        ttk.Button(row2, text="+ Router", command=self.add_router_dialog).pack(side="left", padx=2)
        ttk.Button(row2, text="+ Link", command=self.add_link_dialog).pack(side="left", padx=2)
        ttk.Button(row2, text="Toggle Offline", command=self.toggle_selected_offline).pack(side="left", padx=2)
        ttk.Button(row2, text="Random Net", command=self.load_random_topology).pack(side="left", padx=2)
        ttk.Button(row2, text="Disconnected Net", command=self.load_disconnected_topology).pack(side="left", padx=2)
        ttk.Button(row2, text="Default Net", command=self.load_default_topology).pack(side="left", padx=2)

    def load_default_topology(self):
        """Load default router topology."""
        self.graph.clear()
        try:
            g = Graph.load_from_file("data/sample_network.json")
            self.graph = g
        except Exception:
            # Fallback inline creation
            self.graph.add_router(Router("R1", "Core R1", 120, 120))
            self.graph.add_router(Router("R2", "Edge R2", 320, 80))
            self.graph.add_router(Router("R3", "Gateway R3", 520, 140))
            self.graph.add_router(Router("R4", "Switch R4", 180, 300))
            self.graph.add_router(Router("R5", "Distributor R5", 380, 320))
            self.graph.add_router(Router("R6", "Border R6", 580, 300))

            self.graph.add_edge("R1", "R2")
            self.graph.add_edge("R1", "R4")
            self.graph.add_edge("R2", "R3")
            self.graph.add_edge("R2", "R5")
            self.graph.add_edge("R3", "R6")
            self.graph.add_edge("R4", "R5")
            self.graph.add_edge("R5", "R6")

        self.update_comboboxes()
        self.reset_simulation()
        self.console.log("Loaded default network topology.", "info")

    def load_random_topology(self):
        """Generate a random connected router topology."""
        self.graph.clear()
        names = ["Core", "Edge", "Gate", "Switch", "Hub", "Border", "Spine", "Leaf"]
        count = random.randint(6, 9)

        coords = [
            (120, 100), (280, 80), (450, 110), (600, 90),
            (140, 280), (320, 300), (520, 290), (650, 310), (380, 190)
        ]

        for i in range(count):
            rid = f"R{i+1}"
            rname = f"{names[i % len(names)]} R{i+1}"
            cx, cy = coords[i]
            self.graph.add_router(Router(rid, rname, cx, cy))

        # Add edges ensuring connectivity
        r_ids = list(self.graph.routers.keys())
        for i in range(len(r_ids) - 1):
            self.graph.add_edge(r_ids[i], r_ids[i + 1])

        # Extra random links
        for _ in range(random.randint(2, 4)):
            u, v = random.sample(r_ids, 2)
            self.graph.add_edge(u, v)

        self.update_comboboxes()
        self.reset_simulation()
        self.console.log("Generated random connected topology.", "info")

    def load_disconnected_topology(self):
        """Load a network topology with disconnected components."""
        self.graph.clear()
        self.graph.add_router(Router("R1", "Core R1", 140, 140))
        self.graph.add_router(Router("R2", "Edge R2", 300, 140))
        self.graph.add_router(Router("R3", "Isolated R3", 500, 140))
        self.graph.add_router(Router("R4", "Isolated R4", 640, 140))

        self.graph.add_edge("R1", "R2")
        self.graph.add_edge("R3", "R4")  # Separate component

        self.update_comboboxes()
        self.reset_simulation()
        self.console.log("Loaded disconnected network topology for component testing.", "warning")

    def update_comboboxes(self):
        """Refresh router IDs in comboboxes."""
        rids = sorted(list(self.graph.routers.keys()))
        self.src_combo.config(values=rids)
        self.dest_combo.config(values=rids)

        if rids:
            if self.source_id not in rids:
                self.source_id = rids[0]
            if self.dest_id not in rids:
                self.dest_id = rids[-1] if len(rids) > 1 else rids[0]

            self.src_combo.set(self.source_id)
            self.dest_combo.set(self.dest_id)

    def _on_src_dest_change(self, event=None):
        self.source_id = self.src_combo.get()
        self.dest_id = self.dest_combo.get()
        self.reset_simulation()

    def add_router_dialog(self):
        """Open dialog to create router."""
        dlg = AddRouterDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            rid, rname = dlg.result
            if self.graph.add_router(Router(rid, rname, 350, 200)):
                self.update_comboboxes()
                self.redraw_canvas()
                self.console.log(f"Added router '{rid}' ({rname}).", "info")
            else:
                messagebox.showerror("Error", f"Router ID '{rid}' already exists.")

    def add_link_dialog(self):
        """Open dialog to add edge link."""
        rids = sorted(list(self.graph.routers.keys()))
        if len(rids) < 2:
            messagebox.showwarning("Warning", "Need at least 2 routers to add a link.")
            return

        dlg = AddLinkDialog(self, rids)
        self.wait_window(dlg)
        if dlg.result:
            u, v = dlg.result
            if self.graph.add_edge(u, v):
                self.redraw_canvas()
                self.console.log(f"Created link between '{u}' and '{v}'.", "info")
            else:
                messagebox.showerror("Error", "Link creation failed.")

    def toggle_selected_offline(self):
        """Toggle online/offline status of selected or source router."""
        rid = self.selected_router_id or self.source_id
        if not rid or rid not in self.graph.routers:
            return

        r = self.graph.routers[rid]
        new_status = not r.is_online
        self.graph.set_router_online_status(rid, new_status)
        self.reset_simulation()
        status_str = "Online" if new_status else "Offline"
        self.console.log(f"Router '{rid}' is now {status_str}.", "warning" if not new_status else "info")

    def run_simulation(self):
        """Run BFS or DFS routing simulation."""
        if not self.source_id or not self.dest_id:
            messagebox.showwarning("Warning", "Select valid Source and Destination routers.")
            return

        alg_type = self.alg_combo.get()
        if "BFS" in alg_type:
            result = bfs_path(self.graph, self.source_id, self.dest_id)
        else:
            result = dfs_path(self.graph, self.source_id, self.dest_id)

        self.current_result = result
        self.sim_service.load_simulation(
            result=result,
            on_step=self._on_sim_step,
            on_complete=self._on_sim_complete
        )
        self.sim_service.play()

    def reset_simulation(self):
        """Reset canvas highlights and simulation state."""
        self.sim_service.stop()
        self.current_result = None
        self.ds_listbox.delete(0, "end")
        self.ds_lbl.config(text="Current State: Idle")
        self.redraw_canvas()
        self.update_stats()
        self.update_representations()

    def _on_sim_step(self, step: SimulationStep, step_num: int, total_steps: int):
        """Callback executed on each simulation step."""
        self.redraw_canvas(step=step)
        self.console.log(step.message, level="explore" if step.step_type in ["enqueue", "push"] else "info")

        # Update Live Data Structure Inspector
        self.ds_listbox.delete(0, "end")
        ds_type = "Queue" if "BFS" in self.alg_combo.get() else "Stack"
        self.ds_lbl.config(text=f"BFS/DFS {ds_type} Contents (Step {step_num}/{total_steps}):")

        if step.data_structure_state:
            for item in step.data_structure_state:
                self.ds_listbox.insert("end", f"  📍 {item}")

        # Update stats
        self.card_steps.update_value(str(step_num))

    def _on_sim_complete(self):
        """Callback when algorithm completes."""
        if not self.current_result:
            return

        res = self.current_result
        if res.success:
            self.console.log(res.message, "success")
            self.card_hops.update_value(f"{len(res.path)-1} hops", Theme.COLOR_SUCCESS)

            # Trigger Packet Transmission Animation
            self.animate_packet_transmission(res.path)
        else:
            self.console.log(res.message, "error")
            self.card_hops.update_value("Unreachable", Theme.COLOR_ERROR)

    def animate_packet_transmission(self, path: List[str]):
        """Animate pink packet circle moving along the path routers."""
        if len(path) < 2:
            return

        coords_list = []
        for rid in path:
            if rid in self.graph.routers:
                r = self.graph.routers[rid]
                coords_list.append((r.x, r.y))

        # Interpolate packet coordinates along hops
        frames_per_hop = 15
        all_frames = []
        for i in range(len(coords_list) - 1):
            x1, y1 = coords_list[i]
            x2, y2 = coords_list[i + 1]
            for f in range(frames_per_hop):
                t = f / float(frames_per_hop)
                px = x1 + (x2 - x1) * t
                py = y1 + (y2 - y1) * t
                all_frames.append((px, py))
        all_frames.append(coords_list[-1])

        def _draw_packet_frame(frame_idx: int):
            if frame_idx >= len(all_frames):
                self.console.log("Packet successfully transmitted to destination.", "success")
                return

            px, py = all_frames[frame_idx]
            self.canvas.delete("packet")
            self.canvas.create_oval(
                px - 8, py - 8, px + 8, py + 8,
                fill=Theme.COLOR_PACKET,
                outline=Theme.TEXT_MAIN,
                width=2,
                tags="packet"
            )
            self._packet_timer = self.after(40, lambda: _draw_packet_frame(frame_idx + 1))

        _draw_packet_frame(0)

    def redraw_canvas(self, step: Optional[SimulationStep] = None):
        """Render routers and link edges on Tkinter Canvas."""
        self.canvas.delete("all")

        visited_nodes = set(step.visited_elements) if step else set()
        active_path_nodes = set(step.active_path) if step else set()
        current_node = step.current_element if step else None

        final_path = set(self.current_result.path) if (self.current_result and self.current_result.success) else set()

        # Draw Edges first
        for u, v, w in self.graph.get_edges():
            ru = self.graph.routers[u]
            rv = self.graph.routers[v]

            edge_color = Theme.BORDER_COLOR
            width = 2

            if u in final_path and v in final_path:
                edge_color = Theme.COLOR_SUCCESS
                width = 4
            elif step and step.active_path and len(step.active_path) >= 2:
                if (u == step.active_path[0] and v == step.active_path[1]) or (v == step.active_path[0] and u == step.active_path[1]):
                    edge_color = Theme.COLOR_EXPLORE
                    width = 4

            self.canvas.create_line(ru.x, ru.y, rv.x, rv.y, fill=edge_color, width=width, tags="edge")

        # Draw Router Nodes
        radius = 22
        for rid, r in self.graph.routers.items():
            # Color determination
            fill_color = Theme.BG_CARD_ALT
            outline_color = Theme.BORDER_COLOR

            if not r.is_online:
                fill_color = Theme.COLOR_OFFLINE
            elif rid == self.source_id:
                fill_color = Theme.ACCENT_CYAN
                outline_color = Theme.TEXT_MAIN
            elif rid == self.dest_id:
                fill_color = Theme.COLOR_SUCCESS
                outline_color = Theme.TEXT_MAIN
            elif rid == current_node:
                fill_color = Theme.COLOR_EXPLORE
            elif rid in final_path:
                fill_color = Theme.COLOR_SUCCESS
            elif rid in visited_nodes:
                fill_color = Theme.ACCENT_BLUE

            # Draw Node Circle
            node_tag = f"node_{rid}"
            self.canvas.create_oval(
                r.x - radius, r.y - radius, r.x + radius, r.y + radius,
                fill=fill_color, outline=outline_color, width=2, tags=("node", node_tag)
            )

            # Label Text inside node
            textColor = Theme.TEXT_DARK if fill_color in [Theme.ACCENT_CYAN, Theme.COLOR_SUCCESS, Theme.COLOR_EXPLORE] else Theme.TEXT_MAIN
            self.canvas.create_text(
                r.x, r.y,
                text=r.id,
                font=Theme.FONT_BOLD,
                fill=textColor,
                tags=("node", node_tag)
            )

            # Name Subtitle below node
            self.canvas.create_text(
                r.x, r.y + radius + 12,
                text=r.name,
                font=Theme.FONT_SMALL,
                fill=Theme.TEXT_MUTED,
                tags=("node", node_tag)
            )

    def update_stats(self):
        """Update network node and link count stats."""
        self.card_nodes.update_value(str(len(self.graph.routers)))
        self.card_edges.update_value(str(len(self.graph.get_edges())))

    def update_representations(self):
        """Refresh Adjacency List and Adjacency Matrix representations."""
        # Adjacency List Text
        adj_dict = self.graph.get_adjacency_list_view()
        self.adj_list_text.delete("1.0", "end")
        for r_id, nbrs in adj_dict.items():
            status = "Online" if self.graph.routers[r_id].is_online else "Offline"
            self.adj_list_text.insert("end", f"{r_id} ({status}) -> [{', '.join(nbrs)}]\n")

        # Adjacency Matrix Text
        nodes, matrix = self.graph.get_adjacency_matrix_view()
        self.adj_mat_text.delete("1.0", "end")
        if nodes:
            header = "    " + " ".join(f"{n:>4}" for n in nodes) + "\n"
            self.adj_mat_text.insert("end", header)
            self.adj_mat_text.insert("end", "    " + "-" * (len(nodes) * 5) + "\n")
            for i, row in enumerate(matrix):
                row_str = f"{nodes[i]:<3}| " + " ".join(f"{val:>4}" for val in row) + "\n"
                self.adj_mat_text.insert("end", row_str)

    # --- Canvas Drag & Drop Node Interactions ---
    def _on_canvas_click(self, event):
        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("node_"):
                    rid = tag.replace("node_", "")
                    self._drag_data["item"] = item
                    self._drag_data["router_id"] = rid
                    self._drag_data["x"] = event.x
                    self._drag_data["y"] = event.y
                    self.selected_router_id = rid
                    return

    def _on_canvas_drag(self, event):
        rid = self._drag_data["router_id"]
        if rid and rid in self.graph.routers:
            r = self.graph.routers[rid]
            r.x = event.x
            r.y = event.y
            self.redraw_canvas()

    def _on_canvas_release(self, event):
        self._drag_data["item"] = None
        self._drag_data["router_id"] = None

    # --- 2D Grid-Maze Demonstration Tab ---
    def _build_maze_tab(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Maze controls toolbar
        bar = CardFrame(parent, padding=8)
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Button(bar, text="Run Grid BFS (Shortest)", style="Primary.TButton", command=self._run_maze_bfs).pack(side="left", padx=4)
        ttk.Button(bar, text="Run Grid DFS (Exploration)", command=self._run_maze_dfs).pack(side="left", padx=4)
        ttk.Button(bar, text="Reset Grid Maze", command=self._reset_maze).pack(side="left", padx=4)

        self.maze_status_lbl = ttk.Label(bar, text="Click cells to toggle walls (Black). Green = Start, Red = End.", style="Card.TLabel")
        self.maze_status_lbl.pack(side="right", padx=8)

        # 2D Grid Canvas
        self.maze_grid = [
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0]
        ]
        self.maze_start = (0, 0)
        self.maze_end = (5, 7)

        self.maze_canvas = tk.Canvas(parent, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.maze_canvas.grid(row=1, column=0, sticky="nsew", pady=6)
        self.maze_canvas.bind("<Button-1>", self._on_maze_click)

        self._draw_maze()

    def _draw_maze(self, path=None, visited=None):
        self.maze_canvas.delete("all")
        rows = len(self.maze_grid)
        cols = len(self.maze_grid[0])

        cw = 60
        ch = 60

        visited_set = set(visited) if visited else set()
        path_set = set(path) if path else set()

        for r in range(rows):
            for c in range(cols):
                x1, y1 = c * cw + 20, r * ch + 20
                x2, y2 = x1 + cw, y1 + ch

                fill = Theme.BG_CARD
                if self.maze_grid[r][c] == 1:
                    fill = "#1E1E1E"  # Wall
                elif (r, c) == self.maze_start:
                    fill = Theme.ACCENT_CYAN
                elif (r, c) == self.maze_end:
                    fill = Theme.COLOR_ERROR
                elif (r, c) in path_set:
                    fill = Theme.COLOR_SUCCESS
                elif (r, c) in visited_set:
                    fill = Theme.COLOR_EXPLORE

                self.maze_canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=Theme.BORDER_COLOR, width=1)
                self.maze_canvas.create_text(x1 + cw / 2, y1 + ch / 2, text=f"({r},{c})", fill=Theme.TEXT_MUTED, font=Theme.FONT_SMALL)

    def _on_maze_click(self, event):
        cw, ch = 60, 60
        c = (event.x - 20) // cw
        r = (event.y - 20) // ch

        if 0 <= r < len(self.maze_grid) and 0 <= c < len(self.maze_grid[0]):
            if (r, c) not in [self.maze_start, self.maze_end]:
                self.maze_grid[r][c] = 1 if self.maze_grid[r][c] == 0 else 0
                self._draw_maze()

    def _run_maze_bfs(self):
        res = grid_maze_bfs(self.maze_grid, self.maze_start, self.maze_end)
        if res.success:
            self._draw_maze(path=res.path, visited=res.visited_order)
            self.maze_status_lbl.config(text=f"Grid BFS Shortest Path Found ({len(res.path)-1} steps).")
        else:
            self.maze_status_lbl.config(text="No reachable path in maze.")

    def _run_maze_dfs(self):
        res = grid_maze_dfs(self.maze_grid, self.maze_start, self.maze_end)
        if res.success:
            self._draw_maze(path=res.path, visited=res.visited_order)
            self.maze_status_lbl.config(text=f"Grid DFS Path Explored ({len(res.path)-1} steps).")
        else:
            self.maze_status_lbl.config(text="No reachable path in maze.")

    def _reset_maze(self):
        self._draw_maze()
        self.maze_status_lbl.config(text="Grid maze reset.")
