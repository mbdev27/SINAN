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
        valores_agravo = " ".join(df["ID_AGRAVO"].dropna().astype(str).unique()[:20]).upper()

    if "Z20" in valores_agravo or "BIO" in nome or {"MATERIAL", "AGENTE", "CIRC_ACID"}.intersection(colunas):
        return {
            "agravo": "Acidente de Trabalho com Exposição a Material Biológico",
            "confianca": "Alta",
            "motivo": "Encontrados sinais compatíveis com exposição a material biológico.",
            "ficha_sugerida": "ACIDENTE DE TRABALHO COM EXPOSIÇÃO À MATERIAL BIOLÓGICO.pdf"
        }

    if "Y96" in valores_agravo or {"TIPO_ACID", "EVOLUCAO", "CAT", "LOCAL_ACID"}.intersection(colunas):
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
    dados = []

    for col in df.columns:
        vazios = df[col].isna().sum() + (df[col].astype(str).str.strip() == "").sum()
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
    if campos is None:
        campos = list(df.columns)

    campos_existentes = [c for c in campos if c in df.columns]

    if not campos_existentes or df.empty:
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

    duplicados = df[df["NU_NOTIFIC"].astype(str).duplicated(keep=False)]
    return duplicados.sort_values("NU_NOTIFIC")


def detectar_sexo_incompativel(df):
    if "CS_SEXO" not in df.columns:
        return pd.DataFrame()

    validos = ["M", "F", "I", "9"]
    return df[~df["CS_SEXO"].astype(str).str.upper().str.strip().isin(validos)]


def extrair_idade_sinan(valor):
    texto = str(valor).strip()

    if texto.endswith(".0"):
        texto = texto[:-2]

    numeros = re.sub(r"\D", "", texto)

    if not numeros:
        return pd.NA

    if len(numeros) > 3:
        idade = int(numeros[-3:])
    else:
        idade = int(numeros)

    if 0 <= idade <= 120:
        return idade

    return pd.NA


def detectar_idade_incompativel(df):
    if "DT_NASC" not in df.columns or "DT_ACID" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()
    temp["DT_NASC"] = pd.to_datetime(temp["DT_NASC"], errors="coerce")
    temp["DT_ACID"] = pd.to_datetime(temp["DT_ACID"], errors="coerce")

    temp["IDADE_CALC_AUDITORIA"] = temp.apply(
        lambda r: (
            r["DT_ACID"].year - r["DT_NASC"].year
            - ((r["DT_ACID"].month, r["DT_ACID"].day) < (r["DT_NASC"].month, r["DT_NASC"].day))
        )
        if pd.notna(r["DT_NASC"]) and pd.notna(r["DT_ACID"])
        else pd.NA,
        axis=1
    )

    problemas = temp[
        (temp["IDADE_CALC_AUDITORIA"].notna()) &
        (
            (temp["IDADE_CALC_AUDITORIA"] < 0) |
            (temp["IDADE_CALC_AUDITORIA"] > 120)
        )
    ]

    return problemas


def detectar_cid_incompativel(df, agravo):
    problemas = []

    if "ID_AGRAVO" not in df.columns:
        return pd.DataFrame()

    for idx, row in df.iterrows():
        cid = normalizar_texto(row.get("ID_AGRAVO", ""))

        if agravo == "Acidente de Trabalho Grave":
            if "Y96" not in cid and cid not in ["", "IGNORADO"]:
                problemas.append(row)

        if agravo == "Acidente de Trabalho com Exposição a Material Biológico":
            if "Z20" not in cid and cid not in ["", "IGNORADO"]:
                problemas.append(row)

    if not problemas:
        return pd.DataFrame()

    return pd.DataFrame(problemas)


def detectar_municipio_divergente(df):
    if "ID_MUNICIP" not in df.columns or "ID_MN_RESI" not in df.columns:
        return pd.DataFrame()

    return df[
        df["ID_MUNICIP"].astype(str).str.strip()
        != df["ID_MN_RESI"].astype(str).str.strip()
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


def gerar_auditoria_sinan(df, agravo="Acidente de Trabalho Grave"):
    campos_criticos = [
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
    }
