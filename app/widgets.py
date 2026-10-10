"""
Reusable desktop GUI components for NetRoute (Cards, Stat Boxes, Control Bar, Console Log).
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from app.theme import Theme


class CardFrame(ttk.Frame):
    """Container frame with card padding and light panel background."""

    def __init__(self, parent, title: Optional[str] = None, padding: int = 12, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self.config(padding=padding)

        if title:
            header_lbl = ttk.Label(self, text=title, style="CardTitle.TLabel")
            header_lbl.pack(anchor="w", pady=(0, 8))


class StatCard(ttk.Frame):
    """Compact status display card for operations, dataset size, and runtime metrics."""

    def __init__(self, parent, title: str, value: str = "--", accent_color: str = Theme.ACCENT_BLUE, **kwargs):
        super().__init__(parent, style="CardAlt.TFrame", padding=10, **kwargs)
        self.accent_color = accent_color

        self.title_lbl = ttk.Label(self, text=title, font=Theme.FONT_SMALL, background=Theme.BG_CARD_ALT, foreground=Theme.TEXT_MUTED)
        self.title_lbl.pack(anchor="w")

        self.val_lbl = tk.Label(self, text=value, font=(Theme.FONT_FAMILY, 16, "bold"), bg=Theme.BG_CARD_ALT, fg=accent_color)
        self.val_lbl.pack(anchor="w", pady=(2, 0))

    def update_value(self, new_value: str, color: Optional[str] = None):
        """Update stat card label text and optional color."""
        self.val_lbl.config(text=str(new_value))
        if color:
            self.val_lbl.config(fg=color)


class ConsoleLog(ttk.Frame):
    """Scrollable event console log displaying step-by-step algorithm output."""

    def __init__(self, parent, height: int = 5, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)

        header_frame = ttk.Frame(self, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 4))

        title_lbl = ttk.Label(header_frame, text="Execution Step Log", style="CardTitle.TLabel")
        title_lbl.pack(side="left")

        clear_btn = ttk.Button(header_frame, text="Clear Log", command=self.clear, width=10)
        clear_btn.pack(side="right")

        text_frame = ttk.Frame(self, style="Card.TFrame")
        text_frame.pack(fill="both", expand=True)

        self.text = tk.Text(
            text_frame,
            height=height,
            bg="#F8FAFC",
            fg=Theme.TEXT_MAIN,
            insertbackground=Theme.TEXT_MAIN,
            font=Theme.FONT_MONO,
            relief="solid",
            bd=1,
            wrap="word",
            state="disabled"
        )
        self.scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

    def log(self, message: str, level: str = "info"):
        """Append log line to console."""
        self.text.config(state="normal")
        prefix = "• "
        if level == "success":
            prefix = "✔ "
        elif level == "warning" or level == "explore":
            prefix = "➜ "
        elif level == "error":
            prefix = "✖ "

        self.text.insert("end", f"{prefix}{message}\n")
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        """Clear all console text."""
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


class ControlBar(ttk.Frame):
    """Control panel for Play, Pause, Step, Reset, and Animation Speed."""

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
        super().__init__(parent, style="Card.TFrame", padding=8, **kwargs)

        self.on_play = on_play
        self.on_pause = on_pause
        self.on_step = on_step
        self.on_reset = on_reset
        self.on_speed_change = on_speed_change

        # Controls Layout
        self.btn_play = ttk.Button(self, text="▶ Play", style="Primary.TButton", command=self.on_play, width=9)
        self.btn_play.pack(side="left", padx=4)

        self.btn_pause = ttk.Button(self, text="⏸ Pause", command=self.on_pause, width=9)
        self.btn_pause.pack(side="left", padx=4)

        self.btn_step = ttk.Button(self, text="⏭ Step", command=self.on_step, width=9)
        self.btn_step.pack(side="left", padx=4)

        self.btn_reset = ttk.Button(self, text="↺ Reset", command=self.on_reset, width=9)
        self.btn_reset.pack(side="left", padx=4)

        # Speed Control Slider
        speed_frame = ttk.Frame(self, style="Card.TFrame")
        speed_frame.pack(side="right", padx=8)

        lbl = ttk.Label(speed_frame, text="Speed:", style="Card.TLabel", font=Theme.FONT_SMALL)
        lbl.pack(side="left", padx=(0, 4))

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
            length=120,
            command=self._handle_speed_change
        )
        self.speed_slider.set(500)
        self.speed_slider.pack(side="left")

        self.speed_val_lbl = ttk.Label(speed_frame, text="500 ms", style="Card.TLabel", font=Theme.FONT_SMALL, width=8)
        self.speed_val_lbl.pack(side="left", padx=4)

    def _handle_speed_change(self, val):
        ms = int(float(val))
        self.speed_val_lbl.config(text=f"{ms} ms")
        if self.on_speed_change:
            self.on_speed_change(ms)
