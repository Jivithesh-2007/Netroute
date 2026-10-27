"""
theme.py — Design System, Color Tokens, and Clean UI Styling.
Ensures 100% text visibility, clean light theme, and high contrast.
"""

from typing import List

# Color Palette
BG_PAGE = "#F8FAFC"
BG_CARD = "#FFFFFF"
PRIMARY = "#2563EB"
PRIMARY_DARK = "#1E40AF"
CYAN = "#0891B2"
PURPLE = "#7C3AED"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"
TEXT_MAIN = "#0F172A"
TEXT_MUTED = "#475569"
BORDER = "#CBD5E1"

# Graph Node & Link Colors
COLOR_NODE_DEFAULT = "#2563EB"
COLOR_NODE_SOURCE = "#10B981"
COLOR_NODE_DEST = "#F59E0B"
COLOR_NODE_ACTIVE = "#7C3AED"
COLOR_NODE_VISITED = "#38BDF8"
COLOR_NODE_ROUTE = "#059669"
COLOR_NODE_OFFLINE = "#94A3B8"
COLOR_PACKET = "#DC2626"

COLOR_EDGE_DEFAULT = "#CBD5E1"
COLOR_EDGE_EXPLORED = "#F59E0B"
COLOR_EDGE_ROUTE = "#10B981"
COLOR_EDGE_TREE = "#8B5CF6"
COLOR_EDGE_ACTIVE = "#7C3AED"

CUSTOM_CSS = f"""
<style>
    /* Global Container */
    .stApp {{
        background-color: {BG_PAGE} !important;
        color: {TEXT_MAIN} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }}
    
    /* Standard Text */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {{
        color: {TEXT_MAIN} !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: #FFFFFF !important;
        color: {TEXT_MAIN} !important;
        border: 1px solid #94A3B8 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 6px 14px !important;
        transition: all 0.15s ease-in-out !important;
    }}
    .stButton > button:hover {{
        background-color: #F1F5F9 !important;
        color: {PRIMARY_DARK} !important;
        border-color: {PRIMARY} !important;
    }}
    .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {{
        background-color: {PRIMARY} !important;
        color: #FFFFFF !important;
        border: 1px solid {PRIMARY_DARK} !important;
    }}
    .stButton > button[kind="primary"] p, .stButton > button[data-testid="baseButton-primary"] p {{
        color: #FFFFFF !important;
    }}
    .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {{
        background-color: {PRIMARY_DARK} !important;
        color: #FFFFFF !important;
    }}

    /* Inputs, Selectboxes */
    div[data-baseweb="select"] * {{
        color: {TEXT_MAIN} !important;
    }}
    div[data-baseweb="input"] input {{
        color: {TEXT_MAIN} !important;
        background-color: #FFFFFF !important;
    }}
    .stSelectbox label, .stTextInput label {{
        color: {TEXT_MAIN} !important;
        font-weight: 600 !important;
    }}

    /* Navigation Tabs */
    button[data-baseweb="tab"] {{
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 18px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {PRIMARY} !important;
        border-bottom: 2px solid {PRIMARY} !important;
        font-weight: 700 !important;
    }}

    /* Path Pills */
    .path-pill-container {{
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
        background-color: #1E293B;
        padding: 10px 14px;
        border-radius: 8px;
        margin: 8px 0;
    }}
    .path-pill {{
        background-color: #0F172A;
        color: #38BDF8 !important;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #334155;
    }}
    .path-arrow {{
        color: #94A3B8 !important;
        font-weight: 700;
        font-size: 0.95rem;
    }}

    /* Step Log Card */
    .step-card {{
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-left: 4px solid {PRIMARY};
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }}
    .step-card-header {{
        font-weight: 700;
        font-size: 0.85rem;
        color: {PRIMARY} !important;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}
    .step-card-desc {{
        font-size: 0.92rem;
        color: {TEXT_MAIN} !important;
        line-height: 1.4;
    }}

    /* Stat Cards */
    .metric-card {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
    }}
    .metric-card-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {TEXT_MUTED} !important;
        text-transform: uppercase;
    }}
    .metric-card-val {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {TEXT_MAIN} !important;
        margin: 4px 0;
    }}

    /* Search Visualizer Array Container */
    .search-array-container {{
        display: flex;
        gap: 10px;
        align-items: flex-start;
        flex-wrap: wrap;
        margin: 12px 0;
        padding: 14px;
        background: #F8FAFC;
        border-radius: 8px;
        border: 1px solid #CBD5E1;
    }}
    .search-cell {{
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 54px;
    }}
    .search-cell-idx {{
        font-size: 0.72rem;
        font-weight: 600;
        color: #64748B;
        margin-bottom: 3px;
    }}
    .search-cell-box {{
        width: 54px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.95rem;
        border-radius: 6px;
        border: 2px solid #CBD5E1;
        background: #FFFFFF;
        color: #0F172A;
    }}
    .search-cell-box-active {{
        border-color: #7C3AED !important;
        background: #7C3AED !important;
        color: #FFFFFF !important;
    }}
    .search-cell-box-match {{
        border-color: #10B981 !important;
        background: #10B981 !important;
        color: #FFFFFF !important;
    }}
    .search-cell-box-checked {{
        border-color: #94A3B8 !important;
        background: #E2E8F0 !important;
        color: #64748B !important;
    }}
    .search-cell-box-dim {{
        border-color: #E2E8F0 !important;
        background: #F8FAFC !important;
        color: #CBD5E1 !important;
        border-style: dashed !important;
    }}
    .search-cell-pointer {{
        font-size: 0.70rem;
        font-weight: 700;
        margin-top: 4px;
        text-align: center;
    }}
</style>
"""


def render_path_pills(path: List[str]) -> str:
    """Renders dark pill badges connected with arrows."""
    if not path:
        return '<div style="color:#64748B; font-style:italic;">No path discovered</div>'
    items = []
    for i, node in enumerate(path):
        items.append(f'<span class="path-pill">{node}</span>')
        if i < len(path) - 1:
            items.append('<span class="path-arrow">➔</span>')
    return f'<div class="path-pill-container">{" ".join(items)}</div>'


def render_step_card(step_num: int, operation: str, description: str, color: str = PRIMARY) -> str:
    """Renders a styled step execution card with operation tag."""
    return f"""
    <div class="step-card" style="border-left-color: {color};">
        <div class="step-card-header" style="color: {color} !important;">STEP {step_num} | {operation}</div>
        <div class="step-card-desc">{description}</div>
    </div>
    """
