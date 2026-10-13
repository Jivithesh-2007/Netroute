"""
MODULE B.3 — HASH TABLE LAB (CO3)
Interactive visualizer for Separate Chaining and Open Addressing with Linear Probing,
with table-size configuration, probe counter, collision tracking, tombstone markers,
search path animation, and load factor calculation.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from app.theme import Theme
from app.widgets import CardFrame, StatCard, ConsoleLog
from algorithms.hashing import HashTableChaining, HashTableLinearProbing
from utils.validation import parse_integer


class HashingLabView(ttk.Frame):
    """Hash Table collision resolution lab visualizer with PanedWindow and dynamic scaling."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.table_size: int = 10
        self.chaining_table = HashTableChaining(self.table_size)
        self.probing_table = HashTableLinearProbing(self.table_size)

        self._build_ui()
        self.after(100, self.redraw_table)

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # PanedWindow for Left Work Area vs Right Inspector
        self.paned = ttk.Panedwindow(self, orient="horizontal")
        self.paned.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # === LEFT WORK AREA ===
        left_area = ttk.Frame(self.paned, style="TFrame")
        self.paned.add(left_area, weight=3)

        left_area.grid_rowconfigure(1, weight=1)
        left_area.grid_columnconfigure(0, weight=1)

        # Toolbar Frame
        toolbar = CardFrame(left_area, padding=(8, 6))
        toolbar.grid(row=0, column=0, sticky="ew")

        # Row 1: Collision Resolution & Table Size Selection
        row1 = ttk.Frame(toolbar, style="Card.TFrame")
        row1.pack(fill="x", pady=(0, 6))

        ttk.Label(row1, text="Resolution Method:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.method_combo = ttk.Combobox(
            row1,
            values=["Separate Chaining (Chained Lists)", "Linear Probing (Open Addressing)"],
            state="readonly",
            width=28
        )
        self.method_combo.current(0)
        self.method_combo.pack(side="left", padx=(0, 10))
        self.method_combo.bind("<<ComboboxSelected>>", lambda e: self.redraw_table())

        ttk.Label(row1, text="Table Size (M):", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.size_combo = ttk.Combobox(
            row1,
            values=["7 (Prime)", "10 (Decimal)", "11 (Prime)", "13 (Prime)", "17 (Prime)"],
            state="readonly",
            width=14
        )
        self.size_combo.current(1)
        self.size_combo.pack(side="left", padx=(0, 10))
        self.size_combo.bind("<<ComboboxSelected>>", self._on_size_change)

        # Row 2: Operations (Insert, Search, Delete, Clear)
        row2 = ttk.Frame(toolbar, style="Card.TFrame")
        row2.pack(fill="x")

        ttk.Label(row2, text="Key (Integer):", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.key_entry = ttk.Entry(row2, width=8)
        self.key_entry.insert(0, "42")
        self.key_entry.pack(side="left", padx=(0, 8))

        btn_insert = ttk.Button(row2, text="+ Insert", style="Primary.TButton", command=self.do_insert)
        btn_insert.pack(side="left", padx=2)

        btn_search = ttk.Button(row2, text="🔍 Search", style="Tool.TButton", command=self.do_search)
        btn_search.pack(side="left", padx=2)

        btn_delete = ttk.Button(row2, text="🗑 Delete", style="Tool.TButton", command=self.do_delete)
        btn_delete.pack(side="left", padx=2)

        btn_clear = ttk.Button(row2, text="↺ Clear Table", style="Tool.TButton", command=self.do_clear)
        btn_clear.pack(side="left", padx=(8, 2))

        # Canvas Area for Hash Table Graphics
        canvas_card = CardFrame(left_area, padding=4)
        canvas_card.grid(row=1, column=0, sticky="nsew", pady=(6, 6))

        self.canvas = tk.Canvas(canvas_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw_table())

        # Console Log
        self.console = ConsoleLog(left_area, height=5)
        self.console.grid(row=2, column=0, sticky="ew")

        # === RIGHT INSPECTOR ===
        right_panel = ttk.Frame(self.paned, style="TFrame")
        self.paned.add(right_panel, weight=1)

        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        stats_card = CardFrame(right_panel, title="Hash Table Metrics (CO3)", padding=8)
        stats_card.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        s_grid = ttk.Frame(stats_card, style="Card.TFrame")
        s_grid.pack(fill="x")
        s_grid.columnconfigure((0, 1), weight=1)

        self.card_load = StatCard(s_grid, "Load Factor (α)", "0.00", Theme.ACCENT_CYAN)
        self.card_load.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.card_collisions = StatCard(s_grid, "Collisions", "0", Theme.COLOR_ERROR)
        self.card_collisions.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.card_probes = StatCard(s_grid, "Total Probes", "0", Theme.COLOR_EXPLORE)
        self.card_probes.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        self.card_items = StatCard(s_grid, "Item Count (n)", "0", Theme.COLOR_SUCCESS)
        self.card_items.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # Principles & Complexity Card
        info_card = CardFrame(right_panel, title="Theoretical Principles & Specs", padding=8)
        info_card.grid(row=1, column=0, sticky="nsew")

        info_text = (
            "==================================================\n"
            "  HASH TABLE COLLISION RESOLUTION (CO3 / PrO-7)\n"
            "==================================================\n\n"
            "1. HASH FUNCTION\n"
            "   • h(key) = key mod M\n"
            "   • Prime table size M reduces clustering.\n\n"
            "2. SEPARATE CHAINING\n"
            "   • Buckets maintain linked lists.\n"
            "   • Load factor α = n / M can exceed 1.0.\n"
            "   • Search / Insert: O(1 + α) average.\n\n"
            "3. LINEAR PROBING (OPEN ADDRESSING)\n"
            "   • Probe sequence: (h(key) + i) mod M\n"
            "   • Primary clustering occurs when clusters form.\n"
            "   • Load factor α must remain < 1.0 (ideal < 0.7).\n"
            "   • DELETED tombstones preserve search probe paths.\n"
            "==================================================\n"
        )
        info_txt_widget = tk.Text(info_card, bg=Theme.BG_CARD, fg=Theme.TEXT_MAIN, font=Theme.FONT_MONO, relief="solid", bd=1)
        info_txt_widget.insert("1.0", info_text)
        info_txt_widget.config(state="disabled")
        info_txt_widget.pack(fill="both", expand=True)

    def _on_size_change(self, event=None):
        val = self.size_combo.get()
        size_str = val.split()[0]
        try:
            new_size = int(size_str)
            self.table_size = new_size
            self.chaining_table = HashTableChaining(self.table_size)
            self.probing_table = HashTableLinearProbing(self.table_size)
            self.redraw_table()
            self.console.log(f"Configured hash table size M = {self.table_size}.", "info")
        except ValueError:
            pass

    def get_active_table(self):
        return self.chaining_table if "Chaining" in self.method_combo.get() else self.probing_table

    def do_insert(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", msg)
            return

        table = self.get_active_table()
        res = table.insert(key)
        self.console.log(res.message, "success" if res.success else "error")
        highlight_idx = res.path[0] if (res.path and res.success) else None
        self.redraw_table(highlight_indices=res.path if res.path else None, found_idx=highlight_idx)

    def do_search(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", msg)
            return

        table = self.get_active_table()
        res = table.search(key)
        self.console.log(res.message, "success" if res.success else "warning")
        found_idx = res.path[-1] if (res.path and res.success) else None
        self.redraw_table(highlight_indices=res.path if res.path else None, found_idx=found_idx)

    def do_delete(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", msg)
            return

        table = self.get_active_table()
        res = table.delete(key)
        self.console.log(res.message, "info" if res.success else "warning")
        self.redraw_table()

    def do_clear(self):
        self.get_active_table().clear()
        self.redraw_table()
        self.console.log("Cleared all elements in active hash table.", "info")

    def redraw_table(self, highlight_indices: Optional[List[int]] = None, found_idx: Optional[int] = None):
        self.canvas.delete("all")
        is_chaining = "Chaining" in self.method_combo.get()
        table = self.get_active_table()

        # Update Metrics
        self.card_load.update_value(f"{table.get_load_factor():.2f}")
        self.card_collisions.update_value(str(table.collisions))
        self.card_probes.update_value(str(table.total_probes))
        self.card_items.update_value(str(table.item_count))

        if is_chaining:
            self._draw_chaining_canvas(table, highlight_indices, found_idx)
        else:
            self._draw_probing_canvas(table, highlight_indices, found_idx)

    def _draw_chaining_canvas(self, table: HashTableChaining, highlight_indices, found_idx):
        start_y = 16
        box_h = 28
        gap_y = 6

        probed_set = set(highlight_indices) if highlight_indices else set()

        for i in range(table.size):
            y1 = start_y + i * (box_h + gap_y)
            y2 = y1 + box_h
            x1 = 30
            x2 = 120

            fill = Theme.BG_CARD
            outline = Theme.BORDER_COLOR
            if i == found_idx:
                fill = Theme.COLOR_SUCCESS
                outline = "#166534"
            elif i in probed_set:
                fill = Theme.COLOR_EXPLORE
                outline = "#B45309"

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1)
            self.canvas.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2,
                text=f"Slot [{i}]",
                fill="#FFFFFF" if i in [found_idx] or i in probed_set else Theme.TEXT_MAIN,
                font=Theme.FONT_SMALL_BOLD
            )

            # Draw Bucket Chain
            bucket = table.buckets[i]
            curr_x = x2 + 24
            for k, v in bucket:
                # Arrow
                self.canvas.create_line(curr_x - 24, (y1 + y2) / 2, curr_x, (y1 + y2) / 2, fill=Theme.ACCENT_BLUE, width=2, arrow="last")
                # Linked Node Box
                node_fill = Theme.BG_SELECTED
                node_outline = Theme.ACCENT_BLUE
                self.canvas.create_rectangle(curr_x, y1, curr_x + 55, y2, fill=node_fill, outline=node_outline, width=1)
                self.canvas.create_text(curr_x + 27, (y1 + y2) / 2, text=f"{k}", fill=Theme.ACCENT_BLUE, font=Theme.FONT_BOLD)
                curr_x += 75

    def _draw_probing_canvas(self, table: HashTableLinearProbing, highlight_indices, found_idx):
        start_x = 30
        box_w = 58
        box_h = 52
        y1 = 60
        y2 = y1 + box_h

        probed_set = set(highlight_indices) if highlight_indices else set()

        for i in range(table.size):
            x1 = start_x + i * (box_w + 6)
            x2 = x1 + box_w

            cell = table.table[i]
            fill = Theme.BG_CARD
            outline = Theme.BORDER_COLOR
            text = "EMPTY"
            text_color = Theme.TEXT_MUTED

            if cell == HashTableLinearProbing.DELETED:
                fill = Theme.BG_CARD_ALT
                outline = Theme.COLOR_ERROR
                text = "DEL"
                text_color = Theme.COLOR_ERROR
            elif cell is not None:
                fill = Theme.BG_SELECTED
                outline = Theme.ACCENT_BLUE
                text = f"{cell[0]}"
                text_color = Theme.ACCENT_BLUE

            if i == found_idx:
                fill = Theme.COLOR_SUCCESS
                outline = "#166534"
                text_color = "#FFFFFF"
            elif i in probed_set:
                fill = Theme.COLOR_EXPLORE
                outline = "#B45309"
                text_color = "#FFFFFF"

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=2 if (i in probed_set or i == found_idx) else 1)
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, fill=text_color, font=Theme.FONT_BOLD)
            self.canvas.create_text((x1 + x2) / 2, y2 + 16, text=f"[{i}]", fill=Theme.TEXT_MUTED, font=Theme.FONT_SMALL)
