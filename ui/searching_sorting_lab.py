"""
MODULE B — SEARCHING AND SORTING LAB (CO3)
Interactive array visualizer for Linear, Binary, and Interpolation Search,
and Bubble, Insertion, Selection, and Merge Sort, with PanedWindow resizable layout,
step counters, complexity matrix, and real algorithm execution.
"""
import random
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from app.theme import Theme
from app.widgets import CardFrame, StatCard, ConsoleLog, ControlBar
from models.simulation import SimulationStep, SimulationResult
from algorithms.searching import linear_search, binary_search_iterative, binary_search_recursive, interpolation_search
from algorithms.sorting import bubble_sort, insertion_sort, selection_sort, merge_sort
from services.simulation_service import SimulationService
from ui.dialogs import CustomArrayDialog


class SearchingSortingLabView(ttk.Frame):
    """Searching and Sorting Lab interactive module with resizable layout."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.array: List[int] = [45, 12, 89, 34, 67, 23, 90, 11, 56, 78]
        self.target_val: int = 67
        self.sim_service = SimulationService(root_widget=self)

        self._build_ui()
        self.after(100, self.redraw_bars)

    def on_hide(self):
        """Lifecycle hook when module view is hidden."""
        self.sim_service.stop()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # PanedWindow for Left Canvas Work Area vs Right Inspector
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

        # Row 1: Mode & Algorithm Selection
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

        # Target Key Entry Container (Shown in Searching Mode)
        self.search_ctrl_frame = ttk.Frame(row1, style="Card.TFrame")

        ttk.Label(self.search_ctrl_frame, text="Target Key:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.target_entry = ttk.Entry(self.search_ctrl_frame, width=7)
        self.target_entry.insert(0, str(self.target_val))
        self.target_entry.pack(side="left")

        # Row 2: Data Generators
        row2 = ttk.Frame(toolbar, style="Card.TFrame")
        row2.pack(fill="x")

        ttk.Label(row2, text="Array Data:", font=Theme.FONT_SMALL_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 6))
        ttk.Button(row2, text="🎲 Random Array", style="Tool.TButton", command=self.generate_random_array).pack(side="left", padx=2)
        ttk.Button(row2, text="↗ Sorted Array", style="Tool.TButton", command=self.generate_sorted_array).pack(side="left", padx=2)
        ttk.Button(row2, text="↘ Reverse Array", style="Tool.TButton", command=self.generate_reversed_array).pack(side="left", padx=2)
        ttk.Button(row2, text="✏ Custom Array...", style="Tool.TButton", command=self.open_custom_array_dialog).pack(side="left", padx=2)

        # Canvas Area for Bar Visualizer
        canvas_card = CardFrame(left_area, padding=4)
        canvas_card.grid(row=1, column=0, sticky="nsew", pady=(6, 6))

        self.canvas = tk.Canvas(canvas_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw_bars())

        # Control Bar
        self.control_bar = ControlBar(
            left_area,
            on_play=self.run_simulation,
            on_pause=self.sim_service.pause,
            on_step=self.sim_service.step_forward,
            on_reset=self.reset_simulation,
            on_speed_change=self.sim_service.set_speed
        )
        self.control_bar.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        # Console Log
        self.console = ConsoleLog(left_area, height=5)
        self.console.grid(row=3, column=0, sticky="ew")

        # === RIGHT INSPECTOR ===
        right_panel = ttk.Frame(self.paned, style="TFrame")
        self.paned.add(right_panel, weight=1)

        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Stats Card
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

        # Theoretical Complexity Summary
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
