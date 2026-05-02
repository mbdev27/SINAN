import plotly.io as pio


CORES = {
    "navy": "#0A2647",
    "emerald": "#00ED64",
    "titanium": "#E1E8ED",
    "midnight": "#101820",
    "white": "#F8FAFC",
    "white_pure": "#FFFFFF",
    "text_dark": "#101820",
    "text_light": "#F8FAFC",
    "muted": "#64748B",
    "border": "#D6DEE6",
    "danger": "#DC2626",
    "warning": "#F59E0B",
    "success": "#00ED64",
}

PALETA = [
    CORES["navy"],
    CORES["emerald"],
    "#1D4ED8",
    "#14B8A6",
    "#F59E0B",
    "#DC2626",
]


def aplicar_tema_streamlit(st):
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Montserrat:wght@700;800&display=swap');

        :root {{
            --hz-navy: {CORES["navy"]};
            --hz-emerald: {CORES["emerald"]};
            --hz-titanium: {CORES["titanium"]};
            --hz-midnight: {CORES["midnight"]};
            --hz-white: {CORES["white"]};
            --hz-white-pure: {CORES["white_pure"]};
            --hz-text-dark: {CORES["text_dark"]};
            --hz-text-light: {CORES["text_light"]};
            --hz-muted: {CORES["muted"]};
            --hz-border: {CORES["border"]};
            --hz-shadow: rgba(10, 38, 71, 0.16);
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Inter', sans-serif !important;
            background:
                radial-gradient(circle at top left, rgba(0, 237, 100, 0.10), transparent 30%),
                linear-gradient(135deg, #F8FAFC 0%, #EAF1F7 100%) !important;
            color: var(--hz-text-dark) !important;
        }}

        [data-testid="stAppViewContainer"] * {{
            font-family: 'Inter', sans-serif !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Montserrat', sans-serif !important;
            color: var(--hz-navy) !important;
            letter-spacing: -0.02em;
        }}

        p, li, span, div, label {{
            color: var(--hz-text-dark);
        }}

        a {{
            color: var(--hz-navy) !important;
            font-weight: 700;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--hz-midnight) 0%, var(--hz-navy) 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.08);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--hz-white) !important;
        }}

        [data-testid="stSidebar"] button {{
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: var(--hz-white) !important;
        }}

        [data-testid="stSidebar"] button:hover {{
            background: var(--hz-emerald) !important;
            color: var(--hz-midnight) !important;
            border-color: var(--hz-emerald) !important;
        }}

        .hz-hero,
        .mb-header {{
            background:
                linear-gradient(135deg, rgba(10,38,71,0.98), rgba(16,24,32,0.95)),
                radial-gradient(circle at top right, rgba(0,237,100,0.24), transparent 30%);
            padding: 34px;
            border-radius: 20px;
            margin-bottom: 28px;
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0px 20px 50px rgba(10,38,71,0.25);
        }}

        .hz-hero h1,
        .mb-header h1 {{
            color: var(--hz-white) !important;
            margin-bottom: 8px;
            font-size: clamp(2rem, 4vw, 4rem);
        }}

        .hz-hero p,
        .mb-header p {{
            color: var(--hz-titanium) !important;
            font-size: 1.08rem;
            max-width: 980px;
            line-height: 1.65;
            text-align: left !important;
        }}

        .hz-kicker {{
            display: inline-block;
            color: var(--hz-emerald) !important;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 10px;
            font-size: 0.78rem;
        }}

        .hz-card,
        .mb-card {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(14px);
            padding: 22px;
            border-radius: 18px;
            border: 1px solid var(--hz-border);
            border-left: 6px solid var(--hz-emerald);
            box-shadow: 0px 12px 35px var(--hz-shadow);
            margin-bottom: 18px;
            min-height: 145px;
        }}

        .hz-card h3,
        .hz-card h4,
        .mb-card h3,
        .mb-card h4 {{
            color: var(--hz-navy) !important;
            margin-bottom: 10px;
        }}

        .hz-card p,
        .mb-card p {{
            color: var(--hz-text-dark) !important;
            line-height: 1.6;
        }}

        .hz-panel {{
            background: rgba(255,255,255,0.86);
            border: 1px solid var(--hz-border);
            border-radius: 20px;
            padding: 26px;
            box-shadow: 0px 12px 35px var(--hz-shadow);
            margin-bottom: 22px;
        }}

        .hz-panel-dark {{
            background: linear-gradient(135deg, var(--hz-midnight), var(--hz-navy));
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 20px;
            padding: 26px;
            box-shadow: 0px 18px 45px rgba(16,24,32,0.35);
            margin-bottom: 22px;
        }}

        .hz-panel-dark h2,
        .hz-panel-dark h3,
        .hz-panel-dark p,
        .hz-panel-dark li {{
            color: var(--hz-white) !important;
        }}

        .hz-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(0,237,100,0.12);
            color: var(--hz-navy) !important;
            border: 1px solid rgba(0,237,100,0.36);
            padding: 8px 12px;
            border-radius: 999px;
            font-weight: 800;
            margin: 4px 6px 4px 0;
        }}

        .stMetric {{
            background: rgba(255,255,255,0.94) !important;
            border: 1px solid var(--hz-border);
            border-left: 6px solid var(--hz-emerald);
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0px 10px 30px var(--hz-shadow);
        }}

        [data-testid="stMetricValue"] {{
            color: var(--hz-navy) !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--hz-muted) !important;
            font-weight: 700 !important;
        }}

        button,
        .stButton button,
        .stDownloadButton button {{
            background: var(--hz-emerald) !important;
            color: var(--hz-midnight) !important;
            border: 1px solid var(--hz-emerald) !important;
            border-radius: 14px !important;
            font-weight: 800 !important;
            padding: 0.72rem 1rem !important;
            box-shadow: 0px 10px 28px rgba(0,237,100,0.25);
            transition: all 0.18s ease-in-out;
        }}

        button:hover,
        .stButton button:hover,
        .stDownloadButton button:hover {{
            filter: brightness(1.04);
            transform: translateY(-1px);
            box-shadow: 0px 14px 36px rgba(0,237,100,0.34);
        }}

        input,
        textarea,
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {{
            background: var(--hz-white-pure) !important;
            color: var(--hz-text-dark) !important;
            border-color: var(--hz-border) !important;
            border-radius: 12px !important;
        }}

        input::placeholder {{
            color: var(--hz-muted) !important;
        }}

        [data-testid="stDataFrame"] {{
            background: var(--hz-white-pure) !important;
            border-radius: 16px !important;
            border: 1px solid var(--hz-border) !important;
            overflow: hidden;
        }}

        [data-testid="stAlert"] {{
            border-radius: 16px !important;
            border: 1px solid rgba(10,38,71,0.15) !important;
        }}

        .js-plotly-plot,
        .plot-container {{
            border-radius: 18px !important;
        }}

        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--hz-border), transparent);
            margin: 28px 0;
        }}

        @media (prefers-color-scheme: dark) {{
            html, body, [data-testid="stAppViewContainer"] {{
                background:
                    radial-gradient(circle at top left, rgba(0,237,100,0.12), transparent 28%),
                    linear-gradient(135deg, #101820 0%, #071827 100%) !important;
                color: var(--hz-white) !important;
            }}

            p, li, span, div, label {{
                color: var(--hz-white);
            }}

            h1, h2, h3, h4, h5, h6 {{
                color: var(--hz-white) !important;
            }}

            .hz-card,
            .mb-card,
            .hz-panel,
            .stMetric {{
                background: rgba(16,24,32,0.86) !important;
                border-color: rgba(225,232,237,0.16) !important;
                box-shadow: 0px 14px 42px rgba(0,0,0,0.36);
            }}

            .hz-card h3,
            .hz-card h4,
            .mb-card h3,
            .mb-card h4 {{
                color: var(--hz-white) !important;
            }}

            .hz-card p,
            .mb-card p,
            .hz-panel p,
            .hz-panel li {{
                color: var(--hz-titanium) !important;
            }}

            [data-testid="stMetricValue"] {{
                color: var(--hz-emerald) !important;
            }}

            [data-testid="stMetricLabel"] {{
                color: var(--hz-titanium) !important;
            }}

            input,
            textarea,
            [data-baseweb="select"] > div,
            [data-baseweb="input"] > div {{
                background: rgba(248,250,252,0.96) !important;
                color: var(--hz-midnight) !important;
            }}

            [data-testid="stDataFrame"] {{
                background: var(--hz-white-pure) !important;
            }}
        }}

        @media (max-width: 768px) {{
            .hz-hero,
            .mb-header {{
                padding: 24px;
                border-radius: 16px;
            }}

            .hz-card,
            .mb-card {{
                min-height: auto;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def aplicar_tema_plotly():
    template = pio.templates["plotly_white"]

    template.layout.paper_bgcolor = "white"
    template.layout.plot_bgcolor = "white"
    template.layout.font = dict(
        color=CORES["text_dark"],
        size=14,
        family="Inter, Arial"
    )
    template.layout.title = dict(
        font=dict(
            color=CORES["navy"],
            size=20,
            family="Montserrat, Arial"
        )
    )
    template.layout.legend = dict(
        font=dict(color=CORES["text_dark"]),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor=CORES["border"],
        borderwidth=1
    )
    template.layout.xaxis = dict(
        tickfont=dict(color=CORES["text_dark"]),
        title=dict(font=dict(color=CORES["text_dark"])),
        gridcolor="#E6EEF5",
        zerolinecolor="#D6DEE6",
    )
    template.layout.yaxis = dict(
        tickfont=dict(color=CORES["text_dark"]),
        title=dict(font=dict(color=CORES["text_dark"])),
        gridcolor="#E6EEF5",
        zerolinecolor="#D6DEE6",
    )
    template.layout.margin = dict(l=40, r=30, t=70, b=45)

    pio.templates["horizonte_tema"] = template
    pio.templates.default = "horizonte_tema"
