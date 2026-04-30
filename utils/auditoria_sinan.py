import pandas as pd
import re
import unicodedata

from config.catalogo_agravos import CATALOGO_AGRAVOS


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    return texto


def campo_preenchido(valor):
    texto = normalizar_texto(valor)
    return texto not in ["", "NAN", "NONE", "NAT", "NULL", "IGNORADO"]


def texto_do_banco(df):
    partes = []

    if "ID_AGRAVO" in df.columns:
        partes.append(
            " ".join(
                df["ID_AGRAVO"]
                .dropna()
                .astype(str)
                .unique()[:30]
            )
        )

    return normalizar_texto(" ".join(partes))


def inferir_agravo(df, nome_arquivo=""):
    nome_norm = normalizar_texto(nome_arquivo)
    colunas = set([normalizar_texto(c) for c in df.columns])
    texto_agravo = texto_do_banco(df)

    resultados = []

    for item in CATALOGO_AGRAVOS:
        score = 0
        motivos = []

        for cid in item.get("cids", []):
            cid_norm = normalizar_texto(cid).replace(".", "")
            texto_norm = texto_agravo.replace(".", "")

            if cid_norm and cid_norm in texto_norm:
                score += 60
                motivos.append(f"CID compatível: {cid}")

        for palavra in item.get("palavras", []):
            palavra_norm = normalizar_texto(palavra)

            if palavra_norm and palavra_norm in nome_norm:
                score += 30
                motivos.append(f"Nome do arquivo sugere: {palavra}")

            if palavra_norm and palavra_norm in texto_agravo:
                score += 20
                motivos.append(f"Texto do agravo contém: {palavra}")

        campos_encontrados = []

        for campo in item.get("campos", []):
            campo_norm = normalizar_texto(campo)

            for col in colunas:
                if campo_norm == col or campo_norm in col or col in campo_norm:
                    campos_encontrados.append(campo)
                    break

        if campos_encontrados:
            pontos = min(len(campos_encontrados) * 8, 40)
            score += pontos
            motivos.append(
                f"Campos compatíveis encontrados: {', '.join(campos_encontrados[:8])}"
            )

        resultados.append({
            "agravo": item["agravo"],
            "score": score,
            "ficha_sugerida": item["ficha_pdf"],
            "motivo": "; ".join(motivos) if motivos else "Sem evidências fortes.",
        })

    resultados = sorted(resultados, key=lambda x: x["score"], reverse=True)

    melhor = resultados[0] if resultados else None

    if not melhor or melhor["score"] <= 0:
        return {
            "agravo": "Não identificado",
            "confianca": "Baixa",
            "score": 0,
            "motivo": "Não foi possível reconhecer o agravo automaticamente.",
            "ficha_sugerida": "Selecionar manualmente",
            "ranking": resultados[:5],
        }

    if melhor["score"] >= 80:
        confianca = "Alta"
    elif melhor["score"] >= 40:
        confianca = "Média"
    else:
        confianca = "Baixa"

    return {
        "agravo": melhor["agravo"],
        "confianca": confianca,
        "score": melhor["score"],
        "motivo": melhor["motivo"],
        "ficha_sugerida": melhor["ficha_sugerida"],
        "ranking": resultados[:5],
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
    data_evento = None

    for candidato in ["DT_ACID", "DT_SIN_PRI", "DT_DIAG", "DT_NOTIFIC"]:
        if candidato in df.columns:
            data_evento = candidato
            break

    if "DT_NASC" not in df.columns or data_evento is None:
        return pd.DataFrame()

    temp = df.copy()

    temp["DT_NASC"] = pd.to_datetime(temp["DT_NASC"], errors="coerce")
    temp[data_evento] = pd.to_datetime(temp[data_evento], errors="coerce")

    def calcular(row):
        if pd.isna(row["DT_NASC"]) or pd.isna(row[data_evento]):
            return pd.NA

        idade = row[data_evento].year - row["DT_NASC"].year

        if (row[data_evento].month, row[data_evento].day) < (
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


def cids_esperados_por_agravo(agravo):
    for item in CATALOGO_AGRAVOS:
        if item["agravo"] == agravo:
            return item.get("cids", [])

    return []


def detectar_cid_incompativel(df, agravo):
    if "ID_AGRAVO" not in df.columns:
        return pd.DataFrame()

    esperados = cids_esperados_por_agravo(agravo)

    if not esperados:
        return pd.DataFrame()

    problemas = []

    esperados_norm = [
        normalizar_texto(cid).replace(".", "")
        for cid in esperados
    ]

    for _, row in df.iterrows():
        cid = normalizar_texto(row.get("ID_AGRAVO", "")).replace(".", "")

        if cid in ["", "IGNORADO", "NAN", "NONE", "NAT", "NULL"]:
            continue

        if not any(esperado in cid for esperado in esperados_norm):
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


def campos_criticos_por_agravo(agravo):
    base = [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "ID_AGRAVO",
        "NM_PACIENT",
        "DT_NASC",
        "CS_SEXO",
        "CS_RACA",
        "CS_ESCOL_N",
        "NM_MAE_PAC",
        "ID_MN_RESI",
    ]

    extras = {
        "Acidente de Trabalho Grave": [
            "DT_ACID", "ID_OCUPA_N", "SIT_TRAB", "LOCAL_ACID", "TIPO_ACID", "EVOLUCAO"
        ],
        "Acidente de Trabalho com Exposição a Material Biológico": [
            "DT_ACID", "ID_OCUPA_N", "SIT_TRAB", "MATERIAL", "AGENTE", "CIRC_ACID"
        ],
        "Tuberculose": [
            "TIPO_ENTRA", "FORMA", "BACILOSC", "CULTURA", "HIV"
        ],
        "Hanseníase": [
            "NU_LESOES", "CLASS_OP", "MODO_ENTR", "MODO_DETEC"
        ],
        "Violência Interpessoal/Autoprovocada": [
            "LOCAL_OCOR", "LES_AUTOP", "VIOL_FISIC", "VIOL_SEXU", "MEIO_AGRE"
        ],
        "Sífilis Congênita": [
            "IDADE_MAE", "PRE_NATAL", "TRAT_MAE", "PARC_TRAT"
        ],
        "Sífilis em Gestante": [
            "PRE_NATAL", "CLASS_CLI", "TESTE_TREP", "ESQUEMA"
        ],
    }

    return base + extras.get(agravo, [])


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
