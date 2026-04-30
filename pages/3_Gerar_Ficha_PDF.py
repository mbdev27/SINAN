import tempfile
import streamlit as st
import pandas as pd

from utils.leitor_dbf import ler_dbf
from mappings.acidente_trabalho_grave import aplicar_mapeamento
from utils.gerador_ficha_pdf import gerar_ficha_pdf

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Gerar Ficha PDF",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Gerar Ficha de Notificação Preenchida")
st.markdown("""
Envie o banco DBF, pesquise pelo número da notificação e gere a ficha oficial
de Acidente de Trabalho Grave preenchida em PDF.
""")

CAMINHO_FICHA = "assets/DRT_Acidente_Trabalho_Grave.pdf"

# ============================================================
# UPLOAD
# ============================================================

arquivo = st.file_uploader(
    "Envie o arquivo DBF do SINAN",
    type=["dbf"]
)

if not arquivo:
    st.info("Envie um arquivo `.DBF` para iniciar.")
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

if "NU_NOTIFIC" not in df.columns:
    st.error("O banco não possui a coluna NU_NOTIFIC.")
    st.stop()

# ============================================================
# PESQUISA
# ============================================================

st.header("🔎 Localizar notificação")

numero = st.text_input("Digite o número da notificação")

if not numero:
    st.info("Digite um número de notificação para pesquisar.")
    st.stop()

resultado = df[
    df["NU_NOTIFIC"].astype(str).str.contains(numero, case=False, na=False)
]

if resultado.empty:
    st.warning("Nenhuma notificação encontrada.")
    st.stop()

st.success(f"{len(resultado)} registro(s) encontrado(s).")

opcoes = resultado["NU_NOTIFIC"].astype(str).tolist()

notificacao_escolhida = st.selectbox(
    "Selecione a notificação",
    opcoes
)

registro = resultado[
    resultado["NU_NOTIFIC"].astype(str) == notificacao_escolhida
].iloc[0]

# ============================================================
# PRÉ-VISUALIZAÇÃO
# ============================================================

st.header("📋 Pré-visualização do Registro")

campos_preview = [
    "NU_NOTIFIC",
    "DT_NOTIFIC",
    "DT_ACID",
    "NM_PACIENT",
    "CS_SEXO_DESC",
    "CS_RACA_DESC",
    "ID_OCUPA_N",
    "SIT_TRAB_DESC",
    "LOCAL_ACID_DESC",
    "TIPO_ACID_DESC",
    "EVOLUCAO_DESC",
    "CAT_DESC"
]

preview = {
    campo: registro[campo]
    for campo in campos_preview
    if campo in registro.index
}

st.dataframe(
    pd.DataFrame(preview.items(), columns=["Campo", "Valor"]),
    use_container_width=True
)

# ============================================================
# GERAR PDF
# ============================================================

st.header("📄 Gerar PDF")

try:
    pdf_bytes = gerar_ficha_pdf(registro, CAMINHO_FICHA)

    st.download_button(
        "📥 Baixar ficha preenchida em PDF",
        data=pdf_bytes,
        file_name=f"ficha_acidente_trabalho_{notificacao_escolhida}.pdf",
        mime="application/pdf"
    )

except FileNotFoundError:
    st.error(
        "Ficha PDF base não encontrada. "
        "Coloque o arquivo em assets/DRT_Acidente_Trabalho_Grave.pdf"
    )

except Exception as e:
    st.error(f"Erro ao gerar PDF: {e}")

st.markdown("---")
st.caption("SINAN Decoder • Gerador de Ficha PDF • Versão MVP")
