import pandas as pd
from dbfread import DBF
from pathlib import Path


ENCODINGS_TESTE = [
    "utf-8",
    "utf-8-sig",
    "latin1",
    "iso-8859-1",
    "cp1252"
]


def ler_dbf(caminho_arquivo, encoding="latin1"):
    df, _ = ler_dbf_com_diagnostico(caminho_arquivo, encoding)
    return df


def ler_dbf_com_diagnostico(caminho_arquivo, encoding="latin1"):
    caminho = Path(caminho_arquivo)

    encodings = [encoding] + [e for e in ENCODINGS_TESTE if e != encoding]
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

            diagnostico = {
                "encoding_detectado": enc,
                "registros": len(df),
                "colunas": len(df.columns),
                "arquivo": caminho.name
            }

            return df, diagnostico

        except Exception as e:
            ultimo_erro = e

    raise RuntimeError(f"Não foi possível ler o DBF. Último erro: {ultimo_erro}")


def resumo_dbf(df):
    if df.empty:
        return pd.DataFrame()

    return pd.DataFrame({
        "Coluna": df.columns,
        "Tipo inferido": [str(df[c].dtype) for c in df.columns],
        "Não nulos": [df[c].notna().sum() for c in df.columns],
        "% vazio": [
            round((df[c].isna().sum() / len(df)) * 100, 1) if len(df) else 0
            for c in df.columns
        ],
        "Exemplos": [
            ", ".join(df[c].dropna().astype(str).unique()[:3])
            for c in df.columns
        ]
    })
