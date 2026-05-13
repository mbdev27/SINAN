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
    page_title="Configurações",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

exigir_login()
aplicar_tema_streamlit(st)
aplicar_tema_plotly()


usuario_atual = obter_usuario_atual()
login_atual = usuario_atual.get("usuario")
perfil_atual = str(usuario_atual.get("perfil", "")).strip()
eh_admin = perfil_atual.lower() == "admin"


st.sidebar.markdown("## 👤 Sessão")
st.sidebar.write(f"**Usuário:** {usuario_atual.get('nome', '—')}")
st.sidebar.write(f"**Perfil:** {usuario_atual.get('perfil', '—')}")

if st.sidebar.button("🚪 Sair do sistema", use_container_width=True):
    fazer_logout()
    st.rerun()


st.markdown(
    dedent("""
    <style>
    .config-hero {
        background: linear-gradient(135deg, rgba(10,38,71,.96), rgba(6,78,59,.92));
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 28px;
        padding: 38px;
        margin-bottom: 28px;
        box-shadow: 0 24px 70px rgba(0,0,0,.28);
    }

    .config-kicker {
        color: #00ED64 !important;
        font-size: .78rem;
        font-weight: 900;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: 14px;
        display: block;
    }

    .config-title {
        color: #FFFFFF !important;
        font-size: clamp(2rem, 4vw, 3.6rem);
        font-weight: 900;
        line-height: 1.05;
        letter-spacing: -.04em;
        margin-bottom: 16px;
    }

    .config-subtitle {
        color: #E1E8ED !important;
        font-size: 1.05rem;
        line-height: 1.7;
        max-width: 820px;
    }

    .config-section {
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
    <div class="config-hero">
        <span class="config-kicker">Horizonte Health Intelligence</span>
        <div class="config-title">Configurações</div>
        <div class="config-subtitle">
            Gerencie sua conta, dados cadastrais, senha e preferências de acesso.
            Administradores também podem gerenciar os usuários da plataforma.
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


usuarios = carregar_usuarios()

if login_atual not in usuarios:
    st.error("Usuário atual não localizado na base.")
    st.stop()


dados_meu_usuario = dict(usuarios[login_atual])


st.markdown('<div class="config-section">👤 Minha conta</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    novo_nome = st.text_input(
        "Nome",
        value=dados_meu_usuario.get("nome", "")
    )

    novo_email = st.text_input(
        "E-mail",
        value=dados_meu_usuario.get("email", "")
    )

with col2:
    st.text_input(
        "Usuário",
        value=login_atual,
        disabled=True
    )

    st.text_input(
        "Perfil",
        value=dados_meu_usuario.get("perfil", "Usuário"),
        disabled=True
    )


nova_senha = st.text_input(
    "Nova senha",
    type="password",
    help="Preencha apenas se quiser alterar sua senha."
)

confirmar_senha = st.text_input(
    "Confirmar nova senha",
    type="password"
)


if st.button("💾 Salvar minhas alterações", use_container_width=True):
    if not novo_nome or not novo_email:
        st.error("Nome e e-mail são obrigatórios.")

    elif "@" not in novo_email:
        st.error("Informe um e-mail válido.")

    elif nova_senha and nova_senha != confirmar_senha:
        st.error("As senhas não conferem.")

    else:
        dados_meu_usuario["nome"] = novo_nome
        dados_meu_usuario["email"] = novo_email

        if nova_senha:
            dados_meu_usuario["senha"] = nova_senha

        ok = salvar_usuario_runtime(
            login_atual,
            dados_meu_usuario
        )

        if ok:
            st.session_state["nome_usuario"] = novo_nome
            st.success("Dados atualizados com sucesso.")
            st.rerun()
        else:
            st.error("Não foi possível salvar as alterações.")


if not eh_admin:
    st.caption("Horizonte Health Intelligence • Configurações do Usuário")
    st.stop()


st.markdown("---")
st.markdown('<div class="config-section">🛡️ Administração de usuários</div>', unsafe_allow_html=True)


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


k1, k2, k3, k4 = st.columns(4)

k1.metric("Total de usuários", len(df_usuarios))
k2.metric("Administradores", len(df_usuarios[df_usuarios["Perfil"] == "Admin"]))
k3.metric("Bloqueados", len(df_usuarios[df_usuarios["Bloqueado"] == "🔒 Sim"]))
k4.metric("Não verificados", len(df_usuarios[df_usuarios["Verificado"] == "❌ Não"]))


st.dataframe(
    df_usuarios,
    use_container_width=True,
    height=420
)


st.markdown("---")
st.subheader("⚙️ Editar usuário")

lista_usuarios = list(usuarios.keys())

usuario_selecionado = st.selectbox(
    "Selecione o usuário",
    lista_usuarios
)

dados_usuario = dict(usuarios[usuario_selecionado])

col1, col2 = st.columns(2)

with col1:
    nome = st.text_input(
        "Nome do usuário selecionado",
        value=dados_usuario.get("nome", "")
    )

    email = st.text_input(
        "E-mail do usuário selecionado",
        value=dados_usuario.get("email", "")
    )

    perfis = ["Admin", "Gestor", "Técnico", "Demo", "Usuário"]

    perfil = dados_usuario.get("perfil", "Usuário")

    if perfil not in perfis:
        perfil = "Usuário"

    novo_perfil = st.selectbox(
        "Perfil",
        perfis,
        index=perfis.index(perfil)
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

    senha_manual = st.text_input(
        "Nova senha manual",
        type="password"
    )


b1, b2, b3 = st.columns(3)

with b1:
    if st.button("💾 Salvar usuário", use_container_width=True):
        dados_usuario["nome"] = nome
        dados_usuario["email"] = email
        dados_usuario["perfil"] = novo_perfil
        dados_usuario["verificado"] = verificado
        dados_usuario["bloqueado"] = bloqueado

        if senha_manual:
            dados_usuario["senha"] = senha_manual

        ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

        if ok:
            st.success("Usuário atualizado.")
            st.rerun()
        else:
            st.error("Não foi possível salvar.")

with b2:
    if st.button("🔓 Desbloquear e verificar", use_container_width=True):
        dados_usuario["bloqueado"] = False
        dados_usuario["verificado"] = True

        ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

        if ok:
            st.success("Usuário desbloqueado e verificado.")
            st.rerun()
        else:
            st.error("Não foi possível atualizar.")

with b3:
    if usuario_selecionado != login_atual:
        if st.button("🗑️ Excluir usuário", use_container_width=True):
            ok = excluir_usuario_runtime(usuario_selecionado)

            if ok:
                st.success("Usuário excluído.")
                st.rerun()
            else:
                st.warning("Não foi possível excluir.")
    else:
        st.info("Você não pode excluir o próprio usuário.")


st.markdown("---")
st.subheader("➕ Criar usuário manualmente")

with st.form("form_criar_usuario_admin", clear_on_submit=True):
    novo_nome_admin = st.text_input("Nome completo")
    novo_email_admin = st.text_input("E-mail")
    novo_usuario_admin = st.text_input("Usuário")
    novo_perfil_admin = st.selectbox(
        "Perfil",
        ["Admin", "Gestor", "Técnico", "Demo", "Usuário"],
        index=3
    )
    senha_inicial = st.text_input("Senha inicial", type="password")

    criar = st.form_submit_button("Criar usuário", use_container_width=True)

    if criar:
        usuarios_existentes = carregar_usuarios()
        novo_usuario_admin = str(novo_usuario_admin).strip()

        if not novo_nome_admin or not novo_email_admin or not novo_usuario_admin or not senha_inicial:
            st.error("Preencha todos os campos.")

        elif "@" not in novo_email_admin:
            st.error("Informe um e-mail válido.")

        elif novo_usuario_admin in usuarios_existentes:
            st.error("Este usuário já existe.")

        else:
            ok = salvar_usuario_runtime(
                novo_usuario_admin,
                {
                    "senha": senha_inicial,
                    "nome": novo_nome_admin,
                    "perfil": novo_perfil_admin,
                    "email": novo_email_admin,
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
st.subheader("📥 Exportar usuários")

csv_usuarios = df_usuarios.to_csv(index=False).encode("utf-8")

st.download_button(
    "📄 Baixar lista de usuários",
    data=csv_usuarios,
    file_name="usuarios_horizonte.csv",
    mime="text/csv",
    use_container_width=True
)


st.caption("Horizonte Health Intelligence • Configurações")
