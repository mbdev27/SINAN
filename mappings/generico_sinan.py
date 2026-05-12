import pandas as pd


SEXO = {
    "M": "Masculino",
    "F": "Feminino",
    "I": "Ignorado",
    "9": "Ignorado",
    "": "Ignorado",
}

RACA_COR = {
    "1": "Branca",
    "2": "Preta",
    "3": "Amarela",
    "4": "Parda",
    "5": "Indígena",
    "9": "Ignorado",
    "": "Ignorado",
}

GESTANTE = {
    "1": "1º trimestre",
    "2": "2º trimestre",
    "3": "3º trimestre",
    "4": "Idade gestacional ignorada",
    "5": "Não",
    "6": "Não se aplica",
    "9": "Ignorado",
    "": "Ignorado",
}


def limpar_codigo(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto


def mapear(serie, mapa):
    return serie.apply(
        lambda x: mapa.get(limpar_codigo(x), "Ignorado")
    )


def primeira_coluna_existente(df, candidatos):
    for coluna in candidatos:
        if coluna in df.columns:
            return coluna

    return None


def calcular_idade(df):
    if "DT_NASC" not in df.columns:
        return pd.Series([pd.NA] * len(df), index=df.index)

    data_base = primeira_coluna_existente(
        df,
        [
            "DT_SIN_PRI",
            "DT_NOTIFIC",
            "DT_OCOR",
            "DT_ACID",
            "DT_DIAG",
        ]
    )

    if data_base is None:
        return pd.Series([pd.NA] * len(df), index=df.index)

    nascimento = pd.to_datetime(
        df["DT_NASC"],
        errors="coerce"
    )

    evento = pd.to_datetime(
        df[data_base],
        errors="coerce"
    )

    idade = evento.dt.year - nascimento.dt.year

    ajuste = (
        (evento.dt.month < nascimento.dt.month)
        |
        (
            (evento.dt.month == nascimento.dt.month)
            &
            (evento.dt.day < nascimento.dt.day)
        )
    )

    idade = idade - ajuste.astype("Int64")

    return idade


def faixa_etaria(idade):
    try:
        idade = int(idade)
    except Exception:
        return "Ignorado"

    if idade < 0:
        return "Ignorado"

    if idade <= 9:
        return "0 a 9 anos"

    if idade <= 19:
        return "10 a 19 anos"

    if idade <= 29:
        return "20 a 29 anos"

    if idade <= 39:
        return "30 a 39 anos"

    if idade <= 49:
        return "40 a 49 anos"

    if idade <= 59:
        return "50 a 59 anos"

    return "60 anos ou mais"


def aplicar_mapeamento_generico(df):
    df = df.copy()

    for coluna in df.columns:
        if coluna.startswith("DT_"):
            df[coluna] = pd.to_datetime(
                df[coluna],
                errors="coerce"
            )

    if "CS_SEXO" in df.columns:
        df["CS_SEXO_DESC"] = mapear(
            df["CS_SEXO"],
            SEXO
        )

    if "CS_RACA" in df.columns:
        df["CS_RACA_DESC"] = mapear(
            df["CS_RACA"],
            RACA_COR
        )

    if "CS_GESTANT" in df.columns:
        df["CS_GESTANT_DESC"] = mapear(
            df["CS_GESTANT"],
            GESTANTE
        )

    df["IDADE_CALCULADA"] = calcular_idade(df)

    df["FAIXA_ETARIA_CALCULADA"] = df[
        "IDADE_CALCULADA"
    ].apply(faixa_etaria)

    return df


def gerar_tabela_publica_generica(df):
    colunas_sensiveis = [
        "NM_PACIENT",
        "NM_MAE_PAC",
        "ID_CNS_SUS",
        "NM_LOGRADO",
        "NU_NUMERO",
        "DS_COMPL",
        "DS_REF_RES",
        "NU_TELEFON",
        "FONE",
        "DDD",
    ]

    return df.drop(
        columns=[
            c for c in colunas_sensiveis
            if c in df.columns
        ],
        errors="ignore"
    )
