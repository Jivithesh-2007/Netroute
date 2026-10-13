"""
Reusable desktop GUI components for NetRoute (Cards, Stat Boxes, Control Bar, Console Log, Zoom Controls).
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
from app.theme import Theme


class CardFrame(ttk.Frame):
    """Container frame with card padding, light surface background, and clean border."""

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
    """Compact status display card for operations, dataset size, and runtime metrics."""

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
        """Update stat card label text and optional color."""
        self.val_lbl.config(text=str(new_value))
        if color:
            self.val_lbl.config(fg=color)


class ConsoleLog(ttk.Frame):
    """Scrollable event console log displaying step-by-step algorithm output with Copy & Export."""

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

        # Configure color tags
        self.text.tag_config("info", foreground=Theme.TEXT_MAIN)
        self.text.tag_config("explore", foreground=Theme.COLOR_EXPLORE)
        self.text.tag_config("success", foreground=Theme.COLOR_SUCCESS)
        self.text.tag_config("error", foreground=Theme.COLOR_ERROR)
        self.text.tag_config("warning", foreground=Theme.COLOR_WARNING)
        self.text.tag_config("route", foreground=Theme.ACCENT_BLUE)

    def log(self, message: str, level: str = "info"):
        """Append log line to console with level formatting."""
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
        """Clear all console text."""
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")

    def copy_log(self):
        """Copy current log content to system clipboard."""
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
        """Export log content to local text file."""
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
    """Control panel for Play, Pause, Step, Reset, Step Indicator, and Animation Speed."""

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

        # Controls Layout - Left aligned actions
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

        # Step Progress Indicator Badge
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

        # Speed Control Slider - Right aligned
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
        """Update step progress badge."""
        if total > 0:
            self.step_lbl.config(
                text=f"Step: {current} / {total}",
                foreground=Theme.ACCENT_BLUE
            )
        else:
            self.step_lbl.config(text="Step: Complete", foreground=Theme.COLOR_SUCCESS)

    def reset_step_indicator(self):
        """Reset step badge to idle."""
        self.step_lbl.config(text="Step: Idle", foreground=Theme.TEXT_MUTED)

    def set_running_state(self, is_running: bool, is_paused: bool = False):
        """Adjust button states according to simulation status."""
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
    """Compact toolbar for Zoom In, Zoom Out, Fit to View, and Reset Zoom."""

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

