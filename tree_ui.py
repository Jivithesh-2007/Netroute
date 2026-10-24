import math
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any, Tuple
from theme import Theme, CardFrame, StatCard, ConsoleLog, ZoomPanToolbar
from algorithms import (
    BinarySearchTree, AVLTree, MinHeap, MaxHeap, BTree,
    parse_integer
)

class TreeLabView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.tree_type = "bst"
        self.bst = BinarySearchTree()
        self.avl = AVLTree()
        self.min_heap = MinHeap()
        self.max_heap = MaxHeap()
        self.b_tree = BTree(t=2)

        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self._drag_data = {"start_x": 0, "start_y": 0}

        self.highlighted_nodes = []
        self.search_path = []

        self.load_sample_data()
        self._build_ui()
        self.after(150, self.fit_to_view)

    def load_sample_data(self):
        self.bst = BinarySearchTree()
        self.avl = AVLTree()
        self.min_heap = MinHeap()
        self.max_heap = MaxHeap()
        self.b_tree = BTree(t=2)

        sample_keys = [50, 30, 70, 20, 40, 60, 80]
        for k in sample_keys:
            self.bst.insert(k)
            self.avl.insert(k)
            self.min_heap.insert(k)
            self.max_heap.insert(k)
            self.b_tree.insert(k)

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        main_col = ttk.Frame(paned, style="TFrame")
        paned.add(main_col, weight=3)
        main_col.grid_rowconfigure(1, weight=1)
        main_col.grid_columnconfigure(0, weight=1)

        side_col = ttk.Frame(paned, style="TFrame", width=340)
        paned.add(side_col, weight=1)
        side_col.grid_rowconfigure(2, weight=1)
        side_col.grid_columnconfigure(0, weight=1)

        top_ctrl = CardFrame(main_col, padding=(8, 6))
        top_ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(top_ctrl, text="Tree Structure:", style="Card.TLabel").pack(side="left", padx=(2, 4))
        self.cb_type = ttk.Combobox(
            top_ctrl,
            values=["Binary Search Tree (BST)", "Self-Balancing AVL Tree", "Binary Min-Heap", "Binary Max-Heap", "B-Tree (Multi-Key)"],
            state="readonly",
            width=24
        )
        self.cb_type.set("Binary Search Tree (BST)")
        self.cb_type.pack(side="left", padx=2)
        self.cb_type.bind("<<ComboboxSelected>>", self._on_tree_type_change)

        ttk.Label(top_ctrl, text="Key:", style="Card.TLabel").pack(side="left", padx=(8, 2))
        self.ent_key = ttk.Entry(top_ctrl, width=6)
        self.ent_key.insert(0, "25")
        self.ent_key.pack(side="left", padx=2)

        ttk.Button(top_ctrl, text="Insert", style="Primary.TButton", command=self.on_insert).pack(side="left", padx=2)
        ttk.Button(top_ctrl, text="Search", style="Success.TButton", command=self.on_search).pack(side="left", padx=2)
        ttk.Button(top_ctrl, text="Delete", style="Danger.TButton", command=self.on_delete).pack(side="left", padx=2)
        ttk.Button(top_ctrl, text="Clear", style="Tool.TButton", command=self.on_clear).pack(side="left", padx=2)
        ttk.Button(top_ctrl, text="Sample", style="Tool.TButton", command=self.on_reload_sample).pack(side="left", padx=2)

        self.zoom_toolbar = ZoomPanToolbar(
            top_ctrl,
            on_zoom_in=lambda: self._zoom(1.15),
            on_zoom_out=lambda: self._zoom(0.85),
            on_fit_view=self.fit_to_view,
            on_reset_zoom=self._reset_zoom
        )
        self.zoom_toolbar.pack(side="right")

        canvas_card = CardFrame(main_col, padding=0)
        canvas_card.grid(row=1, column=0, sticky="nsew")
        canvas_card.grid_rowconfigure(0, weight=1)
        canvas_card.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_card, bg="#FFFFFF", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<ButtonPress-1>", self._on_pan_press)
        self.canvas.bind("<B1-Motion>", self._on_pan_drag)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom(1.1))
        self.canvas.bind("<Button-5>", lambda e: self._zoom(0.9))

        stats_row = ttk.Frame(side_col, style="TFrame")
        stats_row.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        stats_row.grid_columnconfigure(0, weight=1)
        stats_row.grid_columnconfigure(1, weight=1)

        self.stat_height = StatCard(stats_row, title="Tree Height", value="3", subtitle="Levels", color=Theme.PRIMARY, height=75)
        self.stat_height.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.stat_nodes = StatCard(stats_row, title="Total Keys", value="7", subtitle="Active elements", color=Theme.SUCCESS, height=75)
        self.stat_nodes.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        trav_card = CardFrame(side_col, padding=(8, 6))
        trav_card.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(trav_card, text="Tree Traversals & Metrics (CO4):", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))

        self.lbl_inorder = ttk.Label(trav_card, text="Inorder (L-Root-R): []", style="Card.TLabel")
        self.lbl_inorder.pack(anchor="w", pady=1)

        self.lbl_preorder = ttk.Label(trav_card, text="Preorder (Root-L-R): []", style="Card.TLabel")
        self.lbl_preorder.pack(anchor="w", pady=1)

        self.lbl_postorder = ttk.Label(trav_card, text="Postorder (L-R-Root): []", style="Card.TLabel")
        self.lbl_postorder.pack(anchor="w", pady=1)

        self.lbl_levelorder = ttk.Label(trav_card, text="Level-Order (BFS): []", style="Card.TLabel")
        self.lbl_levelorder.pack(anchor="w", pady=1)

        ttk.Separator(trav_card, orient="horizontal").pack(fill="x", pady=4)
        ttk.Button(trav_card, text="BST vs AVL Skewed Test (PrO-12)", style="Purple.TButton", command=self.test_skewed_comparison).pack(fill="x", pady=2)

        self.console = ConsoleLog(side_col, height=10)
        self.console.grid(row=2, column=0, sticky="nsew")

        self.redraw()

    def _on_tree_type_change(self, event=None):
        txt = self.cb_type.get()
        if "AVL" in txt:
            self.tree_type = "avl"
        elif "Min-Heap" in txt:
            self.tree_type = "min_heap"
        elif "Max-Heap" in txt:
            self.tree_type = "max_heap"
        elif "B-Tree" in txt:
            self.tree_type = "b_tree"
        else:
            self.tree_type = "bst"

        self.highlighted_nodes.clear()
        self.search_path.clear()
        self.console.log(f"Switched tree visualizer to: {txt}", "info")
        self.redraw()
        self.fit_to_view()

    def on_insert(self):
        valid, val, msg = parse_integer(self.ent_key.get())
        if not valid:
            messagebox.showerror("Invalid Key", msg, parent=self)
            return

        self.highlighted_nodes = [val]
        self.search_path.clear()

        if self.tree_type == "bst":
            ok = self.bst.insert(val)
            log_msg = f"Inserted {val} into BST." if ok else f"Key {val} already exists in BST."
        elif self.tree_type == "avl":
            ok, rot_msg = self.avl.insert(val)
            log_msg = rot_msg if ok else f"Key {val} already exists in AVL."
        elif self.tree_type == "min_heap":
            self.min_heap.insert(val)
            log_msg = f"Inserted {val} into Min-Heap (sifted up)."
            ok = True
        elif self.tree_type == "max_heap":
            self.max_heap.insert(val)
            log_msg = f"Inserted {val} into Max-Heap (sifted up)."
            ok = True
        else:
            ok = self.b_tree.insert(val)
            log_msg = f"Inserted {val} into B-Tree (order t=2)." if ok else f"Key {val} already in B-Tree."

        self.console.log(log_msg, "success" if ok else "warning")
        self.redraw()

    def on_search(self):
        valid, val, msg = parse_integer(self.ent_key.get())
        if not valid:
            messagebox.showerror("Invalid Key", msg, parent=self)
            return

        self.highlighted_nodes.clear()

        if self.tree_type == "bst":
            found, path = self.bst.search(val)
            self.search_path = path
            log_msg = f"Key {val} found in BST via search path: {path}." if found else f"Key {val} not found in BST. Path traversed: {path}."
        elif self.tree_type == "avl":
            found, path = self.avl.search(val)
            self.search_path = path
            log_msg = f"Key {val} found in AVL via search path: {path}." if found else f"Key {val} not found in AVL. Path traversed: {path}."
        elif self.tree_type in ("min_heap", "max_heap"):
            h = self.min_heap if self.tree_type == "min_heap" else self.max_heap
            found = val in h.heap
            self.search_path = [val] if found else []
            log_msg = f"Key {val} present in Heap array." if found else f"Key {val} not in Heap."
        else:
            found = self.b_tree.search(val)
            self.search_path = [val] if found else []
            log_msg = f"Key {val} found in B-Tree." if found else f"Key {val} not found in B-Tree."

        self.console.log(log_msg, "success" if found else "error")
        self.redraw()

    def on_delete(self):
        valid, val, msg = parse_integer(self.ent_key.get())
        if not valid:
            messagebox.showerror("Invalid Key", msg, parent=self)
            return

        self.highlighted_nodes.clear()
        self.search_path.clear()

        if self.tree_type == "bst":
            ok = self.bst.delete(val)
            log_msg = f"Deleted {val} from BST (rebalanced pointers)." if ok else f"Key {val} not in BST."
        elif self.tree_type == "avl":
            ok, rot_msg = self.avl.delete(val)
            log_msg = rot_msg if ok else f"Key {val} not in AVL."
        elif self.tree_type in ("min_heap", "max_heap"):
            h = self.min_heap if self.tree_type == "min_heap" else self.max_heap
            root = h.extract()
            log_msg = f"Extracted root {root} from Heap." if root is not None else "Heap is empty."
            ok = root is not None
        else:
            ok = self.b_tree.delete(val)
            log_msg = f"Deleted {val} from B-Tree." if ok else f"Key {val} not in B-Tree."

        self.console.log(log_msg, "success" if ok else "warning")
        self.redraw()

    def on_clear(self):
        self.bst = BinarySearchTree()
        self.avl = AVLTree()
        self.min_heap = MinHeap()
        self.max_heap = MaxHeap()
        self.b_tree = BTree(t=2)
        self.highlighted_nodes.clear()
        self.search_path.clear()
        self.console.clear()
        self.console.log("Cleared all tree structures.", "info")
        self.redraw()

    def on_reload_sample(self):
        self.load_sample_data()
        self.highlighted_nodes.clear()
        self.search_path.clear()
        self.console.log("Reloaded balanced sample dataset [50, 30, 70, 20, 40, 60, 80].", "info")
        self.redraw()
        self.fit_to_view()

    def test_skewed_comparison(self):
        skewed_keys = [10, 20, 30, 40, 50, 60, 70, 80]
        test_bst = BinarySearchTree()
        test_avl = AVLTree()
        for k in skewed_keys:
            test_bst.insert(k)
            test_avl.insert(k)

        bst_h = test_bst.get_metrics()["height"]
        avl_h = test_avl.height(test_avl.root)

        self.console.clear()
        self.console.log("=== PR-12 BALANCED TREE EVALUATION: BST vs AVL ===", "highlight")
        self.console.log(f"Inserted sorted sequential dataset: {skewed_keys}", "info")
        self.console.log(f"Unbalanced BST Height: {bst_h} (Degrades to O(N) linked list)", "error")
        self.console.log(f"Self-Balancing AVL Height: {avl_h} (Rotations guarantee O(log N))", "success")
        self.console.log("Conclusion: AVL tree strictly bounds worst-case lookups to 1.44 log2(N).", "info")

    def _to_screen(self, x: float, y: float) -> Tuple[float, float]:
        return (x * self.scale + self.offset_x, y * self.scale + self.offset_y)

    def fit_to_view(self):
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.redraw()

    def _zoom(self, factor: float):
        cw = self.canvas.winfo_width() / 2
        ch = self.canvas.winfo_height() / 2
        new_scale = max(0.4, min(2.5, self.scale * factor))
        self.offset_x = cw - (cw - self.offset_x) * (new_scale / self.scale)
        self.offset_y = ch - (ch - self.offset_y) * (new_scale / self.scale)
        self.scale = new_scale
        self.redraw()

    def _reset_zoom(self):
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.redraw()

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

    def redraw(self):
        self.canvas.delete("all")
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)

        if self.tree_type == "bst":
            m = self.bst.get_metrics()
            t = self.bst.traversals()
            self.stat_height.update_val(str(m["height"]))
            self.stat_nodes.update_val(str(m["total_nodes"]), f"Leaves: {m['leaf_count']}")
            self.lbl_inorder.config(text=f"Inorder (L-Root-R): {t['inorder']}")
            self.lbl_preorder.config(text=f"Preorder (Root-L-R): {t['preorder']}")
            self.lbl_postorder.config(text=f"Postorder (L-R-Root): {t['postorder']}")
            self.lbl_levelorder.config(text=f"Level-Order (BFS): {t['levelorder']}")
            self._draw_binary_tree(self.bst.root, cw / 2, 45, cw / 4, 1)

        elif self.tree_type == "avl":
            bfs_dict = self.avl.get_balance_factors()
            h = self.avl.height(self.avl.root)
            self.stat_height.update_val(str(h), "Balanced O(log N)")
            self.stat_nodes.update_val(str(len(bfs_dict)))
            self.lbl_inorder.config(text=f"Inorder: {sorted(bfs_dict.keys())}")
            self.lbl_preorder.config(text=f"Root: {self.avl.root.val if self.avl.root else None}")
            self.lbl_postorder.config(text=f"Balance Factors (BF = HL - HR):")
            self.lbl_levelorder.config(text=f"All BF in [-1, 0, 1]: {all(abs(v) <= 1 for v in bfs_dict.values())}")
            self._draw_avl_tree(self.avl.root, cw / 2, 45, cw / 4, 1, bfs_dict)

        elif self.tree_type in ("min_heap", "max_heap"):
            h = self.min_heap if self.tree_type == "min_heap" else self.max_heap
            arr = h.get_array()
            tree_h = int(math.log2(len(arr))) + 1 if arr else 0
            self.stat_height.update_val(str(tree_h), "Complete Binary Tree")
            self.stat_nodes.update_val(str(len(arr)), f"Root: {h.peek()}")
            self.lbl_inorder.config(text=f"Heap 1D Array Representation:")
            self.lbl_preorder.config(text=f"Array: {arr}")
            self.lbl_postorder.config(text=f"Root: {h.peek()} | Min/Max Priority Queue")
            self.lbl_levelorder.config(text=f"Child index formula: 2i+1, 2i+2")
            self._draw_heap_tree(arr, cw / 2, 45)
            self._draw_heap_array_view(arr, cw, ch)

        else:
            all_keys = self.b_tree.traverse()
            self.stat_height.update_val("B-Tree", "Order t=2")
            self.stat_nodes.update_val(str(len(all_keys)))
            self.lbl_inorder.config(text=f"B-Tree Traversal: {all_keys}")
            self.lbl_preorder.config(text=f"Order Parameter: t=2 (Min keys=1, Max keys=3)")
            self.lbl_postorder.config(text=f"Multi-key partitioned B-Tree node indexing")
            self.lbl_levelorder.config(text=f"Proactive child node splitting on insert")
            self._draw_btree_node(self.b_tree.root, cw / 2, 55, cw / 3)

    def _draw_binary_tree(self, node, x: float, y: float, dx: float, level: int):
        if not node:
            return
        sx, sy = self._to_screen(x, y)
        r = 17 * self.scale

        if node.left:
            nx, ny = self._to_screen(x - dx, y + 60)
            self.canvas.create_line(sx, sy, nx, ny, fill="#94A3B8", width=2)
            self._draw_binary_tree(node.left, x - dx, y + 60, dx / 2, level + 1)

        if node.right:
            nx, ny = self._to_screen(x + dx, y + 60)
            self.canvas.create_line(sx, sy, nx, ny, fill="#94A3B8", width=2)
            self._draw_binary_tree(node.right, x + dx, y + 60, dx / 2, level + 1)

        fill_color = Theme.SUCCESS if node.val in self.search_path else (Theme.WARNING if node.val in self.highlighted_nodes else Theme.PRIMARY)
        self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=fill_color, outline="#1E293B", width=2)
        font_sz = max(8, int(9 * self.scale))
        self.canvas.create_text(sx, sy, text=str(node.val), fill="#FFFFFF", font=("Helvetica", font_sz, "bold"))

    def _draw_avl_tree(self, node, x: float, y: float, dx: float, level: int, bfs_dict: Dict[int, int]):
        if not node:
            return
        sx, sy = self._to_screen(x, y)
        r = 17 * self.scale

        if node.left:
            nx, ny = self._to_screen(x - dx, y + 60)
            self.canvas.create_line(sx, sy, nx, ny, fill="#94A3B8", width=2)
            self._draw_avl_tree(node.left, x - dx, y + 60, dx / 2, level + 1, bfs_dict)

        if node.right:
            nx, ny = self._to_screen(x + dx, y + 60)
            self.canvas.create_line(sx, sy, nx, ny, fill="#94A3B8", width=2)
            self._draw_avl_tree(node.right, x + dx, y + 60, dx / 2, level + 1, bfs_dict)

        fill_color = Theme.SUCCESS if node.val in self.search_path else (Theme.WARNING if node.val in self.highlighted_nodes else Theme.TEAL)
        self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=fill_color, outline="#1E293B", width=2)
        font_sz = max(8, int(9 * self.scale))
        self.canvas.create_text(sx, sy, text=str(node.val), fill="#FFFFFF", font=("Helvetica", font_sz, "bold"))

        bf = bfs_dict.get(node.val, 0)
        self.canvas.create_text(sx, sy + r + 10, text=f"BF={bf}", fill=Theme.TEXT_MUTED, font=("Helvetica", max(7, font_sz - 1)))

    def _draw_heap_tree(self, arr: List[int], x: float, y: float):
        if not arr:
            return
        coords = {}
        cw = max(self.canvas.winfo_width(), 400)

        def _calc_pos(idx: int, cx: float, cy: float, dx: float):
            if idx >= len(arr):
                return
            coords[idx] = (cx, cy)
            _calc_pos(2 * idx + 1, cx - dx, cy + 55, dx / 2)
            _calc_pos(2 * idx + 2, cx + dx, cy + 55, dx / 2)

        _calc_pos(0, x, y, cw / 4)

        for idx in range(len(arr)):
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < len(arr) and idx in coords and left in coords:
                x1, y1 = self._to_screen(*coords[idx])
                x2, y2 = self._to_screen(*coords[left])
                self.canvas.create_line(x1, y1, x2, y2, fill="#94A3B8", width=2)
            if right < len(arr) and idx in coords and right in coords:
                x1, y1 = self._to_screen(*coords[idx])
                x2, y2 = self._to_screen(*coords[right])
                self.canvas.create_line(x1, y1, x2, y2, fill="#94A3B8", width=2)

        r = 17 * self.scale
        for idx, val in enumerate(arr):
            if idx in coords:
                sx, sy = self._to_screen(*coords[idx])
                fill_color = Theme.PURPLE if idx == 0 else Theme.PRIMARY
                self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=fill_color, outline="#1E293B", width=2)
                font_sz = max(8, int(9 * self.scale))
                self.canvas.create_text(sx, sy, text=str(val), fill="#FFFFFF", font=("Helvetica", font_sz, "bold"))
                self.canvas.create_text(sx, sy + r + 10, text=f"[{idx}]", fill=Theme.TEXT_MUTED, font=("Helvetica", max(7, font_sz - 1)))

    def _draw_heap_array_view(self, arr: List[int], cw: float, ch: float):
        if not arr:
            return
        box_w = 40 * self.scale
        box_h = 32 * self.scale
        start_x = max(20, (cw - len(arr) * box_w) / 2)
        y = ch - 50

        self.canvas.create_text(cw / 2, y - 16, text="Synchronized 1D Heap Array Representation:", font=Theme.FONT_SMALL_BOLD, fill=Theme.TEXT_MUTED)
        for i, val in enumerate(arr):
            x0 = start_x + i * box_w
            x1 = x0 + box_w
            y0 = y
            y1 = y + box_h
            c = Theme.PURPLE if i == 0 else "#DBEAFE"
            fg = "#FFFFFF" if i == 0 else Theme.TEXT_MAIN
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=c, outline=Theme.PRIMARY, width=1)
            self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(val), font=Theme.FONT_SMALL_BOLD, fill=fg)
            self.canvas.create_text((x0 + x1) / 2, y1 + 10, text=str(i), font=Theme.FONT_SMALL, fill=Theme.TEXT_MUTED)

    def _draw_btree_node(self, node, x: float, y: float, dx: float):
        if not node:
            return
        sx, sy = self._to_screen(x, y)
        n_keys = len(node.keys)
        cell_w = 34 * self.scale
        node_w = max(40 * self.scale, n_keys * cell_w)
        node_h = 28 * self.scale

        if not node.leaf and node.children:
            n_children = len(node.children)
            child_span = dx * 1.8
            start_cx = x - child_span / 2
            step_cx = child_span / max(1, n_children - 1) if n_children > 1 else 0
            for ci, child in enumerate(node.children):
                cx = start_cx + ci * step_cx if n_children > 1 else x
                cy = y + 70
                csx, csy = self._to_screen(cx, cy)
                self.canvas.create_line(sx, sy + node_h / 2, csx, csy - node_h / 2, fill="#94A3B8", width=2)
                self._draw_btree_node(child, cx, cy, dx / 2)

        x0 = sx - node_w / 2
        y0 = sy - node_h / 2
        x1 = sx + node_w / 2
        y1 = sy + node_h / 2
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=Theme.BG_PANEL, outline=Theme.PRIMARY, width=2)

        for ki, key in enumerate(node.keys):
            kx0 = x0 + ki * cell_w
            kx1 = kx0 + cell_w
            fill_c = Theme.WARNING if key in self.highlighted_nodes or key in self.search_path else "#DBEAFE"
            self.canvas.create_rectangle(kx0, y0, kx1, y1, fill=fill_c, outline=Theme.PRIMARY, width=1)
            self.canvas.create_text((kx0 + kx1) / 2, (y0 + y1) / 2, text=str(key), fill=Theme.TEXT_MAIN, font=Theme.FONT_SMALL_BOLD)
