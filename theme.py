"""
theme.py — Design System, Color Tokens, and High-Contrast SaaS Components.
Ensures 100% text visibility across all widgets, buttons, tabs, and cards.
Zero emojis used.
"""

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
    /* Global App Container */
    .stApp {{
        background-color: {BG_PAGE} !important;
        color: {TEXT_MAIN} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }}
    
    /* Global Text Visibility Fix */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {{
        color: {TEXT_MAIN} !important;
    }}
    
    /* Streamlit Default Buttons (Fix invisible button text) */
    .stButton > button {{
        background-color: #FFFFFF !important;
        color: {TEXT_MAIN} !important;
        border: 1px solid #94A3B8 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 6px 14px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease-in-out !important;
    }}
    .stButton > button:hover {{
        background-color: #F1F5F9 !important;
        color: {PRIMARY_DARK} !important;
        border-color: {PRIMARY} !important;
    }}
    .stButton > button:active {{
        background-color: #E2E8F0 !important;
        color: {PRIMARY_DARK} !important;
    }}
    
    /* Primary Buttons */
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
    
    /* Disabled Buttons */
    .stButton > button:disabled, .stButton > button[disabled] {{
        background-color: #F1F5F9 !important;
        color: #94A3B8 !important;
        border-color: #E2E8F0 !important;
        cursor: not-allowed !important;
        box-shadow: none !important;
    }}
    .stButton > button:disabled p, .stButton > button[disabled] p {{
        color: #94A3B8 !important;
    }}

    /* Download Buttons */
    .stDownloadButton > button {{
        background-color: #FFFFFF !important;
        color: {TEXT_MAIN} !important;
        border: 1px solid #94A3B8 !important;
        font-weight: 600 !important;
    }}
    .stDownloadButton > button p {{
        color: {TEXT_MAIN} !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: #F1F5F9 !important;
        color: {PRIMARY_DARK} !important;
    }}
    
    /* Inputs, Selectboxes, Radios */
    div[data-baseweb="select"] * {{
        color: {TEXT_MAIN} !important;
    }}
    div[data-baseweb="input"] input {{
        color: {TEXT_MAIN} !important;
        background-color: #FFFFFF !important;
    }}
    .stSelectbox label, .stTextInput label, .stSlider label, .stRadio label {{
        color: {TEXT_MAIN} !important;
        font-weight: 700 !important;
    }}
    .stRadio div[role="radiogroup"] label span {{
        color: {TEXT_MAIN} !important;
    }}

    /* Navigation Tabs */
    button[data-baseweb="tab"] {{
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 18px !important;
    }}
    button[data-baseweb="tab"] div {{
        color: #475569 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {PRIMARY} !important;
        border-bottom: 2px solid {PRIMARY} !important;
        font-weight: 700 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] div {{
        color: {PRIMARY} !important;
        font-weight: 700 !important;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }}
    .metric-label {{
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {TEXT_MUTED} !important;
        margin-bottom: 2px;
    }}
    .metric-value {{
        font-size: 1.45rem;
        font-weight: 800;
        line-height: 1.15;
    }}
    .metric-sub {{
        font-size: 0.74rem;
        color: {TEXT_MUTED} !important;
        margin-top: 2px;
    }}
    
    /* Status Badges */
    .badge-pill {{
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        background: #F1F5F9;
        color: {TEXT_MAIN} !important;
        border: 1px solid {BORDER};
        margin-right: 4px;
    }}
    .badge-status-ready {{ background: #EFF6FF; color: #1D4ED8 !important; border: 1px solid #BFDBFE; }}
    .badge-status-running {{ background: #FEF3C7; color: #B45309 !important; border: 1px solid #FDE68A; }}
    .badge-status-completed {{ background: #ECFDF5; color: #047857 !important; border: 1px solid #A7F3D0; }}
    .badge-status-blocked {{ background: #FEF2F2; color: #B91C1C !important; border: 1px solid #FECACA; }}
    
    /* Queue / Stack Chips */
    .chip {{
        display: inline-block;
        padding: 4px 10px;
        margin: 2px 3px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
    }}
    .chip-front {{ background: #DBEAFE; color: #1E40AF !important; border: 1px solid #93C5FD; }}
    .chip-rear  {{ background: #FEF3C7; color: #92400E !important; border: 1px solid #FCD34D; }}
    .chip-top   {{ background: #EDE9FE; color: #5B21B6 !important; border: 1px solid #C4B5FD; }}
    .chip-bot   {{ background: #F3F4F6; color: #1E293B !important; border: 1px solid #CBD5E1; }}
    .chip-item  {{ background: #F8FAFC; color: #334155 !important; border: 1px solid #CBD5E1; }}
    .chip-visited {{ background: #DCFCE7; color: #166534 !important; border: 1px solid #86EFAC; }}
    
    /* Alert / Banner Boxes */
    div[data-testid="stAlert"] {{
        background-color: #FFFFFF !important;
        color: {TEXT_MAIN} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 6px !important;
    }}
    div[data-testid="stAlert"] * {{
        color: {TEXT_MAIN} !important;
    }}
</style>
"""


def render_metric_card(label: str, value: str, sub: str = "", color: str = PRIMARY) -> str:
    """Renders a modern, responsive SaaS statistic card with guaranteed text visibility."""
    return f"""
    <div class="metric-card" style="border-top: 3px solid {color};">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color} !important;">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """
