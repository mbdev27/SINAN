import os
import pandas as pd
import unicodedata


CAMINHOS_CNES = [
    "data/cnes_ipojuca.xlsx",
    "data/CNES Ipojuca.xlsx",
    "CNES Ipojuca.xlsx",
]


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    return texto


def limpar_codigo(valor):
    """
    Limpa o código CNES, mantendo apenas números.
    """
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.endswith(".0"):
        texto = texto[:-2]

    somente_digitos = "".join(c for c in texto if c.isdigit())

    return somente_digitos


def localizar_arquivo_cnes(caminho=None):
    caminhos = [caminho] if caminho else CAMINHOS_CNES

    for item in caminhos:
        if item and os.path.exists(item):
            return item

    return None


def carregar_cnes(caminho=None):
    """
    Carrega a base CNES de Ipojuca.

    Esta função foi ajustada para a planilha enviada, onde o cabeçalho real
    fica no meio do arquivo, na linha que contém:
    CNES | Nome Fantasia | Razão Social
    """

    arquivo = localizar_arquivo_cnes(caminho)

    if not arquivo:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    try:
        bruto = pd.read_excel(
            arquivo,
            header=None,
            dtype=str
        )
    except Exception:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    linha_cabecalho = None

    for idx, row in bruto.iterrows():
        valores = [
            normalizar_texto(v)
            for v in row.tolist()
        ]

        contem_cnes = any(v == "CNES" for v in valores)
        contem_nome_fantasia = any("NOME FANTASIA" in v for v in valores)

        if contem_cnes and contem_nome_fantasia:
            linha_cabecalho = idx
            break

    if linha_cabecalho is None:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    tabela = bruto.iloc[linha_cabecalho + 1:].copy()
    tabela.columns = bruto.iloc[linha_cabecalho].tolist()

    tabela.columns = [
        str(c).strip()
        for c in tabela.columns
    ]

    col_cnes = None
    col_nome = None

    for col in tabela.columns:
        col_norm = normalizar_texto(col)

        if col_norm == "CNES":
            col_cnes = col

        if "NOME FANTASIA" in col_norm:
            col_nome = col

    if not col_cnes or not col_nome:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    cnes = tabela[[col_cnes, col_nome]].copy()
    cnes.columns = ["CNES", "NOME_UNIDADE"]

    cnes["CNES"] = cnes["CNES"].apply(limpar_codigo)

    cnes["NOME_UNIDADE"] = (
        cnes["NOME_UNIDADE"]
        .fillna("Unidade não identificada")
        .astype(str)
        .str.strip()
    )

    cnes = cnes[
        (cnes["CNES"] != "")
        & (cnes["NOME_UNIDADE"] != "")
        & (cnes["CNES"].str.upper() != "TOTAL")
    ]

    cnes = cnes.drop_duplicates(subset=["CNES"])

    return cnes.reset_index(drop=True)


def anexar_nome_unidade(df, coluna_unidade="ID_UNIDADE"):
    """
    Anexa nome fantasia da unidade ao DataFrame usando o CNES.
    """

    df = df.copy()

    if coluna_unidade not in df.columns:
        df["NOME_UNIDADE"] = "Coluna CNES não encontrada no banco"
        return df

    base_cnes = carregar_cnes()

    if base_cnes.empty:
        df["NOME_UNIDADE"] = "Base CNES não localizada ou inválida"
        return df

    df["_CNES_LIMPO"] = df[coluna_unidade].apply(limpar_codigo)

    df = df.merge(
        base_cnes,
        how="left",
        left_on="_CNES_LIMPO",
        right_on="CNES"
    )

    df["NOME_UNIDADE"] = df["NOME_UNIDADE"].fillna(
        "Unidade não encontrada na base CNES"
    )

    df = df.drop(
        columns=["_CNES_LIMPO", "CNES"],
        errors="ignore"
    )

    return df
