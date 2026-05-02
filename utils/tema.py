import plotly.io as pio


CORES = {
    "navy": "#0A2647",
    "emerald": "#00ED64",
    "titanium": "#E1E8ED",
    "midnight": "#101820",
    "white": "#F8FAFC",
    "white_pure": "#FFFFFF",
    "text_dark": "#101820",
    "muted": "#64748B",
    "border": "#D6DEE6",
    "danger": "#DC2626",
    "warning": "#F59E0B",
}

PALETA = [
    "#0A2647",
    "#00ED64",
    "#1D4ED8",
    "#14B8A6",
    "#64748B",
    "#DC2626",
]


def aplicar_tema_streamlit(st):
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Montserrat:wght@700;800&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #F8FAFC 0%, #E1E8ED 100%) !important;
            color: #101820 !important;
            font-family: 'Inter', sans-serif !important;
        }

        * {
            font-family: 'Inter', sans-serif !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Montserrat', sans-serif !important;
            color: #101820 !important;
            font-weight: 800 !important;
        }

        p, li, label, span, div {
            color: #101820;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #101820 0%, #0A2647 100%) !important;
        }

        [data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }

        [data-testid="stSidebar"] button {
            background: #00ED64 !important;
            color: #101820 !important;
            border-radius: 12px !important;
            border: 1px solid #00ED64 !important;
            font-weight: 800 !important;
        }

        .hz-hero,
        .mb-header {
            background: linear-gradient(135deg, #101820 0%, #0A2647 72%, #064E3B 100%) !important;
            padding: 36px;
            border-radius: 22px;
            margin-bottom: 28px;
            box-shadow: 0px 20px 50px rgba(10, 38, 71, 0.25);
            border: 1px solid rgba(255,255,255,0.12);
        }

        .hz-hero h1,
        .mb-header h1 {
            color: #F8FAFC !important;
            font-size: clamp(2rem, 4vw, 4rem);
            margin-bottom: 8px;
        }

        .hz-hero p,
        .mb-header p {
            color: #E1E8ED !important;
            font-size: 1.08rem;
            line-height: 1.65;
        }

        .hz-kicker {
            display: inline-block;
            color: #00ED64 !important;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 10px;
            font-size: 0.78rem;
        }

        .hz-card,
        .mb-card {
            background: #FFFFFF !important;
            border: 1px solid #D6DEE6 !important;
            border-left: 6px solid #00ED64 !important;
            border-radius: 18px !important;
            padding: 22px !important;
            box-shadow: 0px 12px 35px rgba(10, 38, 71, 0.14) !important;
            margin-bottom: 18px !important;
        }

        .hz-card h3,
        .hz-card h4,
        .mb-card h3,
        .mb-card h4 {
            color: #0A2647 !important;
        }

        .hz-card p,
        .mb-card p {
            color: #101820 !important;
        }

        div[data-testid="stMetric"] {
            background: #FFFFFF !important;
            border: 1px solid #D6DEE6 !important;
            border-left: 6px solid #00ED64 !important;
            border-radius: 18px !important;
            padding: 18px !important;
            box-shadow: 0px 10px 30px rgba(10, 38, 71, 0.14) !important;
        }

        div[data-testid="stMetric"] * {
            color: #101820 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #0A2647 !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-weight: 700 !important;
        }

        button,
        .stButton button,
        .stDownloadButton button {
            background: #00ED64 !important;
            color: #101820 !important;
            border: 1px solid #00ED64 !important;
            border-radius: 14px !important;
            font-weight: 800 !important;
        }

        button:hover,
        .stButton button:hover,
        .stDownloadButton button:hover {
            filter: brightness(1.05);
            transform: translateY(-1px);
        }

        input,
        textarea,
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {
            background: #FFFFFF !important;
            color: #101820 !important;
            border-color: #D6DEE6 !important;
            border-radius: 12px !important;
        }

        [data-testid="stDataFrame"] {
            background: #FFFFFF !important;
            border-radius: 16px !important;
            border: 1px solid #D6DEE6 !important;
            overflow: hidden !important;
        }

        [data-testid="stAlert"] {
            border-radius: 16px !important;
        }

        @media (prefers-color-scheme: dark) {
            html, body, [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #101820 0%, #071827 100%) !important;
                color: #F8FAFC !important;
            }

            h1, h2, h3, h4, h5, h6 {
                color: #F8FAFC !important;
            }

            p, li, label, span, div {
                color: #F8FAFC;
            }

            .hz-card,
            .mb-card,
            div[data-testid="stMetric"] {
                background: rgba(16, 24, 32, 0.94) !important;
                border-color: rgba(225,232,237,0.18) !important;
                border-left-color: #00ED64 !important;
            }

            .hz-card p,
            .mb-card p {
                color: #E1E8ED !important;
            }

            div[data-testid="stMetricValue"] {
                color: #00ED64 !important;
            }

            div[data-testid="stMetricLabel"] {
                color: #E1E8ED !important;
            }

            input,
            textarea,
            [data-baseweb="select"] > div,
            [data-baseweb="input"] > div {
                background: #F8FAFC !important;
                color: #101820 !important;
            }

            [data-testid="stDataFrame"] {
                background: #FFFFFF !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def aplicar_tema_plotly():
    template = pio.templates["plotly_white"]

    template.layout.paper_bgcolor = "#FFFFFF"
    template.layout.plot_bgcolor = "#FFFFFF"
    template.layout.font = dict(
        color="#101820",
        size=14,
        family="Inter, Arial"
    )
    template.layout.title = dict(
        font=dict(
            color="#0A2647",
            size=20,
            family="Montserrat, Arial"
        )
    )
    template.layout.colorway = PALETA
    template.layout.xaxis = dict(
        tickfont=dict(color="#101820"),
        title=dict(font=dict(color="#101820")),
        gridcolor="#E6EEF5",
        zerolinecolor="#D6DEE6",
    )
    template.layout.yaxis = dict(
        tickfont=dict(color="#101820"),
        title=dict(font=dict(color="#101820")),
        gridcolor="#E6EEF5",
        zerolinecolor="#D6DEE6",
    )
    template.layout.legend = dict(
        font=dict(color="#101820"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#D6DEE6",
        borderwidth=1
    )

    pio.templates["horizonte_tema"] = template
    pio.templates.default = "horizonte_tema"
