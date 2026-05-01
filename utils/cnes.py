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
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().replace(".0", "")
    return "".join(c for c in texto if c.isdigit())


def localizar_arquivo_cnes(caminho=None):
    caminhos = [caminho] if caminho else CAMINHOS_CNES

    for item in caminhos:
        if item and os.path.exists(item):
            return item

    return None


def detectar_coluna_por_nome(colunas, candidatos):
    for col in colunas:
        col_norm = normalizar_texto(col)

        for cand in candidatos:
            cand_norm = normalizar_texto(cand)

            if col_norm == cand_norm or cand_norm in col_norm:
                return col

    return None


def tentar_ler_aba_com_cabecalho(arquivo, aba):
    bruto = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None,
        dtype=str
    )

    for idx, row in bruto.iterrows():
        valores = [normalizar_texto(v) for v in row.tolist()]

        tem_cnes = any(
            v == "CNES"
            or "CODIGO CNES" in v
            or "COD CNES" in v
            for v in valores
        )

        tem_nome = any(
            "NOME FANTASIA" in v
            or "NOME DA UNIDADE" in v
            or "UNIDADE" == v
            or "ESTABELECIMENTO" in v
            or "NOME" == v
            for v in valores
        )

        if tem_cnes and tem_nome:
            tabela = bruto.iloc[idx + 1:].copy()
            tabela.columns = bruto.iloc[idx].tolist()
            tabela.columns = [str(c).strip() for c in tabela.columns]
            return tabela

    return pd.DataFrame()


def carregar_cnes(caminho=None):
    arquivo = localizar_arquivo_cnes(caminho)

    if not arquivo:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    try:
        xls = pd.ExcelFile(arquivo)
    except Exception:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    bases = []

    for aba in xls.sheet_names:
        tabela = tentar_ler_aba_com_cabecalho(arquivo, aba)

        if tabela.empty:
            try:
                tabela = pd.read_excel(
                    arquivo,
                    sheet_name=aba,
                    dtype=str
                )
            except Exception:
                continue

        tabela.columns = [str(c).strip() for c in tabela.columns]

        col_cnes = detectar_coluna_por_nome(
            tabela.columns,
            [
                "CNES",
                "CÓDIGO CNES",
                "CODIGO CNES",
                "COD CNES",
                "COD_CNES",
                "ID_UNIDADE",
                "CO_UNI_NOT",
                "CODIGO DA UNIDADE",
                "CÓDIGO DA UNIDADE",
            ]
        )

        col_nome = detectar_coluna_por_nome(
            tabela.columns,
            [
                "NOME FANTASIA",
                "NOME DA UNIDADE",
                "NOME UNIDADE",
                "UNIDADE",
                "ESTABELECIMENTO",
                "NO_FANTASIA",
                "RAZÃO SOCIAL",
                "RAZAO SOCIAL",
                "NOME",
            ]
        )

        if not col_cnes or not col_nome:
            continue

        base = tabela[[col_cnes, col_nome]].copy()
        base.columns = ["CNES", "NOME_UNIDADE"]

        base["CNES"] = base["CNES"].apply(limpar_codigo)

        base["NOME_UNIDADE"] = (
            base["NOME_UNIDADE"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        base = base[
            (base["CNES"] != "")
            & (base["NOME_UNIDADE"] != "")
            & (base["NOME_UNIDADE"].str.upper() != "NAN")
        ]

        bases.append(base)

    if not bases:
        return pd.DataFrame(columns=["CNES", "NOME_UNIDADE"])

    cnes = pd.concat(bases, ignore_index=True)
    cnes["CNES"] = cnes["CNES"].apply(limpar_codigo)

    cnes = cnes.drop_duplicates(subset=["CNES"], keep="first")

    return cnes.reset_index(drop=True)


def localizar_nome_por_cnes(codigo_cnes, base_cnes):
    """
    Localiza nome da unidade aceitando:
    - código igual;
    - código do DBF como prefixo do CNES da planilha;
    - CNES da planilha como prefixo do código do DBF.

    Isso resolve casos em que o DBF aparece com 6 dígitos
    e a base CNES com 7 dígitos.
    """

    codigo = limpar_codigo(codigo_cnes)

    if not codigo or base_cnes.empty:
        return "Unidade não encontrada na base CNES"

    base = base_cnes.copy()
    base["CNES_LIMPO"] = base["CNES"].apply(limpar_codigo)

    # 1. Igualdade exata
    localizado = base[base["CNES_LIMPO"] == codigo]

    if not localizado.empty:
        return localizado.iloc[0]["NOME_UNIDADE"]

    # 2. Código do DBF é prefixo do CNES da planilha
    localizado = base[
        base["CNES_LIMPO"].astype(str).str.startswith(codigo)
    ]

    if not localizado.empty:
        return localizado.iloc[0]["NOME_UNIDADE"]

    # 3. CNES da planilha é prefixo do código do DBF
    localizado = base[
        base["CNES_LIMPO"].astype(str).apply(
            lambda x: codigo.startswith(x) if x else False
        )
    ]

    if not localizado.empty:
        return localizado.iloc[0]["NOME_UNIDADE"]

    return "Unidade não encontrada na base CNES"


def buscar_nome_unidade(codigo_cnes):
    base = carregar_cnes()

    if base.empty:
        return "Base CNES não localizada ou inválida"

    return localizar_nome_por_cnes(codigo_cnes, base)


def anexar_nome_unidade(df, coluna_unidade="ID_UNIDADE"):
    df = df.copy()

    if coluna_unidade not in df.columns:
        df["NOME_UNIDADE"] = "Coluna CNES não encontrada no banco"
        return df

    base = carregar_cnes()

    if base.empty:
        df["NOME_UNIDADE"] = "Base CNES não localizada ou inválida"
        return df

    df["CNES"] = df[coluna_unidade].apply(limpar_codigo)

    df["NOME_UNIDADE"] = df["CNES"].apply(
        lambda codigo: localizar_nome_por_cnes(codigo, base)
    )

    return df
