import tempfile
import streamlit as st
import pandas as pd

from utils.leitor_dbf import ler_dbf_com_diagnostico, resumo_dbf
from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.auditoria_sinan import inferir_agravo, gerar_auditoria_sinan
from mappings.acidente_trabalho_grave import aplicar_mapeamento, gerar_tabela_publica
from config.agravos import AGRAVOS
from modulos.painel_acidente_trabalho import render_painel_acidente_trabalho


st.set_page_config(
    page_title="Leitor DBF SINAN",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_tema_streamlit(st)
aplicar_tema_plotly()


st.markdown("""
<style>
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin-bottom: 18px;
}

.metric-card {
    background: #FFFFFF;
    border-left: 5px solid #0057B7;
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.10);
}

.metric-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #0057B7 !important;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 1.05rem;
    font-weight: 800;
    color: #000000 !important;
    word-break: break-word;
}
</style>
""", unsafe_allow_html=True)


def mini_metric_grid(items):
    html = '<div class="metric-grid">'
    for label, value in items:
        html += f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


st.markdown("""
<div class="mb-header">
    <h1>🗂️ Leitor Inteligente DBF SINAN</h1>
    <p>
        Envie um banco DBF do SINAN, reconheça automaticamente o agravo,
        associe a ficha correspondente, audite a qualidade do banco e acesse
        o painel específico sem precisar enviar o arquivo novamente.
    </p>
</div>
""", unsafe_allow_html=True)


LIMITE_MB = 100
LIMITE_BYTES = LIMITE_MB * 1024 * 1024


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


with tempfile.NamedTemporaryFile(delete=False, suffix=".DBF") as tmp:
    tmp.write(arquivo.read())
    caminho_tmp = tmp.name

try:
    df, diagnostico_leitura = ler_dbf_com_diagnostico(caminho_tmp)
except Exception as e:
    st.error(f"Erro ao ler o arquivo DBF: {e}")
    st.stop()

if df.empty:
    st.warning("O DBF foi lido, mas não possui registros.")
    st.stop()


inferido = inferir_agravo(df, arquivo.name)

opcoes_agravos = list(AGRAVOS.keys())

if inferido["agravo"] in opcoes_agravos:
    indice_inicial = opcoes_agravos.index(inferido["agravo"])
else:
    indice_inicial = 0

st.subheader("📌 Agravo associado ao banco")

agravo_confirmado = st.selectbox(
    "O sistema identificou o agravo abaixo. Você pode alterar manualmente, se necessário.",
    opcoes_agravos,
    index=indice_inicial
)

ficha_sugerida = AGRAVOS[agravo_confirmado].get("ficha", "Ficha não informada")

if agravo_confirmado == inferido["agravo"]:
    confianca = inferido["confianca"]
    motivo = inferido["motivo"]
else:
    confianca = "Manual"
    motivo = "Agravo alterado manualmente pelo usuário."


st.header("🧠 Leitura Inteligente do Banco")

mini_metric_grid([
    ("Registros", diagnostico_leitura["registros"]),
    ("Colunas", diagnostico_leitura["colunas"]),
    ("Agravo identificado", agravo_confirmado),
    ("Confiança", confianca),
])

st.info(
    f"**Ficha sugerida:** {ficha_sugerida}  \n\n"
    f"**Motivo:** {motivo}"
)

if "ranking" in inferido and inferido["ranking"]:
    with st.expander("🏁 Ver ranking de possíveis agravos"):
        st.dataframe(pd.DataFrame(inferido["ranking"]), use_container_width=True)


if agravo_confirmado == "Acidente de Trabalho Grave":
    df = aplicar_mapeamento(df)
    df_publico = gerar_tabela_publica(df)
else:
    df_publico = df.copy()


st.session_state["df_sinan_atual"] = df
st.session_state["df_sinan_publico"] = df_publico
st.session_state["agravo_sinan_atual"] = agravo_confirmado
st.session_state["ficha_sinan_atual"] = ficha_sugerida


auditoria = gerar_auditoria_sinan(df, agravo=agravo_confirmado)

st.header("🧪 Auditoria de Qualidade do Banco")

mini_metric_grid([
    ("Score do banco", f"{auditoria['score_banco']}%"),
    ("Qualidade", auditoria["qualidade_banco"]),
    ("Duplicidades prováveis", len(auditoria["duplicidades"])),
    ("Sexo incompatível", len(auditoria["sexo_incompativel"])),
    ("CID incompatível", len(auditoria["cid_incompativel"])),
])

b1, b2 = st.columns(2)

with b1:
    st.subheader("🏥 Incompletude por unidade")
    if not auditoria["incompletude_unidade"].empty:
        st.dataframe(auditoria["incompletude_unidade"], use_container_width=True)
    else:
        st.info("Não foi possível calcular por unidade.")

with b2:
    st.subheader("🧱 Colunas mais vazias")
    st.dataframe(auditoria["colunas_vazias"].head(20), use_container_width=True)

with st.expander("🔍 Ver inconsistências detalhadas"):
    st.markdown("### Duplicidades prováveis")
    st.dataframe(auditoria["duplicidades"], use_container_width=True)

    st.markdown("### Sexo incompatível")
    st.dataframe(auditoria["sexo_incompativel"], use_container_width=True)

    st.markdown("### Idade incompatível")
    st.dataframe(auditoria["idade_incompativel"], use_container_width=True)

    st.markdown("### CID incompatível")
    st.dataframe(auditoria["cid_incompativel"], use_container_width=True)

    st.markdown("### Município de notificação diferente do município de residência")
    st.dataframe(auditoria["municipio_divergente"], use_container_width=True)


st.header("📊 Resumo do Banco")

notificacoes_unicas = "—"
if "NU_NOTIFIC" in df.columns:
    notificacoes_unicas = df["NU_NOTIFIC"].nunique()

mini_metric_grid([
    ("Registros", len(df)),
    ("Colunas", len(df.columns)),
    ("Notificações únicas", notificacoes_unicas),
])


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


df_exibicao = df_busca.copy()

if df_exibicao.empty:
    st.warning("Nenhum registro encontrado.")
    st.stop()


st.header("📋 Dados decodificados")

st.dataframe(df_exibicao, use_container_width=True)


with st.expander("📚 Estrutura do DBF"):
    st.dataframe(resumo_dbf(df), use_container_width=True)


st.download_button(
    "📥 Baixar dados decodificados em CSV",
    data=df_exibicao.to_csv(index=False).encode("utf-8"),
    file_name="sinan_dados_decodificados.csv",
    mime="text/csv"
)


st.markdown("---")

st.header("🚀 Acessar painel específico")

if agravo_confirmado == "Acidente de Trabalho Grave":
    if st.button("👷 Abrir Painel de Acidente de Trabalho Grave", use_container_width=True):
        st.session_state["abrir_painel_acidente_trabalho"] = True
else:
    st.info(
        "Este agravo já foi reconhecido, mas o painel específico ainda será criado. "
        "Por enquanto, utilize a auditoria e os dados decodificados nesta página."
    )

if st.session_state.get("abrir_painel_acidente_trabalho", False):
    st.markdown("---")
    render_painel_acidente_trabalho(df)

st.caption("SINAN Decoder • Leitor DBF Inteligente • Versão 5")
