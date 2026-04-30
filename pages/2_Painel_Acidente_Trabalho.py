import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.leitor_dbf import ler_dbf
from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly, CORES, PALETA
from mappings.acidente_trabalho_grave import aplicar_mapeamento, gerar_tabela_publica
from utils.gerador_ficha_pdf import gerar_ficha_pdf


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Painel Acidente de Trabalho Grave",
    page_icon="👷",
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_tema_streamlit(st)
aplicar_tema_plotly()

CAMINHO_FICHA = "assets/DRT_Acidente_Trabalho_Grave.pdf"
LIMITE_MB = 100
LIMITE_BYTES = LIMITE_MB * 1024 * 1024


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="mb-header">
        <h1>👷 Painel Analítico — Acidente de Trabalho Grave</h1>
        <p>
            Análise interativa dos registros do SINAN a partir do banco DBF decodificado,
            com filtros, buscas, gráficos, avaliação da qualidade do preenchimento e geração
            da ficha oficial em PDF.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# UPLOAD
# ============================================================

arquivo = st.file_uploader(
    "Envie o banco DBF de Acidente de Trabalho Grave",
    type=["dbf"]
)

if not arquivo:
    st.info("Envie um arquivo `.DBF` para iniciar o painel.")
    st.stop()

if arquivo.size > LIMITE_BYTES:
    st.error(f"O arquivo enviado possui mais de {LIMITE_MB} MB. Envie um arquivo menor.")
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

for col in ["DT_NOTIFIC", "DT_ACID", "DT_NASC", "DT_OBITO"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    if col in df_publico.columns:
        df_publico[col] = pd.to_datetime(df_publico[col], errors="coerce")


# ============================================================
# BUSCA PARA GERAÇÃO DA FICHA
# ============================================================

st.header("🔎 Localizar registro para gerar ficha")

tipo_busca = st.selectbox(
    "Pesquisar por",
    [
        "Número da notificação",
        "Nome do paciente",
        "Nome da mãe"
    ]
)

termo_busca = st.text_input("Digite o termo de busca")

resultado_ficha = pd.DataFrame()

if termo_busca:
    if tipo_busca == "Número da notificação" and "NU_NOTIFIC" in df.columns:
        resultado_ficha = df[
            df["NU_NOTIFIC"].astype(str).str.contains(termo_busca, case=False, na=False)
        ]

    elif tipo_busca == "Nome do paciente" and "NM_PACIENT" in df.columns:
        resultado_ficha = df[
            df["NM_PACIENT"].astype(str).str.contains(termo_busca, case=False, na=False)
        ]

    elif tipo_busca == "Nome da mãe" and "NM_MAE_PAC" in df.columns:
        resultado_ficha = df[
            df["NM_MAE_PAC"].astype(str).str.contains(termo_busca, case=False, na=False)
        ]

if termo_busca and resultado_ficha.empty:
    st.warning("Nenhum registro encontrado para a busca informada.")

registro_pdf = None

if not resultado_ficha.empty:
    st.success(f"{len(resultado_ficha)} registro(s) encontrado(s).")

    resultado_ficha = resultado_ficha.copy()

    resultado_ficha["OPCAO_BUSCA"] = (
        resultado_ficha.get("NU_NOTIFIC", "").astype(str)
        + " | "
        + resultado_ficha.get("NM_PACIENT", "").astype(str)
        + " | "
        + resultado_ficha.get("NM_MAE_PAC", "").astype(str)
    )

    escolha = st.selectbox(
        "Selecione o registro para geração da ficha",
        resultado_ficha["OPCAO_BUSCA"].tolist()
    )

    registro_pdf = resultado_ficha[
        resultado_ficha["OPCAO_BUSCA"] == escolha
    ].iloc[0]

    campos_preview = [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "DT_ACID",
        "NM_PACIENT",
        "NM_MAE_PAC",
        "CS_SEXO_DESC",
        "CS_RACA_DESC",
        "IDADE_CALCULADA",
        "FAIXA_ETARIA_CALCULADA",
        "OCUPACAO_DESC",
        "SIT_TRAB_DESC",
        "LOCAL_ACID_DESC",
        "TIPO_ACID_DESC",
        "EVOLUCAO_DESC",
        "CAT_DESC"
    ]

    preview = {
        campo: registro_pdf[campo]
        for campo in campos_preview
        if campo in registro_pdf.index
    }

    st.dataframe(
        pd.DataFrame(preview.items(), columns=["Campo", "Valor"]),
        use_container_width=True
    )

    try:
        pdf_bytes = gerar_ficha_pdf(registro_pdf, CAMINHO_FICHA)

        st.download_button(
            "📥 Baixar ficha preenchida em PDF",
            data=pdf_bytes,
            file_name=f"ficha_acidente_trabalho_{registro_pdf.get('NU_NOTIFIC', 'registro')}.pdf",
            mime="application/pdf"
        )

    except FileNotFoundError:
        st.error(
            "Ficha PDF base não encontrada. "
            "Coloque o arquivo em assets/DRT_Acidente_Trabalho_Grave.pdf"
        )

    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")


# ============================================================
# FILTROS DO PAINEL
# ============================================================

st.sidebar.header("🔎 Filtros")

df_filtrado = df_publico.copy()

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


def filtro(label, coluna):
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


filtro("Sexo", "CS_SEXO_DESC")
filtro("Raça/Cor", "CS_RACA_DESC")
filtro("Gestante", "CS_GESTANT_DESC")
filtro("Situação no Mercado de Trabalho", "SIT_TRAB_DESC")
filtro("Local do Acidente", "LOCAL_ACID_DESC")
filtro("Tipo de Acidente", "TIPO_ACID_DESC")
filtro("Regime de Tratamento", "REGIME_DESC")
filtro("Evolução", "EVOLUCAO_DESC")
filtro("CAT", "CAT_DESC")
filtro("Ocupação", "OCUPACAO_DESC")
filtro("Faixa Etária", "FAIXA_ETARIA_CALCULADA")

busca_geral = st.text_input("🔍 Pesquisar qualquer termo no banco filtrado")

if busca_geral:
    mask = df_filtrado.astype(str).apply(
        lambda col: col.str.contains(busca_geral, case=False, na=False)
    ).any(axis=1)
    df_filtrado = df_filtrado[mask]

if df_filtrado.empty:
    st.warning("Nenhum registro encontrado com os filtros aplicados.")
    st.stop()


# ============================================================
# INDICADORES
# ============================================================

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
if "OCUPACAO_DESC" in df_filtrado.columns and not df_filtrado["OCUPACAO_DESC"].dropna().empty:
    ocupacao_top = df_filtrado["OCUPACAO_DESC"].astype(str).value_counts().idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros", total)
c2.metric("Óbitos", int(obitos))
c3.metric("CAT emitida", int(cat_emitida))
c4.metric("Ocupação mais frequente", ocupacao_top)


# ============================================================
# GRÁFICOS
# ============================================================

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
        color_discrete_sequence=PALETA,
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
        color_discrete_sequence=[CORES["azul"]]
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
        color_discrete_sequence=[CORES["verde"]]
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
        color_discrete_sequence=[CORES["laranja"]]
    )
    col4.plotly_chart(fig, use_container_width=True)

col5, col6 = st.columns(2)

if "FAIXA_ETARIA_CALCULADA" in df_filtrado.columns:
    ordem_faixas = [
        "0 a 9 anos",
        "10 a 19 anos",
        "20 a 29 anos",
        "30 a 39 anos",
        "40 a 49 anos",
        "50 a 59 anos",
        "60 anos ou mais",
        "Ignorado"
    ]

    idade = df_filtrado["FAIXA_ETARIA_CALCULADA"].value_counts().reset_index()
    idade.columns = ["Faixa etária", "Quantidade"]
    idade["Faixa etária"] = pd.Categorical(
        idade["Faixa etária"],
        categories=ordem_faixas,
        ordered=True
    )
    idade = idade.sort_values("Faixa etária")

    fig = px.bar(
        idade,
        x="Faixa etária",
        y="Quantidade",
        title="Distribuição por Faixa Etária",
        color_discrete_sequence=[CORES["amarelo"]]
    )
    col5.plotly_chart(fig, use_container_width=True)

if "OCUPACAO_DESC" in df_filtrado.columns:
    ocup = (
        df_filtrado["OCUPACAO_DESC"]
        .value_counts()
        .reset_index()
        .head(20)
    )
    ocup.columns = ["Ocupação", "Quantidade"]

    fig = px.bar(
        ocup,
        x="Quantidade",
        y="Ocupação",
        orientation="h",
        title="Top 20 Ocupações",
        color_discrete_sequence=[CORES["azul"]]
    )
    col6.plotly_chart(fig, use_container_width=True)

if "DT_NOTIFIC" in df_filtrado.columns:
    base_serie = df_filtrado.dropna(subset=["DT_NOTIFIC"]).copy()
    base_serie["MES"] = base_serie["DT_NOTIFIC"].dt.to_period("M").astype(str)

    serie = (
        base_serie
        .groupby("MES")
        .size()
        .reset_index(name="Quantidade")
        .sort_values("MES")
    )

    if not serie.empty:
        fig = px.line(
            serie,
            x="MES",
            y="Quantidade",
            markers=True,
            title="Notificações por mês",
            color_discrete_sequence=[CORES["azul"]]
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# QUALIDADE DO PREENCHIMENTO DA FICHA
# ============================================================

CAMPOS_AVALIADOS_FICHA = [
    "NU_NOTIFIC",
    "DT_NOTIFIC",
    "ID_MUNICIP",
    "ID_UNIDADE",
    "DT_ACID",
    "NM_PACIENT",
    "DT_NASC",
    "NU_IDADE_N",
    "CS_SEXO",
    "CS_GESTANT",
    "CS_RACA",
    "CS_ESCOL_N",
    "NM_MAE_PAC",
    "ID_MN_RESI",
    "NM_BAIRRO",
    "NM_LOGRADO",
    "ID_OCUPA_N",
    "SIT_TRAB",
    "LOCAL_ACID",
    "CNAE",
    "TIPO_ACID",
    "MAIS_TRAB",
    "ATENDE_MED",
    "PART_CORP1",
    "CID_LESAO",
    "REGIME",
    "EVOLUCAO",
    "CAT",
    "DS_OBS"
]

CAMPOS_OBRIGATORIOS_FICHA = [
    "NU_NOTIFIC",
    "DT_NOTIFIC",
    "ID_MUNICIP",
    "ID_UNIDADE",
    "DT_ACID",
    "NM_PACIENT",
    "DT_NASC",
    "CS_SEXO",
    "CS_RACA",
    "CS_ESCOL_N",
    "ID_OCUPA_N",
    "SIT_TRAB",
    "LOCAL_ACID",
    "TIPO_ACID",
    "EVOLUCAO"
]


def campo_preenchido(valor):
    if pd.isna(valor):
        return False

    texto = str(valor).strip()

    if texto == "":
        return False

    if texto.lower() in ["nan", "none", "nat", "null"]:
        return False

    if texto.upper() == "IGNORADO":
        return False

    return True


def calcular_percentual_preenchimento(row):
    campos_existentes = [c for c in CAMPOS_AVALIADOS_FICHA if c in row.index]

    if not campos_existentes:
        return 0

    preenchidos = sum(campo_preenchido(row[c]) for c in campos_existentes)

    return round((preenchidos / len(campos_existentes)) * 100, 1)


def classificar_preenchimento(percentual):
    if percentual < 70:
        return "🚩 Ruim"

    if percentual < 90:
        return "🟨 Mediana"

    return "🟩 Boa"


def verificar_obrigatorios(row):
    faltantes = []

    for campo in CAMPOS_OBRIGATORIOS_FICHA:
        if campo in row.index:
            if not campo_preenchido(row[campo]):
                faltantes.append(campo)

    if faltantes:
        return "⚠️ Faltando: " + ", ".join(faltantes)

    return "✅ Obrigatórios preenchidos"


df_filtrado = df_filtrado.copy()

df_filtrado["PERCENTUAL_PREENCHIMENTO"] = df_filtrado.apply(
    calcular_percentual_preenchimento,
    axis=1
)

df_filtrado["QUALIDADE_PREENCHIMENTO"] = df_filtrado["PERCENTUAL_PREENCHIMENTO"].apply(
    classificar_preenchimento
)

df_filtrado["ALERTA_OBRIGATORIOS"] = df_filtrado.apply(
    verificar_obrigatorios,
    axis=1
)


# ============================================================
# TABELA
# ============================================================

st.header("📋 Dados Decodificados")

st.markdown("""
Esta tabela apresenta os registros decodificados e inclui uma avaliação automática da qualidade do preenchimento da ficha.
""")

media_preenchimento = df_filtrado["PERCENTUAL_PREENCHIMENTO"].mean()
fichas_ruins = df_filtrado["QUALIDADE_PREENCHIMENTO"].str.contains("Ruim", na=False).sum()
fichas_medias = df_filtrado["QUALIDADE_PREENCHIMENTO"].str.contains("Mediana", na=False).sum()
fichas_boas = df_filtrado["QUALIDADE_PREENCHIMENTO"].str.contains("Boa", na=False).sum()
com_alerta = df_filtrado["ALERTA_OBRIGATORIOS"].str.contains("Faltando", na=False).sum()

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Média de preenchimento", f"{media_preenchimento:.1f}%")
m2.metric("🚩 Ruins", int(fichas_ruins))
m3.metric("🟨 Medianas", int(fichas_medias))
m4.metric("🟩 Boas", int(fichas_boas))
m5.metric("⚠️ Obrigatórios ausentes", int(com_alerta))

st.dataframe(
    df_filtrado,
    use_container_width=True,
    column_config={
        "PERCENTUAL_PREENCHIMENTO": st.column_config.ProgressColumn(
            "Preenchimento da ficha",
            help="Percentual estimado de variáveis preenchidas na ficha.",
            format="%.1f%%",
            min_value=0,
            max_value=100,
        ),
        "QUALIDADE_PREENCHIMENTO": st.column_config.TextColumn(
            "Qualidade do preenchimento"
        ),
        "ALERTA_OBRIGATORIOS": st.column_config.TextColumn(
            "Campos obrigatórios"
        ),
    }
)

st.download_button(
    "📥 Baixar dados filtrados em CSV",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="acidente_trabalho_grave_decodificado.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("SINAN Decoder • Acidente de Trabalho Grave • Versão 2")
