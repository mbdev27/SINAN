import streamlit as st

from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.auth import exigir_login, fazer_logout, obter_usuario_atual


st.set_page_config(
    page_title="MB Health Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

exigir_login()

aplicar_tema_streamlit(st)
aplicar_tema_plotly()


usuario = obter_usuario_atual()

st.sidebar.markdown("## 👤 Sessão")
st.sidebar.write(f"**Usuário:** {usuario.get('nome', 'Usuário')}")
st.sidebar.write(f"**Perfil:** {usuario.get('perfil', 'Perfil não informado')}")

if st.sidebar.button("🚪 Sair do sistema", use_container_width=True):
    fazer_logout()
    st.rerun()


st.markdown("""
<div class="mb-header">
    <h1>🧠 MB Health Intelligence</h1>
    <p>
        Plataforma de inteligência epidemiológica para leitura, auditoria,
        análise e qualificação de bancos SINAN.
    </p>
</div>
""", unsafe_allow_html=True)


st.markdown("## Bem-vindo à plataforma")

st.markdown("""
A **MB Health Intelligence**, desenvolvida pela **MB Technological Solutions®**, foi criada
para transformar bancos epidemiológicos do SINAN em informação clara, auditável e útil
para tomada de decisão.

A proposta é simples e poderosa: pegar arquivos DBF, geralmente difíceis de interpretar,
e convertê-los em painéis inteligentes, com leitura automática do agravo, auditoria da
qualidade do banco, identificação de inconsistências, visualizações analíticas e dados
decodificados.
""")


c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="mb-card">
        <h3>📂 Leitura DBF</h3>
        <p>
            Carregue bancos DBF do SINAN e permita que o sistema reconheça
            automaticamente o agravo e a estrutura do arquivo.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="mb-card">
        <h3>🧪 Auditoria</h3>
        <p>
            Identifique incompletude, duplicidades, campos vazios, inconsistências
            e qualidade de preenchimento das fichas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="mb-card">
        <h3>📊 Painéis</h3>
        <p>
            Acesse dashboards por agravo, com indicadores, gráficos, filtros,
            tabelas e exportação de dados.
        </p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("## 🚀 Como usar")

st.markdown("""
1. Acesse a página **Leitor DBF** no menu lateral.
2. Faça upload do banco DBF do SINAN.
3. Confirme o agravo identificado automaticamente.
4. Analise a auditoria de qualidade do banco.
5. Abra o painel analítico específico.
6. Exporte os dados filtrados quando necessário.
""")


st.markdown("## 🧩 Módulos disponíveis")

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
        <p>Dengue, Chikungunya e indicadores clínicos e laboratoriais.</p>
    </div>
    """, unsafe_allow_html=True)


m4, m5, m6 = st.columns(3)

with m4:
    st.markdown("""
    <div class="mb-card">
        <h4>☣️ Intoxicação Exó
