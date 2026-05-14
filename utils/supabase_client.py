import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from supabase import create_client, Client


ARQUIVO_USUARIOS_LOCAL = Path("data/usuarios.json")


@st.cache_resource
def obter_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["service_role_key"]
    return create_client(url, key)


def agora_iso():
    return datetime.now(timezone.utc).isoformat()


def gerar_hash_senha(senha):
    if not senha:
        return ""
    return hashlib.sha256(str(senha).encode("utf-8")).hexdigest()


def limpar_timestamp(valor):
    if not valor:
        return None

    if isinstance(valor, str) and valor.strip() == "":
        return None

    return valor


def testar_conexao_supabase():
    supabase = obter_supabase()

    resposta = (
        supabase
        .table("usuarios")
        .select("id, usuario, nome, perfil")
        .limit(5)
        .execute()
    )

    return resposta.data or []


def listar_usuarios_supabase():
    supabase = obter_supabase()

    resposta = (
        supabase
        .table("usuarios")
        .select(
            "id, usuario, nome, email, perfil, municipio, instituicao, "
            "cargo, funcao, tema, verificado, bloqueado, aceitou_lgpd, "
            "ultimo_acesso, criado_em"
        )
        .order("usuario")
        .execute()
    )

    return resposta.data or []


def carregar_usuarios_json_local():
    if not ARQUIVO_USUARIOS_LOCAL.exists():
        return {}

    try:
        with open(ARQUIVO_USUARIOS_LOCAL, "r", encoding="utf-8") as f:
            dados = json.load(f)

        return dados if isinstance(dados, dict) else {}

    except Exception:
        return {}


def usuario_local_para_supabase(usuario, dados):
    return {
        "usuario": usuario,
        "nome": dados.get("nome", usuario),
        "email": dados.get("email", f"{usuario}@horizonte.local"),
        "perfil": dados.get("perfil", "Usuário"),
        "municipio": dados.get("municipio") or None,
        "instituicao": dados.get("instituicao") or None,
        "cargo": dados.get("cargo") or None,
        "funcao": dados.get("funcao") or None,
        "tema": dados.get("tema", "Escuro"),
        "avatar_url": dados.get("avatar_path") or dados.get("avatar_url") or None,
        "verificado": bool(dados.get("verificado", False)),
        "bloqueado": bool(dados.get("bloqueado", False)),
        "aceitou_lgpd": bool(dados.get("aceitou_lgpd", False)),
        "data_aceite_lgpd": limpar_timestamp(dados.get("data_aceite_lgpd")),
        "ultimo_acesso": limpar_timestamp(dados.get("ultimo_acesso")),
        "senha_hash": gerar_hash_senha(dados.get("senha", "")),
    }


def migrar_usuarios_locais_para_supabase():
    supabase = obter_supabase()
    usuarios = carregar_usuarios_json_local()

    resultado = {
        "total_lidos": 0,
        "migrados": 0,
        "erros": 0,
        "detalhes": [],
    }

    for usuario, dados in usuarios.items():
        resultado["total_lidos"] += 1

        try:
            payload = usuario_local_para_supabase(usuario, dados)

            (
                supabase
                .table("usuarios")
                .upsert(payload, on_conflict="usuario")
                .execute()
            )

            resultado["migrados"] += 1
            resultado["detalhes"].append({
                "usuario": usuario,
                "status": "Migrado/atualizado",
                "erro": "",
            })

        except Exception as e:
            resultado["erros"] += 1
            resultado["detalhes"].append({
                "usuario": usuario,
                "status": "Erro",
                "erro": str(e),
            })

    return resultado


def registrar_log_acesso_supabase(usuario, observacao="Login registrado"):
    try:
        supabase = obter_supabase()

        resposta_usuario = (
            supabase
            .table("usuarios")
            .select("id")
            .eq("usuario", usuario)
            .limit(1)
            .execute()
        )

        usuario_id = None

        if resposta_usuario.data:
            usuario_id = resposta_usuario.data[0].get("id")

        supabase.table("logs_acesso").insert({
            "usuario": usuario,
            "usuario_id": usuario_id,
            "data_acesso": agora_iso(),
            "origem": "Streamlit",
            "observacao": observacao,
        }).execute()

        return True

    except Exception:
        return False
