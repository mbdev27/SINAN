import pandas as pd
import numpy as np

from utils.cnes import (
    carregar_cnes,
    localizar_nome_por_cnes
)


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

    resultado = resultado.sort_values("Preenchimento (%)")

    return resultado.reset_index(drop=True)


def detectar_duplicidades(df):
    colunas = []

    for c in [
        "NM_PACIENT",
        "NM_MAE_PAC",
        "DT_OCOR",
        "DT_SIN_PRI",
        "DT_ACID",
        "DT_NOTIFIC"
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


def detectar_sexo_incompativel(df):
    if "CS_SEXO" not in df.columns:
        return pd.DataFrame()

    coluna_gestante = None

    for candidato in [
        "GESTANTE",
        "CS_GESTANT"
    ]:
        if candidato in df.columns:
            coluna_gestante = candidato
            break

    if coluna_gestante is None:
        return pd.DataFrame()

    sexo = (
        df["CS_SEXO"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    gest = (
        df[coluna_gestante]
        .astype(str)
        .str.strip()
    )

    inconsistentes = df[
        (sexo == "M")
        &
        (~gest.isin(["5", "6", "9", ""]))
    ]

    return inconsistentes.reset_index(drop=True)


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


def detectar_cid_incompativel(df):
    coluna_cid = None

    for c in [
        "CID10",
        "NU_CID10",
        "CID",
        "CID_PRINC",
        "ID_AGRAVO"
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

    vazios = cid.isin([
        "",
        "NAN",
        "NONE",
        "NULL",
        "IGNORADO"
    ])

    inconsistentes = df[
        (~vazios)
        &
        (
            (cid.str.len() < 3)
            |
            (~cid.str.match(r"^[A-Z][0-9]"))
        )
    ]

    return inconsistentes.reset_index(drop=True)


def detectar_municipio_divergente(df):
    col_not = None
    col_res = None

    for c in [
        "ID_MUNICIP",
        "ID_MUNICIP_NOT",
        "ID_MN_NOTI"
    ]:
        if c in df.columns:
            col_not = c
            break

    for c in [
        "ID_MN_RESI",
        "ID_MUNICIP_RES",
        "MUNICIPIO_RESIDENCIA"
    ]:
        if c in df.columns:
            col_res = c
            break

    if not col_not or not col_res:
        return pd.DataFrame()

    noti = (
        df[col_not]
        .astype(str)
        .str.strip()
    )

    resi = (
        df[col_res]
        .astype(str)
        .str.strip()
    )

    divergentes = df[
        (noti != "")
        &
        (resi != "")
        &
        (noti != resi)
    ]

    return divergentes.reset_index(drop=True)


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
            nome_unidade = "Base CNES não localizada ou inválida"
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
            "Classificação": classificar_qualidade(preenchimento)
        })

    resultado = pd.DataFrame(resultado)

    return (
        resultado
        .sort_values("Preenchimento (%)")
        .reset_index(drop=True)
    )


def inferir_agravo(df, nome_arquivo=""):
    colunas = [
        str(c).upper()
        for c in df.columns
    ]

    nome_arquivo = str(nome_arquivo).upper()

    ranking = []

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

    if "ACIDENTE" in nome_arquivo or "ACID" in nome_arquivo:
        score_acidente += 2
        encontrados_acidente.append("NOME_ARQUIVO")

    ranking.append({
        "Agravo": "Acidente de Trabalho Grave",
        "Score": score_acidente,
        "Colunas identificadas": ", ".join(encontrados_acidente)
    })

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

    if "VIOL" in nome_arquivo:
        score_violencia += 2
        encontrados_violencia.append("NOME_ARQUIVO")

    ranking.append({
        "Agravo": "Violência Interpessoal/Autoprovocada",
        "Score": score_violencia,
        "Colunas identificadas": ", ".join(encontrados_violencia)
    })

    score_arbovirose = 0
    termos_arbovirose = [
        "FEBRE",
        "MIALGIA",
        "CEFALEIA",
        "EXANTEMA",
        "SOROTIPO",
        "CLASSI_FIN",
        "CRITERIO",
        "ALRM",
        "GRAV",
        "RESUL_NS1",
        "RESUL_SORO",
        "DENGUE",
        "CHIK"
    ]
    encontrados_arbovirose = []

    for termo in termos_arbovirose:
        if any(termo in c for c in colunas):
            score_arbovirose += 1
            encontrados_arbovirose.append(termo)

    if (
        "DENG" in nome_arquivo
        or "CHIK" in nome_arquivo
        or "ARBOV" in nome_arquivo
    ):
        score_arbovirose += 3
        encontrados_arbovirose.append("NOME_ARQUIVO")

    ranking.append({
        "Agravo": "Dengue/Chikungunya",
        "Score": score_arbovirose,
        "Colunas identificadas": ", ".join(encontrados_arbovirose)
    })

    score_intoxicacao = 0
    termos_intoxicacao = [
        "TOX",
        "INTOX",
        "AGENTE",
        "AGENT",
        "EXPOS",
        "EXPO",
        "CIRCUNST",
        "CLASSI_FIN",
        "CRITERIO",
        "HOSPITALIZ",
        "DT_INTERNA",
        "EVOLUCAO",
        "TP_ATEND",
        "GRUPO_AGEN"
    ]
    encontrados_intoxicacao = []

    for termo in termos_intoxicacao:
        if any(termo in c for c in colunas):
            score_intoxicacao += 1
            encontrados_intoxicacao.append(termo)

    if (
        "IEXOG" in nome_arquivo
        or "INTOX" in nome_arquivo
        or "EXOG" in nome_arquivo
        or "TOX" in nome_arquivo
    ):
        score_intoxicacao += 4
        encontrados_intoxicacao.append("NOME_ARQUIVO")

    ranking.append({
        "Agravo": "Intoxicação Exógena",
        "Score": score_intoxicacao,
        "Colunas identificadas": ", ".join(encontrados_intoxicacao)
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
        "ficha_sugerida": f"{melhor['Agravo']}.pdf",
        "motivo": (
            f"Foram encontradas colunas compatíveis: "
            f"{melhor['Colunas identificadas']}"
        ),
        "ranking": ranking
    }


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
