import tempfile
import streamlit as st
import pandas as pd

from utils.leitor_dbf import (
    ler_dbf_com_diagnostico,
    resumo_dbf
)

from utils.tema import (
    aplicar_tema_streamlit,
    aplicar_tema_plotly
)

from utils.auditoria_sinan import (
    inferir_agravo,
    gerar_auditoria_sinan
)

from utils.qualidade_ficha import (
    adicionar_qualidade_ficha,
    colocar_qualidade_no_inicio,
    resumo_qualidade_ficha,
)

from mappings.acidente_trabalho_grave import (
    aplicar_mapeamento,
    gerar_tabela_publica
)

from config.agravos import AGRAVOS


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Leitor DBF SINAN",
    page_icon="🗂️",
    layout="wide"
)

aplicar_tema_streamlit(st)
aplicar_tema_plotly()


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown("""
<div class="mb-header">
    <h1>🗂️ Leitor Inteligente de Bancos DBF — SINAN</h1>
    <p>
        Plataforma inteligente para leitura,
        auditoria epidemiológica, decodificação,
        análise e exploração de bancos DBF do SINAN.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# UPLOAD
# ============================================================

st.markdown("## 📤 Upload do banco DBF")

arquivo = st.file_uploader(
    "Selecione o arquivo DBF",
    type=["dbf"]
)

if arquivo is None:
    st.info("Envie um banco DBF do SINAN para iniciar.")
    st.stop()


# ============================================================
# LIMITE DE TAMANHO
# ============================================================

tamanho_mb = arquivo.size / (1024 * 1024)

if tamanho_mb > 100:
    st.error("❌ O arquivo excede o limite atual de 100MB.")
    st.stop()


# ============================================================
# LEITURA DO DBF
# ============================================================

with tempfile.NamedTemporaryFile(delete=False, suffix=".DBF") as tmp:
    tmp.write(arquivo.read())
    caminho_tmp = tmp.name

try:
    df, diagnostico_leitura = ler_dbf_com_diagnostico(caminho_tmp)

except Exception as e:
    st.error(f"Erro ao ler o arquivo DBF: {e}")
    st.stop()

if df.empty:
    st.warning("O banco enviado não possui registros.")
    st.stop()


# ============================================================
# DETECÇÃO DE AGRAVO
# ============================================================

agravo_detectado = inferir_agravo(df)

nomes_agravos = list(AGRAVOS.keys())

if agravo_detectado in nomes_agravos:
    idx = nomes_agravos.index(agravo_detectado)
else:
    idx = 0

agravo_confirmado = st.selectbox(
    "🩺 Selecione o agravo",
    nomes_agravos,
    index=idx
)


# ============================================================
# MAPEAMENTO
# ============================================================

if agravo_confirmado == "Acidente de Trabalho Grave":
    df = aplicar_mapeamento(df)

df_publico = gerar_tabela_publica(df)


# ============================================================
# LEITURA INTELIGENTE
# ============================================================

st.markdown("## 🧠 Leitura Inteligente do Banco")

c1, c2, c3 = st.columns(3)

c1.markdown(f"""
<div class="mb-card">
    <h3>{len(df.columns)}</h3>
    <p>Colunas identificadas</p>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="mb-card">
    <h3>{agravo_detectado}</h3>
    <p>Agravo identificado</p>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="mb-card">
    <h3>{len(df)}</h3>
    <p>Registros encontrados</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# AUDITORIA
# ============================================================

auditoria = gerar_auditoria_sinan(df)

st.markdown("## 🧪 Auditoria de Qualidade do Banco")

a1, a2, a3, a4 = st.columns(4)

a1.markdown(f"""
<div class="mb-card">
    <h3>{auditoria["qualidade_banco"]}</h3>
    <p>Qualidade geral</p>
</div>
""", unsafe_allow_html=True)

a2.markdown(f"""
<div class="mb-card">
    <h3>{auditoria["duplicidades"]}</h3>
    <p>Duplicidades prováveis</p>
</div>
""", unsafe_allow_html=True)

a3.markdown(f"""
<div class="mb-card">
    <h3>{auditoria["sexo_incompativel"]}</h3>
    <p>Sexo incompatível</p>
</div>
""", unsafe_allow_html=True)

a4.markdown(f"""
<div class="mb-card">
    <h3>{auditoria["cid_incompativel"]}</h3>
    <p>CID incompatível</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# BOTÃO PARA O PAINEL
# ============================================================

st.markdown("---")

if agravo_confirmado == "Acidente de Trabalho Grave":

    st.session_state["df_dbf"] = df

    if st.button("👷 Abrir Painel Analítico — Acidente de Trabalho Grave"):
        st.switch_page("pages/2_Painel_Acidente_Trabalho.py")


# ============================================================
# QUALIDADE DAS FICHAS
# ============================================================

df_exibicao = df_publico.copy()

if df_exibicao.empty:
    st.warning("Nenhum registro encontrado.")
    st.stop()

df_exibicao = adicionar_qualidade_ficha(
    df_exibicao,
    agravo_confirmado
)

df_exibicao = colocar_qualidade_no_inicio(df_exibicao)

resumo = resumo_qualidade_ficha(df_exibicao)

st.markdown("## 🧾 Qualidade do Preenchimento das Fichas")

q1, q2, q3, q4, q5 = st.columns(5)

q1.metric(
    "Média",
    f"{resumo['media']}%"
)

q2.metric(
    "🚩 Ruins",
    resumo["ruins"]
)

q3.metric(
    "🟨 Medianas",
    resumo["medianas"]
)

q4.metric(
    "🟩 Boas",
    resumo["boas"]
)

q5.metric(
    "⚠️ Obrigatórios ausentes",
    resumo["alertas"]
)


# ============================================================
# DADOS DECODIFICADOS
# ============================================================

st.markdown("---")
st.markdown("## 📋 Dados Decodificados")

st.dataframe(
    df_exibicao,
    use_container_width=True,
    height=650,

    column_config={

        "PERCENTUAL_PREENCHIMENTO": st.column_config.ProgressColumn(
            "Preenchimento da ficha",
            help="Percentual estimado de variáveis preenchidas.",
            format="%.1f%%",
            min_value=0,
            max_value=100,
        ),

        "QUALIDADE_PREENCHIMENTO": st.column_config.TextColumn(
            "Qualidade"
        ),

        "ALERTA_OBRIGATORIOS": st.column_config.TextColumn(
            "Campos obrigatórios"
        ),

    }
)


# ============================================================
# ESTRUTURA DO DBF
# ============================================================

st.markdown("---")

with st.expander("🧱 Estrutura do DBF"):

    estrutura = pd.DataFrame({
        "Campo": df_exibicao.columns,

        "Tipo": [
            str(df_exibicao[c].dtype)
            for c in df_exibicao.columns
        ],

        "Valores preenchidos": [
            int(df_exibicao[c].notna().sum())
            for c in df_exibicao.columns
        ],

        "Percentual preenchido": [
            round(
                (df_exibicao[c].notna().sum() / len(df_exibicao)) * 100,
                1
            )
            if len(df_exibicao) > 0 else 0

            for c in df_exibicao.columns
        ]
    })

    st.dataframe(
        estrutura,
        use_container_width=True,
        height=500
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.markdown("---")

st.download_button(
    "📥 Baixar dados decodificados em CSV",
    data=df_exibicao.to_csv(index=False).encode("utf-8"),
    file_name="dados_decodificados.csv",
    mime="text/csv"
)
