# Mapeamento inicial da ficha Acidente de Trabalho Grave

CAMPOS_PRINCIPAIS = {
    "NU_NOTIFIC": "Número da Notificação",
    "TP_NOT": "Tipo de Notificação",
    "ID_AGRAVO": "Agravo/doença",
    "DT_NOTIFIC": "Data da Notificação",
    "SEM_NOT": "Semana Epidemiológica da Notificação",
    "DT_ACID": "Data do Acidente",
    "SEM_ACID": "Semana Epidemiológica do Acidente",
    "NM_PACIENT": "Nome do Paciente",
    "DT_NASC": "Data de Nascimento",
    "NU_IDADE_N": "Idade",
    "CS_SEXO": "Sexo",
    "CS_GESTANT": "Gestante",
    "CS_RACA": "Raça/Cor",
    "CS_ESCOL_N": "Escolaridade",
    "NM_MAE_PAC": "Nome da Mãe",
    "NM_BAIRRO": "Bairro de Residência",
    "NM_LOGRADO": "Logradouro",
    "ID_OCUPA_N": "Ocupação",
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
    "DS_OBS": "Observações"
}


DICIONARIOS = {
    "TP_NOT": {
        "2": "Individual"
    },

    "CS_SEXO": {
        "M": "Masculino",
        "F": "Feminino",
        "I": "Ignorado"
    },

    "CS_GESTANT": {
        "1": "1º trimestre",
        "2": "2º trimestre",
        "3": "3º trimestre",
        "4": "Idade gestacional ignorada",
        "5": "Não",
        "6": "Não se aplica",
        "9": "Ignorado"
    },

    "CS_RACA": {
        "1": "Branca",
        "2": "Preta",
        "3": "Amarela",
        "4": "Parda",
        "5": "Indígena",
        "9": "Ignorado"
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
        "10": "Não se aplica"
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
        "99": "Ignorado"
    },

    "LOCAL_ACID": {
        "1": "Instalações do contratante",
        "2": "Via pública",
        "3": "Instalações de terceiros",
        "4": "Domicílio próprio",
        "9": "Ignorado"
    },

    "TIPO_ACID": {
        "1": "Típico",
        "2": "Trajeto",
        "9": "Ignorado"
    },

    "MAIS_TRAB": {
        "1": "Sim",
        "2": "Não",
        "9": "Ignorado"
    },

    "ATENDE_MED": {
        "1": "Sim",
        "2": "Não",
        "9": "Ignorado"
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
        "99": "Ignorado"
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
        "99": "Ignorado"
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
        "99": "Ignorado"
    },

    "REGIME": {
        "1": "Hospitalar",
        "2": "Ambulatorial",
        "3": "Ambos",
        "9": "Ignorado"
    },

    "EVOLUCAO": {
        "1": "Cura",
        "2": "Incapacidade temporária",
        "3": "Incapacidade parcial permanente",
        "4": "Incapacidade total permanente",
        "5": "Óbito por acidente de trabalho grave",
        "6": "Óbito por outras causas",
        "7": "Outro",
        "9": "Ignorado"
    },

    "CAT": {
        "1": "Sim",
        "2": "Não",
        "3": "Não se aplica",
        "9": "Ignorado"
    }
}


COLUNAS_SENSIVEIS = [
    "NM_PACIENT",
    "NM_MAE_PAC",
    "NM_LOGRADO",
    "NU_NUMERO",
    "NM_COMPLEM",
    "NU_CEP",
    "NU_DDD_TEL",
    "NU_TELEFON",
    "ID_CNS_SUS"
]


def aplicar_mapeamento(df):
    """
    Renomeia campos principais e cria colunas traduzidas.
    Mantém colunas originais e acrescenta *_DESC.
    """
    df = df.copy()

    for coluna, mapa in DICIONARIOS.items():
        if coluna in df.columns:
            df[f"{coluna}_DESC"] = (
                df[coluna]
                .astype(str)
                .str.strip()
                .map(mapa)
                .fillna(df[coluna].astype(str))
            )

    return df


def gerar_tabela_publica(df):
    """
    Remove dados sensíveis da visualização pública.
    """
    colunas_remover = [c for c in COLUNAS_SENSIVEIS if c in df.columns]
    return df.drop(columns=colunas_remover, errors="ignore")
