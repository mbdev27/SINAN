import pandas as pd


CAMPOS_AVALIADOS_POR_AGRAVO = {
    "Acidente de Trabalho Grave": [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_ACID",
        "NM_PACIENT",
        "DT_NASC",
        "NU_IDADE_N",
        "CS_SEXO",
        "CS_GESTANT",
        "CS_RACA",
        "CS_ESCOL_N",
        "NM_MAE_PAC",
        "ID_MN_RESI",
        "NM_BAIRRO",
        "NM_LOGRADO",
        "ID_OCUPA_N",
        "SIT_TRAB",
        "LOCAL_ACID",
        "CNAE",
        "TIPO_ACID",
        "MAIS_TRAB",
        "ATENDE_MED",
        "PART_CORP1",
        "CID_LESAO",
        "REGIME",
        "EVOLUCAO",
        "CAT",
        "DS_OBS",
    ],

    "Violência Interpessoal/Autoprovocada": [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_AGRAVO",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_OCOR",
        "NM_PACIENT",
        "DT_NASC",
        "NU_IDADE_N",
        "CS_SEXO",
        "CS_GESTANT",
        "CS_RACA",
        "CS_ESCOL_N",
        "NM_MAE_PAC",
        "ID_MN_RESI",
        "NM_BAIRRO",
        "NM_LOGRADO",
        "ID_OCUPA_N",
        "LOCAL_OCOR",
        "OUT_VEZES",
        "LES_AUTOP",
        "VIOL_FISIC",
        "VIOL_PSICO",
        "VIOL_SEXU",
        "NUM_ENVOLV",
        "AUTOR_SEXO",
        "REL_TRAB",
        "DT_ENCERRA",
    ],

    "Dengue/Chikungunya": [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_AGRAVO",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_SIN_PRI",
        "NM_PACIENT",
        "DT_NASC",
        "NU_IDADE_N",
        "CS_SEXO",
        "CS_GESTANT",
        "CS_RACA",
        "CS_ESCOL_N",
        "NM_MAE_PAC",
        "ID_MN_RESI",
        "NM_BAIRRO",
        "ID_OCUPA_N",
        "DT_INVEST",
        "FEBRE",
        "MIALGIA",
        "CEFALEIA",
        "EXANTEMA",
        "VOMITO",
        "NAUSEA",
        "DOR_COSTAS",
        "CLASSI_FIN",
        "CRITERIO",
        "EVOLUCAO",
        "DT_ENCERRA",
    ],

    "Intoxicação Exógena": [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_AGRAVO",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_SIN_PRI",
        "NM_PACIENT",
        "DT_NASC",
        "NU_IDADE_N",
        "CS_SEXO",
        "CS_GESTANT",
        "CS_RACA",
        "CS_ESCOL_N",
        "NM_MAE_PAC",
        "ID_MN_RESI",
        "NM_BAIRRO",
        "ID_OCUPA_N",
        "SIT_TRAB",
        "LOCAL_EXPO",
        "GRUPO_AGEN",
        "AGENTE_TOX",
        "VIA_1",
        "VIA_EXPO",
        "CIRCUNST",
        "TIPO_EXP",
        "TP_ATEND",
        "HOSPITALIZ",
        "REL_TRAB",
        "CAT",
        "CLASSI_FIN",
        "CRITERIO",
        "EVOLUCAO",
        "DT_ENCERRA",
    ],
}


CAMPOS_OBRIGATORIOS_POR_AGRAVO = {
    "Acidente de Trabalho Grave": [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_ACID",
        "NM_PACIENT",
        "DT_NASC",
        "CS_SEXO",
        "CS_RACA",
        "CS_ESCOL_N",
        "ID_OCUPA_N",
        "SIT_TRAB",
        "LOCAL_ACID",
        "TIPO_ACID",
        "EVOLUCAO",
    ],

    "Violência Interpessoal/Autoprovocada": [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_AGRAVO",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_OCOR",
        "NM_PACIENT",
        "DT_NASC",
        "CS_SEXO",
        "CS_RACA",
        "CS_ESCOL_N",
        "ID_MN_RESI",
        "LOCAL_OCOR",
        "LES_AUTOP",
        "VIOL_FISIC",
        "VIOL_SEXU",
        "NUM_ENVOLV",
        "AUTOR_SEXO",
    ],

    "Dengue/Chikungunya": [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_AGRAVO",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_SIN_PRI",
        "NM_PACIENT",
        "DT_NASC",
        "CS_SEXO",
        "CS_RACA",
        "CLASSI_FIN",
        "CRITERIO",
        "EVOLUCAO",
    ],

    "Intoxicação Exógena": [
        "NU_NOTIFIC",
        "DT_NOTIFIC",
        "ID_AGRAVO",
        "ID_MUNICIP",
        "ID_UNIDADE",
        "DT_SIN_PRI",
        "NM_PACIENT",
        "DT_NASC",
        "CS_SEXO",
        "CS_RACA",
        "LOCAL_EXPO",
        "GRUPO_AGEN",
        "CIRCUNST",
        "CLASSI_FIN",
        "CRITERIO",
        "EVOLUCAO",
    ],
}


def campo_preenchido(valor):
    if pd.isna(valor):
        return False

    texto = str(valor).strip()

    if texto == "":
        return False

    if texto.lower() in [
        "nan",
        "none",
        "nat",
        "null",
        "ignorado",
        "não informado",
        "nao informado",
    ]:
        return False

    return True


def calcular_percentual_linha(row, campos_avaliados):
    campos_existentes = [
        campo for campo in campos_avaliados
        if campo in row.index
    ]

    if not campos_existentes:
        return 0

    preenchidos = sum(
        campo_preenchido(row[campo])
        for campo in campos_existentes
    )

    return round(
        (preenchidos / len(campos_existentes)) * 100,
        1
    )


def classificar_qualidade(percentual):
    if percentual < 70:
        return "🚩 Ruim"

    if percentual < 90:
        return "🟨 Mediana"

    return "🟩 Boa"


def verificar_obrigatorios_linha(row, campos_obrigatorios):
    faltantes = []

    for campo in campos_obrigatorios:
        if campo in row.index:
            if not campo_preenchido(row[campo]):
                faltantes.append(campo)
        else:
            faltantes.append(campo)

    if faltantes:
        return "⚠️ Faltando: " + ", ".join(faltantes)

    return "✅ Obrigatórios preenchidos"


def adicionar_qualidade_ficha(df, agravo):
    df = df.copy()

    campos_avaliados = CAMPOS_AVALIADOS_POR_AGRAVO.get(
        agravo,
        list(df.columns)
    )

    campos_obrigatorios = CAMPOS_OBRIGATORIOS_POR_AGRAVO.get(
        agravo,
        []
    )

    df["PERCENTUAL_PREENCHIMENTO"] = df.apply(
        lambda row: calcular_percentual_linha(
            row,
            campos_avaliados
        ),
        axis=1
    )

    df["QUALIDADE_PREENCHIMENTO"] = df[
        "PERCENTUAL_PREENCHIMENTO"
    ].apply(
        classificar_qualidade
    )

    df["ALERTA_OBRIGATORIOS"] = df.apply(
        lambda row: verificar_obrigatorios_linha(
            row,
            campos_obrigatorios
        ),
        axis=1
    )

    return df


def resumo_qualidade_ficha(df):
    if (
        df.empty
        or "PERCENTUAL_PREENCHIMENTO" not in df.columns
    ):
        return {
            "media": 0,
            "ruins": 0,
            "medianas": 0,
            "boas": 0,
            "alertas": 0,
        }

    media = df["PERCENTUAL_PREENCHIMENTO"].mean()

    ruins = df["QUALIDADE_PREENCHIMENTO"].str.contains(
        "Ruim",
        na=False
    ).sum()

    medianas = df["QUALIDADE_PREENCHIMENTO"].str.contains(
        "Mediana",
        na=False
    ).sum()

    boas = df["QUALIDADE_PREENCHIMENTO"].str.contains(
        "Boa",
        na=False
    ).sum()

    alertas = df["ALERTA_OBRIGATORIOS"].str.contains(
        "Faltando",
        na=False
    ).sum()

    return {
        "media": round(media, 1),
        "ruins": int(ruins),
        "medianas": int(medianas),
        "boas": int(boas),
        "alertas": int(alertas),
    }


def colocar_qualidade_no_inicio(df):
    colunas_prioritarias = [
        "PERCENTUAL_PREENCHIMENTO",
        "QUALIDADE_PREENCHIMENTO",
        "ALERTA_OBRIGATORIOS",
    ]

    colunas_existentes = [
        col for col in colunas_prioritarias
        if col in df.columns
    ]

    demais_colunas = [
        col for col in df.columns
        if col not in colunas_existentes
    ]

    return df[
        colunas_existentes + demais_colunas
    ]
