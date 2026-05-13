import base64
import copy
import json
import random
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

import streamlit as st


ARQUIVO_USUARIOS = Path("data/usuarios.json")


USUARIOS_PADRAO = {
    "admin": {
        "senha": "admin123",
        "nome": "Administrador",
        "perfil": "Admin",
        "email": "admin@horizonte.local",
        "verificado": True,
        "bloqueado": False,
    },
    "demo": {
        "senha": "demo123",
        "nome": "Usuário Demonstração",
        "perfil": "Demo",
        "email": "demo@horizonte.local",
        "verificado": True,
        "bloqueado": False,
    },
}


def garantir_pasta_data():
    ARQUIVO_USUARIOS.parent.mkdir(parents=True, exist_ok=True)


def carregar_usuarios_arquivo():
    garantir_pasta_data()

    if not ARQUIVO_USUARIOS.exists():
        return {}

    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
            dados = json.load(f)

        return dados if isinstance(dados, dict) else {}

    except Exception:
        return {}


def salvar_usuarios_arquivo(usuarios):
    garantir_pasta_data()

    try:
        with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=4)

        return True

    except Exception:
        return False


def carregar_usuarios_secrets():
    try:
        if "usuarios" not in st.secrets:
            return {}

        usuarios = {}

        for usuario, dados in st.secrets["usuarios"].items():
            usuarios[usuario] = dict(dados)

        return usuarios

    except Exception:
        return {}


def carregar_usuarios():
    usuarios = copy.deepcopy(USUARIOS_PADRAO)
    usuarios.update(carregar_usuarios_secrets())
    usuarios.update(carregar_usuarios_arquivo())
    return usuarios


def salvar_usuario_runtime(usuario, dados):
    usuario = str(usuario).strip()

    if not usuario:
        return False

    usuarios_arquivo = carregar_usuarios_arquivo()
    usuarios_arquivo[usuario] = dados

    return salvar_usuarios_arquivo(usuarios_arquivo)


def excluir_usuario_runtime(usuario):
    usuario = str(usuario).strip()
    usuarios_arquivo = carregar_usuarios_arquivo()

    if usuario in usuarios_arquivo:
        usuarios_arquivo.pop(usuario, None)
        return salvar_usuarios_arquivo(usuarios_arquivo)

    return False


def imagem_base64(caminho):
    try:
        with open(caminho, "rb") as img:
            return base64.b64encode(img.read()).decode()
    except Exception:
        return None


def gerar_codigo():
    return str(random.randint(1000, 9999))


def usuario_logado():
    return st.session_state.get("autenticado", False)


def obter_usuario_atual():
    return {
        "usuario": st.session_state.get("usuario"),
        "nome": st.session_state.get("nome_usuario"),
        "perfil": st.session_state.get("perfil_usuario"),
    }


def usuario_e_admin():
    perfil = str(st.session_state.get("perfil_usuario", "")).strip().lower()
    return perfil == "admin"


def enviar_email_codigo(destinatario, codigo, assunto):
    try:
        smtp = st.secrets.get("smtp", None)

        if not smtp:
            return False

        msg = EmailMessage()
        msg["Subject"] = assunto
        msg["From"] = smtp.get("sender", smtp["user"])
        msg["To"] = destinatario

        msg.set_content(
            f"""
Horizonte Health Intelligence

Seu código de verificação é: {codigo}

Este código possui 4 dígitos e deve ser usado para concluir a operação solicitada.

Caso você não tenha solicitado este acesso, ignore esta mensagem.
"""
        )

        contexto = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            smtp["host"],
            int(smtp.get("port", 465)),
            context=contexto
        ) as server:
            server.login(smtp["user"], smtp["password"])
            server.send_message(msg)

        return True

    except Exception:
        return False


def fazer_login(usuario, senha):
    usuarios = carregar_usuarios()
    usuario = str(usuario).strip()

    if usuario in usuarios:
        dados = usuarios[usuario]

        if dados.get("bloqueado", False):
            st.error("Este usuário está bloqueado. Procure o administrador.")
            return False

        if not dados.get("verificado", False):
            st.error("Este usuário ainda não concluiu a verificação por e-mail.")
            return False

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

    if fundo:
        background_css = f"""
        background:
            linear-gradient(
                90deg,
                rgba(5, 15, 25, 0.72) 0%,
                rgba(5, 15, 25, 0.54) 45%,
                rgba(5, 15, 25, 0.38) 100%
            ),
            url("data:image/png;base64,{fundo}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        """
    else:
        background_css = """
        background:
            radial-gradient(circle at 20% 20%, rgba(0,237,100,0.16), transparent 34%),
            radial-gradient(circle at 80% 70%, rgba(0,237,100,0.10), transparent 30%),
            linear-gradient(135deg, #050F19 0%, #0A2647 58%, #064E3B 100%);
        """

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        header[data-testid="stHeader"] {{
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
        }}

        .block-container {{
            max-width: 430px !important;
            padding-top: 5vh !important;
            padding-left: 18px !important;
            padding-right: 18px !important;
            margin: 0 auto !important;
        }}

        [data-testid="stAppViewContainer"] {{
            {background_css}
            min-height: 100vh;
        }}

        [data-testid="stImage"] {{
            display: flex !important;
            justify-content: center !important;
            margin-bottom: 10px !important;
        }}

        [data-testid="stImage"] img {{
            max-width: 250px !important;
            width: 100% !important;
            height: auto !important;
        }}

        .hz-login-title {{
            text-align: center;
            color: #FFFFFF !important;
            font-size: 1.25rem;
            line-height: 1.15;
            font-weight: 900;
            letter-spacing: -0.03em;
            margin-top: 4px;
            margin-bottom: 8px;
        }}

        .hz-login-subtitle {{
            text-align: center;
            color: #E1E8ED !important;
            line-height: 1.55;
            font-size: 0.94rem;
            margin-bottom: 20px;
        }}

        .hz-panel {{
            background: rgba(5, 15, 25, 0.56);
            border: 1px solid rgba(225, 232, 237, 0.18);
            border-radius: 22px;
            padding: 22px;
            box-shadow: 0 28px 70px rgba(0,0,0,0.34);
            backdrop-filter: blur(14px);
            margin-top: 8px;
        }}

        .hz-mini-title {{
            color: #FFFFFF !important;
            font-weight: 900;
            font-size: 1.25rem;
            text-align: center;
            margin-bottom: 6px;
        }}

        .hz-mini-subtitle {{
            color: #C9D5DF !important;
            text-align: center;
            font-size: 0.88rem;
            line-height: 1.5;
            margin-bottom: 18px;
        }}

        .hz-divider {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 18px 0;
            color: #94A3B8 !important;
            font-size: 0.86rem;
        }}

        .hz-divider:before,
        .hz-divider:after {{
            content: "";
            flex: 1;
            height: 1px;
            background: rgba(225,232,237,0.18);
        }}

        .hz-note {{
            text-align: center;
            color: #94A3B8 !important;
            font-size: 0.82rem;
            margin-top: 18px;
        }}

        .hz-success-icon {{
            width: 72px;
            height: 72px;
            border-radius: 999px;
            border: 2px solid #00ED64;
            color: #00ED64 !important;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 18px auto;
            font-size: 2.2rem;
            font-weight: 900;
        }}

        input {{
            background: rgba(8, 19, 31, 0.72) !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(225, 232, 237, 0.25) !important;
            border-radius: 14px !important;
            min-height: 46px !important;
        }}

        input::placeholder {{
            color: #94A3B8 !important;
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

        [data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
        }}

        [data-testid="stAlert"] {{
            border-radius: 14px !important;
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
            st.image(caminho, width=250)
            return

    st.markdown(
        """
        <div style="text-align:center;">
            <div style="
                width:118px;height:118px;margin:auto;border-radius:28px;
                background:linear-gradient(135deg,#0A2647,#00ED64);
                display:flex;align-items:center;justify-content:center;
                color:white;font-size:64px;font-weight:900;
                border:1px solid rgba(255,255,255,.25);
            ">H</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def iniciar_verificacao_cadastro(nome, email, usuario, senha):
    codigo = gerar_codigo()

    st.session_state["cadastro_pendente"] = {
        "nome": nome,
        "email": email,
        "usuario": usuario,
        "senha": senha,
        "codigo": codigo,
    }

    enviado = enviar_email_codigo(
        email,
        codigo,
        "Código de verificação — Horizonte"
    )

    st.session_state["email_enviado_real"] = enviado
    st.session_state["auth_tela"] = "verificar_cadastro"


def iniciar_redefinicao(usuario):
    usuarios = carregar_usuarios()
    dados = usuarios.get(usuario)

    if not dados:
        st.error("Usuário não encontrado.")
        return

    email = dados.get("email", "")
    codigo = gerar_codigo()

    st.session_state["redefinicao_pendente"] = {
        "usuario": usuario,
        "email": email,
        "codigo": codigo,
    }

    enviado = enviar_email_codigo(
        email,
        codigo,
        "Código para redefinição de senha — Horizonte"
    )

    st.session_state["email_enviado_real"] = enviado
    st.session_state["auth_tela"] = "verificar_redefinicao"


def exibir_codigo_teste(chave):
    if not st.session_state.get("email_enviado_real", False):
        codigo = st.session_state.get(chave, {}).get("codigo")

        if codigo:
            st.info(f"Modo teste: código de verificação **{codigo}**")


def tela_login():
    css_login()

    if "auth_tela" not in st.session_state:
        st.session_state["auth_tela"] = "login"

    exibir_logo()

    tela = st.session_state["auth_tela"]

    if tela == "login":
        st.markdown(
            '<div class="hz-login-title">Horizonte Health Intelligence</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="hz-login-subtitle">Plataforma segura para leitura de bancos DBF do SINAN, auditoria epidemiológica e apoio à decisão.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_login", clear_on_submit=False):
            usuario = st.text_input("Usuário", placeholder="Usuário")
            senha = st.text_input("Senha", type="password", placeholder="Senha")
            st.checkbox("Lembrar de mim", value=True)

            entrar = st.form_submit_button(
                "Entrar",
                use_container_width=True
            )

            if entrar:
                if fazer_login(usuario, senha):
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        st.markdown(
            '<div class="hz-divider">ou</div>',
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Criar conta", use_container_width=True):
                st.session_state["auth_tela"] = "cadastro"
                st.rerun()

        with c2:
            if st.button("Esqueci a senha", use_container_width=True):
                st.session_state["auth_tela"] = "redefinir_email"
                st.rerun()

        st.markdown(
            '<div class="hz-note">Ambiente seguro • acesso verificado</div>',
            unsafe_allow_html=True
        )

    elif tela == "cadastro":
        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Criar conta</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-mini-subtitle">Preencha seus dados. Enviaremos um código de 4 dígitos para validar seu e-mail.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_cadastro", clear_on_submit=False):
            nome = st.text_input("Nome completo")
            email = st.text_input("E-mail institucional")
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            confirmar = st.text_input("Confirmar senha", type="password")
            aceite = st.checkbox("Li e aceito os termos de uso e política de privacidade")

            cadastrar = st.form_submit_button(
                "Cadastrar",
                use_container_width=True
            )

            if cadastrar:
                usuarios = carregar_usuarios()
                usuario = str(usuario).strip()

                if not nome or not email or not usuario or not senha:
                    st.error("Preencha todos os campos.")
                elif "@" not in email:
                    st.error("Informe um e-mail válido.")
                elif usuario in usuarios:
                    st.error("Este usuário já existe.")
                elif senha != confirmar:
                    st.error("As senhas não conferem.")
                elif not aceite:
                    st.error("É necessário aceitar os termos para continuar.")
                else:
                    iniciar_verificacao_cadastro(nome, email, usuario, senha)
                    st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    elif tela == "verificar_cadastro":
        pendente = st.session_state.get("cadastro_pendente", {})

        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Verifique seu e-mail</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="hz-mini-subtitle">Enviamos um código de 4 dígitos para <b>{pendente.get("email", "")}</b>.</div>',
            unsafe_allow_html=True
        )

        exibir_codigo_teste("cadastro_pendente")

        codigo = st.text_input("Código de verificação", max_chars=4)

        if st.button("Verificar código", use_container_width=True):
            if codigo == pendente.get("codigo"):
                salvar_usuario_runtime(
                    pendente["usuario"],
                    {
                        "senha": pendente["senha"],
                        "nome": pendente["nome"],
                        "perfil": "Demo",
                        "email": pendente["email"],
                        "verificado": True,
                        "bloqueado": False,
                    }
                )

                st.session_state.pop("cadastro_pendente", None)
                st.session_state["auth_tela"] = "cadastro_sucesso"
                st.rerun()
            else:
                st.error("Código inválido.")

        if st.button("Reenviar código", use_container_width=True):
            iniciar_verificacao_cadastro(
                pendente["nome"],
                pendente["email"],
                pendente["usuario"],
                pendente["senha"],
            )
            st.rerun()

        if st.button("Voltar", use_container_width=True):
            st.session_state["auth_tela"] = "cadastro"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    elif tela == "cadastro_sucesso":
        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-success-icon">✓</div>', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Conta verificada!</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-mini-subtitle">Seu cadastro foi concluído e o usuário já integra a lista de acesso da plataforma.</div>',
            unsafe_allow_html=True
        )

        if st.button("Ir para o login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    elif tela == "redefinir_email":
        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Redefinir senha</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-mini-subtitle">Informe seu usuário. Enviaremos um código de 4 dígitos para o e-mail cadastrado.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_redefinir_email", clear_on_submit=False):
            usuario = st.text_input("Usuário")

            enviar = st.form_submit_button(
                "Enviar código",
                use_container_width=True
            )

            if enviar:
                iniciar_redefinicao(str(usuario).strip())
                st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    elif tela == "verificar_redefinicao":
        pendente = st.session_state.get("redefinicao_pendente", {})

        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Verifique seu e-mail</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="hz-mini-subtitle">Enviamos um código de 4 dígitos para <b>{pendente.get("email", "")}</b>.</div>',
            unsafe_allow_html=True
        )

        exibir_codigo_teste("redefinicao_pendente")

        codigo = st.text_input("Código de verificação", max_chars=4)

        if st.button("Verificar código", use_container_width=True):
            if codigo == pendente.get("codigo"):
                st.session_state["auth_tela"] = "nova_senha"
                st.rerun()
            else:
                st.error("Código inválido.")

        if st.button("Reenviar código", use_container_width=True):
            iniciar_redefinicao(pendente["usuario"])
            st.rerun()

        if st.button("Voltar", use_container_width=True):
            st.session_state["auth_tela"] = "redefinir_email"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    elif tela == "nova_senha":
        pendente = st.session_state.get("redefinicao_pendente", {})

        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Criar nova senha</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-mini-subtitle">Defina uma nova senha para sua conta.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_nova_senha", clear_on_submit=False):
            nova = st.text_input("Nova senha", type="password")
            confirmar = st.text_input("Confirmar nova senha", type="password")

            salvar = st.form_submit_button(
                "Redefinir senha",
                use_container_width=True
            )

            if salvar:
                if not nova:
                    st.error("Informe a nova senha.")
                elif nova != confirmar:
                    st.error("As senhas não conferem.")
                else:
                    usuarios = carregar_usuarios()
                    usuario = pendente["usuario"]
                    dados = dict(usuarios[usuario])
                    dados["senha"] = nova
                    dados["verificado"] = True

                    salvar_usuario_runtime(usuario, dados)

                    st.session_state.pop("redefinicao_pendente", None)
                    st.success("Senha redefinida com sucesso.")
                    st.session_state["auth_tela"] = "login"
                    st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


def exigir_login():
    if not usuario_logado():
        tela_login()
        st.stop()
