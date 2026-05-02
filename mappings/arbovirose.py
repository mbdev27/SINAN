import pandas as pd


SIM_NAO = {
    "1": "Sim",
    "2": "Não",
    "9": "Ignorado",
    "": "Ignorado",
}

SIM_NAO_NA = {
    "1": "Sim",
    "2": "Não",
    "8": "Não se aplica",
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

ESCOLARIDADE = {
    "0": "Analfabeto",
    "1": "1ª a 4ª série incompleta do EF",
    "2": "4ª série completa do EF",
    "3": "5ª à 8ª série incompleta do EF",
    "4": "Ensino fundamental completo",
    "5": "Ensino médio incompleto",
    "6": "Ensino médio completo",
    "7": "Educação superior incompleta",
    "8": "Educação superior completa",
    "9": "Ignorado",
    "10": "Não se aplica",
    "": "Ignorado",
}

RESULTADO_LAB = {
    "1": "Positivo/Reagente",
    "2": "Negativo/Não reagente",
    "3": "Inconclusivo",
    "4": "Não realizado",
    "": "Ignorado",
}

SOROTIPO = {
    "1": "DENV 1",
    "2": "DENV 2",
    "3": "DENV 3",
    "4": "DENV 4",
    "": "Ignorado",
}

CLASSIFICACAO_FINAL = {
    "5": "Descartado",
    "10": "Dengue",
    "11": "Dengue com sinais de alarme",
    "12": "Dengue grave",
    "13": "Chikungunya",
    "": "Ignorado",
}

CRITERIO = {
    "1": "Laboratorial",
    "2": "Clínico-epidemiológico",
    "3": "Em investigação",
    "": "Ignorado",
}

EVOLUCAO = {
    "1": "Cura",
    "2": "Óbito pelo agravo",
    "3": "Óbito por outras causas",
    "4": "Óbito em investigação",
    "9": "Ignorado",
    "": "Ignorado",
}

AUTOCTONE = {
    "1": "Sim",
    "2": "Não",
    "3": "Indeterminado",
    "": "Ignorado",
}

CLINICA_CHIK = {
    "1": "Aguda",
    "2": "Crônica",
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


def calcular_idade(df):
    if "DT_NASC" not in df.columns:
        return pd.Series([pd.NA] * len(df), index=df.index)

    data_base = None

    for candidato in ["DT_SIN_PRI", "DT_NOTIFIC"]:
        if candidato in df.columns:
            data_base = candidato
            break

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


def aplicar_mapeamento_arbovirose(df):
    df = df.copy()

    for col in [
        "DT_NOTIFIC",
        "DT_SIN_PRI",
        "DT_NASC",
        "DT_INVEST",
        "DT_INTERNA",
        "DT_OBITO",
        "DT_ENCERRA",
        "DT_ALRM",
        "DT_GRAV",
        "DT_SORO",
        "DT_NS1",
        "DT_VIRAL",
        "DT_PCR",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "ID_AGRAVO" in df.columns:
        df["AGRAVO_DESC"] = (
            df["ID_AGRAVO"]
            .astype(str)
            .str.upper()
            .str.strip()
            .replace({
                "A90": "Dengue",
                "A92": "Chikungunya",
                "A920": "Chikungunya",
            })
        )

    if "CS_SEXO" in df.columns:
        df["CS_SEXO_DESC"] = mapear(df["CS_SEXO"], SEXO)

    if "CS_RACA" in df.columns:
        df["CS_RACA_DESC"] = mapear(df["CS_RACA"], RACA_COR)

    if "CS_GESTANT" in df.columns:
        df["CS_GESTANT_DESC"] = mapear(df["CS_GESTANT"], GESTANTE)

    if "CS_ESCOL_N" in df.columns:
        df["CS_ESCOL_N_DESC"] = mapear(df["CS_ESCOL_N"], ESCOLARIDADE)

    if "CLASSI_FIN" in df.columns:
        df["CLASSI_FIN_DESC"] = mapear(df["CLASSI_FIN"], CLASSIFICACAO_FINAL)

    if "CRITERIO" in df.columns:
        df["CRITERIO_DESC"] = mapear(df["CRITERIO"], CRITERIO)

    if "EVOLUCAO" in df.columns:
        df["EVOLUCAO_DESC"] = mapear(df["EVOLUCAO"], EVOLUCAO)

    if "HOSPITALIZ" in df.columns:
        df["HOSPITALIZ_DESC"] = mapear(df["HOSPITALIZ"], SIM_NAO)

    if "TPAUTOCTO" in df.columns:
        df["TPAUTOCTO_DESC"] = mapear(df["TPAUTOCTO"], AUTOCTONE)

    if "CLINC_CHIK" in df.columns:
        df["CLINC_CHIK_DESC"] = mapear(df["CLINC_CHIK"], CLINICA_CHIK)

    if "SOROTIPO" in df.columns:
        df["SOROTIPO_DESC"] = mapear(df["SOROTIPO"], SOROTIPO)

    exames = [
        "RESUL_SORO",
        "RESUL_NS1",
        "RESUL_VI_N",
        "RESUL_PCR_",
        "HISTOPA_N",
        "IMUNOH_N",
        "RES_CHIKS1",
        "RES_CHIKS2",
        "RESUL_PRNT",
    ]

    for col in exames:
        if col in df.columns:
            df[f"{col}_DESC"] = mapear(df[col], RESULTADO_LAB)

    campos_sim_nao = [
        "FEBRE",
        "MIALGIA",
        "CEFALEIA",
        "EXANTEMA",
        "VOMITO",
        "NAUSEA",
        "DOR_COSTAS",
        "CONJUNTVIT",
        "ARTRITE",
        "ARTRALGIA",
        "PETEQUIA_N",
        "LEUCOPENIA",
        "LACO",
        "DOR_RETRO",
        "DIABETES",
        "HEMATOLOG",
        "HEPATOPAT",
        "RENAL",
        "HIPERTENSA",
        "ACIDO_PEPT",
        "AUTO_IMUNE",
        "ALRM_HIPOT",
        "ALRM_PLAQ",
        "ALRM_VOM",
        "ALRM_SANG",
        "ALRM_HEMAT",
        "ALRM_ABDOM",
        "ALRM_LETAR",
        "ALRM_HEPAT",
        "ALRM_LIQ",
        "GRAV_PULSO",
        "GRAV_CONV",
        "GRAV_ENCH",
        "GRAV_INSUF",
        "GRAV_TAQUI",
        "GRAV_EXTRE",
        "GRAV_HIPOT",
        "GRAV_HEMAT",
        "GRAV_MELEN",
        "GRAV_METRO",
        "GRAV_SANG",
        "GRAV_AST",
        "GRAV_MIOC",
        "GRAV_CONSC",
        "GRAV_ORGAO",
    ]

    for col in campos_sim_nao:
        if col in df.columns:
            df[f"{col}_DESC"] = mapear(df[col], SIM_NAO)

    df["IDADE_CALCULADA"] = calcular_idade(df)
    df["FAIXA_ETARIA_CALCULADA"] = df["IDADE_CALCULADA"].apply(faixa_etaria)

    return df


def gerar_tabela_publica_arbovirose(df):
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
