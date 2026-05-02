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
    "3": "Não se aplica",
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

SIT_TRAB = {
    "01": "Empregado registrado",
    "1": "Empregado registrado",
    "02": "Empregado não registrado",
    "2": "Empregado não registrado",
    "03": "Autônomo/conta própria",
    "3": "Autônomo/conta própria",
    "04": "Servidor público estatutário",
    "4": "Servidor público estatutário",
    "05": "Servidor público celetista",
    "5": "Servidor público celetista",
    "06": "Aposentado",
    "6": "Aposentado",
    "07": "Desempregado",
    "7": "Desempregado",
    "08": "Trabalho temporário",
    "8": "Trabalho temporário",
    "09": "Cooperativado",
    "9": "Cooperativado",
    "10": "Trabalhador avulso",
    "11": "Empregador",
    "12": "Outros",
    "99": "Ignorado",
    "": "Ignorado",
}

LOCAL_EXPOSICAO = {
    "1": "Residência",
    "2": "Ambiente de trabalho",
    "3": "Trajeto do trabalho",
    "4": "Serviços de saúde",
    "5": "Escola/creche",
    "6": "Ambiente externo",
    "7": "Outro",
    "9": "Ignorado",
    "": "Ignorado",
}

GRUPO_AGENTE = {
    "01": "Medicamento",
    "1": "Medicamento",
    "02": "Agrotóxico de uso agrícola",
    "2": "Agrotóxico de uso agrícola",
    "03": "Agrotóxico de uso doméstico",
    "3": "Agrotóxico de uso doméstico",
    "04": "Agrotóxico de uso saúde pública",
    "4": "Agrotóxico de uso saúde pública",
    "05": "Raticida",
    "5": "Raticida",
    "06": "Produto veterinário",
    "6": "Produto veterinário",
    "07": "Produto de uso domiciliar",
    "7": "Produto de uso domiciliar",
    "08": "Cosmético/higiene pessoal",
    "8": "Cosmético/higiene pessoal",
    "09": "Produto químico de uso industrial",
    "9": "Produto químico de uso industrial",
    "10": "Metal",
    "11": "Drogas de abuso",
    "12": "Planta tóxica",
    "13": "Alimento e bebida",
    "14": "Outro",
    "99": "Ignorado",
    "": "Ignorado",
}

FINALIDADE_AGROTOXICO = {
    "1": "Inseticida",
    "2": "Herbicida",
    "3": "Carrapaticida",
    "4": "Raticida",
    "5": "Fungicida",
    "6": "Preservante para madeira",
    "7": "Outro",
    "8": "Não se aplica",
    "9": "Ignorado",
    "": "Ignorado",
}

VIA_EXPOSICAO = {
    "1": "Digestiva",
    "2": "Cutânea",
    "3": "Respiratória",
    "4": "Ocular",
    "5": "Parenteral",
    "6": "Vaginal",
    "7": "Transplacentária",
    "8": "Outra",
    "9": "Ignorada",
    "": "Ignorado",
}

CIRCUNSTANCIA = {
    "01": "Uso habitual",
    "1": "Uso habitual",
    "02": "Acidental",
    "2": "Acidental",
    "03": "Ambiental",
    "3": "Ambiental",
    "04": "Uso terapêutico",
    "4": "Uso terapêutico",
    "05": "Prescrição médica inadequada",
    "5": "Prescrição médica inadequada",
    "06": "Erro de administração",
    "6": "Erro de administração",
    "07": "Automedicação",
    "7": "Automedicação",
    "08": "Abuso",
    "8": "Abuso",
    "09": "Ingestão de alimento ou bebida",
    "9": "Ingestão de alimento ou bebida",
    "10": "Tentativa de suicídio",
    "11": "Tentativa de aborto",
    "12": "Violência/homicídio",
    "13": "Outra",
    "99": "Ignorado",
    "": "Ignorado",
}

TIPO_EXPOSICAO = {
    "1": "Aguda única",
    "2": "Aguda repetida",
    "3": "Crônica",
    "4": "Aguda sobre crônica",
    "9": "Ignorado",
    "": "Ignorado",
}

TIPO_ATENDIMENTO = {
    "1": "Hospitalar",
    "2": "Ambulatorial",
    "3": "Domiciliar",
    "4": "Nenhum",
    "9": "Ignorado",
    "": "Ignorado",
}

CLASSIFICACAO_FINAL = {
    "1": "Intoxicação confirmada",
    "2": "Só exposição",
    "3": "Reação adversa",
    "4": "Outro diagnóstico",
    "5": "Síndrome de abstinência",
    "9": "Ignorado",
    "": "Ignorado",
}

CRITERIO = {
    "1": "Clínico laboratorial",
    "2": "Clínico epidemiológico",
    "": "Ignorado",
}

EVOLUCAO = {
    "1": "Cura sem sequela",
    "2": "Cura com sequela",
    "3": "Óbito por intoxicação exógena",
    "4": "Óbito por outra causa",
    "5": "Perda de seguimento",
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


def primeira_coluna_existente(df, candidatos):
    for c in candidatos:
        if c in df.columns:
            return c
    return None


def aplicar_mapeamento_intoxicacao_exogena(df):
    df = df.copy()

    for col in [
        "DT_NOTIFIC",
        "DT_SIN_PRI",
        "DT_NASC",
        "DT_INVEST",
        "DT_INTERNA",
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

    if "CS_ESCOL_N" in df.columns:
        df["CS_ESCOL_N_DESC"] = mapear(df["CS_ESCOL_N"], ESCOLARIDADE)

    col_sit = primeira_coluna_existente(df, ["SIT_TRAB", "SIT_TRABAL", "SIT_MERCA"])
    if col_sit:
        df["SIT_TRAB_DESC"] = mapear(df[col_sit], SIT_TRAB)

    col_local = primeira_coluna_existente(df, ["LOCAL_EXPO", "LOCAL_EXP", "LOC_EXPO"])
    if col_local:
        df["LOCAL_EXPO_DESC"] = mapear(df[col_local], LOCAL_EXPOSICAO)

    col_agente = primeira_coluna_existente(df, ["GRUPO_AGEN", "GRUPO_AGENT", "AGENTE_TOX", "GRUPO_TOX"])
    if col_agente:
        df["GRUPO_AGENTE_DESC"] = mapear(df[col_agente], GRUPO_AGENTE)

    col_finalidade = primeira_coluna_existente(df, ["FINALI_AGR", "FINALIDADE", "FINALID_AG"])
    if col_finalidade:
        df["FINALIDADE_AGROTOXICO_DESC"] = mapear(df[col_finalidade], FINALIDADE_AGROTOXICO)

    col_via = primeira_coluna_existente(df, ["VIA_1", "VIA_EXPO", "VIA_EXPOS", "VIA_EXP"])
    if col_via:
        df["VIA_EXPOSICAO_DESC"] = mapear(df[col_via], VIA_EXPOSICAO)

    col_circ = primeira_coluna_existente(df, ["CIRCUNST", "CIRCUNSTAN", "CIRC_EXP"])
    if col_circ:
        df["CIRCUNSTANCIA_DESC"] = mapear(df[col_circ], CIRCUNSTANCIA)

    col_tipo = primeira_coluna_existente(df, ["TIPO_EXP", "TP_EXPOS", "TIPO_EXPO"])
    if col_tipo:
        df["TIPO_EXPOSICAO_DESC"] = mapear(df[col_tipo], TIPO_EXPOSICAO)

    col_atend = primeira_coluna_existente(df, ["TP_ATEND", "TIPO_ATEND"])
    if col_atend:
        df["TIPO_ATENDIMENTO_DESC"] = mapear(df[col_atend], TIPO_ATENDIMENTO)

    col_hosp = primeira_coluna_existente(df, ["HOSPITALIZ", "HOSPITAL"])
    if col_hosp:
        df["HOSPITALIZ_DESC"] = mapear(df[col_hosp], SIM_NAO)

    col_trab = primeira_coluna_existente(df, ["REL_TRAB", "EXPO_TRAB", "TRABALHO"])
    if col_trab:
        df["REL_TRAB_DESC"] = mapear(df[col_trab], SIM_NAO)

    col_cat = primeira_coluna_existente(df, ["CAT", "REL_CAT"])
    if col_cat:
        df["CAT_DESC"] = mapear(df[col_cat], SIM_NAO_NA)

    col_class = primeira_coluna_existente(df, ["CLASSI_FIN", "CLASSIFIN", "CLASS_FINAL"])
    if col_class:
        df["CLASSI_FIN_DESC"] = mapear(df[col_class], CLASSIFICACAO_FINAL)

    col_criterio = primeira_coluna_existente(df, ["CRITERIO", "CRIT_CONF"])
    if col_criterio:
        df["CRITERIO_DESC"] = mapear(df[col_criterio], CRITERIO)

    col_evol = primeira_coluna_existente(df, ["EVOLUCAO", "EVOL_CASO"])
    if col_evol:
        df["EVOLUCAO_DESC"] = mapear(df[col_evol], EVOLUCAO)

    df["IDADE_CALCULADA"] = calcular_idade(df)
    df["FAIXA_ETARIA_CALCULADA"] = df["IDADE_CALCULADA"].apply(faixa_etaria)

    return df


def gerar_tabela_publica_intoxicacao_exogena(df):
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
