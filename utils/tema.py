import plotly.io as pio


CORES = {
    "azul": "#0057B7",
    "verde": "#1A944E",
    "amarelo": "#FFC20E",
    "laranja": "#FF8C00",
    "fundo": "#F6F9FC",
    "branco": "#FFFFFF",
    "preto": "#000000",
}

PALETA = [
    CORES["azul"],
    CORES["verde"],
    CORES["amarelo"],
    CORES["laranja"],
]


def aplicar_tema_streamlit(st):
    st.markdown(
        f"""
        <style>
        :root {{
            --azul: {CORES["azul"]};
            --verde: {CORES["verde"]};
            --amarelo: {CORES["amarelo"]};
            --laranja: {CORES["laranja"]};
            --fundo: {CORES["fundo"]};
            --branco: {CORES["branco"]};
            --preto: {CORES["preto"]};
        }}

        html, body, [data-testid="stAppViewContainer"], * {{
            color: #aed2f5 !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(to bottom right, #F6F9FC, #EAF3FF) !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--amarelo) !important;
            font-weight: 800 !important;
        }}

        p, li {{
            text-align: justify !important;
            color: #000000 !important;
        }}

        [data-testid="stSidebar"] {{
            background: var(--azul) !important;
        }}

        [data-testid="stSidebar"] * {{
            color: #FFFFFF !important;
        }}

        .stMetric {{
            background-color: var(--amarelo) !important;
            padding: 18px;
            border-radius: 10px;
            border-left: 6px solid var(--azul);
            box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
        }}

        button, .stButton button {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border-radius: 8px !important;
            border: 1px solid var(--azul) !important;
        }}

        .mb-card {{
            background: white;
            padding: 22px;
            border-radius: 14px;
            border-left: 7px solid var(--azul);
            box-shadow: 0px 2px 8px rgba(0,0,0,0.12);
            margin-bottom: 18px;
        }}

        .mb-header {{
            background: linear-gradient(135deg, var(--azul), var(--verde));
            padding: 34px;
            border-radius: 14px;
            margin-bottom: 25px;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.18);
        }}

        .mb-header h1 {{
            color: white !important;
            margin-bottom: 4px;
        }}

        .mb-header p {{
            color: white !important;
            font-size: 1.1rem;
            text-align: left !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def aplicar_tema_plotly():
    template = pio.templates["plotly_white"]

    template.layout.paper_bgcolor = "white"
    template.layout.plot_bgcolor = "white"
    template.layout.font = dict(color="#000000", size=14)
    template.layout.title = dict(
        font=dict(
            color=CORES["azul"],
            size=20,
            family="Arial"
        )
    )

    template.layout.legend = dict(
        font=dict(color="#000000")
    )

    template.layout.xaxis = dict(
        tickfont=dict(color="#000000"),
        title=dict(font=dict(color="#000000")),
        gridcolor="#E5E5E5",
        zerolinecolor="#E5E5E5",
    )

    template.layout.yaxis = dict(
        tickfont=dict(color="#000000"),
        title=dict(font=dict(color="#000000")),
        gridcolor="#E5E5E5",
        zerolinecolor="#E5E5E5",
    )

    pio.templates["mb_tema"] = template
    pio.templates.default = "mb_tema"
