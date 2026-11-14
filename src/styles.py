"""
styles.py
=========
Premium CSS design system for SustainTour India.
Color palette: Deep teal sidebar (#142D2A), light content (#F7F9F8),
accent teal (#167D70), secondary green (#6BAE91).
"""


def get_custom_css() -> str:
    """Returns the full premium CSS to inject via st.markdown."""
    return """
    <style>
    /* ------------------------------------------------------------------ */
    /* TYPOGRAPHY                                                           */
    /* ------------------------------------------------------------------ */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont,
                     'Segoe UI', Roboto, sans-serif;
        color: #18332F;
    }

    /* ------------------------------------------------------------------ */
    /* MAIN LAYOUT                                                          */
    /* ------------------------------------------------------------------ */
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1440px;
        background-color: #F7F9F8;
    }

    /* ------------------------------------------------------------------ */
    /* SIDEBAR — dark premium theme                                         */
    /* ------------------------------------------------------------------ */
    section[data-testid="stSidebar"] {
        background-color: #142D2A !important;
        border-right: none !important;
    }
    section[data-testid="stSidebar"] * {
        color: #C8D8D5 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #A8C4BF !important;
        font-size: 0.9rem !important;
        padding: 0.35rem 0 !important;
        cursor: pointer !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #A8C4BF !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #2A4D49 !important;
    }

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem 0 0.1rem 0;
        margin-bottom: 0.1rem;
    }
    .sidebar-logo-text {
        font-size: 1.15rem;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }
    .sidebar-subtitle {
        font-size: 0.75rem;
        color: #6BAE91 !important;
        font-weight: 500;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .sidebar-nav-label {
        font-size: 0.68rem;
        font-weight: 700;
        color: #4A7A73 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
        margin-top: 0.5rem;
    }
    .sidebar-info-box {
        background: rgba(22, 125, 112, 0.12);
        border: 1px solid #2A4D49;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        font-size: 0.78rem;
        color: #8CBDB7 !important;
        line-height: 1.65;
        margin-top: 1rem;
    }
    .sidebar-info-box b {
        color: #6BAE91 !important;
    }

    /* ------------------------------------------------------------------ */
    /* PAGE HEADER                                                          */
    /* ------------------------------------------------------------------ */
    .page-header {
        background: #FFFFFF;
        border: 1px solid #E2E8E5;
        border-radius: 14px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px -2px rgba(22, 125, 112, 0.08);
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    .page-header-icon {
        font-size: 2rem;
        line-height: 1;
        flex-shrink: 0;
    }
    .page-header-title {
        font-size: 1.65rem;
        font-weight: 800;
        color: #18332F;
        margin: 0 0 0.2rem 0;
        letter-spacing: -0.025em;
    }
    .page-header-desc {
        font-size: 0.93rem;
        color: #475569;
        margin: 0;
        line-height: 1.55;
    }

    /* ------------------------------------------------------------------ */
    /* FILTER / CONTROL BAR                                                */
    /* ------------------------------------------------------------------ */
    .control-bar {
        background: #FFFFFF;
        border: 1px solid #E2E8E5;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .data-badge {
        background: #EEF7F5;
        border: 1px solid #C5E0DB;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.82rem;
        color: #167D70;
        font-weight: 500;
        line-height: 1.6;
    }

    /* ------------------------------------------------------------------ */
    /* KPI CARDS                                                           */
    /* ------------------------------------------------------------------ */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8E5;
        border-radius: 14px;
        padding: 1.2rem 1.35rem;
        box-shadow: 0 2px 8px -2px rgba(0,0,0,0.05);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #167D70, #6BAE91);
        border-radius: 14px 14px 0 0;
    }
    .kpi-card-warn::before {
        background: linear-gradient(90deg, #D99A32, #F5C26B);
    }
    .kpi-card-info::before {
        background: linear-gradient(90deg, #2563EB, #60A5FA);
    }
    .kpi-card-danger::before {
        background: linear-gradient(90deg, #D85A5A, #F87171);
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #18332F;
        line-height: 1.1;
        letter-spacing: -0.025em;
    }
    .kpi-subvalue {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 0.2rem;
    }
    .kpi-delta {
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 0.5rem;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        padding: 0.15rem 0.55rem;
        border-radius: 6px;
    }
    .delta-positive { color: #15803D; background: #F0FDF4; }
    .delta-negative { color: #DC2626; background: #FEF2F2; }
    .delta-neutral  { color: #475569; background: #F1F5F9; }
    .delta-warning  { color: #B45309; background: #FFFBEB; }

    /* ------------------------------------------------------------------ */
    /* SECTION HEADINGS                                                    */
    /* ------------------------------------------------------------------ */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-top: 1.75rem;
        margin-bottom: 0.4rem;
    }
    .section-icon {
        font-size: 1.25rem;
        line-height: 1;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #18332F;
        margin: 0;
        letter-spacing: -0.015em;
    }
    .section-desc {
        font-size: 0.9rem;
        color: #64748B;
        margin-bottom: 1rem;
        line-height: 1.55;
        margin-top: 0.1rem;
    }
    .section-divider {
        border: none;
        border-top: 1px solid #E2E8E5;
        margin: 0.5rem 0 1.25rem 0;
    }

    /* ------------------------------------------------------------------ */
    /* CALLOUT BOXES                                                       */
    /* ------------------------------------------------------------------ */
    .callout-box {
        background: #F8FAF9;
        border-left: 3px solid #167D70;
        padding: 0.9rem 1.1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #334155;
        line-height: 1.6;
    }
    .callout-warning {
        border-left-color: #D99A32;
        background: #FFFDF0;
    }
    .callout-info {
        border-left-color: #2563EB;
        background: #F0F4FF;
    }
    .callout-danger {
        border-left-color: #D85A5A;
        background: #FFF5F5;
    }

    /* ------------------------------------------------------------------ */
    /* CONTENT CARDS / PANELS                                             */
    /* ------------------------------------------------------------------ */
    .content-card {
        background: #FFFFFF;
        border: 1px solid #E2E8E5;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 2px 8px -2px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .info-panel {
        background: #EEF7F5;
        border: 1px solid #C5E0DB;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        font-size: 0.88rem;
        color: #18332F;
        line-height: 1.65;
    }

    /* ------------------------------------------------------------------ */
    /* FOOTER                                                              */
    /* ------------------------------------------------------------------ */
    .app-footer {
        text-align: center;
        font-size: 0.82rem;
        color: #94A3B8;
        padding: 2rem 0 0.75rem 0;
        border-top: 1px solid #E2E8E5;
        margin-top: 3rem;
    }

    /* ------------------------------------------------------------------ */
    /* STREAMLIT OVERRIDES                                                 */
    /* ------------------------------------------------------------------ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: #F7F9F8;
        border-radius: 10px;
        padding: 0.3rem;
        border: 1px solid #E2E8E5;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        padding: 0.4rem 0.9rem;
        font-size: 0.88rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #167D70 !important;
        color: white !important;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8E5;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #18332F !important;
    }
    .stSelectbox label, .stMultiselect label, .stSlider label {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stExpander {
        border: 1px solid #E2E8E5 !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
    }
    .stAlert {
        border-radius: 10px !important;
    }

    /* ===== GEOSPATIAL COMMAND CENTER — DARK THEME ===== */
    :root { color-scheme: dark; }
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .main, .block-container {
        background: #071722 !important; color: #d9e8ee !important;
    }
    .block-container {max-width: 1700px; padding: 1.15rem 1.7rem 3rem;}
    [data-testid="stHeader"] {background: rgba(7,23,34,.94)!important;}
    [data-testid="stToolbar"] {color:#c4dce4!important;}
    section[data-testid="stSidebar"] {background: #06121e!important; border-right: 1px solid #193441!important;}
    section[data-testid="stSidebar"] .stRadio [role="radiogroup"] {gap:.35rem;}
    section[data-testid="stSidebar"] .stRadio label {border-radius:8px!important; padding:.5rem .65rem!important;}
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {background:#104a3d!important;}
    .sidebar-logo-text {color:#e8f9f7!important;}
    .sidebar-subtitle {color:#71b9a5!important;}
    .sidebar-info-box {background:#0e2530!important; border-color:#244552!important;}
    .page-header,.control-bar,.kpi-card,.content-card,.info-panel,
    div[data-testid="stMetric"], [data-testid="stExpander"],
    .stExpander {background:#102735!important; border:1px solid #213e4c!important;
      box-shadow:0 5px 20px rgba(0,0,0,.12)!important; border-radius:10px!important;}
    .page-header-title,.section-title,.kpi-value,
    div[data-testid="stMetricValue"] > div {color:#edf8fa!important;}
    .page-header-desc,.section-desc,.kpi-label,.kpi-subvalue,
    div[data-testid="stMetricLabel"] > div {color:#9db8c4!important;}
    .section-header {margin-top:1.2rem;}
    .section-divider {border-color:#244553!important;}
    .data-badge {background:#10382f!important; border-color:#215e50!important; color:#9ce6c7!important;}
    .kpi-card::before {background:linear-gradient(90deg,#10b981,#38bdf8)!important;}
    .kpi-card-warn::before {background:#e8ad48!important;}
    .kpi-card-danger::before {background:#f36d73!important;}
    .delta-positive {background:#123b34!important; color:#6ee7b7!important;}
    .delta-negative {background:#452832!important; color:#fda4af!important;}
    .delta-neutral {background:#233847!important; color:#b6d1dc!important;}
    .delta-warning {background:#493b24!important; color:#fcd34d!important;}
    .callout-box {background:#102b35!important; color:#d0e3e9!important;}
    .callout-warning {background:#3b3020!important;}
    .callout-info {background:#172d49!important;}
    .callout-danger {background:#402732!important;}
    .stTabs [data-baseweb="tab-list"] {background:#102735!important; border-color:#244553!important;}
    .stTabs [data-baseweb="tab"] {color:#b6d0da!important;}
    .stTabs [aria-selected="true"] {background:#14594b!important; color:#f3fffa!important;}
    .stSelectbox label,.stMultiselect label,.stSlider label {color:#b3ced9!important;}
    [data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"], p, h1, h2, h3, h4 {color:#dbeaf0;}
    [data-baseweb="select"] > div, [data-baseweb="input"] > div,
    [data-testid="stNumberInput"] input {background:#122b39!important; color:#ecf6f9!important;
      border-color:#2b5260!important;}
    [data-testid="stDataFrame"] {border:1px solid #254653; border-radius:10px;}
    .app-footer {border-top-color:#244553!important; color:#7c9da9!important;}
    .stButton button, .stDownloadButton button {background:#125d4d!important;
      color:#f0fff9!important; border:1px solid #267b66!important; border-radius:8px!important;}
    .stButton button:hover, .stDownloadButton button:hover {background:#16816a!important;}
    /* Existing inline light headings from Task 2: override at CSS level. */
    [data-testid="stMarkdownContainer"] h1[style],
    [data-testid="stMarkdownContainer"] h2[style],
    [data-testid="stMarkdownContainer"] h3[style] {color:#edf8fa!important;}
    [data-testid="stMarkdownContainer"] p[style] {color:#a6bfcb!important;}
    @media(max-width:800px) {.block-container{padding:1rem .8rem 2rem;}}
    </style>
    """


def render_page_header(icon: str, title: str, description: str) -> str:
    """Return HTML for a consistent premium page header."""
    return f"""
    <div class="page-header">
        <span class="page-header-icon">{icon}</span>
        <div>
            <div class="page-header-title">{title}</div>
            <div class="page-header-desc">{description}</div>
        </div>
    </div>
    """


def render_section_header(icon: str, title: str, description: str = "") -> str:
    """Return HTML for a consistent section heading with optional description."""
    desc_html = f'<div class="section-desc">{description}</div>' if description else ""
    return f"""
    <div class="section-header">
        <span class="section-icon">{icon}</span>
        <div class="section-title">{title}</div>
    </div>
    {desc_html}
    """


def render_kpi_card(
    label: str,
    value: str,
    subvalue: str = "",
    delta: str = "",
    delta_type: str = "neutral",
    card_type: str = "",
) -> str:
    """Return HTML for a styled KPI card."""
    card_class = f"kpi-card {f'kpi-card-{card_type}' if card_type else ''}"
    delta_html = (
        f'<div class="kpi-delta delta-{delta_type}">{delta}</div>' if delta else ""
    )
    sub_html = f'<div class="kpi-subvalue">{subvalue}</div>' if subvalue else ""
    return f"""
    <div class="{card_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
        {delta_html}
    </div>
    """
