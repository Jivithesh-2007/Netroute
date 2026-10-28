from typing import List
BG_PAGE = '#F8FAFC'
BG_CARD = '#FFFFFF'
PRIMARY = '#2563EB'
PRIMARY_DARK = '#1E40AF'
CYAN = '#0891B2'
PURPLE = '#7C3AED'
SUCCESS = '#10B981'
WARNING = '#F59E0B'
ERROR = '#EF4444'
TEXT_MAIN = '#0F172A'
TEXT_MUTED = '#475569'
BORDER = '#CBD5E1'
COLOR_NODE_DEFAULT = '#2563EB'
COLOR_NODE_SOURCE = '#10B981'
COLOR_NODE_DEST = '#F59E0B'
COLOR_NODE_ACTIVE = '#7C3AED'
COLOR_NODE_VISITED = '#38BDF8'
COLOR_NODE_ROUTE = '#059669'
COLOR_NODE_OFFLINE = '#94A3B8'
COLOR_PACKET = '#DC2626'
COLOR_EDGE_DEFAULT = '#CBD5E1'
COLOR_EDGE_EXPLORED = '#F59E0B'
COLOR_EDGE_ROUTE = '#10B981'
COLOR_EDGE_TREE = '#8B5CF6'
COLOR_EDGE_ACTIVE = '#7C3AED'
CUSTOM_CSS = f'\n<style>\n    /* Global Container */\n    .stApp {{\n        background-color: {BG_PAGE} !important;\n        color: {TEXT_MAIN} !important;\n        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;\n    }}\n    \n    /* Standard Text */\n    p, span, div, label, h1, h2, h3, h4, h5, h6 {{\n        color: {TEXT_MAIN} !important;\n    }}\n    \n    /* Buttons */\n    .stButton > button {{\n        background-color: #FFFFFF !important;\n        color: {TEXT_MAIN} !important;\n        border: 1px solid #94A3B8 !important;\n        border-radius: 6px !important;\n        font-weight: 600 !important;\n        font-size: 0.88rem !important;\n        padding: 6px 14px !important;\n        transition: all 0.15s ease-in-out !important;\n    }}\n    .stButton > button:hover {{\n        background-color: #F1F5F9 !important;\n        color: {PRIMARY_DARK} !important;\n        border-color: {PRIMARY} !important;\n    }}\n    .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {{\n        background-color: {PRIMARY} !important;\n        color: #FFFFFF !important;\n        border: 1px solid {PRIMARY_DARK} !important;\n    }}\n    .stButton > button[kind="primary"] p, .stButton > button[data-testid="baseButton-primary"] p {{\n        color: #FFFFFF !important;\n    }}\n    .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {{\n        background-color: {PRIMARY_DARK} !important;\n        color: #FFFFFF !important;\n    }}\n\n    /* Inputs, Selectboxes */\n    div[data-baseweb="select"] * {{\n        color: {TEXT_MAIN} !important;\n    }}\n    div[data-baseweb="input"] input {{\n        color: {TEXT_MAIN} !important;\n        background-color: #FFFFFF !important;\n    }}\n    .stSelectbox label, .stTextInput label {{\n        color: {TEXT_MAIN} !important;\n        font-weight: 600 !important;\n    }}\n\n    /* Sidebar Navigation Radio Buttons */\n    [data-testid="stSidebar"] div[data-testid="stRadio"] > label {{\n        display: none !important;\n    }}\n    [data-testid="stSidebar"] div[data-testid="stRadio"] > div {{\n        gap: 3px !important;\n    }}\n    [data-testid="stSidebar"] div[data-testid="stRadio"] label {{\n        padding: 7px 12px !important;\n        border-radius: 6px !important;\n        cursor: pointer !important;\n        transition: all 0.15s ease !important;\n        font-weight: 600 !important;\n        font-size: 0.88rem !important;\n        color: {TEXT_MAIN} !important;\n    }}\n    [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{\n        background-color: #E2E8F0 !important;\n        color: {PRIMARY} !important;\n    }}\n\n    /* Navigation Tabs */\n    button[data-baseweb="tab"] {{\n        color: #475569 !important;\n        font-weight: 600 !important;\n        font-size: 0.95rem !important;\n        padding: 10px 18px !important;\n    }}\n    button[data-baseweb="tab"][aria-selected="true"] {{\n        color: {PRIMARY} !important;\n        border-bottom: 2px solid {PRIMARY} !important;\n        font-weight: 700 !important;\n    }}\n\n    /* Path Pills */\n    .path-pill-container {{\n        display: flex;\n        align-items: center;\n        flex-wrap: wrap;\n        gap: 6px;\n        background-color: #1E293B;\n        padding: 10px 14px;\n        border-radius: 8px;\n        margin: 8px 0;\n    }}\n    .path-pill {{\n        background-color: #0F172A;\n        color: #38BDF8 !important;\n        font-weight: 700;\n        font-size: 0.9rem;\n        padding: 4px 10px;\n        border-radius: 6px;\n        border: 1px solid #334155;\n    }}\n    .path-arrow {{\n        color: #94A3B8 !important;\n        font-weight: 700;\n        font-size: 0.95rem;\n    }}\n\n    /* Step Log Card */\n    .step-card {{\n        background: #FFFFFF;\n        border: 1px solid #CBD5E1;\n        border-left: 4px solid {PRIMARY};\n        border-radius: 6px;\n        padding: 12px 16px;\n        margin-bottom: 10px;\n    }}\n    .step-card-header {{\n        font-weight: 700;\n        font-size: 0.85rem;\n        color: {PRIMARY} !important;\n        text-transform: uppercase;\n        margin-bottom: 4px;\n    }}\n    .step-card-desc {{\n        font-size: 0.92rem;\n        color: {TEXT_MAIN} !important;\n        line-height: 1.4;\n    }}\n\n    /* Stat Cards */\n    .metric-card {{\n        background: #FFFFFF;\n        border: 1px solid {BORDER};\n        border-radius: 8px;\n        padding: 12px 16px;\n        text-align: left;\n    }}\n    .metric-card-label {{\n        font-size: 0.78rem;\n        font-weight: 600;\n        color: {TEXT_MUTED} !important;\n        text-transform: uppercase;\n    }}\n    .metric-card-val {{\n        font-size: 1.5rem;\n        font-weight: 700;\n        color: {TEXT_MAIN} !important;\n        margin: 4px 0;\n    }}\n\n    /* Search Visualizer Array Container */\n    .search-array-container {{\n        display: flex;\n        gap: 10px;\n        align-items: flex-start;\n        flex-wrap: wrap;\n        margin: 12px 0;\n        padding: 14px;\n        background: #F8FAFC;\n        border-radius: 8px;\n        border: 1px solid #CBD5E1;\n    }}\n    .search-cell {{\n        display: flex;\n        flex-direction: column;\n        align-items: center;\n        min-width: 54px;\n    }}\n    .search-cell-idx {{\n        font-size: 0.72rem;\n        font-weight: 600;\n        color: #64748B;\n        margin-bottom: 3px;\n    }}\n    .search-cell-box {{\n        width: 54px;\n        height: 44px;\n        display: flex;\n        align-items: center;\n        justify-content: center;\n        font-weight: 700;\n        font-size: 0.95rem;\n        border-radius: 6px;\n        border: 2px solid #CBD5E1;\n        background: #FFFFFF;\n        color: #0F172A;\n    }}\n    .search-cell-box-active {{\n        border-color: #7C3AED !important;\n        background: #7C3AED !important;\n        color: #FFFFFF !important;\n    }}\n    .search-cell-box-match {{\n        border-color: #10B981 !important;\n        background: #10B981 !important;\n        color: #FFFFFF !important;\n    }}\n    .search-cell-box-checked {{\n        border-color: #94A3B8 !important;\n        background: #E2E8F0 !important;\n        color: #64748B !important;\n    }}\n    .search-cell-box-dim {{\n        border-color: #E2E8F0 !important;\n        background: #F8FAFC !important;\n        color: #CBD5E1 !important;\n        border-style: dashed !important;\n    }}\n    .search-cell-pointer {{\n        font-size: 0.70rem;\n        font-weight: 700;\n        margin-top: 4px;\n        text-align: center;\n    }}\n</style>\n'

def render_path_pills(path: List[str]) -> str:
    if not path:
        return '<div style="color:#64748B; font-style:italic;">No path discovered</div>'
    items = []
    for i, node in enumerate(path):
        items.append(f'<span class="path-pill">{node}</span>')
        if i < len(path) - 1:
            items.append('<span class="path-arrow" style="display:inline-flex; align-items:center;"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="width:14px;height:14px;color:#94A3B8;"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" /></svg></span>')
    return f"""<div class="path-pill-container">{' '.join(items)}</div>"""

def render_step_card(step_num: int, operation: str, description: str, color: str=PRIMARY, why: str='', neighbor_info: str='', route_info: str='') -> str:
    extra_html = ''
    if why:
        extra_html += f'<div style="margin-top:6px; font-size:0.86rem; color:#334155; background:#F8FAFC; border-left:3px solid {color}; padding:6px 10px; border-radius:4px;"><b>Action & Why:</b> {why}</div>'
    if neighbor_info:
        extra_html += f'<div style="margin-top:4px; font-size:0.80rem; color:#64748B;">{neighbor_info}</div>'
    if route_info:
        extra_html += f'<div style="margin-top:4px; font-size:0.80rem; color:#059669;"><b>Current Route Reconstruction:</b> {route_info}</div>'
    return f'\n    <div class="step-card" style="border-left-color: {color};">\n        <div class="step-card-header" style="color: {color} !important;">STEP {step_num} | {operation}</div>\n        <div class="step-card-desc">{description}</div>\n        {extra_html}\n    </div>\n    '
