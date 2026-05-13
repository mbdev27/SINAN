import html
from textwrap import dedent

import pandas as pd
import streamlit as st

from utils.auth import (
    exigir_login,
    obter_usuario_atual,
    carregar_usuarios,
    salvar_usuario_runtime,
    excluir_usuario_runtime,
    fazer_logout,
)

from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly


st.set_page_config(
    page_title="Administração de Usuários",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

exigir_login()
aplicar_tema_streamlit(st)
aplicar_tema_plotly()


usuario_atual = obter_usuario_atual()
perfil_usuario = str(usuario_atual.get("perfil", "")).strip().lower()

if perfil_usuario != "admin":
    st.error("⛔ Esta área é restrita a administradores.")
    st.stop()


st.sidebar.markdown("## 👤 Sessão")
st.sidebar.write(f"**Usuário:** {usuario_atual.get('nome', '—')}")
st.sidebar.write(f"**Perfil:** {usuario_atual.get('perfil', '—')}")

if st.sidebar.button("🚪 Sair do sistema", use_container_width=True):
    fazer_logout()
    st.rerun()


st.markdown(
    dedent("""
    <style>
    .admin-hero {
        background: linear-gradient(135deg, rgba(10,38,71,.96), rgba(6,78,59,.92));
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 28px;
        padding: 38px;
        margin-bottom: 28px;
        box-shadow: 0 24px 70px rgba(0,0,0,.28);
    }

    .admin-kicker {
        color: #00ED64 !important;
        font-size: .78rem;
        font-weight: 900;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: 14px;
        display: block;
    }

    .admin-title {
        color: #FFFFFF !important;
        font-size: clamp(2rem, 4vw, 3.6rem);
        font-weight: 900;
        line-height: 1.05;
        letter-spacing: -.04em;
        margin-bottom: 16px;
    }

    .admin-subtitle {
        color: #E1E8ED !important;
        font-size: 1.05rem;
        line-height: 1.7;
        max-width: 820px;
    }

    .admin-kpi-card {
        background: linear-gradient(180deg, rgba(8,19,31,.86), rgba(5,15,25,.92));
        border: 1px solid rgba(255,255,255,.10);
        border-left: 6px solid #00ED64;
        border-radius: 22px;
        padding: 22px;
        min-height: 128px;
        box-shadow: 0 18px 45px rgba(0,0,0,.24);
    }

    .admin-kpi-label {
        color: #C9D5DF !important;
        font-size: .92rem;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .admin-kpi-value {
        color: #FFFFFF !important;
        font-size: 2.4rem;
        font-weight: 900;
        line-height: 1;
    }

    .admin-section {
        margin-top: 24px;
        margin-bottom: 10px;
        color: #FFFFFF !important;
        font-size: 1.55rem;
        font-weight: 900;
    }
    </style>
    """),
    unsafe_allow_html=True
)


st.markdown(
    dedent("""
    <div class="admin-hero">
        <span class="admin-kicker">Horizonte Health Intelligence</span>
        <div class="admin-title">Administração de Usuários</div>
        <div class="admin-subtitle">
            Gerencie acessos, perfis, verificações, bloqueios e segurança da plataforma.
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


usuarios = carregar_usuarios()

if not usuarios:
    st.warning("Nenhum usuário encontrado.")
    st.stop()


linhas = []

for login, dados in usuarios.items():
    linhas.append({
        "Usuário": login,
        "Nome": dados.get("nome", ""),
        "E-mail": dados.get("email", ""),
        "Perfil": dados.get("perfil", "Usuário"),
        "Verificado": "✅ Sim" if dados.get("verificado", False) else "❌ Não",
        "Bloqueado": "🔒 Sim" if dados.get("bloqueado", False) else "🔓 Não",
    })

df_usuarios = pd.DataFrame(linhas)

total_usuarios = len(df_usuarios)
usuarios_admin = len(df_usuarios[df_usuarios["Perfil"] == "Admin"])
usuarios_bloqueados = len(df_usuarios[df_usuarios["Bloqueado"] == "🔒 Sim"])
usuarios_nao_verificados = len(df_usuarios[df_usuarios["Verificado"] == "❌ Não"])


def kpi_card(label, value):
    st.markdown(
        dedent(f"""
        <div class="admin-kpi-card">
            <div class="admin-kpi-label">{html.escape(str(label))}</div>
            <div class="admin-kpi-value">{html.escape(str(value))}</div>
        </div>
        """),
        unsafe_allow_html=True
    )


k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card("Total de usuários", total_usuarios)

with k2:
    kpi_card("Administradores", usuarios_admin)

with k3:
    kpi_card("Bloqueados", usuarios_bloqueados)

with k4:
    kpi_card("Não verificados", usuarios_nao_verificados)


st.markdown('<div class="admin-section">👥 Usuários cadastrados</div>', unsafe_allow_html=True)

st.dataframe(
    df_usuarios,
    use_container_width=True,
    height=420
)


st.markdown("---")
st.markdown('<div class="admin-section">⚙️ Editar usuário</div>', unsafe_allow_html=True)

lista_usuarios = list(usuarios.keys())

usuario_selecionado = st.selectbox(
    "Selecione o usuário",
    lista_usuarios
)

dados_usuario = dict(usuarios[usuario_selecionado])

col1, col2 = st.columns(2)

with col1:
    nome = st.text_input(
        "Nome",
        value=dados_usuario.get("nome", "")
    )

    email = st.text_input(
        "E-mail",
        value=dados_usuario.get("email", "")
    )

    perfis_disponiveis = [
        "Admin",
        "Gestor",
        "Técnico",
        "Demo",
        "Usuário",
    ]

    perfil_atual = dados_usuario.get("perfil", "Usuário")

    if perfil_atual not in perfis_disponiveis:
        perfil_atual = "Usuário"

    perfil = st.selectbox(
        "Perfil",
        perfis_disponiveis,
        index=perfis_disponiveis.index(perfil_atual)
    )

with col2:
    verificado = st.checkbox(
        "E-mail verificado",
        value=bool(dados_usuario.get("verificado", False))
    )

    bloqueado = st.checkbox(
        "Usuário bloqueado",
        value=bool(dados_usuario.get("bloqueado", False))
    )

    nova_senha = st.text_input(
        "Nova senha manual",
        type="password",
        help="Preencha apenas se quiser alterar a senha."
    )


b1, b2, b3 = st.columns(3)

with b1:
    if st.button("💾 Salvar alterações", use_container_width=True):
        dados_usuario["nome"] = nome
        dados_usuario["email"] = email
        dados_usuario["perfil"] = perfil
        dados_usuario["verificado"] = verificado
        dados_usuario["bloqueado"] = bloqueado

        if nova_senha:
            dados_usuario["senha"] = nova_senha

        ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

        if ok:
            st.success("Usuário atualizado com sucesso.")
            st.rerun()
        else:
            st.error("Não foi possível salvar o usuário.")

with b2:
    if st.button("🔓 Desbloquear e verificar", use_container_width=True):
        dados_usuario["bloqueado"] = False
        dados_usuario["verificado"] = True

        ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

        if ok:
            st.success("Usuário desbloqueado e verificado.")
            st.rerun()
        else:
            st.error("Não foi possível atualizar o usuário.")

with b3:
    if usuario_selecionado != usuario_atual.get("usuario"):
        if st.button("🗑️ Excluir usuário", use_container_width=True):
            ok = excluir_usuario_runtime(usuario_selecionado)

            if ok:
                st.success("Usuário excluído.")
                st.rerun()
            else:
                st.warning("Não foi possível excluir este usuário.")
    else:
        st.info("Você não pode excluir o próprio usuário logado.")


st.markdown("---")
st.markdown('<div class="admin-section">➕ Criar usuário manualmente</div>', unsafe_allow_html=True)

with st.form("form_criar_usuario_admin", clear_on_submit=True):
    novo_nome = st.text_input("Nome completo")
    novo_email = st.text_input("E-mail")
    novo_usuario = st.text_input("Usuário")

    novo_perfil = st.selectbox(
        "Perfil",
        ["Admin", "Gestor", "Técnico", "Demo", "Usuário"],
        index=3
    )

    nova_senha_admin = st.text_input(
        "Senha inicial",
        type="password"
    )

    criar = st.form_submit_button(
        "Criar usuário",
        use_container_width=True
    )

    if criar:
        usuarios_existentes = carregar_usuarios()
        novo_usuario = str(novo_usuario).strip()

        if not novo_nome or not novo_email or not novo_usuario or not nova_senha_admin:
            st.error("Preencha todos os campos.")

        elif "@" not in novo_email:
            st.error("Informe um e-mail válido.")

        elif novo_usuario in usuarios_existentes:
            st.error("Este usuário já existe.")

        else:
            ok = salvar_usuario_runtime(
                novo_usuario,
                {
                    "senha": nova_senha_admin,
                    "nome": novo_nome,
                    "perfil": novo_perfil,
                    "email": novo_email,
                    "verificado": True,
                    "bloqueado": False,
                }
            )

            if ok:
                st.success("Usuário criado com sucesso.")
                st.rerun()
            else:
                st.error("Não foi possível criar o usuário.")


st.markdown("---")
st.markdown('<div class="admin-section">📥 Exportar usuários</div>', unsafe_allow_html=True)

csv_usuarios = df_usuarios.to_csv(index=False).encode("utf-8")

st.download_button(
    "📄 Baixar lista de usuários",
    data=csv_usuarios,
    file_name="usuarios_horizonte.csv",
    mime="text/csv",
    use_container_width=True
)


st.caption("Horizonte Health Intelligence • Central Administrativa")
