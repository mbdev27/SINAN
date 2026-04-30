import pandas as pd


def carregar_cbo(caminho="data/cbo.csv"):
    """
    Carrega a lista CBO tentando múltiplos encodings e separadores.
    Evita erro UnicodeDecodeError no Streamlit Cloud.
    """

    encodings = [
        "utf-8",
        "utf-8-sig",
        "latin1",
        "iso-8859-1",
        "cp1252"
    ]

    separadores = [",", ";", "\t"]

    ultimo_erro = None

    for enc in encodings:
        for sep in separadores:
            try:
                cbo = pd.read_csv(
                    caminho,
                    dtype=str,
                    encoding=enc,
                    sep=sep,
                    engine="python",
                    on_bad_lines="skip"
                )

                if cbo.empty:
                    continue

                cbo.columns = [str(c).strip().upper() for c in cbo.columns]

                # Tenta detectar colunas de código e título
                col_codigo = None
                col_titulo = None

                for col in cbo.columns:
                    col_norm = (
                        col.upper()
                        .replace("Ó", "O")
                        .replace("Í", "I")
                        .replace("Ç", "C")
                        .replace("Ã", "A")
                    )

                    if col_norm in ["CODIGO", "CBO", "COD_CBO", "CODIGO_CBO"]:
                        col_codigo = col

                    if col_norm in ["TITULO", "OCUPACAO", "NOME", "DESCRICAO"]:
                        col_titulo = col

                # Se não encontrou pelo nome, usa as duas primeiras colunas
                if col_codigo is None and len(cbo.columns) >= 1:
                    col_codigo = cbo.columns[0]

                if col_titulo is None and len(cbo.columns) >= 2:
                    col_titulo = cbo.columns[1]

                if col_codigo is None or col_titulo is None:
                    continue

                cbo = cbo[[col_codigo, col_titulo]].copy()
                cbo.columns = ["CODIGO", "TITULO"]

                cbo["CODIGO"] = (
                    cbo["CODIGO"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.replace(".0", "", regex=False)
                )

                cbo["TITULO"] = (
                    cbo["TITULO"]
                    .fillna("Ignorado")
                    .astype(str)
                    .str.strip()
                )

                cbo = cbo[cbo["CODIGO"] != ""]
                cbo = cbo.drop_duplicates(subset=["CODIGO"])

                return cbo

            except Exception as e:
                ultimo_erro = e
                continue

    # Se tudo falhar, retorna vazio em vez de quebrar o app
    return pd.DataFrame(columns=["CODIGO", "TITULO"])


def aplicar_cbo(df, coluna_cbo="ID_OCUPA_N", caminho="data/cbo.csv"):
    """
    Cruza o código CBO do banco SINAN com a lista CBO.
    Se houver erro ou arquivo ausente, mantém o código bruto.
    """

    df = df.copy()

    if coluna_cbo not in df.columns:
        df["OCUPACAO_DESC"] = "Ignorado"
        return df

    cbo = carregar_cbo(caminho)

    df[coluna_cbo] = (
        df[coluna_cbo]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(".0", "", regex=False)
    )

    if cbo.empty:
        df["OCUPACAO_DESC"] = df[coluna_cbo].replace("", "Ignorado")
        return df

    df = df.merge(
        cbo,
        how="left",
        left_on=coluna_cbo,
        right_on="CODIGO"
    )

    df["OCUPACAO_DESC"] = df["TITULO"].fillna("Ignorado")

    df = df.drop(columns=["CODIGO", "TITULO"], errors="ignore")

    return df
