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

CLASSIFICACAO = {
    "1": "Confirmado",
    "2": "Descartado",
    "": "Ignorado",
}

CRITERIO = {
    "1": "Laboratorial",
    "2": "Clínico-epidemiológico",
    "": "Ignorado",
}

AUTOCTONE = {
    "1": "Sim",
    "2": "Não",
    "3": "Indeterminado",
    "": "Ignorado",
}

REL_TRAB = {
    "1": "Sim",
    "2": "Não",
    "9": "Ignorado",
    "": "Ignorado",
}

EVOLUCAO = {
    "1": "Cura/Melhora",
    "2": "Óbito pelo agravo notificado",
    "3": "Óbito por outras causas",
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
    return serie.apply(lambda x: mapa.get(limpar_codigo(x), "Ignorado"))


def primeira_coluna_existente(df, candidatos):
    for c in candidatos:
        if c in df.columns:
            return c
    return None


def calcular_idade(df):
    if "DT_NASC" not in df.columns:
        return pd.Series([pd.NA] * len(df), index=df.index)

    data_base = primeira_coluna_existente(df, ["DT_SIN_PRI", "DT_NOTIFIC"])

    if data_base is None:
        return pd.Series([pd.NA] * len(df), index=df.index)

    nasc = pd.to_datetime(df["DT_NASC"], errors="coerce")
    evento = pd.to_datetime(df[data_base], errors="coerce")

    idade = evento.dt.year - nasc.dt.year

    ajuste = (
        (evento.dt.month < nasc.dt.month)
        |
        ((evento.dt.month == nasc.dt.month) & (evento.dt.day < nasc.dt.day))
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


def identificar_tipo_toxoplasmose(df, nome_arquivo=""):
    nome = str(nome_arquivo).upper()

    if "GEST" in nome:
        return "Toxoplasmose Gestacional"

    if "CONGEN" in nome or "CONG" in nome:
        return "Toxoplasmose Congênita"

    if "ADQUIR" in nome:
        return "Toxoplasmose Adquirida"

    if "ID_AGRAVO" in df.columns:
        codigos = (
            df["ID_AGRAVO"]
            .astype(str)
            .str.upper()
            .str.strip()
            .unique()
            .tolist()
        )

        if any("O986" in c or "O98" in c for c in codigos):
            return "Toxoplasmose Gestacional"

        if any("P371" in c or "P37" in c for c in codigos):
            return "Toxoplasmose Congênita"

        if any("B58" in c for c in codigos):
            return "Toxoplasmose Adquirida"

    return "Toxoplasmose"


def aplicar_mapeamento_toxoplasmose(df, nome_arquivo=""):
    df = df.copy()

    for col in [
        "DT_NOTIFIC",
        "DT_SIN_PRI",
        "DT_NASC",
        "DT_INVEST",
        "DT_OBITO",
        "DT_ENCERRA",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["TIPO_TOXOPLASMOSE"] = identificar_tipo_toxoplasmose(df, nome_arquivo)

    if "CS_SEXO" in df.columns:
        df["CS_SEXO_DESC"] = mapear(df["CS_SEXO"], SEXO)

    if "CS_RACA" in df.columns:
        df["CS_RACA_DESC"] = mapear(df["CS_RACA"], RACA_COR)

    if "CS_GESTANT" in df.columns:
        df["CS_GESTANT_DESC"] = mapear(df["CS_GESTANT"], GESTANTE)

    col_class = primeira_coluna_existente(df, ["CLASSI_FIN", "CLASSIFIN", "CLASS_FINAL"])
    if col_class:
        df["CLASSI_FIN_DESC"] = mapear(df[col_class], CLASSIFICACAO)

    col_criterio = primeira_coluna_existente(df, ["CRITERIO", "CRIT_CONF"])
    if col_criterio:
        df["CRITERIO_DESC"] = mapear(df[col_criterio], CRITERIO)

    col_autoctone = primeira_coluna_existente(df, ["TPAUTOCTO", "AUTOCTONE"])
    if col_autoctone:
        df["TPAUTOCTO_DESC"] = mapear(df[col_autoctone], AUTOCTONE)

    col_trab = primeira_coluna_existente(df, ["DOENCA_TRA", "REL_TRAB", "TRABALHO"])
    if col_trab:
        df["REL_TRAB_DESC"] = mapear(df[col_trab], REL_TRAB)

    col_evol = primeira_coluna_existente(df, ["EVOLUCAO", "EVOL_CASO"])
    if col_evol:
        df["EVOLUCAO_DESC"] = mapear(df[col_evol], EVOLUCAO)

    df["IDADE_CALCULADA"] = calcular_idade(df)
    df["FAIXA_ETARIA_CALCULADA"] = df["IDADE_CALCULADA"].apply(faixa_etaria)

    return df


def gerar_tabela_publica_toxoplasmose(df):
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
        columns=[c for c in colunas_sensiveis if c in df.columns],
        errors="ignore"
    )
