"""
Application design system, clean modern Light Theme tokens, typography, and TTK style configurations.
"""
import tkinter as tk
from tkinter import ttk


class Theme:
    """Modern Professional White Theme design system for NetRoute Desktop."""

    # Base Colors (Exact White Palette Specification)
    BG_DARK = "#F5F7FB"       # Application background
    BG_SIDEBAR = "#FFFFFF"    # Sidebar background
    BG_CARD = "#FFFFFF"       # Main surface / card background
    BG_CARD_ALT = "#F8FAFC"   # Subtle panel background
    BG_CANVAS = "#FFFFFF"     # Crisp canvas background
    BG_SELECTED = "#DBEAFE"   # Selected background

    # Accent Colors
    ACCENT_BLUE = "#2563EB"   # Primary blue
    ACCENT_HOVER = "#1D4ED8"  # Hover blue
    ACCENT_CYAN = "#0EA5E9"   # Secondary blue / cyan
    ACCENT_INDIGO = "#4F46E5" # Indigo accent

    # Status Colors
    COLOR_SUCCESS = "#15803D" # Success green
    COLOR_WARNING = "#D97706" # Warning / Exploring amber
    COLOR_EXPLORE = "#D97706" # Exploration amber
    COLOR_ERROR = "#DC2626"   # Error / Unreachable red
    COLOR_OFFLINE = "#94A3B8" # Offline / Disabled grey
    COLOR_PACKET = "#2563EB"  # Packet animation blue/indigo

    # Text Colors
    TEXT_MAIN = "#172033"     # Primary text
    TEXT_MUTED = "#64748B"    # Secondary text
    TEXT_DISABLED = "#94A3B8" # Disabled text
    TEXT_LIGHT = "#FFFFFF"    # Light text for solid buttons
    TEXT_DARK = "#172033"     # Dark text

    # Visual Borders
    BORDER_COLOR = "#E2E8F0"  # Border color
    BORDER_LIGHT = "#F1F5F9"  # Lighter border

    # Typography
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
        """Configure native TTK widget styles to match the white theme."""
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Configure Frame styles
        style.configure("TFrame", background=cls.BG_DARK)
        style.configure("Sidebar.TFrame", background=cls.BG_SIDEBAR)
        style.configure("Card.TFrame", background=cls.BG_CARD)
        style.configure("CardAlt.TFrame", background=cls.BG_CARD_ALT)
        style.configure("Subtle.TFrame", background=cls.BG_CARD_ALT)

        # Configure Label styles
        style.configure("TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("Header.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MAIN, font=cls.FONT_TITLE)
        style.configure("Subtitle.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MUTED, font=cls.FONT_SUBTITLE)
        style.configure("Card.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_BODY)
        style.configure("CardTitle.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MAIN, font=cls.FONT_SECTION)
        style.configure("CardSubtitle.TLabel", background=cls.BG_CARD, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("Muted.TLabel", background=cls.BG_DARK, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)
        style.configure("PanelMuted.TLabel", background=cls.BG_CARD_ALT, foreground=cls.TEXT_MUTED, font=cls.FONT_SMALL)

        # Standard secondary button
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

        # Primary solid blue button
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

        # Success button
        style.configure("Success.TButton",
                        background=cls.COLOR_SUCCESS,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 5))
        style.map("Success.TButton",
                  background=[("active", "#166534"), ("disabled", "#86EFAC")])

        # Danger button
        style.configure("Danger.TButton",
                        background=cls.COLOR_ERROR,
                        foreground=cls.TEXT_LIGHT,
                        font=cls.FONT_BOLD,
                        padding=(10, 5))
        style.map("Danger.TButton",
                  background=[("active", "#B91C1C"), ("disabled", "#FCA5A5")])

        # Compact toolbar button
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

        # Sidebar Nav Button Style
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

        # Notebook / Tabs
        style.configure("TNotebook", background=cls.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=cls.BG_CARD_ALT,
                        foreground=cls.TEXT_MUTED,
                        padding=(12, 6),
                        font=cls.FONT_BOLD)
        style.map("TNotebook.Tab",
                  background=[("selected", cls.BG_CARD), ("active", "#F1F5F9")],
                  foreground=[("selected", cls.ACCENT_BLUE), ("active", cls.TEXT_MAIN)])

        # Entry & Combobox
        style.configure("TEntry", fieldbackground=cls.BG_CARD, foreground=cls.TEXT_MAIN, insertcolor=cls.TEXT_MAIN, padding=4)
        style.configure("TCombobox", fieldbackground=cls.BG_CARD, background=cls.BG_CARD_ALT, foreground=cls.TEXT_MAIN, padding=4)
        style.map("TCombobox",
                  fieldbackground=[("readonly", cls.BG_CARD)],
                  selectbackground=[("readonly", cls.BG_SELECTED)],
                  selectforeground=[("readonly", cls.TEXT_MAIN)])

        # PanedWindow sash
        style.configure("TPanedwindow", background=cls.BG_DARK)
        style.configure("Sash", sashthickness=5, gripcount=0, background=cls.BORDER_COLOR)

        # Scrollbar
        style.configure("TScrollbar", background="#CBD5E1", troughcolor=cls.BG_DARK, borderwidth=0, arrowsize=11)

        # Treeview (Table)
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

        # Separator
        style.configure("TSeparator", background=cls.BORDER_COLOR)
