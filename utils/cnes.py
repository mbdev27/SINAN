import os
import pandas as pd
import unicodedata


CAMINHOS_CNES = [
    "data/cnes_ipojuca.xlsx",
    "data/CNES Ipojuca.xlsx",
    "CNES Ipojuca.xlsx",
]


def normalizar_texto(txt):
    if pd.isna(txt):
        return ""

    txt = str(txt).strip().upper()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))

    return txt


def limpar_codigo(valor):
    if pd.isna(valor):
        return ""

    valor = str(valor).strip()
    valor = valor.replace(".0", "")

    somente_digitos = "".join([c for c in valor if c.isdigit()])

    return somente_digitos


def detectar_coluna(df, candidatos):
    for col in df.columns:
        col_norm = normalizar_texto(col)

        for candidato in candidatos:
            cand_norm = normalizar_texto(candidato)

            if cand_norm == col_norm or cand_norm in col_norm:
                return col

    return None


def carregar_cnes(caminho=None):
    caminhos = [caminho] if caminho else CAMINHOS_CNES

    arquivo = None

    for c in caminhos:
        if c and os.path.exists(c):
            arquivo = c
            break

    if not arquivo:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    try:
        df = pd.read_excel(arquivo, dtype=str)
    except Exception:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    df.columns = [str(c).strip() for c in df.columns]

    col_cnes = detectar_coluna(
        df,
        [
            "CNES",
            "CODIGO CNES",
            "CÓDIGO CNES",
            "COD_CNES",
            "COD CNES",
            "ID_UNIDADE",
            "CODIGO DA UNIDADE",
            "CÓDIGO DA UNIDADE",
        ]
    )

    col_nome = detectar_coluna(
        df,
        [
            "NOME",
            "NOME UNIDADE",
            "NOME DA UNIDADE",
            "UNIDADE",
            "ESTABELECIMENTO",
            "NO_FANTASIA",
            "NOME FANTASIA",
            "RAZAO SOCIAL",
            "RAZÃO SOCIAL",
        ]
    )

    if not col_cnes or not col_nome:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    cnes = df[[col_cnes, col_nome]].copy()
    cnes.columns = ["CNES", "NOME_UNIDADE"]

    cnes["CNES"] = cnes["CNES"].apply(limpar_codigo)

    cnes["NOME_UNIDADE"] = (
        cnes["NOME_UNIDADE"]
        .fillna("Unidade não identificada")
        .astype(str)
        .str.strip()
    )

    cnes = cnes[cnes["CNES"] != ""]
    cnes = cnes.drop_duplicates(subset=["CNES"])

    return cnes
