import streamlit as st

from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.auth import fazer_login, fazer_logout, usuario_logado, obter_usuario_atual


st.set_page_config(
    page_title="MB Health Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_tema_streamlit(st)
aplicar_tema_plotly()


# ============================================================
# LOGIN
# ============================================================

def tela_login():
    st.markdown("""
    <div class="mb-header">
        <h1>MB Health Intelligence</h1>
        <p>
            Plataforma de inteligência epidemiológica para leitura, auditoria,
            análise e qualificação de bancos SINAN.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("## 🔐 Acesso ao Sistema")

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        entrar = st.button("Entrar", use_container_width=True)

        if entrar:
            if fazer_login(usuario, senha):
                st.success("Login realizado com sucesso.")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

        st.info(
            "Ambiente demonstrativo. Para produção, recomenda-se autenticação "
            "com banco de dados, criptografia de senha e controle por município."
        )


if not usuario_logado():
    tela_login()
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

usuario = obter_usuario_atual()

st.sidebar.markdown("## 👤 Sessão")
st.sidebar.write(f"**Usuário:** {usuario['nome']}")
st.sidebar.write(f"**Perfil:** {usuario['perfil']}")

if st.sidebar.button("Sair"):
    fazer_logout()
    st.rerun()


# ============================================================
# HOME INSTITUCIONAL
# ============================================================

st.markdown("""
<div class="mb-header">
    <h1>🧠 MB Health Intelligence</h1>
    <p>
        Inteligência epidemiológica, auditoria de dados e apoio à decisão
        para Vigilância em Saúde.
    </p>
</div>
""", unsafe_allow_html=True)


st.markdown("## Plataforma de Inteligência Epidemiológica para o SUS")

st.markdown("""
A **MB Health Intelligence**, da **MB Technological Solutions®**, nasce para transformar
bancos epidemiológicos complexos em informação clara, auditável e estratégica.

A plataforma foi pensada para equipes de Vigilância em Saúde que lidam diariamente com
arquivos DBF do SINAN, fichas de notificação, inconsistências, subpreenchimento,
demanda por indicadores e necessidade de respostas rápidas à gestão.
""")


# ============================================================
# CARDS PRINCIPAIS
# ============================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="mb-card">
        <h3>📂 Leitura Inteligente</h3>
        <p>
            Upload de bancos DBF do SINAN com identificação automática do agravo,
            diagnóstico da estrutura do arquivo e preparação dos dados para análise.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="mb-card">
        <h3>🧪 Auditoria Epidemiológica</h3>
        <p>
            Detecção de incompletude, inconsistências, duplicidades, campos críticos
            vazios e qualidade do preenchimento por registro e unidade notificadora.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="mb-card">
        <h3>📊 Painéis Analíticos</h3>
        <p>
            Dashboards específicos por agravo com filtros, indicadores, gráficos,
            tabelas decodificadas e exportação de dados.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# VISÃO ESTRATÉGICA
# ============================================================

st.markdown("## 🎯 Objetivo Estratégico")

st.markdown("""
A proposta não é apenas visualizar dados. É criar uma camada moderna de inteligência
sobre sistemas legados do SUS, apoiando municípios, regionais e estados na qualificação
da informação em saúde.

A plataforma busca reduzir o trabalho manual, ampliar a capacidade analítica das equipes
e transformar bancos brutos em evidências úteis para decisão.
""")


# ============================================================
# MÓDULOS DISPONÍVEIS
# ============================================================

st.markdown("## 🧩 Módulos Analíticos em Desenvolvimento")

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
    <div class="mb-card">
        <h4>👷 Saúde do Trabalhador</h4>
        <p>Acidente de Trabalho Grave e Exposição a Material Biológico.</p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="mb-card">
        <h4>🛡️ Violências</h4>
        <p>Violência Interpessoal e Autoprovocada.</p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="mb-card">
        <h4>🦟 Arboviroses</h4>
        <p>Dengue, Chikungunya e indicadores clínicos/laboratoriais.</p>
    </div>
    """, unsafe_allow_html=True)

m4, m5, m6 = st.columns(3)

with m4:
    st.markdown("""
    <div class="mb-card">
        <h4>☣️ Intoxicação Exógena</h4>
        <p>Agente tóxico, circunstância, via de exposição e evolução.</p>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown("""
    <div class="mb-card">
        <h4>🐀 Leptospirose</h4>
        <p>Exposição ambiental, sinais clínicos, hospitalização e desfecho.</p>
    </div>
    """, unsafe_allow_html=True)

with m6:
    st.markdown("""
    <div class="mb-card">
        <h4>🧬 Toxoplasmose</h4>
        <p>Formas adquirida, gestacional e congênita.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FLUXO DE USO
# ============================================================

st.markdown("## 🚀 Como usar")

st.markdown("""
1. Acesse a página **Leitor DBF SINAN** no menu lateral.
2. Faça upload do banco DBF.
3. Confirme o agravo identificado automaticamente.
4. Analise a auditoria de qualidade do banco.
5. Abra o painel analítico específico.
6. Exporte os dados decodificados quando necessário.
""")


# ============================================================
# DIFERENCIAIS
# ============================================================

st.markdown("## 💼 Diferenciais da Solução")

d1, d2 = st.columns(2)

with d1:
    st.markdown("""
    <div class="mb-card">
        <h3>Para a gestão pública</h3>
        <p>
            Apoia planejamento, monitoramento, relatórios técnicos,
            tomada de decisão e qualificação das notificações.
        </p>
    </div>
    """, unsafe_allow_html=True)

with d2:
    st.markdown("""
    <div class="mb-card">
        <h3>Para as equipes técnicas</h3>
        <p>
            Reduz trabalho manual, melhora leitura dos bancos, facilita análise
            e evidencia problemas de preenchimento.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CHAMADA FINAL
# ============================================================

st.markdown("---")

st.markdown("""
### 🌎 Visão de futuro

A MB Health Intelligence foi concebida para evoluir de um painel analítico para uma
plataforma SaaS de inteligência epidemiológica, com múltiplos agravos, login por município,
banco histórico, relatórios automáticos, alertas e integração com inteligência artificial.
""")

st.success(
    "Para iniciar, acesse a página Leitor DBF SINAN no menu lateral."
)

st.caption("MB Technological Solutions® • Inteligência Epidemiológica Aplicada ao SUS")
