from textwrap import dedent

import streamlit as st

from utils.auth import exigir_login, obter_usuario_atual
from utils.tema import aplicar_tema_streamlit


st.set_page_config(
    page_title="Sobre a Horizonte",
    page_icon="🌌",
    layout="wide"
)

exigir_login()
aplicar_tema_streamlit(st)

usuario = obter_usuario_atual()
nome_usuario = usuario.get("nome", usuario.get("usuario", "Usuário"))


st.markdown(
    dedent("""
    <style>
    .hz-page {
        max-width: 1450px;
        margin: auto;
        padding-bottom: 4rem;
    }

    .sobre-hero {
        border-radius: 34px;
        padding: 4.5rem 4rem;
        background:
            radial-gradient(circle at top left, rgba(0,237,100,0.18), transparent 28%),
            radial-gradient(circle at bottom right, rgba(16,24,32,0.95), transparent 34%),
            linear-gradient(135deg, #07111B 0%, #0A2647 48%, #08131F 100%);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 30px 80px rgba(0,0,0,0.38);
        margin-bottom: 2rem;
    }

    .sobre-kicker {
        display: inline-flex;
        padding: .45rem .9rem;
        border-radius: 999px;
        background: rgba(0,237,100,0.12);
        color: #00ED64 !important;
        font-weight: 800;
        font-size: .82rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        border: 1px solid rgba(0,237,100,0.25);
    }

    .sobre-title {
        color: #FFFFFF !important;
        font-size: clamp(2.7rem, 5vw, 5rem);
        line-height: 1.02;
        font-weight: 900;
        margin-bottom: 1.5rem;
        max-width: 920px;
        letter-spacing: -0.04em;
    }

    .sobre-subtitle {
        color: rgba(255,255,255,0.82) !important;
        font-size: 1.16rem;
        line-height: 1.9;
        max-width: 930px;
    }

    .sobre-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 1.2rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    .sobre-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 26px;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
    }

    .sobre-card h3 {
        color: #FFFFFF !important;
        font-size: 1.15rem;
        margin-bottom: .8rem;
        font-weight: 800;
    }

    .sobre-card p {
        color: rgba(255,255,255,0.78) !important;
        line-height: 1.7;
        font-size: .95rem;
    }

    .sobre-section {
        margin-top: 3rem;
        margin-bottom: 2rem;
    }

    .sobre-section-title {
        color: #FFFFFF !important;
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
    }

    .sobre-section-text {
        color: rgba(255,255,255,0.78) !important;
        line-height: 1.9;
        font-size: 1rem;
        max-width: 1100px;
    }

    .sobre-pillars {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }

    .sobre-pillar {
        border-radius: 24px;
        padding: 1.5rem;
        background: linear-gradient(180deg, rgba(8,19,31,0.96), rgba(10,38,71,0.82));
        border: 1px solid rgba(255,255,255,0.06);
    }

    .sobre-pillar span {
        font-size: 2rem;
        display: block;
        margin-bottom: .8rem;
    }

    .sobre-pillar h4 {
        color: #FFFFFF !important;
        margin-bottom: .6rem;
        font-size: 1.05rem;
        font-weight: 800;
    }

    .sobre-pillar p {
        color: rgba(255,255,255,0.74) !important;
        line-height: 1.65;
        font-size: .93rem;
    }

    .sobre-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }

    .sobre-metric {
        border-radius: 24px;
        padding: 1.6rem;
        text-align: center;
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
    }

    .sobre-metric h2 {
        color: #00ED64 !important;
        font-size: 2rem;
        margin-bottom: .4rem;
        font-weight: 900;
    }

    .sobre-metric p {
        color: rgba(255,255,255,0.74) !important;
        font-size: .9rem;
        line-height: 1.4;
    }

    .sobre-footer {
        margin-top: 4rem;
        padding: 2rem;
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(0,237,100,0.12), rgba(10,38,71,0.45));
        border: 1px solid rgba(0,237,100,0.14);
    }

    .sobre-footer h2 {
        color: #FFFFFF !important;
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 1rem;
    }

    .sobre-footer p {
        color: rgba(255,255,255,0.82) !important;
        line-height: 1.9;
        font-size: 1rem;
        max-width: 980px;
    }
    </style>
    """),
    unsafe_allow_html=True
)


st.markdown('<div class="hz-page">', unsafe_allow_html=True)

st.markdown(
    dedent("""
    <section class="sobre-hero">
        <div class="sobre-kicker">Horizonte Health Intelligence</div>

        <div class="sobre-title">
            Inteligência em saúde pública, vigilância epidemiológica
            e transformação digital.
        </div>

        <div class="sobre-subtitle">
            A Horizonte nasce para transformar bancos complexos,
            notificações fragmentadas e indicadores invisíveis
            em inteligência estratégica para municípios, estados
            e instituições de saúde.
            <br><br>
            Nossa missão é tornar os dados do SUS mais acessíveis,
            auditáveis, inteligentes e acionáveis.
        </div>
    </section>
    """),
    unsafe_allow_html=True
)


st.markdown(
    dedent("""
    <div class="sobre-grid">
        <div class="sobre-card">
            <h3>📊 Painéis Inteligentes</h3>
            <p>Dashboards analíticos construídos para vigilância epidemiológica, sanitária e gestão estratégica em saúde.</p>
        </div>

        <div class="sobre-card">
            <h3>🧠 Auditoria Automatizada</h3>
            <p>Identificação automática de inconsistências, duplicidades, baixa completude e padrões críticos.</p>
        </div>

        <div class="sobre-card">
            <h3>🗂️ Leitura Universal de DBFs</h3>
            <p>Compatibilidade com bancos do SINAN e expansão futura para e-SUS, SIM, SINASC e outros sistemas.</p>
        </div>

        <div class="sobre-card">
            <h3>🚨 Alertas Inteligentes</h3>
            <p>Detecção automática de tendências incomuns, aumento de casos e fragilidades operacionais.</p>
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


st.markdown(
    dedent("""
    <section class="sobre-section">
        <div class="sobre-section-title">Uma plataforma construída para o SUS real.</div>

        <div class="sobre-section-text">
            A Horizonte foi idealizada a partir das dores reais enfrentadas diariamente por equipes de vigilância em saúde.
            <br><br>
            Bancos incompletos, retrabalho operacional, dificuldade de visualizar tendências epidemiológicas,
            ausência de ferramentas modernas e pouco suporte analítico para tomada de decisão.
            <br><br>
            Em vez de apenas armazenar dados, a Horizonte interpreta, organiza, audita e transforma informação em inteligência.
        </div>
    </section>
    """),
    unsafe_allow_html=True
)


st.markdown(
    dedent("""
    <div class="sobre-pillars">
        <div class="sobre-pillar">
            <span>🌎</span>
            <h4>Saúde baseada em evidências</h4>
            <p>Indicadores epidemiológicos mais confiáveis para fortalecer decisões técnicas e gestão pública.</p>
        </div>

        <div class="sobre-pillar">
            <span>⚡</span>
            <h4>Velocidade operacional</h4>
            <p>Redução do tempo gasto em limpeza, análise e consolidação de bancos.</p>
        </div>

        <div class="sobre-pillar">
            <span>🔒</span>
            <h4>Segurança e rastreabilidade</h4>
            <p>Histórico de uploads, auditorias automáticas e controle de acessos por perfil.</p>
        </div>

        <div class="sobre-pillar">
            <span>🛰️</span>
            <h4>Escalabilidade</h4>
            <p>Estrutura preparada para expansão institucional, integração com bancos externos e uso multiusuário.</p>
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


st.markdown(
    dedent("""
    <section class="sobre-section">
        <div class="sobre-section-title">Horizonte em números</div>

        <div class="sobre-metrics">
            <div class="sobre-metric">
                <h2>+70</h2>
                <p>Agravos compatíveis com o SINAN</p>
            </div>

            <div class="sobre-metric">
                <h2>100%</h2>
                <p>Leitura automatizada de DBF</p>
            </div>

            <div class="sobre-metric">
                <h2>∞</h2>
                <p>Possibilidades analíticas</p>
            </div>

            <div class="sobre-metric">
                <h2>24/7</h2>
                <p>Disponibilidade em nuvem</p>
            </div>
        </div>
    </section>
    """),
    unsafe_allow_html=True
)


st.markdown(
    dedent("""
    <section class="sobre-section">
        <div class="sobre-section-title">Módulos atuais da plataforma</div>

        <div class="sobre-section-text">
            • Painel Universal SINAN<br>
            • Auditoria inteligente de bancos<br>
            • Histórico de uploads<br>
            • Relatórios técnicos em PDF<br>
            • Painéis específicos por agravo<br>
            • Controle de usuários e permissões<br>
            • Indicadores de qualidade do banco<br>
            • Alertas epidemiológicos automatizados<br>
            • Exportação institucional de dados
        </div>
    </section>
    """),
    unsafe_allow_html=True
)


st.markdown(
    dedent(f"""
    <section class="sobre-footer">
        <h2>O futuro da vigilância em saúde começa aqui.</h2>

        <p>
            Bem-vindo(a), <strong>{nome_usuario}</strong>.
            <br><br>
            A Horizonte não é apenas uma plataforma.
            É a construção de uma nova geração de inteligência aplicada à saúde pública brasileira.
            <br><br>
            Onde antes existiam planilhas esquecidas, agora surgem mapas, tendências,
            indicadores, alertas e decisões.
        </p>
    </section>
    """),
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)
