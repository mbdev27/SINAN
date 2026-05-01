import pandas as pd


SIM_NAO_IGN = {
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

LOCAL_OCORRENCIA = {
    "01": "Residência",
    "1": "Residência",
    "02": "Habitação coletiva",
    "2": "Habitação coletiva",
    "03": "Escola",
    "3": "Escola",
    "04": "Local de prática esportiva",
    "4": "Local de prática esportiva",
    "05": "Bar ou similar",
    "5": "Bar ou similar",
    "06": "Via pública",
    "6": "Via pública",
    "07": "Comércio/serviços",
    "7": "Comércio/serviços",
    "08": "Indústrias/construção",
    "8": "Indústrias/construção",
    "09": "Outro",
    "9": "Outro",
    "99": "Ignorado",
    "": "Ignorado",
}

SITUACAO_CONJUGAL = {
    "1": "Solteiro",
    "2": "Casado/união consensual",
    "3": "Viúvo",
    "4": "Separado",
    "8": "Não se aplica",
    "9": "Ignorado",
    "": "Ignorado",
}

ORIENTACAO_SEXUAL = {
    "1": "Heterossexual",
    "2": "Homossexual",
    "3": "Bissexual",
    "8": "Não se aplica",
    "9": "Ignorado",
    "": "Ignorado",
}

IDENTIDADE_GENERO = {
    "1": "Travesti",
    "2": "Mulher transexual",
    "3": "Homem transexual",
    "8": "Não se aplica",
    "9": "Ignorado",
    "": "Ignorado",
}

NUM_ENVOLVIDOS = {
    "1": "Um",
    "2": "Dois ou mais",
    "9": "Ignorado",
    "": "Ignorado",
}

SEXO_AUTOR = {
    "1": "Masculino",
    "2": "Feminino",
    "3": "Ambos os sexos",
    "9": "Ignorado",
    "": "Ignorado",
}

CICLO_VIDA_AUTOR = {
    "1": "Criança (0 a 9 anos)",
    "2": "Adolescente (10 a 19 anos)",
    "3": "Jovem (20 a 24 anos)",
    "4": "Pessoa adulta (25 a 59 anos)",
    "5": "Pessoa idosa (60 anos ou mais)",
    "9": "Ignorado",
    "": "Ignorado",
}

EVOLUCAO = {
    "1": "Alta",
    "2": "Evasão/fuga",
    "3": "Óbito por violência",
    "4": "Óbito por outras causas",
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


def sim_nao_coluna(df, coluna):
    if coluna not in df.columns:
        return pd.Series(["Ignorado"] * len(df), index=df.index)

    return mapear(df[coluna], SIM_NAO_IGN)


def calcular_idade(df):
    if "DT_NASC" not in df.columns:
        return pd.NA

    data_base = None

    for candidato in ["DT_OCOR", "DT_NOTIFIC"]:
        if candidato in df.columns:
            data_base = candidato
            break

    if data_base is None:
        return pd.NA

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


def aplicar_mapeamento_violencia(df):
    df = df.copy()

    for col in ["DT_NOTIFIC", "DT_OCOR", "DT_NASC", "DT_OBITO", "DT_ENCERRA"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "CS_SEXO" in df.columns:
        df["CS_SEXO_DESC"] = mapear(df["CS_SEXO"], SEXO)

    if "CS_RACA" in df.columns:
        df["CS_RACA_DESC"] = mapear(df["CS_RACA"], RACA_COR)

    if "CS_GESTANT" in df.columns:
        df["CS_GESTANT_DESC"] = mapear(df["CS_GESTANT"], GESTANTE)

    if "CS_ESCOL_N" in df.columns:
        df["CS_ESCOL_N_DESC"] = mapear(df["CS_ESCOL_N"], ESCOLARIDADE)

    if "LOCAL_OCOR" in df.columns:
        df["LOCAL_OCOR_DESC"] = mapear(df["LOCAL_OCOR"], LOCAL_OCORRENCIA)

    if "SIT_CONJUG" in df.columns:
        df["SIT_CONJUG_DESC"] = mapear(df["SIT_CONJUG"], SITUACAO_CONJUGAL)

    if "ORIENT_SEX" in df.columns:
        df["ORIENT_SEX_DESC"] = mapear(df["ORIENT_SEX"], ORIENTACAO_SEXUAL)

    if "IDENT_GEN" in df.columns:
        df["IDENT_GEN_DESC"] = mapear(df["IDENT_GEN"], IDENTIDADE_GENERO)

    if "NUM_ENVOLV" in df.columns:
        df["NUM_ENVOLV_DESC"] = mapear(df["NUM_ENVOLV"], NUM_ENVOLVIDOS)

    if "AUTOR_SEXO" in df.columns:
        df["AUTOR_SEXO_DESC"] = mapear(df["AUTOR_SEXO"], SEXO_AUTOR)

    if "CICL_VID" in df.columns:
        df["CICL_VID_DESC"] = mapear(df["CICL_VID"], CICLO_VIDA_AUTOR)

    if "EVOLUCAO" in df.columns:
        df["EVOLUCAO_DESC"] = mapear(df["EVOLUCAO"], EVOLUCAO)

    campos_sim_nao = [
        "OUT_VEZES",
        "LES_AUTOP",
        "VIOL_FISIC",
        "VIOL_PSICO",
        "VIOL_TORT",
        "VIOL_SEXU",
        "VIOL_TRAF",
        "VIOL_FINAN",
        "VIOL_NEGLI",
        "VIOL_INFAN",
        "VIOL_LEGAL",
        "VIOL_OUTR",
        "AG_FORCA",
        "AG_ENFOR",
        "AG_OBJETO",
        "AG_CORTE",
        "AG_QUENTE",
        "AG_ENVEN",
        "AG_FOGO",
        "AG_AMEACA",
        "AG_OUTROS",
        "SEX_ASSEDI",
        "SEX_ESTUPR",
        "SEX_PORNO",
        "SEX_EXPLO",
        "SEX_OUTRO",
        "PROC_DST",
        "PROC_HIV",
        "PROC_HEPB",
        "PROC_SANG",
        "PROC_SEMEN",
        "PROC_VAGIN",
        "PROC_CONTR",
        "PROC_ABORT",
        "REL_TRAB",
        "REL_CAT",
        "AUTOR_ALCO",
        "ENC_SAUDE",
        "ENC_TUTELA",
        "ENC_DEAM",
        "ENC_MPU",
        "ENC_MULHER",
        "ENC_CREAS",
        "ENC_OUTR",
    ]

    for col in campos_sim_nao:
        if col in df.columns:
            df[f"{col}_DESC"] = sim_nao_coluna(df, col)

    df["IDADE_CALCULADA"] = calcular_idade(df)
    df["FAIXA_ETARIA_CALCULADA"] = df["IDADE_CALCULADA"].apply(faixa_etaria)

    return df


def gerar_tabela_publica_violencia(df):
    df = df.copy()

    colunas_sensiveis = [
        "NM_PACIENT",
        "NM_MAE_PAC",
        "ID_CNS_SUS",
        "NM_LOGRADO",
        "NU_NUMERO",
        "DS_COMPL",
        "DS_REF_RES",
        "FONE",
        "DDD",
    ]

    return df.drop(columns=[c for c in colunas_sensiveis if c in df.columns], errors="ignore")
