import pandas as pd
import streamlit as st

from utils.supabase_client import obter_supabase


def limpar_valor(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto == "" or texto.lower() in ["nan", "none", "null"]:
        return None

    return texto


def ler_csv_cnes(arquivo):
    arquivo.seek(0)

    return pd.read_csv(
        arquivo,
        sep=";",
        dtype=str,
        encoding="latin1",
        chunksize=5000,
        low_memory=False,
    )


def enviar_lote_supabase(tabela, registros, conflito):
    if not registros:
        return 0

    supabase = obter_supabase()

    total = 0

    for i in range(0, len(registros), 500):
        lote = registros[i:i + 500]

        (
            supabase
            .table(tabela)
            .upsert(
                lote,
                on_conflict=conflito
            )
            .execute()
        )

        total += len(lote)

    return total


def importar_municipios_cnes_csv(arquivo):
    resultado = {
        "total_lidos": 0,
        "importados": 0,
        "erros": 0,
        "detalhes": [],
    }

    try:
        for chunk in ler_csv_cnes(arquivo):
            registros = []

            for _, linha in chunk.iterrows():
                co_municipio = limpar_valor(linha.get("CO_MUNICIPIO"))

                if not co_municipio:
                    continue

                registros.append({
                    "co_municipio": co_municipio,
                    "no_municipio": limpar_valor(linha.get("NO_MUNICIPIO")),
                    "co_sigla_estado": limpar_valor(linha.get("CO_SIGLA_ESTADO")),
                    "tp_cadastro": limpar_valor(linha.get("TP_CADASTRO")),
                    "tp_pacto": limpar_valor(linha.get("TP_PACTO")),
                    "tp_envia": limpar_valor(linha.get("TP_ENVIA")),
                    "tp_envia_cnes": limpar_valor(linha.get("TP_ENVIA_CNES")),
                    "tp_cib_sas": limpar_valor(linha.get("TP_CIB_SAS")),
                    "tp_pleno_origem": limpar_valor(linha.get("TP_PLENO_ORIGEM")),
                    "tp_mac": limpar_valor(linha.get("TP_MAC")),
                    "nu_populacao": limpar_valor(linha.get("NU_POPULACAO")),
                    "nu_densidade": limpar_valor(linha.get("NU_DENSIDADE")),
                    "cmtp_inicio_mac": limpar_valor(linha.get("CMTP_INICIO_MAC")),
                })

            resultado["total_lidos"] += len(chunk)

            try:
                enviados = enviar_lote_supabase(
                    tabela="municipios_cnes",
                    registros=registros,
                    conflito="co_municipio"
                )

                resultado["importados"] += enviados

            except Exception as e:
                resultado["erros"] += 1
                resultado["detalhes"].append({
                    "arquivo": arquivo.name,
                    "status": "Erro no lote de municípios",
                    "erro": str(e),
                })

        resultado["detalhes"].append({
            "arquivo": arquivo.name,
            "status": "Concluído",
            "erro": "",
        })

    except Exception as e:
        resultado["erros"] += 1
        resultado["detalhes"].append({
            "arquivo": arquivo.name,
            "status": "Erro geral",
            "erro": str(e),
        })

    return resultado


def importar_estabelecimentos_cnes_csv(arquivo):
    resultado = {
        "total_lidos": 0,
        "importados": 0,
        "erros": 0,
        "detalhes": [],
    }

    try:
        for chunk in ler_csv_cnes(arquivo):
            registros = []

            for _, linha in chunk.iterrows():
                cnes = limpar_valor(linha.get("CO_CNES"))

                if not cnes:
                    continue

                nome_fantasia = (
                    limpar_valor(linha.get("NO_FANTASIA"))
                    or limpar_valor(linha.get("NO_RAZAO_SOCIAL"))
                    or f"CNES {cnes}"
                )

                registros.append({
                    "cnes": cnes,
                    "co_unidade": limpar_valor(linha.get("CO_UNIDADE")),
                    "nome_fantasia": nome_fantasia,
                    "razao_social": limpar_valor(linha.get("NO_RAZAO_SOCIAL")),
                    "cnpj_mantenedora": limpar_valor(linha.get("NU_CNPJ_MANTENEDORA")),
                    "cnpj": limpar_valor(linha.get("NU_CNPJ")),
                    "nome_logradouro": limpar_valor(linha.get("NO_LOGRADOURO")),
                    "numero_endereco": limpar_valor(linha.get("NU_ENDERECO")),
                    "complemento": limpar_valor(linha.get("NO_COMPLEMENTO")),
                    "bairro": limpar_valor(linha.get("NO_BAIRRO")),
                    "cep": limpar_valor(linha.get("CO_CEP")),
                    "telefone": limpar_valor(linha.get("NU_TELEFONE")),
                    "email": limpar_valor(linha.get("NO_EMAIL")),
                    "codigo_ibge_municipio": limpar_valor(linha.get("CO_MUNICIPIO_GESTOR")),
                    "municipio_gestor": limpar_valor(linha.get("CO_MUNICIPIO_GESTOR")),
                    "estado_gestor": limpar_valor(linha.get("CO_ESTADO_GESTOR")),
                    "uf": None,
                    "tipo_unidade": limpar_valor(linha.get("TP_UNIDADE")),
                    "natureza_juridica": limpar_valor(linha.get("CO_NATUREZA_JUR")),
                    "latitude": limpar_valor(linha.get("NU_LATITUDE")),
                    "longitude": limpar_valor(linha.get("NU_LONGITUDE")),
                    "tipo_gestao": limpar_valor(linha.get("TP_GESTAO")),
                    "data_atualizacao_cnes": limpar_valor(
                        linha.get("TO_CHAR(DT_ATUALIZACAO,'DD/MM/YYYY')")
                    ),
                    "arquivo_origem": arquivo.name,
                    "ativo": True,
                })

            resultado["total_lidos"] += len(chunk)

            try:
                enviados = enviar_lote_supabase(
                    tabela="unidades_cnes",
                    registros=registros,
                    conflito="cnes"
                )

                resultado["importados"] += enviados

            except Exception as e:
                resultado["erros"] += 1
                resultado["detalhes"].append({
                    "arquivo": arquivo.name,
                    "status": "Erro no lote de estabelecimentos",
                    "erro": str(e),
                })

        resultado["detalhes"].append({
            "arquivo": arquivo.name,
            "status": "Concluído",
            "erro": "",
        })

    except Exception as e:
        resultado["erros"] += 1
        resultado["detalhes"].append({
            "arquivo": arquivo.name,
            "status": "Erro geral",
            "erro": str(e),
        })

    return resultado


def contar_referencias_cnes():
    supabase = obter_supabase()

    municipios = (
        supabase
        .table("municipios_cnes")
        .select("co_municipio", count="exact")
        .limit(1)
        .execute()
    )

    unidades = (
        supabase
        .table("unidades_cnes")
        .select("cnes", count="exact")
        .limit(1)
        .execute()
    )

    return {
        "municipios_cnes": municipios.count or 0,
        "unidades_cnes": unidades.count or 0,
    }
