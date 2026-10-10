"""
MODULE D — PERFORMANCE COMPARISON DASHBOARD
Empirical benchmarking and performance comparisons for graph algorithms,
searching, sorting, hash table collision strategies, and tree structures.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from app.theme import Theme
from app.widgets import CardFrame, StatCard
from services.benchmark_service import BenchmarkService


class PerformanceDashboardView(ttk.Frame):
    """Performance Dashboard module view."""

    def __init__(self, parent, app=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.app = app

        self.benchmark_data = None
        self._build_ui()
        self.run_benchmark_suite()

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Toolbar Card
        toolbar = CardFrame(self, padding=8)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(toolbar, text="Benchmark Suite:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.suite_combo = ttk.Combobox(
            toolbar,
            values=["Sorting Algorithms Comparison", "Searching Algorithms Comparison", "BST vs AVL Tree Benchmark"],
            state="readonly",
            width=28
        )
        self.suite_combo.current(0)
        self.suite_combo.pack(side="left", padx=(0, 12))
        self.suite_combo.bind("<<ComboboxSelected>>", lambda e: self.render_charts())

        btn_run = ttk.Button(toolbar, text="▶ Run Benchmarks", style="Primary.TButton", command=self.run_benchmark_suite)
        btn_run.pack(side="left", padx=4)

        self.status_lbl = ttk.Label(toolbar, text="Ready.", style="Card.TLabel")
        self.status_lbl.pack(side="right", padx=8)

        # Content Split Layout: Chart Canvas on Left, Comparison Data Table on Right
        content = ttk.Frame(self, style="TFrame")
        content.grid(row=1, column=0, sticky="nsew")

        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)

        # Left: Canvas Chart
        chart_card = CardFrame(content, title="Empirical Measured Execution Time (ms)")
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.chart_canvas = tk.Canvas(chart_card, bg=Theme.BG_CANVAS, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)

        # Right: Benchmark Data Treeview Table
        table_card = CardFrame(content, title="Benchmark Results Table")
        table_card.grid(row=0, column=1, sticky="nsew")

        self.tree = ttk.Treeview(
            table_card,
            columns=("Alg", "Size", "Ops", "Time"),
            show="headings",
            height=15
        )
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("Alg", text="Algorithm")
        self.tree.heading("Size", text="N Size")
        self.tree.heading("Ops", text="Comparisons / Ops")
        self.tree.heading("Time", text="Runtime (ms)")

        self.tree.column("Alg", width=110)
        self.tree.column("Size", width=60)
        self.tree.column("Ops", width=100)
        self.tree.column("Time", width=90)

    def run_benchmark_suite(self):
        """Execute real algorithm benchmarks."""
        self.status_lbl.config(text="Running benchmarks...")
        self.update_idletasks()

        self.sort_results = BenchmarkService.benchmark_sorting([20, 50, 100, 200])
        self.search_results = BenchmarkService.benchmark_searching([100, 500, 1000, 2000])
        self.tree_results = BenchmarkService.benchmark_trees(500)

        self.status_lbl.config(text="Benchmark execution complete.")
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
        # Render Bar Chart for Largest Size (200 elements)
        target_size = 200
        data_points = []
        for alg_name, size_list in self.sort_results.items():
            for item in size_list:
                if item["size"] == target_size:
                    data_points.append((alg_name, item["time_ms"], item["comparisons"]))
                self.tree.insert("", "end", values=(alg_name, item["size"], item["comparisons"], f"{item['time_ms']:.3f}"))

        self._draw_bar_chart(data_points, f"Sorting Benchmark (Array Size N = {target_size})")

    def _render_searching_chart(self):
        target_size = 2000
        data_points = []
        for alg_name, size_list in self.search_results.items():
            for item in size_list:
                if item["size"] == target_size:
                    data_points.append((alg_name, item["time_ms"], item["comparisons"]))
                self.tree.insert("", "end", values=(alg_name, item["size"], item["comparisons"], f"{item['time_ms']:.4f}"))

        self._draw_bar_chart(data_points, f"Searching Benchmark (Array Size N = {target_size})")

    def _render_tree_chart(self):
        data_points = []
        for tree_type, metrics in self.tree_results.items():
            data_points.append((f"{tree_type} Insert", metrics["insert_time_ms"], metrics["num_ops"]))
            data_points.append((f"{tree_type} Search", metrics["search_time_ms"], metrics["search_comparisons"]))
            self.tree.insert("", "end", values=(tree_type, metrics["num_ops"], metrics["search_comparisons"], f"{metrics['insert_time_ms']:.3f}"))

        self._draw_bar_chart(data_points, "BST vs AVL Tree Sequential Operations (N = 500)")

    def _draw_bar_chart(self, data_points, title: str):
        cw = self.chart_canvas.winfo_width() or 500
        ch = self.chart_canvas.winfo_height() or 400

        self.chart_canvas.create_text(20, 20, text=title, fill=Theme.ACCENT_CYAN, font=Theme.FONT_TITLE, anchor="w")

        if not data_points:
            return

        max_val = max(p[1] for p in data_points) if max(p[1] for p in data_points) > 0 else 1.0

        n = len(data_points)
        margin_x = 60
        margin_y = 60
        avail_w = cw - 2 * margin_x
        bar_w = max(20, avail_w / n - 20)

        colors = [Theme.ACCENT_CYAN, Theme.ACCENT_BLUE, Theme.COLOR_SUCCESS, Theme.COLOR_EXPLORE]

        for i, (label, val, ops) in enumerate(data_points):
            x1 = margin_x + i * (bar_w + 20)
            x2 = x1 + bar_w

            h_factor = (val / max_val) * (ch - 140)
            y2 = ch - margin_y
            y1 = y2 - h_factor

            fill = colors[i % len(colors)]
            self.chart_canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=Theme.BORDER_COLOR, width=1)
            self.chart_canvas.create_text((x1 + x2) / 2, y1 - 12, text=f"{val:.3f} ms", fill=Theme.TEXT_MAIN, font=Theme.FONT_BOLD)
            self.chart_canvas.create_text((x1 + x2) / 2, y2 + 16, text=label, fill=Theme.TEXT_MAIN, font=Theme.FONT_SMALL)
            self.chart_canvas.create_text((x1 + x2) / 2, y2 + 32, text=f"({ops} ops)", fill=Theme.TEXT_MUTED, font=Theme.FONT_SMALL)
