import streamlit as st
import pandas as pd

from utils.auth import (
    exigir_login,
    obter_usuario_atual,
    carregar_usuarios,
    salvar_usuario_runtime,
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

st.sidebar.markdown("## 👤 Sessão")
st.sidebar.write(f"**Usuário:** {usuario_atual['nome']}")
st.sidebar.write(f"**Perfil:** {usuario_atual['perfil']}")

if st.sidebar.button("🚪 Sair do sistema", use_container_width=True):
    fazer_logout()
    st.rerun()


if usuario_atual["perfil"] != "Admin":
    st.error("Acesso restrito a administradores.")
    st.stop()


st.markdown(
    """
    <div class="hz-hero">
        <span class="hz-kicker">Horizonte Health Intelligence</span>
        <h1>Administração de Usuários</h1>
        <p>
            Gerencie perfis, verificações, bloqueios e acessos dos usuários
            da plataforma.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


usuarios = carregar_usuarios()

linhas = []

for login, dados in usuarios.items():
    linhas.append({
        "Usuário": login,
        "Nome": dados.get("nome", ""),
        "E-mail": dados.get("email", ""),
        "Perfil": dados.get("perfil", "Usuário"),
        "Verificado": dados.get("verificado", False),
        "Bloqueado": dados.get("bloqueado", False),
    })

df_usuarios = pd.DataFrame(linhas)

st.markdown("## 👥 Usuários cadastrados")

st.dataframe(
    df_usuarios,
    use_container_width=True,
    height=420
)


st.markdown("---")
st.markdown("## ⚙️ Editar usuário")

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

    perfil = st.selectbox(
        "Perfil",
        ["Admin", "Gestor", "Técnico", "Demo", "Usuário"],
        index=["Admin", "Gestor", "Técnico", "Demo", "Usuário"].index(
            dados_usuario.get("perfil", "Usuário")
            if dados_usuario.get("perfil", "Usuário") in ["Admin", "Gestor", "Técnico", "Demo", "Usuário"]
            else "Usuário"
        )
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


c1, c2, c3 = st.columns(3)

with c1:
    if st.button("💾 Salvar alterações", use_container_width=True):
        dados_usuario["nome"] = nome
        dados_usuario["email"] = email
        dados_usuario["perfil"] = perfil
        dados_usuario["verificado"] = verificado
        dados_usuario["bloqueado"] = bloqueado

        if nova_senha:
            dados_usuario["senha"] = nova_senha

        salvar_usuario_runtime(
            usuario_selecionado,
            dados_usuario
        )

        st.success("Usuário atualizado com sucesso.")
        st.rerun()

with c2:
    if st.button("🔓 Desbloquear e verificar", use_container_width=True):
        dados_usuario["bloqueado"] = False
        dados_usuario["verificado"] = True

        salvar_usuario_runtime(
            usuario_selecionado,
            dados_usuario
        )

        st.success("Usuário desbloqueado e verificado.")
        st.rerun()

with c3:
    if usuario_selecionado != usuario_atual["usuario"]:
        if st.button("🗑️ Excluir usuário", use_container_width=True):
            if "usuarios_runtime" in st.session_state:
                st.session_state["usuarios_runtime"].pop(usuario_selecionado, None)

            st.success("Usuário excluído.")
            st.rerun()
    else:
        st.info("Você não pode excluir o próprio usuário logado.")


st.markdown("---")
st.markdown("## ➕ Criar usuário manualmente")

with st.form("form_criar_usuario_admin", clear_on_submit=True):
    novo_nome = st.text_input("Nome completo")
    novo_email = st.text_input("E-mail")
    novo_usuario = st.text_input("Usuário")
    novo_perfil = st.selectbox(
        "Perfil do novo usuário",
        ["Admin", "Gestor", "Técnico", "Demo", "Usuário"],
        index=3
    )
    nova_senha_admin = st.text_input("Senha inicial", type="password")
    criar = st.form_submit_button("Criar usuário", use_container_width=True)

    if criar:
        if not novo_nome or not novo_email or not novo_usuario or not nova_senha_admin:
            st.error("Preencha todos os campos.")
        elif novo_usuario in usuarios:
            st.error("Este usuário já existe.")
        else:
            salvar_usuario_runtime(
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

            st.success("Usuário criado com sucesso.")
            st.rerun()


st.caption("Horizonte Health Intelligence • Administração de Usuários")
