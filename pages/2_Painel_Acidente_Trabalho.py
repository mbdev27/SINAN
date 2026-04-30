# ============================================================
# QUALIDADE DO PREENCHIMENTO DA FICHA
# ============================================================

CAMPOS_AVALIADOS_FICHA = [
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
    "DS_OBS"
]

CAMPOS_OBRIGATORIOS_FICHA = [
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
    "EVOLUCAO"
]


def campo_preenchido(valor):
    if pd.isna(valor):
        return False

    texto = str(valor).strip()

    if texto == "":
        return False

    if texto.lower() in ["nan", "none", "nat", "null"]:
        return False

    if texto.upper() == "IGNORADO":
        return False

    return True


def calcular_percentual_preenchimento(row):
    campos_existentes = [c for c in CAMPOS_AVALIADOS_FICHA if c in row.index]

    if not campos_existentes:
        return 0

    preenchidos = sum(campo_preenchido(row[c]) for c in campos_existentes)

    return round((preenchidos / len(campos_existentes)) * 100, 1)


def classificar_preenchimento(percentual):
    if percentual < 70:
        return "🚩 Ruim"

    if percentual < 90:
        return "🟨 Mediana"

    return "🟩 Boa"


def verificar_obrigatorios(row):
    faltantes = []

    for campo in CAMPOS_OBRIGATORIOS_FICHA:
        if campo in row.index:
            if not campo_preenchido(row[campo]):
                faltantes.append(campo)

    if faltantes:
        return "⚠️ Faltando: " + ", ".join(faltantes)

    return "✅ Obrigatórios preenchidos"


df_filtrado = df_filtrado.copy()

df_filtrado["PERCENTUAL_PREENCHIMENTO"] = df_filtrado.apply(
    calcular_percentual_preenchimento,
    axis=1
)

df_filtrado["QUALIDADE_PREENCHIMENTO"] = df_filtrado["PERCENTUAL_PREENCHIMENTO"].apply(
    classificar_preenchimento
)

df_filtrado["ALERTA_OBRIGATORIOS"] = df_filtrado.apply(
    verificar_obrigatorios,
    axis=1
)
