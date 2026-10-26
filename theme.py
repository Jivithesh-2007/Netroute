# NetRoute — Clean Theme & Color Tokens

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

CSS = f"""
<style>
    .stApp {{ background-color: {BG_PAGE}; color: {TEXT_MAIN}; }}
    .card {{
        background: {BG_SURFACE};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }}
    .chip {{
        display: inline-block;
        padding: 4px 10px;
        margin: 2px 4px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }}
    .chip-front {{ background: #DBEAFE; color: #1E40AF; border: 1px solid #93C5FD; }}
    .chip-rear  {{ background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }}
    .chip-top   {{ background: #EDE9FE; color: #5B21B6; border: 1px solid #C4B5FD; }}
    .chip-bot   {{ background: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; }}
    .chip-item  {{ background: #F1F5F9; color: #334155; border: 1px solid #CBD5E1; }}
    .badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        background: {BG_SURFACE};
        border: 1px solid {BORDER};
        margin-right: 6px;
    }}
</style>
"""
