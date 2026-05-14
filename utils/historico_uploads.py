import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

try:
    from utils.supabase_client import obter_supabase
except Exception:
    obter_supabase = None


ARQUIVO_HISTORICO_UPLOADS = Path("data/historico_uploads.json")


def agora_iso():
    return datetime.now(timezone.utc).isoformat()


def garantir_pasta_data():
    ARQUIVO_HISTORICO_UPLOADS.parent.mkdir(parents=True, exist_ok=True)


def supabase_disponivel():
    return obter_supabase is not None


# ============================================================
# HISTÓRICO LOCAL — FALLBACK
# ============================================================

def carregar_historico_uploads_local():
    garantir_pasta_data()

    if not ARQUIVO_HISTORICO_UPLOADS.exists():
        return []

    try:
        with open(ARQUIVO_HISTORICO_UPLOADS, "r", encoding="utf-8") as f:
            dados = json.load(f)

        return dados if isinstance(dados, list) else []

    except Exception:
        return []


def salvar_historico_uploads_local(historico):
    garantir_pasta_data()

    try:
        with open(ARQUIVO_HISTORICO_UPLOADS, "w", encoding="utf-8") as f:
            json.dump(
                historico,
                f,
                ensure_ascii=False,
                indent=4
            )

        return True

    except Exception:
        return False


# ============================================================
# HISTÓRICO SUPABASE
# ============================================================

def carregar_historico_uploads_supabase():
    if not supabase_disponivel():
        raise RuntimeError("Supabase não disponível.")

    supabase = obter_supabase()

    resposta = (
        supabase
        .table("historico_uploads")
        .select("*")
        .order("data_upload", desc=True)
        .execute()
    )

    return resposta.data or []


def carregar_historico_uploads():
    try:
        dados = carregar_historico_uploads_supabase()

        if dados:
            return dados

        return carregar_historico_uploads_local()

    except Exception:
        return carregar_historico_uploads_local()


def registrar_upload(
    nome_arquivo,
    agravo,
    usuario,
    municipio,
    score_qualidade,
    quantidade_registros,
    quantidade_colunas,
    ficha_sugerida="",
    confianca="",
    codigo_ibge_municipio="",
):
    registro = {
        "nome_arquivo": nome_arquivo,
        "data_upload": agora_iso(),
        "agravo_detectado": agravo,
        "ficha_sugerida": ficha_sugerida,
        "confianca": confianca,
        "usuario": usuario,
        "municipio": municipio,
        "codigo_ibge_municipio": codigo_ibge_municipio or None,
        "score_qualidade": score_qualidade,
        "quantidade_registros": int(quantidade_registros or 0),
        "quantidade_colunas": int(quantidade_colunas or 0),
    }

    try:
        if supabase_disponivel():
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

            registro["usuario_id"] = usuario_id

            resposta = (
                supabase
                .table("historico_uploads")
                .insert(registro)
                .execute()
            )

            if resposta.data:
                return True, resposta.data[0]

            return True, registro

    except Exception:
        pass

    historico = carregar_historico_uploads_local()

    registro_local = dict(registro)
    registro_local["id"] = len(historico) + 1

    historico.append(registro_local)

    ok = salvar_historico_uploads_local(historico)

    return ok, registro_local


def historico_para_dataframe():
    historico = carregar_historico_uploads()

    if not historico:
        return pd.DataFrame(columns=[
            "id",
            "nome_arquivo",
            "data_upload",
            "agravo_detectado",
            "usuario",
            "municipio",
            "score_qualidade",
            "quantidade_registros",
            "quantidade_colunas",
            "ficha_sugerida",
            "confianca",
        ])

    return pd.DataFrame(historico)


def limpar_historico_uploads():
    try:
        if supabase_disponivel():
            supabase = obter_supabase()

            registros = carregar_historico_uploads_supabase()

            for item in registros:
                item_id = item.get("id")

                if item_id:
                    (
                        supabase
                        .table("historico_uploads")
                        .delete()
                        .eq("id", item_id)
                        .execute()
                    )

            return True

    except Exception:
        pass

    return salvar_historico_uploads_local([])


def migrar_historico_uploads_local_para_supabase():
    historico_local = carregar_historico_uploads_local()

    resultado = {
        "total_lidos": 0,
        "migrados": 0,
        "erros": 0,
        "detalhes": [],
    }

    if not supabase_disponivel():
        resultado["erros"] += 1
        resultado["detalhes"].append({
            "arquivo": "",
            "status": "Erro",
            "erro": "Supabase não disponível."
        })
        return resultado

    supabase = obter_supabase()

    for item in historico_local:
        resultado["total_lidos"] += 1

        try:
            usuario = item.get("usuario", "")

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

            payload = {
                "nome_arquivo": item.get("nome_arquivo", ""),
                "data_upload": item.get("data_upload") or agora_iso(),
                "agravo_detectado": item.get("agravo_detectado", ""),
                "ficha_sugerida": item.get("ficha_sugerida", ""),
                "confianca": item.get("confianca", ""),
                "usuario": usuario,
                "usuario_id": usuario_id,
                "municipio": item.get("municipio", ""),
                "codigo_ibge_municipio": item.get("codigo_ibge_municipio") or None,
                "score_qualidade": item.get("score_qualidade", 0),
                "quantidade_registros": item.get("quantidade_registros", 0),
                "quantidade_colunas": item.get("quantidade_colunas", 0),
            }

            (
                supabase
                .table("historico_uploads")
                .insert(payload)
                .execute()
            )

            resultado["migrados"] += 1
            resultado["detalhes"].append({
                "arquivo": item.get("nome_arquivo", ""),
                "status": "Migrado",
                "erro": "",
            })

        except Exception as e:
            resultado["erros"] += 1
            resultado["detalhes"].append({
                "arquivo": item.get("nome_arquivo", ""),
                "status": "Erro",
                "erro": str(e),
            })

    return resultado
