import pandas as pd


def primeira_coluna_existente(df, candidatos):
    for coluna in candidatos:
        if coluna in df.columns:
            return coluna
    return None


def gerar_alerta(tipo, nivel, titulo, descricao, recomendacao):
    return {
        "Tipo": tipo,
        "Nível": nivel,
        "Título": titulo,
        "Descrição": descricao,
        "Recomendação": recomendacao,
    }


def alerta_aumento_incomum(df, coluna_data):
    alertas = []

    if not coluna_data or coluna_data not in df.columns:
        return alertas

    base = df.copy()
    base[coluna_data] = pd.to_datetime(base[coluna_data], errors="coerce")
    base = base.dropna(subset=[coluna_data])

    if base.empty:
        return alertas

    base["MES"] = base[coluna_data].dt.to_period("M").astype(str)

    serie = (
        base
        .groupby("MES")
        .size()
        .reset_index(name="Registros")
        .sort_values("MES")
    )

    if len(serie) < 3:
        return alertas

    media = serie["Registros"].mean()
    ultimo = serie["Registros"].iloc[-1]
    mes = serie["MES"].iloc[-1]

    if media > 0 and ultimo >= media * 1.5:
        alertas.append(
            gerar_alerta(
                tipo="Tendência temporal",
                nivel="Alto",
                titulo="Aumento incomum de notificações",
                descricao=(
                    f"O mês {mes} registrou {ultimo} notificações, "
                    f"acima da média histórica filtrada de {media:.1f}."
                ),
                recomendacao=(
                    "Verificar se há surto, mudança de fluxo de notificação, "
                    "duplicidades ou represamento de digitação."
                )
            )
        )

    elif media > 0 and ultimo >= media * 1.25:
        alertas.append(
            gerar_alerta(
                tipo="Tendência temporal",
                nivel="Médio",
                titulo="Crescimento acima do padrão",
                descricao=(
                    f"O mês {mes} apresentou {ultimo} notificações, "
                    f"acima da média filtrada de {media:.1f}."
                ),
                recomendacao=(
                    "Monitorar a evolução nos próximos períodos e comparar "
                    "com dados territoriais e unidades notificadoras."
                )
            )
        )

    return alertas


def alerta_baixa_completude(auditoria):
    alertas = []

    score = auditoria.get("score_banco", 0)

    try:
        score = float(score)
    except Exception:
        score = 0

    if score < 50:
        alertas.append(
            gerar_alerta(
                tipo="Qualidade do banco",
                nivel="Alto",
                titulo="Score geral de qualidade crítico",
                descricao=f"O banco apresenta score geral de preenchimento de {score}%.",
                recomendacao=(
                    "Realizar revisão das fichas, qualificar campos obrigatórios "
                    "e priorizar unidades com maior incompletude."
                )
            )
        )

    elif score < 70:
        alertas.append(
            gerar_alerta(
                tipo="Qualidade do banco",
                nivel="Médio",
                titulo="Score geral de qualidade regular",
                descricao=f"O banco apresenta score geral de preenchimento de {score}%.",
                recomendacao=(
                    "Recomenda-se revisar os campos com menor preenchimento "
                    "antes de utilizar o banco em análises oficiais."
                )
            )
        )

    return alertas


def alerta_unidade_baixa_completude(auditoria):
    alertas = []

    tabela = auditoria.get("incompletude_unidade", pd.DataFrame())

    if not isinstance(tabela, pd.DataFrame) or tabela.empty:
        return alertas

    coluna_preenchimento = None

    for c in ["Preenchimento (%)", "preenchimento", "Score"]:
        if c in tabela.columns:
            coluna_preenchimento = c
            break

    if not coluna_preenchimento:
        return alertas

    base = tabela.copy()
    base[coluna_preenchimento] = pd.to_numeric(
        base[coluna_preenchimento],
        errors="coerce"
    )

    criticas = base[base[coluna_preenchimento] < 50]

    if not criticas.empty:
        nomes = []

        for _, linha in criticas.head(5).iterrows():
            unidade = (
                linha.get("Nome da unidade")
                or linha.get("Unidade")
                or linha.get("CNES")
                or "Unidade não identificada"
            )

            nomes.append(str(unidade))

        alertas.append(
            gerar_alerta(
                tipo="Unidade notificadora",
                nivel="Alto",
                titulo="Unidades com baixa completude",
                descricao=(
                    f"Foram identificadas {len(criticas)} unidades com "
                    "preenchimento inferior a 50%."
                ),
                recomendacao=(
                    "Priorizar qualificação junto às unidades: "
                    + "; ".join(nomes)
                )
            )
        )

    return alertas


def alerta_duplicidades(auditoria):
    alertas = []

    duplicidades = auditoria.get("duplicidades", pd.DataFrame())

    if not isinstance(duplicidades, pd.DataFrame) or duplicidades.empty:
        return alertas

    qtd = len(duplicidades)

    nivel = "Alto" if qtd >= 10 else "Médio"

    alertas.append(
        gerar_alerta(
            tipo="Duplicidade",
            nivel=nivel,
            titulo="Duplicidades prováveis identificadas",
            descricao=f"Foram identificados {qtd} registros com duplicidade provável.",
            recomendacao=(
                "Conferir nome do paciente, nome da mãe e data de ocorrência/início "
                "dos sintomas antes de consolidar indicadores."
            )
        )
    )

    return alertas


def alerta_inconsistencias_criticas(auditoria):
    alertas = []

    regras = [
        (
            "sexo_incompativel",
            "Sexo incompatível",
            "Foram encontrados registros com incompatibilidade entre sexo e campos relacionados.",
            "Revisar sexo biológico e campos dependentes, como gestante."
        ),
        (
            "idade_incompativel",
            "Idade incompatível",
            "Foram encontrados registros com idade fora de faixa plausível.",
            "Revisar data de nascimento, idade informada e data de ocorrência."
        ),
        (
            "cid_incompativel",
            "CID incompatível",
            "Foram encontrados registros com CID em formato incompatível.",
            "Revisar o campo CID/agravo e corrigir códigos inválidos."
        ),
        (
            "municipio_divergente",
            "Município divergente",
            "Foram encontrados registros com divergência entre município de notificação e residência.",
            "Verificar se a divergência é esperada ou se indica erro de digitação/codificação."
        ),
    ]

    for chave, titulo, descricao, recomendacao in regras:
        tabela = auditoria.get(chave, pd.DataFrame())

        if isinstance(tabela, pd.DataFrame) and not tabela.empty:
            qtd = len(tabela)

            alertas.append(
                gerar_alerta(
                    tipo="Inconsistência",
                    nivel="Médio" if qtd < 10 else "Alto",
                    titulo=titulo,
                    descricao=f"{descricao} Quantidade identificada: {qtd}.",
                    recomendacao=recomendacao
                )
            )

    return alertas


def alerta_campos_criticos_vazios(df):
    alertas = []

    if df is None or df.empty:
        return alertas

    campos_criticos = [
        "DT_NOTIFIC",
        "DT_SIN_PRI",
        "DT_OCOR",
        "DT_ACID",
        "NM_PACIENT",
        "NM_MAE_PAC",
        "DT_NASC",
        "CS_SEXO",
        "ID_MUNICIP",
        "ID_MN_RESI",
        "ID_UNIDADE",
        "CO_UNI_NOT",
        "CLASSI_FIN",
        "EVOLUCAO",
        "CRITERIO",
    ]

    existentes = [c for c in campos_criticos if c in df.columns]

    if not existentes:
        return alertas

    resultado = []

    for campo in existentes:
        vazio = (
            df[campo]
            .replace("", pd.NA)
            .isna()
            .mean()
        ) * 100

        if vazio >= 20:
            resultado.append((campo, round(vazio, 1)))

    if resultado:
        resultado_ordenado = sorted(resultado, key=lambda x: x[1], reverse=True)

        descricao = "; ".join(
            [f"{campo}: {perc}%" for campo, perc in resultado_ordenado[:8]]
        )

        alertas.append(
            gerar_alerta(
                tipo="Campos críticos",
                nivel="Alto",
                titulo="Campos críticos com alto percentual de vazio",
                descricao=descricao,
                recomendacao=(
                    "Priorizar esses campos na qualificação do banco, pois eles "
                    "impactam diretamente a análise epidemiológica e operacional."
                )
            )
        )

    return alertas


def gerar_alertas_inteligentes(df, auditoria, coluna_data=None):
    alertas = []

    alertas.extend(alerta_aumento_incomum(df, coluna_data))
    alertas.extend(alerta_baixa_completude(auditoria))
    alertas.extend(alerta_unidade_baixa_completude(auditoria))
    alertas.extend(alerta_duplicidades(auditoria))
    alertas.extend(alerta_inconsistencias_criticas(auditoria))
    alertas.extend(alerta_campos_criticos_vazios(df))

    if not alertas:
        alertas.append(
            gerar_alerta(
                tipo="Situação geral",
                nivel="Baixo",
                titulo="Nenhum alerta crítico identificado",
                descricao=(
                    "O banco não apresentou sinais críticos automáticos no recorte analisado."
                ),
                recomendacao=(
                    "Manter rotina de monitoramento, auditoria e qualificação periódica."
                )
            )
        )

    return pd.DataFrame(alertas)


def classificar_cor_nivel(nivel):
    nivel = str(nivel).lower()

    if "alto" in nivel:
        return "🔴"

    if "médio" in nivel or "medio" in nivel:
        return "🟠"

    if "baixo" in nivel:
        return "🟢"

    return "⚪"
