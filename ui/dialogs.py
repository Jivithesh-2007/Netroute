"""
Modal dialogs for user input (Add Router, Add Link, Custom Input).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.theme import Theme
from utils.validation import validate_router_id, parse_integer_list, parse_integer


class AddRouterDialog(tk.Toplevel):
    """Modal dialog to add a new router to network canvas."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add New Router")
        self.geometry("340x220")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_DARK)

        self.result = None

        # Container
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Router ID (e.g. R7):", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.id_entry = ttk.Entry(frame)
        self.id_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Display Name:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.name_entry = ttk.Entry(frame)
        self.name_entry.pack(fill="x", pady=(0, 16))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", side="bottom")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Add Router", style="Primary.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()
        self.id_entry.focus_set()

    def _on_submit(self):
        rid = self.id_entry.get().strip().upper()
        rname = self.name_entry.get().strip() or f"Router {rid}"

        valid, msg = validate_router_id(rid)
        if not valid:
            messagebox.showerror("Invalid Input", msg, parent=self)
            return

        self.result = (rid, rname)
        self.destroy()


class AddLinkDialog(tk.Toplevel):
    """Modal dialog to create an edge/link between two routers."""

    def __init__(self, parent, router_ids: list):
        super().__init__(parent)
        self.title("Add Network Link")
        self.geometry("340x220")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_DARK)

        self.result = None
        self.router_ids = router_ids

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Source Router:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.u_combo = ttk.Combobox(frame, values=router_ids, state="readonly")
        self.u_combo.pack(fill="x", pady=(0, 10))
        if router_ids:
            self.u_combo.current(0)

        ttk.Label(frame, text="Target Router:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.v_combo = ttk.Combobox(frame, values=router_ids, state="readonly")
        self.v_combo.pack(fill="x", pady=(0, 16))
        if len(router_ids) > 1:
            self.v_combo.current(1)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", side="bottom")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Add Link", style="Primary.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()

    def _on_submit(self):
        u = self.u_combo.get()
        v = self.v_combo.get()

        if not u or not v:
            messagebox.showerror("Invalid Selection", "Please select both source and target routers.", parent=self)
            return

        if u == v:
            messagebox.showerror("Invalid Connection", "Self-connections are not allowed.", parent=self)
            return

        self.result = (u, v)
        self.destroy()


class CustomArrayDialog(tk.Toplevel):
    """Modal dialog for entering a custom array of integers."""

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


class RemoveLinkDialog(tk.Toplevel):
    """Modal dialog to select and remove an existing link between routers."""

    def __init__(self, parent, edges: list):
        super().__init__(parent)
        self.title("Remove Network Link")
        self.geometry("360x200")
        self.resizable(False, False)
        self.configure(bg=Theme.BG_DARK)

        self.result = None
        self.edges = edges

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Select Link to Remove:", style="Card.TLabel").pack(anchor="w", pady=(0, 6))

        edge_strs = [f"{u} ⟷ {v}" for u, v, _ in edges]
        self.combo = ttk.Combobox(frame, values=edge_strs, state="readonly")
        self.combo.pack(fill="x", pady=(0, 16))
        if edge_strs:
            self.combo.current(0)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", side="bottom")

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Remove Link", style="Danger.TButton", command=self._on_submit).pack(side="right")

        self.transient(parent)
        self.grab_set()

    def _on_submit(self):
        idx = self.combo.current()
        if idx >= 0 and idx < len(self.edges):
            u, v, _ = self.edges[idx]
            self.result = (u, v)
            self.destroy()


class RouteComparisonDialog(tk.Toplevel):
    """Side-by-side comparison modal dialog for BFS vs DFS routing results."""

    def __init__(self, parent, bfs_res, dfs_res, src_id: str, dest_id: str):
        super().__init__(parent)
        self.title(f"Route Comparison: {src_id} ➔ {dest_id}")
        self.geometry("640x480")
        self.minsize(580, 420)
        self.configure(bg=Theme.BG_DARK)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        header = ttk.Frame(frame)
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(
            header,
            text=f"Routing Comparison: '{src_id}' to '{dest_id}'",
            style="Header.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="CO5 Comparative Analysis: BFS (Shortest Hop) vs DFS (Depth-First Exploration)",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        # Comparison Table
        table_frame = ttk.Frame(frame, style="CardAlt.TFrame", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 12))

        columns = ("Metric", "BFS (Queue / FIFO)", "DFS (Stack / LIFO)")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=7)
        tree.pack(fill="both", expand=True)

        for col in columns:
            tree.heading(col, text=col)

        tree.column("Metric", width=160)
        tree.column("BFS (Queue / FIFO)", width=200)
        tree.column("DFS (Stack / LIFO)", width=200)

        bfs_path_str = " -> ".join(bfs_res.path) if bfs_res.success else "None (Unreachable)"
        dfs_path_str = " -> ".join(dfs_res.path) if dfs_res.success else "None (Unreachable)"
        bfs_hops = str(len(bfs_res.path) - 1) if bfs_res.success else "--"
        dfs_hops = str(len(dfs_res.path) - 1) if dfs_res.success else "--"

        tree.insert("", "end", values=("Route Status", "Reachable ✔" if bfs_res.success else "Unreachable ✖", "Reachable ✔" if dfs_res.success else "Unreachable ✖"))
        tree.insert("", "end", values=("Hops (Edges)", f"{bfs_hops} hops (Optimal)", f"{dfs_hops} hops (Not guaranteed)"))
        tree.insert("", "end", values=("Route Sequence", bfs_path_str, dfs_path_str))
        tree.insert("", "end", values=("Visited Routers", f"{len(bfs_res.visited_order)} routers", f"{len(dfs_res.visited_order)} routers"))
        tree.insert("", "end", values=("Explored Steps", f"{bfs_res.total_steps} steps", f"{dfs_res.total_steps} steps"))
        tree.insert("", "end", values=("Time Complexity", "O(V + E)", "O(V + E)"))
        tree.insert("", "end", values=("Space Complexity", "O(V) Queue", "O(V) Stack"))

        # Educational takeaway note card
        note_frame = ttk.Frame(frame, style="CardAlt.TFrame", padding=10)
        note_frame.pack(fill="x", pady=(0, 12))

        note_title = ttk.Label(note_frame, text="DSA Educational Analysis:", style="CardTitle.TLabel")
        note_title.pack(anchor="w", pady=(0, 4))

        note_text = (
            "• BFS guarantees the minimum hop count in an unweighted network because vertices are discovered level-by-level.\n"
            "• DFS explores a deep path first and backtracks, identifying reachability without guaranteeing optimal distance.\n"
            "• For production IP routing tables (OSPF/RIP), BFS-derived principles ensure shortest path delivery."
        )
        note_lbl = ttk.Label(note_frame, text=note_text, style="Card.TLabel", font=Theme.FONT_SMALL)
        note_lbl.pack(anchor="w")

        # Close button
        btn_close = ttk.Button(frame, text="Close", style="Primary.TButton", command=self.destroy)
        btn_close.pack(side="right")

        self.transient(parent)
        self.grab_set()

