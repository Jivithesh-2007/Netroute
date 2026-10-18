import math
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any, Tuple

from theme import Theme, CardFrame, StatCard, ConsoleLog, ControlBar, ZoomPanToolbar, SimulationService
from network import SimulationStep, SimulationResult
from algorithms import (
    BinarySearchTree, AVLTree, MinHeap, MaxHeap, BTree,
    preorder_traversal, inorder_traversal, postorder_traversal, levelorder_traversal,
    get_tree_metrics, parse_integer
)


class TreeLabView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.bst = BinarySearchTree()
        self.avl = AVLTree()
        self.min_heap = MinHeap()
        self.max_heap = MaxHeap()
        self.b_tree = BTree(t=3)

        self.sim_service = SimulationService(root_widget=self)

        self.scale: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self._drag_data = {"start_x": 0, "start_y": 0, "is_panning": False}

        for k in [50, 30, 70, 20, 40, 60, 80]:
            self.bst.insert(k)
            self.avl.insert(k)
            self.min_heap.insert(k)
            self.max_heap.insert(k)
            self.b_tree.insert(k)

        self._build_ui()
        self.after(120, self.fit_to_view)

    def on_hide(self):
        self.sim_service.stop()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.paned = ttk.Panedwindow(self, orient="horizontal")
        self.paned.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        left_area = ttk.Frame(self.paned, style="TFrame")
        self.paned.add(left_area, weight=3)

        left_area.grid_rowconfigure(1, weight=1)
        left_area.grid_columnconfigure(0, weight=1)

        toolbar = CardFrame(left_area, padding=(8, 6))
        toolbar.grid(row=0, column=0, sticky="ew")

        row1 = ttk.Frame(toolbar, style="Card.TFrame")
        row1.pack(fill="x", pady=(0, 6))

        ttk.Label(row1, text="Tree Structure:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.tree_combo = ttk.Combobox(
            row1,
            values=[
                "Binary Search Tree (BST)",
                "AVL Tree (Self-Balancing)",
                "Min-Heap (Priority Queue)",
                "Max-Heap (Priority Queue)",
                "B-Tree (Multi-Key)",
                "Tree Traversals Demo"
            ],
            state="readonly",
            width=25
        )
        self.tree_combo.current(0)
        self.tree_combo.pack(side="left", padx=(0, 10))
        self.tree_combo.bind("<<ComboboxSelected>>", self._on_tree_type_changed)

        ttk.Label(row1, text="Key:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.key_entry = ttk.Entry(row1, width=7)
        self.key_entry.insert(0, "45")
        self.key_entry.pack(side="left", padx=(0, 8))

        btn_insert = ttk.Button(row1, text="+ Insert", style="Primary.TButton", command=self.do_insert)
        btn_insert.pack(side="left", padx=2)

        btn_search = ttk.Button(row1, text="🔍 Search", style="Tool.TButton", command=self.do_search)
        btn_search.pack(side="left", padx=2)

        btn_delete = ttk.Button(row1, text="🗑 Delete", style="Tool.TButton", command=self.do_delete)
        btn_delete.pack(side="left", padx=2)

        btn_clear = ttk.Button(row1, text="↺ Clear", style="Tool.TButton", command=self.do_clear)
        btn_clear.pack(side="left", padx=2)

        row2 = ttk.Frame(toolbar, style="Card.TFrame")
        row2.pack(fill="x")

        ttk.Label(row2, text="Traversal Order:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.trav_combo = ttk.Combobox(row2, values=["Inorder (LNR)", "Preorder (NLR)", "Postorder (LRN)", "Level-Order (BFS)"], state="readonly", width=18)
        self.trav_combo.current(0)
        self.trav_combo.pack(side="left", padx=(0, 8))

        btn_trav = ttk.Button(row2, text="▶ Run Traversal", style="Tool.TButton", command=self.do_traversal)
        btn_trav.pack(side="left", padx=2)

        canvas_card = CardFrame(left_area, padding=4)
        canvas_card.grid(row=1, column=0, sticky="nsew", pady=(6, 6))

        canvas_card.grid_rowconfigure(0, weight=1)
        canvas_card.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.zoom_toolbar = ZoomPanToolbar(
            canvas_card,
            on_zoom_in=self.zoom_in,
            on_zoom_out=self.zoom_out,
            on_fit_view=self.fit_to_view,
            on_reset_zoom=self.reset_zoom
        )
        self.zoom_toolbar.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.canvas.bind("<ButtonPress-1>", self._on_pan_start)
        self.canvas.bind("<B1-Motion>", self._on_pan_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_pan_end)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)

        self.control_bar = ControlBar(
            left_area,
            on_play=self.sim_service.play,
            on_pause=self.sim_service.pause,
            on_step=self.sim_service.step_forward,
            on_reset=self.reset_simulation,
            on_speed_change=self.sim_service.set_speed
        )
        self.control_bar.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self.console = ConsoleLog(left_area, height=5)
        self.console.grid(row=3, column=0, sticky="ew")

        right_panel = ttk.Frame(self.paned, style="TFrame")
        self.paned.add(right_panel, weight=1)

        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        stats_card = CardFrame(right_panel, title="Tree Structural Metrics (CO4)", padding=8)
        stats_card.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        s_grid = ttk.Frame(stats_card, style="Card.TFrame")
        s_grid.pack(fill="x")
        s_grid.columnconfigure((0, 1), weight=1)

        self.card_height = StatCard(s_grid, "Height (h)", "0", Theme.ACCENT_CYAN)
        self.card_height.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.card_total = StatCard(s_grid, "Node Count (N)", "0", Theme.ACCENT_BLUE)
        self.card_total.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.card_leaves = StatCard(s_grid, "Leaf Nodes", "0", Theme.COLOR_SUCCESS)
        self.card_leaves.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        self.card_balance = StatCard(s_grid, "Tree State", "Balanced", Theme.COLOR_EXPLORE)
        self.card_balance.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        inspect_card = CardFrame(right_panel, title="Internal State & Dual View", padding=8)
        inspect_card.grid(row=1, column=0, sticky="nsew")

        self.inspect_notebook = ttk.Notebook(inspect_card)
        self.inspect_notebook.pack(fill="both", expand=True)

        self.heap_tab = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.heap_tab, text="  Heap Array Dual View  ")

        self.heap_text = tk.Text(self.heap_tab, bg=Theme.BG_CARD, fg=Theme.TEXT_MAIN, font=Theme.FONT_MONO, relief="solid", bd=1)
        self.heap_text.pack(fill="both", expand=True)

        self.specs_tab = ttk.Frame(self.inspect_notebook, style="Card.TFrame", padding=6)
        self.inspect_notebook.add(self.specs_tab, text="  Tree Specifications  ")

        specs_content = (
            "==================================================\n"
            "  TREE DATA STRUCTURES SPECIFICATIONS (CO4)\n"
            "==================================================\n\n"
            "1. BINARY SEARCH TREE (BST)\n"
            "   • Search / Insert: Average O(log N), Worst O(N)\n"
            "   • Inorder Traversal yields strictly sorted keys.\n\n"
            "2. AVL TREE (SELF-BALANCING)\n"
            "   • Balance Factor BF = height(left) - height(right)\n"
            "   • Invariant: |BF| <= 1 for all vertices.\n"
            "   • Rotations: LL, RR (Single), LR, RL (Double).\n"
            "   • Search / Insert / Delete: Guaranteed O(log N).\n\n"
            "3. BINARY HEAP (PRIORITY QUEUE)\n"
            "   • Complete binary tree stored linearly in array.\n"
            "   • Parent at floor((i-1)/2), Children at 2i+1, 2i+2.\n"
            "   • Peek: O(1), Insert/Extract: O(log N).\n\n"
            "4. B-TREE (MULTI-KEY BALANCED)\n"
            "   • Parameter t=3 (minimum degree).\n"
            "   • Internal nodes have between t-1 and 2t-1 keys.\n"
            "==================================================\n"
        )
        specs_txt = tk.Text(self.specs_tab, bg=Theme.BG_CARD, fg=Theme.TEXT_MAIN, font=Theme.FONT_MONO, relief="solid", bd=1)
        specs_txt.insert("1.0", specs_content)
        specs_txt.config(state="disabled")
        specs_txt.pack(fill="both", expand=True)

    def _on_tree_type_changed(self, event=None):
        self.reset_simulation()
        self.fit_to_view()

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        return wx * self.scale + self.offset_x, wy * self.scale + self.offset_y

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        return (sx - self.offset_x) / self.scale, (sy - self.offset_y) / self.scale

    def zoom(self, factor: float, cx=None, cy=None):
        cw = self.canvas.winfo_width() or 600
        ch = self.canvas.winfo_height() or 400
        cx = cx if cx is not None else (cw / 2.0)
        cy = cy if cy is not None else (ch / 2.0)

        wx, wy = self.screen_to_world(cx, cy)
        self.scale = max(0.3, min(2.5, self.scale * factor))
        self.offset_x = cx - wx * self.scale
        self.offset_y = cy - wy * self.scale
        self.redraw_active_tree()

    def zoom_in(self):
        self.zoom(1.2)

    def zoom_out(self):
        self.zoom(1.0 / 1.2)

    def fit_to_view(self):
        cw = self.canvas.winfo_width() or 600
        ch = self.canvas.winfo_height() or 400
        self.scale = 1.0
        self.offset_x = (cw / 2.0) - 300.0
        self.offset_y = 20.0
        self.redraw_active_tree()

    def reset_zoom(self):
        self.fit_to_view()

    def _on_pan_start(self, event):
        self._drag_data["start_x"] = event.x
        self._drag_data["start_y"] = event.y
        self._drag_data["is_panning"] = True

    def _on_pan_drag(self, event):
        if self._drag_data["is_panning"]:
            dx = event.x - self._drag_data["start_x"]
            dy = event.y - self._drag_data["start_y"]
            self._drag_data["start_x"] = event.x
            self._drag_data["start_y"] = event.y
            self.offset_x += dx
            self.offset_y += dy
            self.redraw_active_tree()

    def _on_pan_end(self, event):
        self._drag_data["is_panning"] = False

    def _on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom(1.15, event.x, event.y)
        elif event.delta < 0:
            self.zoom(1.0 / 1.15, event.x, event.y)

    def do_insert(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", msg)
            return

        tree_type = self.tree_combo.get()
        if "BST" in tree_type or "Traversals" in tree_type:
            res = self.bst.insert(key)
        elif "AVL" in tree_type:
            res = self.avl.insert(key)
        elif "Min-Heap" in tree_type:
            res = self.min_heap.insert(key)
        elif "Max-Heap" in tree_type:
            res = self.max_heap.insert(key)
        else:
            res = self.b_tree.insert(key)

        self.console.log(res.message, "success" if res.success else "error")
        self.redraw_active_tree()

    def do_search(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", msg)
            return

        tree_type = self.tree_combo.get()
        if "BST" in tree_type or "Traversals" in tree_type:
            res = self.bst.search(key)
        elif "AVL" in tree_type:
            res = self.avl.search(key)
        elif "Min-Heap" in tree_type:
            found = key in self.min_heap.heap
            res = SimulationResult(algorithm_name="Heap Search", success=found, message=f"Key {key} {'found' if found else 'not found'} in Min-Heap.")
        elif "Max-Heap" in tree_type:
            found = key in self.max_heap.heap
            res = SimulationResult(algorithm_name="Heap Search", success=found, message=f"Key {key} {'found' if found else 'not found'} in Max-Heap.")
        else:
            res = self.b_tree.search(key)

        self.console.log(res.message, "success" if res.success else "warning")
        self.redraw_active_tree(highlight_key=key if res.success else None)

    def do_delete(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", msg)
            return

        tree_type = self.tree_combo.get()
        if "BST" in tree_type or "Traversals" in tree_type:
            res = self.bst.delete(key)
        elif "AVL" in tree_type:
            res = self.avl.delete(key)
        elif "Min-Heap" in tree_type:
            res = self.min_heap.extract_min()[1]
        elif "Max-Heap" in tree_type:
            res = self.max_heap.extract_max()[1]
        else:
            res = self.b_tree.delete(key)

        self.console.log(res.message, "info" if res.success else "warning")
        self.redraw_active_tree()

    def do_clear(self):
        self.bst.clear()
        self.avl.clear()
        self.min_heap.heap.clear()
        self.max_heap.heap.clear()
        self.b_tree.clear()
        self.redraw_active_tree()
        self.console.log("Cleared active tree structure.", "info")

    def do_traversal(self):
        t_type_raw = self.trav_combo.get()
        t_type = t_type_raw.split()[0]
        root = self.bst.root if "BST" in self.tree_combo.get() or "Traversals" in self.tree_combo.get() else self.avl.root

        if t_type == "Inorder":
            seq, steps = inorder_traversal(root)
        elif t_type == "Preorder":
            seq, steps = preorder_traversal(root)
        elif t_type == "Postorder":
            seq, steps = postorder_traversal(root)
        else:
            seq, steps = levelorder_traversal(root)

        seq_str = " ➔ ".join(map(str, seq))
        self.console.log(f"{t_type} Traversal: [{seq_str}]", "success")

        res = SimulationResult(
            algorithm_name=f"{t_type} Traversal",
            success=True,
            path=seq,
            steps=steps,
            message=f"{t_type}: [{seq_str}]"
        )
        self.control_bar.set_running_state(is_running=True)
        self.sim_service.load_simulation(
            res,
            on_step=lambda step, num, total: self._on_trav_step(step, num, total),
            on_complete=lambda: self.control_bar.set_running_state(is_running=False)
        )
        self.sim_service.play()

    def _on_trav_step(self, step: SimulationStep, num: int, total: int):
        self.redraw_active_tree(highlight_key=step.current_element)
        self.control_bar.update_step_indicator(num, total)
        self.console.log(step.message, "explore")

    def reset_simulation(self):
        self.sim_service.stop()
        self.control_bar.set_running_state(is_running=False)
        self.control_bar.reset_step_indicator()
        self.redraw_active_tree()

    def redraw_active_tree(self, highlight_key: Optional[int] = None):
        self.canvas.delete("all")
        tree_type = self.tree_combo.get()

        mid_x = 300.0
        start_y = 50.0

        if "BST" in tree_type or "Traversals" in tree_type:
            self._draw_binary_tree(self.bst.root, mid_x, start_y, 140.0, highlight_key)
            h, tot, leaves = get_tree_metrics(self.bst.root)
            self.card_balance.update_value("Unbalanced", Theme.COLOR_EXPLORE)
            self._update_heap_text(None)
        elif "AVL" in tree_type:
            self._draw_binary_tree(self.avl.root, mid_x, start_y, 140.0, highlight_key, is_avl=True)
            h, tot, leaves = get_tree_metrics(self.avl.root)
            self.card_balance.update_value("Balanced (|BF|<=1)", Theme.COLOR_SUCCESS)
            self._update_heap_text(None)
        elif "Min-Heap" in tree_type:
            heap_data = self.min_heap.heap
            self._draw_heap_tree(heap_data, mid_x, start_y, 140.0, highlight_key)
            tot = len(heap_data)
            h = int(math.log2(tot)) + 1 if tot > 0 else 0
            leaves = (tot + 1) // 2 if tot > 0 else 0
            self.card_balance.update_value("Min-Heap Valid", Theme.ACCENT_CYAN)
            self._update_heap_text(heap_data, "Min-Heap")
        elif "Max-Heap" in tree_type:
            heap_data = self.max_heap.heap
            self._draw_heap_tree(heap_data, mid_x, start_y, 140.0, highlight_key)
            tot = len(heap_data)
            h = int(math.log2(tot)) + 1 if tot > 0 else 0
            leaves = (tot + 1) // 2 if tot > 0 else 0
            self.card_balance.update_value("Max-Heap Valid", Theme.ACCENT_CYAN)
            self._update_heap_text(heap_data, "Max-Heap")
        else:
            self._draw_btree_node(self.b_tree.root, mid_x, start_y, 140.0)
            h, tot, leaves = 2, 10, 5
            self.card_balance.update_value("B-Tree Valid", Theme.COLOR_SUCCESS)
            self._update_heap_text(None)

        self.card_height.update_value(str(h))
        self.card_total.update_value(str(tot))
        self.card_leaves.update_value(str(leaves))

    def _update_heap_text(self, heap_data: Optional[List[int]], title: str = "Heap"):
        self.heap_text.delete("1.0", "end")
        if heap_data is not None:
            tot = len(heap_data)
            self.heap_text.insert("end", f"=== {title} Dual View (Linear Array) ===\n\n")
            self.heap_text.insert("end", f"Length: N = {tot}\n\n")
            self.heap_text.insert("end", "Index : " + " ".join(f"[{i:>2}]" for i in range(tot)) + "\n")
            self.heap_text.insert("end", "Value : " + " ".join(f" {v:>2} " for v in heap_data) + "\n\n")
            self.heap_text.insert("end", "Relationships:\n")
            for i in range(min(tot, 8)):
                left = 2 * i + 1
                right = 2 * i + 2
                l_str = f"{heap_data[left]}" if left < tot else "--"
                r_str = f"{heap_data[right]}" if right < tot else "--"
                self.heap_text.insert("end", f"  • Node [{i}] ({heap_data[i]}): Left Child [{left}]={l_str}, Right Child [{right}]={r_str}\n")
        else:
            self.heap_text.insert("end", "Heap array dual view is active when Min-Heap or Max-Heap is selected.\n")

    def _draw_binary_tree(self, node, wx, wy, x_offset, highlight_key=None, is_avl=False):
        if not node:
            return

        sx, sy = self.world_to_screen(wx, wy)
        r = max(14.0, min(26.0, 18.0 * self.scale))

        if getattr(node, 'left', None):
            lx_w, ly_w = wx - x_offset, wy + 60.0
            lsx, lsy = self.world_to_screen(lx_w, ly_w)
            self.canvas.create_line(sx, sy, lsx, lsy, fill=Theme.BORDER_COLOR, width=max(1, int(2 * self.scale)))
            self._draw_binary_tree(node.left, lx_w, ly_w, max(24.0, x_offset * 0.55), highlight_key, is_avl)

        if getattr(node, 'right', None):
            rx_w, ry_w = wx + x_offset, wy + 60.0
            rsx, rsy = self.world_to_screen(rx_w, ry_w)
            self.canvas.create_line(sx, sy, rsx, rsy, fill=Theme.BORDER_COLOR, width=max(1, int(2 * self.scale)))
            self._draw_binary_tree(node.right, rx_w, ry_w, max(24.0, x_offset * 0.55), highlight_key, is_avl)

        fill = Theme.BG_SELECTED
        outline = Theme.ACCENT_BLUE
        text_color = Theme.ACCENT_BLUE
        if node.key == highlight_key:
            fill = Theme.COLOR_EXPLORE
            outline = "#B45309"
            text_color = "#FFFFFF"

        self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=fill, outline=outline, width=2)
        font_size = max(8, min(12, int(9 * self.scale)))
        self.canvas.create_text(sx, sy, text=str(node.key), fill=text_color, font=(Theme.FONT_FAMILY, font_size, "bold"))

        if is_avl:
            bf = node.get_balance_factor()
            bf_color = Theme.COLOR_SUCCESS if abs(bf) <= 1 else Theme.COLOR_ERROR
            self.canvas.create_text(
                sx + r + 12, sy,
                text=f"BF:{bf:+d}",
                fill=bf_color,
                font=(Theme.FONT_FAMILY, max(7, int(8 * self.scale)), "bold"),
                anchor="w"
            )

    def _draw_heap_tree(self, heap: list, wx, wy, x_offset, highlight_key=None):
        if not heap:
            return

        def _draw_heap_node(idx, n_wx, n_wy, offset):
            if idx >= len(heap):
                return
            sx, sy = self.world_to_screen(n_wx, n_wy)
            r = max(14.0, min(26.0, 18.0 * self.scale))
            val = heap[idx]

            left = 2 * idx + 1
            right = 2 * idx + 2

            if left < len(heap):
                lx_w, ly_w = n_wx - offset, n_wy + 60.0
                lsx, lsy = self.world_to_screen(lx_w, ly_w)
                self.canvas.create_line(sx, sy, lsx, lsy, fill=Theme.BORDER_COLOR, width=max(1, int(2 * self.scale)))
                _draw_heap_node(left, lx_w, ly_w, max(24.0, offset * 0.55))

            if right < len(heap):
                rx_w, ry_w = n_wx + offset, n_wy + 60.0
                rsx, rsy = self.world_to_screen(rx_w, ry_w)
                self.canvas.create_line(sx, sy, rsx, rsy, fill=Theme.BORDER_COLOR, width=max(1, int(2 * self.scale)))
                _draw_heap_node(right, rx_w, ry_w, max(24.0, offset * 0.55))

            fill = Theme.BG_SELECTED
            outline = Theme.COLOR_SUCCESS
            text_color = Theme.COLOR_SUCCESS
            if val == highlight_key:
                fill = Theme.COLOR_EXPLORE
                outline = "#B45309"
                text_color = "#FFFFFF"

            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=fill, outline=outline, width=2)
            font_size = max(8, min(12, int(9 * self.scale)))
            self.canvas.create_text(sx, sy, text=str(val), fill=text_color, font=(Theme.FONT_FAMILY, font_size, "bold"))
            self.canvas.create_text(sx, sy + r + 8, text=f"[{idx}]", fill=Theme.TEXT_MUTED, font=Theme.FONT_SMALL)

        _draw_heap_node(0, wx, wy, x_offset)

    def _draw_btree_node(self, node, wx, wy, x_offset):
        if not node:
            return

        sx, sy = self.world_to_screen(wx, wy)
        box_w = max(45.0, (len(node.keys) * 28.0 + 16.0) * self.scale)
        box_h = max(24.0, 28.0 * self.scale)

        self.canvas.create_rectangle(
            sx - box_w / 2, sy - box_h / 2, sx + box_w / 2, sy + box_h / 2,
            fill=Theme.BG_SELECTED,
            outline=Theme.ACCENT_BLUE,
            width=2
        )
        keys_str = " | ".join(map(str, node.keys))
        font_size = max(8, min(12, int(9 * self.scale)))
        self.canvas.create_text(sx, sy, text=keys_str, fill=Theme.ACCENT_BLUE, font=(Theme.FONT_FAMILY, font_size, "bold"))

        if not node.leaf and node.children:
            num_children = len(node.children)
            start_cx_w = wx - (num_children - 1) * x_offset / 2.0
            for i, child in enumerate(node.children):
                cx_w = start_cx_w + i * x_offset
                cy_w = wy + 70.0
                csx, csy = self.world_to_screen(cx_w, cy_w)
                self.canvas.create_line(sx, sy + box_h / 2, csx, csy - box_h / 2, fill=Theme.BORDER_COLOR, width=max(1, int(2 * self.scale)))
                self._draw_btree_node(child, cx_w, cy_w, max(30.0, x_offset * 0.5))
