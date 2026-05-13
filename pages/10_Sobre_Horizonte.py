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


st.markdown(
    """
    <style>

    .hz-page {
        max-width: 1450px;
        margin: auto;
        padding-bottom: 4rem;
    }

    .hz-hero {
        position: relative;
        overflow: hidden;
        border-radius: 34px;
        padding: 4.5rem 4rem;
        background:
            radial-gradient(circle at top left, rgba(0,237,100,0.18), transparent 28%),
            radial-gradient(circle at bottom right, rgba(16,24,32,0.95), transparent 34%),
            linear-gradient(135deg, #07111B 0%, #0A2647 48%, #08131F 100%);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow:
            0 30px 80px rgba(0,0,0,0.38),
            inset 0 1px 0 rgba(255,255,255,0.04);
        margin-bottom: 2rem;
    }

    .hz-kicker {
        display: inline-flex;
        align-items: center;
        gap: .55rem;
        padding: .45rem .9rem;
        border-radius: 999px;
        background: rgba(0,237,100,0.12);
        color: #00ED64;
        font-weight: 800;
        font-size: .82rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        border: 1px solid rgba(0,237,100,0.25);
    }

    .hz-title {
        color: white;
        font-size: clamp(2.7rem, 5vw, 5rem);
        line-height: 1.02;
        font-weight: 900;
        margin-bottom: 1.5rem;
        max-width: 920px;
        letter-spacing: -0.04em;
    }

    .hz-subtitle {
        color: rgba(255,255,255,0.82);
        font-size: 1.16rem;
        line-height: 1.9;
        max-width: 930px;
    }

    .hz-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 1.2rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    .hz-card {
        background:
            linear-gradient(180deg,
            rgba(255,255,255,0.05),
            rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 26px;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
        transition: all .25s ease;
    }

    .hz-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0,237,100,0.35);
        box-shadow: 0 18px 40px rgba(0,0,0,0.24);
    }

    .hz-card h3 {
        color: white;
        font-size: 1.15rem;
        margin-bottom: .8rem;
        font-weight: 800;
    }

    .hz-card p {
        color: rgba(255,255,255,0.78);
        line-height: 1.7;
        font-size: .95rem;
    }

    .hz-section {
        margin-top: 3rem;
        margin-bottom: 2rem;
    }

    .hz-section-title {
        color: white;
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
    }

    .hz-section-text {
        color: rgba(255,255,255,0.78);
        line-height: 1.9;
        font-size: 1rem;
        max-width: 1100px;
    }

    .hz-pillars {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }

    .hz-pillar {
        border-radius: 24px;
        padding: 1.5rem;
        background:
            linear-gradient(180deg,
            rgba(8,19,31,0.96),
            rgba(10,38,71,0.82));
        border: 1px solid rgba(255,255,255,0.06);
    }

    .hz-pillar span {
        font-size: 2rem;
        display: block;
        margin-bottom: .8rem;
    }

    .hz-pillar h4 {
        color: white;
        margin-bottom: .6rem;
        font-size: 1.05rem;
        font-weight: 800;
    }

    .hz-pillar p {
        color: rgba(255,255,255,0.74);
        line-height: 1.65;
        font-size: .93rem;
    }

    .hz-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }

    .hz-metric {
        border-radius: 24px;
        padding: 1.6rem;
        text-align: center;
        background:
            linear-gradient(180deg,
            rgba(255,255,255,0.05),
            rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
    }

    .hz-metric h2 {
        color: #00ED64;
        font-size: 2rem;
        margin-bottom: .4rem;
        font-weight: 900;
    }

    .hz-metric p {
        color: rgba(255,255,255,0.74);
        font-size: .9rem;
        line-height: 1.4;
    }

    .hz-footer {
        margin-top: 4rem;
        padding: 2rem;
        border-radius: 28px;
        background:
            linear-gradient(135deg,
            rgba(0,237,100,0.12),
            rgba(10,38,71,0.45));
        border: 1px solid rgba(0,237,100,0.14);
    }

    .hz-footer h2 {
        color: white;
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 1rem;
    }

    .hz-footer p {
        color: rgba(255,255,255,0.82);
        line-height: 1.9;
        font-size: 1rem;
        max-width: 980px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown('<div class="hz-page">', unsafe_allow_html=True)

st.markdown(
    """
    <section class="hz-hero">

        <div class="hz-kicker">
            Horizonte Health Intelligence
        </div>

        <div class="hz-title">
            Inteligência em saúde pública,
            vigilância epidemiológica
            e transformação digital.
        </div>

        <div class="hz-subtitle">
            A Horizonte nasce para transformar bancos complexos,
            notificações fragmentadas e indicadores invisíveis
            em inteligência estratégica para municípios,
            estados e instituições de saúde.
            <br><br>
            Nossa missão é tornar os dados do SUS mais acessíveis,
            auditáveis, inteligentes e acionáveis.
        </div>

    </section>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="hz-grid">

        <div class="hz-card">
            <h3>📊 Painéis Inteligentes</h3>
            <p>
                Dashboards analíticos construídos para vigilância
                epidemiológica, sanitária e gestão estratégica em saúde.
            </p>
        </div>

        <div class="hz-card">
            <h3>🧠 Auditoria Automatizada</h3>
            <p>
                Identificação automática de inconsistências,
                duplicidades, baixa completude e padrões críticos.
            </p>
        </div>

        <div class="hz-card">
            <h3>🗂️ Leitura Universal de DBFs</h3>
            <p>
                Compatibilidade com bancos do SINAN e expansão
                futura para e-SUS, SIM, SINASC e outros sistemas.
            </p>
        </div>

        <div class="hz-card">
            <h3>🚨 Alertas Inteligentes</h3>
            <p>
                Detecção automática de tendências incomuns,
                aumento de casos e fragilidades operacionais.
            </p>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <section class="hz-section">

        <div class="hz-section-title">
            Uma plataforma construída para o SUS real.
        </div>

        <div class="hz-section-text">
            A Horizonte foi idealizada a partir das dores reais
            enfrentadas diariamente por equipes de vigilância em saúde.
            <br><br>
            Bancos incompletos, retrabalho operacional,
            dificuldade de visualizar tendências epidemiológicas,
            ausência de ferramentas modernas e pouco suporte
            analítico para tomada de decisão.
            <br><br>
            Em vez de apenas armazenar dados,
            a Horizonte interpreta, organiza,
            audita e transforma informação em inteligência.
        </div>

    </section>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="hz-pillars">

        <div class="hz-pillar">
            <span>🌎</span>
            <h4>Saúde baseada em evidências</h4>
            <p>
                Indicadores epidemiológicos mais confiáveis
                para fortalecer decisões técnicas e gestão pública.
            </p>
        </div>

        <div class="hz-pillar">
            <span>⚡</span>
            <h4>Velocidade operacional</h4>
            <p>
                Redução do tempo gasto em limpeza,
                análise e consolidação de bancos.
            </p>
        </div>

        <div class="hz-pillar">
            <span>🔒</span>
            <h4>Segurança e rastreabilidade</h4>
            <p>
                Histórico de uploads, auditorias automáticas
                e controle de acessos por perfil.
            </p>
        </div>

        <div class="hz-pillar">
            <span>🛰️</span>
            <h4>Escalabilidade</h4>
            <p>
                Estrutura preparada para expansão institucional,
                integração com bancos externos e uso multiusuário.
            </p>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <section class="hz-section">

        <div class="hz-section-title">
            Horizonte em números
        </div>

        <div class="hz-metrics">

            <div class="hz-metric">
                <h2>+70</h2>
                <p>Agravos compatíveis com o SINAN</p>
            </div>

            <div class="hz-metric">
                <h2>100%</h2>
                <p>Leitura automatizada de DBF</p>
            </div>

            <div class="hz-metric">
                <h2>∞</h2>
                <p>Possibilidades analíticas</p>
            </div>

            <div class="hz-metric">
                <h2>24/7</h2>
                <p>Disponibilidade em nuvem</p>
            </div>

        </div>

    </section>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <section class="hz-section">

        <div class="hz-section-title">
            Módulos atuais da plataforma
        </div>

        <div class="hz-section-text">
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
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"""
    <section class="hz-footer">

        <h2>
            O futuro da vigilância em saúde começa aqui.
        </h2>

        <p>
            Bem-vindo(a), <strong>{usuario.get("nome", usuario.get("usuario", "Usuário"))}</strong>.
            <br><br>
            A Horizonte não é apenas uma plataforma.
            É a construção de uma nova geração de inteligência
            aplicada à saúde pública brasileira.
            <br><br>
            Onde antes existiam planilhas esquecidas,
            agora surgem mapas, tendências,
            indicadores, alertas e decisões.
        </p>

    </section>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)
