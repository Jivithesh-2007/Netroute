import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any, Tuple
from theme import Theme, CardFrame, StatCard, ConsoleLog, ControlBar, SimulationService
from network import SimulationStep, SimulationResult
from algorithms import (
    linear_search, binary_search_iterative, binary_search_recursive, interpolation_search,
    bubble_sort, insertion_sort, selection_sort, merge_sort,
    schedule_tasks, HashTableChaining, HashTableLinearProbing,
    BenchmarkService, get_complexity_info, parse_integer, parse_integer_list
)

class CustomArrayDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Enter Custom Array")
        self.geometry("380x180")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_APP)
        self.result = None

        frame = CardFrame(self, padding=12)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        ttk.Label(frame, text="Enter numbers separated by spaces or commas:", style="Card.TLabel").pack(anchor="w", pady=(0, 4))
        self.entry = ttk.Entry(frame)
        self.entry.pack(fill="x", pady=(0, 6))
        self.entry.insert(0, "45, 12, 89, 34, 67, 23, 90, 11")

        ttk.Label(frame, text="Example: 10 20 30 40 50", style="CardMuted.TLabel").pack(anchor="w", pady=(0, 12))

        btn_box = ttk.Frame(frame, style="Card.TFrame")
        btn_box.pack(fill="x", side="bottom")
        ttk.Button(btn_box, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_box, text="Set Array", style="Primary.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()
        self.entry.focus_set()

    def _on_submit(self):
        valid, nums, msg = parse_integer_list(self.entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", msg, parent=self)
            return
        self.result = nums
        self.destroy()

class SearchingSortingLabView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app
        self.array: List[int] = [45, 12, 89, 34, 67, 23, 90, 11]
        self.sim_service = SimulationService(root_widget=self)
        self.current_result: Optional[SimulationResult] = None
        self._highlighted_indices = []
        self._secondary_indices = []

        self._build_ui()
        self.draw_bars(self.array)

    def on_hide(self):
        self.sim_service.stop()

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

        ttk.Label(top_ctrl, text="Algorithm:", style="Card.TLabel").pack(side="left", padx=(2, 4))
        self.cb_algo = ttk.Combobox(
            top_ctrl,
            values=[
                "Bubble Sort", "Insertion Sort", "Selection Sort", "Merge Sort",
                "Linear Search", "Binary Search (Iterative)", "Binary Search (Recursive)", "Interpolation Search"
            ],
            state="readonly",
            width=22
        )
        self.cb_algo.set("Bubble Sort")
        self.cb_algo.pack(side="left", padx=2)

        ttk.Label(top_ctrl, text="Target:", style="Card.TLabel").pack(side="left", padx=(8, 2))
        self.ent_target = ttk.Entry(top_ctrl, width=6)
        self.ent_target.insert(0, "34")
        self.ent_target.pack(side="left", padx=2)

        ttk.Button(top_ctrl, text="Execute", style="Primary.TButton", command=self.run_algorithm).pack(side="left", padx=6)
        ttk.Button(top_ctrl, text="Shuffle", style="Tool.TButton", command=self.shuffle_array).pack(side="left", padx=2)
        ttk.Button(top_ctrl, text="Custom Array", style="Tool.TButton", command=self.open_custom_array).pack(side="left", padx=2)

        canvas_card = CardFrame(main_col, padding=0)
        canvas_card.grid(row=1, column=0, sticky="nsew")
        canvas_card.grid_rowconfigure(0, weight=1)
        canvas_card.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_card, bg="#FFFFFF", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.draw_bars(self.array))

        bottom_bar = ttk.Frame(main_col, style="TFrame")
        bottom_bar.grid(row=2, column=0, sticky="ew", pady=(6, 0))

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

        self.stat_comp = StatCard(stats_row, title="Comparisons", value="0", subtitle="Operation count", color=Theme.PRIMARY, height=75)
        self.stat_comp.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.stat_swaps = StatCard(stats_row, title="Swaps / Writes", value="0", subtitle="Mutations", color=Theme.PURPLE, height=75)
        self.stat_swaps.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        sched_card = CardFrame(side_col, padding=(8, 6))
        sched_card.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(sched_card, text="Practical Task Scheduling (PrO-9):", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 2))
        ttk.Label(sched_card, text="Order jobs using sorting algorithms:", style="CardMuted.TLabel").pack(anchor="w", pady=(0, 4))

        sched_btns = ttk.Frame(sched_card, style="Card.TFrame")
        sched_btns.pack(fill="x")
        ttk.Button(sched_btns, text="By Priority", style="Tool.TButton", command=lambda: self.run_scheduling("priority")).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(sched_btns, text="By Deadline (EDF)", style="Tool.TButton", command=lambda: self.run_scheduling("deadline")).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(sched_btns, text="By Duration (SJF)", style="Tool.TButton", command=lambda: self.run_scheduling("duration")).pack(side="left", expand=True, fill="x", padx=1)

        self.console = ConsoleLog(side_col, height=12)
        self.console.grid(row=2, column=0, sticky="nsew")

    def shuffle_array(self):
        self.sim_service.stop()
        self.array = [random.randint(10, 100) for _ in range(10)]
        self.reset_simulation()
        self.console.log(f"Generated new random array: {self.array}", "info")

    def open_custom_array(self):
        dlg = CustomArrayDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.sim_service.stop()
            self.array = list(dlg.result)
            self.reset_simulation()
            self.console.log(f"Set custom array: {self.array}", "info")

    def run_algorithm(self):
        self.reset_simulation()
        name = self.cb_algo.get()

        if "Search" in name:
            valid, target, msg = parse_integer(self.ent_target.get())
            if not valid:
                messagebox.showerror("Invalid Input", msg, parent=self)
                return

            if "Binary" in name or "Interpolation" in name:
                self.array.sort()
                self.draw_bars(self.array)
                self.console.log("Pre-sorted array for logarithmic/interpolation search.", "info")

            if name == "Linear Search":
                res = linear_search(self.array, target)
            elif name == "Binary Search (Iterative)":
                res = binary_search_iterative(self.array, target)
            elif name == "Binary Search (Recursive)":
                res = binary_search_recursive(self.array, target)
            else:
                res = interpolation_search(self.array, target)
        else:
            if name == "Bubble Sort":
                res = bubble_sort(self.array)
            elif name == "Insertion Sort":
                res = insertion_sort(self.array)
            elif name == "Selection Sort":
                res = selection_sort(self.array)
            else:
                res = merge_sort(self.array)

        self.current_result = res
        self.console.log(f"Running {name} on array of size {len(self.array)}...", "info")
        self._load_and_run(res)

    def run_scheduling(self, sort_by: str):
        tasks = [
            {"id": "P1", "name": "OS Kernel Route Table Refresh", "priority": 1, "deadline": 4, "duration": 2},
            {"id": "P2", "name": "BGP Keepalive Packet Broadcast", "priority": 2, "deadline": 2, "duration": 1},
            {"id": "P3", "name": "Interface Error Log Backup", "priority": 4, "deadline": 10, "duration": 3},
            {"id": "P4", "name": "DHCP Lease Renewal Batch", "priority": 3, "deadline": 6, "duration": 2}
        ]
        sorted_tasks, rationale = schedule_tasks(tasks, sort_by=sort_by)
        self.console.clear()
        self.console.log(f"=== PR-9 PRACTICAL TASK SCHEDULING DEMO ({sort_by.upper()}) ===", "highlight")
        self.console.log(rationale, "info")
        self.console.log(f"{'Task':<6} {'Name':<32} {'Pri':<5} {'Dead':<6} {'Dur':<5} {'Comp':<5}", "warning")
        for t in sorted_tasks:
            self.console.log(f"{t['id']:<6} {t['name']:<32} {t['priority']:<5} {t['deadline']:<6} {t['duration']:<5} {t['completion_time']:<5}", "success" if t['slack'] >= 0 else "error")

    def _load_and_run(self, res: SimulationResult):
        def _on_step(step: SimulationStep, curr: int, total: int):
            self.control_bar.update_step(curr, total)
            self._highlighted_indices = step.highlight_indices
            self._secondary_indices = step.secondary_indices
            cur_arr = step.data_structure_state if step.data_structure_state else self.array
            self.draw_bars(cur_arr)
            lvl = "success" if step.step_type in ("found", "complete") else ("error" if step.step_type == "not_found" else "info")
            self.console.log(step.message, lvl)

        def _on_complete():
            self.control_bar.set_running_state(False)
            self._highlighted_indices = []
            self._secondary_indices = []
            if res.path and isinstance(res.path, list) and len(res.path) == len(self.array):
                self.array = list(res.path)
            self.draw_bars(self.array, is_final=True)
            self.stat_comp.update_val(str(res.total_comparisons), f"{res.execution_time_ms:.2f}ms")
            self.stat_swaps.update_val(str(res.total_swaps))
            self.console.log(f"Execution finished in {res.execution_time_ms:.2f} ms ({res.total_comparisons} comparisons).", "success")

        self.sim_service.load_simulation(res, _on_step, _on_complete)
        self.control_bar.set_running_state(True)
        self.sim_service.play()

    def reset_simulation(self):
        self.sim_service.stop()
        self._highlighted_indices = []
        self._secondary_indices = []
        self.control_bar.update_step(0, 0)
        self.control_bar.set_running_state(False)
        self.stat_comp.update_val("0", "Operation count")
        self.stat_swaps.update_val("0", "Mutations")
        self.draw_bars(self.array)

    def draw_bars(self, arr: List[int], is_final: bool = False):
        self.canvas.delete("all")
        if not arr:
            return

        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 260)
        n = len(arr)
        max_val = max(arr) if max(arr) > 0 else 1

        margin_x = 24
        margin_y = 35
        avail_w = cw - 2 * margin_x
        bar_w = max(10, (avail_w / n) - 6)
        avail_h = ch - 2 * margin_y

        for i, val in enumerate(arr):
            x0 = margin_x + i * (bar_w + 6)
            x1 = x0 + bar_w
            bar_h = (val / max_val) * avail_h
            y1 = ch - margin_y
            y0 = y1 - bar_h

            if is_final:
                color = Theme.SUCCESS
            elif i in self._highlighted_indices:
                color = Theme.WARNING
            elif i in self._secondary_indices:
                color = Theme.PURPLE
            else:
                color = Theme.PRIMARY

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#1E293B", width=1)
            self.canvas.create_text((x0 + x1) / 2, y0 - 8, text=str(val), font=Theme.FONT_SMALL_BOLD, fill=Theme.TEXT_MAIN)
            self.canvas.create_text((x0 + x1) / 2, y1 + 12, text=f"[{i}]", font=Theme.FONT_SMALL, fill=Theme.TEXT_MUTED)

class HashingLabView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app
        self.mode = "chaining"
        self.ht_chaining = HashTableChaining(size=7)
        self.ht_linear = HashTableLinearProbing(size=7)

        for k in [10, 24, 15, 31, 8]:
            self.ht_chaining.insert(k)
            self.ht_linear.insert(k)

        self._build_ui()
        self.redraw()

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
        side_col.grid_rowconfigure(1, weight=1)
        side_col.grid_columnconfigure(0, weight=1)

        top_ctrl = CardFrame(main_col, padding=(8, 6))
        top_ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(top_ctrl, text="Collision Mode:", style="Card.TLabel").pack(side="left", padx=(2, 4))
        self.cb_mode = ttk.Combobox(top_ctrl, values=["Separate Chaining (Linked Lists)", "Linear Probing (Open Addressing)"], state="readonly", width=30)
        self.cb_mode.set("Separate Chaining (Linked Lists)")
        self.cb_mode.pack(side="left", padx=2)
        self.cb_mode.bind("<<ComboboxSelected>>", self._on_mode_change)

        ttk.Label(top_ctrl, text="Key:", style="Card.TLabel").pack(side="left", padx=(10, 2))
        self.ent_key = ttk.Entry(top_ctrl, width=6)
        self.ent_key.insert(0, "42")
        self.ent_key.pack(side="left", padx=2)

        ttk.Button(top_ctrl, text="Insert", style="Primary.TButton", command=self.on_insert).pack(side="left", padx=2)
        ttk.Button(top_ctrl, text="Search", style="Success.TButton", command=self.on_search).pack(side="left", padx=2)
        ttk.Button(top_ctrl, text="Delete", style="Danger.TButton", command=self.on_delete).pack(side="left", padx=2)
        ttk.Button(top_ctrl, text="Reset", style="Tool.TButton", command=self.on_reset).pack(side="left", padx=4)

        canvas_card = CardFrame(main_col, padding=0)
        canvas_card.grid(row=1, column=0, sticky="nsew")
        canvas_card.grid_rowconfigure(0, weight=1)
        canvas_card.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_card, bg="#FFFFFF", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        stats_row = ttk.Frame(side_col, style="TFrame")
        stats_row.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        stats_row.grid_columnconfigure(0, weight=1)
        stats_row.grid_columnconfigure(1, weight=1)

        self.stat_load = StatCard(stats_row, title="Load Factor (α)", value="0.71", subtitle="N / Table Size", color=Theme.PRIMARY, height=75)
        self.stat_load.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.stat_count = StatCard(stats_row, title="Total Keys", value="5", subtitle="Active elements", color=Theme.SUCCESS, height=75)
        self.stat_count.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        self.console = ConsoleLog(side_col, height=14)
        self.console.grid(row=1, column=0, sticky="nsew")

    def _on_mode_change(self, event=None):
        txt = self.cb_mode.get()
        self.mode = "linear" if "Linear" in txt else "chaining"
        self.console.log(f"Switched hash collision resolution mode to: {txt}", "info")
        self.redraw()

    def on_insert(self):
        valid, val, msg = parse_integer(self.ent_key.get())
        if not valid:
            messagebox.showerror("Invalid Key", msg, parent=self)
            return

        if self.mode == "chaining":
            _, log_msg, _ = self.ht_chaining.insert(val)
        else:
            _, log_msg, _ = self.ht_linear.insert(val)

        self.console.log(log_msg, "success" if "inserted" in log_msg.lower() or "placed" in log_msg.lower() else "warning")
        self.redraw()

    def on_search(self):
        valid, val, msg = parse_integer(self.ent_key.get())
        if not valid:
            messagebox.showerror("Invalid Key", msg, parent=self)
            return

        if self.mode == "chaining":
            found, _, idx, probes = self.ht_chaining.search(val)
            res_msg = f"Key {val} found in bucket [{idx}] after {probes} comparisons." if found else f"Key {val} NOT found in bucket [{idx}]."
        else:
            found, _, path = self.ht_linear.search(val)
            res_msg = f"Key {val} discovered via probe path: {path}." if found else f"Key {val} NOT found after probing slots: {path}."

        self.console.log(res_msg, "success" if found else "error")

    def on_delete(self):
        valid, val, msg = parse_integer(self.ent_key.get())
        if not valid:
            messagebox.showerror("Invalid Key", msg, parent=self)
            return

        if self.mode == "chaining":
            ok, log_msg, _ = self.ht_chaining.delete(val)
        else:
            ok, log_msg, _ = self.ht_linear.delete(val)

        self.console.log(log_msg, "success" if ok else "warning")
        self.redraw()

    def on_reset(self):
        self.ht_chaining = HashTableChaining(size=7)
        self.ht_linear = HashTableLinearProbing(size=7)
        for k in [10, 24, 15, 31, 8]:
            self.ht_chaining.insert(k)
            self.ht_linear.insert(k)
        self.console.clear()
        self.console.log("Reset Hash Table with sample elements [10, 24, 15, 31, 8].", "info")
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)

        if self.mode == "chaining":
            lf = self.ht_chaining.load_factor()
            cnt = self.ht_chaining.total_elements
            state = self.ht_chaining.get_state()
            self.stat_load.update_val(f"{lf:.2f}", f"Size: {self.ht_chaining.size}")
            self.stat_count.update_val(str(cnt))

            start_x = 40
            start_y = 35
            slot_h = 32
            gap = 14

            for bucket_idx, keys in state:
                y = start_y + bucket_idx * (slot_h + gap)
                self.canvas.create_rectangle(start_x, y, start_x + 90, y + slot_h, fill=Theme.PRIMARY, outline="#0F172A", width=1)
                self.canvas.create_text(start_x + 45, y + slot_h / 2, text=f"Bucket [{bucket_idx}]", fill="#FFFFFF", font=Theme.FONT_SMALL_BOLD)

                cur_x = start_x + 90
                for k in keys:
                    self.canvas.create_line(cur_x, y + slot_h / 2, cur_x + 28, y + slot_h / 2, fill="#64748B", width=2, arrow="last")
                    cur_x += 28
                    self.canvas.create_rectangle(cur_x, y, cur_x + 55, y + slot_h, fill="#DBEAFE", outline=Theme.PRIMARY, width=1)
                    self.canvas.create_text(cur_x + 27, y + slot_h / 2, text=str(k), fill=Theme.TEXT_MAIN, font=Theme.FONT_BOLD)
                    cur_x += 55

                if not keys:
                    self.canvas.create_line(cur_x, y + slot_h / 2, cur_x + 24, y + slot_h / 2, fill="#CBD5E1", width=1, arrow="last")
                    self.canvas.create_text(cur_x + 38, y + slot_h / 2, text="NULL", fill="#94A3B8", font=Theme.FONT_SMALL)
        else:
            lf = self.ht_linear.load_factor()
            cnt = self.ht_linear.total_elements
            state = self.ht_linear.get_state()
            self.stat_load.update_val(f"{lf:.2f}", f"Size: {self.ht_linear.size}")
            self.stat_count.update_val(str(cnt))

            start_x = 40
            start_y = 35
            slot_w = 75
            slot_h = 42

            for i, key, status in state:
                x = start_x + (i % 4) * (slot_w + 35)
                y = start_y + (i // 4) * (slot_h + 40)

                if status == "Occupied":
                    fill_c = "#DBEAFE"
                    out_c = Theme.PRIMARY
                    txt = str(key)
                elif status == "Tombstone":
                    fill_c = "#FEE2E2"
                    out_c = Theme.ERROR
                    txt = "<DEL>"
                else:
                    fill_c = Theme.BG_PANEL
                    out_c = Theme.BORDER
                    txt = "EMPTY"

                self.canvas.create_rectangle(x, y, x + slot_w, y + slot_h, fill=fill_c, outline=out_c, width=2)
                self.canvas.create_text(x + slot_w / 2, y + 14, text=f"Slot [{i}]", font=Theme.FONT_SMALL, fill=Theme.TEXT_MUTED)
                self.canvas.create_text(x + slot_w / 2, y + 30, text=txt, font=Theme.FONT_BOLD, fill=Theme.TEXT_MAIN)

class PerformanceDashboardView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctrl = CardFrame(self, padding=(10, 8))
        ctrl.grid(row=0, column=0, sticky="ew", padx=2, pady=(0, 6))

        ttk.Label(ctrl, text="Category:", style="Card.TLabel").pack(side="left", padx=(2, 4))
        self.cb_cat = ttk.Combobox(ctrl, values=["Sorting Algorithms", "Searching Algorithms", "Tree Operations (BST vs AVL)"], state="readonly", width=26)
        self.cb_cat.set("Sorting Algorithms")
        self.cb_cat.pack(side="left", padx=2)

        ttk.Label(ctrl, text="Dataset Size:", style="Card.TLabel").pack(side="left", padx=(10, 4))
        self.cb_size = ttk.Combobox(ctrl, values=["50 Items", "100 Items", "250 Items"], state="readonly", width=12)
        self.cb_size.set("100 Items")
        self.cb_size.pack(side="left", padx=2)

        ttk.Button(ctrl, text="Run Empirical Benchmark", style="Primary.TButton", command=self.run_benchmark).pack(side="left", padx=8)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        left_pane = CardFrame(body, padding=8)
        body.add(left_pane, weight=2)
        left_pane.grid_rowconfigure(1, weight=1)
        left_pane.grid_columnconfigure(0, weight=1)

        ttk.Label(left_pane, text="Benchmark Runtime Comparison (ms)", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.canvas_chart = tk.Canvas(left_pane, bg="#FFFFFF", highlightthickness=0)
        self.canvas_chart.grid(row=1, column=0, sticky="nsew")

        right_pane = CardFrame(body, padding=8)
        body.add(right_pane, weight=3)
        right_pane.grid_rowconfigure(1, weight=1)
        right_pane.grid_columnconfigure(0, weight=1)

        ttk.Label(right_pane, text="Empirical Results & Big-O Reference", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))

        cols = ("Algorithm", "Input N", "Runtime (ms)", "Comparisons", "Time Complexity", "Space")
        self.tree = ttk.Treeview(right_pane, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=95, anchor="center")
        self.tree.column("Algorithm", width=130, anchor="w")
        self.tree.column("Time Complexity", width=110, anchor="center")

        scroll = ttk.Scrollbar(right_pane, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        scroll.grid(row=1, column=1, sticky="ns")

        self.after(200, self.run_benchmark)

    def run_benchmark(self):
        cat = self.cb_cat.get()
        size_txt = self.cb_size.get().split()[0]
        n = int(size_txt)

        self.tree.delete(*self.tree.get_children())
        chart_data = []

        if "Sorting" in cat:
            data = BenchmarkService.benchmark_sorting([n])
            for alg_name, runs in data.items():
                s, ms, ops = runs[0]
                cx = get_complexity_info(alg_name)
                self.tree.insert("", "end", values=(alg_name, s, f"{ms:.2f}", ops, cx["time_avg"], cx["space"]))
                chart_data.append((alg_name, ms))
        elif "Searching" in cat:
            data = BenchmarkService.benchmark_searching([n * 5])
            for alg_name, runs in data.items():
                s, ms, ops = runs[0]
                cx = get_complexity_info(alg_name)
                self.tree.insert("", "end", values=(alg_name, s, f"{ms:.3f}", ops, cx["time_avg"], cx["space"]))
                chart_data.append((alg_name, ms))
        else:
            data = BenchmarkService.benchmark_trees(n)
            for alg_name, ms in data.items():
                cx = get_complexity_info(f"{alg_name} Search")
                self.tree.insert("", "end", values=(f"{alg_name} Tree", n, f"{ms:.2f}", "-", cx["time_avg"], cx["space"]))
                chart_data.append((alg_name, ms))

        self.draw_chart(chart_data)

    def draw_chart(self, chart_data: List[Tuple[str, float]]):
        self.canvas_chart.delete("all")
        if not chart_data:
            return

        cw = max(self.canvas_chart.winfo_width(), 320)
        ch = max(self.canvas_chart.winfo_height(), 240)
        max_ms = max(ms for _, ms in chart_data) if chart_data else 1.0
        if max_ms == 0:
            max_ms = 0.01

        colors = [Theme.PRIMARY, Theme.SECONDARY, Theme.PURPLE, Theme.SUCCESS, Theme.WARNING]
        bar_w = 40
        gap = 25
        start_x = 35
        start_y = ch - 35
        avail_h = ch - 70

        for i, (name, ms) in enumerate(chart_data):
            x0 = start_x + i * (bar_w + gap)
            x1 = x0 + bar_w
            bar_h = max(4, (ms / max_ms) * avail_h)
            y0 = start_y - bar_h
            y1 = start_y

            c = colors[i % len(colors)]
            self.canvas_chart.create_rectangle(x0, y0, x1, y1, fill=c, outline="#0F172A", width=1)
            self.canvas_chart.create_text((x0 + x1) / 2, y0 - 8, text=f"{ms:.2f}ms", font=Theme.FONT_SMALL_BOLD, fill=Theme.TEXT_MAIN)
            self.canvas_chart.create_text((x0 + x1) / 2, y1 + 12, text=name.split()[0], font=Theme.FONT_SMALL, fill=Theme.TEXT_MUTED)

class LearningOutcomesView(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = CardFrame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        ttk.Label(container, text="Course Outcomes & Laboratory Practicum Mapping (25CS306)", style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        text_box = tk.Text(container, font=Theme.FONT_BODY, bg=Theme.BG_PANEL, bd=0, padx=12, pady=10, wrap="word")
        scroll = ttk.Scrollbar(container, orient="vertical", command=text_box.yview)
        text_box.configure(yscrollcommand=scroll.set)

        text_box.grid(row=1, column=0, sticky="nsew")
        scroll.grid(row=1, column=1, sticky="ns")

        content = """================================================================================
COURSE OUTCOMES (CO) ALIGNMENT
================================================================================
• CO3: Evaluate the performance of searching, sorting, and hashing algorithms for solving engineering problems.
• CO4: Develop and evaluate tree structures (BST, AVL, Heaps, B-Trees) for hierarchical data management.
• CO5: Evaluate graph data structures and traversal techniques (BFS, DFS) for network routing and connectivity.

================================================================================
LABORATORY PRACTICUM OUTCOMES (PrO) IMPLEMENTATION MAPPING
================================================================================
PrO-7  | Hash table with collision resolution
       | -> NetRoute implements Separate Chaining (linked lists) and Open Addressing (Linear Probing with tombstone markers).
       
PrO-8  | Search algorithm performance on large datasets
       | -> Implemented Linear, Binary (Iterative & Recursive), and Interpolation Search with real comparison counters and benchmark tables.

PrO-9  | Sorting technique for a scheduling problem
       | -> Real sorting algorithms (Bubble, Insertion, Selection, Merge) coupled with practical task scheduling by priority/deadline.

PrO-10 | Evaluate tree structures for data management
       | -> Structural comparisons between BST, AVL, Binary Heap (Min/Max), and B-Tree on real data.

PrO-11 | Store and retrieve hierarchical data using a tree
       | -> Preorder, Inorder, Postorder, and Level-Order traversals on BST/AVL with dynamic node additions.

PrO-12 | Evaluate balanced trees for search and update
       | -> Full AVL Tree rotations (LL, RR, LR, RL) guaranteeing O(log N) worst-case bounds, preventing degenerate trees.

PrO-13 | Adjacency Matrix and Adjacency List graph views
       | -> Live synchronized dual-representation tables (O(V+E) list and O(V^2) matrix) synchronized with network topology.

PrO-14 | Choose a suitable graph representation
       | -> Compares sparse network representation (Adjacency List) vs dense matrix for lookup and storage efficiency.

PrO-15 | Graph-based connectivity or routing applications
       | -> Interactive network routing simulator with BFS shortest-hop route discovery, DFS path finding, and packet animations.
"""
        text_box.insert("1.0", content)
        text_box.config(state="disabled")
