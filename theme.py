"""
theme.py — Design System, Color Tokens, and SaaS Components for NetRoute.
"""

# Palette
BG_PAGE = "#F8FAFC"
BG_SURFACE = "#FFFFFF"
PRIMARY = "#2563EB"
PRIMARY_DARK = "#1E40AF"
CYAN = "#0891B2"
PURPLE = "#7C3AED"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"
TEXT_MAIN = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER = "#E2E8F0"

# Node & Link Visualization Colors
COLOR_NODE_DEFAULT = "#2563EB"
COLOR_NODE_SOURCE = "#10B981"
COLOR_NODE_DEST = "#F59E0B"
COLOR_NODE_ACTIVE = "#7C3AED"
COLOR_NODE_VISITED = "#38BDF8"
COLOR_NODE_ROUTE = "#059669"
COLOR_NODE_OFFLINE = "#94A3B8"
COLOR_PACKET = "#E11D48"

COLOR_EDGE_DEFAULT = "#CBD5E1"
COLOR_EDGE_EXPLORED = "#F59E0B"
COLOR_EDGE_ROUTE = "#10B981"
COLOR_EDGE_TREE = "#8B5CF6"
COLOR_EDGE_ACTIVE = "#7C3AED"

CUSTOM_CSS = f"""
<style>
    /* Global App Background */
    .stApp {{
        background-color: {BG_PAGE};
        color: {TEXT_MAIN};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    
    /* Top Header Bar */
    .netroute-header {{
        background: {BG_SURFACE};
        border-bottom: 1px solid {BORDER};
        padding: 12px 20px;
        margin-bottom: 16px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }}
    
    /* Metric Card */
    .metric-card {{
        background: {BG_SURFACE};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }}
    .metric-label {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {TEXT_MUTED};
        margin-bottom: 2px;
    }}
    .metric-value {{
        font-size: 1.45rem;
        font-weight: 800;
        color: {PRIMARY};
        line-height: 1.15;
    }}
    .metric-sub {{
        font-size: 0.72rem;
        color: {TEXT_MUTED};
        margin-top: 2px;
    }}
    
    /* Badges */
    .badge-pill {{
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        background: #F1F5F9;
        color: {TEXT_MUTED};
        border: 1px solid {BORDER};
        margin-right: 4px;
    }}
    .badge-status-ready {{ background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }}
    .badge-status-running {{ background: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }}
    .badge-status-completed {{ background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }}
    .badge-status-blocked {{ background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }}
    
    /* Queue / Stack Chips */
    .chip {{
        display: inline-block;
        padding: 4px 10px;
        margin: 2px 3px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
    }}
    .chip-front {{ background: #DBEAFE; color: #1E40AF; border: 1px solid #93C5FD; }}
    .chip-rear  {{ background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }}
    .chip-top   {{ background: #EDE9FE; color: #5B21B6; border: 1px solid #C4B5FD; }}
    .chip-bot   {{ background: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; }}
    .chip-item  {{ background: #F8FAFC; color: #334155; border: 1px solid #CBD5E1; }}
    .chip-visited {{ background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }}
    
    /* Panel Containers */
    .panel-box {{
        background: {BG_SURFACE};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }}
</style>
"""


def render_metric_card(label: str, value: str, sub: str = "", color: str = PRIMARY) -> str:
    """Renders a modern, responsive SaaS statistic card."""
    return f"""
    <div class="metric-card" style="border-top: 3px solid {color};">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """
