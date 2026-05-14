import json
from urllib.request import urlopen

import pandas as pd

from utils.supabase_client import obter_supabase


URL_MUNICIPIOS_IBGE = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
)


def baixar_municipios_ibge():
    with urlopen(URL_MUNICIPIOS_IBGE, timeout=60) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    municipios = []

    for item in dados:
        microrregiao = item.get("microrregiao", {})
        mesorregiao = microrregiao.get("mesorregiao", {})
        uf = mesorregiao.get("UF", {})
        regiao = uf.get("regiao", {})

        municipios.append({
            "codigo_ibge": str(item.get("id", "")),
            "nome": item.get("nome", ""),
            "uf": uf.get("sigla", ""),
            "regional_saude": None,
            "ativo": True,
        })

    return municipios


def importar_municipios_ibge_para_supabase():
    supabase = obter_supabase()
    municipios = baixar_municipios_ibge()

    resultado = {
        "total_lidos": len(municipios),
        "importados": 0,
        "erros": 0,
        "detalhes": [],
    }

    for municipio in municipios:
        try:
            (
                supabase
                .table("municipios")
                .upsert(
                    municipio,
                    on_conflict="codigo_ibge"
                )
                .execute()
            )

            resultado["importados"] += 1
            resultado["detalhes"].append({
                "codigo_ibge": municipio["codigo_ibge"],
                "municipio": municipio["nome"],
                "uf": municipio["uf"],
                "status": "Importado/atualizado",
                "erro": "",
            })

        except Exception as e:
            resultado["erros"] += 1
            resultado["detalhes"].append({
                "codigo_ibge": municipio.get("codigo_ibge", ""),
                "municipio": municipio.get("nome", ""),
                "uf": municipio.get("uf", ""),
                "status": "Erro",
                "erro": str(e),
            })

    return resultado


def listar_municipios_supabase():
    supabase = obter_supabase()

    resposta = (
        supabase
        .table("municipios")
        .select("codigo_ibge, nome, uf, regional_saude, ativo")
        .order("uf")
        .order("nome")
        .execute()
    )

    return resposta.data or []


def municipios_para_dataframe():
    dados = listar_municipios_supabase()

    if not dados:
        return pd.DataFrame(columns=[
            "codigo_ibge",
            "nome",
            "uf",
            "regional_saude",
            "ativo",
        ])

    return pd.DataFrame(dados)
