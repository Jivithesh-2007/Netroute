import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict, Any

from theme import Theme, CardFrame, StatCard, ConsoleLog, ControlBar, SimulationService
from network import SimulationStep, SimulationResult
from algorithms import (
    linear_search, binary_search_iterative, binary_search_recursive, interpolation_search,
    bubble_sort, insertion_sort, selection_sort, merge_sort,
    HashTableChaining, HashTableLinearProbing,
    BenchmarkService, parse_integer, parse_integer_list
)


class CustomArrayDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Enter Custom Array")
        self.geometry("400x200")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_DARK)

        self.result = None

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Enter numbers separated by spaces or commas:", style="Card.TLabel").pack(anchor="w", pady=(0, 4))

        self.entry = ttk.Entry(frame)
        self.entry.pack(fill="x", pady=(0, 6))
        self.entry.insert(0, "45, 12, 89, 34, 67, 23, 90, 11")

        ttk.Label(frame, text="Example: 10 20 30 40 50", style="Muted.TLabel").pack(anchor="w", pady=(0, 16))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", side="bottom")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Set Array", style="Primary.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()
        self.entry.focus_set()

    def _on_submit(self):
        txt = self.entry.get()
        valid, nums, msg = parse_integer_list(txt)
        if not valid:
            messagebox.showerror("Invalid Input", msg, parent=self)
            return

        self.result = nums
        self.destroy()


class SearchingSortingLabView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.array: List[int] = [45, 12, 89, 34, 67, 23, 90, 11, 56, 78]
        self.target_val: int = 67
        self.sim_service = SimulationService(root_widget=self)

        self._build_ui()
        self.after(100, self.redraw_bars)

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

        ttk.Label(row1, text="Mode:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.mode_combo = ttk.Combobox(
            row1,
            values=["Sorting Algorithms", "Searching Algorithms"],
            state="readonly",
            width=20
        )
        self.mode_combo.current(0)
        self.mode_combo.pack(side="left", padx=(0, 10))
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)

        ttk.Label(row1, text="Algorithm:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.alg_combo = ttk.Combobox(
            row1,
            values=["Bubble Sort", "Insertion Sort", "Selection Sort", "Merge Sort"],
            state="readonly",
            width=22
        )
        self.alg_combo.current(0)
        self.alg_combo.pack(side="left", padx=(0, 10))

        self.search_ctrl_frame = ttk.Frame(row1, style="Card.TFrame")

        ttk.Label(self.search_ctrl_frame, text="Target Key:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.target_entry = ttk.Entry(self.search_ctrl_frame, width=7)
        self.target_entry.insert(0, str(self.target_val))
        self.target_entry.pack(side="left")

        row2 = ttk.Frame(toolbar, style="Card.TFrame")
        row2.pack(fill="x")

        ttk.Label(row2, text="Array Data:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 6))
        ttk.Button(row2, text="🎲 Random Array", style="Tool.TButton", command=self.generate_random_array).pack(side="left", padx=2)
        ttk.Button(row2, text="↗ Sorted Array", style="Tool.TButton", command=self.generate_sorted_array).pack(side="left", padx=2)
        ttk.Button(row2, text="↘ Reverse Array", style="Tool.TButton", command=self.generate_reversed_array).pack(side="left", padx=2)
        ttk.Button(row2, text="✏ Custom Array...", style="Tool.TButton", command=self.open_custom_array_dialog).pack(side="left", padx=2)

        canvas_card = CardFrame(left_area, padding=4)
        canvas_card.grid(row=1, column=0, sticky="nsew", pady=(6, 6))

        self.canvas = tk.Canvas(canvas_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw_bars())

        self.control_bar = ControlBar(
            left_area,
            on_play=self.run_simulation,
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

        stats_card = CardFrame(right_panel, title="Algorithm Metrics & State", padding=8)
        stats_card.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        s_grid = ttk.Frame(stats_card, style="Card.TFrame")
        s_grid.pack(fill="x")
        s_grid.columnconfigure((0, 1), weight=1)

        self.card_size = StatCard(s_grid, "Elements (N)", str(len(self.array)), Theme.ACCENT_CYAN)
        self.card_size.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.card_comps = StatCard(s_grid, "Comparisons", "0", Theme.COLOR_EXPLORE)
        self.card_comps.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.card_swaps = StatCard(s_grid, "Swaps / Writes", "0", Theme.ACCENT_BLUE)
        self.card_swaps.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        self.card_time = StatCard(s_grid, "Runtime (ms)", "0.0", Theme.COLOR_SUCCESS)
        self.card_time.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        comp_card = CardFrame(right_panel, title="Theoretical Complexity Matrix (CO3)", padding=8)
        comp_card.grid(row=1, column=0, sticky="nsew")

        self.comp_tree = ttk.Treeview(
            comp_card,
            columns=("Algorithm", "Best", "Average", "Worst", "Space"),
            show="headings",
            height=8
        )
        self.comp_tree.pack(fill="both", expand=True)

        self.comp_tree.heading("Algorithm", text="Algorithm")
        self.comp_tree.heading("Best", text="Best Case")
        self.comp_tree.heading("Average", text="Avg Case")
        self.comp_tree.heading("Worst", text="Worst Case")
        self.comp_tree.heading("Space", text="Space")

        self.comp_tree.column("Algorithm", width=110)
        self.comp_tree.column("Best", width=65)
        self.comp_tree.column("Average", width=65)
        self.comp_tree.column("Worst", width=65)
        self.comp_tree.column("Space", width=55)

        self._populate_complexity_matrix()

    def _populate_complexity_matrix(self):
        data = [
            ("Bubble Sort", "O(N)", "O(N²)", "O(N²)", "O(1)"),
            ("Insertion Sort", "O(N)", "O(N²)", "O(N²)", "O(1)"),
            ("Selection Sort", "O(N²)", "O(N²)", "O(N²)", "O(1)"),
            ("Merge Sort", "O(N log N)", "O(N log N)", "O(N log N)", "O(N)"),
            ("Linear Search", "O(1)", "O(N)", "O(N)", "O(1)"),
            ("Binary Search", "O(1)", "O(log N)", "O(log N)", "O(1)"),
            ("Interpolation", "O(1)", "O(log log N)", "O(N)", "O(1)")
        ]
        for row in data:
            self.comp_tree.insert("", "end", values=row)

    def _on_mode_change(self, event=None):
        mode = self.mode_combo.get()
        if "Sorting" in mode:
            self.alg_combo.config(values=["Bubble Sort", "Insertion Sort", "Selection Sort", "Merge Sort"])
            self.alg_combo.current(0)
            self.search_ctrl_frame.pack_forget()
        else:
            self.alg_combo.config(values=["Linear Search", "Binary Search (Iterative)", "Binary Search (Recursive)", "Interpolation Search"])
            self.alg_combo.current(0)
            self.search_ctrl_frame.pack(side="left", padx=(0, 10))
        self.reset_simulation()

    def generate_random_array(self):
        self.array = [random.randint(10, 99) for _ in range(12)]
        self.card_size.update_value(str(len(self.array)))
        self.reset_simulation()
        self.console.log("Generated random dataset.", "info")

    def generate_sorted_array(self):
        self.array = sorted([random.randint(10, 99) for _ in range(12)])
        self.card_size.update_value(str(len(self.array)))
        self.reset_simulation()
        self.console.log("Generated sorted dataset.", "info")

    def generate_reversed_array(self):
        self.array = sorted([random.randint(10, 99) for _ in range(12)], reverse=True)
        self.card_size.update_value(str(len(self.array)))
        self.reset_simulation()
        self.console.log("Generated reverse-sorted dataset (worst case).", "info")

    def open_custom_array_dialog(self):
        dlg = CustomArrayDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.array = dlg.result
            self.card_size.update_value(str(len(self.array)))
            self.reset_simulation()
            self.console.log(f"Loaded custom array: {self.array}", "info")

    def run_simulation(self):
        alg = self.alg_combo.get()
        mode = self.mode_combo.get()

        if "Searching" in mode:
            try:
                target = int(self.target_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid integer target key.")
                return

            if "Binary" in alg or "Interpolation" in alg:
                if self.array != sorted(self.array):
                    ans = messagebox.askyesno(
                        "Sorted Requirement",
                        f"{alg} requires a monotonic sorted array. Sort automatically now?"
                    )
                    if ans:
                        self.array = sorted(self.array)
                        self.redraw_bars()
                    else:
                        return

            if "Linear" in alg:
                res = linear_search(self.array, target)
            elif "Iterative" in alg:
                res = binary_search_iterative(self.array, target)
            elif "Recursive" in alg:
                res = binary_search_recursive(self.array, target)
            else:
                res = interpolation_search(self.array, target)

        else:
            if "Bubble" in alg:
                res = bubble_sort(self.array)
            elif "Insertion" in alg:
                res = insertion_sort(self.array)
            elif "Selection" in alg:
                res = selection_sort(self.array)
            else:
                res = merge_sort(self.array)

        self.control_bar.set_running_state(is_running=True)
        self.sim_service.load_simulation(
            result=res,
            on_step=self._on_step,
            on_complete=lambda: self._on_complete(res)
        )
        self.card_comps.update_value(str(res.total_comparisons))
        self.card_swaps.update_value(str(res.total_swaps))
        self.card_time.update_value(f"{res.execution_time_ms:.2f}")
        self.sim_service.play()

    def reset_simulation(self):
        self.sim_service.stop()
        self.control_bar.set_running_state(is_running=False)
        self.control_bar.reset_step_indicator()
        self.card_comps.update_value("0")
        self.card_swaps.update_value("0")
        self.card_time.update_value("0.0")
        self.redraw_bars()

    def _on_step(self, step: SimulationStep, step_num: int, total_steps: int):
        self.console.log(step.message, "explore" if step.step_type in ["compare", "probe"] else "info")
        arr = step.data_structure_state if step.data_structure_state is not None else self.array
        self.redraw_bars(arr=arr, highlights=step.highlight_indices, secondaries=step.secondary_indices)
        self.control_bar.update_step_indicator(step_num, total_steps)

    def _on_complete(self, res: SimulationResult):
        self.control_bar.set_running_state(is_running=False)
        self.console.log(res.message, "success" if res.success else "error")

    def redraw_bars(self, arr=None, highlights=None, secondaries=None):
        self.canvas.delete("all")
        data = arr if arr is not None else self.array
        if not data:
            return

        highlights = set(highlights) if highlights else set()
        secondaries = set(secondaries) if secondaries else set()

        cw = self.canvas.winfo_width() or 600
        ch = self.canvas.winfo_height() or 300

        n = len(data)
        max_val = max(data) if max(data) > 0 else 1
        padding = 32
        available_w = max(100.0, cw - 2 * padding)
        bar_w = max(12.0, min(65.0, (available_w / n) - 6.0))
        total_drawn_w = n * (bar_w + 6.0) - 6.0
        start_x = max(padding, (cw - total_drawn_w) / 2.0)

        for i, val in enumerate(data):
            x1 = start_x + i * (bar_w + 6.0)
            x2 = x1 + bar_w

            h_factor = (val / max_val) * max(50.0, ch - 90.0)
            y2 = ch - 35.0
            y1 = y2 - h_factor

            fill = Theme.BG_SELECTED
            outline = Theme.ACCENT_BLUE
            text_color = Theme.TEXT_MAIN

            if i in highlights:
                fill = Theme.COLOR_EXPLORE
                outline = "#B45309"
                text_color = Theme.COLOR_EXPLORE
            elif i in secondaries:
                fill = Theme.COLOR_SUCCESS
                outline = "#166534"
                text_color = Theme.COLOR_SUCCESS

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1)
            self.canvas.create_text(x1 + bar_w / 2.0, y1 - 10, text=str(val), fill=text_color, font=Theme.FONT_BOLD)
            self.canvas.create_text(x1 + bar_w / 2.0, y2 + 12, text=f"[{i}]", fill=Theme.TEXT_MUTED, font=Theme.FONT_SMALL)


class HashingLabView(ttk.Frame):
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

        canvas_card = CardFrame(left_area, padding=4)
        canvas_card.grid(row=1, column=0, sticky="nsew", pady=(6, 6))

        self.canvas = tk.Canvas(canvas_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw_table())

        self.console = ConsoleLog(left_area, height=5)
        self.console.grid(row=2, column=0, sticky="ew")

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
                fill="#FFFFFF" if (i == found_idx or i in probed_set) else Theme.TEXT_MAIN,
                font=Theme.FONT_SMALL_BOLD
            )

            bucket = table.buckets[i]
            curr_x = x2 + 24
            for k, v in bucket:
                self.canvas.create_line(curr_x - 24, (y1 + y2) / 2, curr_x, (y1 + y2) / 2, fill=Theme.ACCENT_BLUE, width=2, arrow="last")
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


class PerformanceDashboardView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.sort_results = None
        self.search_results = None
        self.tree_results = None

        self._build_ui()
        self.after(100, self.run_benchmark_suite)

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        toolbar = CardFrame(self, padding=(8, 6))
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(toolbar, text="Benchmark Suite:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.suite_combo = ttk.Combobox(
            toolbar,
            values=[
                "Sorting Algorithms Comparison (N=20..200)",
                "Searching Algorithms Comparison (N=100..2000)",
                "BST vs AVL Tree Benchmark (N=500)"
            ],
            state="readonly",
            width=38
        )
        self.suite_combo.current(0)
        self.suite_combo.pack(side="left", padx=(0, 10))
        self.suite_combo.bind("<<ComboboxSelected>>", lambda e: self.render_charts())

        btn_run = ttk.Button(toolbar, text="▶ Re-run Benchmarks", style="Primary.TButton", command=self.run_benchmark_suite)
        btn_run.pack(side="left", padx=4)

        btn_export = ttk.Button(toolbar, text="💾 Export Results...", style="Tool.TButton", command=self.export_results)
        btn_export.pack(side="left", padx=4)

        self.status_lbl = ttk.Label(toolbar, text="System Ready.", style="Card.TLabel", font=Theme.FONT_SMALL)
        self.status_lbl.pack(side="right", padx=8)

        self.paned = ttk.Panedwindow(self, orient="horizontal")
        self.paned.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        chart_card = CardFrame(self.paned, title="Empirical Measured Execution Time (ms)", subtitle="Hardware-timed offline benchmarks", padding=8)
        self.paned.add(chart_card, weight=3)

        self.chart_canvas = tk.Canvas(chart_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)
        self.chart_canvas.bind("<Configure>", lambda e: self.render_charts())

        table_card = CardFrame(self.paned, title="Benchmark Results Table", subtitle="Real operations and runtimes", padding=8)
        self.paned.add(table_card, weight=2)

        self.tree = ttk.Treeview(
            table_card,
            columns=("Alg", "Size", "Ops", "Time"),
            show="headings",
            height=14
        )
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("Alg", text="Algorithm")
        self.tree.heading("Size", text="N Size")
        self.tree.heading("Ops", text="Comparisons / Ops")
        self.tree.heading("Time", text="Runtime (ms)")

        self.tree.column("Alg", width=120)
        self.tree.column("Size", width=65)
        self.tree.column("Ops", width=110)
        self.tree.column("Time", width=95)

    def run_benchmark_suite(self):
        self.status_lbl.config(text="Executing real algorithm benchmarks...")
        self.update_idletasks()

        self.sort_results = BenchmarkService.benchmark_sorting([20, 50, 100, 200])
        self.search_results = BenchmarkService.benchmark_searching([100, 500, 1000, 2000])
        self.tree_results = BenchmarkService.benchmark_trees(500)

        self.status_lbl.config(text="Benchmark execution complete (100% measured).")
        self.render_charts()

    def render_charts(self):
        self.chart_canvas.delete("all")
        for item in self.tree.get_children():
            self.tree.delete(item)

        suite = self.suite_combo.get()

        if "Sorting" in suite and self.sort_results:
            self._render_sorting_chart()
        elif "Searching" in suite and self.search_results:
            self._render_searching_chart()
        elif self.tree_results:
            self._render_tree_chart()

    def _render_sorting_chart(self):
        target_size = 200
        data_points = []
        for alg_name, size_list in self.sort_results.items():
            for item in size_list:
                if item["size"] == target_size:
                    data_points.append((alg_name, item["time_ms"], item["comparisons"]))
                self.tree.insert("", "end", values=(alg_name, item["size"], item["comparisons"], f"{item['time_ms']:.3f} ms"))

        self._draw_bar_chart(data_points, f"Sorting Benchmark Execution Time (N = {target_size} elements)")

    def _render_searching_chart(self):
        target_size = 2000
        data_points = []
        for alg_name, size_list in self.search_results.items():
            for item in size_list:
                if item["size"] == target_size:
                    data_points.append((alg_name, item["time_ms"], item["comparisons"]))
                self.tree.insert("", "end", values=(alg_name, item["size"], item["comparisons"], f"{item['time_ms']:.4f} ms"))

        self._draw_bar_chart(data_points, f"Searching Benchmark Execution Time (N = {target_size} elements)")

    def _render_tree_chart(self):
        data_points = []
        for tree_type, metrics in self.tree_results.items():
            data_points.append((f"{tree_type} Insert", metrics["insert_time_ms"], metrics["num_ops"]))
            data_points.append((f"{tree_type} Search", metrics["search_time_ms"], metrics["search_comparisons"]))
            self.tree.insert("", "end", values=(f"{tree_type} Insert", metrics["num_ops"], f"{metrics['num_ops']} items", f"{metrics['insert_time_ms']:.3f} ms"))
            self.tree.insert("", "end", values=(f"{tree_type} Search", metrics["num_ops"], f"{metrics['search_comparisons']} comps", f"{metrics['search_time_ms']:.3f} ms"))

        self._draw_bar_chart(data_points, "BST vs AVL Tree Benchmark (Sequential Ops N = 500)")

    def _draw_bar_chart(self, data_points, title: str):
        cw = self.chart_canvas.winfo_width() or 550
        ch = self.chart_canvas.winfo_height() or 380

        self.chart_canvas.create_text(24, 20, text=title, fill=Theme.TEXT_MAIN, font=Theme.FONT_HEADER, anchor="w")

        if not data_points:
            return

        max_val = max(p[1] for p in data_points) if max(p[1] for p in data_points) > 0 else 1.0

        n = len(data_points)
        margin_x = 50.0
        margin_y = 55.0
        avail_w = max(100.0, cw - 2 * margin_x)
        bar_w = max(24.0, min(80.0, (avail_w / n) - 24.0))
        total_bars_w = n * (bar_w + 24.0) - 24.0
        start_x = max(margin_x, (cw - total_bars_w) / 2.0)

        baseline_y = ch - margin_y
        self.chart_canvas.create_line(margin_x - 10, baseline_y, cw - margin_x + 10, baseline_y, fill=Theme.BORDER_COLOR, width=2)

        colors = [Theme.ACCENT_BLUE, Theme.ACCENT_CYAN, Theme.COLOR_SUCCESS, Theme.COLOR_EXPLORE]

        for i, (label, val, ops) in enumerate(data_points):
            x1 = start_x + i * (bar_w + 24.0)
            x2 = x1 + bar_w

            h_factor = (val / max_val) * max(40.0, ch - 140.0)
            y2 = baseline_y
            y1 = y2 - h_factor

            fill = colors[i % len(colors)]
            self.chart_canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=Theme.BORDER_COLOR, width=1)
            self.chart_canvas.create_text((x1 + x2) / 2.0, y1 - 10, text=f"{val:.3f} ms", fill=Theme.TEXT_MAIN, font=Theme.FONT_SMALL_BOLD)
            self.chart_canvas.create_text((x1 + x2) / 2.0, y2 + 14, text=label, fill=Theme.TEXT_MAIN, font=Theme.FONT_SMALL)
            self.chart_canvas.create_text((x1 + x2) / 2.0, y2 + 28, text=f"({ops} ops)", fill=Theme.TEXT_MUTED, font=Theme.FONT_SMALL)

    def export_results(self):
        children = self.tree.get_children()
        if not children:
            messagebox.showinfo("No Data", "No benchmark data available to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Benchmark Results"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("Algorithm,Size,Comparisons / Ops,Runtime (ms)\n")
                    for item in children:
                        vals = self.tree.item(item, "values")
                        f.write(f'"{vals[0]}","{vals[1]}","{vals[2]}","{vals[3]}"\n')
                messagebox.showinfo("Export Successful", f"Benchmark results saved successfully to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not save file: {e}")


class LearningOutcomesView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_card = CardFrame(self, title="Course Outcome Mapping & Academic Documentation", subtitle="Course: Data Structures and Algorithms (25CS306)", padding=10)
        main_card.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        notebook = ttk.Notebook(main_card)
        notebook.pack(fill="both", expand=True, pady=(6, 0))

        tab_co = self._create_text_tab(notebook, self._get_co_text())
        notebook.add(tab_co, text="  Course Outcomes (CO3, CO4, CO5)  ")

        tab_pro = self._create_text_tab(notebook, self._get_pro_text())
        notebook.add(tab_pro, text="  Practicum Outcomes (PrO-7 to PrO-15)  ")

        tab_demo = self._create_text_tab(notebook, self._get_demo_text())
        notebook.add(tab_demo, text="  Lab Demonstration Guide  ")

        tab_arch = self._create_text_tab(notebook, self._get_arch_text())
        notebook.add(tab_arch, text="  System Architecture & Offline Guarantee  ")

    def _create_text_tab(self, parent_notebook, content_str: str) -> ttk.Frame:
        tab_frame = ttk.Frame(parent_notebook, style="Card.TFrame", padding=10)

        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(
            tab_frame,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_BODY,
            relief="solid",
            bd=1,
            wrap="word",
            yscrollcommand=scrollbar.set,
            padx=16,
            pady=14
        )
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        text_widget.insert("1.0", content_str.strip())
        text_widget.config(state="disabled")
        return tab_frame

    def _get_co_text(self) -> str:
        return """
================================================================================
  1. COURSE OUTCOMES (CO) COVERAGE
================================================================================

• CO3: Evaluate the performance of searching and sorting algorithms for solving
       engineering problems.
       Implemented in: Searching & Sorting Lab and Hash Table Lab.
       Features:
       - Linear, Binary (iterative/recursive), and Interpolation Search.
       - Bubble, Insertion, Selection, and Merge Sort.
       - Hash Table with Separate Chaining and Open Addressing (Linear Probing).
       - Live comparison counters, swap tracking, and theoretical complexity matrices.

• CO4: Develop tree structures for solving engineering problems.
       Implemented in: Tree Structures Lab.
       Features:
       - Binary Tree Traversals (Inorder, Preorder, Postorder, Level-order).
       - Binary Search Tree (BST) with 3-case deletion.
       - Self-balancing AVL Tree with LL, RR, LR, RL rotations and balance factor display.
       - Binary Min/Max Heap with dual array & tree visualization.
       - B-Tree multi-key node splitting visualizer.

• CO5: Evaluate the applicability of graph data structures and traversal techniques
       for solving engineering problems.
       Implemented in: Network Routing Simulator.
       Features:
       - Interactive Canvas graph editor with drag-and-drop nodes and Fit-to-View coordinate transforms.
       - BFS shortest-path routing with FIFO Queue state visualizer.
       - DFS path exploration with LIFO Stack state visualizer.
       - Adjacency List O(V+E) & Adjacency Matrix O(V²) views synchronized in real time.
       - Packet transmission animation along route.
       - Router online/offline status toggling with dynamic rerouting.
       - 2D Grid-Maze pathfinding demonstration.
"""

    def _get_pro_text(self) -> str:
        return """
================================================================================
  2. PRACTICUM OUTCOMES (PrO) MAPPING
================================================================================

• PrO-7: Hash table with collision resolution.
  -> Demonstrated in Hash Table Lab via Separate Chaining & Linear Probing with tombstone markers.

• PrO-8: Search algorithm performance on large datasets.
  -> Demonstrated in Searching & Sorting Lab via Linear, Binary, and Interpolation Search benchmarking.

• PrO-9: Sorting technique for a scheduling problem.
  -> Demonstrated in Searching & Sorting Lab via empirical comparisons of Bubble, Insertion, Selection, and Merge Sort.

• PrO-10: Evaluate tree structures for data management.
  -> Demonstrated in Tree Structures Lab by contrasting BST, AVL, Heap, and B-Tree structures.

• PrO-11: Store and retrieve hierarchical data using a suitable tree.
  -> Demonstrated in Tree Structures Lab via Binary Tree Traversals and BST lookup/insertion.

• PrO-12: Evaluate balanced trees for search and update operations.
  -> Demonstrated in Tree Structures Lab via self-balancing AVL rotations guaranteeing O(log N).

• PrO-13: Adjacency Matrix and Adjacency List graph representations.
  -> Demonstrated in Network Simulator with real-time synchronized Adjacency List and Matrix tables.

• PrO-14: Choose a suitable graph representation for specific engineering problems.
  -> Demonstrated in Network Simulator by comparing space O(V+E) vs O(V²) and edge lookup efficiency.

• PrO-15: Graph-based connectivity or routing applications.
  -> Demonstrated in Network Simulator via network packet routing simulations and grid-maze connectivity analysis.
"""

    def _get_demo_text(self) -> str:
        return """
================================================================================
  3. LAB PRACTICUM DEMONSTRATION GUIDE
================================================================================

1) Network Routing Simulator:
   - Select Source (e.g. R1) and Destination (e.g. R6).
   - Click "▶ Run Route" to watch BFS enqueue nodes and discover the shortest hop path.
   - Watch the packet animate node-by-node along the reconstructed route.
   - Click "⚡ Toggle Offline" on a core router (e.g. R2) and rerun BFS to see dynamic rerouting.
   - Click "⚖ Compare BFS & DFS" to see side-by-side hop and step comparisons.
   - Use Zoom In, Zoom Out, or "⊡ Fit View" to automatically scale and center large topologies.

2) Searching & Sorting Lab:
   - Select "Sorting Algorithms" -> "Merge Sort".
   - Click "▶ Play" to observe bar chart comparisons and array merge writes.
   - Switch to "Searching Algorithms" -> "Interpolation Search" to see probe calculations.

3) Hash Table Lab:
   - Enter keys into Separate Chaining and Linear Probing.
   - Observe collision counters, probe counts, tombstone markers ("DEL"), and load factor (α).

4) Tree Structures Lab:
   - Select "AVL Tree" and insert sequential numbers (10, 20, 30).
   - Observe automatic LL / RR rotations rebalancing the tree height and balance factors.
   - Switch to "Tree Traversals" and run "Inorder" to view sorted traversal sequence.
   - Select "Min-Heap" to inspect the linear array dual view synchronized with the binary tree.

5) Performance Dashboard:
   - Click "▶ Re-run Benchmarks" to execute real empirical algorithms on generated datasets.
   - View measured runtimes (ms) and comparison counts rendered on custom canvas charts.
   - Click "💾 Export Results..." to export benchmark tables to CSV.
"""

    def _get_arch_text(self) -> str:
        return """
================================================================================
  4. SYSTEM ARCHITECTURE & OFFLINE GUARANTEE
================================================================================

• 100% Native Desktop Implementation:
  - Built strictly in Python 3 using Tkinter, ttk, and Canvas.
  - Zero browser dependencies, zero HTML/CSS/React runtimes.
  - Complete offline functionality with no external APIs or network calls.

• Deterministic DSA Implementations:
  - No AI, machine learning, or simulated random delays.
  - All metrics, paths, and comparisons are direct outputs of real algorithms.

• Consolidated Architecture:
  - main.py      : Application entry point.
  - app.py       : Main window, sidebar navigation, and view lifecycle management.
  - network_ui.py: Network topology canvas, graph editing, and routing animation.
  - labs_ui.py   : Searching, sorting, hashing, and performance comparison labs.
  - tree_ui.py   : Binary tree, BST, AVL, Heap, and B-tree visualizer.
  - algorithms.py: All search, sort, hash, tree, and benchmark algorithm implementations.
  - network.py   : Graph data model, BFS/DFS traversal, and topology persistence.
  - theme.py     : Shared white theme tokens and reusable UI widgets.
"""
