import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.leitor_dbf import ler_dbf, resumo_dbf
from mappings.acidente_trabalho_grave import (
    CAMPOS_PRINCIPAIS,
    aplicar_mapeamento,
    gerar_tabela_publica
)

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Leitor DBF SINAN",
    page_icon="🗂️",
    layout="wide"
)

st.title("🗂️ Leitor DBF SINAN")
st.markdown("""
Esta página lê bancos `.DBF` do SINAN, aplica uma primeira camada de tradução
e prepara os dados para análise em painel.
""")

# ============================================================
# UPLOAD
# ============================================================

arquivo = st.file_uploader(
    "Envie o arquivo DBF do SINAN",
    type=["dbf"]
)

agravo = st.selectbox(
    "Selecione a ficha correspondente",
    ["Acidente de Trabalho Grave"]
)

if not arquivo:
    st.info("Envie um arquivo `.DBF` para iniciar a leitura.")
    st.stop()

# ============================================================
# LEITURA DO DBF
# ============================================================

with tempfile.NamedTemporaryFile(delete=False, suffix=".DBF") as tmp:
    tmp.write(arquivo.read())
    caminho_tmp = tmp.name

try:
    df = ler_dbf(caminho_tmp)
except Exception as e:
    st.error(f"Erro ao ler o arquivo DBF: {e}")
    st.stop()

if df.empty:
    st.warning("O DBF foi lido, mas não possui registros.")
    st.stop()

df = aplicar_mapeamento(df)
df_publico = gerar_tabela_publica(df)

# ============================================================
# INDICADORES
# ============================================================

st.header("📊 Resumo do Banco")

col1, col2, col3 = st.columns(3)

col1.metric("Registros", len(df))
col2.metric("Colunas", len(df.columns))

if "NU_NOTIFIC" in df.columns:
    col3.metric("Notificações únicas", df["NU_NOTIFIC"].nunique())
else:
    col3.metric("Notificações únicas", "—")

# ============================================================
# BUSCAS
# ============================================================

st.header("🔎 Busca e Consulta")

busca_notificacao = st.text_input("Buscar por número da notificação")

df_busca = df_publico.copy()

if busca_notificacao and "NU_NOTIFIC" in df_busca.columns:
    df_busca = df_busca[
        df_busca["NU_NOTIFIC"].astype(str).str.contains(busca_notificacao, case=False, na=False)
    ]

termo = st.text_input("Buscar qualquer termo no banco")

if termo:
    mask = df_busca.astype(str).apply(
        lambda col: col.str.contains(termo, case=False, na=False)
    ).any(axis=1)
    df_busca = df_busca[mask]

# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("🔎 Filtros")

df_filtrado = df_busca.copy()

if "DT_NOTIFIC" in df_filtrado.columns:
    df_filtrado["DT_NOTIFIC"] = pd.to_datetime(df_filtrado["DT_NOTIFIC"], errors="coerce")
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

def filtro_multiselect(label, coluna):
    global df_filtrado

    if coluna in df_filtrado.columns:
        opcoes = sorted(df_filtrado[coluna].dropna().astype(str).unique())
        selecionados = st.sidebar.multiselect(label, opcoes)

        if selecionados:
            df_filtrado = df_filtrado[df_filtrado[coluna].astype(str).isin(selecionados)]

filtro_multiselect("Sexo", "CS_SEXO_DESC")
filtro_multiselect("Raça/Cor", "CS_RACA_DESC")
filtro_multiselect("Gestante", "CS_GESTANT_DESC")
filtro_multiselect("Situação no Mercado de Trabalho", "SIT_TRAB_DESC")
filtro_multiselect("Local do Acidente", "LOCAL_ACID_DESC")
filtro_multiselect("Tipo de Acidente", "TIPO_ACID_DESC")
filtro_multiselect("Evolução", "EVOLUCAO_DESC")
filtro_multiselect("CAT", "CAT_DESC")

if df_filtrado.empty:
    st.warning("Nenhum registro encontrado com os filtros aplicados.")
    st.stop()

# ============================================================
# GRÁFICOS
# ============================================================

st.header("📈 Painel Inicial")

colA, colB = st.columns(2)

if "CS_SEXO_DESC" in df_filtrado.columns:
    sexo = df_filtrado["CS_SEXO_DESC"].value_counts().reset_index()
    sexo.columns = ["Sexo", "Quantidade"]

    fig = px.pie(
        sexo,
        names="Sexo",
        values="Quantidade",
        title="Distribuição por Sexo"
    )
    colA.plotly_chart(fig, use_container_width=True)

if "EVOLUCAO_DESC" in df_filtrado.columns:
    evolucao = df_filtrado["EVOLUCAO_DESC"].value_counts().reset_index()
    evolucao.columns = ["Evolução", "Quantidade"]

    fig = px.bar(
        evolucao,
        x="Evolução",
        y="Quantidade",
        title="Evolução do Caso"
    )
    colB.plotly_chart(fig, use_container_width=True)

colC, colD = st.columns(2)

if "SIT_TRAB_DESC" in df_filtrado.columns:
    sit = df_filtrado["SIT_TRAB_DESC"].value_counts().reset_index()
    sit.columns = ["Situação", "Quantidade"]

    fig = px.bar(
        sit,
        x="Situação",
        y="Quantidade",
        title="Situação no Mercado de Trabalho"
    )
    colC.plotly_chart(fig, use_container_width=True)

if "LOCAL_ACID_DESC" in df_filtrado.columns:
    local = df_filtrado["LOCAL_ACID_DESC"].value_counts().reset_index()
    local.columns = ["Local", "Quantidade"]

    fig = px.bar(
        local,
        x="Local",
        y="Quantidade",
        title="Local do Acidente"
    )
    colD.plotly_chart(fig, use_container_width=True)

# ============================================================
# TABELA
# ============================================================

st.header("📋 Dados Decodificados")

st.dataframe(df_filtrado, use_container_width=True)

# ============================================================
# RESUMO E DOWNLOAD
# ============================================================

with st.expander("📚 Estrutura do DBF"):
    st.dataframe(resumo_dbf(df), use_container_width=True)

st.download_button(
    "📥 Baixar dados decodificados CSV",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="sinan_acidente_trabalho_decodificado.csv",
    mime="text/csv"
)
