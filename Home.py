import streamlit as st

from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.auth import exigir_login, fazer_logout, obter_usuario_atual


st.set_page_config(
    page_title="Página Inicial",
    page_icon="🏠",
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
<div class="mb-header">
    <h1>🏠 MB Health Intelligence</h1>
    <p>
        Inteligência epidemiológica aplicada ao SUS.
        Uma plataforma da MB Technological Solutions®.
    </p>
</div>
""", unsafe_allow_html=True)


st.markdown("## Transformando bancos SINAN em inteligência para decisão")

st.markdown("""
A **MB Health Intelligence** é uma plataforma desenvolvida para apoiar a Vigilância em Saúde
na leitura, auditoria, qualificação e análise de bancos epidemiológicos do SINAN.

O projeto nasce de uma dor real dos serviços públicos de saúde: muitos municípios possuem
grande volume de dados, mas enfrentam dificuldades para transformar bancos DBF, fichas de
notificação e registros codificados em informação útil para gestão, planejamento e resposta
oportuna.

A proposta da **MB Technological Solutions®** é criar uma ponte entre tecnologia, vigilância
epidemiológica e gestão pública. Não se trata apenas de visualizar dados, mas de qualificar
a informação, revelar inconsistências e apoiar decisões com evidências.
""")


st.markdown("## 🧠 O que a ferramenta faz")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="mb-card">
        <h3>📂 Lê bancos DBF</h3>
        <p>
            Permite o upload de arquivos DBF do SINAN e realiza a leitura estruturada
            dos dados, mesmo quando os bancos possuem campos codificados.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="mb-card">
        <h3>🔎 Reconhece o agravo</h3>
        <p>
            Analisa automaticamente o banco enviado e sugere o agravo correspondente,
            permitindo ao usuário confirmar ou alterar manualmente.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="mb-card">
        <h3>🧪 Audita a qualidade</h3>
        <p>
            Calcula score do banco, identifica colunas vazias, duplicidades prováveis,
            inconsistências e preenchimento das fichas de notificação.
        </p>
    </div>
    """, unsafe_allow_html=True)


c4, c5, c6 = st.columns(3)

with c4:
    st.markdown("""
    <div class="mb-card">
        <h3>📊 Gera painéis</h3>
        <p>
            Apresenta dashboards interativos por agravo, com indicadores,
            filtros, gráficos e tabelas decodificadas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown("""
    <div class="mb-card">
        <h3>🧾 Qualifica fichas</h3>
        <p>
            Mede o percentual de preenchimento por notificação e sinaliza fichas ruins,
            medianas ou boas, além de campos obrigatórios ausentes.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown("""
    <div class="mb-card">
        <h3>📥 Exporta dados</h3>
        <p>
            Permite baixar dados decodificados e filtrados em CSV, apoiando relatórios,
            análises complementares e prestação de contas.
        </p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("## 🚀 Como usar a plataforma")

st.markdown("""
1. No menu lateral, acesse **Leitor DBF**.
2. Envie o arquivo DBF do SINAN.
3. Aguarde a leitura inteligente do banco.
4. Confira o agravo identificado automaticamente.
5. Ajuste o agravo manualmente, se necessário.
6. Consulte a auditoria de qualidade do banco.
7. Abra o painel analítico específico.
8. Use os filtros, gráficos e tabelas para análise.
9. Exporte os dados decodificados quando precisar.
""")


st.markdown("## 🧩 Módulos analíticos")

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
    <div class="mb-card">
        <h4>👷 Saúde do Trabalhador</h4>
        <p>
            Análise de acidentes de trabalho graves, exposição ocupacional,
            evolução, CAT, ocupação e qualidade das notificações.
        </p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="mb-card">
        <h4>🛡️ Violência Interpessoal/Autoprovocada</h4>
        <p>
            Perfil das vítimas, tipos de violência, meios de agressão,
            provável autor, encaminhamentos e recorrência.
        </p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="mb-card">
        <h4>🦟 Arboviroses</h4>
        <p>
            Dengue e Chikungunya, classificação final, sinais clínicos,
            sinais de alarme, dengue grave e exames laboratoriais.
        </p>
    </div>
    """, unsafe_allow_html=True)

m4, m5, m6 = st.columns(3)

with m4:
    st.markdown("""
    <div class="mb-card">
        <h4>☣️ Intoxicação Exógena</h4>
        <p>
            Grupo do agente tóxico, local, circunstância, via de exposição,
            hospitalização, relação com trabalho e evolução.
        </p>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown("""
    <div class="mb-card">
        <h4>🐀 Leptospirose</h4>
        <p>
            Situações de risco, sinais clínicos, hospitalização,
            classificação, critério de confirmação e evolução do caso.
        </p>
    </div>
    """, unsafe_allow_html=True)

with m6:
    st.markdown("""
    <div class="mb-card">
        <h4>🧬 Toxoplasmose</h4>
        <p>
            Toxoplasmose adquirida, gestacional e congênita,
            com análise de classificação, critério, evolução e perfil.
        </p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("## 💼 Sobre a MB Technological Solutions®")

st.markdown("""
A **MB Technological Solutions®** nasce com a missão de desenvolver soluções digitais
para problemas reais da gestão pública, especialmente no campo da saúde coletiva,
vigilância em saúde e inteligência de dados.

A empresa combina conhecimento técnico-sanitário, desenvolvimento tecnológico e visão
estratégica para criar ferramentas capazes de reduzir trabalho manual, qualificar
processos e apoiar decisões baseadas em evidências.

A visão é evoluir a plataforma para um produto SaaS de inteligência epidemiológica,
com múltiplos agravos, login por município, banco histórico, relatórios automáticos,
alertas, integração com inteligência artificial e suporte à gestão regional e estadual.
""")


st.markdown("## 🌎 Visão de futuro")

st.markdown("""
A plataforma foi construída para crescer de forma modular. Cada novo agravo incorporado
aumenta a capacidade analítica do sistema e amplia seu valor para municípios, regionais,
estados, instituições de pesquisa e equipes técnicas.

O objetivo é criar uma camada moderna de inteligência sobre sistemas legados do SUS,
transformando bancos brutos em informação viva: clara, visual, auditável e acionável.
""")


st.markdown("---")

col_a, col_b = st.columns([2, 1])

with col_a:
    st.success("Para começar, acesse **Leitor DBF** no menu lateral.")

with col_b:
    if st.button("🚪 Sair do sistema", use_container_width=True):
        fazer_logout()
        st.rerun()


st.caption("MB Technological Solutions® • MB Health Intelligence • Inteligência Epidemiológica Aplicada ao SUS")
