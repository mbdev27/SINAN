import base64
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


def imagem_base64(caminho):
    try:
        with open(caminho, "rb") as img:
            return base64.b64encode(img.read()).decode()
    except Exception:
        return None


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
    fundo = None

    for caminho in [
        "assets/digital_presence.png",
        "digital_presence.png",
    ]:
        if Path(caminho).exists():
            fundo = imagem_base64(caminho)
            break

    background_css = (
        f"""
        background:
            linear-gradient(90deg, rgba(7,24,39,0.96) 0%, rgba(7,24,39,0.82) 45%, rgba(7,24,39,0.45) 100%),
            url("data:image/png;base64,{fundo}");
        background-size: cover;
        background-position: center;
        """
        if fundo
        else """
        background:
            radial-gradient(circle at 20% 20%, rgba(0,237,100,0.18), transparent 34%),
            linear-gradient(135deg, #071827 0%, #0A2647 58%, #064E3B 100%);
        """
    )

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {{
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
        }}

        .block-container {{
            max-width: 100% !important;
            padding: 0 !important;
        }}

        [data-testid="stAppViewContainer"] {{
            {background_css}
            min-height: 100vh;
        }}

        .hz-login-page {{
            min-height: 100vh;
            display: grid;
            grid-template-columns: minmax(340px, 520px) 1fr;
            align-items: center;
            padding: 56px clamp(24px, 5vw, 88px);
            gap: 48px;
        }}

        .hz-login-card {{
            width: 100%;
            background: rgba(8, 19, 31, 0.78);
            border: 1px solid rgba(225, 232, 237, 0.18);
            border-radius: 30px;
            padding: 34px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.48);
            backdrop-filter: blur(18px);
        }}

        .hz-logo-wrap {{
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }}

        .hz-title {{
            text-align: center;
            color: #FFFFFF !important;
            font-size: 1.8rem;
            font-weight: 900;
            margin-bottom: 8px;
            letter-spacing: -0.03em;
        }}

        .hz-subtitle {{
            text-align: center;
            color: #E1E8ED !important;
            line-height: 1.65;
            margin-bottom: 28px;
            font-size: 0.98rem;
        }}

        .hz-side-copy {{
            max-width: 560px;
        }}

        .hz-kicker-login {{
            color: #00ED64 !important;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-size: 0.8rem;
            margin-bottom: 16px;
        }}

        .hz-side-copy h1 {{
            color: #FFFFFF !important;
            font-size: clamp(2.4rem, 5vw, 5rem);
            line-height: 1.02;
            font-weight: 900;
            letter-spacing: -0.05em;
            margin-bottom: 22px;
        }}

        .hz-side-copy p {{
            color: #E1E8ED !important;
            font-size: 1.08rem;
            line-height: 1.8;
            max-width: 520px;
        }}

        .hz-pills {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 26px;
        }}

        .hz-pill {{
            color: #E1E8ED !important;
            border: 1px solid rgba(0,237,100,0.35);
            background: rgba(0,237,100,0.08);
            padding: 9px 13px;
            border-radius: 999px;
            font-size: 0.86rem;
            font-weight: 700;
        }}

        input {{
            background: rgba(248,250,252,0.96) !important;
            color: #101820 !important;
            border-radius: 14px !important;
        }}

        label {{
            color: #F8FAFC !important;
            font-weight: 700 !important;
        }}

        button {{
            background: #00ED64 !important;
            color: #101820 !important;
            border: 1px solid #00ED64 !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
            min-height: 48px !important;
        }}

        button:hover {{
            filter: brightness(1.05);
            transform: translateY(-1px);
            box-shadow: 0px 14px 36px rgba(0,237,100,0.32);
        }}

        .hz-login-note {{
            text-align: center;
            color: #94A3B8 !important;
            font-size: 0.82rem;
            margin-top: 18px;
        }}

        @media (max-width: 900px) {{
            .hz-login-page {{
                grid-template-columns: 1fr;
                padding: 32px 18px;
            }}

            .hz-side-copy {{
                display: none;
            }}

            .hz-login-card {{
                margin: 0 auto;
                max-width: 460px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def exibir_logo():
    for caminho in [
        "assets/horizonte_logo.png",
        "horizonte_logo.png",
        "assets/logo.png",
    ]:
        if Path(caminho).exists():
            st.image(caminho, width=220)
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

    st.markdown('<div class="hz-login-page">', unsafe_allow_html=True)

    st.markdown('<div class="hz-login-card">', unsafe_allow_html=True)

    st.markdown('<div class="hz-logo-wrap">', unsafe_allow_html=True)
    exibir_logo()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["auth_tela"] == "login":
        st.markdown('<div class="hz-title">Horizonte Health Intelligence</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-subtitle">Acesse sua central segura de leitura DBF, auditoria epidemiológica e painéis inteligentes do SINAN.</div>',
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
        st.markdown('<div class="hz-title">Criar cadastro</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-subtitle">Solicite um acesso para testar a plataforma Horizonte.</div>',
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
                    st.success("Cadastro criado. Faça login para continuar.")
                    st.session_state["auth_tela"] = "login"
                    st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

    elif st.session_state["auth_tela"] == "redefinir":
        st.markdown('<div class="hz-title">Redefinir senha</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-subtitle">Informe seu usuário e uma nova senha para o ambiente de testes.</div>',
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
                    st.success("Senha redefinida.")
                    st.session_state["auth_tela"] = "login"
                    st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hz-side-copy">
            <div class="hz-kicker-login">Secure • Innovate • Elevate</div>
            <h1>Inteligência pública com segurança digital.</h1>
            <p>
                A Horizonte transforma bancos epidemiológicos em informação clara,
                auditável e estratégica para apoiar decisões em Vigilância em Saúde.
            </p>
            <div class="hz-pills">
                <span class="hz-pill">SINAN DBF</span>
                <span class="hz-pill">Auditoria epidemiológica</span>
                <span class="hz-pill">GovTech</span>
                <span class="hz-pill">Dados seguros</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


def exigir_login():
    if not usuario_logado():
        tela_login()
        st.stop()
