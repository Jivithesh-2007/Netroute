import math
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Tuple, Optional, Any
from theme import Theme, CardFrame, StatCard, ConsoleLog, ControlBar, ZoomPanToolbar, SimulationService
from network import Graph, SimulationStep, SimulationResult, bfs_path, dfs_path, validate_router_id

class AddRouterDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add New Router")
        self.geometry("320x180")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_APP)
        self.result = None

        frame = CardFrame(self, padding=12)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        ttk.Label(frame, text="Router ID (e.g. R7):", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.id_entry = ttk.Entry(frame)
        self.id_entry.pack(fill="x", pady=(0, 6))

        ttk.Label(frame, text="Display Name:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.name_entry = ttk.Entry(frame)
        self.name_entry.pack(fill="x", pady=(0, 10))

        btn_box = ttk.Frame(frame, style="Card.TFrame")
        btn_box.pack(fill="x", side="bottom")
        ttk.Button(btn_box, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_box, text="Add Router", style="Primary.TButton", command=self._on_submit).pack(side="right")

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
    def __init__(self, parent, router_ids: List[str]):
        super().__init__(parent)
        self.title("Add Network Connection")
        self.geometry("320x180")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_APP)
        self.result = None

        frame = CardFrame(self, padding=12)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        ttk.Label(frame, text="Endpoint Router A:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.cb_u = ttk.Combobox(frame, values=router_ids, state="readonly")
        self.cb_u.pack(fill="x", pady=(0, 6))
        if router_ids:
            self.cb_u.set(router_ids[0])

        ttk.Label(frame, text="Endpoint Router B:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.cb_v = ttk.Combobox(frame, values=router_ids, state="readonly")
        self.cb_v.pack(fill="x", pady=(0, 10))
        if len(router_ids) > 1:
            self.cb_v.set(router_ids[1])

        btn_box = ttk.Frame(frame, style="Card.TFrame")
        btn_box.pack(fill="x", side="bottom")
        ttk.Button(btn_box, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_box, text="Connect", style="Primary.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()

    def _on_submit(self):
        u = self.cb_u.get().strip()
        v = self.cb_v.get().strip()
        if not u or not v or u == v:
            messagebox.showerror("Invalid Selection", "Please select two distinct routers.", parent=self)
            return
        self.result = (u, v)
        self.destroy()

class NetworkSimulatorView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app
        self.graph = Graph(directed=False)
        self.sim_service = SimulationService(root_widget=self)

        self.source_id = "R1"
        self.dest_id = "R6"
        self.selected_router = None
        self.current_result: Optional[SimulationResult] = None

        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self._drag_data = {"start_x": 0, "start_y": 0, "router": None}

        self._packet_timer = None
        self._packet_frames: List[Tuple[float, float]] = []
        self._packet_frame_idx = 0

        self.explored_nodes = set()
        self.visited_nodes = set()
        self.visited_order = []
        self.active_path = []
        self.current_node = None

        self._build_ui()
        self.load_preset("sample")
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

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        main_col = ttk.Frame(paned, style="TFrame")
        paned.add(main_col, weight=3)
        main_col.grid_rowconfigure(2, weight=1)
        main_col.grid_columnconfigure(0, weight=1)

        side_col = ttk.Frame(paned, style="TFrame", width=360)
        paned.add(side_col, weight=1)
        side_col.grid_rowconfigure(2, weight=1)
        side_col.grid_columnconfigure(0, weight=1)

        top_ctrl = CardFrame(main_col, padding=(8, 6))
        top_ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        ttk.Label(top_ctrl, text="Src:", style="Card.TLabel").pack(side="left", padx=(2, 2))
        self.cb_src = ttk.Combobox(top_ctrl, width=5, state="readonly")
        self.cb_src.pack(side="left", padx=2)
        self.cb_src.bind("<<ComboboxSelected>>", self._on_endpoint_change)

        ttk.Label(top_ctrl, text="Dst:", style="Card.TLabel").pack(side="left", padx=(6, 2))
        self.cb_dst = ttk.Combobox(top_ctrl, width=5, state="readonly")
        self.cb_dst.pack(side="left", padx=2)
        self.cb_dst.bind("<<ComboboxSelected>>", self._on_endpoint_change)

        ttk.Button(top_ctrl, text="Run BFS (Shortest)", style="Primary.TButton", command=self.run_bfs).pack(side="left", padx=4)
        ttk.Button(top_ctrl, text="Run DFS (Discover)", style="Purple.TButton", command=self.run_dfs).pack(side="left", padx=4)
        ttk.Button(top_ctrl, text="Animate Packet", style="Secondary.TButton", command=self.start_packet_animation).pack(side="left", padx=4)

        self.zoom_toolbar = ZoomPanToolbar(
            top_ctrl,
            on_zoom_in=lambda: self._zoom(1.15),
            on_zoom_out=lambda: self._zoom(0.85),
            on_fit_view=self.fit_to_view,
            on_reset_zoom=self._reset_zoom
        )
        self.zoom_toolbar.pack(side="right")

        self.banner = CardFrame(main_col, padding=(10, 6))
        self.banner.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        self.banner.grid_columnconfigure(1, weight=1)

        self.lbl_banner_algo = tk.Label(
            self.banner, text="READY", font=Theme.FONT_SMALL_BOLD,
            bg=Theme.BG_SELECTED, fg=Theme.PRIMARY, padx=8, pady=3
        )
        self.lbl_banner_algo.grid(row=0, column=0, rowspan=2, padx=(0, 10))

        lbl_t_hdr = tk.Label(self.banner, text="Traversal Order:", font=Theme.FONT_SMALL_BOLD, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        lbl_t_hdr.grid(row=0, column=1, sticky="w")
        self.lbl_traversal = tk.Label(self.banner, text="None (Click 'Run BFS' or 'Run DFS')", font=Theme.FONT_BOLD, bg=Theme.BG_CARD, fg=Theme.PRIMARY)
        self.lbl_traversal.grid(row=0, column=2, sticky="w", padx=(6, 0))

        lbl_r_hdr = tk.Label(self.banner, text="Discovered Path:", font=Theme.FONT_SMALL_BOLD, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        lbl_r_hdr.grid(row=1, column=1, sticky="w")
        self.lbl_route = tk.Label(self.banner, text="None", font=Theme.FONT_BOLD, bg=Theme.BG_CARD, fg=Theme.SUCCESS)
        self.lbl_route.grid(row=1, column=2, sticky="w", padx=(6, 0))

        canvas_card = CardFrame(main_col, padding=0)
        canvas_card.grid(row=2, column=0, sticky="nsew")
        canvas_card.grid_rowconfigure(0, weight=1)
        canvas_card.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_card,
            bg="#FFFFFF",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<ButtonPress-2>", self._on_pan_press)
        self.canvas.bind("<B2-Motion>", self._on_pan_drag)
        self.canvas.bind("<ButtonPress-3>", self._on_pan_press)
        self.canvas.bind("<B3-Motion>", self._on_pan_drag)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom(1.1))
        self.canvas.bind("<Button-5>", lambda e: self._zoom(0.9))

        bottom_bar = ttk.Frame(main_col, style="TFrame")
        bottom_bar.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        self.control_bar = ControlBar(
            bottom_bar,
            on_play=self.sim_service.play,
            on_pause=self.sim_service.pause,
            on_step=self.sim_service.step_forward,
            on_reset=self.reset_simulation,
            on_speed_change=self.sim_service.set_speed
        )
        self.control_bar.pack(fill="x")

        stats_row = ttk.Frame(side_col, style="TFrame")
        stats_row.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        stats_row.grid_columnconfigure(0, weight=1)
        stats_row.grid_columnconfigure(1, weight=1)

        self.stat_hops = StatCard(stats_row, title="Path Hops", value="0", subtitle="Optimal: -", color=Theme.SUCCESS, height=75)
        self.stat_hops.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.stat_visited = StatCard(stats_row, title="Explored", value="0", subtitle="Routers visited", color=Theme.PRIMARY, height=75)
        self.stat_visited.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        mgmt_card = CardFrame(side_col, padding=(8, 6))
        mgmt_card.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(mgmt_card, text="Topology & Device Controls", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))
        btn_r1 = ttk.Frame(mgmt_card, style="Card.TFrame")
        btn_r1.pack(fill="x", pady=2)
        ttk.Button(btn_r1, text="+ Router", style="Tool.TButton", command=self._add_router_dialog).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(btn_r1, text="- Remove", style="Tool.TButton", command=self._remove_selected_router).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(btn_r1, text="+ Link", style="Tool.TButton", command=self._add_link_dialog).pack(side="left", expand=True, fill="x", padx=1)

        btn_r2 = ttk.Frame(mgmt_card, style="Card.TFrame")
        btn_r2.pack(fill="x", pady=2)
        ttk.Button(btn_r2, text="Toggle Power", style="Tool.TButton", command=self._toggle_selected_power).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(btn_r2, text="Random Mesh", style="Tool.TButton", command=lambda: self.load_preset("random")).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(btn_r2, text="Reset Sample", style="Tool.TButton", command=lambda: self.load_preset("sample")).pack(side="left", expand=True, fill="x", padx=1)

        self.side_tabs = ttk.Notebook(side_col)
        self.side_tabs.grid(row=2, column=0, sticky="nsew")

        tab_traversal = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_traversal, text=" 📋 Traversal Order ")

        trav_frame = CardFrame(tab_traversal, padding=6)
        trav_frame.pack(fill="both", expand=True)
        trav_frame.grid_rowconfigure(1, weight=1)
        trav_frame.grid_columnconfigure(0, weight=1)

        self.lbl_trav_summary = tk.Label(
            trav_frame,
            text="Ordered Visited Sequence:",
            font=Theme.FONT_SMALL_BOLD,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            anchor="w"
        )
        self.lbl_trav_summary.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        t_cols = ("Step", "Router", "Action", "Level", "Role")
        self.tree_traversal = ttk.Treeview(trav_frame, columns=t_cols, show="headings", height=9)
        self.tree_traversal.heading("Step", text="#")
        self.tree_traversal.column("Step", width=36, anchor="center")
        self.tree_traversal.heading("Router", text="Router")
        self.tree_traversal.column("Router", width=62, anchor="center")
        self.tree_traversal.heading("Action", text="Action")
        self.tree_traversal.column("Action", width=120, anchor="w")
        self.tree_traversal.heading("Level", text="Hop/Depth")
        self.tree_traversal.column("Level", width=68, anchor="center")
        self.tree_traversal.heading("Role", text="Role")
        self.tree_traversal.column("Role", width=70, anchor="center")

        t_scroll = ttk.Scrollbar(trav_frame, orient="vertical", command=self.tree_traversal.yview)
        self.tree_traversal.configure(yscrollcommand=t_scroll.set)
        self.tree_traversal.grid(row=1, column=0, sticky="nsew")
        t_scroll.grid(row=1, column=1, sticky="ns")

        self.lbl_trav_path_footer = tk.Label(
            trav_frame,
            text="Path: None",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_CARD,
            fg=Theme.SUCCESS,
            anchor="w",
            wraplength=310,
            justify="left"
        )
        self.lbl_trav_path_footer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        tab_queue = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_queue, text=" ⚡ Queue/Stack ")
        q_frame = CardFrame(tab_queue, padding=8)
        q_frame.pack(fill="both", expand=True)

        ttk.Label(q_frame, text="Active Traversal Data Structure:", style="CardTitle.TLabel").pack(anchor="w")
        self.lbl_ds_title = ttk.Label(q_frame, text="Waiting for algorithm...", style="CardMuted.TLabel")
        self.lbl_ds_title.pack(anchor="w", pady=(2, 6))

        self.ds_listbox = tk.Listbox(q_frame, font=Theme.FONT_MONO, height=8, bg=Theme.BG_PANEL, bd=0, highlightthickness=1, highlightbackground=Theme.BORDER)
        self.ds_listbox.pack(fill="both", expand=True)

        tab_log = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_log, text=" 📜 Live Trace ")
        self.console = ConsoleLog(tab_log, height=8)
        self.console.pack(fill="both", expand=True)

        tab_repr = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_repr, text=" 📊 Matrices & List ")
        repr_frame = CardFrame(tab_repr, padding=6)
        repr_frame.pack(fill="both", expand=True)

        ttk.Label(repr_frame, text="Graph Representations (PrO-13 / PrO-14):", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))
        self.txt_repr = tk.Text(repr_frame, font=Theme.FONT_MONO, height=10, bg=Theme.BG_PANEL, bd=0, wrap="none")
        self.txt_repr.pack(fill="both", expand=True)

        self._draw_legend()

    def _draw_legend(self):
        legend = CardFrame(self.canvas, padding=(6, 4))
        items = [
            ("Normal", Theme.PRIMARY),
            ("Source", Theme.SECONDARY),
            ("Destination", Theme.SUCCESS),
            ("Exploring", Theme.WARNING),
            ("Visited", "#93C5FD"),
            ("Route", Theme.SUCCESS),
            ("Offline", Theme.COLOR_OFFLINE)
        ]
        for name, color in items:
            row = ttk.Frame(legend, style="Card.TFrame")
            row.pack(side="left", padx=4)
            dot = tk.Label(row, text="●", fg=color, bg=Theme.BG_CARD, font=("Helvetica", 10))
            dot.pack(side="left")
            lbl = tk.Label(row, text=name, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, font=Theme.FONT_SMALL)
            lbl.pack(side="left", padx=(1, 0))
        self.canvas.create_window(10, 10, window=legend, anchor="nw", tags="legend")

    def load_preset(self, preset_name: str):
        self.sim_service.stop()
        if preset_name == "sample":
            self.graph.load_sample_topology()
        else:
            self.graph.generate_random(6)

        nodes = sorted(self.graph.routers.keys())
        self.cb_src["values"] = nodes
        self.cb_dst["values"] = nodes
        if nodes:
            self.source_id = nodes[0]
            self.dest_id = nodes[-1] if len(nodes) > 1 else nodes[0]
            self.cb_src.set(self.source_id)
            self.cb_dst.set(self.dest_id)

        self.reset_simulation()
        self.fit_to_view()
        self._update_representations()
        self.console.clear()
        self.console.log(f"Loaded network topology preset: {preset_name.upper()} with {len(self.graph.routers)} routers.", "info")

    def _on_endpoint_change(self, event=None):
        self.source_id = self.cb_src.get()
        self.dest_id = self.cb_dst.get()
        self.reset_simulation()
        self.redraw()

    def run_bfs(self):
        self.reset_simulation()
        res = bfs_path(self.graph, self.source_id, self.dest_id)
        self.current_result = res
        self.lbl_banner_algo.config(text="BFS (SHORTEST HOP)", bg="#DBEAFE", fg=Theme.PRIMARY)
        self.lbl_ds_title.config(text="BFS FIFO Queue (Level-by-Level Discovery):")
        self.console.log(f"Starting BFS Shortest-Hop search: {self.source_id} -> {self.dest_id}", "info")
        self._load_and_run_simulation(res)

    def run_dfs(self):
        self.reset_simulation()
        res = dfs_path(self.graph, self.source_id, self.dest_id)
        self.current_result = res
        self.lbl_banner_algo.config(text="DFS (DEEP DISCOVERY)", bg="#DDD6FE", fg=Theme.PURPLE)
        self.lbl_ds_title.config(text="DFS LIFO Stack (Deep Branch Discovery):")
        self.console.log(f"Starting DFS Path search: {self.source_id} -> {self.dest_id}", "info")
        self._load_and_run_simulation(res)

    def _load_and_run_simulation(self, res: SimulationResult):
        self.side_tabs.select(0)
        self._populate_traversal_table(res)

        full_traversal = " → ".join(res.visited_order) if res.visited_order else "None"
        final_route = f"{' → '.join(res.path)} ({len(res.path)-1} hops)" if res.success else "No Route Available"

        self.lbl_traversal.config(text=full_traversal)
        self.lbl_route.config(text=final_route)
        self.lbl_trav_summary.config(text=f"Traversal Sequence: {full_traversal}")
        self.lbl_trav_path_footer.config(text=f"Discovered Path: {final_route}")
        self.stat_visited.update_val(str(len(res.visited_order)))
        if res.success:
            self.stat_hops.update_val(str(len(res.path) - 1), f"Time: {res.execution_time_ms:.2f}ms")

        def _on_step(step: SimulationStep, curr: int, total: int):
            self.control_bar.update_step(curr, total)
            self.current_node = step.current_element

            if step.visited_elements:
                self.visited_nodes = set(step.visited_elements)
                self.visited_order = list(step.visited_elements)
            elif step.extra_info and "visited_order" in step.extra_info:
                self.visited_order = list(step.extra_info["visited_order"])
                self.visited_nodes = set(self.visited_order)

            if step.step_type in ("enqueue", "push", "discover"):
                self.explored_nodes.add(step.current_element)
            if step.active_path:
                self.active_path = list(step.active_path)

            self.ds_listbox.delete(0, "end")
            if step.data_structure_state is not None:
                for idx, item in enumerate(step.data_structure_state):
                    self.ds_listbox.insert("end", f"[{idx}] {item}")

            lvl = "success" if step.step_type == "complete" else ("warning" if "not found" in step.message.lower() else "info")
            self.console.log(step.message, lvl)

            self.redraw()

        def _on_complete():
            self.control_bar.set_running_state(False)
            self.visited_order = list(res.visited_order)
            self.visited_nodes = set(self.visited_order)
            self.active_path = list(res.path) if res.success else []

            if res.success:
                self.console.log(f"Traversal complete: {full_traversal}", "info")
                self.console.log(f"Discovered path ({len(res.path)-1} hops): {' -> '.join(res.path)}", "success")
                self.start_packet_animation()
            else:
                self.console.log(res.message, "error")

            self.redraw()

        self.sim_service.load_simulation(res, _on_step, _on_complete)
        self.control_bar.set_running_state(True)
        self.sim_service.play()

    def _populate_traversal_table(self, res: SimulationResult):
        self.tree_traversal.delete(*self.tree_traversal.get_children())
        steps = res.extra_info.get("step_details", [])
        dist_map = res.extra_info.get("dist", {})

        if steps:
            for s in steps:
                self.tree_traversal.insert(
                    "", "end",
                    values=(s["order"], s["router"], s["action"], f"Hop {s['level']}", s["role"])
                )
        else:
            for i, rid in enumerate(res.visited_order):
                role = "Source" if rid == self.source_id else ("Destination" if rid == self.dest_id else "Visited")
                action = "Source Initialized" if i == 0 else ("Target Reached" if rid == self.dest_id else "Visited & Explored")
                lvl = f"Hop {dist_map.get(rid, '-')}"
                self.tree_traversal.insert("", "end", values=(i + 1, rid, action, lvl, role))

    def reset_simulation(self):
        self.sim_service.stop()
        if self._packet_timer:
            try:
                self.after_cancel(self._packet_timer)
            except Exception:
                pass
            self._packet_timer = None
        self.canvas.delete("packet")
        self.explored_nodes.clear()
        self.visited_nodes.clear()
        self.visited_order.clear()
        self.active_path.clear()
        self.current_node = None
        self.control_bar.update_step(0, 0)
        self.control_bar.set_running_state(False)
        self.stat_hops.update_val("0", "Optimal: -")
        self.stat_visited.update_val("0")
        self.ds_listbox.delete(0, "end")
        self.tree_traversal.delete(*self.tree_traversal.get_children())
        self.lbl_banner_algo.config(text="READY", bg=Theme.BG_SELECTED, fg=Theme.PRIMARY)
        self.lbl_traversal.config(text="None (Click 'Run BFS' or 'Run DFS')")
        self.lbl_route.config(text="None")
        self.lbl_trav_summary.config(text="Ordered Visited Sequence: None")
        self.lbl_trav_path_footer.config(text="Path: None")
        self.redraw()

    def start_packet_animation(self):
        if not self.current_result or not self.current_result.success or not self.current_result.path:
            messagebox.showinfo("No Path", "Run BFS or DFS to discover a valid path before animating packets.")
            return

        if self._packet_timer:
            try:
                self.after_cancel(self._packet_timer)
            except Exception:
                pass
            self._packet_timer = None
        self.canvas.delete("packet")

        path = self.current_result.path
        coords = []
        for rid in path:
            if rid in self.graph.routers:
                r = self.graph.routers[rid]
                sx, sy = self._to_screen(r.x, r.y)
                coords.append((sx, sy))

        if len(coords) < 2:
            return

        frames = []
        steps_per_segment = 12
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            for s in range(steps_per_segment):
                t = s / float(steps_per_segment)
                fx = x1 + t * (x2 - x1)
                fy = y1 + t * (y2 - y1)
                frames.append((fx, fy))
        frames.append(coords[-1])

        self._packet_frames = frames
        self._packet_frame_idx = 0
        self._step_packet_frame()

    def _step_packet_frame(self):
        if self._packet_frame_idx < len(self._packet_frames):
            x, y = self._packet_frames[self._packet_frame_idx]
            self.canvas.delete("packet")
            r = 7
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#F59E0B", outline="#FFFFFF", width=2, tags="packet")
            self._packet_frame_idx += 1
            self._packet_timer = self.after(30, self._step_packet_frame)
        else:
            self.canvas.delete("packet")
            self.console.log(f"Packet reached destination '{self.dest_id}' successfully!", "success")

    def _to_screen(self, x: float, y: float) -> Tuple[float, float]:
        return (x * self.scale + self.offset_x, y * self.scale + self.offset_y)

    def _to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        return ((sx - self.offset_x) / self.scale, (sy - self.offset_y) / self.scale)

    def fit_to_view(self):
        if not self.graph.routers:
            return
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)
        min_x = min(r.x for r in self.graph.routers.values())
        max_x = max(r.x for r in self.graph.routers.values())
        min_y = min(r.y for r in self.graph.routers.values())
        max_y = max(r.y for r in self.graph.routers.values())

        w = max(max_x - min_x, 100)
        h = max(max_y - min_y, 100)
        margin = 70.0
        scale_x = (cw - 2 * margin) / w
        scale_y = (ch - 2 * margin) / h
        self.scale = max(0.4, min(1.8, min(scale_x, scale_y)))
        self.offset_x = margin + (cw - 2 * margin - w * self.scale) / 2 - min_x * self.scale
        self.offset_y = margin + (ch - 2 * margin - h * self.scale) / 2 - min_y * self.scale
        self.redraw()

    def _zoom(self, factor: float):
        cw = self.canvas.winfo_width() / 2
        ch = self.canvas.winfo_height() / 2
        new_scale = max(0.3, min(3.0, self.scale * factor))
        self.offset_x = cw - (cw - self.offset_x) * (new_scale / self.scale)
        self.offset_y = ch - (ch - self.offset_y) * (new_scale / self.scale)
        self.scale = new_scale
        self.redraw()

    def _reset_zoom(self):
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.fit_to_view()

    def _on_mousewheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self._zoom(factor)

    def _on_pan_press(self, event):
        self._drag_data["start_x"] = event.x
        self._drag_data["start_y"] = event.y

    def _on_pan_drag(self, event):
        dx = event.x - self._drag_data["start_x"]
        dy = event.y - self._drag_data["start_y"]
        self.offset_x += dx
        self.offset_y += dy
        self._drag_data["start_x"] = event.x
        self._drag_data["start_y"] = event.y
        self.redraw()

    def _on_canvas_press(self, event):
        wx, wy = self._to_world(event.x, event.y)
        clicked_router = None
        for rid, r in self.graph.routers.items():
            dist = math.hypot(r.x - wx, r.y - wy)
            if dist <= 24:
                clicked_router = rid
                break

        if clicked_router:
            self.selected_router = clicked_router
            self._drag_data["router"] = clicked_router
            self._drag_data["start_x"] = wx
            self._drag_data["start_y"] = wy
        else:
            self.selected_router = None
            self._on_pan_press(event)
        self.redraw()

    def _on_canvas_drag(self, event):
        if self._drag_data.get("router"):
            rid = self._drag_data["router"]
            wx, wy = self._to_world(event.x, event.y)
            self.graph.set_router_position(rid, wx, wy)
            self.redraw()
        else:
            self._on_pan_drag(event)

    def _on_canvas_release(self, event):
        self._drag_data["router"] = None
        self._update_representations()

    def _add_router_dialog(self):
        dlg = AddRouterDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            rid, rname = dlg.result
            cw = max(self.canvas.winfo_width(), 400) / 2
            ch = max(self.canvas.winfo_height(), 300) / 2
            wx, wy = self._to_world(cw, ch)
            if self.graph.add_router(rid, rname, wx, wy):
                nodes = sorted(self.graph.routers.keys())
                self.cb_src["values"] = nodes
                self.cb_dst["values"] = nodes
                self.redraw()
                self._update_representations()
                self.console.log(f"Added router '{rid}' ({rname}).", "success")
            else:
                messagebox.showerror("Error", f"Router ID {rid} already exists.")

    def _remove_selected_router(self):
        if not self.selected_router:
            messagebox.showinfo("Selection Required", "Click a router on canvas to select it first.")
            return
        rid = self.selected_router
        if self.graph.remove_router(rid):
            self.selected_router = None
            nodes = sorted(self.graph.routers.keys())
            self.cb_src["values"] = nodes
            self.cb_dst["values"] = nodes
            if self.source_id == rid and nodes:
                self.source_id = nodes[0]
                self.cb_src.set(self.source_id)
            if self.dest_id == rid and nodes:
                self.dest_id = nodes[-1]
                self.cb_dst.set(self.dest_id)
            self.reset_simulation()
            self._update_representations()
            self.console.log(f"Removed router '{rid}' and associated links.", "info")

    def _add_link_dialog(self):
        nodes = sorted(self.graph.routers.keys())
        if len(nodes) < 2:
            messagebox.showinfo("Insufficient Routers", "At least two routers are required to form a connection.")
            return
        dlg = AddLinkDialog(self, nodes)
        self.wait_window(dlg)
        if dlg.result:
            u, v = dlg.result
            if self.graph.add_edge(u, v, 1.0):
                self.redraw()
                self._update_representations()
                self.console.log(f"Connected link between '{u}' and '{v}'.", "success")

    def _toggle_selected_power(self):
        if not self.selected_router:
            messagebox.showinfo("Selection Required", "Click a router on canvas to select it first.")
            return
        st = self.graph.toggle_router_status(self.selected_router)
        state_str = "ONLINE" if st else "OFFLINE"
        self.console.log(f"Router '{self.selected_router}' status changed to {state_str}.", "warning" if not st else "info")
        self.reset_simulation()
        self._update_representations()
        self.redraw()

    def _update_representations(self):
        adj_list = self.graph.get_adjacency_list()
        nodes, matrix = self.graph.get_adjacency_matrix()

        txt = "=== ADJACENCY LIST O(V+E) ===\n"
        for u, neighbors in adj_list.items():
            txt += f"  {u} -> [{', '.join(neighbors)}]\n"

        txt += "\n=== ADJACENCY MATRIX O(V^2) ===\n     "
        for n in nodes:
            txt += f"{n:>4}"
        txt += "\n"
        for i, u in enumerate(nodes):
            txt += f"{u:>4} "
            for j in range(len(nodes)):
                val = int(matrix[i][j])
                txt += f"{val:>4}"
            txt += "\n"

        comps = self.graph.get_connected_components()
        txt += f"\nConnectivity: {'Connected (1 Component)' if len(comps)==1 else f'Disconnected ({len(comps)} Components)'}\n"

        self.txt_repr.config(state="normal")
        self.txt_repr.delete("1.0", "end")
        self.txt_repr.insert("end", txt)
        self.txt_repr.config(state="disabled")

    def redraw(self):
        self.canvas.delete("graph")
        path_edges = set()
        if len(self.active_path) > 1:
            for i in range(len(self.active_path) - 1):
                u = self.active_path[i]
                v = self.active_path[i + 1]
                path_edges.add(tuple(sorted((u, v))))

        for (u, v), w in self.graph.edges.items():
            if u not in self.graph.routers or v not in self.graph.routers:
                continue
            r1 = self.graph.routers[u]
            r2 = self.graph.routers[v]
            x1, y1 = self._to_screen(r1.x, r1.y)
            x2, y2 = self._to_screen(r2.x, r2.y)
            is_active_edge = tuple(sorted((u, v))) in path_edges

            line_color = Theme.SUCCESS if is_active_edge else ("#E2E8F0" if (not r1.is_online or not r2.is_online) else "#94A3B8")
            line_width = 4 if is_active_edge else 2

            self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=line_width, tags="graph")

        node_r = 18 * self.scale
        for rid, r in self.graph.routers.items():
            x, y = self._to_screen(r.x, r.y)

            if not r.is_online:
                fill_color = Theme.COLOR_OFFLINE
            elif rid == self.current_node:
                fill_color = Theme.COLOR_EXPLORE
            elif rid == self.source_id:
                fill_color = Theme.SECONDARY
            elif rid == self.dest_id:
                fill_color = Theme.SUCCESS
            elif rid in self.active_path:
                fill_color = Theme.SUCCESS
            elif rid in self.visited_nodes:
                fill_color = "#93C5FD"
            else:
                fill_color = Theme.PRIMARY

            outline_color = "#1D4ED8" if rid == self.selected_router else "#0F172A"
            outline_width = 3 if rid == self.selected_router else 1

            self.canvas.create_oval(
                x - node_r, y - node_r, x + node_r, y + node_r,
                fill=fill_color, outline=outline_color, width=outline_width, tags="graph"
            )

            font_sz = max(8, int(9 * self.scale))
            text_color = "#0F172A" if fill_color in ("#93C5FD", "#FDE047") else "#FFFFFF"
            self.canvas.create_text(
                x, y,
                text=rid, fill=text_color, font=("Helvetica", font_sz, "bold"), tags="graph"
            )

            status_tag = "" if r.is_online else " (OFFLINE)"
            lbl_color = Theme.ERROR if not r.is_online else Theme.TEXT_MUTED
            self.canvas.create_text(
                x, y + node_r + 10,
                text=f"{r.name}{status_tag}", fill=lbl_color, font=("Helvetica", max(7, font_sz - 1)), tags="graph"
            )

            if rid in self.visited_order:
                order_num = self.visited_order.index(rid) + 1
                bx = x + node_r * 0.75
                by = y - node_r * 0.75
                br = 8 * self.scale
                self.canvas.create_oval(
                    bx - br, by - br, bx + br, by + br,
                    fill="#F59E0B", outline="#FFFFFF", width=1.5, tags="graph"
                )
                self.canvas.create_text(
                    bx, by,
                    text=str(order_num), fill="#172033",
                    font=("Helvetica", max(7, int(8 * self.scale)), "bold"), tags="graph"
                )

        self.canvas.tag_raise("legend")
