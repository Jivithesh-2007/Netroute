import sys
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Any

class Theme:
    BG_APP = "#F4F7FC"
    BG_SIDEBAR = "#FFFFFF"
    BG_CARD = "#FFFFFF"
    BG_PANEL = "#F8FAFC"
    BG_SELECTED = "#DBEAFE"

    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#1D4ED8"
    SECONDARY = "#0EA5E9"
    PURPLE = "#7C3AED"
    TEAL = "#0D9488"
    SUCCESS = "#16A34A"
    WARNING = "#EA580C"
    ERROR = "#DC2626"

    COLOR_OFFLINE = "#94A3B8"
    COLOR_EXPLORE = "#EA580C"
    COLOR_VISITED = "#DBEAFE"

    TEXT_MAIN = "#172033"
    TEXT_MUTED = "#64748B"
    TEXT_DISABLED = "#94A3B8"
    TEXT_LIGHT = "#FFFFFF"

    BORDER = "#E2E8F0"

    FONT_FAMILY = "Helvetica"
    FONT_TITLE = ("Helvetica", 14, "bold")
    FONT_HEADER = ("Helvetica", 12, "bold")
    FONT_SECTION = ("Helvetica", 11, "bold")
    FONT_BODY = ("Helvetica", 10, "normal")
    FONT_BOLD = ("Helvetica", 10, "bold")
    FONT_SMALL = ("Helvetica", 9, "normal")
    FONT_SMALL_BOLD = ("Helvetica", 9, "bold")
    FONT_MONO = ("Menlo", 9, "normal") if "darwin" in sys.platform else ("Courier", 9, "normal")

    @classmethod
    def setup_styles(cls, root: tk.Tk):
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=cls.BG_APP)
        style.configure("Sidebar.TFrame", background=cls.BG_SIDEBAR)
        style.configure("Card.TFrame", background=cls.BG_CARD)
        style.configure("Panel.TFrame", background=cls.BG_PANEL)

        style.configure("TLabel", background=cls.BG_APP, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("Header.TLabel", background=cls.BG_APP, foreground=cls.TEXT_MAIN, font=cls.FONT_TITLE)
        style.configure("Subtitle.TLabel", background=cls.BG_APP, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("Card.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("CardTitle.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_SECTION)
        style.configure("CardMuted.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("Muted.TLabel", background=cls.BG_APP, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)

        style.configure("TButton",
                        background=cls.BG_PANEL,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BOLD,
                        borderwidth=1,
                        relief="flat",
                        focuscolor="none",
                        padding=(10, 5))
        style.map("TButton",
                  background=[("pressed", "#E2E8F0"), ("active", "#EEF2F6"), ("disabled", "#F8FAFC")],
                  foreground=[("disabled", cls.TEXT_DISABLED)])

        style.configure("Primary.TButton",
                        background=cls.PRIMARY,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        borderwidth=0,
                        relief="flat",
                        focuscolor="none",
                        padding=(12, 5))
        style.map("Primary.TButton",
                  background=[("pressed", "#1E40AF"), ("active", cls.PRIMARY_HOVER), ("disabled", "#93C5FD")],
                  foreground=[("disabled", "#DBEAFE")])

        style.configure("Secondary.TButton",
                        background=cls.SECONDARY,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 5))
        style.map("Secondary.TButton",
                  background=[("active", "#0284C7"), ("disabled", "#BAE6FD")])

        style.configure("Purple.TButton",
                        background=cls.PURPLE,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 5))
        style.map("Purple.TButton",
                  background=[("active", "#6D28D9"), ("disabled", "#DDD6FE")])

        style.configure("Success.TButton",
                        background=cls.SUCCESS,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 5))
        style.map("Success.TButton",
                  background=[("active", "#15803D"), ("disabled", "#86EFAC")])

        style.configure("Danger.TButton",
                        background=cls.ERROR,
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
                  background=[("active", cls.BG_SELECTED), ("disabled", cls.BG_PANEL)],
                  foreground=[("active", cls.PRIMARY), ("disabled", cls.TEXT_DISABLED)])

        style.configure("Nav.TButton",
                        background=cls.BG_SIDEBAR,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BODY,
                        borderwidth=0,
                        anchor="w",
                        padding=(12, 8))
        style.map("Nav.TButton",
                  background=[("selected", cls.BG_SELECTED), ("active", "#F1F5F9")],
                  foreground=[("selected", cls.PRIMARY), ("active", cls.PRIMARY)])

        style.configure("TCombobox",
                        background=cls.BG_CARD,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BODY,
                        padding=4)

        style.configure("Treeview",
                        background=cls.BG_CARD,
                        foreground=cls.TEXT_MAIN,
                        fieldbackground=cls.BG_CARD,
                        font=cls.FONT_SMALL,
                        rowheight=24)
        style.configure("Treeview.Heading",
                        background=cls.BG_PANEL,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_SMALL_BOLD)
        style.map("Treeview",
                  background=[("selected", cls.BG_SELECTED)],
                  foreground=[("selected", cls.TEXT_MAIN)])


class CardFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self.configure(padding=kwargs.get("padding", 10))
        border = tk.Frame(self, bg=Theme.BORDER, width=1)
        border.place(x=0, y=0, relwidth=1, height=1)


class StatCard(ttk.Frame):
    def __init__(self, parent, title: str, value: str = "0", subtitle: str = "", color: str = Theme.PRIMARY, **kwargs):
        super().__init__(parent, style="Card.TFrame", padding=(10, 8), **kwargs)
        self.pack_propagate(False)

        top_line = tk.Frame(self, bg=color, height=3)
        top_line.pack(fill="x", side="top", pady=(0, 4))

        self.lbl_title = tk.Label(self, text=title.upper(), font=Theme.FONT_SMALL_BOLD, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, anchor="w")
        self.lbl_title.pack(fill="x")

        self.lbl_val = tk.Label(self, text=value, font=Theme.FONT_TITLE, bg=Theme.BG_CARD, fg=color, anchor="w")
        self.lbl_val.pack(fill="x")

        self.lbl_sub = tk.Label(self, text=subtitle, font=Theme.FONT_SMALL, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, anchor="w")
        self.lbl_sub.pack(fill="x")

    def update_val(self, value: str, subtitle: Optional[str] = None):
        self.lbl_val.config(text=value)
        if subtitle is not None:
            self.lbl_sub.config(text=subtitle)


class ConsoleLog(ttk.Frame):
    def __init__(self, parent, height: int = 6, **kwargs):
        super().__init__(parent, style="Card.TFrame", padding=(6, 6), **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hdr = ttk.Frame(self, style="Card.TFrame")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(hdr, text="Execution Trace & Step Log", style="CardTitle.TLabel").pack(side="left")

        clear_btn = ttk.Button(hdr, text="Clear", style="Tool.TButton", command=self.clear, width=6)
        clear_btn.pack(side="right")

        text_container = tk.Frame(self, bg=Theme.BORDER, padx=1, pady=1)
        text_container.grid(row=1, column=0, sticky="nsew")

        self.text = tk.Text(
            text_container,
            height=height,
            font=Theme.FONT_MONO,
            bg="#1E293B",
            fg="#F8FAFC",
            wrap="word",
            bd=0,
            padx=8,
            pady=6
        )
        scroll = ttk.Scrollbar(text_container, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)

        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.text.tag_configure("info", foreground="#93C5FD")
        self.text.tag_configure("success", foreground="#4ADE80")
        self.text.tag_configure("warning", foreground="#FDBA74")
        self.text.tag_configure("error", foreground="#F87171")
        self.text.tag_configure("highlight", foreground="#FDE047")

    def log(self, message: str, level: str = "info"):
        self.text.config(state="normal")
        self.text.insert("end", f"• {message}\n", level)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


class ControlBar(ttk.Frame):
    def __init__(
        self,
        parent,
        on_play: Callable[[], None],
        on_pause: Callable[[], None],
        on_step: Callable[[], None],
        on_reset: Callable[[], None],
        on_speed_change: Callable[[int], None],
        **kwargs
    ):
        super().__init__(parent, style="Card.TFrame", padding=(8, 6), **kwargs)

        self.btn_play = ttk.Button(self, text="▶ Play", style="Success.TButton", command=on_play, width=7)
        self.btn_play.pack(side="left", padx=3)

        self.btn_pause = ttk.Button(self, text="⏸ Pause", style="TButton", command=on_pause, width=7)
        self.btn_pause.pack(side="left", padx=3)

        self.btn_step = ttk.Button(self, text="⏭ Step", style="Primary.TButton", command=on_step, width=7)
        self.btn_step.pack(side="left", padx=3)

        self.btn_reset = ttk.Button(self, text="↺ Reset", style="TButton", command=on_reset, width=7)
        self.btn_reset.pack(side="left", padx=3)

        ttk.Label(self, text="Speed:", style="Card.TLabel").pack(side="left", padx=(12, 4))
        self.speed_var = tk.IntVar(value=400)
        self.slider = ttk.Scale(self, from_=1000, to_=50, variable=self.speed_var, orient="horizontal", length=110)
        self.slider.pack(side="left", padx=3)
        self.slider.bind("<Motion>", lambda e: on_speed_change(int(self.speed_var.get())))
        self.slider.bind("<ButtonRelease-1>", lambda e: on_speed_change(int(self.speed_var.get())))

        self.step_label = ttk.Label(self, text="Step: 0/0", style="CardMuted.TLabel")
        self.step_label.pack(side="right", padx=6)

    def update_step(self, current: int, total: int):
        self.step_label.config(text=f"Step: {current}/{total}")

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
        super().__init__(parent, style="Card.TFrame", padding=(4, 2), **kwargs)

        self.btn_zoom_in = ttk.Button(self, text="+ Zoom In", style="Tool.TButton", command=on_zoom_in, width=9)
        self.btn_zoom_in.pack(side="left", padx=2)

        self.btn_zoom_out = ttk.Button(self, text="- Zoom Out", style="Tool.TButton", command=on_zoom_out, width=10)
        self.btn_zoom_out.pack(side="left", padx=2)

        self.btn_fit = ttk.Button(self, text="Fit View", style="Tool.TButton", command=on_fit_view, width=8)
        self.btn_fit.pack(side="left", padx=2)

        self.btn_reset = ttk.Button(self, text="1:1 Reset", style="Tool.TButton", command=on_reset_zoom, width=8)
        self.btn_reset.pack(side="left", padx=2)


class SimulationService:
    def __init__(self, root_widget: Optional[Any] = None):
        self.root = root_widget
        self.steps: List[Any] = []
        self.current_step_index: int = -1
        self.is_running: bool = False
        self.is_paused: bool = False
        self.speed_ms: int = 400
        self._timer_id: Optional[str] = None
        self.on_step_callback: Optional[Callable[[Any, int, int], None]] = None
        self.on_complete_callback: Optional[Callable[[], None]] = None

    def load_simulation(
        self,
        result: Any,
        on_step: Callable[[Any, int, int], None],
        on_complete: Optional[Callable[[], None]] = None
    ):
        self.stop()
        self.steps = getattr(result, "steps", [])
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
