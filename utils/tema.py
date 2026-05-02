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

    # Compatibilidade com códigos antigos
    "azul": "#0A2647",
    "verde": "#00ED64",
    "amarelo": "#F59E0B",
    "laranja": "#F97316",
    "fundo": "#101820",
    "branco": "#F8FAFC",
    "preto": "#101820",
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
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Montserrat:wght@700;800&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #071827 0%, #0A2647 62%, #064E3B 100%) !important;
            color: #F8FAFC !important;
        }

        body, p, li, label, input, textarea, button {
            font-family: 'Inter', sans-serif !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em;
        }

        /* NÃO aplicar fonte global em ícones internos */
        span[class*="material"],
        i[class*="material"],
        [class*="Material"],
        [data-testid="stIconMaterial"] {
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        }

        /* Oculta qualquer fallback textual de ícone que vaze */
        span[title*="keyboard_double"],
        button[title*="keyboard_double"],
        [aria-label*="keyboard_double"],
        [title="Keyboard_double_arrow_right"],
        [title="Keyboard_double_arrow_left"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08131F 0%, #0A2647 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        [data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 12px !important;
            margin-bottom: 4px !important;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: rgba(255,255,255,0.10) !important;
        }

        .hz-hero,
        .mb-header {
            background: linear-gradient(135deg, rgba(7,24,39,0.98), rgba(10,38,71,0.98), rgba(6,78,59,0.94));
            border: 1px solid rgba(255,255,255,0.10);
            padding: 42px;
            border-radius: 24px;
            margin-bottom: 32px;
            box-shadow: 0px 24px 60px rgba(0,0,0,0.35);
        }

        .hz-kicker {
            color: #00ED64 !important;
            font-weight: 800;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            display: inline-block;
            margin-bottom: 10px;
        }

        .hz-hero h1,
        .mb-header h1 {
            color: #FFFFFF !important;
            font-size: clamp(2.1rem, 4vw, 4.4rem);
            line-height: 1.08;
            margin-top: 10px;
            margin-bottom: 18px;
        }

        .hz-hero p,
        .mb-header p {
            color: #E1E8ED !important;
            font-size: 1.08rem;
            line-height: 1.7;
            max-width: 1000px;
        }

        .hz-card,
        .mb-card {
            background: rgba(8,19,31,0.76);
            border: 1px solid rgba(255,255,255,0.10);
            border-left: 6px solid #00ED64;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0px 18px 40px rgba(0,0,0,0.24);
            backdrop-filter: blur(12px);
            margin-bottom: 18px;
            height: 100%;
        }

        .hz-card h3,
        .hz-card h4,
        .mb-card h3,
        .mb-card h4 {
            color: #FFFFFF !important;
        }

        .hz-card p,
        .mb-card p {
            color: #E1E8ED !important;
            line-height: 1.65;
        }

        div[data-testid="stMetric"] {
            background: rgba(8,19,31,0.76) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-left: 6px solid #00ED64 !important;
            border-radius: 20px !important;
            padding: 18px !important;
            min-height: 128px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            box-shadow: 0px 18px 40px rgba(0,0,0,0.24) !important;
            overflow: hidden !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #E1E8ED !important;
            font-weight: 700 !important;
            font-size: clamp(0.72rem, 1vw, 0.95rem) !important;
            overflow-wrap: anywhere !important;
        }

        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
            font-size: clamp(1.35rem, 2vw, 2.5rem) !important;
            overflow-wrap: anywhere !important;
        }

        input,
        textarea,
        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div {
            background: rgba(255,255,255,0.98) !important;
            color: #101820 !important;
            border: 1px solid rgba(255,255,255,0.20) !important;
            border-radius: 14px !important;
        }

        input,
        textarea {
            color: #101820 !important;
        }

        label {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }

        [data-testid="stFileUploader"] {
            background: rgba(255,255,255,0.08) !important;
            border: 2px dashed rgba(255,255,255,0.18) !important;
            border-radius: 18px !important;
            padding: 18px !important;
        }

        [data-testid="stFileUploader"] * {
            color: #F8FAFC !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: transparent !important;
        }

        [data-testid="stFileUploaderDropzone"] button {
            background: #00ED64 !important;
            color: #101820 !important;
        }

        button,
        .stButton button,
        .stDownloadButton button {
            background: #00ED64 !important;
            color: #101820 !important;
            border: 1px solid #00ED64 !important;
            border-radius: 14px !important;
            font-weight: 800 !important;
            min-height: 48px;
            transition: all 0.18s ease-in-out;
        }

        button:hover,
        .stButton button:hover,
        .stDownloadButton button:hover {
            filter: brightness(1.05);
            transform: translateY(-1px);
            box-shadow: 0px 12px 30px rgba(0,237,100,0.26);
        }

        [data-testid="stDataFrame"] {
            background: #FFFFFF !important;
            border-radius: 18px !important;
            overflow: hidden !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
        }

        [data-testid="stDataFrame"] * {
            color: #101820 !important;
        }

        [data-testid="stExpander"] {
            background: rgba(8,19,31,0.58) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
        }

        [data-testid="stExpander"] * {
            color: #F8FAFC !important;
        }

        [data-testid="stAlert"] {
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
        }

        [data-testid="stAlert"] * {
            color: inherit !important;
        }

        @media (max-width: 900px) {
            .hz-hero,
            .mb-header {
                padding: 28px;
                border-radius: 18px;
            }

            div[data-testid="stMetric"] {
                min-height: 108px !important;
                padding: 14px !important;
            }

            div[data-testid="stMetricValue"] {
                font-size: 1.55rem !important;
            }

            div[data-testid="stMetricLabel"] {
                font-size: 0.78rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def aplicar_tema_plotly():
    template = pio.templates["plotly_dark"]

    template.layout.paper_bgcolor = "rgba(0,0,0,0)"
    template.layout.plot_bgcolor = "rgba(0,0,0,0)"
    template.layout.font = dict(
        color="#F8FAFC",
        size=14,
        family="Inter"
    )
    template.layout.colorway = PALETA
    template.layout.title = dict(
        font=dict(
            color="#FFFFFF",
            size=22,
            family="Montserrat"
        )
    )
    template.layout.xaxis = dict(
        tickfont=dict(color="#E1E8ED"),
        title=dict(font=dict(color="#E1E8ED")),
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.12)",
    )
    template.layout.yaxis = dict(
        tickfont=dict(color="#E1E8ED"),
        title=dict(font=dict(color="#E1E8ED")),
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.12)",
    )
    template.layout.legend = dict(
        font=dict(color="#F8FAFC"),
        bgcolor="rgba(8,19,31,0.72)"
    )

    pio.templates["horizonte_dark"] = template
    pio.templates.default = "horizonte_dark"
