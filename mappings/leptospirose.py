import pandas as pd


SIM_NAO_IGN = {
    "1": "Sim",
    "2": "Não",
    "9": "Ignorado",
    "": "Ignorado",
}

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
    "1": "Clínico-laboratorial",
    "2": "Clínico-epidemiológico",
    "": "Ignorado",
}

AUTOCTONE = {
    "1": "Sim",
    "2": "Não",
    "3": "Indeterminado",
    "": "Ignorado",
}

AREA = {
    "1": "Urbana",
    "2": "Rural",
    "3": "Periurbana",
    "9": "Ignorado",
    "": "Ignorado",
}

AMBIENTE = {
    "1": "Domiciliar",
    "2": "Trabalho",
    "3": "Lazer",
    "4": "Outro",
    "9": "Ignorado",
    "": "Ignorado",
}

EVOLUCAO = {
    "1": "Cura",
    "2": "Óbito por leptospirose",
    "3": "Óbito por outras causas",
    "9": "Ignorado",
    "": "Ignorado",
}

RESULTADO_LAB = {
    "1": "Reagente/Positivo",
    "2": "Não reagente/Negativo",
    "3": "Inconclusivo/Não realizada",
    "4": "Não realizado",
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


def aplicar_mapeamento_leptospirose(df):
    df = df.copy()

    for col in [
        "DT_NOTIFIC",
        "DT_SIN_PRI",
        "DT_NASC",
        "DT_INVEST",
        "DT_ATEND",
        "DT_INTERNA",
        "DT_ALTA",
        "DT_COLETA",
        "DT_OBITO",
        "DT_ENCERRA",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "CS_SEXO" in df.columns:
        df["CS_SEXO_DESC"] = mapear(df["CS_SEXO"], SEXO)

    if "CS_RACA" in df.columns:
        df["CS_RACA_DESC"] = mapear(df["CS_RACA"], RACA_COR)

    if "CS_GESTANT" in df.columns:
        df["CS_GESTANT_DESC"] = mapear(df["CS_GESTANT"], GESTANTE)

    col_hosp = primeira_coluna_existente(df, ["HOSPITALIZ", "HOSPITAL"])
    if col_hosp:
        df["HOSPITALIZ_DESC"] = mapear(df[col_hosp], SIM_NAO_IGN)

    col_class = primeira_coluna_existente(df, ["CLASSI_FIN", "CLASSIFIN", "CLASS_FINAL"])
    if col_class:
        df["CLASSI_FIN_DESC"] = mapear(df[col_class], CLASSIFICACAO)

    col_criterio = primeira_coluna_existente(df, ["CRITERIO", "CRIT_CONF"])
    if col_criterio:
        df["CRITERIO_DESC"] = mapear(df[col_criterio], CRITERIO)

    col_autoctone = primeira_coluna_existente(df, ["TPAUTOCTO", "AUTOCTONE"])
    if col_autoctone:
        df["TPAUTOCTO_DESC"] = mapear(df[col_autoctone], AUTOCTONE)

    col_area = primeira_coluna_existente(df, ["TP_LOCAL", "AREA_INFEC", "ZONA_INFEC"])
    if col_area:
        df["AREA_INFEC_DESC"] = mapear(df[col_area], AREA)

    col_ambiente = primeira_coluna_existente(df, ["AMBIENTE", "AMB_INFEC", "LOCAL_INF"])
    if col_ambiente:
        df["AMBIENTE_INFEC_DESC"] = mapear(df[col_ambiente], AMBIENTE)

    col_trab = primeira_coluna_existente(df, ["DOENCA_TRA", "REL_TRAB", "TRABALHO"])
    if col_trab:
        df["REL_TRAB_DESC"] = mapear(df[col_trab], SIM_NAO_IGN)

    col_evol = primeira_coluna_existente(df, ["EVOLUCAO", "EVOL_CASO"])
    if col_evol:
        df["EVOLUCAO_DESC"] = mapear(df[col_evol], EVOLUCAO)

    sintomas_riscos = [
        "FEBRE",
        "MIALGIA",
        "CEFALEIA",
        "VOMITO",
        "DIARREIA",
        "PROSTRACAO",
        "ICTERICIA",
        "CONJUNTVIT",
        "DOR_PANTUR",
        "INSUF_RENAL",
        "ALTER_RESP",
        "HEMOR_PULM",
        "MENINGISMO",
        "ALTER_CARD",
        "HEMORRAGIA",
        "LAMA",
        "AGUA_LAMA",
        "ENCHENTE",
        "FOSSA",
        "ESGOTO",
        "RIO",
        "LAGOA",
        "TERRENO",
        "LIXO",
        "ANIMAIS",
        "ROEDORES",
        "RATO",
        "CAIXA_DAG",
        "PLANTIO",
        "GRAOS",
    ]

    for col in sintomas_riscos:
        if col in df.columns:
            df[f"{col}_DESC"] = mapear(df[col], SIM_NAO_IGN)

    exames = [
        "RES_ELISA",
        "RES_IGM",
        "RES_MICRO",
        "RES_PCR",
        "RES_ISOLAM",
        "RES_IMUNO",
    ]

    for col in exames:
        if col in df.columns:
            df[f"{col}_DESC"] = mapear(df[col], RESULTADO_LAB)

    df["IDADE_CALCULADA"] = calcular_idade(df)
    df["FAIXA_ETARIA_CALCULADA"] = df["IDADE_CALCULADA"].apply(faixa_etaria)

    return df


def gerar_tabela_publica_leptospirose(df):
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
