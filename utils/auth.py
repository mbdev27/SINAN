import streamlit as st


USUARIOS_PADRAO = {
    "admin": {
        "senha": "admin123",
        "nome": "Administrador",
        "perfil": "Admin"
    },
    "demo": {
        "senha": "demo123",
        "nome": "Usuário Demonstração",
        "perfil": "Demo"
    }
}


def carregar_usuarios():
    try:
        if "usuarios" in st.secrets:
            return st.secrets["usuarios"]
    except Exception:
        pass

    return USUARIOS_PADRAO


def usuario_logado():
    return st.session_state.get("autenticado", False)


def obter_usuario_atual():
    return {
        "usuario": st.session_state.get("usuario"),
        "nome": st.session_state.get("nome_usuario"),
        "perfil": st.session_state.get("perfil_usuario"),
    }


def fazer_login(usuario, senha):
    usuarios = carregar_usuarios()

    if usuario in usuarios:
        dados = usuarios[usuario]

        if senha == dados.get("senha"):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.session_state["nome_usuario"] = dados.get("nome", usuario)
            st.session_state["perfil_usuario"] = dados.get("perfil", "Usuário")
            return True

    return False


def fazer_logout():
    chaves = [
        "autenticado",
        "usuario",
        "nome_usuario",
        "perfil_usuario",
        "df_sinan_atual",
        "df_sinan_publico",
        "agravo_sinan_atual",
        "ficha_sinan_atual",
        "abrir_painel_acidente_trabalho",
        "abrir_painel_violencia",
        "abrir_painel_arbovirose",
        "abrir_painel_intoxicacao",
        "abrir_painel_leptospirose",
        "abrir_painel_toxoplasmose",
    ]

    for chave in chaves:
        if chave in st.session_state:
            del st.session_state[chave]


def tela_login():
    st.markdown("""
    <div class="mb-header">
        <h1>🔐 MB Health Intelligence</h1>
        <p>
            Acesso restrito à plataforma de inteligência epidemiológica.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("## Entrar no sistema")

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):
            if fazer_login(usuario, senha):
                st.success("Login realizado com sucesso.")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

        st.caption("Usuário de teste: admin | Senha: admin123")


def exigir_login():
    if not usuario_logado():
        tela_login()
        st.stop()
