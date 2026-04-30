import pandas as pd
import re


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip().upper()


def campo_preenchido(valor):
    texto = normalizar_texto(valor)
    return texto not in ["", "NAN", "NONE", "NAT", "NULL", "IGNORADO"]


def inferir_agravo(df, nome_arquivo=""):
    colunas = set(df.columns)
    nome = nome_arquivo.upper()

    valores_agravo = ""
    if "ID_AGRAVO" in df.columns:
        valores_agravo = " ".join(
            df["ID_AGRAVO"]
            .dropna()
            .astype(str)
            .unique()[:20]
        ).upper()

    sinais_biologico = {
        "MATERIAL",
        "AGENTE",
        "CIRC_ACID",
        "CIRCUNSTAN",
        "SIT_VACIN",
        "FONTE",
        "EPI_LUVA",
        "EPI_AVENTAL"
    }

    sinais_grave = {
        "TIPO_ACID",
        "EVOLUCAO",
        "CAT",
        "LOCAL_ACID",
        "PART_CORP1",
        "CID_LESAO"
    }

    if (
        "Z20" in valores_agravo
        or "BIO" in nome
        or "ACBIO" in nome
        or len(sinais_biologico.intersection(colunas)) >= 2
    ):
        return {
            "agravo": "Acidente de Trabalho com Exposição a Material Biológico",
            "confianca": "Alta",
            "motivo": "Encontrados sinais compatíveis com exposição a material biológico.",
            "ficha_sugerida": "ACIDENTE DE TRABALHO COM EXPOSIÇÃO À MATERIAL BIOLÓGICO.pdf"
        }

    if (
        "Y96" in valores_agravo
        or len(sinais_grave.intersection(colunas)) >= 2
    ):
        return {
            "agravo": "Acidente de Trabalho Grave",
            "confianca": "Alta",
            "motivo": "Encontrados campos compatíveis com Acidente de Trabalho Grave.",
            "ficha_sugerida": "DRT_Acidente_Trabalho_Grave.pdf"
        }

    return {
        "agravo": "Não identificado",
        "confianca": "Baixa",
        "motivo": "Não foi possível reconhecer o agravo automaticamente.",
        "ficha_sugerida": "Selecionar manualmente"
    }


def detectar_colunas_vazias(df):
    if df.empty:
        return pd.DataFrame()

    dados = []

    for col in df.columns:
        serie = df[col].astype(str).str.strip()
        vazios = (
            df[col].isna().sum()
            + (serie == "").sum()
            + serie.str.upper().isin(["NAN", "NONE", "NAT", "NULL", "IGNORADO"]).sum()
        )

        percentual = round((vazios / len(df)) * 100, 1) if len(df) else 0

        if percentual >= 90:
            status = "🚩 Quase vazia"
        elif percentual >= 50:
            status = "🟨 Muito incompleta"
        else:
            status = "🟩 Utilizável"

        dados.append({
            "Coluna": col,
            "Vazios": int(vazios),
            "% vazio": percentual,
            "Status": status
        })

    return pd.DataFrame(dados).sort_values("% vazio", ascending=False)


def calcular_completude_banco(df, campos=None):
    if df.empty:
        return 0

    if campos is None:
        campos = list(df.columns)

    campos_existentes = [c for c in campos if c in df.columns]

    if not campos_existentes:
        return 0

    total_celulas = len(df) * len(campos_existentes)
    preenchidas = 0

    for col in campos_existentes:
        preenchidas += df[col].apply(campo_preenchido).sum()

    return round((preenchidas / total_celulas) * 100, 1)


def qualidade_banco(score):
    if score < 70:
        return "🚩 Ruim"
    if score < 90:
        return "🟨 Mediana"
    return "🟩 Boa"


def detectar_duplicidades(df):
    if "NU_NOTIFIC" not in df.columns:
        return pd.DataFrame()

    duplicados = df[
        df["NU_NOTIFIC"]
        .astype(str)
        .duplicated(keep=False)
    ]

    return duplicados.sort_values("NU_NOTIFIC")


def detectar_sexo_incompativel(df):
    if "CS_SEXO" not in df.columns:
        return pd.DataFrame()

    validos = ["M", "F", "I", "9", "IGNORADO"]

    return df[
        ~df["CS_SEXO"]
        .astype(str)
        .str.upper()
        .str.strip()
        .isin(validos)
    ]


def detectar_idade_incompativel(df):
    if "DT_NASC" not in df.columns or "DT_ACID" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()

    temp["DT_NASC"] = pd.to_datetime(temp["DT_NASC"], errors="coerce")
    temp["DT_ACID"] = pd.to_datetime(temp["DT_ACID"], errors="coerce")

    def calcular(row):
        if pd.isna(row["DT_NASC"]) or pd.isna(row["DT_ACID"]):
            return pd.NA

        idade = row["DT_ACID"].year - row["DT_NASC"].year

        if (row["DT_ACID"].month, row["DT_ACID"].day) < (
            row["DT_NASC"].month,
            row["DT_NASC"].day
        ):
            idade -= 1

        return idade

    temp["IDADE_CALC_AUDITORIA"] = temp.apply(calcular, axis=1)

    problemas = temp[
        (temp["IDADE_CALC_AUDITORIA"].notna())
        & (
            (temp["IDADE_CALC_AUDITORIA"] < 0)
            | (temp["IDADE_CALC_AUDITORIA"] > 120)
        )
    ]

    return problemas


def detectar_cid_incompativel(df, agravo):
    if "ID_AGRAVO" not in df.columns:
        return pd.DataFrame()

    problemas = []

    for _, row in df.iterrows():
        cid = normalizar_texto(row.get("ID_AGRAVO", ""))

        if cid in ["", "IGNORADO", "NAN", "NONE", "NAT", "NULL"]:
            continue

        if agravo == "Acidente de Trabalho Grave":
            if "Y96" not in cid:
                problemas.append(row)

        elif agravo == "Acidente de Trabalho com Exposição a Material Biológico":
            if "Z20" not in cid:
                problemas.append(row)

    if not problemas:
        return pd.DataFrame()

    return pd.DataFrame(problemas)


def detectar_municipio_divergente(df):
    if "ID_MUNICIP" not in df.columns or "ID_MN_RESI" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()

    temp["ID_MUNICIP_AUD"] = temp["ID_MUNICIP"].astype(str).str.strip()
    temp["ID_MN_RESI_AUD"] = temp["ID_MN_RESI"].astype(str).str.strip()

    return temp[
        (temp["ID_MUNICIP_AUD"] != "")
        & (temp["ID_MN_RESI_AUD"] != "")
        & (temp["ID_MUNICIP_AUD"] != temp["ID_MN_RESI_AUD"])
    ]


def incompletude_por_unidade(df, campos_criticos):
    if "ID_UNIDADE" not in df.columns:
        return pd.DataFrame()

    dados = []

    for unidade, grupo in df.groupby("ID_UNIDADE"):
        score = calcular_completude_banco(grupo, campos_criticos)

        dados.append({
            "Unidade": unidade,
            "Registros": len(grupo),
            "% preenchimento": score,
            "Qualidade": qualidade_banco(score)
        })

    return pd.DataFrame(dados).sort_values("% preenchimento")


def campos_criticos_por_agravo(agravo):
    if agravo == "Acidente de Trabalho com Exposição a Material Biológico":
        return [
            "NU_NOTIFIC",
            "DT_NOTIFIC",
            "ID_MUNICIP",
            "ID_UNIDADE",
            "DT_ACID",
            "NM_PACIENT",
            "DT_NASC",
            "CS_SEXO",
            "CS_RACA",
            "CS_ESCOL_N",
            "ID_OCUPA_N",
            "SIT_TRAB",
            "MATERIAL",
            "AGENTE",
            "CIRC_ACID",
            "EVOLUCAO"
        ]

    return [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_ACID",
        "NM_PACIENT",
        "DT_NASC",
        "CS_SEXO",
        "CS_RACA",
        "CS_ESCOL_N",
        "ID_OCUPA_N",
        "SIT_TRAB",
        "LOCAL_ACID",
        "TIPO_ACID",
        "EVOLUCAO"
    ]


def gerar_auditoria_sinan(df, agravo="Acidente de Trabalho Grave"):
    campos_criticos = campos_criticos_por_agravo(agravo)

    score = calcular_completude_banco(df, campos_criticos)

    return {
        "score_banco": score,
        "qualidade_banco": qualidade_banco(score),
        "colunas_vazias": detectar_colunas_vazias(df),
        "duplicidades": detectar_duplicidades(df),
        "sexo_incompativel": detectar_sexo_incompativel(df),
        "idade_incompativel": detectar_idade_incompativel(df),
        "cid_incompativel": detectar_cid_incompativel(df, agravo),
        "municipio_divergente": detectar_municipio_divergente(df),
        "incompletude_unidade": incompletude_por_unidade(df, campos_criticos),
        "campos_criticos": campos_criticos,
    }
