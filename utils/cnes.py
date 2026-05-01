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


def encontrar_linha_cabecalho(bruto):
    for idx, row in bruto.iterrows():
        valores = [normalizar_texto(v) for v in row.tolist()]

        tem_cnes = any(v == "CNES" for v in valores)
        tem_nome = any("NOME FANTASIA" in v for v in valores)

        if tem_cnes and tem_nome:
            return idx

    return None


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
        try:
            bruto = pd.read_excel(
                arquivo,
                sheet_name=aba,
                header=None,
                dtype=str
            )
        except Exception:
            continue

        linha_cabecalho = encontrar_linha_cabecalho(bruto)

        if linha_cabecalho is None:
            continue

        tabela = bruto.iloc[linha_cabecalho + 1:].copy()
        tabela.columns = bruto.iloc[linha_cabecalho].tolist()
        tabela.columns = [str(c).strip() for c in tabela.columns]

        col_cnes = None
        col_nome = None

        for col in tabela.columns:
            col_norm = normalizar_texto(col)

            if col_norm == "CNES":
                col_cnes = col

            if "NOME FANTASIA" in col_norm:
                col_nome = col

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
    codigo = limpar_codigo(codigo_cnes)

    if not codigo or base_cnes.empty:
        return "Unidade não encontrada na base CNES"

    base = base_cnes.copy()
    base["CNES_LIMPO"] = base["CNES"].apply(limpar_codigo)

    # 1. Igualdade exata
    localizado = base[base["CNES_LIMPO"] == codigo]

    if not localizado.empty:
        return localizado.iloc[0]["NOME_UNIDADE"]

    # 2. DBF com 6 dígitos, planilha com 7: 242731 -> 2427311
    localizado = base[
        base["CNES_LIMPO"].astype(str).str.startswith(codigo)
    ]

    if not localizado.empty:
        return localizado.iloc[0]["NOME_UNIDADE"]

    # 3. Caso inverso
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
