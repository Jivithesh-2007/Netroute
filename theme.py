"""
Theme and Design System for NetRoute SaaS Application.
Defines cohesive color palettes, typography styling, and badge/card components.
"""

# Palette
BG_PAGE = "#F8FAFC"
BG_CARD = "#FFFFFF"
PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"
CYAN = "#0891B2"
PURPLE = "#7C3AED"
SUCCESS = "#16A34A"
WARNING = "#F59E0B"
ERROR = "#DC2626"
TEXT_MAIN = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER = "#E2E8F0"

# Node & Edge Colors
COLOR_NODE_DEFAULT = "#FFFFFF"
COLOR_NODE_BORDER = "#2563EB"
COLOR_NODE_SOURCE = "#2563EB"
COLOR_NODE_DEST = "#7C3AED"
COLOR_NODE_VISITED = "#93C5FD"
COLOR_NODE_ACTIVE = "#F59E0B"
COLOR_NODE_ROUTE = "#16A34A"
COLOR_NODE_OFFLINE = "#94A3B8"
COLOR_PACKET = "#E11D48"

COLOR_EDGE_DEFAULT = "#CBD5E1"
COLOR_EDGE_EXPLORED = "#F59E0B"
COLOR_EDGE_ROUTE = "#16A34A"
COLOR_EDGE_TREE = "#8B5CF6"
COLOR_EDGE_ACTIVE = "#0891B2"

CUSTOM_CSS = f"""
<style>
    .stApp {{
        background-color: {BG_PAGE};
        color: {TEXT_MAIN};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .stat-card {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}
    .stat-label {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {TEXT_MUTED};
        margin-bottom: 2px;
    }}
    .stat-value {{
        font-size: 1.6rem;
        font-weight: 800;
        color: {PRIMARY};
        line-height: 1.2;
    }}
    .stat-sub {{
        font-size: 0.75rem;
        color: {TEXT_MUTED};
        margin-top: 2px;
    }}
    .co-badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        background: #FFFFFF;
        border: 1px solid {BORDER};
        margin-right: 6px;
    }}
    .chip {{
        display: inline-block;
        padding: 5px 12px;
        margin: 3px 4px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
    }}
    .chip-front {{ background: #DBEAFE; color: #1E40AF; border: 1px solid #93C5FD; }}
    .chip-rear  {{ background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }}
    .chip-top   {{ background: #EDE9FE; color: #5B21B6; border: 1px solid #C4B5FD; }}
    .chip-bot   {{ background: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; }}
    .chip-item  {{ background: #F8FAFC; color: #334155; border: 1px solid #CBD5E1; }}
    .chip-visited {{ background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }}
</style>
"""


def render_stat_card(label: str, value: str, sub: str = "", color: str = PRIMARY) -> str:
    """Helper to render a clean SaaS-style statistic card."""
    return f"""
    <div class="stat-card" style="border-top: 3px solid {color};">
        <div class="stat-label">{label}</div>
        <div class="stat-value" style="color: {color};">{value}</div>
        <div class="stat-sub">{sub}</div>
    </div>
    """
