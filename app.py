import streamlit as st

from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.auth import exigir_login, fazer_logout, obter_usuario_atual


st.set_page_config(
    page_title="Horizonte Health Intelligence",
    page_icon="🌅",
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


st.markdown("""
<div class="hz-hero">
    <span class="hz-kicker">Horizonte GovTech</span>
    <h1>Horizonte Health Intelligence</h1>
    <p>
        Inteligência epidemiológica, auditoria de dados e painéis analíticos
        para transformar bancos SINAN em clareza institucional.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("## Uma nova experiência para a Vigilância em Saúde")

st.markdown("""
A **Horizonte Health Intelligence** é uma plataforma da **Horizonte** criada para apoiar
equipes técnicas, coordenações e gestores públicos na leitura, auditoria e análise de
bancos epidemiológicos do SINAN.

A solução foi desenhada para ser robusta, intuitiva e institucional. Ela traduz bancos DBF
codificados em indicadores, gráficos, tabelas decodificadas e alertas de qualidade,
reduzindo trabalho manual e ampliando a capacidade de decisão.
""")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="hz-card">
        <h3>📂 Leitura DBF</h3>
        <p>
            Envie bancos DBF do SINAN e permita que a plataforma leia, organize
            e prepare os dados para análise epidemiológica.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="hz-card">
        <h3>🧠 Detecção inteligente</h3>
        <p>
            O sistema reconhece automaticamente o agravo provável e sugere
            a ficha correspondente, mantendo controle manual pelo usuário.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="hz-card">
        <h3>🧪 Auditoria de qualidade</h3>
        <p>
            Identifica incompletude, duplicidades, inconsistências,
            campos críticos vazios e qualidade do preenchimento.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="hz-panel-dark">
    <h2>O que a Horizonte entrega</h2>
    <p>
        Mais do que dashboards, a Horizonte entrega visão. Cada módulo foi pensado
        para transformar dados brutos em inteligência pública: clara, auditável,
        segura e pronta para orientar decisões.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🚀 Como usar")

st.markdown("""
1. Acesse **Leitor DBF** no menu lateral.
2. Faça upload do banco DBF do SINAN.
3. Confirme o agravo detectado.
4. Analise o diagnóstico e a auditoria do banco.
5. Abra o painel analítico específico.
6. Use filtros, gráficos e tabelas para explorar os dados.
7. Exporte os dados decodificados quando necessário.
""")

st.markdown("## 🧩 Módulos beta")

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
    <div class="hz-card">
        <h4>👷 Saúde do Trabalhador</h4>
        <p>Acidente de Trabalho Grave e Exposição a Material Biológico.</p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="hz-card">
        <h4>🛡️ Violências</h4>
        <p>Violência interpessoal e autoprovocada.</p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="hz-card">
        <h4>🦟 Arboviroses</h4>
        <p>Dengue, Chikungunya e indicadores clínicos/laboratoriais.</p>
    </div>
    """, unsafe_allow_html=True)

m4, m5, m6 = st.columns(3)

with m4:
    st.markdown("""
    <div class="hz-card">
        <h4>☣️ Intoxicação Exógena</h4>
        <p>Agente tóxico, circunstância, via de exposição e desfecho.</p>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown("""
    <div class="hz-card">
        <h4>🐀 Leptospirose</h4>
        <p>Riscos ambientais, sinais clínicos, laboratório e evolução.</p>
    </div>
    """, unsafe_allow_html=True)

with m6:
    st.markdown("""
    <div class="hz-card">
        <h4>🧬 Toxoplasmose</h4>
        <p>Formas adquirida, gestacional e congênita.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## 💼 Sobre a Horizonte")

st.markdown("""
A **Horizonte** é uma GovTech brasileira voltada à criação de plataformas digitais
para gestão pública, inteligência epidemiológica, dashboards institucionais,
automação de fluxos e análise estratégica.

Sua missão é provar que tecnologia pública pode ser segura, elegante, intuitiva
e humana. A plataforma representa a primeira versão beta desse ecossistema:
um produto modular, preparado para crescer em múltiplos agravos, múltiplos municípios
e, futuramente, múltiplas áreas da gestão pública.
""")

st.markdown("---")

if st.button("🚀 Ir para o Leitor DBF", use_container_width=True):
    st.switch_page("pages/1_Leitor_DBF.py")

st.caption("Horizonte • Health Intelligence • Beta 1")
