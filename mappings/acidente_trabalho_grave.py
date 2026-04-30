import pandas as pd

from utils.cbo import aplicar_cbo


# ============================================================
# CAMPOS PRINCIPAIS DO AGRAVO
# ============================================================

CAMPOS_PRINCIPAIS = {
    "NU_NOTIFIC": "Número da Notificação",
    "TP_NOT": "Tipo de Notificação",
    "ID_AGRAVO": "Agravo/Doença",
    "DT_NOTIFIC": "Data da Notificação",
    "SEM_NOT": "Semana Epidemiológica da Notificação",
    "DT_ACID": "Data do Acidente",
    "SEM_ACID": "Semana Epidemiológica do Acidente",
    "NM_PACIENT": "Nome do Paciente",
    "DT_NASC": "Data de Nascimento",
    "NU_IDADE_N": "Idade no Banco",
    "CS_SEXO": "Sexo",
    "CS_GESTANT": "Gestante",
    "CS_RACA": "Raça/Cor",
    "CS_ESCOL_N": "Escolaridade",
    "NM_MAE_PAC": "Nome da Mãe",
    "ID_OCUPA_N": "Código CBO/Ocupação",
    "SIT_TRAB": "Situação no Mercado de Trabalho",
    "LOCAL_ACID": "Local onde ocorreu o acidente",
    "CNAE": "Atividade Econômica",
    "TIPO_ACID": "Tipo de Acidente",
    "MAIS_TRAB": "Houve outros trabalhadores atingidos",
    "ATENDE_MED": "Ocorreu atendimento médico",
    "PART_CORP1": "Parte do corpo atingida 1",
    "PART_CORP2": "Parte do corpo atingida 2",
    "PART_CORP3": "Parte do corpo atingida 3",
    "CID_LESAO": "Diagnóstico da Lesão",
    "REGIME": "Regime de Tratamento",
    "EVOLUCAO": "Evolução do Caso",
    "DT_OBITO": "Data do Óbito",
    "CAT": "CAT emitida",
    "DS_OBS": "Observações",
}


# ============================================================
# DICIONÁRIOS OFICIAIS DA FICHA
# ============================================================

DICIONARIOS = {
    "TP_NOT": {
        "2": "Individual",
    },

    "CS_SEXO": {
        "M": "Masculino",
        "F": "Feminino",
        "I": "Ignorado",
        "9": "Ignorado",
    },

    "CS_GESTANT": {
        "1": "1º trimestre",
        "2": "2º trimestre",
        "3": "3º trimestre",
        "4": "Idade gestacional ignorada",
        "5": "Não",
        "6": "Não se aplica",
        "9": "Ignorado",
    },

    "CS_RACA": {
        "1": "Branca",
        "2": "Preta",
        "3": "Amarela",
        "4": "Parda",
        "5": "Indígena",
        "9": "Ignorado",
    },

    "CS_ESCOL_N": {
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
    },

    "SIT_TRAB": {
        "01": "Empregado registrado com carteira assinada",
        "02": "Empregado não registrado",
        "03": "Autônomo/conta própria",
        "04": "Servidor público estatutário",
        "05": "Servidor público celetista",
        "06": "Aposentado",
        "07": "Desempregado",
        "08": "Trabalho temporário",
        "09": "Cooperativado",
        "10": "Trabalhador avulso",
        "11": "Empregador",
        "12": "Outros",
        "99": "Ignorado",
    },

    "LOCAL_ACID": {
        "1": "Instalações do contratante",
        "2": "Via pública",
        "3": "Instalações de terceiros",
        "4": "Domicílio próprio",
        "9": "Ignorado",
    },

    "TIPO_ACID": {
        "1": "Típico",
        "2": "Trajeto",
        "9": "Ignorado",
    },

    "MAIS_TRAB": {
        "1": "Sim",
        "2": "Não",
        "9": "Ignorado",
    },

    "ATENDE_MED": {
        "1": "Sim",
        "2": "Não",
        "9": "Ignorado",
    },

    "PART_CORP1": {
        "01": "Olho",
        "02": "Cabeça",
        "03": "Pescoço",
        "04": "Tórax",
        "05": "Abdome",
        "06": "Mão",
        "07": "Membro superior",
        "08": "Membro inferior",
        "09": "Pé",
        "10": "Todo o corpo",
        "11": "Outro",
        "99": "Ignorado",
    },

    "PART_CORP2": {
        "01": "Olho",
        "02": "Cabeça",
        "03": "Pescoço",
        "04": "Tórax",
        "05": "Abdome",
        "06": "Mão",
        "07": "Membro superior",
        "08": "Membro inferior",
        "09": "Pé",
        "10": "Todo o corpo",
        "11": "Outro",
        "99": "Ignorado",
    },

    "PART_CORP3": {
        "01": "Olho",
        "02": "Cabeça",
        "03": "Pescoço",
        "04": "Tórax",
        "05": "Abdome",
        "06": "Mão",
        "07": "Membro superior",
        "08": "Membro inferior",
        "09": "Pé",
        "10": "Todo o corpo",
        "11": "Outro",
        "99": "Ignorado",
    },

    "REGIME": {
        "1": "Hospitalar",
        "2": "Ambulatorial",
        "3": "Ambos",
        "9": "Ignorado",
    },

    "EVOLUCAO": {
        "1": "Cura",
        "2": "Incapacidade temporária",
        "3": "Incapacidade parcial permanente",
        "4": "Incapacidade total permanente",
        "5": "Óbito por acidente de trabalho grave",
        "6": "Óbito por outras causas",
        "7": "Outro",
        "9": "Ignorado",
    },

    "CAT": {
        "1": "Sim",
        "2": "Não",
        "3": "Não se aplica",
        "9": "Ignorado",
    },
}


# ============================================================
# COLUNAS SENSÍVEIS
# ============================================================

COLUNAS_SENSIVEIS = [
    "NM_PACIENT",
    "NM_MAE_PAC",
    "NM_LOGRADO",
    "NU_NUMERO",
    "NM_COMPLEM",
    "NU_CEP",
    "NU_DDD_TEL",
    "NU_TELEFON",
    "ID_CNS_SUS",
]


# ============================================================
# FUNÇÕES DE LIMPEZA
# ============================================================

def normalizar_valor(valor):
    """
    Converte valores vazios, nulos ou inválidos para Ignorado.
    """
    if pd.isna(valor):
        return "Ignorado"

    texto = str(valor).strip()

    if texto == "":
        return "Ignorado"

    if texto.lower() in ["nan", "none", "nat", "null"]:
        return "Ignorado"

    return texto


def normalizar_codigo(valor, largura=None):
    """
    Normaliza códigos do DBF.

    Exemplo:
    1.0 -> 1
    01 -> 01
    vazio -> Ignorado
    """
    valor = normalizar_valor(valor)

    if valor == "Ignorado":
        return valor

    texto = str(valor).strip()

    if texto.endswith(".0"):
        texto = texto[:-2]

    if largura and texto.isdigit():
        texto = texto.zfill(largura)

    return texto


def aplicar_ignorados(df):
    """
    Aplica Ignorado em campos vazios de todo o DataFrame.
    """
    df = df.copy()

    for col in df.columns:
        df[col] = df[col].apply(normalizar_valor)

    return df


# ============================================================
# IDADE
# ============================================================

def calcular_idade_linha(row):
    """
    Calcula idade usando DT_NASC e DT_ACID.
    Se não for possível, tenta usar NU_IDADE_N.
    """
    nascimento = pd.to_datetime(row.get("DT_NASC", None), errors="coerce")
    acidente = pd.to_datetime(row.get("DT_ACID", None), errors="coerce")

    if pd.notna(nascimento) and pd.notna(acidente):
        idade = acidente.year - nascimento.year

        if (acidente.month, acidente.day) < (nascimento.month, nascimento.day):
            idade -= 1

        if 0 <= idade <= 120:
            return idade

    idade_banco = row.get("NU_IDADE_N", None)

    if idade_banco is not None:
        texto = str(idade_banco).strip()

        if texto.endswith(".0"):
            texto = texto[:-2]

        if texto.isdigit():
            # Em alguns bancos SINAN a idade pode vir codificada.
            # Nesta primeira versão, usamos apenas valores plausíveis.
            idade = int(texto[-3:]) if len(texto) > 3 else int(texto)

            if 0 <= idade <= 120:
                return idade

    return pd.NA


def criar_faixa_etaria(idade):
    if pd.isna(idade):
        return "Ignorado"

    idade = int(idade)

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


def aplicar_idade(df):
    df = df.copy()

    df["IDADE_CALCULADA"] = df.apply(calcular_idade_linha, axis=1)
    df["FAIXA_ETARIA_CALCULADA"] = df["IDADE_CALCULADA"].apply(criar_faixa_etaria)

    return df


# ============================================================
# MAPEAMENTO PRINCIPAL
# ============================================================

def aplicar_mapeamento(df):
    """
    Aplica:
    - normalização de vazios;
    - tradução de códigos;
    - CBO;
    - idade calculada.
    """
    df = df.copy()

    # Padroniza nomes das colunas
    df.columns = [str(c).strip().upper() for c in df.columns]

    # Datas principais antes da transformação geral
    for col in ["DT_NOTIFIC", "DT_ACID", "DT_NASC", "DT_OBITO"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Decodifica os campos mapeados
    for coluna, mapa in DICIONARIOS.items():
        if coluna in df.columns:
            largura = 2 if coluna in ["SIT_TRAB", "PART_CORP1", "PART_CORP2", "PART_CORP3"] else None

            codigos = df[coluna].apply(lambda v: normalizar_codigo(v, largura=largura))

            df[f"{coluna}_DESC"] = (
                codigos
                .map(mapa)
                .fillna(codigos)
                .replace("", "Ignorado")
            )

            df[f"{coluna}_DESC"] = df[f"{coluna}_DESC"].apply(normalizar_valor)

    # Aplica CBO
    df = aplicar_cbo(df, coluna_cbo="ID_OCUPA_N", caminho="data/cbo.csv")

    # Idade calculada
    df = aplicar_idade(df)

    # Limpa vazios remanescentes, mas preserva datas como datas
    for col in df.columns:
        if col not in ["DT_NOTIFIC", "DT_ACID", "DT_NASC", "DT_OBITO"]:
            df[col] = df[col].apply(normalizar_valor)

    return df


def gerar_tabela_publica(df):
    """
    Remove dados sensíveis da visualização pública.
    """
    colunas_remover = [c for c in COLUNAS_SENSIVEIS if c in df.columns]
    return df.drop(columns=colunas_remover, errors="ignore")
