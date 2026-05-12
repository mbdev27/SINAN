import tempfile
import streamlit as st
import pandas as pd

from utils.leitor_dbf import ler_dbf_com_diagnostico, resumo_dbf
from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.auth import exigir_login, fazer_logout, obter_usuario_atual
from utils.auditoria_sinan import inferir_agravo, gerar_auditoria_sinan

from mappings.acidente_trabalho_grave import aplicar_mapeamento, gerar_tabela_publica
from mappings.violencia import aplicar_mapeamento_violencia, gerar_tabela_publica_violencia
from mappings.arbovirose import aplicar_mapeamento_arbovirose, gerar_tabela_publica_arbovirose
from mappings.intoxicacao_exogena import aplicar_mapeamento_intoxicacao_exogena, gerar_tabela_publica_intoxicacao_exogena
from mappings.leptospirose import aplicar_mapeamento_leptospirose, gerar_tabela_publica_leptospirose
from mappings.toxoplasmose import aplicar_mapeamento_toxoplasmose, gerar_tabela_publica_toxoplasmose

from mappings.generico_sinan import aplicar_mapeamento_generico, gerar_tabela_publica_generica

from config.agravos import AGRAVOS

from modulos.painel_acidente_trabalho import render_painel_acidente_trabalho
from modulos.painel_violencia import render_painel_violencia
from modulos.painel_arbovirose import render_painel_arbovirose
from modulos.painel_intoxicacao_exogena import render_painel_intoxicacao_exogena
from modulos.painel_leptospirose import render_painel_leptospirose
from modulos.painel_toxoplasmose import render_painel_toxoplasmose
from modulos.painel_generico_sinan import render_painel_generico_sinan


st.set_page_config(
    page_title="Leitor DBF SINAN",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

exigir_login()

aplicar_tema_streamlit(st)
aplicar_tema_plotly()


usuario = obter_usuario_atual()

st.sidebar.markdown("## 👤 Sessão")
st.sidebar.write(f"**Usuário:** {usuario['nome']}")
st.sidebar.write(f"**Perfil:** {usuario['perfil']}")

if st.sidebar.button("🚪 Sair do sistema", use_container_width=True):
    fazer_logout()
    st.rerun()


st.markdown(
    """
    <div class="hz-hero">
        <span class="hz-kicker">Horizonte Health Intelligence</span>
        <h1>Leitor Inteligente de Bancos DBF — SINAN</h1>
        <p>
            Upload, leitura inteligente, detecção automática do agravo,
            auditoria de qualidade e acesso aos painéis analíticos.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("## 📤 Upload do banco DBF")

arquivo = st.file_uploader(
    "Selecione o arquivo DBF",
    type=["dbf"]
)

if arquivo is None:
    st.info("Envie um banco DBF do SINAN para iniciar.")
    st.stop()


tamanho_mb = arquivo.size / (1024 * 1024)

if tamanho_mb > 100:
    st.error("❌ O arquivo excede o limite atual de 100MB.")
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
    st.warning("O banco enviado não possui registros.")
    st.stop()


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
    ficha_sugerida = AGRAVOS[agravo_confirmado].get(
        "ficha",
        "Ficha não informada"
    )


painel_especifico = True

if agravo_confirmado == "Acidente de Trabalho Grave":
    df = aplicar_mapeamento(df)
    df_publico = gerar_tabela_publica(df)

elif agravo_confirmado == "Violência Interpessoal/Autoprovocada":
    df = aplicar_mapeamento_violencia(df)
    df_publico = gerar_tabela_publica_violencia(df)

elif agravo_confirmado == "Dengue/Chikungunya":
    df = aplicar_mapeamento_arbovirose(df)
    df_publico = gerar_tabela_publica_arbovirose(df)

elif agravo_confirmado == "Intoxicação Exógena":
    df = aplicar_mapeamento_intoxicacao_exogena(df)
    df_publico = gerar_tabela_publica_intoxicacao_exogena(df)

elif agravo_confirmado == "Leptospirose":
    df = aplicar_mapeamento_leptospirose(df)
    df_publico = gerar_tabela_publica_leptospirose(df)

elif agravo_confirmado == "Toxoplasmose":
    df = aplicar_mapeamento_toxoplasmose(df, arquivo.name)
    df_publico = gerar_tabela_publica_toxoplasmose(df)

else:
    painel_especifico = False
    df = aplicar_mapeamento_generico(df)
    df_publico = gerar_tabela_publica_generica(df)


st.session_state["df_sinan_atual"] = df
st.session_state["df_sinan_publico"] = df_publico
st.session_state["agravo_sinan_atual"] = agravo_confirmado
st.session_state["ficha_sinan_atual"] = ficha_sugerida


st.markdown("## 🧠 Leitura Inteligente do Banco")

l1, l2, l3, l4 = st.columns(4)

l1.metric(
    label="Registros",
    value=diagnostico_leitura.get("registros", len(df))
)

l2.metric(
    label="Colunas",
    value=diagnostico_leitura.get("colunas", len(df.columns))
)

l3.metric(
    label="Agravo",
    value=agravo_confirmado
)

l4.metric(
    label="Precisão",
    value=confianca
)


st.info(
    f"**Ficha sugerida:** {ficha_sugerida}\n\n"
    f"**Motivo:** {motivo}"
)


ranking = inferido.get("ranking", [])

if ranking:
    with st.expander("🏁 Ver ranking de possíveis agravos"):
        st.dataframe(
            pd.DataFrame(ranking),
            use_container_width=True
        )


auditoria = gerar_auditoria_sinan(
    df,
    agravo=agravo_confirmado
)

st.markdown("## 🧪 Auditoria de Qualidade do Banco")

duplicidades_qtd = len(auditoria.get("duplicidades", pd.DataFrame()))
sexo_incompat_qtd = len(auditoria.get("sexo_incompativel", pd.DataFrame()))
cid_incompat_qtd = len(auditoria.get("cid_incompativel", pd.DataFrame()))


a1, a2, a3, a4, a5 = st.columns(5)

a1.metric(
    label="Score",
    value=f"{auditoria.get('score_banco', 0)}%"
)

a2.metric(
    label="Qualidade",
    value=auditoria.get("qualidade_banco", "—")
)

a3.metric(
    label="Duplicidades",
    value=duplicidades_qtd
)

a4.metric(
    label="Sexo incompat.",
    value=sexo_incompat_qtd
)

a5.metric(
    label="CID incompat.",
    value=cid_incompat_qtd
)


b1, b2 = st.columns(2)

with b1:
    st.subheader("🏥 Incompletude por unidade")

    incompletude = auditoria.get(
        "incompletude_unidade",
        pd.DataFrame()
    )

    if isinstance(incompletude, pd.DataFrame) and not incompletude.empty:
        st.dataframe(
            incompletude,
            use_container_width=True,
            height=450
        )
    else:
        st.info("Não foi possível calcular a incompletude por unidade.")


with b2:
    st.subheader("🧱 Colunas mais vazias")

    colunas_vazias = auditoria.get(
        "colunas_vazias",
        pd.DataFrame()
    )

    if isinstance(colunas_vazias, pd.DataFrame) and not colunas_vazias.empty:
        st.dataframe(
            colunas_vazias.head(20),
            use_container_width=True,
            height=450
        )
    else:
        st.info("Não foram encontradas colunas vazias relevantes.")


with st.expander("🔍 Ver inconsistências detalhadas"):
    st.markdown("### Duplicidades")
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

    st.markdown("### Município divergente")
    st.dataframe(
        auditoria.get("municipio_divergente", pd.DataFrame()),
        use_container_width=True
    )


def fechar_paineis():
    for chave in [
        "abrir_painel_acidente_trabalho",
        "abrir_painel_violencia",
        "abrir_painel_arbovirose",
        "abrir_painel_intoxicacao",
        "abrir_painel_leptospirose",
        "abrir_painel_toxoplasmose",
        "abrir_painel_generico",
    ]:
        st.session_state[chave] = False


st.markdown("---")
st.markdown("## 🚀 Abrir painel analítico")


if agravo_confirmado == "Acidente de Trabalho Grave":
    if st.button("👷 Abrir Painel — Acidente de Trabalho Grave", use_container_width=True):
        fechar_paineis()
        st.session_state["abrir_painel_acidente_trabalho"] = True

elif agravo_confirmado == "Violência Interpessoal/Autoprovocada":
    if st.button("🛡️ Abrir Painel — Violência", use_container_width=True):
        fechar_paineis()
        st.session_state["abrir_painel_violencia"] = True

elif agravo_confirmado == "Dengue/Chikungunya":
    if st.button("🦟 Abrir Painel — Arboviroses", use_container_width=True):
        fechar_paineis()
        st.session_state["abrir_painel_arbovirose"] = True

elif agravo_confirmado == "Intoxicação Exógena":
    if st.button("☣️ Abrir Painel — Intoxicação Exógena", use_container_width=True):
        fechar_paineis()
        st.session_state["abrir_painel_intoxicacao"] = True

elif agravo_confirmado == "Leptospirose":
    if st.button("🐀 Abrir Painel — Leptospirose", use_container_width=True):
        fechar_paineis()
        st.session_state["abrir_painel_leptospirose"] = True

elif agravo_confirmado == "Toxoplasmose":
    if st.button("🧬 Abrir Painel — Toxoplasmose", use_container_width=True):
        fechar_paineis()
        st.session_state["abrir_painel_toxoplasmose"] = True

else:
    st.info(
        "Este agravo ainda não possui painel específico. "
        "Você pode abrir o Painel Universal SINAN para análise geral do banco."
    )

    if st.button("📊 Abrir Painel Universal SINAN", use_container_width=True):
        fechar_paineis()
        st.session_state["abrir_painel_generico"] = True


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
            "Campo": df.columns,
            "Tipo": [str(df[c].dtype) for c in df.columns],
            "Valores preenchidos": [
                int(df[c].notna().sum())
                for c in df.columns
            ],
            "Percentual preenchido": [
                round((df[c].notna().sum() / len(df)) * 100, 1)
                if len(df) > 0 else 0
                for c in df.columns
            ]
        })

        st.dataframe(
            estrutura,
            use_container_width=True,
            height=500
        )


st.markdown("---")

st.download_button(
    "📥 Baixar dados decodificados em CSV",
    data=df_publico.to_csv(index=False).encode("utf-8"),
    file_name="dados_decodificados.csv",
    mime="text/csv"
)


if st.session_state.get("abrir_painel_acidente_trabalho", False):
    st.markdown("---")
    render_painel_acidente_trabalho(df)

if st.session_state.get("abrir_painel_violencia", False):
    st.markdown("---")
    render_painel_violencia(df)

if st.session_state.get("abrir_painel_arbovirose", False):
    st.markdown("---")
    render_painel_arbovirose(df)

if st.session_state.get("abrir_painel_intoxicacao", False):
    st.markdown("---")
    render_painel_intoxicacao_exogena(df)

if st.session_state.get("abrir_painel_leptospirose", False):
    st.markdown("---")
    render_painel_leptospirose(df)

if st.session_state.get("abrir_painel_toxoplasmose", False):
    st.markdown("---")
    render_painel_toxoplasmose(df)

if st.session_state.get("abrir_painel_generico", False):
    st.markdown("---")
    render_painel_generico_sinan(
        df,
        nome_agravo=agravo_confirmado
    )


st.caption("Horizonte Health Intelligence • Beta 1")
