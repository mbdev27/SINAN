import streamlit as st
from pathlib import Path


USUARIOS_PADRAO = {
    "admin": {
        "senha": "admin123",
        "nome": "Administrador",
        "perfil": "Admin",
        "email": "admin@horizonte.local"
    },
    "demo": {
        "senha": "demo123",
        "nome": "Usuário Demonstração",
        "perfil": "Demo",
        "email": "demo@horizonte.local"
    }
}


def carregar_usuarios():
    if "usuarios_runtime" not in st.session_state:
        st.session_state["usuarios_runtime"] = USUARIOS_PADRAO.copy()

    try:
        if "usuarios" in st.secrets:
            usuarios = {}
            for usuario, dados in st.secrets["usuarios"].items():
                usuarios[usuario] = dict(dados)
            usuarios.update(st.session_state["usuarios_runtime"])
            return usuarios
    except Exception:
        pass

    return st.session_state["usuarios_runtime"]


def salvar_usuario_runtime(usuario, dados):
    if "usuarios_runtime" not in st.session_state:
        st.session_state["usuarios_runtime"] = USUARIOS_PADRAO.copy()

    st.session_state["usuarios_runtime"][usuario] = dados


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
    usuario = str(usuario).strip()

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
        "abrir_painel_generico",
    ]

    for chave in chaves:
        if chave in st.session_state:
            del st.session_state[chave]


def css_login():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] {
            visibility: hidden !important;
            width: 0 !important;
        }

        .block-container {
            max-width: 1180px !important;
            padding-top: 3rem !important;
        }

        .hz-login-shell {
            min-height: 88vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .hz-login-card {
            width: min(100%, 460px);
            background: rgba(8, 19, 31, 0.82);
            border: 1px solid rgba(225, 232, 237, 0.16);
            border-radius: 28px;
            padding: 34px;
            box-shadow: 0 28px 70px rgba(0,0,0,0.38);
            backdrop-filter: blur(14px);
        }

        .hz-login-logo {
            display: flex;
            justify-content: center;
            margin-bottom: 22px;
        }

        .hz-login-title {
            text-align: center;
            color: #FFFFFF !important;
            font-size: 1.55rem;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .hz-login-subtitle {
            text-align: center;
            color: #E1E8ED !important;
            line-height: 1.6;
            margin-bottom: 26px;
        }

        .hz-login-actions {
            display: flex;
            gap: 10px;
            margin-top: 14px;
        }

        .hz-login-note {
            text-align: center;
            color: #94A3B8 !important;
            font-size: 0.85rem;
            margin-top: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def exibir_logo():
    caminhos = [
        Path("assets/horizonte_logo.png"),
        Path("assets/logo.png"),
        Path("horizonte_logo.png"),
    ]

    for caminho in caminhos:
        if caminho.exists():
            st.image(str(caminho), width=210)
            return

    st.markdown(
        """
        <div style="text-align:center;">
            <div style="
                width:120px;height:120px;margin:auto;border-radius:28px;
                background:linear-gradient(135deg,#0A2647,#00ED64);
                display:flex;align-items:center;justify-content:center;
                color:white;font-size:64px;font-weight:900;
                border:1px solid rgba(255,255,255,.25);
            ">H</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def tela_login():
    css_login()

    if "auth_tela" not in st.session_state:
        st.session_state["auth_tela"] = "login"

    st.markdown('<div class="hz-login-shell"><div class="hz-login-card">', unsafe_allow_html=True)

    st.markdown('<div class="hz-login-logo">', unsafe_allow_html=True)
    exibir_logo()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["auth_tela"] == "login":
        st.markdown('<div class="hz-login-title">Horizonte Health Intelligence</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-login-subtitle">Plataforma segura para leitura de bancos DBF do SINAN, auditoria epidemiológica e apoio à decisão em Vigilância em Saúde.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_login", clear_on_submit=False):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                if fazer_login(usuario, senha):
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Criar cadastro", use_container_width=True):
                st.session_state["auth_tela"] = "cadastro"
                st.rerun()

        with c2:
            if st.button("Redefinir senha", use_container_width=True):
                st.session_state["auth_tela"] = "redefinir"
                st.rerun()

        st.markdown(
            '<div class="hz-login-note">Ambiente de testes Horizonte • acesso controlado</div>',
            unsafe_allow_html=True
        )

    elif st.session_state["auth_tela"] == "cadastro":
        st.markdown('<div class="hz-login-title">Criar cadastro</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-login-subtitle">Solicite ou crie um acesso para ambiente de testes da plataforma.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_cadastro", clear_on_submit=False):
            nome = st.text_input("Nome completo")
            email = st.text_input("E-mail institucional")
            usuario = st.text_input("Nome de usuário")
            senha = st.text_input("Senha", type="password")
            confirmar = st.text_input("Confirmar senha", type="password")
            cadastrar = st.form_submit_button("Cadastrar", use_container_width=True)

            if cadastrar:
                usuarios = carregar_usuarios()
                usuario = str(usuario).strip()

                if not nome or not email or not usuario or not senha:
                    st.error("Preencha todos os campos.")
                elif usuario in usuarios:
                    st.error("Este usuário já existe.")
                elif senha != confirmar:
                    st.error("As senhas não conferem.")
                else:
                    salvar_usuario_runtime(
                        usuario,
                        {
                            "senha": senha,
                            "nome": nome,
                            "perfil": "Demo",
                            "email": email,
                        }
                    )
                    st.success("Cadastro criado para este ambiente de testes. Faça login para continuar.")
                    st.session_state["auth_tela"] = "login"
                    st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

    elif st.session_state["auth_tela"] == "redefinir":
        st.markdown('<div class="hz-login-title">Redefinir senha</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-login-subtitle">Informe seu usuário e uma nova senha para o ambiente de testes.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_redefinir", clear_on_submit=False):
            usuario = st.text_input("Usuário")
            nova_senha = st.text_input("Nova senha", type="password")
            confirmar = st.text_input("Confirmar nova senha", type="password")
            redefinir = st.form_submit_button("Salvar nova senha", use_container_width=True)

            if redefinir:
                usuarios = carregar_usuarios()
                usuario = str(usuario).strip()

                if usuario not in usuarios:
                    st.error("Usuário não encontrado.")
                elif not nova_senha:
                    st.error("Informe uma nova senha.")
                elif nova_senha != confirmar:
                    st.error("As senhas não conferem.")
                else:
                    dados = dict(usuarios[usuario])
                    dados["senha"] = nova_senha
                    salvar_usuario_runtime(usuario, dados)
                    st.success("Senha redefinida neste ambiente de testes.")
                    st.session_state["auth_tela"] = "login"
                    st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)


def exigir_login():
    if not usuario_logado():
        tela_login()
        st.stop()
