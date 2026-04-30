import pandas as pd
from dbfread import DBF
from pathlib import Path


def ler_dbf(caminho_arquivo, encoding="latin1"):
    """
    Lê arquivo DBF e retorna um DataFrame.

    Tenta primeiro latin1, depois utf-8 e cp1252.
    """
    caminho = Path(caminho_arquivo)

    encodings = [encoding, "utf-8", "cp1252", "iso-8859-1"]

    ultimo_erro = None

    for enc in encodings:
        try:
            tabela = DBF(
                caminho,
                encoding=enc,
                load=True,
                char_decode_errors="ignore"
            )
            df = pd.DataFrame(iter(tabela))
            df.columns = [str(c).strip().upper() for c in df.columns]
            return df
        except Exception as e:
            ultimo_erro = e

    raise RuntimeError(f"Não foi possível ler o DBF. Último erro: {ultimo_erro}")


def resumo_dbf(df):
    """
    Retorna resumo estrutural do banco.
    """
    return pd.DataFrame({
        "Coluna": df.columns,
        "Tipo inferido": [str(df[c].dtype) for c in df.columns],
        "Não nulos": [df[c].notna().sum() for c in df.columns],
        "Exemplos": [
            ", ".join(df[c].dropna().astype(str).unique()[:3])
            for c in df.columns
        ]
    })
