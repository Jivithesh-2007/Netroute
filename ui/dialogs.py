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
