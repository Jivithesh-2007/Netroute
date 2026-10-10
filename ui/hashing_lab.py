"""
MODULE B.3 — HASH TABLE LAB (CO3)
Interactive visualizer for Separate Chaining and Open Addressing with Linear Probing,
with probe counter, collision tracking, tombstone markers, and load factor calculation.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.theme import Theme
from app.widgets import CardFrame, StatCard, ConsoleLog
from algorithms.hashing import HashTableChaining, HashTableLinearProbing
from utils.validation import parse_integer


class HashingLabView(ttk.Frame):
    """Hash Table collision resolution lab visualizer."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.table_size = 10
        self.chaining_table = HashTableChaining(self.table_size)
        self.probing_table = HashTableLinearProbing(self.table_size)

        self._build_ui()
        self.redraw_table()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        # Left Panel: Controls & Canvas
        left_panel = ttk.Frame(self, style="TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        # Toolbar Frame
        toolbar = CardFrame(left_panel, padding=8)
        toolbar.grid(row=0, column=0, sticky="ew")

        ttk.Label(toolbar, text="Collision Method:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.method_combo = ttk.Combobox(toolbar, values=["Separate Chaining", "Linear Probing (Open Addressing)"], state="readonly", width=25)
        self.method_combo.current(0)
        self.method_combo.pack(side="left", padx=(0, 12))
        self.method_combo.bind("<<ComboboxSelected>>", lambda e: self.redraw_table())

        ttk.Label(toolbar, text="Key:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.key_entry = ttk.Entry(toolbar, width=8)
        self.key_entry.insert(0, "42")
        self.key_entry.pack(side="left", padx=(0, 8))

        btn_insert = ttk.Button(toolbar, text="Insert", style="Primary.TButton", command=self.do_insert)
        btn_insert.pack(side="left", padx=2)

        btn_search = ttk.Button(toolbar, text="Search", command=self.do_search)
        btn_search.pack(side="left", padx=2)

        btn_delete = ttk.Button(toolbar, text="Delete", command=self.do_delete)
        btn_delete.pack(side="left", padx=2)

        btn_clear = ttk.Button(toolbar, text="Clear Table", command=self.do_clear)
        btn_clear.pack(side="left", padx=2)

        # Canvas Area for Hash Table Graphics
        canvas_card = CardFrame(left_panel, padding=4)
        canvas_card.grid(row=1, column=0, sticky="nsew", pady=6)

        self.canvas = tk.Canvas(canvas_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Log
        self.console = ConsoleLog(left_panel, height=4)
        self.console.grid(row=2, column=0, sticky="ew")

        # Right Panel: Metrics & Stats
        right_panel = ttk.Frame(self, style="TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")

        stats_card = CardFrame(right_panel, title="Hash Table Metrics")
        stats_card.pack(fill="x", pady=(0, 8))

        s_grid = ttk.Frame(stats_card, style="Card.TFrame")
        s_grid.pack(fill="x")
        s_grid.columnconfigure((0, 1), weight=1)

        self.card_load = StatCard(s_grid, "Load Factor (α)", "0.00", Theme.ACCENT_CYAN)
        self.card_load.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.card_collisions = StatCard(s_grid, "Collisions", "0", Theme.COLOR_ERROR)
        self.card_collisions.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.card_probes = StatCard(s_grid, "Total Probes", "0", Theme.COLOR_EXPLORE)
        self.card_probes.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        self.card_items = StatCard(s_grid, "Items Count", "0", Theme.COLOR_SUCCESS)
        self.card_items.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # Explanation Box
        info_card = CardFrame(right_panel, title="Collision Resolution Principles")
        info_card.pack(fill="both", expand=True)

        info_lbl = ttk.Label(
            info_card,
            text=(
                "• Hash Function: h(k) = k mod M (M = 10 buckets).\n\n"
                "• Separate Chaining: Each bucket holds a linked list. "
                "Alpha can exceed 1.0 without overflowing.\n\n"
                "• Linear Probing: Probes next index (h(k)+i) mod M. "
                "Uses DELETED tombstones to preserve search probes."
            ),
            style="Card.TLabel",
            font=Theme.FONT_SMALL,
            wraplength=220
        )
        info_lbl.pack(anchor="w")

    def get_active_table(self):
        return self.chaining_table if "Chaining" in self.method_combo.get() else self.probing_table

    def do_insert(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Error", msg)
            return

        table = self.get_active_table()
        res = table.insert(key)
        self.console.log(res.message, "success" if res.success else "error")
        self.redraw_table(highlight_idx=res.path[0] if res.path else None)

    def do_search(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Error", msg)
            return

        table = self.get_active_table()
        res = table.search(key)
        self.console.log(res.message, "found" if res.success else "warning")
        self.redraw_table(highlight_idx=res.path[0] if res.path else None)

    def do_delete(self):
        valid, key, msg = parse_integer(self.key_entry.get())
        if not valid:
            messagebox.showerror("Error", msg)
            return

        table = self.get_active_table()
        res = table.delete(key)
        self.console.log(res.message, "info" if res.success else "warning")
        self.redraw_table()

    def do_clear(self):
        self.get_active_table().clear()
        self.redraw_table()
        self.console.log("Cleared hash table.", "info")

    def redraw_table(self, highlight_idx: int = None):
        self.canvas.delete("all")
        is_chaining = "Chaining" in self.method_combo.get()
        table = self.get_active_table()

        # Update Metrics
        self.card_load.update_value(f"{table.get_load_factor():.2f}")
        self.card_collisions.update_value(str(table.collisions))
        self.card_probes.update_value(str(table.total_probes))
        self.card_items.update_value(str(table.item_count))

        cw = self.canvas.winfo_width() or 600
        ch = self.canvas.winfo_height() or 400

        if is_chaining:
            self._draw_chaining_canvas(table, highlight_idx)
        else:
            self._draw_probing_canvas(table, highlight_idx)

    def _draw_chaining_canvas(self, table: HashTableChaining, highlight_idx: int = None):
        start_y = 20
        box_h = 30
        gap_y = 8

        for i in range(table.size):
            y1 = start_y + i * (box_h + gap_y)
            y2 = y1 + box_h
            x1 = 40
            x2 = 120

            fill = Theme.ACCENT_BLUE if i == highlight_idx else Theme.BG_CARD
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=Theme.BORDER_COLOR, width=1)
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=f"Bucket {i}", fill=Theme.TEXT_MAIN, font=Theme.FONT_BOLD)

            # Draw Bucket Chain List
            bucket = table.buckets[i]
            curr_x = x2 + 30
            for k, v in bucket:
                # Arrow line
                self.canvas.create_line(curr_x - 30, (y1 + y2) / 2, curr_x, (y1 + y2) / 2, fill=Theme.ACCENT_CYAN, width=2, arrow="last")
                # Node box
                self.canvas.create_rectangle(curr_x, y1, curr_x + 60, y2, fill=Theme.BG_CARD_ALT, outline=Theme.ACCENT_CYAN, width=1)
                self.canvas.create_text(curr_x + 30, (y1 + y2) / 2, text=f"{k}", fill=Theme.TEXT_MAIN, font=Theme.FONT_BOLD)
                curr_x += 80

    def _draw_probing_canvas(self, table: HashTableLinearProbing, highlight_idx: int = None):
        start_x = 40
        box_w = 60
        box_h = 50
        y1 = 60
        y2 = y1 + box_h

        for i in range(table.size):
            x1 = start_x + i * (box_w + 6)
            x2 = x1 + box_w

            cell = table.table[i]
            fill = Theme.BG_CARD
            text = "EMPTY"
            text_color = Theme.TEXT_MUTED

            if cell == HashTableLinearProbing.DELETED:
                fill = Theme.COLOR_ERROR
                text = "DEL"
                text_color = Theme.TEXT_MAIN
            elif cell is not None:
                fill = Theme.COLOR_SUCCESS
                text = f"{cell[0]}"
                text_color = Theme.TEXT_DARK

            if i == highlight_idx:
                fill = Theme.COLOR_EXPLORE
                text_color = Theme.TEXT_DARK

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=Theme.BORDER_COLOR, width=1)
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, fill=text_color, font=Theme.FONT_BOLD)
            self.canvas.create_text((x1 + x2) / 2, y2 + 16, text=f"[{i}]", fill=Theme.TEXT_MUTED, font=Theme.FONT_SMALL)
