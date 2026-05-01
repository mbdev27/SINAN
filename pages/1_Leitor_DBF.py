import tempfile
import streamlit as st
import pandas as pd

from utils.leitor_dbf import ler_dbf_com_diagnostico, resumo_dbf
from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.auditoria_sinan import inferir_agravo, gerar_auditoria_sinan
from utils.qualidade_ficha import (
    adicionar_qualidade_ficha,
    colocar_qualidade_no_inicio,
    resumo_qualidade_ficha,
)
from mappings.acidente_trabalho_grave import aplicar_mapeamento, gerar_tabela_publica
from config.agravos import AGRAVOS
from modulos.painel_acidente_trabalho import render_painel_acidente_trabalho


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

st.markdown("""
<div class="mb-header">
    <h1>🗂️ Leitor Inteligente de Bancos DBF — SINAN</h1>
    <p>
        Plataforma inteligente para leitura, auditoria epidemiológica,
        decodificação e análise de bancos DBF do SINAN.
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

inferido = inferir_agravo(df, arquivo.name)

agravo_detectado = inferido.get("agravo", "Não identificado")
confianca = inferido.get("confianca", "Baixa")
motivo = inferido.get("motivo", "Sem justificativa disponível.")
ficha_sugerida = inferido.get("ficha_sugerida", "Selecionar manualmente")

nomes_agravos = list(AGRAVOS.keys())

if agravo_detectado in nomes_agravos:
    idx = nomes_agravos.index(agravo_detectado)
else:
    idx = 0

agravo_confirmado = st.selectbox(
    "🩺 Agravo identificado",
    nomes_agravos,
    index=idx,
    help="O sistema sugere automaticamente o agravo, mas você pode alterar manualmente."
)

if agravo_confirmado != agravo_detectado:
    confianca = "Manual"
    motivo = "Agravo alterado manualmente pelo usuário."
    ficha_sugerida = AGRAVOS[agravo_confirmado].get("ficha", "Ficha não informada")


# ============================================================
# MAPEAMENTO
# ============================================================

if agravo_confirmado == "Acidente de Trabalho Grave":
    df = aplicar_mapeamento(df)
    df_publico = gerar_tabela_publica(df)
else:
    df_publico = df.copy()


# ============================================================
# GUARDAR EM MEMÓRIA DA SESSÃO
# ============================================================

st.session_state["df_sinan_atual"] = df
st.session_state["df_sinan_publico"] = df_publico
st.session_state["agravo_sinan_atual"] = agravo_confirmado
st.session_state["ficha_sinan_atual"] = ficha_sugerida


# ============================================================
# LEITURA INTELIGENTE
# ============================================================

st.markdown("## 🧠 Leitura Inteligente do Banco")

l1, l2, l3, l4 = st.columns(4)

l1.metric("Registros", diagnostico_leitura.get("registros", len(df)))
l2.metric("Colunas", diagnostico_leitura.get("colunas", len(df.columns)))
l3.metric("Agravo identificado", agravo_confirmado)
l4.metric("Confiança", confianca)

st.info(
    f"**Ficha sugerida:** {ficha_sugerida}  \n\n"
    f"**Motivo:** {motivo}"
)

if "ranking" in inferido and inferido["ranking"]:
    with st.expander("🏁 Ver ranking de possíveis agravos"):
        st.dataframe(
            pd.DataFrame(inferido["ranking"]),
            use_container_width=True
        )


# ============================================================
# AUDITORIA DO BANCO
# ============================================================

auditoria = gerar_auditoria_sinan(df, agravo=agravo_confirmado)

st.markdown("## 🧪 Auditoria de Qualidade do Banco")

duplicidades_qtd = len(auditoria.get("duplicidades", pd.DataFrame()))
sexo_incompat_qtd = len(auditoria.get("sexo_incompativel", pd.DataFrame()))
cid_incompat_qtd = len(auditoria.get("cid_incompativel", pd.DataFrame()))

a1, a2, a3, a4, a5 = st.columns(5)

a1.metric("Score do banco", f"{auditoria.get('score_banco', 0)}%")
a2.metric("Qualidade", auditoria.get("qualidade_banco", "—"))
a3.metric("Duplicidades prováveis", duplicidades_qtd)
a4.metric("Sexo incompatível", sexo_incompat_qtd)
a5.metric("CID incompatível", cid_incompat_qtd)

b1, b2 = st.columns(2)

with b1:
    st.subheader("🏥 Incompletude por unidade")

    incompletude = auditoria.get("incompletude_unidade", pd.DataFrame())

    if isinstance(incompletude, pd.DataFrame) and not incompletude.empty:
        st.dataframe(incompletude, use_container_width=True)
    else:
        st.info("Não foi possível calcular a incompletude por unidade.")

with b2:
    st.subheader("🧱 Colunas mais vazias")

    colunas_vazias = auditoria.get("colunas_vazias", pd.DataFrame())

    if isinstance(colunas_vazias, pd.DataFrame) and not colunas_vazias.empty:
        st.dataframe(colunas_vazias.head(20), use_container_width=True)
    else:
        st.info("Não foram encontradas colunas vazias relevantes.")

with st.expander("🔍 Ver inconsistências detalhadas"):
    st.markdown("### Duplicidades prováveis")
    st.dataframe(
        auditoria.get("duplicidades", pd.DataFrame()),
        use_container_width=True
    )

    st.markdown("### Sexo incompatível")
    st.dataframe(
        auditoria.get("sexo_incompativel", pd.DataFrame()),
        use_container_width=True
    )

    st.markdown("### Idade incompatível")
    st.dataframe(
        auditoria.get("idade_incompativel", pd.DataFrame()),
        use_container_width=True
    )

    st.markdown("### CID incompatível")
    st.dataframe(
        auditoria.get("cid_incompativel", pd.DataFrame()),
        use_container_width=True
    )

    st.markdown("### Município de notificação diferente do município de residência")
    st.dataframe(
        auditoria.get("municipio_divergente", pd.DataFrame()),
        use_container_width=True
    )


# ============================================================
# BOTÃO PARA PAINEL ESPECÍFICO
# ============================================================

st.markdown("---")
st.markdown("## 🚀 Acessar painel específico")

if agravo_confirmado == "Acidente de Trabalho Grave":

    if st.button(
        "👷 Abrir Painel Analítico — Acidente de Trabalho Grave",
        use_container_width=True
    ):
        st.session_state["abrir_painel_acidente_trabalho"] = True

else:
    st.info(
        "Este agravo já foi reconhecido, mas o painel específico ainda será criado. "
        "Por enquanto, utilize a auditoria e os dados decodificados nesta página."
    )


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

q1.metric("Média", f"{resumo['media']}%")
q2.metric("🚩 Ruins", resumo["ruins"])
q3.metric("🟨 Medianas", resumo["medianas"])
q4.metric("🟩 Boas", resumo["boas"])
q5.metric("⚠️ Obrigatórios ausentes", resumo["alertas"])


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
    try:
        st.dataframe(
            resumo_dbf(df),
            use_container_width=True,
            height=500
        )
    except Exception:
        estrutura = pd.DataFrame({
            "Campo": df_exibicao.columns,
            "Tipo": [str(df_exibicao[c].dtype) for c in df_exibicao.columns],
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


# ============================================================
# RENDERIZA PAINEL ESPECÍFICO ABAIXO
# ============================================================

if st.session_state.get("abrir_painel_acidente_trabalho", False):
    st.markdown("---")
    render_painel_acidente_trabalho(df)

st.caption("SINAN Decoder • Leitor DBF Inteligente • Versão 6")
