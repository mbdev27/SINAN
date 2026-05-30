import base64
import copy
import hashlib
import json
import random
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import streamlit as st

from utils.termos import (
    TERMO_RESPONSABILIDADE_SIGILO,
    VERSAO_TERMO_RESPONSABILIDADE,
    agora_aceite_iso,
    texto_resumido_aceite,
)

try:
    from utils.supabase_client import obter_supabase
except Exception:
    obter_supabase = None


ARQUIVO_USUARIOS = Path("data/usuarios.json")
ARQUIVO_EXCLUSAO = Path("data/solicitacoes_exclusao.json")
PASTA_AVATARES = Path("data/avatars")


USUARIOS_PADRAO = {
    "admin": {
        "senha": "admin123",
        "nome": "Administrador",
        "perfil": "Admin",
        "email": "admin@horizonte.local",
        "municipio": "",
        "instituicao": "Horizonte",
        "cargo": "Administrador",
        "funcao": "Gestão da plataforma",
        "tema": "Claro",
        "aceitou_lgpd": False,
        "data_aceite_lgpd": "",
        "versao_termo_lgpd": "",
        "requer_troca_senha": False,
        "avatar_path": "",
        "ultimo_acesso": "",
        "historico_acessos": [],
        "verificado": True,
        "bloqueado": False,
    },
    "demo": {
        "senha": "demo123",
        "nome": "Usuário Demonstração",
        "perfil": "Demo",
        "email": "demo@horizonte.local",
        "municipio": "",
        "instituicao": "",
        "cargo": "",
        "funcao": "",
        "tema": "Claro",
        "aceitou_lgpd": False,
        "data_aceite_lgpd": "",
        "versao_termo_lgpd": "",
        "requer_troca_senha": False,
        "avatar_path": "",
        "ultimo_acesso": "",
        "historico_acessos": [],
        "verificado": True,
        "bloqueado": False,
    },
}


def agora_iso():
    return datetime.now(timezone.utc).isoformat()


def agora_br():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def gerar_hash_senha(senha):
    if not senha:
        return ""

    return hashlib.sha256(str(senha).encode("utf-8")).hexdigest()


def gerar_codigo():
    return str(random.randint(1000, 9999))


def garantir_pastas():
    ARQUIVO_USUARIOS.parent.mkdir(parents=True, exist_ok=True)
    PASTA_AVATARES.mkdir(parents=True, exist_ok=True)


def carregar_json(caminho, padrao):
    garantir_pastas()

    if not caminho.exists():
        return copy.deepcopy(padrao)

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)

        return dados if isinstance(dados, type(padrao)) else copy.deepcopy(padrao)

    except Exception:
        return copy.deepcopy(padrao)


def salvar_json(caminho, dados):
    garantir_pastas()

    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        return True

    except Exception:
        return False


def imagem_base64(caminho):
    try:
        with open(caminho, "rb") as img:
            return base64.b64encode(img.read()).decode()
    except Exception:
        return None


def normalizar_usuario(dados):
    base = {
        "id": "",
        "senha": "",
        "senha_hash": "",
        "nome": "",
        "perfil": "Usuário",
        "email": "",
        "municipio": "",
        "instituicao": "",
        "cargo": "",
        "funcao": "",
        "tema": "Claro",
        "aceitou_lgpd": False,
        "data_aceite_lgpd": "",
        "versao_termo_lgpd": "",
        "requer_troca_senha": False,
        "avatar_path": "",
        "ultimo_acesso": "",
        "historico_acessos": [],
        "verificado": False,
        "bloqueado": False,
    }

    base.update(dict(dados))

    if not isinstance(base.get("historico_acessos"), list):
        base["historico_acessos"] = []

    return base


def converter_usuario_supabase(item):
    return normalizar_usuario({
        "id": item.get("id", ""),
        "senha": "",
        "senha_hash": item.get("senha_hash", ""),
        "nome": item.get("nome", ""),
        "perfil": item.get("perfil", "Usuário"),
        "email": item.get("email", ""),
        "municipio": item.get("municipio") or "",
        "instituicao": item.get("instituicao") or "",
        "cargo": item.get("cargo") or "",
        "funcao": item.get("funcao") or "",
        "tema": item.get("tema") or "Claro",
        "aceitou_lgpd": bool(item.get("aceitou_lgpd", False)),
        "data_aceite_lgpd": item.get("data_aceite_lgpd") or "",
        "versao_termo_lgpd": item.get("versao_termo_lgpd") or "",
        "requer_troca_senha": bool(item.get("requer_troca_senha", False)),
        "avatar_path": item.get("avatar_url") or "",
        "ultimo_acesso": item.get("ultimo_acesso") or "",
        "historico_acessos": [],
        "verificado": bool(item.get("verificado", False)),
        "bloqueado": bool(item.get("bloqueado", False)),
    })


def carregar_usuarios_arquivo():
    return carregar_json(ARQUIVO_USUARIOS, {})


def salvar_usuarios_arquivo(usuarios):
    return salvar_json(ARQUIVO_USUARIOS, usuarios)


def carregar_usuarios_json_com_padrao():
    usuarios = copy.deepcopy(USUARIOS_PADRAO)
    usuarios.update(carregar_usuarios_arquivo())

    return {
        usuario: normalizar_usuario(dados)
        for usuario, dados in usuarios.items()
    }


def supabase_disponivel():
    return obter_supabase is not None


def carregar_usuarios_supabase():
    if not supabase_disponivel():
        raise RuntimeError("Supabase não disponível.")

    supabase = obter_supabase()

    resposta = (
        supabase
        .table("usuarios")
        .select("*")
        .order("usuario")
        .execute()
    )

    usuarios = {}

    for item in resposta.data or []:
        login = item.get("usuario")

        if login:
            usuarios[login] = converter_usuario_supabase(item)

    return usuarios


def carregar_usuarios():
    try:
        usuarios = carregar_usuarios_supabase()

        if usuarios:
            return usuarios

        return carregar_usuarios_json_com_padrao()

    except Exception:
        return carregar_usuarios_json_com_padrao()


def payload_usuario_supabase(usuario, dados):
    payload = {
        "usuario": usuario,
        "nome": dados.get("nome", usuario),
        "email": dados.get("email", f"{usuario}@horizonte.local"),
        "perfil": dados.get("perfil", "Usuário"),
        "municipio": dados.get("municipio") or None,
        "instituicao": dados.get("instituicao") or None,
        "cargo": dados.get("cargo") or None,
        "funcao": dados.get("funcao") or None,
        "tema": dados.get("tema", "Claro"),
        "avatar_url": dados.get("avatar_path") or None,
        "verificado": bool(dados.get("verificado", False)),
        "bloqueado": bool(dados.get("bloqueado", False)),
        "aceitou_lgpd": bool(dados.get("aceitou_lgpd", False)),
        "data_aceite_lgpd": dados.get("data_aceite_lgpd") or None,
        "ultimo_acesso": dados.get("ultimo_acesso") or None,
        "versao_termo_lgpd": dados.get("versao_termo_lgpd") or None,
        "requer_troca_senha": bool(dados.get("requer_troca_senha", False)),
    }

    if dados.get("senha"):
        payload["senha_hash"] = gerar_hash_senha(dados.get("senha"))

    elif dados.get("senha_hash"):
        payload["senha_hash"] = dados.get("senha_hash")

    return payload


def salvar_usuario_runtime(usuario, dados):
    usuario = str(usuario).strip()

    if not usuario:
        return False

    dados = normalizar_usuario(dados)

    try:
        if supabase_disponivel():
            supabase = obter_supabase()
            payload = payload_usuario_supabase(usuario, dados)

            try:
                (
                    supabase
                    .table("usuarios")
                    .upsert(payload, on_conflict="usuario")
                    .execute()
                )

                return True

            except Exception:
                payload.pop("versao_termo_lgpd", None)
                payload.pop("requer_troca_senha", None)

                (
                    supabase
                    .table("usuarios")
                    .upsert(payload, on_conflict="usuario")
                    .execute()
                )

                return True

    except Exception:
        pass

    usuarios_arquivo = carregar_usuarios_arquivo()
    usuarios_arquivo[usuario] = dados

    return salvar_usuarios_arquivo(usuarios_arquivo)


def excluir_usuario_runtime(usuario):
    usuario = str(usuario).strip()

    try:
        if supabase_disponivel():
            supabase = obter_supabase()

            (
                supabase
                .table("usuarios")
                .delete()
                .eq("usuario", usuario)
                .execute()
            )

            return True

    except Exception:
        pass

    usuarios_arquivo = carregar_usuarios_arquivo()

    if usuario in usuarios_arquivo:
        usuarios_arquivo.pop(usuario, None)
        return salvar_usuarios_arquivo(usuarios_arquivo)

    return False


def forcar_novo_aceite_termo_para_todos():
    usuarios = carregar_usuarios()
    total = 0

    for login, dados in usuarios.items():
        dados = dict(dados)
        dados["aceitou_lgpd"] = False
        dados["data_aceite_lgpd"] = ""
        dados["versao_termo_lgpd"] = ""

        if salvar_usuario_runtime(login, dados):
            total += 1

    return total


def carregar_solicitacoes_exclusao():
    try:
        if supabase_disponivel():
            supabase = obter_supabase()

            resposta = (
                supabase
                .table("solicitacoes_exclusao")
                .select("*")
                .order("data_solicitacao", desc=True)
                .execute()
            )

            return resposta.data or []

    except Exception:
        pass

    return carregar_json(ARQUIVO_EXCLUSAO, [])


def registrar_solicitacao_exclusao(usuario, motivo=""):
    usuarios = carregar_usuarios()
    dados = usuarios.get(usuario, {})

    try:
        if supabase_disponivel():
            supabase = obter_supabase()

            usuario_id = dados.get("id") or None

            supabase.table("solicitacoes_exclusao").insert({
                "usuario": usuario,
                "usuario_id": usuario_id,
                "nome": dados.get("nome", ""),
                "email": dados.get("email", ""),
                "perfil": dados.get("perfil", ""),
                "motivo": motivo,
                "status": "Pendente",
                "data_solicitacao": agora_iso(),
            }).execute()

            return True

    except Exception:
        pass

    solicitacoes = carregar_json(ARQUIVO_EXCLUSAO, [])

    solicitacoes.append({
        "usuario": usuario,
        "nome": dados.get("nome", ""),
        "email": dados.get("email", ""),
        "perfil": dados.get("perfil", ""),
        "motivo": motivo,
        "status": "Pendente",
        "data_solicitacao": agora_br(),
    })

    return salvar_json(ARQUIVO_EXCLUSAO, solicitacoes)


def atualizar_status_solicitacao_exclusao(indice, status):
    solicitacoes = carregar_solicitacoes_exclusao()

    if indice < 0 or indice >= len(solicitacoes):
        return False

    solicitacao = solicitacoes[indice]

    try:
        if supabase_disponivel() and solicitacao.get("id"):
            supabase = obter_supabase()

            (
                supabase
                .table("solicitacoes_exclusao")
                .update({
                    "status": status,
                    "data_atualizacao": agora_iso(),
                })
                .eq("id", solicitacao["id"])
                .execute()
            )

            return True

    except Exception:
        pass

    solicitacoes[indice]["status"] = status
    solicitacoes[indice]["data_atualizacao"] = agora_br()

    return salvar_json(ARQUIVO_EXCLUSAO, solicitacoes)


def salvar_avatar_usuario(usuario, arquivo):
    if arquivo is None:
        return ""

    garantir_pastas()

    extensao = Path(arquivo.name).suffix.lower()

    if extensao not in [".png", ".jpg", ".jpeg", ".webp"]:
        extensao = ".png"

    caminho = PASTA_AVATARES / f"{usuario}{extensao}"

    try:
        with open(caminho, "wb") as f:
            f.write(arquivo.getbuffer())

        return str(caminho)

    except Exception:
        return ""


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


def usuario_logado():
    return st.session_state.get("autenticado", False)


def obter_usuario_atual():
    usuario = st.session_state.get("usuario")
    nome = st.session_state.get("nome_usuario")
    perfil = st.session_state.get("perfil_usuario")

    return {
        "usuario": usuario,
        "nome": nome,
        "perfil": perfil,
    }


def obter_dados_usuario_logado():
    usuario = st.session_state.get("usuario")

    if not usuario:
        return {}

    usuarios = carregar_usuarios()

    return usuarios.get(usuario, {})


def usuario_e_admin():
    perfil = str(st.session_state.get("perfil_usuario", "")).strip().lower()
    return perfil == "admin"


def registrar_log_acesso(usuario, dados):
    try:
        if supabase_disponivel():
            supabase = obter_supabase()

            supabase.table("logs_acesso").insert({
                "usuario": usuario,
                "usuario_id": dados.get("id") or None,
                "data_acesso": agora_iso(),
                "origem": "Streamlit",
                "observacao": "Login realizado com sucesso.",
            }).execute()

            return True

    except Exception:
        return False

    return False


def finalizar_login(usuario, dados):
    momento = agora_iso()

    dados["ultimo_acesso"] = momento

    historico = dados.get("historico_acessos", [])

    if not isinstance(historico, list):
        historico = []

    historico.append(momento)
    dados["historico_acessos"] = historico[-20:]

    salvar_usuario_runtime(usuario, dados)
    registrar_log_acesso(usuario, dados)

    st.session_state["autenticado"] = True
    st.session_state["usuario"] = usuario
    st.session_state["nome_usuario"] = dados.get("nome", usuario)
    st.session_state["perfil_usuario"] = dados.get("perfil", "Usuário")
    st.session_state["tema_usuario"] = dados.get("tema", "Claro")

    return True


def termo_esta_valido(dados):
    return (
        bool(dados.get("aceitou_lgpd", False))
        and dados.get("versao_termo_lgpd", "") == VERSAO_TERMO_RESPONSABILIDADE
    )


def fazer_login(usuario, senha):
    usuarios = carregar_usuarios()
    usuario = str(usuario).strip()

    if usuario not in usuarios:
        return False

    dados = usuarios[usuario]

    if dados.get("bloqueado", False):
        st.error("Este usuário está bloqueado. Procure o administrador.")
        return False

    if not dados.get("verificado", False):
        st.error("Este usuário ainda não concluiu a verificação por e-mail.")
        return False

    senha_hash = gerar_hash_senha(senha)

    senha_valida = False

    if dados.get("senha_hash"):
        senha_valida = senha_hash == dados.get("senha_hash")

    elif dados.get("senha"):
        senha_valida = str(senha) == str(dados.get("senha"))

    if not senha_valida:
        return False

    if not termo_esta_valido(dados):
        st.session_state["termo_pendente_usuario"] = usuario
        st.session_state["termo_pendente_validado"] = True
        return False

    if dados.get("requer_troca_senha", False):
        st.session_state["troca_senha_obrigatoria_usuario"] = usuario
        st.session_state["troca_senha_obrigatoria_validado"] = True
        return False

    return finalizar_login(usuario, dados)


def fazer_logout():
    chaves = [
        "autenticado",
        "usuario",
        "nome_usuario",
        "perfil_usuario",
        "tema_usuario",
        "termo_pendente_usuario",
        "termo_pendente_validado",
        "troca_senha_obrigatoria_usuario",
        "troca_senha_obrigatoria_validado",
        "termo_cadastro_aceito",
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
        [data-testid="collapsedControl"],
        header[data-testid="stHeader"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(0,155,90,0.10), transparent 24%),
                linear-gradient(135deg, #F7FAF8 0%, #FFFFFF 48%, #EAF6EF 100%) !important;
            min-height: 100vh;
        }

        .block-container {
            max-width: 430px !important;
            padding-top: 4vh !important;
            padding-left: 18px !important;
            padding-right: 18px !important;
            margin: 0 auto !important;
        }

        .hz-login-shell {
            background: #FFFFFF;
            border: 1px solid #DDE5E0;
            border-radius: 28px;
            padding: 34px 28px 28px 28px;
            box-shadow: 0 24px 70px rgba(16, 24, 32, 0.14);
            min-height: 86vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .hz-login-shell:after {
            content: "";
            position: absolute;
            left: -10%;
            right: -10%;
            bottom: -35px;
            height: 130px;
            background:
                repeating-radial-gradient(
                    ellipse at center,
                    rgba(0,155,90,0.16) 0,
                    rgba(0,155,90,0.16) 1px,
                    transparent 2px,
                    transparent 14px
                );
            opacity: .35;
            pointer-events: none;
        }

        .hz-login-content {
            position: relative;
            z-index: 2;
        }

        [data-testid="stImage"] {
            display: flex !important;
            justify-content: center !important;
            margin-bottom: 8px !important;
        }

        [data-testid="stImage"] img {
            max-width: 190px !important;
            width: 100% !important;
            height: auto !important;
        }

        .hz-login-title {
            text-align: center;
            color: #101820 !important;
            font-size: 1.25rem;
            line-height: 1.15;
            font-weight: 900;
            letter-spacing: -0.03em;
            margin-top: 8px;
            margin-bottom: 4px;
        }

        .hz-login-subtitle {
            text-align: center;
            color: #4B5563 !important;
            line-height: 1.45;
            font-size: 0.88rem;
            margin-bottom: 22px;
        }

        .hz-panel {
            background: #FFFFFF;
            border: 1px solid #DDE5E0;
            border-radius: 26px;
            padding: 24px;
            box-shadow: 0 20px 55px rgba(16,24,32,0.12);
            margin-top: 8px;
        }

        .hz-mini-title {
            color: #101820 !important;
            font-weight: 900;
            font-size: 1.25rem;
            text-align: center;
            margin-bottom: 6px;
        }

        .hz-mini-subtitle {
            color: #4B5563 !important;
            text-align: center;
            font-size: 0.88rem;
            line-height: 1.5;
            margin-bottom: 18px;
        }

        .hz-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 18px 0;
            color: #64748B !important;
            font-size: 0.86rem;
        }

        .hz-divider:before,
        .hz-divider:after {
            content: "";
            flex: 1;
            height: 1px;
            background: #DDE5E0;
        }

        .hz-note {
            text-align: center;
            color: #64748B !important;
            font-size: 0.82rem;
            margin-top: 18px;
        }

        input, textarea {
            background: #FFFFFF !important;
            color: #101820 !important;
            border: 1px solid #CBD5D1 !important;
            border-radius: 12px !important;
        }

        input {
            min-height: 44px !important;
        }

        input::placeholder {
            color: #64748B !important;
        }

        label {
            color: #101820 !important;
            font-weight: 700 !important;
        }

        button {
            border-radius: 12px !important;
            font-weight: 900 !important;
            min-height: 46px !important;
        }

        .stButton > button,
        [data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #009B5A, #00B86B) !important;
            color: #FFFFFF !important;
            border: 1px solid #009B5A !important;
            box-shadow: 0px 14px 28px rgba(0,155,90,0.24);
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            filter: brightness(1.04);
            transform: translateY(-1px);
        }

        [data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }

        [data-testid="stAlert"] {
            border-radius: 14px !important;
        }

        .hz-link-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: .82rem;
            color: #4B5563;
            margin-top: -4px;
            margin-bottom: 10px;
        }
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
            st.image(caminho, width=185)
            return

    st.markdown(
        """
        <div style="text-align:center;">
            <div style="
                width:84px;height:84px;margin:auto;border-radius:22px;
                background:linear-gradient(135deg,#101820,#009B5A);
                display:flex;align-items:center;justify-content:center;
                color:white;font-size:48px;font-weight:900;
                border:1px solid rgba(0,0,0,.08);
            ">H</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def exibir_termo_em_area():
    st.text_area(
        "Termo completo",
        value=TERMO_RESPONSABILIDADE_SIGILO,
        height=420,
        disabled=True,
        label_visibility="collapsed"
    )


def abrir_modal_termo_cadastro():
    if hasattr(st, "dialog"):
        @st.dialog("Termo de Responsabilidade, Sigilo e Uso Aceitável")
        def modal_termo():
            st.caption("Role até o final, leia o conteúdo e confirme o aceite.")
            exibir_termo_em_area()

            confirmar = st.checkbox(
                texto_resumido_aceite(),
                key="modal_confirmar_termo_cadastro"
            )

            if st.button("Aceitar termo", use_container_width=True):
                if confirmar:
                    st.session_state["termo_cadastro_aceito"] = True
                    st.rerun()
                else:
                    st.error("É necessário marcar a declaração de aceite.")

        modal_termo()

    else:
        st.warning("Seu Streamlit não possui modal nativo. O termo será exibido abaixo.")
        exibir_termo_em_area()


def tela_aceite_obrigatorio():
    css_login()
    exibir_logo()

    usuario = st.session_state.get("termo_pendente_usuario")

    if not usuario:
        st.session_state["auth_tela"] = "login"
        st.rerun()

    usuarios = carregar_usuarios()
    dados = usuarios.get(usuario)

    if not dados:
        st.error("Usuário não localizado.")
        st.session_state.pop("termo_pendente_usuario", None)
        st.session_state.pop("termo_pendente_validado", None)
        st.stop()

    st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
    st.markdown('<div class="hz-mini-title">Aceite obrigatório do termo</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hz-mini-subtitle">
            Para acessar a plataforma, é obrigatório ler e aceitar o Termo de
            Responsabilidade, Sigilo e Uso Aceitável de Dados Sensíveis.
        </div>
        """,
        unsafe_allow_html=True
    )

    exibir_termo_em_area()

    aceite = st.checkbox(
        texto_resumido_aceite(),
        key="aceite_termo_login"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Aceitar e continuar", use_container_width=True):
            if not aceite:
                st.error("A aceitação do termo é obrigatória para acessar a plataforma.")
            else:
                dados["aceitou_lgpd"] = True
                dados["data_aceite_lgpd"] = agora_aceite_iso()
                dados["versao_termo_lgpd"] = VERSAO_TERMO_RESPONSABILIDADE

                salvar_usuario_runtime(usuario, dados)

                st.session_state.pop("termo_pendente_usuario", None)
                st.session_state.pop("termo_pendente_validado", None)

                if dados.get("requer_troca_senha", False):
                    st.session_state["troca_senha_obrigatoria_usuario"] = usuario
                    st.session_state["troca_senha_obrigatoria_validado"] = True
                else:
                    finalizar_login(usuario, dados)

                st.rerun()

    with col2:
        if st.button("Não aceito", use_container_width=True):
            st.warning("O acesso à plataforma não será permitido sem o aceite do termo.")
            st.session_state.pop("termo_pendente_usuario", None)
            st.session_state.pop("termo_pendente_validado", None)
            st.session_state["auth_tela"] = "login"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


def tela_troca_senha_obrigatoria():
    css_login()
    exibir_logo()

    usuario = st.session_state.get("troca_senha_obrigatoria_usuario")

    if not usuario:
        st.session_state["auth_tela"] = "login"
        st.rerun()

    usuarios = carregar_usuarios()
    dados = usuarios.get(usuario)

    if not dados:
        st.error("Usuário não localizado.")
        st.session_state.pop("troca_senha_obrigatoria_usuario", None)
        st.session_state.pop("troca_senha_obrigatoria_validado", None)
        st.stop()

    st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
    st.markdown('<div class="hz-mini-title">Atualização de senha obrigatória</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hz-mini-subtitle">
            O administrador solicitou a atualização da sua senha.
            Crie uma nova senha para continuar acessando a plataforma.
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("form_troca_senha_obrigatoria", clear_on_submit=False):
        nova = st.text_input("Nova senha", type="password")
        confirmar = st.text_input("Confirmar nova senha", type="password")

        salvar = st.form_submit_button("Atualizar senha e acessar", use_container_width=True)

        if salvar:
            if not nova:
                st.error("Informe a nova senha.")
            elif nova != confirmar:
                st.error("As senhas não conferem.")
            else:
                dados["senha"] = nova
                dados["senha_hash"] = ""
                dados["requer_troca_senha"] = False

                salvar_usuario_runtime(usuario, dados)

                st.session_state.pop("troca_senha_obrigatoria_usuario", None)
                st.session_state.pop("troca_senha_obrigatoria_validado", None)

                finalizar_login(usuario, dados)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


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


def abrir_login_card():
    st.markdown('<div class="hz-login-shell"><div class="hz-login-content">', unsafe_allow_html=True)


def fechar_login_card():
    st.markdown('</div></div>', unsafe_allow_html=True)


def tela_login():
    css_login()

    if st.session_state.get("termo_pendente_usuario"):
        tela_aceite_obrigatorio()

    if st.session_state.get("troca_senha_obrigatoria_usuario"):
        tela_troca_senha_obrigatoria()

    if "auth_tela" not in st.session_state:
        st.session_state["auth_tela"] = "login"

    tela = st.session_state["auth_tela"]

    if tela == "login":
        abrir_login_card()

        exibir_logo()

        st.markdown(
            '<div class="hz-login-title">Bem-vindo(a) de volta!</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="hz-login-subtitle">Acesse sua conta para continuar</div>',
            unsafe_allow_html=True
        )

        with st.form("form_login", clear_on_submit=False):
            usuario = st.text_input("Usuário ou e-mail", placeholder="Usuário ou e-mail")
            senha = st.text_input("Senha", type="password", placeholder="Senha")

            entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                if fazer_login(usuario, senha):
                    st.rerun()

                elif st.session_state.get("termo_pendente_usuario"):
                    st.rerun()

                elif st.session_state.get("troca_senha_obrigatoria_usuario"):
                    st.rerun()

                else:
                    st.error("Usuário ou senha inválidos.")

        col_check, col_senha = st.columns([1, 1])

        with col_check:
            st.checkbox("Lembrar-me", value=False)

        with col_senha:
            if st.button("Esqueci minha senha", use_container_width=True):
                st.session_state["auth_tela"] = "redefinir_email"
                st.rerun()

        st.markdown('<div class="hz-divider">ou</div>', unsafe_allow_html=True)

        if st.button("Criar conta", use_container_width=True):
            st.session_state["auth_tela"] = "cadastro"
            st.rerun()

        st.markdown(
            '<div class="hz-note">Horizonte Health Intelligence • ambiente seguro</div>',
            unsafe_allow_html=True
        )

        fechar_login_card()

    elif tela == "cadastro":
        exibir_logo()
        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Criar conta</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-mini-subtitle">Preencha seus dados. Para criar a conta, é obrigatório aceitar o Termo de Responsabilidade, Sigilo e Uso Aceitável de Dados Sensíveis.</div>',
            unsafe_allow_html=True
        )

        if st.button("📜 Ler termo completo", use_container_width=True):
            abrir_modal_termo_cadastro()

        termo_aceito_previo = bool(st.session_state.get("termo_cadastro_aceito", False))

        with st.form("form_cadastro", clear_on_submit=False):
            nome = st.text_input("Nome completo")
            email = st.text_input("E-mail institucional")
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            confirmar = st.text_input("Confirmar senha", type="password")

            aceite = st.checkbox(
                texto_resumido_aceite(),
                value=termo_aceito_previo,
                key="checkbox_termo_cadastro"
            )

            cadastrar = st.form_submit_button("Cadastrar", use_container_width=True)

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
                    st.error("A aceitação do termo é obrigatória para criar conta.")

                else:
                    iniciar_verificacao_cadastro(nome, email, usuario, senha)
                    st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    elif tela == "verificar_cadastro":
        pendente = st.session_state.get("cadastro_pendente", {})

        exibir_logo()
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
                        "municipio": "",
                        "instituicao": "",
                        "cargo": "",
                        "funcao": "",
                        "tema": "Claro",
                        "aceitou_lgpd": True,
                        "data_aceite_lgpd": agora_aceite_iso(),
                        "versao_termo_lgpd": VERSAO_TERMO_RESPONSABILIDADE,
                        "requer_troca_senha": False,
                        "avatar_path": "",
                        "ultimo_acesso": "",
                        "historico_acessos": [],
                        "verificado": True,
                        "bloqueado": False,
                    }
                )

                st.session_state.pop("cadastro_pendente", None)
                st.session_state.pop("termo_cadastro_aceito", None)
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

        st.markdown("</div>", unsafe_allow_html=True)

    elif tela == "cadastro_sucesso":
        exibir_logo()
        st.success("Conta verificada! Faça login para continuar.")

        if st.button("Ir para o login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

    elif tela == "redefinir_email":
        exibir_logo()
        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Redefinir senha</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hz-mini-subtitle">Informe seu usuário. Enviaremos um código de 4 dígitos para o e-mail cadastrado.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_redefinir_email", clear_on_submit=False):
            usuario = st.text_input("Usuário")
            enviar = st.form_submit_button("Enviar código", use_container_width=True)

            if enviar:
                iniciar_redefinicao(str(usuario).strip())
                st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    elif tela == "verificar_redefinicao":
        pendente = st.session_state.get("redefinicao_pendente", {})

        exibir_logo()
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

        st.markdown("</div>", unsafe_allow_html=True)

    elif tela == "nova_senha":
        pendente = st.session_state.get("redefinicao_pendente", {})

        exibir_logo()
        st.markdown('<div class="hz-panel">', unsafe_allow_html=True)
        st.markdown('<div class="hz-mini-title">Criar nova senha</div>', unsafe_allow_html=True)

        with st.form("form_nova_senha", clear_on_submit=False):
            nova = st.text_input("Nova senha", type="password")
            confirmar = st.text_input("Confirmar nova senha", type="password")
            salvar = st.form_submit_button("Redefinir senha", use_container_width=True)

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
                    dados["senha_hash"] = ""
                    dados["verificado"] = True
                    dados["requer_troca_senha"] = False

                    salvar_usuario_runtime(usuario, dados)

                    st.session_state.pop("redefinicao_pendente", None)
                    st.success("Senha redefinida com sucesso.")
                    st.session_state["auth_tela"] = "login"
                    st.rerun()

        if st.button("Voltar para login", use_container_width=True):
            st.session_state["auth_tela"] = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def exigir_login():
    if not usuario_logado():
        tela_login()
        st.stop()
