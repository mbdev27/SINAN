import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.leitor_dbf import ler_dbf, resumo_dbf
from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly, CORES, PALETA
from mappings.acidente_trabalho_grave import aplicar_mapeamento, gerar_tabela_publica
from config.agravos import AGRAVOS

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Leitor DBF SINAN",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_tema_streamlit(st)
aplicar_tema_plotly()

# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="mb-header">
        <h1>🗂️ Leitor DBF SINAN</h1>
        <p>
            Envie um banco de dados DBF do SINAN, selecione o agravo correspondente
            e visualize os registros decodificados de forma clara, filtrável e segura.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# CONFIGURAÇÕES
# ============================================================

LIMITE_MB = 100
LIMITE_BYTES = LIMITE_MB * 1024 * 1024

# ============================================================
# SELEÇÃO DO AGRAVO
# ============================================================

st.subheader("📌 Selecione o agravo")

agravo = st.selectbox(
    "Selecione o agravo correspondente ao banco DBF",
    list(AGRAVOS.keys())
)

st.info(
    f"Agravo selecionado: **{agravo}**. "
    "Após conferir a leitura do banco, acesse o painel analítico correspondente no menu lateral."
)

# ============================================================
# UPLOAD
# ============================================================

st.subheader("📤 Envio do arquivo DBF")

arquivo = st.file_uploader(
    "Envie o arquivo DBF do SINAN",
    type=["dbf"]
)

if not arquivo:
    st.info("Envie um arquivo `.DBF` para iniciar a leitura.")
    st.stop()

if arquivo.size > LIMITE_BYTES:
    st.error(f"O arquivo enviado possui mais de {LIMITE_MB} MB. Envie um arquivo menor.")
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

# ============================================================
# APLICA MAPEAMENTO
# ============================================================

if agravo == "Acidente de Trabalho Grave":
    df = aplicar_mapeamento(df)
    df_publico = gerar_tabela_publica(df)
else:
    df_publico = df.copy()

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

st.header("🔎 Busca no banco")

df_busca = df_publico.copy()

busca_notificacao = st.text_input("Buscar por número da notificação")

if busca_notificacao and "NU_NOTIFIC" in df_busca.columns:
    df_busca = df_busca[
        df_busca["NU_NOTIFIC"]
        .astype(str)
        .str.contains(busca_notificacao, case=False, na=False)
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

usar_periodo_total = st.sidebar.checkbox(
    "Selecionar todo o período disponível",
    value=True
)

if "DT_NOTIFIC" in df_filtrado.columns:
    df_filtrado["DT_NOTIFIC"] = pd.to_datetime(df_filtrado["DT_NOTIFIC"], errors="coerce")

    min_d = df_filtrado["DT_NOTIFIC"].min()
    max_d = df_filtrado["DT_NOTIFIC"].max()

    if pd.notna(min_d) and pd.notna(max_d) and not usar_periodo_total:
        data_ini, data_fim = st.sidebar.date_input(
            "Período da notificação",
            value=[min_d.date(), max_d.date()],
            min_value=min_d.date(),
            max_value=max_d.date()
        )

        df_filtrado = df_filtrado[
            (df_filtrado["DT_NOTIFIC"].dt.date >= data_ini) &
            (df_filtrado["DT_NOTIFIC"].dt.date <= data_fim)
        ]

def preparar_opcoes(serie):
    serie = serie.fillna("Ignorado").astype(str).str.strip()
    serie = serie.replace("", "Ignorado")
    serie = serie.replace(["nan", "None", "NaT", "NULL", "null"], "Ignorado")
    return sorted(serie.unique())

def filtro_multiselect(label, coluna):
    global df_filtrado

    if coluna in df_filtrado.columns:
        df_filtrado[coluna] = (
            df_filtrado[coluna]
            .fillna("Ignorado")
            .astype(str)
            .str.strip()
            .replace("", "Ignorado")
        )

        opcoes = preparar_opcoes(df_filtrado[coluna])
        selecionados = st.sidebar.multiselect(label, opcoes)

        if selecionados:
            df_filtrado = df_filtrado[df_filtrado[coluna].isin(selecionados)]

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

st.header("📈 Visualização inicial")

colA, colB = st.columns(2)

if "CS_SEXO_DESC" in df_filtrado.columns:
    sexo = df_filtrado["CS_SEXO_DESC"].value_counts().reset_index()
    sexo.columns = ["Sexo", "Quantidade"]

    fig = px.pie(
        sexo,
        names="Sexo",
        values="Quantidade",
        title="Distribuição por sexo",
        color_discrete_sequence=PALETA,
        hole=0.35
    )
    colA.plotly_chart(fig, use_container_width=True)

if "EVOLUCAO_DESC" in df_filtrado.columns:
    evolucao = df_filtrado["EVOLUCAO_DESC"].value_counts().reset_index()
    evolucao.columns = ["Evolução", "Quantidade"]

    fig = px.bar(
        evolucao,
        x="Evolução",
        y="Quantidade",
        title="Evolução do caso",
        color_discrete_sequence=[CORES["azul"]]
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
        title="Situação no mercado de trabalho",
        color_discrete_sequence=[CORES["verde"]]
    )
    colC.plotly_chart(fig, use_container_width=True)

if "LOCAL_ACID_DESC" in df_filtrado.columns:
    local = df_filtrado["LOCAL_ACID_DESC"].value_counts().reset_index()
    local.columns = ["Local", "Quantidade"]

    fig = px.bar(
        local,
        x="Local",
        y="Quantidade",
        title="Local onde ocorreu o acidente",
        color_discrete_sequence=[CORES["laranja"]]
    )
    colD.plotly_chart(fig, use_container_width=True)

# ============================================================
# TABELA
# ============================================================

st.header("📋 Dados decodificados")

st.dataframe(df_filtrado, use_container_width=True)

# ============================================================
# ESTRUTURA E DOWNLOAD
# ============================================================

with st.expander("📚 Estrutura do DBF"):
    st.dataframe(resumo_dbf(df), use_container_width=True)

st.download_button(
    "📥 Baixar dados decodificados em CSV",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="sinan_acidente_trabalho_decodificado.csv",
    mime="text/csv"
)

st.markdown("---")

st.success(
    "Leitura concluída. Para análises completas e geração da ficha PDF, "
    "acesse o módulo **Painel Acidente de Trabalho Grave** no menu lateral."
)

st.caption("SINAN Decoder • Leitor DBF • Versão 2")
