"""
MODULE C — TREE STRUCTURES LAB (CO4)
Interactive tree renderer for Binary Search Tree, AVL Tree, Min/Max Heap,
B-Tree multi-key nodes, and Preorder/Inorder/Postorder/Level-order traversals.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any

from app.theme import Theme
from app.widgets import CardFrame, StatCard, ConsoleLog, ControlBar
from models.simulation import SimulationStep, SimulationResult
from algorithms.binary_search_tree import BinarySearchTree
from algorithms.avl_tree import AVLTree
from algorithms.heap import MinHeap, MaxHeap
from algorithms.b_tree import BTree
from algorithms.tree_traversals import (
    preorder_traversal, inorder_traversal, postorder_traversal, levelorder_traversal, get_tree_metrics
)
from services.simulation_service import SimulationService
from utils.validation import parse_integer


class TreeLabView(ttk.Frame):
    """Tree Structures Lab module view."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        # Data Structure Instances
        self.bst = BinarySearchTree()
        self.avl = AVLTree()
        self.min_heap = MinHeap()
        self.max_heap = MaxHeap()
        self.b_tree = BTree(t=3)

        self.sim_service = SimulationService(root_widget=self)

        # Seed sample data into BST & AVL
        for k in [50, 30, 70, 20, 40, 60, 80]:
            self.bst.insert(k)
            self.avl.insert(k)
            self.min_heap.insert(k)
            self.b_tree.insert(k)

        self._build_ui()
        self.redraw_active_tree()

    def on_hide(self):
        """Lifecycle hook when module view is hidden."""
        self.sim_service.stop()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        # Left Panel: Controls & Tree Canvas
        left_panel = ttk.Frame(self, style="TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Toolbar
        toolbar = CardFrame(left_panel, padding=8)
        toolbar.grid(row=0, column=0, sticky="ew")

        ttk.Label(toolbar, text="Tree Type:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.tree_combo = ttk.Combobox(
            toolbar,
            values=["Binary Search Tree (BST)", "AVL Tree (Self-Balancing)", "Min-Heap / Priority Queue", "B-Tree (Multi-Key)", "Tree Traversals"],
            state="readonly",
            width=24
        )
        self.tree_combo.current(0)
        self.tree_combo.pack(side="left", padx=(0, 12))
        self.tree_combo.bind("<<ComboboxSelected>>", lambda e: self.redraw_active_tree())

        ttk.Label(toolbar, text="Key:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.key_entry = ttk.Entry(toolbar, width=8)
        self.key_entry.insert(0, "45")
        self.key_entry.pack(side="left", padx=(0, 8))

        btn_insert = ttk.Button(toolbar, text="Insert", style="Primary.TButton", command=self.do_insert)
        btn_insert.pack(side="left", padx=2)

        btn_search = ttk.Button(toolbar, text="Search", command=self.do_search)
        btn_search.pack(side="left", padx=2)

        btn_delete = ttk.Button(toolbar, text="Delete", command=self.do_delete)
        btn_delete.pack(side="left", padx=2)

        btn_clear = ttk.Button(toolbar, text="Clear", command=self.do_clear)
        btn_clear.pack(side="left", padx=2)

        # Traversal sub-toolbar buttons
        self.trav_combo = ttk.Combobox(toolbar, values=["Inorder", "Preorder", "Postorder", "Level-Order"], state="readonly", width=12)
        self.trav_combo.current(0)
        self.trav_combo.pack(side="left", padx=(8, 2))

        btn_trav = ttk.Button(toolbar, text="Traverse", command=self.do_traversal)
        btn_trav.pack(side="left", padx=2)

        # Canvas Area
        canvas_card = CardFrame(left_panel, padding=4)
        canvas_card.grid(row=1, column=0, sticky="nsew", pady=6)

        self.canvas = tk.Canvas(canvas_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Controls & Console
        self.control_bar = ControlBar(
            left_panel,
            on_play=self.sim_service.play,
            on_pause=self.sim_service.pause,
            on_step=self.sim_service.step_forward,
            on_reset=self.redraw_active_tree,
            on_speed_change=self.sim_service.set_speed
        )
        self.control_bar.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self.console = ConsoleLog(left_panel, height=4)
        self.console.grid(row=3, column=0, sticky="ew")

        # Right Panel: Metrics & Tree Metrics
        right_panel = ttk.Frame(self, style="TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")

        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        stats_card = CardFrame(right_panel, title="Tree Structural Metrics")
        stats_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        s_grid = ttk.Frame(stats_card, style="Card.TFrame")
        s_grid.pack(fill="x")
        s_grid.columnconfigure((0, 1), weight=1)

        self.card_height = StatCard(s_grid, "Tree Height", "0", Theme.ACCENT_CYAN)
        self.card_height.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.card_total = StatCard(s_grid, "Total Nodes", "0", Theme.ACCENT_BLUE)
        self.card_total.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.card_leaves = StatCard(s_grid, "Leaf Nodes", "0", Theme.COLOR_SUCCESS)
        self.card_leaves.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        self.card_balance = StatCard(s_grid, "Balanced?", "Yes", Theme.COLOR_EXPLORE)
        self.card_balance.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # Heap Array Dual View Card
        self.dual_card = CardFrame(right_panel, title="Heap Array Representation")
        self.dual_card.grid(row=1, column=0, sticky="nsew")

        self.heap_text = tk.Text(self.dual_card, bg="#FFFFFF", fg=Theme.TEXT_MAIN, font=Theme.FONT_MONO, height=8, relief="solid", bd=1)
        self.heap_text.pack(fill="both", expand=True)

    def do_insert(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Error", msg)
            return

        tree_type = self.tree_combo.get()
        if "BST" in tree_type or "Traversals" in tree_type:
            res = self.bst.insert(key)
        elif "AVL" in tree_type:
            res = self.avl.insert(key)
        elif "Heap" in tree_type:
            res = self.min_heap.insert(key)
        else:
            res = self.b_tree.insert(key)

        self.console.log(res.message, "success" if res.success else "error")
        self.redraw_active_tree()

    def do_search(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Error", msg)
            return

        tree_type = self.tree_combo.get()
        if "BST" in tree_type or "Traversals" in tree_type:
            res = self.bst.search(key)
        elif "AVL" in tree_type:
            res = self.avl.search(key)
        elif "Heap" in tree_type:
            found = key in self.min_heap.heap
            res = SimulationResult(algorithm_name="Heap Search", success=found, message=f"Key {key} {'found' if found else 'not found'} in heap.")
        else:
            res = self.b_tree.search(key)

        self.console.log(res.message, "found" if res.success else "warning")
        self.redraw_active_tree(highlight_key=key if res.success else None)

    def do_delete(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Error", msg)
            return

        tree_type = self.tree_combo.get()
        if "BST" in tree_type or "Traversals" in tree_type:
            res = self.bst.delete(key)
        elif "AVL" in tree_type:
            res = self.avl.delete(key)
        elif "Heap" in tree_type:
            res = self.min_heap.extract_min()[1]
        else:
            res = self.b_tree.delete(key)

        self.console.log(res.message, "info" if res.success else "warning")
        self.redraw_active_tree()

    def do_clear(self):
        self.bst.clear()
        self.avl.clear()
        self.min_heap.heap.clear()
        self.b_tree.clear()
        self.redraw_active_tree()
        self.console.log("Cleared tree structure.", "info")

    def do_traversal(self):
        t_type = self.trav_combo.get()
        root = self.bst.root if "BST" in self.tree_combo.get() or "Traversals" in self.tree_combo.get() else self.avl.root

        if t_type == "Inorder":
            seq, steps = inorder_traversal(root)
        elif t_type == "Preorder":
            seq, steps = preorder_traversal(root)
        elif t_type == "Postorder":
            seq, steps = postorder_traversal(root)
        else:
            seq, steps = levelorder_traversal(root)

        seq_str = " -> ".join(map(str, seq))
        self.console.log(f"{t_type} Traversal sequence: [{seq_str}]", "success")

        res = SimulationResult(algorithm_name=f"{t_type} Traversal", success=True, path=seq, steps=steps, message=f"{t_type}: [{seq_str}]")
        self.sim_service.load_simulation(res, on_step=lambda step, num, total: self.redraw_active_tree(highlight_key=step.current_element))
        self.sim_service.play()

    def redraw_active_tree(self, highlight_key: int = None):
        self.canvas.delete("all")
        tree_type = self.tree_combo.get()

        cw = self.canvas.winfo_width() or 600
        ch = self.canvas.winfo_height() or 400

        if "BST" in tree_type or "Traversals" in tree_type:
            self._draw_binary_tree(self.bst.root, cw / 2, 40, cw / 4, highlight_key)
            h, tot, leaves = get_tree_metrics(self.bst.root)
            self.card_balance.update_value("Unbalanced", Theme.COLOR_EXPLORE)
        elif "AVL" in tree_type:
            self._draw_binary_tree(self.avl.root, cw / 2, 40, cw / 4, highlight_key, is_avl=True)
            h, tot, leaves = get_tree_metrics(self.avl.root)
            self.card_balance.update_value("Balanced", Theme.COLOR_SUCCESS)
        elif "Heap" in tree_type:
            self._draw_heap_tree(self.min_heap.heap, cw / 2, 40, cw / 4, highlight_key)
            h = int(math.log2(len(self.min_heap.heap))) + 1 if self.min_heap.heap else 0
            tot = len(self.min_heap.heap)
            leaves = (tot + 1) // 2
            self.card_balance.update_value("Complete", Theme.ACCENT_CYAN)

            # Update Array Dual View Text
            self.heap_text.delete("1.0", "end")
            self.heap_text.insert("end", f"Heap Array List (N={tot}):\n")
            self.heap_text.insert("end", f"Indices: " + " ".join(f"[{i}]" for i in range(tot)) + "\n")
            self.heap_text.insert("end", f"Values:  " + " ".join(f" {v} " for v in self.min_heap.heap) + "\n")
        else:
            self._draw_btree_node(self.b_tree.root, cw / 2, 40, cw / 3)
            h, tot, leaves = 2, 10, 5
            self.card_balance.update_value("Balanced", Theme.COLOR_SUCCESS)

        self.card_height.update_value(str(h))
        self.card_total.update_value(str(tot))
        self.card_leaves.update_value(str(leaves))

    def _draw_binary_tree(self, node, x, y, x_offset, highlight_key=None, is_avl=False):
        if not node:
            return

        r = 20
        # Draw edges to children first
        if getattr(node, 'left', None):
            lx, ly = x - x_offset, y + 60
            self.canvas.create_line(x, y, lx, ly, fill=Theme.BORDER_COLOR, width=2)
            self._draw_binary_tree(node.left, lx, ly, x_offset / 2, highlight_key, is_avl)

        if getattr(node, 'right', None):
            rx, ry = x + x_offset, y + 60
            self.canvas.create_line(x, y, rx, ry, fill=Theme.BORDER_COLOR, width=2)
            self._draw_binary_tree(node.right, rx, ry, x_offset / 2, highlight_key, is_avl)

        fill = Theme.COLOR_EXPLORE if node.key == highlight_key else "#F1F5F9"
        outline = Theme.COLOR_EXPLORE if node.key == highlight_key else Theme.ACCENT_BLUE
        text_color = "#FFFFFF" if node.key == highlight_key else Theme.TEXT_MAIN

        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=2)
        self.canvas.create_text(x, y, text=str(node.key), fill=text_color, font=Theme.FONT_BOLD)

        if is_avl:
            bf = node.get_balance_factor()
            self.canvas.create_text(x + r + 10, y, text=f"BF:{bf}", fill=Theme.ACCENT_BLUE, font=Theme.FONT_SMALL)

    def _draw_heap_tree(self, heap: list, x, y, x_offset, highlight_key=None):
        if not heap:
            return

        def _draw_heap_node(idx, nx, ny, offset):
            if idx >= len(heap):
                return
            r = 18
            val = heap[idx]

            left = 2 * idx + 1
            right = 2 * idx + 2

            if left < len(heap):
                lx, ly = nx - offset, ny + 55
                self.canvas.create_line(nx, ny, lx, ly, fill=Theme.BORDER_COLOR, width=2)
                _draw_heap_node(left, lx, ly, offset / 2)

            if right < len(heap):
                rx, ry = nx + offset, ny + 55
                self.canvas.create_line(nx, ny, rx, ry, fill=Theme.BORDER_COLOR, width=2)
                _draw_heap_node(right, rx, ry, offset / 2)

            fill = Theme.COLOR_EXPLORE if val == highlight_key else "#F1F5F9"
            outline = Theme.COLOR_EXPLORE if val == highlight_key else Theme.COLOR_SUCCESS
            text_color = "#FFFFFF" if val == highlight_key else Theme.TEXT_MAIN

            self.canvas.create_oval(nx - r, ny - r, nx + r, ny + r, fill=fill, outline=outline, width=2)
            self.canvas.create_text(nx, ny, text=str(val), fill=text_color, font=Theme.FONT_BOLD)

        _draw_heap_node(0, x, y, x_offset)

    def _draw_btree_node(self, node, x, y, x_offset):
        if not node:
            return

        box_w = max(40, len(node.keys) * 30 + 20)
        box_h = 30

        self.canvas.create_rectangle(x - box_w / 2, y - box_h / 2, x + box_w / 2, y + box_h / 2, fill="#F1F5F9", outline=Theme.ACCENT_BLUE, width=2)
        keys_str = " | ".join(map(str, node.keys))
        self.canvas.create_text(x, y, text=keys_str, fill=Theme.TEXT_MAIN, font=Theme.FONT_BOLD)

        if not node.leaf and node.children:
            num_children = len(node.children)
            start_cx = x - (num_children - 1) * x_offset / 2
            for i, child in enumerate(node.children):
                cx = start_cx + i * x_offset
                cy = y + 70
                self.canvas.create_line(x, y + box_h / 2, cx, cy - box_h / 2, fill=Theme.BORDER_COLOR, width=2)
                self._draw_btree_node(child, cx, cy, x_offset / 2)
