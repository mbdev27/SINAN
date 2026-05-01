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


def detectar_coluna(df, candidatos):
    colunas_norm = {normalizar_texto(c): c for c in df.columns}

    for candidato in candidatos:
        candidato_norm = normalizar_texto(candidato)

        for col_norm, col_original in colunas_norm.items():
            if candidato_norm == col_norm or candidato_norm in col_norm:
                return col_original

    return None


def carregar_cnes(caminho=None):
    """
    Carrega tabela CNES com código e nome das unidades.
    """

    caminhos = [caminho] if caminho else CAMINHOS_CNES

    arquivo_encontrado = None

    for c in caminhos:
        if c and os.path.exists(c):
            arquivo_encontrado = c
            break

    if not arquivo_encontrado:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    try:
        df = pd.read_excel(arquivo_encontrado, dtype=str)
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
            "ID_UNIDADE",
            "CODIGO DA UNIDADE",
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
            "RAZAO SOCIAL",
        ]
    )

    if not col_cnes or not col_nome:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    cnes = df[[col_cnes, col_nome]].copy()
    cnes.columns = ["CNES", "NOME_UNIDADE"]

    cnes["CNES"] = (
        cnes["CNES"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(".0", "", regex=False)
    )

    cnes["NOME_UNIDADE"] = (
        cnes["NOME_UNIDADE"]
        .fillna("Unidade não identificada")
        .astype(str)
        .str.strip()
    )

    cnes = cnes[cnes["CNES"] != ""]
    cnes = cnes.drop_duplicates(subset=["CNES"])

    return cnes


def anexar_nome_unidade(df, coluna_unidade="ID_UNIDADE"):
    """
    Anexa o nome da unidade ao DataFrame usando a tabela CNES.
    """

    if coluna_unidade not in df.columns:
        return df

    cnes = carregar_cnes()

    if cnes.empty:
        df["NOME_UNIDADE"] = "CNES não localizado"
        return df

    df = df.copy()

    df[coluna_unidade] = (
        df[coluna_unidade]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(".0", "", regex=False)
    )

    df = df.merge(
        cnes,
        how="left",
        left_on=coluna_unidade,
        right_on="CNES"
    )

    df["NOME_UNIDADE"] = df["NOME_UNIDADE"].fillna("Unidade não encontrada na base CNES")

    df = df.drop(columns=["CNES"], errors="ignore")

    return df
