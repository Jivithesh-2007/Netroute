"""
MODULE D — PERFORMANCE COMPARISON DASHBOARD
Empirical benchmarking and performance comparisons for graph algorithms,
searching, sorting, hash table collision strategies, and tree structures,
with clean chart rendering, metrics cards, and results export.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, List

from app.theme import Theme
from app.widgets import CardFrame, StatCard
from services.benchmark_service import BenchmarkService


class PerformanceDashboardView(ttk.Frame):
    """Performance Dashboard module view with PanedWindow, dynamic charts and stats."""

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

        # Toolbar Card
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

        # PanedWindow Content Split Layout
        self.paned = ttk.Panedwindow(self, orient="horizontal")
        self.paned.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # Left: Canvas Chart
        chart_card = CardFrame(self.paned, title="Empirical Measured Execution Time (ms)", subtitle="Hardware-timed offline benchmarks", padding=8)
        self.paned.add(chart_card, weight=3)

        self.chart_canvas = tk.Canvas(chart_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)
        self.chart_canvas.bind("<Configure>", lambda e: self.render_charts())

        # Right: Benchmark Data Treeview Table
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
        """Execute real algorithm benchmarks using BenchmarkService."""
        self.status_lbl.config(text="Executing real algorithm benchmarks...")
        self.update_idletasks()

        self.sort_results = BenchmarkService.benchmark_sorting([20, 50, 100, 200])
        self.search_results = BenchmarkService.benchmark_searching([100, 500, 1000, 2000])
        self.tree_results = BenchmarkService.benchmark_trees(500)

        self.status_lbl.config(text="Benchmark execution complete (100% measured).")
        self.render_charts()

    def render_charts(self):
        """Render bar chart visualization based on active benchmark suite."""
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

        # Title
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

        # Baseline axis line
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
        """Export benchmark table results to CSV/Text file."""
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
