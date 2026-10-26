import json
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Optional, Any

from theme import Theme, CardFrame, StatCard, ConsoleLog, ControlBar, ZoomPanToolbar, SimulationService
from network import Graph, Router, validate_router_id
from algorithms import SimulationStep, SimulationResult, bfs_path, dfs_path

class AddRouterDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Router")
        self.geometry("380x230")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_APP)
        self.result = None

        frame = CardFrame(self, padding=16)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Router ID (e.g. R7):", font=Theme.FONT_BOLD, style="Card.TLabel").pack(anchor="w", pady=(0, 4))
        self.id_entry = ttk.Entry(frame, font=Theme.FONT_BODY)
        self.id_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Router Name:", font=Theme.FONT_BOLD, style="Card.TLabel").pack(anchor="w", pady=(0, 4))
        self.name_entry = ttk.Entry(frame, font=Theme.FONT_BODY)
        self.name_entry.pack(fill="x", pady=(0, 14))

        btn_box = ttk.Frame(frame, style="Card.TFrame")
        btn_box.pack(fill="x", side="bottom")
        ttk.Button(btn_box, text="Cancel", style="TButton", command=self.destroy).pack(side="right", padx=(6, 0))
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
        self.title("Connect Routers")
        self.geometry("380x230")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_APP)
        self.result = None

        frame = CardFrame(self, padding=16)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Endpoint Router A:", font=Theme.FONT_BOLD, style="Card.TLabel").pack(anchor="w", pady=(0, 4))
        self.cb_u = ttk.Combobox(frame, values=router_ids, state="readonly", font=Theme.FONT_BODY)
        self.cb_u.pack(fill="x", pady=(0, 10))
        if router_ids:
            self.cb_u.set(router_ids[0])

        ttk.Label(frame, text="Endpoint Router B:", font=Theme.FONT_BOLD, style="Card.TLabel").pack(anchor="w", pady=(0, 4))
        self.cb_v = ttk.Combobox(frame, values=router_ids, state="readonly", font=Theme.FONT_BODY)
        self.cb_v.pack(fill="x", pady=(0, 14))
        if len(router_ids) > 1:
            self.cb_v.set(router_ids[1])

        btn_box = ttk.Frame(frame, style="Card.TFrame")
        btn_box.pack(fill="x", side="bottom")
        ttk.Button(btn_box, text="Cancel", style="TButton", command=self.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btn_box, text="Connect Routers", style="Primary.TButton", command=self._on_submit).pack(side="right")

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

class RemoveLinkDialog(tk.Toplevel):
    def __init__(self, parent, edges: List[Tuple[str, str]]):
        super().__init__(parent)
        self.title("Remove Connection")
        self.geometry("380x200")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_APP)
        self.result = None

        frame = CardFrame(self, padding=16)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Select Connection to Remove:", font=Theme.FONT_BOLD, style="Card.TLabel").pack(anchor="w", pady=(0, 6))
        edge_strs = [f"{u} <---> {v}" for u, v in edges]
        self.cb_edge = ttk.Combobox(frame, values=edge_strs, state="readonly", font=Theme.FONT_BODY)
        self.cb_edge.pack(fill="x", pady=(0, 16))
        if edge_strs:
            self.cb_edge.set(edge_strs[0])

        self.edges = edges

        btn_box = ttk.Frame(frame, style="Card.TFrame")
        btn_box.pack(fill="x", side="bottom")
        ttk.Button(btn_box, text="Cancel", style="TButton", command=self.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btn_box, text="Remove Link", style="Tool.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()

    def _on_submit(self):
        idx = self.cb_edge.current()
        if idx >= 0 and idx < len(self.edges):
            self.result = self.edges[idx]
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
        self.saved_run_snapshot: Optional[SimulationResult] = None

        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self._drag_data = {"start_x": 0, "start_y": 0, "router": None}

        self._packet_timer = None
        self._packet_frames: List[Tuple[float, float, str, int, int]] = []
        self._packet_frame_idx = 0
        self._packet_running = False
        self._packet_paused = False

        self.visited_nodes = set()
        self.visited_order = []
        self.active_path = []
        self.current_node = None
        self.active_edge = None

        self._build_ui()
        self.load_preset("sample")
        self.after(150, self.fit_to_view)

    def cancel_all_animations(self):
        self.sim_service.stop()
        if self._packet_timer:
            try:
                self.after_cancel(self._packet_timer)
            except Exception:
                pass
            self._packet_timer = None
        self._packet_running = False
        self._packet_paused = False
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

        side_col = ttk.Frame(paned, style="TFrame", width=440)
        paned.add(side_col, weight=1)
        side_col.grid_rowconfigure(2, weight=1)
        side_col.grid_columnconfigure(0, weight=1)

        top_ctrl = CardFrame(main_col, padding=(10, 8))
        top_ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(top_ctrl, text="Source:", font=Theme.FONT_BOLD, style="Card.TLabel").pack(side="left", padx=(4, 2))
        self.cb_src = ttk.Combobox(top_ctrl, width=6, state="readonly", font=Theme.FONT_BODY)
        self.cb_src.pack(side="left", padx=3)
        self.cb_src.bind("<<ComboboxSelected>>", self._on_endpoint_change)

        ttk.Label(top_ctrl, text="Destination:", font=Theme.FONT_BOLD, style="Card.TLabel").pack(side="left", padx=(10, 2))
        self.cb_dst = ttk.Combobox(top_ctrl, width=6, state="readonly", font=Theme.FONT_BODY)
        self.cb_dst.pack(side="left", padx=3)
        self.cb_dst.bind("<<ComboboxSelected>>", self._on_endpoint_change)

        ttk.Button(top_ctrl, text="▶ Run BFS", style="Primary.TButton", command=self.run_bfs).pack(side="left", padx=5)
        ttk.Button(top_ctrl, text="▶ Run DFS", style="Secondary.TButton", command=self.run_dfs).pack(side="left", padx=5)
        ttk.Button(top_ctrl, text="✉ Animate Packet", style="Purple.TButton", command=self.start_packet_animation).pack(side="left", padx=5)

        self.zoom_toolbar = ZoomPanToolbar(
            top_ctrl,
            on_zoom_in=lambda: self._zoom(1.15),
            on_zoom_out=lambda: self._zoom(0.85),
            on_fit_view=self.fit_to_view,
            on_reset_zoom=self._reset_zoom
        )
        self.zoom_toolbar.pack(side="right")

        self.banner = CardFrame(main_col, padding=(10, 8))
        self.banner.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        self.banner.grid_columnconfigure(1, weight=1)

        self.lbl_banner_algo = tk.Label(
            self.banner, text="READY", font=Theme.FONT_SECTION,
            bg=Theme.BG_SELECTED, fg=Theme.PRIMARY, padx=12, pady=4
        )
        self.lbl_banner_algo.grid(row=0, column=0, rowspan=2, padx=(0, 12))

        lbl_t_hdr = tk.Label(self.banner, text="Traversal Order:", font=Theme.FONT_BOLD, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        lbl_t_hdr.grid(row=0, column=1, sticky="w")
        self.lbl_traversal = tk.Label(self.banner, text="None (Click 'Run BFS' or 'Run DFS')", font=Theme.FONT_SECTION, bg=Theme.BG_CARD, fg=Theme.PRIMARY)
        self.lbl_traversal.grid(row=0, column=2, sticky="w", padx=(8, 0))

        lbl_r_hdr = tk.Label(self.banner, text="Discovered Route:", font=Theme.FONT_BOLD, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        lbl_r_hdr.grid(row=1, column=1, sticky="w")
        self.lbl_route = tk.Label(self.banner, text="None", font=Theme.FONT_SECTION, bg=Theme.BG_CARD, fg=Theme.SUCCESS)
        self.lbl_route.grid(row=1, column=2, sticky="w", padx=(8, 0))

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
        self.canvas.bind("<ButtonPress-3>", self._on_canvas_right_click)
        self.canvas.bind("<B3-Motion>", self._on_pan_drag)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom(1.1))
        self.canvas.bind("<Button-5>", lambda e: self._zoom(0.9))
        self.canvas.bind("<Configure>", lambda e: self.after_idle(self._check_canvas_bounds))

        bottom_bar = ttk.Frame(main_col, style="TFrame")
        bottom_bar.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        self.control_bar = ControlBar(
            bottom_bar,
            on_play=self._on_play_clicked,
            on_pause=self._on_pause_clicked,
            on_step=self._on_step_clicked,
            on_reset=self.reset_simulation,
            on_speed_change=self._on_speed_changed
        )
        self.control_bar.pack(fill="x")

        self._build_packet_status_bar(bottom_bar)

        self._build_sidebar(side_col)

        self._draw_legend()

    def _build_packet_status_bar(self, parent):
        self.p_card = CardFrame(parent, padding=(10, 6))
        self.p_card.pack(fill="x", pady=(4, 0))
        self.lbl_packet_info = tk.Label(
            self.p_card,
            text="Packet Status: Idle | Source: - | Destination: - | Current: - | Hop: 0 / 0 | Route: [None]",
            font=Theme.FONT_BODY,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            anchor="w"
        )
        self.lbl_packet_info.pack(side="left", fill="x", expand=True)

    def _build_sidebar(self, parent):
        stats_frame = ttk.Frame(parent, style="TFrame")
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        self.stat_hops = StatCard(stats_frame, title="Path Hops", value="0", subtitle="Optimal Hop Count", color=Theme.SUCCESS)
        self.stat_hops.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        self.stat_visited = StatCard(stats_frame, title="Visited", value="0", subtitle="Routers Explored", color=Theme.PRIMARY)
        self.stat_visited.grid(row=0, column=1, sticky="ew", padx=2)

        self.stat_reach = StatCard(stats_frame, title="Reachable", value="0 / 0", subtitle="Online from Source", color=Theme.SECONDARY)
        self.stat_reach.grid(row=0, column=2, sticky="ew", padx=(2, 0))

        stats_row2 = ttk.Frame(parent, style="TFrame")
        stats_row2.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        stats_row2.grid_columnconfigure(0, weight=1)
        stats_row2.grid_columnconfigure(1, weight=1)
        stats_row2.grid_columnconfigure(2, weight=1)

        self.stat_v_e = StatCard(stats_row2, title="V / E Count", value="0 / 0", subtitle="Vertices / Edges", color=Theme.TEXT_MAIN)
        self.stat_v_e.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        self.stat_ops = StatCard(stats_row2, title="Queue/Stack Ops", value="0 / 0", subtitle="Enq/Deq or Push/Pop", color=Theme.PURPLE)
        self.stat_ops.grid(row=0, column=1, sticky="ew", padx=2)

        self.stat_comps = StatCard(stats_row2, title="Components", value="1", subtitle="Connected Graph", color=Theme.SUCCESS)
        self.stat_comps.grid(row=0, column=2, sticky="ew", padx=(2, 0))

        ctrl_card = CardFrame(parent, padding=(8, 6))
        ctrl_card.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        row_top = ttk.Frame(ctrl_card, style="Card.TFrame")
        row_top.pack(fill="x", pady=(0, 3))
        ttk.Label(row_top, text="Network Topology Controls:", font=Theme.FONT_SECTION, style="CardTitle.TLabel").pack(side="left")

        row1 = ttk.Frame(ctrl_card, style="Card.TFrame")
        row1.pack(fill="x", pady=2)
        ttk.Button(row1, text="+ Add Router", style="Tool.TButton", command=self._add_router_dialog).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(row1, text="- Remove Router", style="Tool.TButton", command=self._remove_selected_router).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(row1, text="+ Connect Routers", style="Tool.TButton", command=self._add_link_dialog).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(row1, text="- Remove Link", style="Tool.TButton", command=self._remove_link_dialog).pack(side="left", expand=True, fill="x", padx=1)

        row2 = ttk.Frame(ctrl_card, style="Card.TFrame")
        row2.pack(fill="x", pady=2)
        ttk.Button(row2, text="⚡ Toggle Power", style="Tool.TButton", command=self._toggle_selected_power).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(row2, text="Generate Connected", style="Tool.TButton", command=lambda: self._generate_graph("connected")).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(row2, text="Generate Disconnected", style="Tool.TButton", command=lambda: self._generate_graph("disconnected")).pack(side="left", expand=True, fill="x", padx=1)

        row3 = ttk.Frame(ctrl_card, style="Card.TFrame")
        row3.pack(fill="x", pady=2)
        ttk.Label(row3, text="Topology Preset:", font=Theme.FONT_BOLD, style="Card.TLabel").pack(side="left", padx=(1, 4))
        self.cb_preset = ttk.Combobox(
            row3,
            values=[
                "Default Sample Mesh",
                "Direct Route",
                "Multiple Possible Routes",
                "Cyclic Network",
                "Disconnected Network",
                "Network with Offline Router"
            ],
            state="readonly",
            font=Theme.FONT_BODY,
            width=24
        )
        self.cb_preset.pack(side="left", expand=True, fill="x", padx=1)
        self.cb_preset.set("Default Sample Mesh")
        self.cb_preset.bind("<<ComboboxSelected>>", self._on_preset_selected)

        row4 = ttk.Frame(ctrl_card, style="Card.TFrame")
        row4.pack(fill="x", pady=(3, 1))
        ttk.Button(row4, text="Save Topology", style="Tool.TButton", command=self.save_topology_json).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(row4, text="Load Topology", style="Tool.TButton", command=self.load_topology_json).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(row4, text="↺ Reset Graph", style="Tool.TButton", command=lambda: self.load_preset("sample")).pack(side="left", expand=True, fill="x", padx=1)

        self.side_tabs = ttk.Notebook(parent)
        self.side_tabs.grid(row=3, column=0, sticky="nsew")
        parent.grid_rowconfigure(3, weight=1)

        tab_queue = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_queue, text=" Queue / Stack ")
        self._build_queue_stack_tab(tab_queue)

        tab_trav = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_trav, text=" Traversal ")
        self._build_traversal_tab(tab_trav)

        tab_adj_list = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_adj_list, text=" Adjacency List ")
        self._build_adj_list_tab(tab_adj_list)

        tab_adj_mat = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_adj_mat, text=" Adjacency Matrix ")
        self._build_adj_matrix_tab(tab_adj_mat)

        tab_tree = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_tree, text=" Traversal Tree ")
        self._build_traversal_tree_tab(tab_tree)

        tab_log = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_log, text=" Execution Log ")
        self.console = ConsoleLog(tab_log, height=9)
        self.console.pack(fill="both", expand=True)

        tab_co = ttk.Frame(self.side_tabs, style="TFrame")
        self.side_tabs.add(tab_co, text=" Course Outcomes ")
        self._build_co_tab(tab_co)

    def _build_queue_stack_tab(self, parent):
        q_frame = CardFrame(parent, padding=8)
        q_frame.pack(fill="both", expand=True)
        q_frame.grid_rowconfigure(2, weight=1)
        q_frame.grid_columnconfigure(0, weight=1)

        header_box = ttk.Frame(q_frame, style="Card.TFrame")
        header_box.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.lbl_ds_title = tk.Label(
            header_box,
            text="Active Traversal Data Structure: Idle",
            font=Theme.FONT_SECTION,
            bg=Theme.BG_CARD,
            fg=Theme.PRIMARY,
            anchor="w"
        )
        self.lbl_ds_title.pack(side="left")

        self.lbl_ds_mode = tk.Label(
            q_frame,
            text="BFS Rule: FIFO Queue (Enters Rear, Exits Front) | DFS Rule: LIFO Stack (Enters/Exits Top)",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED,
            anchor="w",
            wraplength=410,
            justify="left"
        )
        self.lbl_ds_mode.grid(row=1, column=0, sticky="ew", pady=(0, 4))

        list_container = tk.Frame(q_frame, bg=Theme.BORDER, padx=1, pady=1)
        list_container.grid(row=2, column=0, sticky="nsew")

        self.ds_listbox = tk.Listbox(
            list_container,
            font=Theme.FONT_MONO,
            height=6,
            bg=Theme.BG_PANEL_ALT,
            fg=Theme.TEXT_MAIN,
            bd=0,
            selectbackground=Theme.BG_SELECTED
        )
        ds_scroll = ttk.Scrollbar(list_container, orient="vertical", command=self.ds_listbox.yview)
        self.ds_listbox.configure(yscrollcommand=ds_scroll.set)
        self.ds_listbox.pack(side="left", fill="both", expand=True)
        ds_scroll.pack(side="right", fill="y")

        self.final_box = CardFrame(q_frame, padding=6)
        self.final_box.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        ttk.Label(self.final_box, text="Final Queue / Stack State Summary (CO1):", font=Theme.FONT_BOLD, style="CardTitle.TLabel").pack(anchor="w")
        self.lbl_final_summary = tk.Label(
            self.final_box,
            text="Run an algorithm to inspect final queue/stack metrics, operations, and contents.",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            justify="left",
            anchor="w",
            wraplength=400
        )
        self.lbl_final_summary.pack(fill="x", pady=(2, 0))

    def _build_traversal_tab(self, parent):
        t_frame = CardFrame(parent, padding=8)
        t_frame.pack(fill="both", expand=True)
        t_frame.grid_rowconfigure(1, weight=1)
        t_frame.grid_columnconfigure(0, weight=1)

        self.lbl_trav_title = tk.Label(
            t_frame,
            text="Chronological Discovery & Visit Sequence:",
            font=Theme.FONT_SECTION,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            anchor="w"
        )
        self.lbl_trav_title.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        t_container = tk.Frame(t_frame, bg=Theme.BORDER, padx=1, pady=1)
        t_container.grid(row=1, column=0, sticky="nsew")

        cols = ("Step", "Router", "Action", "Level", "Parent")
        self.tree_traversal = ttk.Treeview(t_container, columns=cols, show="headings", height=8)
        self.tree_traversal.heading("Step", text="#")
        self.tree_traversal.column("Step", width=42, anchor="center")
        self.tree_traversal.heading("Router", text="Router")
        self.tree_traversal.column("Router", width=70, anchor="center")
        self.tree_traversal.heading("Action", text="Action")
        self.tree_traversal.column("Action", width=140, anchor="w")
        self.tree_traversal.heading("Level", text="Hop / Depth")
        self.tree_traversal.column("Level", width=85, anchor="center")
        self.tree_traversal.heading("Parent", text="Parent")
        self.tree_traversal.column("Parent", width=70, anchor="center")

        t_scroll = ttk.Scrollbar(t_container, orient="vertical", command=self.tree_traversal.yview)
        self.tree_traversal.configure(yscrollcommand=t_scroll.set)
        self.tree_traversal.pack(side="left", fill="both", expand=True)
        t_scroll.pack(side="right", fill="y")

        self.lbl_trav_footer = tk.Label(
            t_frame,
            text="Path: None",
            font=Theme.FONT_BOLD,
            bg=Theme.BG_CARD,
            fg=Theme.SUCCESS,
            anchor="w",
            wraplength=410,
            justify="left"
        )
        self.lbl_trav_footer.grid(row=2, column=0, sticky="ew", pady=(4, 0))

    def _build_adj_list_tab(self, parent):
        repr_frame = CardFrame(parent, padding=8)
        repr_frame.pack(fill="both", expand=True)

        ttk.Label(repr_frame, text="Adjacency List O(V + E) — Primary Graph Storage:", font=Theme.FONT_SECTION, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))

        txt_container = tk.Frame(repr_frame, bg=Theme.BORDER, padx=1, pady=1)
        txt_container.pack(fill="both", expand=True)

        self.txt_adj_list = tk.Text(
            
            txt_container,
            font=Theme.FONT_MONO,
            height=12,
            bg=Theme.BG_PANEL_ALT,
            fg=Theme.TEXT_MAIN,
            bd=0,
            wrap="none"
        )
        s_y = ttk.Scrollbar(txt_container, orient="vertical", command=self.txt_adj_list.yview)
        s_x = ttk.Scrollbar(txt_container, orient="horizontal", command=self.txt_adj_list.xview)
        self.txt_adj_list.configure(yscrollcommand=s_y.set, xscrollcommand=s_x.set)

        self.txt_adj_list.pack(side="left", fill="both", expand=True)
        s_y.pack(side="right", fill="y")
        s_x.pack(side="bottom", fill="x")

    def _build_adj_matrix_tab(self, parent):
        repr_frame = CardFrame(parent, padding=8)
        repr_frame.pack(fill="both", expand=True)

        ttk.Label(repr_frame, text="Adjacency Matrix O(V²) — Static Grid Inspection:", font=Theme.FONT_SECTION, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))

        txt_container = tk.Frame(repr_frame, bg=Theme.BORDER, padx=1, pady=1)
        txt_container.pack(fill="both", expand=True)

        self.txt_adj_matrix = tk.Text(
            txt_container,
            font=Theme.FONT_MONO,
            height=12,
            bg=Theme.BG_PANEL_ALT,
            fg=Theme.TEXT_MAIN,
            bd=0,
            wrap="none"
        )
        s_y = ttk.Scrollbar(txt_container, orient="vertical", command=self.txt_adj_matrix.yview)
        s_x = ttk.Scrollbar(txt_container, orient="horizontal", command=self.txt_adj_matrix.xview)
        self.txt_adj_matrix.configure(yscrollcommand=s_y.set, xscrollcommand=s_x.set)

        self.txt_adj_matrix.pack(side="left", fill="both", expand=True)
        s_y.pack(side="right", fill="y")
        s_x.pack(side="bottom", fill="x")

    def _build_traversal_tree_tab(self, parent):
        tree_frame = CardFrame(parent, padding=8)
        tree_frame.pack(fill="both", expand=True)

        ttk.Label(tree_frame, text="Traversal Tree (Parent-Child Discovery Edges):", font=Theme.FONT_SECTION, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))

        txt_container = tk.Frame(tree_frame, bg=Theme.BORDER, padx=1, pady=1)
        txt_container.pack(fill="both", expand=True)

        self.txt_tree = tk.Text(
            txt_container,
            font=Theme.FONT_MONO,
            height=12,
            bg=Theme.BG_PANEL_ALT,
            fg=Theme.TEXT_MAIN,
            bd=0,
            wrap="none"
        )
        s_y = ttk.Scrollbar(txt_container, orient="vertical", command=self.txt_tree.yview)
        s_x = ttk.Scrollbar(txt_container, orient="horizontal", command=self.txt_tree.xview)
        self.txt_tree.configure(yscrollcommand=s_y.set, xscrollcommand=s_x.set)

        self.txt_tree.pack(side="left", fill="both", expand=True)
        s_y.pack(side="right", fill="y")
        s_x.pack(side="bottom", fill="x")

    def _build_co_tab(self, parent):
        co_frame = CardFrame(parent, padding=10)
        co_frame.pack(fill="both", expand=True)

        txt_container = tk.Frame(co_frame, bg=Theme.BORDER, padx=1, pady=1)
        txt_container.pack(fill="both", expand=True)

        txt_co = tk.Text(
            txt_container,
            font=Theme.FONT_BODY,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            bd=0,
            wrap="word",
            padx=10,
            pady=8
        )
        co_scroll = ttk.Scrollbar(txt_container, orient="vertical", command=txt_co.yview)
        txt_co.configure(yscrollcommand=co_scroll.set)
        txt_co.pack(side="left", fill="both", expand=True)
        co_scroll.pack(side="right", fill="y")

        doc = (
            "DSA COURSE OUTCOME ALIGNMENT (CO1, CO2, CO5)\n"
            "============================================\n\n"
            "CO1: Develop efficient solutions using stack and/or queue data structures.\n"
            "• BFS Implementation: Uses a genuine First-In-First-Out (FIFO) queue (collections.deque). Discovers routers level-by-level, ensuring the shortest-hop path in unweighted networks.\n"
            "• DFS Implementation: Uses an explicit Last-In-First-Out (LIFO) stack (list). Explores deep network paths and records backtracking; demonstrates valid path discovery without shortest-path guarantees.\n"
            "• Live & Final Inspector: Visualizes the live insertion and removal of routers, and preserves dedicated final queue/stack metrics (operations count, maximum size, remaining items).\n\n"
            "CO2: Use dynamic data structures for efficient storage and retrieval.\n"
            "• Dynamic Graph Storage: The primary representation is a dynamic Adjacency List O(V + E) where routers and links are added, looked up, and deleted in real time.\n"
            "• Storage Efficiency: Avoids allocating fixed-size quadratic matrices during interactive topology editing.\n"
            "• Model-View Consistency: Every node and connection on the canvas maps 1:1 to the underlying graph model.\n\n"
            "CO5: Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems.\n"
            "• Network Routing: Packet routing modeled as graph traversal where routers are vertices and transmission lines are edges.\n"
            "• Dual Representations: Synchronized Adjacency List O(V + E) and Adjacency Matrix O(V²).\n"
            "• Traversal Tree: Displays discovery parent-child tree edges, highlighting source root, target, and final route.\n"
            "• Real Packet Transmission: An animated packet travels across the discovered route hop-by-hop.\n"
            "• Network Diagnostics: Dynamic detection of reachability, articulation points (offline routers), and connected components.\n\n"
            "PRACTICUM ALIGNMENT:\n"
            "• PrO-13: Represent graphs using adjacency lists and adjacency matrices.\n"
            "• PrO-14: Select a suitable graph representation for the problem (Adjacency List for sparse/dynamic, Adjacency Matrix for dense constant-time queries).\n"
            "• PrO-15: Use graph structures to solve network connectivity and packet routing problems.\n"
        )
        txt_co.insert("1.0", doc)
        txt_co.config(state="disabled")

    def _draw_legend(self):
        legend = CardFrame(self.canvas, padding=(8, 4))
        items = [
            ("Normal", Theme.PRIMARY),
            ("Source", Theme.SECONDARY),
            ("Destination", Theme.SUCCESS),
            ("Exploring", Theme.WARNING),
            ("Visited", Theme.COLOR_VISITED),
            ("Route", Theme.COLOR_ROUTE),
            ("Offline", Theme.COLOR_OFFLINE)
        ]
        for name, color in items:
            row = ttk.Frame(legend, style="Card.TFrame")
            row.pack(side="left", padx=5)
            dot = tk.Label(row, text="●", fg=color, bg=Theme.BG_CARD, font=("Helvetica", 11))
            dot.pack(side="left")
            lbl = tk.Label(row, text=name, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, font=Theme.FONT_SMALL_BOLD)
            lbl.pack(side="left", padx=(2, 0))
        self.canvas.create_window(10, 10, window=legend, anchor="nw", tags="legend")

    def load_preset(self, preset_name: str):
        self.cancel_all_animations()
        self.graph.load_preset(preset_name)

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
        self._update_all_statistics()
        self.console.clear()
        self.console.log(f"Loaded topology preset: {preset_name.replace('_', ' ').upper()} ({len(nodes)} routers).", "info")

    def _on_preset_selected(self, event=None):
        name_map = {
            "Default Sample Mesh": "sample",
            "Direct Route": "direct",
            "Multiple Possible Routes": "multi_route",
            "Cyclic Network": "cyclic",
            "Disconnected Network": "disconnected",
            "Network with Offline Router": "offline_router"
        }
        val = self.cb_preset.get()
        key = name_map.get(val, "sample")
        self.load_preset(key)

    def _generate_graph(self, gtype: str):
        self.cancel_all_animations()
        if gtype == "connected":
            self.graph.generate_connected(6)
            self.console.log("Generated random connected network topology (1 connected component).", "info")
        else:
            self.graph.generate_disconnected(6)
            self.console.log("Generated random disconnected network topology (multiple subnets).", "warning")

        nodes = sorted(self.graph.routers.keys())
        self.cb_src["values"] = nodes
        self.cb_dst["values"] = nodes
        if nodes:
            self.source_id = nodes[0]
            self.dest_id = nodes[-1]
            self.cb_src.set(self.source_id)
            self.cb_dst.set(self.dest_id)

        self.reset_simulation()
        self.fit_to_view()
        self._update_all_statistics()

    def _on_endpoint_change(self, event=None):
        self.source_id = self.cb_src.get()
        self.dest_id = self.cb_dst.get()
        self.reset_simulation()
        self.redraw()
        self._update_all_statistics()

    def run_bfs(self):
        self.reset_simulation()
        res = bfs_path(self.graph, self.source_id, self.dest_id)
        self.current_result = res
        self.saved_run_snapshot = res
        self.lbl_banner_algo.config(text="BFS (SHORTEST HOP)", bg="#DBEAFE", fg=Theme.PRIMARY)
        self.lbl_ds_title.config(text="BFS FIFO Queue (Level-by-Level Discovery):", fg=Theme.PRIMARY)
        self.lbl_ds_mode.config(text="Queue Rule: FIFO (Enqueues at rear, dequeues at front). Guarantees shortest hop path in unweighted networks.")
        self.console.log(f"Initiated BFS Shortest-Hop search: {self.source_id} -> {self.dest_id}", "info")
        self._load_and_run_simulation(res)

    def run_dfs(self):
        self.reset_simulation()
        res = dfs_path(self.graph, self.source_id, self.dest_id)
        self.current_result = res
        self.saved_run_snapshot = res
        self.lbl_banner_algo.config(text="DFS (PATH DISCOVERY)", bg="#DDD6FE", fg=Theme.PURPLE)
        self.lbl_ds_title.config(text="DFS LIFO Stack (Deep Branch Discovery):", fg=Theme.PURPLE)
        self.lbl_ds_mode.config(text="Stack Rule: LIFO (Pushes to top, pops from top). Explores deep branches with backtracking. (Not shortest path).")
        self.console.log(f"Initiated DFS Path Discovery: {self.source_id} -> {self.dest_id}", "info")
        self._load_and_run_simulation(res)

    def _load_and_run_simulation(self, res: SimulationResult):
        full_traversal = " -> ".join(res.visited_order) if res.visited_order else "None"
        final_route = f"{' -> '.join(res.path)} ({len(res.path) - 1} hops)" if res.success else "No Route Found"

        self.lbl_traversal.config(text=full_traversal)
        self.lbl_route.config(text=final_route)
        self.stat_visited.update_val(str(len(res.visited_order)))

        op_name = "Enq / Deq" if "BFS" in res.algorithm_name else "Push / Pop"
        self.stat_ops.update_val(f"{res.total_pushes_or_enqueues} / {res.total_pops_or_dequeues}", f"Total {op_name}")

        if res.success:
            self.stat_hops.update_val(str(len(res.path) - 1), f"Time: {res.execution_time_ms:.2f}ms")
            self._update_packet_status("Idle (Route Discovered)", 0, len(res.path) - 1, res.path[0] if res.path else "-")
        else:
            self.stat_hops.update_val("N/A", "Unreachable")
            self._update_packet_status("Failed (Destination Unreachable)", 0, 0, "-")

        self._populate_traversal_table(res)
        self._populate_traversal_tree(res)
        self._update_final_state_summary(res)

        def _on_step(step: SimulationStep, curr: int, total: int):
            self.control_bar.update_step(curr, total)
            self.current_node = step.current_element
            self.active_edge = step.active_edge

            if step.visited_elements:
                self.visited_nodes = set(step.visited_elements)
                self.visited_order = list(step.visited_elements)

            if step.active_path:
                self.active_path = list(step.active_path)

            self.ds_listbox.delete(0, "end")
            for idx, item in enumerate(step.data_structure_state):
                tag = " (Front / Next)" if idx == 0 and "BFS" in res.algorithm_name else (" (Top / Next)" if idx == len(step.data_structure_state) - 1 and "DFS" in res.algorithm_name else "")
                self.ds_listbox.insert("end", f"[{idx}] {item}{tag}")

            lvl = "success" if step.step_type == "complete" else ("warning" if "backtrack" in step.step_type else "info")
            self.console.log(step.message, lvl)
            self.redraw()

        def _on_complete():
            self.control_bar.set_running_state(False)
            self.visited_order = list(res.visited_order)
            self.visited_nodes = set(self.visited_order)
            self.active_path = list(res.path) if res.success else []
            self.current_node = None
            self.active_edge = None

            self._update_final_state_summary(res)

            if res.success:
                self.console.log(f"Traversal Complete. Visited: {full_traversal}", "info")
                self.console.log(f"Discovered Route: {' -> '.join(res.path)} ({len(res.path) - 1} hops). Ready for packet animation.", "success")
            else:
                self.console.log(res.message, "error")

            self.redraw()

        self.sim_service.load_simulation(res, _on_step, _on_complete)
        self.control_bar.set_running_state(True)
        self.sim_service.play()

    def _update_final_state_summary(self, res: SimulationResult):
        is_bfs = "BFS" in res.algorithm_name
        ds_name = "Queue" if is_bfs else "Stack"
        op_in = "Enqueue" if is_bfs else "Push"
        op_out = "Dequeue" if is_bfs else "Pop"

        final_items = res.final_data_structure_state
        if not final_items:
            items_str = f"Empty (0 items remaining — expected after full exploration)"
        else:
            items_str = f"{len(final_items)} items remaining at termination: [{', '.join(final_items)}]"

        summary_text = (
            f"Algorithm: {res.algorithm_name}\n"
            f"• Total {op_in} Operations: {res.total_pushes_or_enqueues}\n"
            f"• Total {op_out} Operations: {res.total_pops_or_dequeues}\n"
            f"• Maximum {ds_name} Size: {res.max_structure_size}\n"
        )
        if not is_bfs:
            summary_text += f"• Backtracking Events: {res.backtracking_count}\n"

        summary_text += (
            f"• Final {ds_name} Contents: {items_str}\n"
            f"• Total Routers Visited: {len(res.visited_order)} ({' -> '.join(res.visited_order)})\n"
            f"• Destination Reachability: {'REACHABLE' if res.success else 'UNREACHABLE'}\n"
            f"• Final Route: {' -> '.join(res.path) if res.success else 'None'} ({len(res.path) - 1 if res.success else 0} hops)"
        )
        self.lbl_final_summary.config(text=summary_text)

    def _populate_traversal_table(self, res: SimulationResult):
        self.tree_traversal.delete(*self.tree_traversal.get_children())
        steps = res.steps
        dist_map = res.depth_or_level
        parent_map = res.parent_map

        for s in steps:
            curr = s.current_element or "-"
            p = parent_map.get(curr, "-")
            lvl = f"Hop {dist_map.get(curr, 0)}" if curr in dist_map else "-"
            self.tree_traversal.insert(
                "", "end",
                values=(s.step_number, curr, s.step_type.upper(), lvl, p if p else "None (Root)")
            )

        final_route = f"{' -> '.join(res.path)} ({len(res.path) - 1} hops)" if res.success else "No Route"
        self.lbl_trav_footer.config(text=f"Final Route: {final_route}")

    def _populate_traversal_tree(self, res: SimulationResult):
        txt = f"=== TRAVERSAL TREE DISCOVERY EDGES ({res.algorithm_name}) ===\n"
        txt += f"Root Source Router: {self.source_id}\n"
        txt += f"Destination Router: {self.dest_id}\n\n"
        txt += f"Tree Edges Generated by Algorithm:\n"

        if res.tree_edges:
            route_edges = set()
            if len(res.path) > 1:
                for i in range(len(res.path) - 1):
                    route_edges.add(tuple(sorted((res.path[i], res.path[i + 1]))))

            for u, v in res.tree_edges:
                is_route = tuple(sorted((u, v))) in route_edges
                marker = " [★ ON FINAL ROUTE]" if is_route else ""
                txt += f"  {u:>4} ---> {v:<4} (Level {res.depth_or_level.get(v, '-')}){marker}\n"
        else:
            txt += "  (No edges discovered)\n"

        txt += f"\nParent Relationships Map:\n"
        for node, par in res.parent_map.items():
            txt += f"  Router {node:>4}  <-- Parent: {par if par else 'None (Source Root)'}\n"

        self.txt_tree.config(state="normal")
        self.txt_tree.delete("1.0", "end")
        self.txt_tree.insert("end", txt)
        self.txt_tree.config(state="disabled")

    def _on_play_clicked(self):
        if self._packet_paused and self._packet_frames:
            self._packet_paused = False
            self._packet_running = True
            self.control_bar.set_running_state(True)
            self._step_packet_frame()
        elif self.sim_service.is_paused:
            self.control_bar.set_running_state(True)
            self.sim_service.play()
        elif self.current_result:
            self._load_and_run_simulation(self.current_result)
        else:
            self.run_bfs()

    def _on_pause_clicked(self):
        if self._packet_running:
            self._packet_running = False
            self._packet_paused = True
            if self._packet_timer:
                try:
                    self.after_cancel(self._packet_timer)
                except Exception:
                    pass
                self._packet_timer = None
            self.control_bar.set_running_state(False, is_paused=True)
            self.console.log("Packet transmission paused.", "warning")
        else:
            self.sim_service.pause()
            self.control_bar.set_running_state(False, is_paused=True)

    def _on_step_clicked(self):
        if self._packet_paused or self._packet_running:
            self._step_packet_single()
        else:
            self.sim_service.step_forward()

    def _on_speed_changed(self, val: int):
        self.sim_service.set_speed(val)

    def reset_simulation(self):
        self.cancel_all_animations()
        self.visited_nodes.clear()
        self.visited_order.clear()
        self.active_path.clear()
        self.current_node = None
        self.active_edge = None
        self.current_result = None
        self.control_bar.update_step(0, 0)
        self.control_bar.set_running_state(False)
        self.stat_hops.update_val("0", "Optimal Hop Count")
        self.stat_visited.update_val("0")
        self.stat_ops.update_val("0 / 0", "Enq/Deq or Push/Pop")
        self.ds_listbox.delete(0, "end")
        self.lbl_banner_algo.config(text="READY", bg=Theme.BG_SELECTED, fg=Theme.PRIMARY)
        self.lbl_traversal.config(text="None (Click 'Run BFS' or 'Run DFS')")
        self.lbl_route.config(text="None")
        self._update_packet_status("Idle", 0, 0, "-")
        self.tree_traversal.delete(*self.tree_traversal.get_children())
        self.txt_tree.config(state="normal")
        self.txt_tree.delete("1.0", "end")
        self.txt_tree.config(state="disabled")
        self.lbl_final_summary.config(text="Run an algorithm to inspect final queue/stack metrics, operations, and contents.")
        self.redraw()

    def _update_packet_status(self, status: str, hop: int, total_hops: int, current_router: str):
        path_str = " -> ".join(self.current_result.path) if self.current_result and self.current_result.success else "None"
        txt = f"Packet Status: {status} | Source: {self.source_id} | Destination: {self.dest_id} | Current: {current_router} | Hop: {hop} / {total_hops} | Route: [{path_str}]"
        self.lbl_packet_info.config(text=txt)

    def start_packet_animation(self):
        if not self.current_result or not self.current_result.success or not self.current_result.path:
            messagebox.showinfo("No Route Available", "Run BFS or DFS to discover a valid path before animating packets.", parent=self)
            return

        for r_id in self.current_result.path:
            if r_id not in self.graph.routers or not self.graph.routers[r_id].is_online:
                messagebox.showerror("Router Offline", f"Router '{r_id}' along the route is offline or removed. Rerun algorithm.", parent=self)
                self.console.log(f"Packet animation aborted: Router '{r_id}' is offline. Please rerun traversal.", "error")
                return

        path = self.current_result.path
        for i in range(len(path) - 1):
            key = tuple(sorted((path[i], path[i + 1])))
            if key not in self.graph.edges:
                messagebox.showerror("Link Removed", f"Connection ({path[i]} <-> {path[i + 1]}) was removed. Rerun algorithm.", parent=self)
                return

        self.cancel_all_animations()

        if len(path) == 1:
            self.console.log("Source is destination. 0 hops packet delivery.", "success")
            self._update_packet_status("Delivered", 0, 0, path[0])
            return

        coords = []
        for rid in path:
            r = self.graph.routers[rid]
            sx, sy = self._to_screen(r.x, r.y)
            coords.append((rid, sx, sy))

        if len(coords) < 2:
            return

        frames = []
        steps_per_segment = 14
        total_hops = len(coords) - 1

        for i in range(total_hops):
            u_id, x1, y1 = coords[i]
            v_id, x2, y2 = coords[i + 1]
            for s in range(steps_per_segment):
                t = s / float(steps_per_segment)
                fx = x1 + t * (x2 - x1)
                fy = y1 + t * (y2 - y1)
                active_r = u_id if t < 0.5 else v_id
                frames.append((fx, fy, active_r, i + 1, total_hops))

        last_id, lx, ly = coords[-1]
        frames.append((lx, ly, last_id, total_hops, total_hops))

        self._packet_frames = frames
        self._packet_frame_idx = 0
        self._packet_running = True
        self._packet_paused = False
        self.control_bar.set_running_state(True)
        self.console.log(f"Transmitting packet along discovered route: {' -> '.join(path)}", "info")
        self._step_packet_frame()

    def _step_packet_frame(self):
        if not self._packet_running:
            return
        if self._packet_frame_idx < len(self._packet_frames):
            x, y, curr_r, hop_num, total_hops = self._packet_frames[self._packet_frame_idx]
            self._render_packet_on_canvas(x, y)
            self._update_packet_status(f"Transmitting Hop {hop_num} / {total_hops}", hop_num, total_hops, curr_r)
            self._packet_frame_idx += 1
            delay = max(20, int(self.sim_service.speed_ms / 14))
            self._packet_timer = self.after(delay, self._step_packet_frame)
        else:
            self._on_packet_delivered()

    def _step_packet_single(self):
        if self._packet_frame_idx < len(self._packet_frames):
            x, y, curr_r, hop_num, total_hops = self._packet_frames[self._packet_frame_idx]
            self._render_packet_on_canvas(x, y)
            self._update_packet_status(f"Stepping Hop {hop_num} / {total_hops}", hop_num, total_hops, curr_r)
            self._packet_frame_idx += 1
        else:
            self._on_packet_delivered()

    def _render_packet_on_canvas(self, x: float, y: float):
        self.canvas.delete("packet")
        r = 10 * self.scale
        self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=Theme.PURPLE, outline="#FFFFFF", width=2.5, tags="packet"
        )
        self.canvas.create_text(
            x, y, text="✉", fill="#FFFFFF",
            font=("Helvetica", max(8, int(9 * self.scale)), "bold"), tags="packet"
        )

    def _on_packet_delivered(self):
        self.canvas.delete("packet")
        self._packet_running = False
        self._packet_paused = False
        self.control_bar.set_running_state(False)
        total_hops = len(self.current_result.path) - 1 if self.current_result and self.current_result.path else 0
        self._update_packet_status("Delivered", total_hops, total_hops, self.dest_id)
        self.console.log(f"Packet delivered successfully to destination '{self.dest_id}' in {total_hops} hops!", "success")

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
        margin = 75.0
        scale_x = (cw - 2 * margin) / w
        scale_y = (ch - 2 * margin) / h
        self.scale = max(0.4, min(1.8, min(scale_x, scale_y)))
        self.offset_x = margin + (cw - 2 * margin - w * self.scale) / 2 - min_x * self.scale
        self.offset_y = margin + (ch - 2 * margin - h * self.scale) / 2 - min_y * self.scale
        self.redraw()

    def _check_canvas_bounds(self):
        if self.graph.routers:
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
            if dist <= 28:
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
        self._update_all_statistics()

    def _on_canvas_right_click(self, event):
        wx, wy = self._to_world(event.x, event.y)
        clicked_router = None
        for rid, r in self.graph.routers.items():
            dist = math.hypot(r.x - wx, r.y - wy)
            if dist <= 28:
                clicked_router = rid
                break

        if clicked_router:
            self.selected_router = clicked_router
            self.redraw()
            menu = tk.Menu(self, tearoff=0, font=Theme.FONT_BODY)
            menu.add_command(label=f"Set '{clicked_router}' as Source", command=lambda: self._set_as_source(clicked_router))
            menu.add_command(label=f"Set '{clicked_router}' as Destination", command=lambda: self._set_as_dest(clicked_router))
            menu.add_separator()
            st = self.graph.routers[clicked_router].is_online
            menu.add_command(label=f"Toggle Power ({'Turn Off' if st else 'Turn On'})", command=self._toggle_selected_power)
            menu.add_command(label=f"Delete Router '{clicked_router}'", command=self._remove_selected_router)
            menu.tk_popup(event.x_root, event.y_root)
        else:
            self._on_pan_press(event)

    def _set_as_source(self, rid: str):
        self.source_id = rid
        self.cb_src.set(rid)
        self.reset_simulation()
        self.redraw()
        self._update_all_statistics()
        self.console.log(f"Set '{rid}' as source router.", "info")

    def _set_as_dest(self, rid: str):
        self.dest_id = rid
        self.cb_dst.set(rid)
        self.reset_simulation()
        self.redraw()
        self._update_all_statistics()
        self.console.log(f"Set '{rid}' as destination router.", "info")

    def _add_router_dialog(self):
        dlg = AddRouterDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            rid, rname = dlg.result
            if rid in self.graph.routers:
                messagebox.showerror("Duplicate Router ID", f"A router with ID '{rid}' already exists.", parent=self)
                return
            cw = max(self.canvas.winfo_width(), 400) / 2
            ch = max(self.canvas.winfo_height(), 300) / 2
            wx, wy = self._to_world(cw, ch)
            if self.graph.add_router(rid, rname, wx, wy):
                nodes = sorted(self.graph.routers.keys())
                self.cb_src["values"] = nodes
                self.cb_dst["values"] = nodes
                self.reset_simulation()
                self.redraw()
                self._update_all_statistics()
                self.console.log(f"Added router '{rid}' ({rname}) at ({wx:.1f}, {wy:.1f}).", "success")
            else:
                messagebox.showerror("Error", f"Failed to add router '{rid}'.", parent=self)

    def _remove_selected_router(self):
        if not self.selected_router:
            messagebox.showinfo("Selection Required", "Click a router on the canvas to select it first.", parent=self)
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
            self._update_all_statistics()
            self.console.log(f"Removed router '{rid}' and all associated links.", "info")

    def _add_link_dialog(self):
        nodes = sorted(self.graph.routers.keys())
        if len(nodes) < 2:
            messagebox.showinfo("Insufficient Routers", "At least two routers are required to form a connection.", parent=self)
            return
        dlg = AddLinkDialog(self, nodes)
        self.wait_window(dlg)
        if dlg.result:
            u, v = dlg.result
            if self.graph.add_edge(u, v, 1.0):
                self.reset_simulation()
                self.redraw()
                self._update_all_statistics()
                self.console.log(f"Connected link between '{u}' and '{v}'.", "success")
            else:
                messagebox.showwarning("Connection Exists", f"Connection between '{u}' and '{v}' already exists.", parent=self)

    def _remove_link_dialog(self):
        edges = list(self.graph.edges.keys())
        if not edges:
            messagebox.showinfo("No Connections", "There are no network connections to remove.", parent=self)
            return
        dlg = RemoveLinkDialog(self, edges)
        self.wait_window(dlg)
        if dlg.result:
            u, v = dlg.result
            if self.graph.remove_edge(u, v):
                self.reset_simulation()
                self._update_all_statistics()
                self.console.log(f"Removed connection between '{u}' and '{v}'.", "info")

    def _toggle_selected_power(self):
        if not self.selected_router:
            messagebox.showinfo("Selection Required", "Click a router on the canvas to select it first.", parent=self)
            return
        st = self.graph.toggle_router_status(self.selected_router)
        state_str = "ONLINE" if st else "OFFLINE"
        lvl = "info" if st else "warning"
        self.console.log(f"Router '{self.selected_router}' power state toggled to {state_str}.", lvl)
        self.reset_simulation()
        self._update_all_statistics()
        self.redraw()

    def save_topology_json(self):
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Topology as JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if not path:
            return
        try:
            data = self.graph.to_dict()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.console.log(f"Topology saved successfully to {path}", "success")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save topology: {e}", parent=self)

    def load_topology_json(self):
        path = filedialog.askopenfilename(
            parent=self,
            title="Load Topology from JSON",
            filetypes=[("JSON Files", "*.json")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.cancel_all_animations()
            self.graph.load_from_dict(data)
            nodes = sorted(self.graph.routers.keys())
            self.cb_src["values"] = nodes
            self.cb_dst["values"] = nodes
            if nodes:
                self.source_id = nodes[0]
                self.dest_id = nodes[-1]
                self.cb_src.set(self.source_id)
                self.cb_dst.set(self.dest_id)
            self.reset_simulation()
            self.fit_to_view()
            self._update_all_statistics()
            self.console.log(f"Loaded topology successfully from {path}", "success")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load topology: {e}", parent=self)

    def _update_all_statistics(self):
        self._update_representations()
        v_count = len(self.graph.routers)
        e_count = len(self.graph.edges)
        self.stat_v_e.update_val(f"{v_count} / {e_count}")

        reachable_set = self.graph.get_reachable_routers(self.source_id)
        online_count = sum(1 for r in self.graph.routers.values() if r.is_online)
        self.stat_reach.update_val(f"{len(reachable_set)} / {online_count}", "Online Reachable")

        comps = self.graph.get_connected_components()
        comp_count = len(comps)
        status = "Connected Graph" if comp_count <= 1 else f"Disconnected ({comp_count} Subnets)"
        color = Theme.SUCCESS if comp_count <= 1 else Theme.WARNING
        self.stat_comps.update_val(str(comp_count), status)

    def _update_representations(self):
        adj_list = self.graph.get_adjacency_list()
        nodes, matrix = self.graph.get_adjacency_matrix()

        # Update Adjacency List Tab
        list_txt = "=== ADJACENCY LIST  O(V + E) ===\n"
        list_txt += "Storage: O(V + E) auxiliary space | Best for sparse, dynamic networks.\n"
        list_txt += "Each router maintains an explicit list of active connected neighbors:\n\n"
        for u, neighbors in adj_list.items():
            st = "" if self.graph.routers[u].is_online else " [OFFLINE]"
            nbr_str = ", ".join(neighbors) if neighbors else "(isolated)"
            list_txt += f"  Router {u:<4}{st:<11} ---> [ {nbr_str} ]\n"

        comps = self.graph.get_connected_components()
        reach = self.graph.get_reachable_routers(self.source_id)
        is_dst_reach = self.dest_id in reach

        list_txt += f"\nConnectivity Diagnostics:\n"
        list_txt += f"• Number of Connected Components: {len(comps)}\n"
        for i, c in enumerate(comps, 1):
            list_txt += f"   - Component {i}: {{{', '.join(sorted(c))}}}\n"
        list_txt += f"• Reachable from Source '{self.source_id}': {len(reach)} routers\n"
        list_txt += f"• Destination '{self.dest_id}' Reachable from Source: {'YES' if is_dst_reach else 'NO'}\n"

        self.txt_adj_list.config(state="normal")
        self.txt_adj_list.delete("1.0", "end")
        self.txt_adj_list.insert("end", list_txt)
        self.txt_adj_list.config(state="disabled")

        # Update Adjacency Matrix Tab
        mat_txt = "=== ADJACENCY MATRIX  O(V²) ===\n"
        mat_txt += "Storage: O(V²) fixed grid | Best for dense lookup: O(1) edge existence check.\n"
        mat_txt += "Row index represents Source, Column index represents Destination:\n\n     "
        for n in nodes:
            mat_txt += f"{n:>6}"
        mat_txt += "\n     " + ("------" * len(nodes)) + "\n"
        for i, u in enumerate(nodes):
            mat_txt += f"{u:>4} |"
            for j in range(len(nodes)):
                val = int(matrix[i][j])
                mat_txt += f"{val:>6}"
            mat_txt += "\n"

        self.txt_adj_matrix.config(state="normal")
        self.txt_adj_matrix.delete("1.0", "end")
        self.txt_adj_matrix.insert("end", mat_txt)
        self.txt_adj_matrix.config(state="disabled")

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
            edge_tuple = tuple(sorted((u, v)))
            is_active_edge = (edge_tuple in path_edges) or (self.active_edge == edge_tuple)

            if not r1.is_online or not r2.is_online:
                line_color = "#E2E8F0"
                line_width = 2.0
            elif is_active_edge:
                line_color = Theme.COLOR_ROUTE
                line_width = 4.0
            else:
                line_color = "#94A3B8"
                line_width = 2.2

            self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=line_width, tags="graph")

        node_r = 20 * self.scale
        for rid, r in self.graph.routers.items():
            x, y = self._to_screen(r.x, r.y)

            if not r.is_online:
                fill_color = Theme.COLOR_OFFLINE
            elif rid == self.current_node:
                fill_color = Theme.COLOR_EXPLORE
            elif rid in self.active_path:
                fill_color = Theme.COLOR_ROUTE
            elif rid == self.source_id:
                fill_color = Theme.SECONDARY
            elif rid == self.dest_id:
                fill_color = Theme.SUCCESS
            elif rid in self.visited_nodes:
                fill_color = Theme.COLOR_VISITED
            else:
                fill_color = Theme.PRIMARY

            outline_color = "#1D4ED8" if rid == self.selected_router else ("#0F172A" if r.is_online else "#64748B")
            outline_width = 3.5 if rid == self.selected_router else 1.5

            self.canvas.create_oval(
                x - node_r, y - node_r, x + node_r, y + node_r,
                fill=fill_color, outline=outline_color, width=outline_width, tags="graph"
            )

            font_sz = max(9, int(11 * self.scale))
            text_color = "#0F172A" if fill_color in (Theme.COLOR_VISITED, Theme.COLOR_EXPLORE) else "#FFFFFF"
            self.canvas.create_text(
                x, y,
                text=rid, fill=text_color, font=("Helvetica", font_sz, "bold"), tags="graph"
            )

            status_tag = "" if r.is_online else " (OFFLINE)"
            lbl_color = Theme.ERROR if not r.is_online else Theme.TEXT_MUTED
            self.canvas.create_text(
                x, y + node_r + 11,
                text=f"{r.name}{status_tag}", fill=lbl_color, font=("Helvetica", max(8, font_sz - 1), "bold" if not r.is_online else "normal"), tags="graph"
            )

            if rid in self.visited_order:
                order_num = self.visited_order.index(rid) + 1
                bx = x + node_r * 0.75
                by = y - node_r * 0.75
                br = 8.5 * self.scale
                self.canvas.create_oval(
                    bx - br, by - br, bx + br, by + br,
                    fill=Theme.WARNING, outline="#FFFFFF", width=1.5, tags="graph"
                )
                self.canvas.create_text(
                    bx, by,
                    text=str(order_num), fill="#172033",
                    font=("Helvetica", max(7, int(8.5 * self.scale)), "bold"), tags="graph"
                )

        self.canvas.tag_raise("legend")
