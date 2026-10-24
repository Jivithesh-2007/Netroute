import sys
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Any

class Theme:
    BG_APP = "#F3F6FC"
    BG_CARD = "#FFFFFF"
    BG_PANEL = "#FFFFFF"
    BG_PANEL_ALT = "#F8FAFC"
    BG_SELECTED = "#DBEAFE"

    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#1D4ED8"
    SECONDARY = "#0891B2"
    SECONDARY_HOVER = "#0E7490"
    PURPLE = "#7C3AED"
    PURPLE_HOVER = "#6D28D9"
    SUCCESS = "#16A34A"
    WARNING = "#F59E0B"
    ERROR = "#DC2626"

    COLOR_VISITED = "#93C5FD"
    COLOR_EXPLORE = "#F59E0B"
    COLOR_ROUTE = "#16A34A"
    COLOR_OFFLINE = "#94A3B8"

    TEXT_MAIN = "#172033"
    TEXT_MUTED = "#475569"
    TEXT_DISABLED = "#94A3B8"
    TEXT_LIGHT = "#FFFFFF"

    BORDER = "#D8E1EE"

    FONT_FAMILY = "Helvetica"
    FONT_TITLE = ("Helvetica", 21, "bold")
    FONT_PAGE_HEAD = ("Helvetica", 17, "bold")
    FONT_SECTION = ("Helvetica", 14, "bold")
    FONT_BODY = ("Helvetica", 12, "normal")
    FONT_BOLD = ("Helvetica", 12, "bold")
    FONT_SMALL = ("Helvetica", 11, "normal")
    FONT_SMALL_BOLD = ("Helvetica", 11, "bold")
    FONT_STAT_VAL = ("Helvetica", 22, "bold")
    FONT_STAT_LBL = ("Helvetica", 12, "bold")
    FONT_MONO = ("Menlo", 11, "normal") if "darwin" in sys.platform else ("Consolas", 11, "normal")
    FONT_STATUS = ("Helvetica", 11, "normal")

    @classmethod
    def setup_styles(cls, root: tk.Tk):
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=cls.BG_APP)
        style.configure("Card.TFrame", background=cls.BG_CARD)
        style.configure("Panel.TFrame", background=cls.BG_PANEL)
        style.configure("PanelAlt.TFrame", background=cls.BG_PANEL_ALT)

        style.configure("TLabel", background=cls.BG_APP, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("Header.TLabel", background=cls.BG_APP, foreground=cls.TEXT_MAIN, font=cls.FONT_TITLE)
        style.configure("Subtitle.TLabel", background=cls.BG_APP, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("Card.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("CardTitle.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_SECTION)
        style.configure("CardMuted.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("Muted.TLabel", background=cls.BG_APP, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)

        style.configure("TButton",
                        background=cls.BG_PANEL_ALT,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BOLD,
                        borderwidth=1,
                        relief="flat",
                        focuscolor="none",
                        padding=(12, 6))
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
                        padding=(14, 6))
        style.map("Primary.TButton",
                  background=[("pressed", "#1E40AF"), ("active", cls.PRIMARY_HOVER), ("disabled", "#93C5FD")],
                  foreground=[("disabled", "#DBEAFE")])

        style.configure("Secondary.TButton",
                        background=cls.SECONDARY,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        borderwidth=0,
                        relief="flat",
                        focuscolor="none",
                        padding=(14, 6))
        style.map("Secondary.TButton",
                  background=[("pressed", "#0E7490"), ("active", cls.SECONDARY_HOVER), ("disabled", "#A5F3FC")],
                  foreground=[("disabled", "#CFFAFE")])

        style.configure("Purple.TButton",
                        background=cls.PURPLE,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        borderwidth=0,
                        relief="flat",
                        focuscolor="none",
                        padding=(14, 6))
        style.map("Purple.TButton",
                  background=[("pressed", "#581C87"), ("active", cls.PURPLE_HOVER), ("disabled", "#DDD6FE")],
                  foreground=[("disabled", "#F3E8FF")])

        style.configure("Success.TButton",
                        background=cls.SUCCESS,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        borderwidth=0,
                        relief="flat",
                        focuscolor="none",
                        padding=(14, 6))
        style.map("Success.TButton",
                  background=[("pressed", "#15803D"), ("active", "#15803D"), ("disabled", "#86EFAC")])

        style.configure("Tool.TButton",
                        background=cls.BG_PANEL_ALT,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BOLD,
                        borderwidth=1,
                        relief="flat",
                        padding=(10, 5))
        style.map("Tool.TButton",
                  background=[("active", cls.BG_SELECTED), ("disabled", cls.BG_PANEL)],
                  foreground=[("active", cls.PRIMARY), ("disabled", cls.TEXT_DISABLED)])

        style.configure("TCombobox",
                        background=cls.BG_CARD,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BODY,
                        padding=5)

        style.configure("Treeview",
                        background=cls.BG_CARD,
                        foreground=cls.TEXT_MAIN,
                        fieldbackground=cls.BG_CARD,
                        font=cls.FONT_SMALL,
                        rowheight=26)
        style.configure("Treeview.Heading",
                        background=cls.BG_PANEL_ALT,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_SMALL_BOLD)
        style.map("Treeview",
                  background=[("selected", cls.BG_SELECTED)],
                  foreground=[("selected", cls.TEXT_MAIN)])

        style.configure("TNotebook", background=cls.BG_APP, borderwidth=0)
        style.configure("TNotebook.Tab", background=cls.BG_PANEL_ALT, foreground=cls.TEXT_MUTED,
                        font=cls.FONT_SMALL_BOLD, padding=(14, 7))
        style.map("TNotebook.Tab",
                  background=[("selected", cls.BG_CARD)],
                  foreground=[("selected", cls.PRIMARY)])

class CardFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        padding = kwargs.pop("padding", 10)
        super().__init__(parent, style="Card.TFrame", padding=padding, **kwargs)
        border = tk.Frame(self, bg=Theme.BORDER, height=1)
        border.place(x=0, y=0, relwidth=1)

class StatCard(ttk.Frame):
    def __init__(self, parent, title: str, value: str = "0", subtitle: str = "", color: str = Theme.PRIMARY, height: int = 82, **kwargs):
        super().__init__(parent, style="Card.TFrame", padding=(10, 6), **kwargs)
        self.pack_propagate(False)
        self.configure(height=height)

        top_line = tk.Frame(self, bg=color, height=3)
        top_line.pack(fill="x", side="top", pady=(0, 4))

        self.lbl_title = tk.Label(self, text=title.upper(), font=Theme.FONT_STAT_LBL, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, anchor="w")
        self.lbl_title.pack(fill="x")

        self.lbl_val = tk.Label(self, text=value, font=Theme.FONT_STAT_VAL, bg=Theme.BG_CARD, fg=color, anchor="w")
        self.lbl_val.pack(fill="x")

        self.lbl_sub = tk.Label(self, text=subtitle, font=Theme.FONT_SMALL, bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, anchor="w")
        self.lbl_sub.pack(fill="x")

    def update_val(self, value: str, subtitle: Optional[str] = None):
        self.lbl_val.config(text=value)
        if subtitle is not None:
            self.lbl_sub.config(text=subtitle)

class ConsoleLog(ttk.Frame):
    def __init__(self, parent, height: int = 7, **kwargs):
        super().__init__(parent, style="Card.TFrame", padding=(8, 6), **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hdr = ttk.Frame(self, style="Card.TFrame")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(hdr, text="Execution Trace & Step Log", style="CardTitle.TLabel").pack(side="left")

        btn_box = ttk.Frame(hdr, style="Card.TFrame")
        btn_box.pack(side="right")

        copy_btn = ttk.Button(btn_box, text="Copy Log", style="Tool.TButton", command=self.copy_log)
        copy_btn.pack(side="left", padx=(0, 4))

        clear_btn = ttk.Button(btn_box, text="Clear Log", style="Tool.TButton", command=self.clear)
        clear_btn.pack(side="left")

        text_container = tk.Frame(self, bg=Theme.BORDER, padx=1, pady=1)
        text_container.grid(row=1, column=0, sticky="nsew")

        self.text = tk.Text(
            text_container,
            height=height,
            font=Theme.FONT_MONO,
            bg="#172033",
            fg="#F3F6FC",
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

    def copy_log(self):
        content = self.text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)

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

        self.btn_play = ttk.Button(self, text="▶ Play", style="Success.TButton", command=on_play)
        self.btn_play.pack(side="left", padx=3)

        self.btn_pause = ttk.Button(self, text="⏸ Pause", style="TButton", command=on_pause)
        self.btn_pause.pack(side="left", padx=3)

        self.btn_step = ttk.Button(self, text="⏭ Step Forward", style="Primary.TButton", command=on_step)
        self.btn_step.pack(side="left", padx=3)

        self.btn_reset = ttk.Button(self, text="↺ Reset Simulation", style="TButton", command=on_reset)
        self.btn_reset.pack(side="left", padx=3)

        ttk.Label(self, text="Delay (Speed):", style="Card.TLabel").pack(side="left", padx=(14, 4))
        self.speed_var = tk.IntVar(value=350)
        self.slider = ttk.Scale(self, from_=1000, to_=60, variable=self.speed_var, orient="horizontal", length=110)
        self.slider.pack(side="left", padx=3)
        self.slider.bind("<Motion>", lambda e: on_speed_change(int(self.speed_var.get())))
        self.slider.bind("<ButtonRelease-1>", lambda e: on_speed_change(int(self.speed_var.get())))

        self.step_label = ttk.Label(self, text="Step: 0 / 0", font=Theme.FONT_BOLD, style="CardTitle.TLabel")
        self.step_label.pack(side="right", padx=10)

    def update_step(self, current: int, total: int):
        self.step_label.config(text=f"Step: {current} / {total}")

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
        super().__init__(parent, style="Card.TFrame", padding=(4, 3), **kwargs)

        self.btn_zoom_in = ttk.Button(self, text="+ Zoom In", style="Tool.TButton", command=on_zoom_in)
        self.btn_zoom_in.pack(side="left", padx=2)

        self.btn_zoom_out = ttk.Button(self, text="- Zoom Out", style="Tool.TButton", command=on_zoom_out)
        self.btn_zoom_out.pack(side="left", padx=2)

        self.btn_fit = ttk.Button(self, text="Fit to View", style="Tool.TButton", command=on_fit_view)
        self.btn_fit.pack(side="left", padx=2)

        self.btn_reset = ttk.Button(self, text="1:1 Reset", style="Tool.TButton", command=on_reset_zoom)
        self.btn_reset.pack(side="left", padx=2)

class SimulationService:
    def __init__(self, root_widget: Optional[Any] = None):
        self.root = root_widget
        self.steps: List[Any] = []
        self.current_step_index: int = -1
        self.is_running: bool = False
        self.is_paused: bool = False
        self.speed_ms: int = 350
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
            if self.current_step_index + 1 == len(self.steps):
                self.is_running = False
                if self.on_complete_callback:
                    self.on_complete_callback()

    def set_speed(self, delay_ms: int):
        self.speed_ms = max(50, min(1500, delay_ms))

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
