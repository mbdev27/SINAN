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


st.title("🌌 Horizonte Health Intelligence")
st.caption("Inteligência em saúde pública, vigilância epidemiológica e transformação digital.")


st.markdown(
    """
A **Horizonte** nasce para transformar bancos complexos, notificações fragmentadas e indicadores invisíveis
em inteligência estratégica para municípios, estados e instituições de saúde.

Nossa missão é tornar os dados do SUS mais acessíveis, auditáveis, inteligentes e acionáveis.
"""
)


st.divider()

st.header("🚀 O que a plataforma entrega")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("📊 Painéis Inteligentes")
    st.write(
        "Dashboards analíticos construídos para vigilância epidemiológica, "
        "sanitária e gestão estratégica em saúde."
    )

with col2:
    st.subheader("🧠 Auditoria Automatizada")
    st.write(
        "Identificação automática de inconsistências, duplicidades, baixa "
        "completude e padrões críticos."
    )

with col3:
    st.subheader("🗂️ Leitura Universal de DBFs")
    st.write(
        "Compatibilidade com bancos do SINAN e expansão futura para e-SUS, "
        "SIM, SINASC e outros sistemas."
    )

with col4:
    st.subheader("🚨 Alertas Inteligentes")
    st.write(
        "Detecção automática de tendências incomuns, aumento de casos e "
        "fragilidades operacionais."
    )


st.divider()

st.header("🏛️ Uma plataforma construída para o SUS real")

st.markdown(
    """
A Horizonte foi idealizada a partir das dores reais enfrentadas diariamente por equipes de vigilância em saúde.

Bancos incompletos, retrabalho operacional, dificuldade de visualizar tendências epidemiológicas,
ausência de ferramentas modernas e pouco suporte analítico para tomada de decisão.

Em vez de apenas armazenar dados, a Horizonte interpreta, organiza, audita e transforma informação em inteligência.
"""
)


st.divider()

st.header("🧭 Pilares da Horizonte")

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.subheader("🌎 Evidência")
    st.write(
        "Indicadores epidemiológicos mais confiáveis para fortalecer decisões técnicas e gestão pública."
    )

with p2:
    st.subheader("⚡ Velocidade")
    st.write(
        "Redução do tempo gasto em limpeza, análise e consolidação de bancos."
    )

with p3:
    st.subheader("🔒 Segurança")
    st.write(
        "Histórico de uploads, auditorias automáticas e controle de acessos por perfil."
    )

with p4:
    st.subheader("🛰️ Escalabilidade")
    st.write(
        "Estrutura preparada para expansão institucional, integração com bancos externos e uso multiusuário."
    )


st.divider()

st.header("📈 Horizonte em números")

m1, m2, m3, m4 = st.columns(4)

m1.metric("+70", "Agravos compatíveis com o SINAN")
m2.metric("100%", "Leitura automatizada de DBF")
m3.metric("∞", "Possibilidades analíticas")
m4.metric("24/7", "Disponibilidade em nuvem")


st.divider()

st.header("🧩 Módulos atuais da plataforma")

st.markdown(
    """
- Painel Universal SINAN
- Auditoria inteligente de bancos
- Histórico de uploads
- Relatórios técnicos em PDF
- Painéis específicos por agravo
- Controle de usuários e permissões
- Indicadores de qualidade do banco
- Alertas epidemiológicos automatizados
- Exportação institucional de dados
"""
)


st.divider()

st.header("🌅 O futuro da vigilância em saúde começa aqui")

st.markdown(
    f"""
Bem-vindo(a), **{nome_usuario}**.

A Horizonte não é apenas uma plataforma.  
É a construção de uma nova geração de inteligência aplicada à saúde pública brasileira.

Onde antes existiam planilhas esquecidas, agora surgem mapas, tendências, indicadores, alertas e decisões.
"""
)

st.caption("Horizonte Health Intelligence • Soluções tecnológicas para saúde pública")
