import streamlit as st

from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.auth import exigir_login, fazer_logout, obter_usuario_atual


st.set_page_config(
    page_title="Página Inicial",
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
    <span class="hz-kicker">Beta 1 • Horizonte Health Intelligence</span>
    <h1>Dados públicos, visão clara, decisões melhores.</h1>
    <p>
        Uma plataforma GovTech para leitura inteligente de bancos SINAN,
        auditoria epidemiológica e painéis analíticos por agravo.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("## O projeto")

st.markdown("""
A **Horizonte Health Intelligence** nasce para resolver uma dor antiga da Vigilância em Saúde:
transformar bancos DBF, fichas de notificação e dados codificados em informação útil para
gestores, técnicos e equipes de campo.

A ferramenta lê bancos do SINAN, identifica o agravo provável, cruza a estrutura dos dados
com a lógica das fichas de notificação e apresenta uma camada analítica limpa, responsiva
e auditável.

O usuário final deve sentir que está usando uma plataforma pública moderna: segura,
organizada, bonita e confiável.
""")

st.markdown("## O que a plataforma faz")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="hz-card">
        <h3>📂 Lê bancos DBF</h3>
        <p>
            Recebe arquivos DBF do SINAN, identifica estrutura, colunas,
            volume de registros e prepara os dados para análise.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="hz-card">
        <h3>🧠 Reconhece agravos</h3>
        <p>
            Sugere automaticamente o agravo correspondente ao banco enviado,
            permitindo validação e ajuste manual pelo usuário.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="hz-card">
        <h3>🧪 Audita dados</h3>
        <p>
            Avalia completude, duplicidades, inconsistências, campos vazios,
            CID incompatível e qualidade do preenchimento.
        </p>
    </div>
    """, unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    st.markdown("""
    <div class="hz-card">
        <h3>📊 Cria painéis</h3>
        <p>
            Gera painéis por agravo, com KPIs, gráficos, filtros,
            séries temporais e tabelas decodificadas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown("""
    <div class="hz-card">
        <h3>🧾 Mede qualidade</h3>
        <p>
            Calcula o percentual de preenchimento por ficha e sinaliza
            registros ruins, medianos e bons.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown("""
    <div class="hz-card">
        <h3>📥 Exporta informação</h3>
        <p>
            Permite baixar dados decodificados para relatórios,
            reuniões técnicas e análises complementares.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## Como usar")

st.markdown("""
1. Entre no sistema com seu usuário e senha.
2. Acesse **Leitor DBF**.
3. Envie o banco DBF do SINAN.
4. Confira a leitura inteligente.
5. Confirme o agravo identificado.
6. Analise a auditoria de qualidade.
7. Abra o painel específico.
8. Explore gráficos, filtros e tabelas.
9. Exporte os dados quando necessário.
""")

st.markdown("## Módulos disponíveis na Beta 1")

st.markdown("""
<span class="hz-badge">👷 Acidente de Trabalho Grave</span>
<span class="hz-badge">🛡️ Violência</span>
<span class="hz-badge">🦟 Dengue/Chikungunya</span>
<span class="hz-badge">☣️ Intoxicação Exógena</span>
<span class="hz-badge">🐀 Leptospirose</span>
<span class="hz-badge">🧬 Toxoplasmose</span>
""", unsafe_allow_html=True)

st.markdown("## Sobre a Horizonte")

st.markdown("""
A **Horizonte** é uma GovTech brasileira criada para desenvolver soluções digitais
que aproximam tecnologia, gestão pública e sociedade.

A empresa atua na intersecção entre design institucional, ciência de dados,
automação de processos e saúde pública. Seu compromisso é criar produtos que
simplificam rotinas, fortalecem equipes e entregam clareza para gestores.

A Horizonte não vende apenas sistemas. Ela entrega visão, confiança e capacidade
de decisão.
""")

st.markdown("""
<div class="hz-panel-dark">
    <h2>Visão de futuro</h2>
    <p>
        Esta versão beta é o primeiro passo para uma plataforma SaaS de inteligência pública,
        com múltiplos municípios, múltiplos agravos, banco histórico, alertas automáticos,
        relatórios técnicos e integração com inteligência artificial.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.success("Para começar, acesse **Leitor DBF** no menu lateral.")

with col2:
    if st.button("🚪 Sair do sistema", use_container_width=True):
        fazer_logout()
        st.rerun()

st.caption("Horizonte • Health Intelligence • GovTech Beta 1")
