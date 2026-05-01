import pandas as pd
import numpy as np

from utils.cnes import (
    carregar_cnes,
    localizar_nome_por_cnes
)


# ============================================================
# CLASSIFICAÇÃO DA QUALIDADE
# ============================================================

def classificar_qualidade(score):

    try:
        score = float(score)
    except Exception:
        return "⚪ Indefinida"

    if score >= 90:
        return "🟢 Excelente"

    if score >= 70:
        return "🟡 Boa"

    if score >= 50:
        return "🟠 Regular"

    return "🔴 Ruim"


# ============================================================
# SCORE GLOBAL DO BANCO
# ============================================================

def calcular_score_banco(df):

    if df.empty:
        return 0

    total_celulas = df.shape[0] * df.shape[1]

    if total_celulas == 0:
        return 0

    preenchidas = (
        df
        .replace("", np.nan)
        .notna()
        .sum()
        .sum()
    )

    score = (preenchidas / total_celulas) * 100

    return round(score, 1)


# ============================================================
# COLUNAS MAIS VAZIAS
# ============================================================

def detectar_colunas_vazias(df):

    resultado = []

    for coluna in df.columns:

        preenchimento = (
            df[coluna]
            .replace("", np.nan)
            .notna()
            .mean()
        ) * 100

        resultado.append({
            "Coluna": coluna,
            "Preenchimento (%)": round(preenchimento, 1),
            "Vazio (%)": round(100 - preenchimento, 1)
        })

    resultado = pd.DataFrame(resultado)

    resultado = resultado.sort_values(
        "Preenchimento (%)"
    )

    return resultado.reset_index(drop=True)


# ============================================================
# DUPLICIDADES
# ============================================================

def detectar_duplicidades(df):

    colunas = []

    for c in [
        "NM_PACIENT",
        "NM_MAE_PAC",
        "DT_OCOR",
        "DT_SIN_PRI"
    ]:
        if c in df.columns:
            colunas.append(c)

    if len(colunas) < 2:
        return pd.DataFrame()

    duplicados = df[
        df.duplicated(
            subset=colunas,
            keep=False
        )
    ]

    return duplicados.reset_index(drop=True)


# ============================================================
# SEXO INCOMPATÍVEL
# ============================================================

def detectar_sexo_incompativel(df):

    if "CS_SEXO" not in df.columns:
        return pd.DataFrame()

    if "GESTANTE" not in df.columns:
        return pd.DataFrame()

    sexo = (
        df["CS_SEXO"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    gest = (
        df["GESTANTE"]
        .astype(str)
        .str.strip()
    )

    inconsistentes = df[
        (sexo == "M")
        &
        (~gest.isin(["5", "6", "9", ""]))
    ]

    return inconsistentes.reset_index(drop=True)


# ============================================================
# IDADE INCOMPATÍVEL
# ============================================================

def detectar_idade_incompativel(df):

    coluna_idade = None

    for c in [
        "NU_IDADE_N",
        "IDADE",
        "IDADE_CALCULADA"
    ]:
        if c in df.columns:
            coluna_idade = c
            break

    if coluna_idade is None:
        return pd.DataFrame()

    idade = pd.to_numeric(
        df[coluna_idade],
        errors="coerce"
    )

    inconsistentes = df[
        (idade < 0)
        |
        (idade > 120)
    ]

    return inconsistentes.reset_index(drop=True)


# ============================================================
# CID INCOMPATÍVEL
# ============================================================

def detectar_cid_incompativel(df):

    coluna_cid = None

    for c in [
        "CID10",
        "NU_CID10",
        "CID",
        "CID_PRINC"
    ]:
        if c in df.columns:
            coluna_cid = c
            break

    if coluna_cid is None:
        return pd.DataFrame()

    cid = (
        df[coluna_cid]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    inconsistentes = df[
        (
            cid.str.len() < 3
        )
        |
        (
            ~cid.str.match(r"^[A-Z][0-9]")
        )
    ]

    return inconsistentes.reset_index(drop=True)


# ============================================================
# MUNICÍPIO DIVERGENTE
# ============================================================

def detectar_municipio_divergente(df):

    col_not = None
    col_res = None

    for c in [
        "ID_MN_RESI",
        "ID_MUNICIP"
    ]:
        if c in df.columns:
            col_res = c
            break

    for c in [
        "ID_MUNICIP_NOT",
        "ID_MUNICIP"
    ]:
        if c in df.columns:
            col_not = c
            break

    if not col_not or not col_res:
        return pd.DataFrame()

    divergentes = df[
        (
            df[col_not]
            .astype(str)
            .str.strip()
            !=
            df[col_res]
            .astype(str)
            .str.strip()
        )
    ]

    return divergentes.reset_index(drop=True)


# ============================================================
# INCOMPLETUDE POR UNIDADE
# ============================================================

def calcular_incompletude_por_unidade(df):

    col_unidade = None

    for candidato in [
        "ID_UNIDADE",
        "CO_UNI_NOT",
        "CNES",
        "UNIDADE_NOTIFICANTE",
        "NM_UNID_NOT"
    ]:
        if candidato in df.columns:
            col_unidade = candidato
            break

    if not col_unidade:

        return pd.DataFrame(columns=[
            "CNES",
            "Nome da unidade",
            "Registros",
            "Preenchimento (%)",
            "Classificação"
        ])

    cnes_base = carregar_cnes()

    resultado = []

    for unidade, grupo in df.groupby(col_unidade):

        unidade_codigo = "".join(
            c for c in str(unidade).replace(".0", "")
            if c.isdigit()
        )

        if cnes_base.empty:

            nome_unidade = (
                "Base CNES não localizada ou inválida"
            )

        else:

            nome_unidade = localizar_nome_por_cnes(
                unidade_codigo,
                cnes_base
            )

        preenchimento = calcular_score_banco(grupo)

        resultado.append({

            "CNES": unidade_codigo,

            "Nome da unidade": nome_unidade,

            "Registros": len(grupo),

            "Preenchimento (%)": preenchimento,

            "Classificação": classificar_qualidade(
                preenchimento
            )
        })

    resultado = pd.DataFrame(resultado)

    return (
        resultado
        .sort_values("Preenchimento (%)")
        .reset_index(drop=True)
    )


# ============================================================
# INFERIR AGRAVO
# ============================================================

def inferir_agravo(df, nome_arquivo=""):

    colunas = [
        str(c).upper()
        for c in df.columns
    ]

    ranking = []

    # --------------------------------------------------------
    # ACIDENTE DE TRABALHO GRAVE
    # --------------------------------------------------------

    score_acidente = 0

    termos_acidente = [
        "CID",
        "ACID",
        "OCUPA",
        "EVOLUCAO",
        "CAT",
        "TRAB"
    ]

    encontrados_acidente = []

    for termo in termos_acidente:

        if any(termo in c for c in colunas):
            score_acidente += 1
            encontrados_acidente.append(termo)

    ranking.append({
        "Agravo": "Acidente de Trabalho Grave",
        "Score": score_acidente,
        "Colunas identificadas": ", ".join(
            encontrados_acidente
        )
    })

    # --------------------------------------------------------
    # VIOLÊNCIA
    # --------------------------------------------------------

    score_violencia = 0

    termos_violencia = [
        "VIOL",
        "AGRESS",
        "AUTOR",
        "SEXUAL",
        "LES_AUTOP",
        "REL_TRAB"
    ]

    encontrados_violencia = []

    for termo in termos_violencia:

        if any(termo in c for c in colunas):
            score_violencia += 1
            encontrados_violencia.append(termo)

    ranking.append({
        "Agravo": "Violência Interpessoal/Autoprovocada",
        "Score": score_violencia,
        "Colunas identificadas": ", ".join(
            encontrados_violencia
        )
    })

    ranking = sorted(
        ranking,
        key=lambda x: x["Score"],
        reverse=True
    )

    melhor = ranking[0]

    score = melhor["Score"]

    if score >= 5:
        confianca = "Alta"

    elif score >= 3:
        confianca = "Média"

    else:
        confianca = "Baixa"

    return {

        "agravo": melhor["Agravo"],

        "confianca": confianca,

        "score": score,

        "ficha_sugerida": (
            f"{melhor['Agravo']}.pdf"
        ),

        "motivo": (
            f"Foram encontradas colunas compatíveis: "
            f"{melhor['Colunas identificadas']}"
        ),

        "ranking": ranking
    }


# ============================================================
# AUDITORIA GERAL
# ============================================================

def gerar_auditoria_sinan(df, agravo=None):

    score = calcular_score_banco(df)

    return {

        "score_banco": score,

        "qualidade_banco": classificar_qualidade(score),

        "colunas_vazias": detectar_colunas_vazias(df),

        "duplicidades": detectar_duplicidades(df),

        "sexo_incompativel": detectar_sexo_incompativel(df),

        "idade_incompativel": detectar_idade_incompativel(df),

        "cid_incompativel": detectar_cid_incompativel(df),

        "municipio_divergente": detectar_municipio_divergente(df),

        "incompletude_unidade": calcular_incompletude_por_unidade(df),
    }
