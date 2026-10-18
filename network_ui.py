import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Optional, Any

from theme import Theme, CardFrame, StatCard, ConsoleLog, ControlBar, ZoomPanToolbar, SimulationService
from network import (
    Graph, Router, SimulationStep, SimulationResult,
    bfs_path, dfs_path, grid_maze_bfs, grid_maze_dfs, validate_router_id
)


class AddRouterDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add New Router")
        self.geometry("340x220")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_DARK)

        self.result = None

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Router ID (e.g. R7):", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.id_entry = ttk.Entry(frame)
        self.id_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Display Name:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.name_entry = ttk.Entry(frame)
        self.name_entry.pack(fill="x", pady=(0, 16))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", side="bottom")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Add Router", style="Primary.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()
        self.id_entry.focus_set()

    def _on_submit(self):
        rid = self.id_entry.get().strip().upper()
        rname = self.name_entry.get().strip() or f"Router {rid}"

        valid, msg = validate_router_id(rid)
        if not valid:
            messagebox.showerror("Invalid Input", msg, parent=self)
            return

        self.result = (rid, rname)
        self.destroy()


class AddLinkDialog(tk.Toplevel):
    def __init__(self, parent, router_ids: list):
        super().__init__(parent)
        self.title("Add Network Link")
        self.geometry("340x220")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_DARK)

        self.result = None
        self.router_ids = router_ids

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Source Router:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.u_combo = ttk.Combobox(frame, values=router_ids, state="readonly")
        self.u_combo.pack(fill="x", pady=(0, 10))
        if router_ids:
            self.u_combo.current(0)

        ttk.Label(frame, text="Target Router:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.v_combo = ttk.Combobox(frame, values=router_ids, state="readonly")
        self.v_combo.pack(fill="x", pady=(0, 16))
        if len(router_ids) > 1:
            self.v_combo.current(1)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", side="bottom")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Add Link", style="Primary.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()

    def _on_submit(self):
        u = self.u_combo.get()
        v = self.v_combo.get()

        if not u or not v:
            messagebox.showerror("Invalid Selection", "Please select both source and target routers.", parent=self)
            return

        if u == v:
            messagebox.showerror("Invalid Connection", "Self-connections are not allowed.", parent=self)
            return

        self.result = (u, v)
        self.destroy()


class RemoveLinkDialog(tk.Toplevel):
    def __init__(self, parent, edges: list):
        super().__init__(parent)
        self.title("Remove Network Link")
        self.geometry("360x200")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_DARK)

        self.result = None
        self.edges = edges

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Select Link to Remove:", style="Card.TLabel").pack(anchor="w", pady=(0, 6))

        edge_strs = [f"{u} ⟷ {v}" for u, v, _ in edges]
        self.combo = ttk.Combobox(frame, values=edge_strs, state="readonly")
        self.combo.pack(fill="x", pady=(0, 16))
        if edge_strs:
            self.combo.current(0)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", side="bottom")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Remove Link", style="Danger.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()

    def _on_submit(self):
        idx = self.combo.current()
        if idx >= 0 and idx < len(self.edges):
            u, v, _ = self.edges[idx]
            self.result = (u, v)
            self.destroy()


class RouteComparisonDialog(tk.Toplevel):
    def __init__(self, parent, bfs_res, dfs_res, src_id: str, dest_id: str):
        super().__init__(parent)
        self.title(f"Route Comparison: {src_id} ➔ {dest_id}")
        self.geometry("640x480")
        self.minsize(580, 420)
        self.configure(bg=Theme.BG_DARK)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        header = ttk.Frame(frame)
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(
            header,
            text=f"Routing Comparison: '{src_id}' to '{dest_id}'",
            style="Header.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="CO5 Comparative Analysis: BFS (Shortest Hop) vs DFS (Depth-First Exploration)",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        table_frame = ttk.Frame(frame, style="CardAlt.TFrame", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 12))

        columns = ("Metric", "BFS (Queue / FIFO)", "DFS (Stack / LIFO)")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=7)
        tree.pack(fill="both", expand=True)

        for col in columns:
            tree.heading(col, text=col)

        tree.column("Metric", width=160)
        tree.column("BFS (Queue / FIFO)", width=200)
        tree.column("DFS (Stack / LIFO)", width=200)

        bfs_path_str = " -> ".join(bfs_res.path) if bfs_res.success else "None (Unreachable)"
        dfs_path_str = " -> ".join(dfs_res.path) if dfs_res.success else "None (Unreachable)"
        bfs_hops = str(len(bfs_res.path) - 1) if bfs_res.success else "--"
        dfs_hops = str(len(dfs_res.path) - 1) if dfs_res.success else "--"

        tree.insert("", "end", values=("Route Status", "Reachable ✔" if bfs_res.success else "Unreachable ✖", "Reachable ✔" if dfs_res.success else "Unreachable ✖"))
        tree.insert("", "end", values=("Hops (Edges)", f"{bfs_hops} hops (Optimal)", f"{dfs_hops} hops (Not guaranteed)"))
        tree.insert("", "end", values=("Route Sequence", bfs_path_str, dfs_path_str))
        tree.insert("", "end", values=("Visited Routers", f"{len(bfs_res.visited_order)} routers", f"{len(dfs_res.visited_order)} routers"))
        tree.insert("", "end", values=("Explored Steps", f"{bfs_res.total_steps} steps", f"{dfs_res.total_steps} steps"))
        tree.insert("", "end", values=("Time Complexity", "O(V + E)", "O(V + E)"))
        tree.insert("", "end", values=("Space Complexity", "O(V) Queue", "O(V) Stack"))

        note_frame = ttk.Frame(frame, style="CardAlt.TFrame", padding=10)
        note_frame.pack(fill="x", pady=(0, 12))

        note_title = ttk.Label(note_frame, text="DSA Educational Analysis:", style="CardTitle.TLabel")
        note_title.pack(anchor="w", pady=(0, 4))

        note_text = (
            "• BFS guarantees the minimum hop count in an unweighted network because vertices are discovered level-by-level.\n"
            "• DFS explores a deep path first and backtracks, identifying reachability without guaranteeing optimal distance.\n"
            "• For production IP routing tables (OSPF/RIP), BFS-derived principles ensure shortest path delivery."
        )
        note_lbl = ttk.Label(note_frame, text=note_text, style="Card.TLabel", font=Theme.FONT_SMALL)
        note_lbl.pack(anchor="w")

        btn_close = ttk.Button(frame, text="Close", style="Primary.TButton", command=self.destroy)
        btn_close.pack(side="right")

        self.transient(parent)
        self.grab_set()


class NetworkSimulatorView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.graph = Graph(directed=False)
        self.sim_service = SimulationService(root_widget=self)

        self.source_id: Optional[str] = "R1"
        self.dest_id: Optional[str] = "R6"
        self.selected_router_id: Optional[str] = None
        self.current_result: Optional[SimulationResult] = None

        self.scale: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

        self._drag_data = {
            "mode": None,
            "start_x": 0,
            "start_y": 0,
            "router_id": None
        }

        self._packet_timer = None
        self._packet_frames: List[Tuple[float, float]] = []
        self._packet_frame_idx: int = 0
        self._inspector_visible: bool = True

        self._build_ui()
        self.load_preset("default")
        self.after(150, self.fit_to_view)

    def on_hide(self):
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
        self.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.tab_network = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_network, text="  🌐 Network Topology & Routing Simulation  ")

        self.tab_network.grid_rowconfigure(0, weight=1)
        self.tab_network.grid_columnconfigure(0, weight=1)

        self.paned_window = ttk.Panedwindow(self.tab_network, orient="horizontal")
        self.paned_window.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.work_area = ttk.Frame(self.paned_window, style="TFrame")
        self.paned_window.add(self.work_area, weight=3)

        self.work_area.grid_rowconfigure(1, weight=1)
        self.work_area.grid_columnconfigure(0, weight=1)

        self._build_toolbars(self.work_area)

        canvas_container = CardFrame(self.work_area, padding=4)
        canvas_container.grid(row=1, column=0, sticky="nsew", pady=(6, 6))

        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_container,
            bg=Theme.BG_CANVAS,
            highlightthickness=0,
            cursor="arrow"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.zoom_toolbar = ZoomPanToolbar(
            canvas_container,
            on_zoom_in=self.zoom_in,
            on_zoom_out=self.zoom_out,
            on_fit_view=self.fit_to_view,
            on_reset_zoom=self.reset_zoom
        )
        self.zoom_toolbar.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.canvas.bind("<ButtonPress-1>", self._on_canvas_press_1)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag_1)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release_1)

        self.canvas.bind("<ButtonPress-2>", self._on_pan_start)
        self.canvas.bind("<B2-Motion>", self._on_pan_drag)
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_drag)

        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.zoom(1.15, e.x, e.y))
        self.canvas.bind("<Button-5>", lambda e: self.zoom(1.0 / 1.15, e.x, e.y))
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.control_bar = ControlBar(
            self.work_area,
            on_play=self.run_simulation,
            on_pause=self.sim_service.pause,
            on_step=self.sim_service.step_forward,
            on_reset=self.reset_simulation,
            on_speed_change=self.sim_service.set_speed
        )
        self.control_bar.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self.console = ConsoleLog(self.work_area, height=5)
        self.console.grid(row=3, column=0, sticky="ew")

        self.inspector_panel = ttk.Frame(self.paned_window, style="TFrame")
        self.paned_window.add(self.inspector_panel, weight=1)

        self._build_inspector(self.inspector_panel)

        self.tab_maze = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_maze, text="  🧩 2D Grid-Maze Exploration Demo  ")
        self._build_maze_tab(self.tab_maze)

    def _build_toolbars(self, parent):
        toolbar_card = CardFrame(parent, padding=(8, 6))
        toolbar_card.grid(row=0, column=0, sticky="ew")

        row1 = ttk.Frame(toolbar_card, style="Card.TFrame")
        row1.pack(fill="x", pady=(0, 6))

        ttk.Label(row1, text="Algorithm:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.alg_combo = ttk.Combobox(
            row1,
            values=["BFS (Shortest Path)", "DFS (Depth-First)"],
            state="readonly",
            width=20
        )
        self.alg_combo.current(0)
        self.alg_combo.pack(side="left", padx=(0, 10))

        ttk.Label(row1, text="Source:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.src_combo = ttk.Combobox(row1, values=[], state="readonly", width=7)
        self.src_combo.pack(side="left", padx=(0, 10))
        self.src_combo.bind("<<ComboboxSelected>>", self._on_src_dest_change)

        ttk.Label(row1, text="Dest:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.dest_combo = ttk.Combobox(row1, values=[], state="readonly", width=7)
        self.dest_combo.pack(side="left", padx=(0, 12))
        self.dest_combo.bind("<<ComboboxSelected>>", self._on_src_dest_change)

        self.btn_run = ttk.Button(row1, text="▶ Run Route", style="Primary.TButton", command=self.run_simulation)
        self.btn_run.pack(side="left", padx=(0, 6))

        self.btn_compare = ttk.Button(row1, text="⚖ Compare BFS & DFS", command=self.open_route_comparison)
        self.btn_compare.pack(side="left", padx=(0, 6))

        self.btn_toggle_inspect = ttk.Button(
            row1,
            text="◫ Toggle Inspector",
            style="Tool.TButton",
            command=self.toggle_inspector
        )
        self.btn_toggle_inspect.pack(side="right")

        row2 = ttk.Frame(toolbar_card, style="Card.TFrame")
        row2.pack(fill="x")

        ttk.Button(row2, text="+ Router", style="Tool.TButton", command=self.add_router_dialog).pack(side="left", padx=2)
        ttk.Button(row2, text="+ Link", style="Tool.TButton", command=self.add_link_dialog).pack(side="left", padx=2)
        ttk.Button(row2, text="🗑 Delete Selected", style="Tool.TButton", command=self.delete_selected_router).pack(side="left", padx=2)
        ttk.Button(row2, text="✂ Remove Link", style="Tool.TButton", command=self.remove_link_dialog).pack(side="left", padx=2)
        ttk.Button(row2, text="⚡ Toggle Offline", style="Tool.TButton", command=self.toggle_selected_offline).pack(side="left", padx=2)

        ttk.Separator(row2, orient="vertical").pack(side="left", fill="y", padx=6, pady=2)

        ttk.Label(row2, text="Presets:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(2, 4))
        self.preset_combo = ttk.Combobox(
            row2,
            values=[
                "Default 6-Node Net",
                "Small Connected (5 Routers)",
                "Medium Network (9 Routers)",
                "Disconnected Partitions",
                "Alternate Routes (Hop Demo)",
                "Offline Bottleneck Reroute",
                "Random Connected Graph"
            ],
            state="readonly",
            width=24
        )
        self.preset_combo.current(0)
        self.preset_combo.pack(side="left", padx=(0, 4))
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)

        ttk.Separator(row2, orient="vertical").pack(side="left", fill="y", padx=6, pady=2)

        ttk.Button(row2, text="💾 Save Net", style="Tool.TButton", command=self.save_topology_dialog).pack(side="left", padx=2)
        ttk.Button(row2, text="📂 Load Net", style="Tool.TButton", command=self.load_topology_dialog).pack(side="left", padx=2)

    def _build_inspector(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        stats_frame = CardFrame(parent, title="Network Statistics & Metrics", padding=8)
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        s_grid = ttk.Frame(stats_frame, style="Card.TFrame")
        s_grid.pack(fill="x")
        s_grid.columnconfigure((0, 1, 2), weight=1)

        self.card_nodes = StatCard(s_grid, "Routers (V)", "0", Theme.ACCENT_BLUE)
        self.card_nodes.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.card_edges = StatCard(s_grid, "Links (E)", "0", Theme.ACCENT_CYAN)
        self.card_edges.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.card_reach = StatCard(s_grid, "Reachability", "Ready", Theme.COLOR_SUCCESS)
        self.card_reach.grid(row=0, column=2, sticky="ew", padx=2, pady=2)

        self.card_hops = StatCard(s_grid, "Route Hops", "--", Theme.COLOR_SUCCESS)
        self.card_hops.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        self.card_steps = StatCard(s_grid, "Alg Steps", "0", Theme.COLOR_EXPLORE)
        self.card_steps.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        self.card_comp = StatCard(s_grid, "Components", "1", Theme.TEXT_MUTED)
        self.card_comp.grid(row=1, column=2, sticky="ew", padx=2, pady=2)

        inspect_card = CardFrame(parent, title="Data Structure Inspector & Representations", padding=8)
        inspect_card.grid(row=1, column=0, sticky="nsew")

        self.inspect_notebook = ttk.Notebook(inspect_card)
        self.inspect_notebook.pack(fill="both", expand=True)

        self.ds_frame = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.ds_frame, text="  Queue / Stack State  ")

        self.ds_lbl = ttk.Label(self.ds_frame, text="Current State: Simulation Idle", style="CardTitle.TLabel")
        self.ds_lbl.pack(anchor="w", pady=(0, 4))

        self.ds_sub_lbl = ttk.Label(
            self.ds_frame,
            text="BFS Queue: FIFO (Front ➔ Rear)  |  DFS Stack: LIFO (Top ➔ Bottom)",
            style="CardSubtitle.TLabel"
        )
        self.ds_sub_lbl.pack(anchor="w", pady=(0, 6))

        self.ds_listbox = tk.Listbox(
            self.ds_frame,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            selectbackground=Theme.BG_SELECTED,
            selectforeground=Theme.ACCENT_BLUE,
            font=Theme.FONT_MONO,
            relief="solid",
            bd=1,
            height=7
        )
        self.ds_listbox.pack(fill="both", expand=True)

        self.adj_list_frame = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.adj_list_frame, text="  Adjacency List O(V+E)  ")

        adj_list_scroll = ttk.Scrollbar(self.adj_list_frame, orient="vertical")
        adj_list_scroll.pack(side="right", fill="y")

        self.adj_list_text = tk.Text(
            self.adj_list_frame,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_MONO,
            relief="solid",
            bd=1,
            yscrollcommand=adj_list_scroll.set,
            padx=6,
            pady=6
        )
        self.adj_list_text.pack(side="left", fill="both", expand=True)
        adj_list_scroll.config(command=self.adj_list_text.yview)

        self.adj_mat_frame = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.adj_mat_frame, text="  Adjacency Matrix O(V²)  ")

        adj_mat_scroll_y = ttk.Scrollbar(self.adj_mat_frame, orient="vertical")
        adj_mat_scroll_y.pack(side="right", fill="y")
        adj_mat_scroll_x = ttk.Scrollbar(self.adj_mat_frame, orient="horizontal")
        adj_mat_scroll_x.pack(side="bottom", fill="x")

        self.adj_mat_text = tk.Text(
            self.adj_mat_frame,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_MONO,
            relief="solid",
            bd=1,
            wrap="none",
            yscrollcommand=adj_mat_scroll_y.set,
            xscrollcommand=adj_mat_scroll_x.set,
            padx=6,
            pady=6
        )
        self.adj_mat_text.pack(side="left", fill="both", expand=True)
        adj_mat_scroll_y.config(command=self.adj_mat_text.yview)
        adj_mat_scroll_x.config(command=self.adj_mat_text.xview)

        self.compare_frame = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.compare_frame, text="  Route Comparison  ")

        self.compare_text = tk.Text(
            self.compare_frame,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_MONO,
            relief="solid",
            bd=1,
            padx=6,
            pady=6
        )
        self.compare_text.pack(fill="both", expand=True)

        self.comp_frame = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=8)
        self.inspect_notebook.add(self.comp_frame, text="  Complexity Specs  ")

        comp_content = (
            "==================================================\n"
            "  GRAPH ALGORITHMS COMPLEXITY ANALYSIS (CO5)\n"
            "==================================================\n\n"
            "1. BREADTH-FIRST SEARCH (BFS)\n"
            "   • Time Complexity:  O(V + E)\n"
            "   • Space Complexity: O(V) via FIFO Queue\n"
            "   • Guarantee:        Fewest hops in unweighted graph\n"
            "   • Traversal Order:  Level-by-level exploration\n\n"
            "2. DEPTH-FIRST SEARCH (DFS)\n"
            "   • Time Complexity:  O(V + E)\n"
            "   • Space Complexity: O(V) via LIFO Call Stack\n"
            "   • Guarantee:        Valid path reachability\n"
            "   • Traversal Order:  Deep branch exploration\n\n"
            "3. GRAPH REPRESENTATIONS\n"
            "   • Adjacency List:   Space O(V + E) — Optimal for sparse\n"
            "   • Adjacency Matrix: Space O(V²) — Fast edge lookup\n"
            "==================================================\n"
        )
        comp_txt = tk.Text(self.comp_frame, bg=Theme.BG_CARD, fg=Theme.TEXT_MAIN, font=Theme.FONT_MONO, relief="solid", bd=1)
        comp_txt.insert("1.0", comp_content)
        comp_txt.config(state="disabled")
        comp_txt.pack(fill="both", expand=True)

    def toggle_inspector(self):
        if self._inspector_visible:
            self.paned_window.forget(self.inspector_panel)
            self._inspector_visible = False
            self.btn_toggle_inspect.config(text="◫ Show Inspector")
        else:
            self.paned_window.add(self.inspector_panel, weight=1)
            self._inspector_visible = True
            self.btn_toggle_inspect.config(text="◫ Collapse Inspector")
        self.after(50, self.fit_to_view)

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        sx = wx * self.scale + self.offset_x
        sy = wy * self.scale + self.offset_y
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        wx = (sx - self.offset_x) / self.scale if self.scale != 0 else sx
        wy = (sy - self.offset_y) / self.scale if self.scale != 0 else sy
        return wx, wy

    def fit_to_view(self):
        if not self.graph.routers:
            self.scale = 1.0
            self.offset_x = 0.0
            self.offset_y = 0.0
            self.redraw_canvas()
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw <= 50 or ch <= 50:
            cw, ch = 700, 420

        xs = [r.x for r in self.graph.routers.values()]
        ys = [r.y for r in self.graph.routers.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        world_pad = 70.0
        world_w = max(1.0, (max_x - min_x) + 2 * world_pad)
        world_h = max(1.0, (max_y - min_y) + 2 * world_pad)

        canvas_margin = 40.0
        avail_w = max(100.0, cw - 2 * canvas_margin)
        avail_h = max(100.0, ch - 2 * canvas_margin)

        scale_x = avail_w / world_w
        scale_y = avail_h / world_h
        new_scale = min(scale_x, scale_y)
        new_scale = max(0.35, min(2.5, new_scale))

        mid_wx = (min_x + max_x) / 2.0
        mid_wy = (min_y + max_y) / 2.0

        self.scale = new_scale
        self.offset_x = (cw / 2.0) - (mid_wx * self.scale)
        self.offset_y = (ch / 2.0) - (mid_wy * self.scale)

        self.redraw_canvas()

    def zoom(self, factor: float, center_x: Optional[float] = None, center_y: Optional[float] = None):
        old_scale = self.scale
        new_scale = max(0.25, min(3.5, self.scale * factor))
        if old_scale == new_scale:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        cx = center_x if center_x is not None else (cw / 2.0)
        cy = center_y if center_y is not None else (ch / 2.0)

        wx, wy = self.screen_to_world(cx, cy)
        self.scale = new_scale
        self.offset_x = cx - wx * self.scale
        self.offset_y = cy - wy * self.scale

        self.redraw_canvas()

    def zoom_in(self):
        self.zoom(1.2)

    def zoom_out(self):
        self.zoom(1.0 / 1.2)

    def reset_zoom(self):
        self.fit_to_view()

    def _on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom(1.15, event.x, event.y)
        elif event.delta < 0:
            self.zoom(1.0 / 1.15, event.x, event.y)

    def _on_canvas_configure(self, event):
        self.redraw_canvas()

    def _on_canvas_press_1(self, event):
        items = self.canvas.find_overlapping(event.x - 8, event.y - 8, event.x + 8, event.y + 8)
        clicked_router_id = None

        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("node_"):
                    clicked_router_id = tag.replace("node_", "")
                    break
            if clicked_router_id:
                break

        if clicked_router_id:
            self._drag_data["mode"] = "node"
            self._drag_data["router_id"] = clicked_router_id
            self._drag_data["start_x"] = event.x
            self._drag_data["start_y"] = event.y
            self.selected_router_id = clicked_router_id
            self.redraw_canvas()
            self.console.log(f"Selected router '{clicked_router_id}' ({self.graph.routers[clicked_router_id].name}).", "info")
        else:
            self._drag_data["mode"] = "pan"
            self._drag_data["start_x"] = event.x
            self._drag_data["start_y"] = event.y
            self.canvas.config(cursor="fleur")

    def _on_canvas_drag_1(self, event):
        if self._drag_data["mode"] == "node":
            rid = self._drag_data["router_id"]
            if rid and rid in self.graph.routers:
                r = self.graph.routers[rid]
                wx, wy = self.screen_to_world(event.x, event.y)
                r.x = wx
                r.y = wy
                self.redraw_canvas()
        elif self._drag_data["mode"] == "pan":
            dx = event.x - self._drag_data["start_x"]
            dy = event.y - self._drag_data["start_y"]
            self._drag_data["start_x"] = event.x
            self._drag_data["start_y"] = event.y
            self.offset_x += dx
            self.offset_y += dy
            self.redraw_canvas()

    def _on_canvas_release_1(self, event):
        self._drag_data["mode"] = None
        self._drag_data["router_id"] = None
        self.canvas.config(cursor="arrow")

    def _on_pan_start(self, event):
        self._drag_data["mode"] = "pan"
        self._drag_data["start_x"] = event.x
        self._drag_data["start_y"] = event.y
        self.canvas.config(cursor="fleur")

    def _on_pan_drag(self, event):
        dx = event.x - self._drag_data["start_x"]
        dy = event.y - self._drag_data["start_y"]
        self._drag_data["start_x"] = event.x
        self._drag_data["start_y"] = event.y
        self.offset_x += dx
        self.offset_y += dy
        self.redraw_canvas()

    def redraw_canvas(self, step: Optional[SimulationStep] = None):
        self.canvas.delete("all")

        visited_nodes = set(step.visited_elements) if step else set()
        current_node = step.current_element if step else None
        final_path = set(self.current_result.path) if (self.current_result and self.current_result.success) else set()

        for u, v, w in self.graph.get_edges():
            if u not in self.graph.routers or v not in self.graph.routers:
                continue

            ru = self.graph.routers[u]
            rv = self.graph.routers[v]

            sx1, sy1 = self.world_to_screen(ru.x, ru.y)
            sx2, sy2 = self.world_to_screen(rv.x, rv.y)

            edge_color = Theme.BORDER_COLOR
            width = max(1, int(2 * self.scale))

            if u in final_path and v in final_path:
                edge_color = Theme.COLOR_SUCCESS
                width = max(2, int(4 * self.scale))
            elif step and step.active_path and len(step.active_path) >= 2:
                p = step.active_path
                if (u == p[0] and v == p[1]) or (v == p[0] and u == p[1]):
                    edge_color = Theme.COLOR_EXPLORE
                    width = max(2, int(4 * self.scale))

            self.canvas.create_line(sx1, sy1, sx2, sy2, fill=edge_color, width=width, tags="edge")

        base_radius = 22.0
        r_screen = max(15.0, min(36.0, base_radius * self.scale))

        for rid, r in self.graph.routers.items():
            sx, sy = self.world_to_screen(r.x, r.y)

            fill_color = Theme.BG_CARD
            outline_color = Theme.ACCENT_BLUE
            text_color = Theme.TEXT_MAIN
            node_width = 2

            if not r.is_online:
                fill_color = Theme.BG_CARD_ALT
                outline_color = Theme.COLOR_OFFLINE
                text_color = Theme.TEXT_DISABLED
            elif rid == self.source_id:
                fill_color = Theme.ACCENT_CYAN
                outline_color = Theme.ACCENT_BLUE
                text_color = "#FFFFFF"
                node_width = 3
            elif rid == self.dest_id:
                fill_color = Theme.COLOR_SUCCESS
                outline_color = "#166534"
                text_color = "#FFFFFF"
                node_width = 3
            elif rid == current_node:
                fill_color = Theme.COLOR_EXPLORE
                outline_color = "#B45309"
                text_color = "#FFFFFF"
                node_width = 3
            elif rid in final_path:
                fill_color = Theme.COLOR_SUCCESS
                outline_color = "#166534"
                text_color = "#FFFFFF"
            elif rid in visited_nodes:
                fill_color = Theme.BG_SELECTED
                outline_color = Theme.ACCENT_BLUE
                text_color = Theme.ACCENT_BLUE

            if rid == self.selected_router_id:
                sel_pad = 6.0
                self.canvas.create_oval(
                    sx - (r_screen + sel_pad), sy - (r_screen + sel_pad),
                    sx + (r_screen + sel_pad), sy + (r_screen + sel_pad),
                    outline=Theme.ACCENT_BLUE,
                    width=2,
                    dash=(3, 2),
                    tags="selection_ring"
                )

            node_tag = f"node_{rid}"
            self.canvas.create_oval(
                sx - r_screen, sy - r_screen,
                sx + r_screen, sy + r_screen,
                fill=fill_color,
                outline=outline_color,
                width=node_width,
                tags=("node", node_tag)
            )

            font_size = max(8, min(13, int(10 * self.scale)))
            self.canvas.create_text(
                sx, sy,
                text=r.id,
                font=(Theme.FONT_FAMILY, font_size, "bold"),
                fill=text_color,
                tags=("node", node_tag)
            )

            sub_font_size = max(7, min(10, int(8 * self.scale)))
            sub_y = sy + r_screen + max(8.0, 12.0 * self.scale)
            name_text = r.name if r.is_online else f"{r.name} (OFFLINE)"
            name_color = Theme.TEXT_MUTED if r.is_online else Theme.COLOR_ERROR

            self.canvas.create_text(
                sx, sub_y,
                text=name_text,
                font=(Theme.FONT_FAMILY, sub_font_size, "normal"),
                fill=name_color,
                tags=("node", node_tag)
            )

        self._draw_legend()

    def _draw_legend(self):
        ch = self.canvas.winfo_height()
        if ch <= 120:
            return

        lx, ly = 12, ch - 50
        box_w, box_h = 560, 40

        self.canvas.create_rectangle(
            lx, ly, lx + box_w, ly + box_h,
            fill=Theme.BG_CARD,
            outline=Theme.BORDER_COLOR,
            width=1,
            tags="legend"
        )

        items = [
            ("Source", Theme.ACCENT_CYAN, "#FFFFFF"),
            ("Destination", Theme.COLOR_SUCCESS, "#FFFFFF"),
            ("Explored", Theme.COLOR_EXPLORE, "#FFFFFF"),
            ("Visited", Theme.BG_SELECTED, Theme.ACCENT_BLUE),
            ("Final Route", Theme.COLOR_SUCCESS, "#FFFFFF"),
            ("Offline", Theme.BG_CARD_ALT, Theme.COLOR_OFFLINE),
            ("Selected", "#FFFFFF", Theme.ACCENT_BLUE)
        ]

        curr_x = lx + 12
        for label, fill, outline in items:
            self.canvas.create_oval(
                curr_x, ly + 14, curr_x + 12, ly + 26,
                fill=fill, outline=outline, width=2, tags="legend"
            )
            curr_x += 16
            self.canvas.create_text(
                curr_x, ly + 20,
                text=label,
                font=Theme.FONT_SMALL,
                fill=Theme.TEXT_MAIN,
                anchor="w",
                tags="legend"
            )
            curr_x += (len(label) * 7 + 14)

    def run_simulation(self):
        if not self.source_id or not self.dest_id:
            messagebox.showwarning("Routing Error", "Please select valid Source and Destination routers.")
            return

        if self.source_id not in self.graph.routers or self.dest_id not in self.graph.routers:
            messagebox.showerror("Routing Error", "Selected routers no longer exist in topology.")
            return

        if not self.graph.routers[self.source_id].is_online:
            messagebox.showwarning("Offline Source", f"Source router '{self.source_id}' is offline. Toggle status to enable routing.")
            return

        if not self.graph.routers[self.dest_id].is_online:
            messagebox.showwarning("Offline Destination", f"Destination router '{self.dest_id}' is offline. Toggle status to enable routing.")
            return

        if self.source_id == self.dest_id:
            messagebox.showinfo("Identical Endpoints", f"Source and Destination are the same router '{self.source_id}' (0 hops required).")
            return

        alg_type = self.alg_combo.get()
        if "BFS" in alg_type:
            result = bfs_path(self.graph, self.source_id, self.dest_id)
        else:
            result = dfs_path(self.graph, self.source_id, self.dest_id)

        self.current_result = result
        self.control_bar.set_running_state(is_running=True)

        self.sim_service.load_simulation(
            result=result,
            on_step=self._on_sim_step,
            on_complete=self._on_sim_complete
        )
        self.sim_service.play()

    def reset_simulation(self):
        self.sim_service.stop()
        if self._packet_timer:
            try:
                self.after_cancel(self._packet_timer)
            except Exception:
                pass
            self._packet_timer = None
        self.canvas.delete("packet")

        self.current_result = None
        self.control_bar.reset_step_indicator()
        self.control_bar.set_running_state(is_running=False)

        self.ds_listbox.delete(0, "end")
        self.ds_lbl.config(text="Current State: Simulation Idle")
        self.card_hops.update_value("--")
        self.card_steps.update_value("0")

        self.redraw_canvas()
        self.update_stats()
        self.update_representations()

    def _on_sim_step(self, step: SimulationStep, step_num: int, total_steps: int):
        self.redraw_canvas(step=step)
        self.console.log(step.message, level="explore" if step.step_type in ["enqueue", "push"] else "info")

        self.ds_listbox.delete(0, "end")
        ds_type = "Queue (FIFO)" if "BFS" in self.alg_combo.get() else "Stack (LIFO)"
        self.ds_lbl.config(text=f"Live {ds_type} State (Step {step_num}/{total_steps}):")

        if step.data_structure_state:
            for idx, item in enumerate(step.data_structure_state):
                order_tag = "Front" if idx == 0 and "BFS" in self.alg_combo.get() else ("Top" if idx == len(step.data_structure_state) - 1 and "DFS" in self.alg_combo.get() else f"[{idx}]")
                self.ds_listbox.insert("end", f"  {order_tag:>6} ➔  Router '{item}'")

        self.card_steps.update_value(str(step_num))
        self.control_bar.update_step_indicator(step_num, total_steps)

    def _on_sim_complete(self):
        self.control_bar.set_running_state(is_running=False)
        if not self.current_result:
            return

        res = self.current_result
        if res.success:
            self.console.log(res.message, "success")
            hops_count = len(res.path) - 1
            self.card_hops.update_value(f"{hops_count} hops", Theme.COLOR_SUCCESS)
            self.card_reach.update_value("Reachable", Theme.COLOR_SUCCESS)

            self.animate_packet_transmission(res.path)
        else:
            self.console.log(res.message, "error")
            self.card_hops.update_value("Unreachable", Theme.COLOR_ERROR)
            self.card_reach.update_value("Unreachable", Theme.COLOR_ERROR)

    def animate_packet_transmission(self, path: List[str]):
        if len(path) < 2:
            return

        coords_list = []
        for rid in path:
            if rid in self.graph.routers:
                r = self.graph.routers[rid]
                coords_list.append((r.x, r.y))

        if len(coords_list) < 2:
            return

        frames_per_hop = 16
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

        self._packet_frames = all_frames
        self._packet_frame_idx = 0

        self._draw_next_packet_frame()

    def _draw_next_packet_frame(self):
        if self._packet_frame_idx >= len(self._packet_frames):
            self.canvas.delete("packet")
            self.console.log(f"Packet reached destination '{self.dest_id}' successfully.", "success")
            return

        wx, wy = self._packet_frames[self._packet_frame_idx]
        sx, sy = self.world_to_screen(wx, wy)

        self.canvas.delete("packet")
        p_radius = max(6.0, 9.0 * self.scale)

        self.canvas.create_oval(
            sx - p_radius, sy - p_radius,
            sx + p_radius, sy + p_radius,
            fill=Theme.COLOR_PACKET,
            outline="#FFFFFF",
            width=2,
            tags="packet"
        )

        self._packet_frame_idx += 1
        self._packet_timer = self.after(35, self._draw_next_packet_frame)

    def add_router_dialog(self):
        dlg = AddRouterDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            rid, rname = dlg.result
            cw = self.canvas.winfo_width() / 2.0
            ch = self.canvas.winfo_height() / 2.0
            cwx, cwy = self.screen_to_world(cw, ch)

            cwx += random.randint(-40, 40)
            cwy += random.randint(-40, 40)

            if self.graph.add_router(Router(rid, rname, cwx, cwy)):
                self.update_comboboxes()
                self.selected_router_id = rid
                self.redraw_canvas()
                self.update_stats()
                self.update_representations()
                self.console.log(f"Added router '{rid}' ({rname}).", "info")
            else:
                messagebox.showerror("Duplicate Router", f"Router ID '{rid}' already exists.")

    def delete_selected_router(self):
        rid = self.selected_router_id or self.source_id
        if not rid or rid not in self.graph.routers:
            messagebox.showinfo("No Selection", "Please click on a router to select it first.")
            return

        if len(self.graph.routers) <= 2:
            messagebox.showwarning("Minimum Routers", "Cannot delete. Graph must have at least 2 routers.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete router '{rid}' ({self.graph.routers[rid].name}) and its links?"
        )
        if confirm:
            self.graph.remove_router(rid)
            self.selected_router_id = None
            self.update_comboboxes()
            self.reset_simulation()
            self.fit_to_view()
            self.console.log(f"Deleted router '{rid}'.", "warning")

    def add_link_dialog(self):
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
                self.update_stats()
                self.update_representations()
                self.console.log(f"Created link between '{u}' and '{v}'.", "info")
            else:
                messagebox.showerror("Link Error", "Could not create link.")

    def remove_link_dialog(self):
        edges = self.graph.get_edges()
        if not edges:
            messagebox.showinfo("No Links", "Current network topology has no links to remove.")
            return

        dlg = RemoveLinkDialog(self, edges)
        self.wait_window(dlg)
        if dlg.result:
            u, v = dlg.result
            if self.graph.remove_edge(u, v):
                self.redraw_canvas()
                self.update_stats()
                self.update_representations()
                self.console.log(f"Removed link between '{u}' and '{v}'.", "warning")

    def toggle_selected_offline(self):
        rid = self.selected_router_id or self.source_id
        if not rid or rid not in self.graph.routers:
            messagebox.showinfo("No Selection", "Please click on a router to select it first.")
            return

        r = self.graph.routers[rid]
        new_status = not r.is_online
        self.graph.set_router_online_status(rid, new_status)
        self.reset_simulation()
        status_str = "ONLINE" if new_status else "OFFLINE"
        level = "info" if new_status else "warning"
        self.console.log(f"Router '{rid}' state toggled to {status_str}.", level)

    def open_route_comparison(self):
        if not self.source_id or not self.dest_id:
            messagebox.showwarning("Selection Required", "Please choose valid Source and Destination routers.")
            return

        bfs_res = bfs_path(self.graph, self.source_id, self.dest_id)
        dfs_res = dfs_path(self.graph, self.source_id, self.dest_id)

        dlg = RouteComparisonDialog(self, bfs_res, dfs_res, self.source_id, self.dest_id)
        self.wait_window(dlg)

    def _on_preset_selected(self, event=None):
        val = self.preset_combo.get()
        if "Default" in val:
            self.load_preset("default")
        elif "Small" in val:
            self.load_preset("small")
        elif "Medium" in val:
            self.load_preset("medium")
        elif "Disconnected" in val:
            self.load_preset("disconnected")
        elif "Alternate" in val:
            self.load_preset("alternate")
        elif "Offline" in val:
            self.load_preset("offline")
        elif "Random" in val:
            self.load_preset("random")

    def load_preset(self, preset_name: str):
        self.graph.clear()

        if preset_name == "default":
            self.graph = Graph.create_default_topology()
            msg = "Loaded Default 6-Node Balanced Topology."
        elif preset_name == "small":
            self.graph = Graph.create_small_connected()
            msg = "Loaded Small 5-Node Ring Topology."
        elif preset_name == "medium":
            self.graph = Graph.create_medium_network()
            msg = "Loaded Medium 9-Node Hierarchical Network."
        elif preset_name == "disconnected":
            self.graph = Graph.create_disconnected_network()
            msg = "Loaded Disconnected Partitions (2 Separate Components)."
        elif preset_name == "alternate":
            self.graph = Graph.create_alternate_routes()
            msg = "Loaded Alternate Routes Scenario (BFS Shortest 2 Hops vs DFS 4 Hops)."
        elif preset_name == "offline":
            self.graph = Graph.create_offline_scenario()
            msg = "Loaded Offline Scenario (Primary Router R2 Down, Reroutes via R3)."
        elif preset_name == "random":
            self.graph = Graph.create_default_topology()
            self._generate_random_topology()
            msg = "Generated Random Connected Network."
        else:
            self.graph = Graph.create_default_topology()
            msg = "Loaded default topology."

        self.update_comboboxes()
        self.reset_simulation()
        self.fit_to_view()
        self.console.log(msg, "info")

    def _generate_random_topology(self):
        self.graph.clear()
        names = ["Core", "Dist", "Edge", "Gate", "Hub", "Spine", "Leaf", "Border"]
        count = random.randint(6, 8)
        coords = [
            (110, 100), (270, 80), (450, 100), (590, 80),
            (130, 270), (300, 290), (470, 270), (620, 290)
        ]

        for i in range(count):
            rid = f"R{i+1}"
            rname = f"{names[i % len(names)]} R{i+1}"
            cx, cy = coords[i]
            self.graph.add_router(Router(rid, rname, cx, cy))

        r_ids = list(self.graph.routers.keys())
        for i in range(len(r_ids) - 1):
            self.graph.add_edge(r_ids[i], r_ids[i + 1])

        for _ in range(random.randint(2, 4)):
            u, v = random.sample(r_ids, 2)
            self.graph.add_edge(u, v)

    def save_topology_dialog(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Network Topology"
        )
        if filepath:
            try:
                self.graph.save_to_file(filepath)
                self.console.log(f"Topology saved successfully to '{filepath}'.", "success")
                messagebox.showinfo("Save Topology", "Network topology saved successfully!")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save topology: {e}")

    def load_topology_dialog(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Network Topology"
        )
        if filepath:
            try:
                g = Graph.load_from_file(filepath)
                if not g.routers:
                    messagebox.showerror("Invalid File", "File contains no routers.")
                    return
                self.graph = g
                self.update_comboboxes()
                self.reset_simulation()
                self.fit_to_view()
                self.console.log(f"Loaded topology from '{filepath}'.", "success")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load topology file: {e}")

    def update_comboboxes(self):
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

    def update_stats(self):
        self.card_nodes.update_value(str(len(self.graph.routers)))
        self.card_edges.update_value(str(len(self.graph.get_edges())))

        comps = self.graph.get_connected_components()
        self.card_comp.update_value(str(len(comps)))

        if self.source_id and self.dest_id and self.source_id in self.graph.routers and self.dest_id in self.graph.routers:
            reachable = self.graph.is_reachable(self.source_id, self.dest_id)
            if reachable:
                self.card_reach.update_value("Reachable", Theme.COLOR_SUCCESS)
            else:
                self.card_reach.update_value("Unreachable", Theme.COLOR_ERROR)
        else:
            self.card_reach.update_value("Ready", Theme.TEXT_MUTED)

    def update_representations(self):
        adj_dict = self.graph.get_adjacency_list_view()
        self.adj_list_text.delete("1.0", "end")
        for r_id, nbrs in adj_dict.items():
            status = "Online" if self.graph.routers[r_id].is_online else "OFFLINE"
            nbr_str = ", ".join(nbrs) if nbrs else "None (Isolated)"
            self.adj_list_text.insert("end", f"{r_id:<4} ({status:<7}) ➔ [{nbr_str}]\n")

        nodes, matrix = self.graph.get_adjacency_matrix_view()
        self.adj_mat_text.delete("1.0", "end")
        if nodes:
            header = "     " + " ".join(f"{n:>4}" for n in nodes) + "\n"
            self.adj_mat_text.insert("end", header)
            self.adj_mat_text.insert("end", "     " + "-" * (len(nodes) * 5) + "\n")
            for i, row in enumerate(matrix):
                row_str = f"{nodes[i]:<4}|" + " ".join(f"{val:>4}" for val in row) + "\n"
                self.adj_mat_text.insert("end", row_str)

        self.compare_text.delete("1.0", "end")
        if self.source_id and self.dest_id:
            bfs_r = bfs_path(self.graph, self.source_id, self.dest_id)
            dfs_r = dfs_path(self.graph, self.source_id, self.dest_id)
            comps = self.graph.get_connected_components()

            comp_summary = (
                f"Source: {self.source_id}  |  Destination: {self.dest_id}\n"
                f"---------------------------------------------------\n"
                f"BFS Result:\n"
                f"  • Path:      {' -> '.join(bfs_r.path) if bfs_r.success else 'Unreachable'}\n"
                f"  • Hops:      {len(bfs_r.path)-1 if bfs_r.success else '--'} (Guaranteed Fewest Hops)\n"
                f"  • Visited:   {len(bfs_r.visited_order)} vertices\n"
                f"  • Steps:     {bfs_r.total_steps} execution steps\n\n"
                f"DFS Result:\n"
                f"  • Path:      {' -> '.join(dfs_r.path) if dfs_r.success else 'Unreachable'}\n"
                f"  • Hops:      {len(dfs_r.path)-1 if dfs_r.success else '--'} (Depth First Path)\n"
                f"  • Visited:   {len(dfs_r.visited_order)} vertices\n"
                f"  • Steps:     {dfs_r.total_steps} execution steps\n\n"
                f"Network Partitions: {len(comps)} connected component(s)\n"
            )
            self.compare_text.insert("end", comp_summary)

    def _build_maze_tab(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        bar = CardFrame(parent, padding=8)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ttk.Button(bar, text="▶ Run Grid BFS (Shortest)", style="Primary.TButton", command=self._run_maze_bfs).pack(side="left", padx=4)
        ttk.Button(bar, text="▶ Run Grid DFS (Exploration)", command=self._run_maze_dfs).pack(side="left", padx=4)
        ttk.Button(bar, text="↺ Reset Grid Maze", command=self._reset_maze).pack(side="left", padx=4)

        self.maze_status_lbl = ttk.Label(
            bar,
            text="Click cells to toggle walls (Dark Slate). Cyan = Start, Red = End, Green = Shortest Route.",
            style="Card.TLabel",
            font=Theme.FONT_SMALL
        )
        self.maze_status_lbl.pack(side="right", padx=8)

        maze_card = CardFrame(parent, padding=4)
        maze_card.grid(row=1, column=0, sticky="nsew")

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

        self.maze_canvas = tk.Canvas(maze_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.maze_canvas.pack(fill="both", expand=True)
        self.maze_canvas.bind("<Button-1>", self._on_maze_click)

        self._draw_maze()

    def _draw_maze(self, path=None, visited=None):
        self.maze_canvas.delete("all")
        rows = len(self.maze_grid)
        cols = len(self.maze_grid[0])
        cw, ch = 56, 56

        visited_set = set(visited) if visited else set()
        path_set = set(path) if path else set()

        for r in range(rows):
            for c in range(cols):
                x1, y1 = c * cw + 24, r * ch + 24
                x2, y2 = x1 + cw, y1 + ch

                fill = Theme.BG_CARD
                outline = Theme.BORDER_COLOR
                txt_color = Theme.TEXT_MUTED

                if self.maze_grid[r][c] == 1:
                    fill = "#1E293B"
                    txt_color = "#94A3B8"
                elif (r, c) == self.maze_start:
                    fill = Theme.ACCENT_CYAN
                    txt_color = "#FFFFFF"
                elif (r, c) == self.maze_end:
                    fill = Theme.COLOR_ERROR
                    txt_color = "#FFFFFF"
                elif (r, c) in path_set:
                    fill = Theme.COLOR_SUCCESS
                    txt_color = "#FFFFFF"
                elif (r, c) in visited_set:
                    fill = Theme.BG_SELECTED
                    txt_color = Theme.ACCENT_BLUE

                self.maze_canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1)
                self.maze_canvas.create_text(x1 + cw / 2, y1 + ch / 2, text=f"({r},{c})", fill=txt_color, font=Theme.FONT_SMALL)

    def _on_maze_click(self, event):
        cw, ch = 56, 56
        c = (event.x - 24) // cw
        r = (event.y - 24) // ch

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
            self.maze_status_lbl.config(text="No reachable path in grid maze.")

    def _run_maze_dfs(self):
        res = grid_maze_dfs(self.maze_grid, self.maze_start, self.maze_end)
        if res.success:
            self._draw_maze(path=res.path, visited=res.visited_order)
            self.maze_status_lbl.config(text=f"Grid DFS Path Explored ({len(res.path)-1} steps).")
        else:
            self.maze_status_lbl.config(text="No reachable path in grid maze.")

    def _reset_maze(self):
        self._draw_maze()
        self.maze_status_lbl.config(text="Grid maze reset.")
