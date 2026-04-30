import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

from utils.leitor_dbf import ler_dbf
from mappings.acidente_trabalho_grave import aplicar_mapeamento, gerar_tabela_publica

st.set_page_config(
    page_title="Painel Acidente de Trabalho Grave",
    page_icon="👷",
    layout="wide"
)

cores = {
    "azul": "#0057B7",
    "verde": "#1A944E",
    "amarelo": "#FFC20E",
    "laranja": "#FF8C00"
}

paleta = [cores["azul"], cores["verde"], cores["amarelo"], cores["laranja"]]

pio.templates["ipojuca_tema"] = pio.templates["plotly_white"]
pio.templates["ipojuca_tema"].layout.update(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#000000", size=14),
    title=dict(font=dict(color=cores["azul"], size=20, family="Arial")),
)
pio.templates.default = "ipojuca_tema"

st.title("👷 Painel Analítico — Acidente de Trabalho Grave")
st.markdown(
    "Análise interativa dos registros do SINAN a partir do banco DBF decodificado."
)

arquivo = st.file_uploader(
    "Envie o banco DBF de Acidente de Trabalho Grave",
    type=["dbf"]
)

if not arquivo:
    st.info("Envie um arquivo `.DBF` para iniciar o painel.")
    st.stop()

with tempfile.NamedTemporaryFile(delete=False, suffix=".DBF") as tmp:
    tmp.write(arquivo.read())
    caminho_tmp = tmp.name

try:
    df = ler_dbf(caminho_tmp)
except Exception as e:
    st.error(f"Erro ao ler o DBF: {e}")
    st.stop()

df = aplicar_mapeamento(df)
df_publico = gerar_tabela_publica(df)

if df_publico.empty:
    st.warning("Nenhum registro encontrado.")
    st.stop()

for col in ["DT_NOTIFIC", "DT_ACID", "DT_OBITO"]:
    if col in df_publico.columns:
        df_publico[col] = pd.to_datetime(df_publico[col], errors="coerce")

st.sidebar.header("🔎 Filtros")

df_filtrado = df_publico.copy()

if "DT_NOTIFIC" in df_filtrado.columns:
    min_d = df_filtrado["DT_NOTIFIC"].min()
    max_d = df_filtrado["DT_NOTIFIC"].max()

    if pd.notna(min_d) and pd.notna(max_d):
        data_ini, data_fim = st.sidebar.date_input(
            "Período da Notificação",
            value=[min_d.date(), max_d.date()],
            min_value=min_d.date(),
            max_value=max_d.date()
        )

        df_filtrado = df_filtrado[
            (df_filtrado["DT_NOTIFIC"].dt.date >= data_ini) &
            (df_filtrado["DT_NOTIFIC"].dt.date <= data_fim)
        ]

def filtro(label, coluna):
    global df_filtrado
    if coluna in df_filtrado.columns:
        opcoes = sorted(df_filtrado[coluna].dropna().astype(str).unique())
        selecionados = st.sidebar.multiselect(label, opcoes)

        if selecionados:
            df_filtrado = df_filtrado[
                df_filtrado[coluna].astype(str).isin(selecionados)
            ]

filtro("Sexo", "CS_SEXO_DESC")
filtro("Raça/Cor", "CS_RACA_DESC")
filtro("Gestante", "CS_GESTANT_DESC")
filtro("Situação no Mercado de Trabalho", "SIT_TRAB_DESC")
filtro("Local do Acidente", "LOCAL_ACID_DESC")
filtro("Tipo de Acidente", "TIPO_ACID_DESC")
filtro("Regime de Tratamento", "REGIME_DESC")
filtro("Evolução", "EVOLUCAO_DESC")
filtro("CAT", "CAT_DESC")

busca = st.text_input("🔍 Pesquisar qualquer termo no banco filtrado")

if busca:
    mask = df_filtrado.astype(str).apply(
        lambda col: col.str.contains(busca, case=False, na=False)
    ).any(axis=1)
    df_filtrado = df_filtrado[mask]

if df_filtrado.empty:
    st.warning("Nenhum registro encontrado com os filtros aplicados.")
    st.stop()

st.header("📊 Indicadores Principais")

total = len(df_filtrado)

obitos = 0
if "EVOLUCAO_DESC" in df_filtrado.columns:
    obitos = df_filtrado["EVOLUCAO_DESC"].astype(str).str.contains(
        "Óbito|Obito", case=False, na=False
    ).sum()

cat_emitida = 0
if "CAT_DESC" in df_filtrado.columns:
    cat_emitida = (
        df_filtrado["CAT_DESC"].astype(str).str.upper().str.strip() == "SIM"
    ).sum()

ocupacao_top = "—"
if "ID_OCUPA_N" in df_filtrado.columns and not df_filtrado["ID_OCUPA_N"].dropna().empty:
    ocupacao_top = df_filtrado["ID_OCUPA_N"].astype(str).value_counts().idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros", total)
c2.metric("Óbitos", int(obitos))
c3.metric("CAT emitida", int(cat_emitida))
c4.metric("Ocupação mais frequente", ocupacao_top)

st.header("📈 Visualizações")

col1, col2 = st.columns(2)

if "CS_SEXO_DESC" in df_filtrado.columns:
    sexo = df_filtrado["CS_SEXO_DESC"].value_counts().reset_index()
    sexo.columns = ["Sexo", "Quantidade"]
    fig = px.pie(
        sexo,
        names="Sexo",
        values="Quantidade",
        title="Distribuição por Sexo",
        color_discrete_sequence=paleta,
        hole=0.35
    )
    col1.plotly_chart(fig, use_container_width=True)

if "EVOLUCAO_DESC" in df_filtrado.columns:
    evolucao = df_filtrado["EVOLUCAO_DESC"].value_counts().reset_index()
    evolucao.columns = ["Evolução", "Quantidade"]
    fig = px.bar(
        evolucao,
        x="Evolução",
        y="Quantidade",
        title="Evolução do Caso",
        color_discrete_sequence=[cores["azul"]]
    )
    col2.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

if "SIT_TRAB_DESC" in df_filtrado.columns:
    sit = df_filtrado["SIT_TRAB_DESC"].value_counts().reset_index()
    sit.columns = ["Situação", "Quantidade"]
    fig = px.bar(
        sit,
        x="Situação",
        y="Quantidade",
        title="Situação no Mercado de Trabalho",
        color_discrete_sequence=[cores["verde"]]
    )
    col3.plotly_chart(fig, use_container_width=True)

if "LOCAL_ACID_DESC" in df_filtrado.columns:
    local = df_filtrado["LOCAL_ACID_DESC"].value_counts().reset_index()
    local.columns = ["Local", "Quantidade"]
    fig = px.bar(
        local,
        x="Local",
        y="Quantidade",
        title="Local onde ocorreu o acidente",
        color_discrete_sequence=[cores["laranja"]]
    )
    col4.plotly_chart(fig, use_container_width=True)

if "DT_NOTIFIC" in df_filtrado.columns:
    serie = (
        df_filtrado.dropna(subset=["DT_NOTIFIC"])
        .assign(MES=df_filtrado["DT_NOTIFIC"].dt.to_period("M").astype(str))
        .groupby("MES")
        .size()
        .reset_index(name="Quantidade")
    )

    if not serie.empty:
        fig = px.line(
            serie,
            x="MES",
            y="Quantidade",
            markers=True,
            title="Notificações por mês",
            color_discrete_sequence=[cores["azul"]]
        )
        st.plotly_chart(fig, use_container_width=True)

st.header("📋 Dados Decodificados")

st.dataframe(df_filtrado, use_container_width=True)

st.download_button(
    "📥 Baixar dados filtrados em CSV",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="acidente_trabalho_grave_decodificado.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("SINAN Decoder • Acidente de Trabalho Grave • Versão MVP")
