import json
from pathlib import Path
from datetime import datetime

import pandas as pd


ARQUIVO_HISTORICO_UPLOADS = Path("data/historico_uploads.json")


def garantir_pasta_data():
    ARQUIVO_HISTORICO_UPLOADS.parent.mkdir(parents=True, exist_ok=True)


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def carregar_historico_uploads():
    garantir_pasta_data()

    if not ARQUIVO_HISTORICO_UPLOADS.exists():
        return []

    try:
        with open(ARQUIVO_HISTORICO_UPLOADS, "r", encoding="utf-8") as f:
            dados = json.load(f)

        if isinstance(dados, list):
            return dados

        return []

    except Exception:
        return []


def salvar_historico_uploads(historico):
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
):
    historico = carregar_historico_uploads()

    registro = {
        "id": len(historico) + 1,
        "nome_arquivo": nome_arquivo,
        "data_upload": agora(),
        "agravo_detectado": agravo,
        "usuario": usuario,
        "municipio": municipio,
        "score_qualidade": score_qualidade,
        "quantidade_registros": quantidade_registros,
        "quantidade_colunas": quantidade_colunas,
        "ficha_sugerida": ficha_sugerida,
        "confianca": confianca,
    }

    historico.append(registro)

    ok = salvar_historico_uploads(historico)

    return ok, registro


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
    return salvar_historico_uploads([])
