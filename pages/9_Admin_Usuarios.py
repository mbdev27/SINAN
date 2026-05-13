import streamlit as st
import pandas as pd

from utils.auth import (
    exigir_login,
    obter_usuario_atual,
    carregar_usuarios,
    salvar_usuario_runtime,
    excluir_usuario_runtime,
    fazer_logout,
)

from utils.tema import (
    aplicar_tema_streamlit,
    aplicar_tema_plotly,
)


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Administração de Usuários",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

exigir_login()

aplicar_tema_streamlit(st)
aplicar_tema_plotly()


# ============================================================
# SESSÃO
# ============================================================

usuario_atual = obter_usuario_atual()

perfil_usuario = str(
    usuario_atual.get("perfil", "")
).strip().lower()


# ============================================================
# BLOQUEIO DE ACESSO
# ============================================================

if perfil_usuario != "admin":
    st.error("⛔ Esta área é restrita a administradores.")

    st.info(
        "Seu perfil atual não possui permissão para acessar "
        "a central administrativa da plataforma."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## 👤 Sessão")

st.sidebar.write(
    f"**Usuário:** {usuario_atual.get('nome', '—')}"
)

st.sidebar.write(
    f"**Perfil:** {usuario_atual.get('perfil', '—')}"
)

if st.sidebar.button(
    "🚪 Sair do sistema",
    use_container_width=True
):
    fazer_logout()
    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hz-hero">
        <span class="hz-kicker">
            Horizonte Health Intelligence
        </span>

        <h1>
            Administração de Usuários
        </h1>

        <p>
            Gerencie acessos, perfis, verificações,
            permissões e segurança da plataforma.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARREGAR USUÁRIOS
# ============================================================

usuarios = carregar_usuarios()

if not usuarios:
    st.warning("Nenhum usuário encontrado.")
    st.stop()


# ============================================================
# TABELA DE USUÁRIOS
# ============================================================

linhas = []

for login, dados in usuarios.items():
    linhas.append({
        "Usuário": login,
        "Nome": dados.get("nome", ""),
        "E-mail": dados.get("email", ""),
        "Perfil": dados.get("perfil", "Usuário"),
        "Verificado": (
            "✅ Sim"
            if dados.get("verificado", False)
            else "❌ Não"
        ),
        "Bloqueado": (
            "🔒 Sim"
            if dados.get("bloqueado", False)
            else "🔓 Não"
        ),
    })

df_usuarios = pd.DataFrame(linhas)

st.markdown("## 👥 Usuários cadastrados")

st.dataframe(
    df_usuarios,
    use_container_width=True,
    height=420
)


# ============================================================
# KPIs
# ============================================================

total_usuarios = len(df_usuarios)

usuarios_admin = len(
    df_usuarios[
        df_usuarios["Perfil"] == "Admin"
    ]
)

usuarios_bloqueados = len(
    df_usuarios[
        df_usuarios["Bloqueado"] == "🔒 Sim"
    ]
)

usuarios_nao_verificados = len(
    df_usuarios[
        df_usuarios["Verificado"] == "❌ Não"
    ]
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total de usuários", total_usuarios)
k2.metric("Administradores", usuarios_admin)
k3.metric("Bloqueados", usuarios_bloqueados)
k4.metric("Não verificados", usuarios_nao_verificados)


# ============================================================
# EDITAR USUÁRIO
# ============================================================

st.markdown("---")
st.markdown("## ⚙️ Editar usuário")

lista_usuarios = list(usuarios.keys())

usuario_selecionado = st.selectbox(
    "Selecione o usuário",
    lista_usuarios
)

dados_usuario = dict(
    usuarios[usuario_selecionado]
)

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

    perfil_atual = dados_usuario.get(
        "perfil",
        "Usuário"
    )

    if perfil_atual not in perfis_disponiveis:
        perfil_atual = "Usuário"

    perfil = st.selectbox(
        "Perfil",
        perfis_disponiveis,
        index=perfis_disponiveis.index(
            perfil_atual
        )
    )

with col2:
    verificado = st.checkbox(
        "E-mail verificado",
        value=bool(
            dados_usuario.get(
                "verificado",
                False
            )
        )
    )

    bloqueado = st.checkbox(
        "Usuário bloqueado",
        value=bool(
            dados_usuario.get(
                "bloqueado",
                False
            )
        )
    )

    nova_senha = st.text_input(
        "Nova senha manual",
        type="password",
        help=(
            "Preencha apenas se quiser "
            "alterar a senha."
        )
    )


# ============================================================
# BOTÕES DE AÇÃO
# ============================================================

b1, b2, b3 = st.columns(3)

with b1:
    if st.button(
        "💾 Salvar alterações",
        use_container_width=True
    ):
        dados_usuario["nome"] = nome
        dados_usuario["email"] = email
        dados_usuario["perfil"] = perfil
        dados_usuario["verificado"] = verificado
        dados_usuario["bloqueado"] = bloqueado

        if nova_senha:
            dados_usuario["senha"] = nova_senha

        ok = salvar_usuario_runtime(
            usuario_selecionado,
            dados_usuario
        )

        if ok:
            st.success(
                "Usuário atualizado com sucesso."
            )
            st.rerun()
        else:
            st.error(
                "Não foi possível salvar o usuário."
            )

with b2:
    if st.button(
        "🔓 Desbloquear e verificar",
        use_container_width=True
    ):
        dados_usuario["bloqueado"] = False
        dados_usuario["verificado"] = True

        ok = salvar_usuario_runtime(
            usuario_selecionado,
            dados_usuario
        )

        if ok:
            st.success(
                "Usuário desbloqueado e verificado."
            )
            st.rerun()
        else:
            st.error(
                "Não foi possível atualizar o usuário."
            )

with b3:
    if usuario_selecionado != usuario_atual["usuario"]:
        if st.button(
            "🗑️ Excluir usuário",
            use_container_width=True
        ):
            ok = excluir_usuario_runtime(
                usuario_selecionado
            )

            if ok:
                st.success("Usuário excluído.")
                st.rerun()
            else:
                st.warning(
                    "Este usuário não pôde ser excluído."
                )
    else:
        st.info(
            "Você não pode excluir "
            "o próprio usuário logado."
        )


# ============================================================
# CRIAR USUÁRIO MANUAL
# ============================================================

st.markdown("---")
st.markdown("## ➕ Criar usuário manualmente")

with st.form(
    "form_criar_usuario_admin",
    clear_on_submit=True
):
    novo_nome = st.text_input(
        "Nome completo"
    )

    novo_email = st.text_input(
        "E-mail"
    )

    novo_usuario = st.text_input(
        "Usuário"
    )

    novo_perfil = st.selectbox(
        "Perfil do novo usuário",
        [
            "Admin",
            "Gestor",
            "Técnico",
            "Demo",
            "Usuário",
        ],
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

        novo_usuario = str(
            novo_usuario
        ).strip()

        if (
            not novo_nome
            or not novo_email
            or not novo_usuario
            or not nova_senha_admin
        ):
            st.error(
                "Preencha todos os campos."
            )

        elif "@" not in novo_email:
            st.error(
                "Informe um e-mail válido."
            )

        elif novo_usuario in usuarios_existentes:
            st.error(
                "Este usuário já existe."
            )

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
                st.success(
                    "Usuário criado com sucesso."
                )
                st.rerun()
            else:
                st.error(
                    "Não foi possível criar o usuário."
                )


# ============================================================
# EXPORTAÇÃO
# ============================================================

st.markdown("---")
st.markdown("## 📥 Exportar usuários")

csv_usuarios = df_usuarios.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "📄 Baixar lista de usuários",
    data=csv_usuarios,
    file_name="usuarios_horizonte.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# RODAPÉ
# ============================================================

st.caption(
    "Horizonte Health Intelligence • "
    "Central Administrativa de Usuários"
)
