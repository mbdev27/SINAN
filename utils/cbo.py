import pandas as pd


def carregar_cbo(caminho="data/cbo.csv"):
    try:
        cbo = pd.read_csv(caminho, dtype=str, encoding="latin1")
    except Exception:
        cbo = pd.read_csv(caminho, dtype=str)

    cbo.columns = [str(c).strip().upper() for c in cbo.columns]

    if "CODIGO" not in cbo.columns or "TITULO" not in cbo.columns:
        return pd.DataFrame(columns=["CODIGO", "TITULO"])

    cbo["CODIGO"] = cbo["CODIGO"].astype(str).str.strip()
    cbo["TITULO"] = cbo["TITULO"].astype(str).str.strip()

    return cbo


def aplicar_cbo(df, coluna_cbo="ID_OCUPA_N", caminho="data/cbo.csv"):
    df = df.copy()

    if coluna_cbo not in df.columns:
        df["OCUPACAO_DESC"] = "Ignorado"
        return df

    cbo = carregar_cbo(caminho)

    if cbo.empty:
        df["OCUPACAO_DESC"] = df[coluna_cbo].fillna("Ignorado").astype(str)
        return df

    df[coluna_cbo] = df[coluna_cbo].fillna("").astype(str).str.strip()

    df = df.merge(
        cbo,
        how="left",
        left_on=coluna_cbo,
        right_on="CODIGO"
    )

    df["OCUPACAO_DESC"] = df["TITULO"].fillna("Ignorado")

    df = df.drop(columns=["CODIGO", "TITULO"], errors="ignore")

    return df
