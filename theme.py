import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional, List, Any
from network import SimulationStep, SimulationResult


class Theme:
    BG_DARK = "#F5F7FB"
    BG_SIDEBAR = "#FFFFFF"
    BG_CARD = "#FFFFFF"
    BG_CARD_ALT = "#F1F5F9"
    BG_CANVAS = "#FFFFFF"
    BG_SELECTED = "#DBEAFE"

    ACCENT_BLUE = "#2563EB"
    ACCENT_HOVER = "#1D4ED8"
    ACCENT_CYAN = "#0EA5E9"
    ACCENT_INDIGO = "#4F46E5"

    COLOR_SUCCESS = "#15803D"
    COLOR_WARNING = "#D97706"
    COLOR_EXPLORE = "#D97706"
    COLOR_ERROR = "#DC2626"
    COLOR_OFFLINE = "#94A3B8"
    COLOR_PACKET = "#2563EB"

    TEXT_MAIN = "#172033"
    TEXT_MUTED = "#64748B"
    TEXT_DISABLED = "#94A3B8"
    TEXT_LIGHT = "#FFFFFF"
    TEXT_DARK = "#172033"

    BORDER_COLOR = "#E2E8F0"
    BORDER_LIGHT = "#F1F5F9"

    FONT_FAMILY = "Helvetica"
    FONT_TITLE = (FONT_FAMILY, 15, "bold")
    FONT_HEADER = (FONT_FAMILY, 13, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 10, "normal")
    FONT_SECTION = (FONT_FAMILY, 11, "bold")
    FONT_BODY = (FONT_FAMILY, 10, "normal")
    FONT_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_SMALL = (FONT_FAMILY, 9, "normal")
    FONT_SMALL_BOLD = (FONT_FAMILY, 9, "bold")
    FONT_MONO = ("Menlo", 9, "normal") if "darwin" in __import__("sys").platform else ("Courier", 9, "normal")

    @classmethod
    def setup_styles(cls, root: tk.Tk):
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=cls.BG_DARK)
        style.configure("Sidebar.TFrame", background=cls.BG_SIDEBAR)
        style.configure("Card.TFrame", background=cls.BG_CARD)
        style.configure("CardAlt.TFrame", background=cls.BG_CARD_ALT)
        style.configure("Subtle.TFrame", background=cls.BG_CARD_ALT)

        style.configure("TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("Header.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MAIN, font=cls.FONT_TITLE)
        style.configure("Subtitle.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MUTED, font=cls.FONT_SUBTITLE)
        style.configure("Card.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("CardTitle.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_SECTION)
        style.configure("CardSubtitle.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("Muted.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("PanelMuted.TLabel", background=cls.BG_CARD_ALT, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)

        style.configure("TButton",
                        background=cls.BG_CARD_ALT,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BOLD,
                        borderwidth=1,
                        relief="flat",
                        focuscolor="none",
                        padding=(10, 5))
        style.map("TButton",
                  background=[("pressed", "#E2E8F0"), ("active", "#EEF2F6"), ("disabled", "#F8FAFC")],
                  foreground=[("pressed", cls.TEXT_MAIN), ("active", cls.TEXT_MAIN), ("disabled", cls.TEXT_DISABLED)])

        style.configure("Primary.TButton",
                        background=cls.ACCENT_BLUE,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        borderwidth=0,
                        relief="flat",
                        focuscolor="none",
                        padding=(12, 5))
        style.map("Primary.TButton",
                  background=[("pressed", "#1E40AF"), ("active", cls.ACCENT_HOVER), ("disabled", "#93C5FD")],
                  foreground=[("disabled", "#DBEAFE")])

        style.configure("Success.TButton",
                        background=cls.COLOR_SUCCESS,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 5))
        style.map("Success.TButton",
                  background=[("active", "#166534"), ("disabled", "#86EFAC")])

        style.configure("Danger.TButton",
                        background=cls.COLOR_ERROR,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 5))
        style.map("Danger.TButton",
                  background=[("active", "#B91C1C"), ("disabled", "#FCA5A5")])

        style.configure("Tool.TButton",
                        background=cls.BG_CARD,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_SMALL_BOLD,
                        borderwidth=1,
                        relief="flat",
                        padding=(8, 4))
        style.map("Tool.TButton",
                  background=[("active", cls.BG_SELECTED), ("disabled", cls.BG_CARD_ALT)],
                  foreground=[("active", cls.ACCENT_BLUE), ("disabled", cls.TEXT_DISABLED)])

        style.configure("Nav.TButton",
                        background=cls.BG_SIDEBAR,
                        foreground=cls.TEXT_MUTED,
                        font=cls.FONT_BOLD,
                        anchor="w",
                        padding=(14, 9),
                        borderwidth=0)
        style.map("Nav.TButton",
                  background=[("selected", cls.BG_SELECTED), ("active", cls.BG_CARD_ALT)],
                  foreground=[("selected", cls.ACCENT_BLUE), ("active", cls.TEXT_MAIN)])

        style.configure("TNotebook", background=cls.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=cls.BG_CARD_ALT,
                        foreground=cls.TEXT_MUTED,
                        padding=(12, 6),
                        font=cls.FONT_BOLD)
        style.map("TNotebook.Tab",
                  background=[("selected", cls.BG_CARD), ("active", "#F1F5F9")],
                  foreground=[("selected", cls.ACCENT_BLUE), ("active", cls.TEXT_MAIN)])

        style.configure("TEntry", fieldbackground=cls.BG_CARD, foreground=cls.TEXT_MAIN, insertcolor=cls.TEXT_MAIN, padding=4)
        style.configure("TCombobox", fieldbackground=cls.BG_CARD, background=cls.BG_CARD_ALT, foreground=cls.TEXT_MAIN, padding=4)
        style.map("TCombobox",
                  fieldbackground=[("readonly", cls.BG_CARD)],
                  selectbackground=[("readonly", cls.BG_SELECTED)],
                  selectforeground=[("readonly", cls.TEXT_MAIN)])

        style.configure("TPanedwindow", background=cls.BG_DARK)
        style.configure("Sash", sashthickness=5, gripcount=0, background=cls.BORDER_COLOR)

        style.configure("TScrollbar", background="#CBD5E1", troughcolor=cls.BG_DARK, borderwidth=0, arrowsize=11)

        style.configure("Treeview",
                        background=cls.BG_CARD,
                        fieldbackground=cls.BG_CARD,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BODY,
                        rowheight=26,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=cls.BG_CARD_ALT,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BOLD,
                        padding=5)
        style.map("Treeview",
                  background=[("selected", cls.BG_SELECTED)],
                  foreground=[("selected", cls.TEXT_MAIN)])

        style.configure("TSeparator", background=cls.BORDER_COLOR)


class CardFrame(ttk.Frame):
    def __init__(self, parent, title: Optional[str] = None, subtitle: Optional[str] = None, padding: int = 10, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self.config(padding=padding)

        if title:
            header_frame = ttk.Frame(self, style="Card.TFrame")
            header_frame.pack(fill="x", pady=(0, 6))

            title_lbl = ttk.Label(header_frame, text=title, style="CardTitle.TLabel")
            title_lbl.pack(side="left")

            if subtitle:
                sub_lbl = ttk.Label(header_frame, text=subtitle, style="CardSubtitle.TLabel")
                sub_lbl.pack(side="left", padx=(8, 0), pady=(1, 0))


class StatCard(ttk.Frame):
    def __init__(self, parent, title: str, value: str = "--", accent_color: str = Theme.ACCENT_BLUE, **kwargs):
        super().__init__(parent, style="CardAlt.TFrame", padding=(10, 8), **kwargs)
        self.accent_color = accent_color

        self.title_lbl = ttk.Label(
            self,
            text=title,
            font=Theme.FONT_SMALL,
            background=Theme.BG_CARD_ALT,
            foreground=Theme.TEXT_MUTED
        )
        self.title_lbl.pack(anchor="w")

        self.val_lbl = tk.Label(
            self,
            text=value,
            font=(Theme.FONT_FAMILY, 15, "bold"),
            bg=Theme.BG_CARD_ALT,
            fg=accent_color,
            anchor="w"
        )
        self.val_lbl.pack(anchor="w", pady=(2, 0), fill="x")

    def update_value(self, new_value: str, color: Optional[str] = None):
        self.val_lbl.config(text=str(new_value))
        if color:
            self.val_lbl.config(fg=color)


class ConsoleLog(ttk.Frame):
    def __init__(self, parent, height: int = 6, **kwargs):
        super().__init__(parent, style="Card.TFrame", padding=(10, 8), **kwargs)

        header_frame = ttk.Frame(self, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 6))

        title_lbl = ttk.Label(header_frame, text="Execution Step Log", style="CardTitle.TLabel")
        title_lbl.pack(side="left")

        actions_frame = ttk.Frame(header_frame, style="Card.TFrame")
        actions_frame.pack(side="right")

        self.btn_copy = ttk.Button(actions_frame, text="📋 Copy", style="Tool.TButton", command=self.copy_log)
        self.btn_copy.pack(side="left", padx=(0, 4))

        self.btn_export = ttk.Button(actions_frame, text="💾 Export", style="Tool.TButton", command=self.export_log)
        self.btn_export.pack(side="left", padx=(0, 4))

        self.btn_clear = ttk.Button(actions_frame, text="Clear", style="Tool.TButton", command=self.clear)
        self.btn_clear.pack(side="left")

        text_frame = ttk.Frame(self, style="Card.TFrame")
        text_frame.pack(fill="both", expand=True)

        self.text = tk.Text(
            text_frame,
            height=height,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            insertbackground=Theme.TEXT_MAIN,
            font=Theme.FONT_MONO,
            relief="solid",
            bd=1,
            wrap="word",
            state="disabled",
            padx=8,
            pady=6
        )
        self.scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self.text.tag_config("info", foreground=Theme.TEXT_MAIN)
        self.text.tag_config("explore", foreground=Theme.COLOR_EXPLORE)
        self.text.tag_config("success", foreground=Theme.COLOR_SUCCESS)
        self.text.tag_config("error", foreground=Theme.COLOR_ERROR)
        self.text.tag_config("warning", foreground=Theme.COLOR_WARNING)
        self.text.tag_config("route", foreground=Theme.ACCENT_BLUE)

    def log(self, message: str, level: str = "info"):
        self.text.config(state="normal")
        prefix = "• "
        tag = "info"
        if level == "success":
            prefix = "✔ "
            tag = "success"
        elif level in ["warning", "explore"]:
            prefix = "➜ "
            tag = "explore"
        elif level == "error":
            prefix = "✖ "
            tag = "error"
        elif level == "route":
            prefix = "★ "
            tag = "route"

        self.text.insert("end", f"{prefix}{message}\n", tag)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")

    def copy_log(self):
        self.text.config(state="normal")
        content = self.text.get("1.0", "end-1c")
        self.text.config(state="disabled")
        if content.strip():
            self.clipboard_clear()
            self.clipboard_append(content)
            orig_text = self.btn_copy.cget("text")
            self.btn_copy.config(text="✓ Copied")
            self.after(1200, lambda: self.btn_copy.config(text=orig_text))
        else:
            messagebox.showinfo("Log Empty", "Execution log is currently empty.")

    def export_log(self):
        self.text.config(state="normal")
        content = self.text.get("1.0", "end-1c")
        self.text.config(state="disabled")
        if not content.strip():
            messagebox.showinfo("Log Empty", "No log contents to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Execution Log"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Export Successful", f"Log saved successfully to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not save file: {e}")


class ControlBar(ttk.Frame):
    def __init__(
        self,
        parent,
        on_play: Callable[[], None],
        on_pause: Callable[[], None],
        on_step: Callable[[], None],
        on_reset: Callable[[], None],
        on_speed_change: Optional[Callable[[int], None]] = None,
        **kwargs
    ):
        super().__init__(parent, style="Card.TFrame", padding=(10, 6), **kwargs)

        self.on_play = on_play
        self.on_pause = on_pause
        self.on_step = on_step
        self.on_reset = on_reset
        self.on_speed_change = on_speed_change

        left_ctrls = ttk.Frame(self, style="Card.TFrame")
        left_ctrls.pack(side="left")

        self.btn_play = ttk.Button(left_ctrls, text="▶ Play", style="Primary.TButton", command=self.on_play, width=8)
        self.btn_play.pack(side="left", padx=(0, 6))

        self.btn_pause = ttk.Button(left_ctrls, text="⏸ Pause", command=self.on_pause, width=8)
        self.btn_pause.pack(side="left", padx=(0, 6))

        self.btn_step = ttk.Button(left_ctrls, text="⏭ Step", command=self.on_step, width=8)
        self.btn_step.pack(side="left", padx=(0, 6))

        self.btn_reset = ttk.Button(left_ctrls, text="↺ Reset", command=self.on_reset, width=8)
        self.btn_reset.pack(side="left", padx=(0, 12))

        self.step_frame = ttk.Frame(left_ctrls, style="CardAlt.TFrame", padding=(8, 4))
        self.step_frame.pack(side="left")

        self.step_lbl = ttk.Label(
            self.step_frame,
            text="Step: Idle",
            font=Theme.FONT_SMALL_BOLD,
            background=Theme.BG_CARD_ALT,
            foreground=Theme.TEXT_MUTED
        )
        self.step_lbl.pack()

        speed_frame = ttk.Frame(self, style="Card.TFrame")
        speed_frame.pack(side="right")

        lbl = ttk.Label(speed_frame, text="Delay:", style="Card.TLabel", font=Theme.FONT_SMALL)
        lbl.pack(side="left", padx=(0, 6))

        self.speed_slider = tk.Scale(
            speed_frame,
            from_=50,
            to=1500,
            orient="horizontal",
            showvalue=0,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MAIN,
            troughcolor="#E2E8F0",
            activebackground=Theme.ACCENT_BLUE,
            highlightthickness=0,
            bd=0,
            length=110,
            command=self._handle_speed_change
        )
        self.speed_slider.set(500)
        self.speed_slider.pack(side="left")

        self.speed_val_lbl = ttk.Label(speed_frame, text="500 ms", style="Card.TLabel", font=Theme.FONT_SMALL, width=7)
        self.speed_val_lbl.pack(side="left", padx=(6, 0))

    def _handle_speed_change(self, val):
        ms = int(float(val))
        self.speed_val_lbl.config(text=f"{ms} ms")
        if self.on_speed_change:
            self.on_speed_change(ms)

    def update_step_indicator(self, current: int, total: int):
        if total > 0:
            self.step_lbl.config(
                text=f"Step: {current} / {total}",
                foreground=Theme.ACCENT_BLUE
            )
        else:
            self.step_lbl.config(text="Step: Complete", foreground=Theme.COLOR_SUCCESS)

    def reset_step_indicator(self):
        self.step_lbl.config(text="Step: Idle", foreground=Theme.TEXT_MUTED)

    def set_running_state(self, is_running: bool, is_paused: bool = False):
        if is_running:
            self.btn_play.state(["disabled"])
            self.btn_pause.state(["!disabled"])
            self.btn_step.state(["disabled"])
        elif is_paused:
            self.btn_play.state(["!disabled"])
            self.btn_pause.state(["disabled"])
            self.btn_step.state(["!disabled"])
        else:
            self.btn_play.state(["!disabled"])
            self.btn_pause.state(["disabled"])
            self.btn_step.state(["!disabled"])


class ZoomPanToolbar(ttk.Frame):
    def __init__(
        self,
        parent,
        on_zoom_in: Callable[[], None],
        on_zoom_out: Callable[[], None],
        on_fit_view: Callable[[], None],
        on_reset_zoom: Callable[[], None],
        **kwargs
    ):
        super().__init__(parent, style="CardAlt.TFrame", padding=(4, 2), **kwargs)

        self.btn_zoom_in = ttk.Button(self, text="🔍+ In", style="Tool.TButton", command=on_zoom_in, width=7)
        self.btn_zoom_in.pack(side="left", padx=2)

        self.btn_zoom_out = ttk.Button(self, text="🔍- Out", style="Tool.TButton", command=on_zoom_out, width=7)
        self.btn_zoom_out.pack(side="left", padx=2)

        self.btn_fit = ttk.Button(self, text="⊡ Fit View", style="Tool.TButton", command=on_fit_view, width=8)
        self.btn_fit.pack(side="left", padx=2)

        self.btn_reset = ttk.Button(self, text="1:1 Reset", style="Tool.TButton", command=on_reset_zoom, width=7)
        self.btn_reset.pack(side="left", padx=2)


class SimulationService:
    def __init__(self, root_widget: Optional[Any] = None):
        self.root = root_widget
        self.steps: List[SimulationStep] = []
        self.current_step_index: int = -1
        self.is_running: bool = False
        self.is_paused: bool = False
        self.speed_ms: int = 500
        self._timer_id: Optional[str] = None
        self.on_step_callback: Optional[Callable[[SimulationStep, int, int], None]] = None
        self.on_complete_callback: Optional[Callable[[], None]] = None

    def load_simulation(
        self,
        result: SimulationResult,
        on_step: Callable[[SimulationStep, int, int], None],
        on_complete: Optional[Callable[[], None]] = None
    ):
        self.stop()
        self.steps = result.steps
        self.current_step_index = -1
        self.on_step_callback = on_step
        self.on_complete_callback = on_complete

    def play(self):
        if not self.steps:
            return
        self.is_running = True
        self.is_paused = False
        self._schedule_next_step()

    def pause(self):
        self.is_paused = True
        self.is_running = False
        self._cancel_timer()

    def stop(self):
        self.is_running = False
        self.is_paused = False
        self._cancel_timer()
        self.current_step_index = -1

    def step_forward(self):
        if not self.steps:
            return
        if self.current_step_index + 1 < len(self.steps):
            self.current_step_index += 1
            step = self.steps[self.current_step_index]
            if self.on_step_callback:
                self.on_step_callback(step, self.current_step_index + 1, len(self.steps))

    def set_speed(self, delay_ms: int):
        self.speed_ms = max(50, min(2000, delay_ms))

    def _schedule_next_step(self):
        self._cancel_timer()
        if not self.is_running or self.is_paused:
            return

        if self.current_step_index + 1 < len(self.steps):
            self.current_step_index += 1
            step = self.steps[self.current_step_index]
            if self.on_step_callback:
                self.on_step_callback(step, self.current_step_index + 1, len(self.steps))

            if self.root:
                self._timer_id = self.root.after(self.speed_ms, self._schedule_next_step)
        else:
            self.is_running = False
            if self.on_complete_callback:
                self.on_complete_callback()

    def _cancel_timer(self):
        if self._timer_id and self.root:
            try:
                self.root.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
