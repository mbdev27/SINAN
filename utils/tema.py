import streamlit as st
import plotly.io as pio


CORES = {
    # ========================================================
    # BASE
    # ========================================================
    "preto": "#101820",
    "black": "#101820",
    "preto_suave": "#1B1F23",
    "dark": "#101820",
    "dark_soft": "#1B1F23",

    "branco": "#FFFFFF",
    "white": "#FFFFFF",
    "gelo": "#F7FAF8",
    "offwhite": "#F7FAF8",

    "cinza": "#E5E7EB",
    "cinza_claro": "#F3F4F6",
    "cinza_texto": "#4B5563",
    "gray": "#4B5563",
    "gray_light": "#E5E7EB",
    "muted": "#4B5563",

    # ========================================================
    # VERDES HORIZONTE
    # ========================================================
    "verde": "#009B5A",
    "verde_claro": "#00C46A",
    "verde_escuro": "#006B3F",

    "green": "#009B5A",
    "green_light": "#00C46A",
    "green_dark": "#006B3F",

    "emerald": "#009B5A",
    "emerald_light": "#00C46A",
    "emerald_dark": "#006B3F",

    # ========================================================
    # AZUIS / NAVY
    # ========================================================
    "azul": "#0A2647",
    "azul_escuro": "#041C32",
    "azul_claro": "#2563EB",

    "blue": "#0A2647",
    "blue_dark": "#041C32",
    "blue_light": "#2563EB",

    "navy": "#0A2647",
    "navy_dark": "#041C32",
    "navy_light": "#1D4ED8",

    # ========================================================
    # ALERTAS E APOIO
    # ========================================================
    "vermelho": "#DC2626",
    "red": "#DC2626",
    "danger": "#DC2626",

    "amarelo": "#F59E0B",
    "yellow": "#F59E0B",
    "warning": "#F59E0B",

    "laranja": "#EA580C",
    "orange": "#EA580C",

    "roxo": "#7C3AED",
    "purple": "#7C3AED",

    "rosa": "#DB2777",
    "pink": "#DB2777",

    "ciano": "#0891B2",
    "cyan": "#0891B2",

    # ========================================================
    # NOMES LEGADOS USADOS EM MÓDULOS ANTIGOS
    # ========================================================
    "primary": "#009B5A",
    "secondary": "#101820",
    "accent": "#00C46A",
    "background": "#F7FAF8",
    "card": "#FFFFFF",
    "text": "#101820",
    "text_muted": "#4B5563",
    "border": "#DDE5E0",
}


PALETA = [
    CORES["emerald"],
    CORES["navy"],
    CORES["emerald_light"],
    CORES["emerald_dark"],
    CORES["blue_light"],
    CORES["warning"],
    CORES["danger"],
    CORES["purple"],
    CORES["orange"],
    CORES["cyan"],
    CORES["pink"],
    CORES["cinza_texto"],
]


def cor(nome, padrao="#009B5A"):
    return CORES.get(nome, padrao)


def aplicar_tema_streamlit(st_module=None):
    if st_module is None:
        st_module = st

    st_module.markdown(
        """
        <style>
        :root {
            --hz-black: #101820;
            --hz-white: #FFFFFF;
            --hz-bg: #F7FAF8;
            --hz-card: #FFFFFF;
            --hz-border: #DDE5E0;
            --hz-muted: #4B5563;
            --hz-green: #009B5A;
            --hz-green-light: #00C46A;
            --hz-green-dark: #006B3F;
            --hz-blue: #0A2647;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background: var(--hz-bg) !important;
            color: var(--hz-black) !important;
        }

        .block-container {
            padding-top: 2.2rem !important;
            padding-bottom: 4rem !important;
            max-width: 1320px !important;
        }

        [data-testid="stSidebar"] {
            background: #101820 !important;
            border-right: 1px solid rgba(255,255,255,0.08) !important;
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        [data-testid="stSidebar"] button {
            background: #009B5A !important;
            color: #FFFFFF !important;
            border-radius: 12px !important;
            border: 1px solid #009B5A !important;
            font-weight: 800 !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--hz-black) !important;
            font-weight: 900 !important;
            letter-spacing: -0.03em;
        }

        p, span, label, div {
            font-family: "Inter", "Segoe UI", sans-serif;
        }

        .stMarkdown, .stText, p {
            color: var(--hz-black) !important;
        }

        [data-testid="stMetric"] {
            background: var(--hz-card) !important;
            border: 1px solid var(--hz-border) !important;
            border-left: 6px solid var(--hz-green) !important;
            border-radius: 18px !important;
            padding: 1rem !important;
            box-shadow: 0 14px 35px rgba(16,24,32,0.07) !important;
        }

        [data-testid="stMetric"] label {
            color: var(--hz-muted) !important;
            font-weight: 700 !important;
        }

        [data-testid="stMetricValue"] {
            color: var(--hz-black) !important;
            font-weight: 900 !important;
        }

        [data-testid="stDataFrame"] {
            border-radius: 16px !important;
            overflow: hidden !important;
            border: 1px solid var(--hz-border) !important;
            background: #FFFFFF !important;
        }

        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"],
        button[kind="secondary"] {
            background: linear-gradient(135deg, #009B5A, #00C46A) !important;
            color: #FFFFFF !important;
            border: 1px solid #009B5A !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
            min-height: 45px !important;
            box-shadow: 0 12px 28px rgba(0,155,90,0.22) !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            filter: brightness(1.05);
            transform: translateY(-1px);
        }

        input, textarea, select {
            background: #FFFFFF !important;
            color: #101820 !important;
            border: 1px solid #CBD5D1 !important;
            border-radius: 12px !important;
        }

        input:focus, textarea:focus {
            border-color: #009B5A !important;
            box-shadow: 0 0 0 2px rgba(0,155,90,0.14) !important;
        }

        [data-testid="stAlert"] {
            border-radius: 16px !important;
            border: 1px solid rgba(0,155,90,0.16) !important;
        }

        div[data-baseweb="tab-list"] {
            gap: .5rem;
        }

        button[data-baseweb="tab"] {
            background: #FFFFFF !important;
            color: #101820 !important;
            border: 1px solid #DDE5E0 !important;
            border-radius: 14px !important;
            padding: .6rem 1rem !important;
            font-weight: 800 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: #101820 !important;
            color: #FFFFFF !important;
            border-color: #101820 !important;
        }

        hr {
            border-color: #DDE5E0 !important;
        }

        .hz-card {
            background: #FFFFFF;
            border: 1px solid #DDE5E0;
            border-radius: 22px;
            padding: 1.3rem;
            box-shadow: 0 14px 35px rgba(16,24,32,0.07);
        }

        .hz-kicker {
            color: #009B5A !important;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-size: .82rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def aplicar_tema_plotly():
    template_light = {
        "layout": {
            "paper_bgcolor": "#FFFFFF",
            "plot_bgcolor": "#FFFFFF",
            "font": {
                "color": "#101820",
                "family": "Inter, Segoe UI, sans-serif"
            },
            "colorway": PALETA,
            "xaxis": {
                "gridcolor": "#E5E7EB",
                "linecolor": "#CBD5D1",
                "zerolinecolor": "#E5E7EB",
            },
            "yaxis": {
                "gridcolor": "#E5E7EB",
                "linecolor": "#CBD5D1",
                "zerolinecolor": "#E5E7EB",
            },
            "legend": {
                "font": {
                    "color": "#101820"
                }
            },
            "margin": {
                "l": 40,
                "r": 30,
                "t": 50,
                "b": 40,
            },
        }
    }

    template_dark_compat = {
        "layout": {
            "paper_bgcolor": "#FFFFFF",
            "plot_bgcolor": "#FFFFFF",
            "font": {
                "color": "#101820",
                "family": "Inter, Segoe UI, sans-serif"
            },
            "colorway": PALETA,
            "xaxis": {
                "gridcolor": "#E5E7EB",
                "linecolor": "#CBD5D1",
                "zerolinecolor": "#E5E7EB",
            },
            "yaxis": {
                "gridcolor": "#E5E7EB",
                "linecolor": "#CBD5D1",
                "zerolinecolor": "#E5E7EB",
            },
            "legend": {
                "font": {
                    "color": "#101820"
                }
            },
            "margin": {
                "l": 40,
                "r": 30,
                "t": 50,
                "b": 40,
            },
        }
    }

    pio.templates["horizonte"] = template_light
    pio.templates["horizonte_light"] = template_light
    pio.templates["horizonte_dark"] = template_dark_compat

    pio.templates.default = "horizonte"
