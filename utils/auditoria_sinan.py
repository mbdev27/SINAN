import pandas as pd
import numpy as np


# =========================================================
# CAMPOS OBRIGATÓRIOS — ACIDENTE DE TRABALHO GRAVE
# =========================================================

CAMPOS_OBRIGATORIOS_AT_GRAVE = [
    "NU_NOTIFIC",
    "DT_NOTIFIC",
    "DT_ACID",
    "NM_PACIENT",
    "NM_MAE_PAC",
    "CS_SEXO",
    "DT_NASC",
    "ID_MN_RESI",
]


# =========================================================
# AGRAVOS SUPORTADOS
# =========================================================

AGRAVOS_MAP = {
    "Acidente de Trabalho Grave": {
        "campos_obrigatorios": CAMPOS_OBRIGATORIOS_AT_GRAVE
    }
}


# =========================================================
# NORMALIZAÇÃO
# =========================================================

def normalizar_vazio(valor):
    """
    Padroniza valores vazios.
    """

    if pd.isna(valor):
        return np.nan

    valor = str(valor).strip()

    if valor in ["", "nan", "None", "NULL", "null", "NaT"]:
        return np.nan

    return valor


# =========================================================
# SCORE DE PREENCHIMENTO
# =========================================================

def calcular_percentual_preenchimento(df):
    """
    Calcula percentual de preenchimento de cada coluna.
    """

    resultado = []

    total = len(df)

    for col in df.columns:

        preenchidos = (
            df[col]
            .apply(normalizar_vazio)
            .notna()
            .sum()
        )

        percentual = round((preenchidos / total) * 100, 2) if total else 0

        resultado.append({
            "Campo": col,
            "Preenchidos": preenchidos,
            "Total": total,
            "Percentual": percentual
        })

    return (
        pd.DataFrame(resultado)
        .sort_values("Percentual")
        .reset_index(drop=True)
    )


# =========================================================
# SCORE GLOBAL DO BANCO
# =========================================================

def calcular_score_banco(df):

    preenchimento = calcular_percentual_preenchimento(df)

    if preenchimento.empty:
        return 0

    score = preenchimento["Percentual"].mean()

    return round(score, 2)


# =========================================================
# CLASSIFICAÇÃO DA QUALIDADE
# =========================================================

def classificar_qualidade(score):

    if score >= 90:
        return "🟢 Excelente"

    elif score >= 70:
        return "🟡 Mediana"

    return "🔴 Ruim"


# =========================================================
# CAMPOS CRÍTICOS VAZIOS
# =========================================================

def detectar_campos_criticos_vazios(df, agravo=None):

    campos = []

    if agravo in AGRAVOS_MAP:
        campos = AGRAVOS_MAP[agravo]["campos_obrigatorios"]

    inconsistencias = []

    for campo in campos:

        if campo not in df.columns:
            inconsistencias.append({
                "Campo": campo,
                "Problema": "Campo obrigatório ausente"
            })
            continue

        vazios = (
            df[campo]
            .apply(normalizar_vazio)
            .isna()
            .sum()
        )

        percentual = round((vazios / len(df)) * 100, 2) if len(df) else 0

        if vazios > 0:

            inconsistencias.append({
                "Campo": campo,
                "Registros vazios": vazios,
                "Percentual vazio": percentual
            })

    return pd.DataFrame(inconsistencias)


# =========================================================
# DETECTAR COLUNAS MAIS VAZIAS
# =========================================================

def detectar_colunas_vazias(df):

    preenchimento = calcular_percentual_preenchimento(df)

    preenchimento["Vazios (%)"] = 100 - preenchimento["Percentual"]

    return (
        preenchimento[
            ["Campo", "Vazios (%)"]
        ]
        .sort_values("Vazios (%)", ascending=False)
        .reset_index(drop=True)
    )


# =========================================================
# DETECTAR DUPLICIDADES
# =========================================================

def detectar_duplicidades(df):
    """
    Detecta possível duplicidade por:
    - Nome do paciente
    - Nome da mãe
    - Data do acidente / sintomas / ocorrência
    """

    col_nome = "NM_PACIENT" if "NM_PACIENT" in df.columns else None

    col_mae = "NM_MAE_PAC" if "NM_MAE_PAC" in df.columns else None

    col_data = None

    for candidato in [
        "DT_ACID",
        "DT_SIN_PRI",
        "DT_OCOR",
        "DT_NOTIFIC"
    ]:

        if candidato in df.columns:
            col_data = candidato
            break

    if not col_nome or not col_mae or not col_data:
        return pd.DataFrame()

    temp = df.copy()

    temp["_NOME_DUP"] = (
        temp[col_nome]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    temp["_MAE_DUP"] = (
        temp[col_mae]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    temp["_DATA_DUP"] = (
        pd.to_datetime(
            temp[col_data],
            errors="coerce"
        )
        .dt.date
        .astype(str)
    )

    duplicados = temp[
        temp.duplicated(
            subset=[
                "_NOME_DUP",
                "_MAE_DUP",
                "_DATA_DUP"
            ],
            keep=False
        )
    ]

    return duplicados.drop(
        columns=[
            "_NOME_DUP",
            "_MAE_DUP",
            "_DATA_DUP"
        ],
        errors="ignore"
    )


# =========================================================
# SEXO INCOMPATÍVEL
# =========================================================

def detectar_sexo_incompativel(df):

    if "CS_SEXO" not in df.columns:
        return pd.DataFrame()

    col = df["CS_SEXO"].astype(str).str.upper()

    invalidos = ~col.isin(["M", "F", "I"])

    return df[invalidos]


# =========================================================
# IDADE INCOMPATÍVEL
# =========================================================

def detectar_idade_incompativel(df):

    colunas_possiveis = [
        "IDADE",
        "NU_IDADE_N",
        "IDADE_CALCULADA"
    ]

    coluna = None

    for c in colunas_possiveis:
        if c in df.columns:
            coluna = c
            break

    if not coluna:
        return pd.DataFrame()

    idade = pd.to_numeric(df[coluna], errors="coerce")

    inconsistentes = (
        (idade < 0) |
        (idade > 120)
    )

    return df[inconsistentes]


# =========================================================
# CID INCOMPATÍVEL
# =========================================================

def detectar_cid_incompativel(df):

    if "CID10" not in df.columns:
        return pd.DataFrame()

    cid = (
        df["CID10"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    invalidos = ~cid.str.match(r"^[A-Z][0-9]{2}")

    return df[invalidos]


# =========================================================
# MUNICÍPIO DIVERGENTE
# =========================================================

def detectar_municipio_divergente(df):

    col_not = None
    col_res = None

    candidatos_not = [
        "ID_MN_NOTI",
        "MUNICIPIO_NOTIFICACAO"
    ]

    candidatos_res = [
        "ID_MN_RESI",
        "MUNICIPIO_RESIDENCIA"
    ]

    for c in candidatos_not:
        if c in df.columns:
            col_not = c
            break

    for c in candidatos_res:
        if c in df.columns:
            col_res = c
            break

    if not col_not or not col_res:
        return pd.DataFrame()

    divergente = (
        df[col_not]
        .astype(str)
        .str.strip()
        !=
        df[col_res]
        .astype(str)
        .str.strip()
    )

    return df[divergente]


# =========================================================
# INCOMPLETUDE POR UNIDADE
# =========================================================

def calcular_incompletude_por_unidade(df):

    col_unidade = None

    for candidato in [
        "ID_UNIDADE",
        "UNIDADE_NOTIFICANTE",
        "NM_UNID_NOT"
    ]:

        if candidato in df.columns:
            col_unidade = candidato
            break

    if not col_unidade:
        return pd.DataFrame()

    resultado = []

    for unidade, grupo in df.groupby(col_unidade):

        preenchimento = calcular_score_banco(grupo)

        resultado.append({
            "Unidade": unidade,
            "Percentual de preenchimento": preenchimento,
            "Classificação": classificar_qualidade(preenchimento)
        })

    return (
        pd.DataFrame(resultado)
        .sort_values("Percentual de preenchimento")
        .reset_index(drop=True)
    )


# =========================================================
# DETECÇÃO INTELIGENTE DE AGRAVO
# =========================================================

def inferir_agravo(df, nome_arquivo=""):

    nome_arquivo = str(nome_arquivo).upper()

    ranking = []

    regras = {
        "Acidente de Trabalho Grave": [
            "DT_ACID",
            "CAT",
            "TP_ACID",
            "LOCAL_ACID",
            "SIT_TRAB",
            "OCUPACAO",
            "ID_OCUPA_N"
        ]
    }

    melhor_agravo = "Desconhecido"
    maior_score = 0

    for agravo, colunas_chave in regras.items():

        score = 0

        presentes = []

        for coluna in colunas_chave:

            if coluna in df.columns:
                score += 1
                presentes.append(coluna)

        if "ACIDENTE" in nome_arquivo:
            score += 2

        ranking.append({
            "Agravo": agravo,
            "Score": score,
            "Colunas identificadas": ", ".join(presentes)
        })

        if score > maior_score:
            maior_score = score
            melhor_agravo = agravo

    ranking = sorted(
        ranking,
        key=lambda x: x["Score"],
        reverse=True
    )

    if maior_score >= 6:
        confianca = "Alta"

    elif maior_score >= 3:
        confianca = "Média"

    else:
        confianca = "Baixa"

    return {
        "agravo": melhor_agravo,
        "confianca": confianca,
        "motivo": f"{maior_score} características compatíveis identificadas.",
        "ranking": ranking
    }


# =========================================================
# AUDITORIA COMPLETA
# =========================================================

def gerar_auditoria_sinan(df, agravo=None):

    score = calcular_score_banco(df)

    return {

        "score_banco": score,

        "qualidade_banco": classificar_qualidade(score),

        "preenchimento": calcular_percentual_preenchimento(df),

        "campos_criticos": detectar_campos_criticos_vazios(df, agravo),

        "colunas_vazias": detectar_colunas_vazias(df),

        "duplicidades": detectar_duplicidades(df),

        "sexo_incompativel": detectar_sexo_incompativel(df),

        "idade_incompativel": detectar_idade_incompativel(df),

        "cid_incompativel": detectar_cid_incompativel(df),

        "municipio_divergente": detectar_municipio_divergente(df),

        "incompletude_unidade": calcular_incompletude_por_unidade(df),
    }
