"""
Application design system, clean modern Light Theme tokens, typography, and TTK style configurations.
"""
import tkinter as tk
from tkinter import ttk


class Theme:
    """Modern Light Theme design system for NetRoute Desktop."""

    # Base Colors (Light Mode)
    BG_DARK = "#F1F5F9"       # Main Window Background (Slate 100)
    BG_SIDEBAR = "#0F172A"    # Sidebar Background (Slate 900 - sleek dark contrast)
    BG_CARD = "#FFFFFF"       # Main Card / Panel Background (Pure White)
    BG_CARD_ALT = "#F8FAFC"   # Secondary Panel Background (Slate 50)
    BG_CANVAS = "#FFFFFF"     # Crisp Canvas Background (Pure White)

    # Accent Colors
    ACCENT_BLUE = "#2563EB"   # Primary Action Accent (Royal Blue 600)
    ACCENT_CYAN = "#0284C7"   # Secondary Accent (Sky 600)
    ACCENT_INDIGO = "#4F46E5" # Sub-accent (Indigo 600)

    # Status Colors
    COLOR_SUCCESS = "#16A34A" # Reachable / Sorted / Success Green (Emerald 600)
    COLOR_EXPLORE = "#D97706" # Exploring / Probing / Queue Orange (Amber 600)
    COLOR_ERROR = "#DC2626"   # Disconnected / Unreachable Red (Red 600)
    COLOR_OFFLINE = "#94A3B8" # Offline / Disabled Node (Slate 400)
    COLOR_PACKET = "#DB2777"  # Packet Animation Pink (Pink 600)

    # Text Colors
    TEXT_MAIN = "#0F172A"     # Primary Text (Deep Slate 900)
    TEXT_MUTED = "#475569"    # Subtitle / Muted Text (Slate 600)
    TEXT_LIGHT = "#F8FAFC"    # Light text for dark buttons/sidebar
    TEXT_DARK = "#0F172A"     # Dark text

    # Visual Borders
    BORDER_COLOR = "#CBD5E1"  # Clean Light Border (Slate 300)

    # Typography
    FONT_FAMILY = "Helvetica"
    FONT_TITLE = (FONT_FAMILY, 16, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 11, "bold")
    FONT_BODY = (FONT_FAMILY, 10, "normal")
    FONT_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_SMALL = (FONT_FAMILY, 9, "normal")
    FONT_MONO = ("Courier", 10, "normal")

    @classmethod
    def setup_styles(cls, root: tk.Tk):
        """Configure native TTK widget styles to match the light theme."""
        style = ttk.Style(root)
        style.theme_use("clam")

        # Configure Frame styles
        style.configure("TFrame", background=cls.BG_DARK)
        style.configure("Sidebar.TFrame", background=cls.BG_SIDEBAR)
        style.configure("Card.TFrame", background=cls.BG_CARD, relief="flat", borderwidth=1)
        style.configure("CardAlt.TFrame", background=cls.BG_CARD_ALT, relief="flat", borderwidth=1)

        # Configure Label styles
        style.configure("TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("Header.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MAIN, font=cls.FONT_TITLE)
        style.configure("Subtitle.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MUTED, font=cls.FONT_SUBTITLE)
        style.configure("Card.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("CardTitle.TLabel", background=cls.BG_CARD, foreground=cls.ACCENT_BLUE, font=cls.FONT_BOLD)
        style.configure("Muted.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)

        # Configure Button styles
        style.configure("TButton",
                        background="#E2E8F0",
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BOLD,
                        borderwidth=1,
                        relief="flat",
                        focuscolor="none",
                        padding=(10, 6))
        style.map("TButton",
                  background=[("active", "#CBD5E1"), ("disabled", "#F1F5F9")],
                  foreground=[("active", cls.TEXT_MAIN), ("disabled", cls.TEXT_MUTED)])

        style.configure("Primary.TButton",
                        background=cls.ACCENT_BLUE,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(12, 6))
        style.map("Primary.TButton",
                  background=[("active", "#1D4ED8")],
                  foreground=[("active", cls.TEXT_LIGHT)])

        style.configure("Success.TButton",
                        background=cls.COLOR_SUCCESS,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 6))

        style.configure("Danger.TButton",
                        background=cls.COLOR_ERROR,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 6))

        # Sidebar Nav Button Style
        style.configure("Nav.TButton",
                        background=cls.BG_SIDEBAR,
                        foreground="#94A3B8",
                        font=cls.FONT_BOLD,
                        anchor="w",
                        padding=(16, 10),
                        borderwidth=0)
        style.map("Nav.TButton",
                  background=[("active", "#1E293B"), ("selected", cls.ACCENT_BLUE)],
                  foreground=[("active", "#38BDF8"), ("selected", cls.TEXT_LIGHT)])

        # Notebook / Tabs
        style.configure("TNotebook", background=cls.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#E2E8F0",
                        foreground=cls.TEXT_MUTED,
                        padding=(12, 6),
                        font=cls.FONT_BOLD)
        style.map("TNotebook.Tab",
                  background=[("selected", cls.ACCENT_BLUE)],
                  foreground=[("selected", cls.TEXT_LIGHT)])

        # Entry & Combobox
        style.configure("TEntry", fieldbackground=cls.BG_CARD, foreground=cls.TEXT_MAIN, insertcolor=cls.TEXT_MAIN)
        style.configure("TCombobox", fieldbackground=cls.BG_CARD, background="#E2E8F0", foreground=cls.TEXT_MAIN)

        # Scrollbar
        style.configure("TScrollbar", background="#CBD5E1", troughcolor=cls.BG_DARK, borderwidth=0, arrowsize=12)

        # Treeview (Table)
        style.configure("Treeview",
                        background=cls.BG_CARD,
                        fieldbackground=cls.BG_CARD,
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BODY,
                        rowheight=24)
        style.configure("Treeview.Heading",
                        background="#E2E8F0",
                        foreground=cls.TEXT_MAIN,
                        font=cls.FONT_BOLD)
        style.map("Treeview",
                  background=[("selected", cls.ACCENT_BLUE)],
                  foreground=[("selected", cls.TEXT_LIGHT)])
