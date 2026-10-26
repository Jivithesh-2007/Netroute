class Theme:
    BG_PAGE = "#F4F7FC"
    BG_SURFACE = "#FFFFFF"
    PRIMARY = "#2563EB"
    CYAN = "#0891B2"
    PURPLE = "#7C3AED"
    SUCCESS = "#16A34A"
    WARNING = "#F59E0B"
    ERROR = "#DC2626"
    TEXT_MAIN = "#172033"
    TEXT_MUTED = "#475569"
    BORDER = "#D8E1EE"

    COLOR_DEFAULT_NODE = "#2563EB"
    COLOR_VISITED_NODE = "#93C5FD"
    COLOR_EXPLORE_NODE = "#F59E0B"
    COLOR_ROUTE_NODE = "#16A34A"
    COLOR_OFFLINE_NODE = "#94A3B8"
    COLOR_SOURCE_NODE = "#2563EB"
    COLOR_DEST_NODE = "#7C3AED"
    COLOR_PACKET = "#E11D48"

    COLOR_DEFAULT_EDGE = "#CBD5E1"
    COLOR_EXPLORE_EDGE = "#F59E0B"
    COLOR_ROUTE_EDGE = "#16A34A"
    COLOR_TREE_EDGE = "#8B5CF6"


CUSTOM_CSS = f"""
<style>
    .stApp {{
        background-color: {Theme.BG_PAGE};
        color: {Theme.TEXT_MAIN};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    .metric-card {{
        background: {Theme.BG_SURFACE};
        border: 1px solid {Theme.BORDER};
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    .metric-card-title {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: {Theme.TEXT_MUTED};
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }}
    .metric-card-value {{
        font-size: 1.5rem;
        font-weight: 800;
        color: {Theme.PRIMARY};
        line-height: 1.1;
    }}
    .metric-card-sub {{
        font-size: 0.75rem;
        color: {Theme.TEXT_MUTED};
        margin-top: 4px;
    }}
    .badge-co {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-right: 6px;
        border: 1px solid {Theme.BORDER};
        background: {Theme.BG_SURFACE};
    }}
    .chip {{
        display: inline-block;
        padding: 4px 10px;
        margin: 2px 4px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
    }}
    .chip-front {{ background-color: #DBEAFE; color: #1E40AF; border: 1px solid #93C5FD; }}
    .chip-rear {{ background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }}
    .chip-normal {{ background-color: #F1F5F9; color: #334155; border: 1px solid #CBD5E1; }}
    .chip-top {{ background-color: #EDE9FE; color: #5B21B6; border: 1px solid #C4B5FD; }}
    .chip-bottom {{ background-color: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; }}
    .chip-visited {{ background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }}
    .log-container {{
        background: #0F172A;
        color: #F8FAFC;
        border-radius: 8px;
        padding: 12px;
        font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
        font-size: 0.82rem;
        max-height: 280px;
        overflow-y: auto;
        line-height: 1.45;
    }}
    .log-entry {{
        margin-bottom: 4px;
    }}
    .log-step {{ color: #38BDF8; font-weight: bold; }}
    .log-type {{ color: #FBBF24; font-weight: bold; }}
    .log-success {{ color: #4ADE80; font-weight: bold; }}
    .log-msg {{ color: #E2E8F0; }}
</style>
"""


def render_metric(title: str, value: str, subtitle: str = "", color: str = Theme.PRIMARY) -> str:
    return (
        f'<div class="metric-card" style="border-top: 3px solid {color};">'
        f'<div class="metric-card-title">{title}</div>'
        f'<div class="metric-card-value" style="color: {color};">{value}</div>'
        f'<div class="metric-card-sub">{subtitle}</div>'
        f'</div>'
    )
