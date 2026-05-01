import streamlit as st
import pandas as pd
import plotly.express as px

from utils.tema import CORES, PALETA
from mappings.violencia import gerar_tabela_publica_violencia
from utils.qualidade_ficha import (
    adicionar_qualidade_ficha,
    resumo_qualidade_ficha,
    colocar_qualidade_no_inicio,
)


def barras_sim_nao(df, colunas, titulo):
    dados = []

    for coluna in colunas:
        col_desc = f"{coluna}_DESC"

        if col_desc in df.columns:
            sim = (
                df[col_desc]
                .astype(str)
                .str.upper()
                .str.strip()
                .eq("SIM")
                .sum()
            )

            if sim > 0:
                dados.append({
                    "Categoria": coluna.replace("_", " ").title(),
                    "Quantidade": sim
                })

    if not dados:
        st.info(f"Não há dados suficientes para o gráfico: {titulo}.")
        return

    base = pd.DataFrame(dados).sort_values("Quantidade")

    fig = px.bar(
        base,
        x="Quantidade",
        y="Categoria",
        orientation="h",
        title=titulo,
        color_discrete_sequence=[CORES["azul"]]
    )

    st.plotly_chart(fig, use_container_width=True)


def filtro_multiselect(df, label, coluna, key):
    if coluna not in df.columns:
        return df

    opcoes = (
        df[coluna]
        .fillna("Ignorado")
        .astype(str)
        .str.strip()
        .replace("", "Ignorado")
        .sort_values()
        .unique()
        .tolist()
    )

    selecionados = st.sidebar.multiselect(
        label,
        opcoes,
        key=key
    )

    if selecionados:
        return df[df[coluna].isin(selecionados)]

    return df


def render_painel_violencia(df):
    st.markdown("""
    <div class="mb-header">
        <h1>🛡️ Painel Analítico — Violência Interpessoal/Autoprovocada</h1>
        <p>
            Análise dos registros de violência interpessoal e autoprovocada,
            com filtros específicos, indicadores, perfil da pessoa atendida,
            características da ocorrência, violência sexual, provável autor,
            encaminhamentos e qualidade do preenchimento.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Nenhum banco DBF carregado.")
        return

    df = df.copy()
    df_publico = gerar_tabela_publica_violencia(df)

    for col in ["DT_NOTIFIC", "DT_OCOR", "DT_NASC", "DT_OBITO", "DT_ENCERRA"]:
        if col in df_publico.columns:
            df_publico[col] = pd.to_datetime(df_publico[col], errors="coerce")

    st.sidebar.header("🔎 Filtros — Violência")

    df_filtrado = df_publico.copy()

    usar_periodo_total = st.sidebar.checkbox(
        "Selecionar todo o período disponível",
        value=True,
        key="periodo_violencia"
    )

    if "DT_OCOR" in df_filtrado.columns:
        min_d = df_filtrado["DT_OCOR"].min()
        max_d = df_filtrado["DT_OCOR"].max()

        if pd.notna(min_d) and pd.notna(max_d) and not usar_periodo_total:
            data_ini, data_fim = st.sidebar.date_input(
                "Período da ocorrência",
                value=[min_d.date(), max_d.date()],
                min_value=min_d.date(),
                max_value=max_d.date(),
                key="datas_violencia"
            )

            df_filtrado = df_filtrado[
                (df_filtrado["DT_OCOR"].dt.date >= data_ini)
                &
                (df_filtrado["DT_OCOR"].dt.date <= data_fim)
            ]

    df_filtrado = filtro_multiselect(df_filtrado, "Sexo", "CS_SEXO_DESC", "viol_sexo")
    df_filtrado = filtro_multiselect(df_filtrado, "Raça/Cor", "CS_RACA_DESC", "viol_raca")
    df_filtrado = filtro_multiselect(df_filtrado, "Faixa Etária", "FAIXA_ETARIA_CALCULADA", "viol_faixa")
    df_filtrado = filtro_multiselect(df_filtrado, "Local de ocorrência", "LOCAL_OCOR_DESC", "viol_local")
    df_filtrado = filtro_multiselect(df_filtrado, "Lesão autoprovocada", "LES_AUTOP_DESC", "viol_auto")
    df_filtrado = filtro_multiselect(df_filtrado, "Ocorreu outras vezes", "OUT_VEZES_DESC", "viol_recorrencia")
    df_filtrado = filtro_multiselect(df_filtrado, "Violência relacionada ao trabalho", "REL_TRAB_DESC", "viol_trab")
    df_filtrado = filtro_multiselect(df_filtrado, "Evolução", "EVOLUCAO_DESC", "viol_evolucao")

    busca = st.text_input(
        "🔍 Pesquisar qualquer termo no banco filtrado",
        key="busca_geral_violencia"
    )

    if busca:
        mask = df_filtrado.astype(str).apply(
            lambda col: col.str.contains(busca, case=False, na=False)
        ).any(axis=1)

        df_filtrado = df_filtrado[mask]

    if df_filtrado.empty:
        st.warning("Nenhum registro encontrado com os filtros aplicados.")
        return

    st.header("📊 Indicadores Principais")

    total = len(df_filtrado)

    autoprovocada = 0
    if "LES_AUTOP_DESC" in df_filtrado.columns:
        autoprovocada = (
            df_filtrado["LES_AUTOP_DESC"]
            .astype(str)
            .str.upper()
            .eq("SIM")
            .sum()
        )

    sexual = 0
    if "VIOL_SEXU_DESC" in df_filtrado.columns:
        sexual = (
            df_filtrado["VIOL_SEXU_DESC"]
            .astype(str)
            .str.upper()
            .eq("SIM")
            .sum()
        )

    recorrente = 0
    if "OUT_VEZES_DESC" in df_filtrado.columns:
        recorrente = (
            df_filtrado["OUT_VEZES_DESC"]
            .astype(str)
            .str.upper()
            .eq("SIM")
            .sum()
        )

    trabalho = 0
    if "REL_TRAB_DESC" in df_filtrado.columns:
        trabalho = (
            df_filtrado["REL_TRAB_DESC"]
            .astype(str)
            .str.upper()
            .eq("SIM")
            .sum()
        )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Registros", total)
    c2.metric("Autoprovocada", int(autoprovocada))
    c3.metric("Violência sexual", int(sexual))
    c4.metric("Recorrente", int(recorrente))
    c5.metric("Relacionada ao trabalho", int(trabalho))

    st.header("📈 Perfil da Pessoa Atendida")

    col1, col2 = st.columns(2)

    if "CS_SEXO_DESC" in df_filtrado.columns:
        sexo = df_filtrado["CS_SEXO_DESC"].value_counts().reset_index()
        sexo.columns = ["Sexo", "Quantidade"]

        fig = px.pie(
            sexo,
            names="Sexo",
            values="Quantidade",
            title="Distribuição por Sexo",
            color_discrete_sequence=PALETA,
            hole=0.35
        )

        col1.plotly_chart(fig, use_container_width=True)

    if "FAIXA_ETARIA_CALCULADA" in df_filtrado.columns:
        faixa = df_filtrado["FAIXA_ETARIA_CALCULADA"].value_counts().reset_index()
        faixa.columns = ["Faixa etária", "Quantidade"]

        ordem = [
            "0 a 9 anos",
            "10 a 19 anos",
            "20 a 29 anos",
            "30 a 39 anos",
            "40 a 49 anos",
            "50 a 59 anos",
            "60 anos ou mais",
            "Ignorado",
        ]

        faixa["Faixa etária"] = pd.Categorical(
            faixa["Faixa etária"],
            categories=ordem,
            ordered=True
        )

        faixa = faixa.sort_values("Faixa etária")

        fig = px.bar(
            faixa,
            x="Faixa etária",
            y="Quantidade",
            title="Distribuição por Faixa Etária",
            color_discrete_sequence=[CORES["verde"]]
        )

        col2.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    if "CS_RACA_DESC" in df_filtrado.columns:
        raca = df_filtrado["CS_RACA_DESC"].value_counts().reset_index()
        raca.columns = ["Raça/Cor", "Quantidade"]

        fig = px.bar(
            raca,
            x="Raça/Cor",
            y="Quantidade",
            title="Distribuição por Raça/Cor",
            color_discrete_sequence=[CORES["azul"]]
        )

        col3.plotly_chart(fig, use_container_width=True)

    if "LOCAL_OCOR_DESC" in df_filtrado.columns:
        local = df_filtrado["LOCAL_OCOR_DESC"].value_counts().reset_index()
        local.columns = ["Local", "Quantidade"]

        fig = px.bar(
            local,
            x="Local",
            y="Quantidade",
            title="Local de Ocorrência",
            color_discrete_sequence=[CORES["laranja"]]
        )

        col4.plotly_chart(fig, use_container_width=True)

    st.header("🧩 Características da Violência")

    tipo_violencia = [
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
    ]

    barras_sim_nao(
        df_filtrado,
        tipo_violencia,
        "Tipos de Violência"
    )

    meio_agressao = [
        "AG_FORCA",
        "AG_ENFOR",
        "AG_OBJETO",
        "AG_CORTE",
        "AG_QUENTE",
        "AG_ENVEN",
        "AG_FOGO",
        "AG_AMEACA",
        "AG_OUTROS",
    ]

    barras_sim_nao(
        df_filtrado,
        meio_agressao,
        "Meios de Agressão"
    )

    st.header("🚨 Violência Sexual e Encaminhamentos")

    violencia_sexual = [
        "SEX_ASSEDI",
        "SEX_ESTUPR",
        "SEX_PORNO",
        "SEX_EXPLO",
        "SEX_OUTRO",
    ]

    barras_sim_nao(
        df_filtrado,
        violencia_sexual,
        "Tipos de Violência Sexual"
    )

    encaminhamentos = [
        "ENC_SAUDE",
        "ENC_TUTELA",
        "ENC_DEAM",
        "ENC_MPU",
        "ENC_MULHER",
        "ENC_CREAS",
        "ENC_OUTR",
    ]

    barras_sim_nao(
        df_filtrado,
        encaminhamentos,
        "Encaminhamentos Realizados"
    )

    st.header("👤 Provável Autor da Violência")

    col5, col6 = st.columns(2)

    if "AUTOR_SEXO_DESC" in df_filtrado.columns:
        autor = df_filtrado["AUTOR_SEXO_DESC"].value_counts().reset_index()
        autor.columns = ["Sexo do autor", "Quantidade"]

        fig = px.pie(
            autor,
            names="Sexo do autor",
            values="Quantidade",
            title="Sexo do Provável Autor",
            color_discrete_sequence=PALETA,
            hole=0.35
        )

        col5.plotly_chart(fig, use_container_width=True)

    if "CICL_VID_DESC" in df_filtrado.columns:
        ciclo = df_filtrado["CICL_VID_DESC"].value_counts().reset_index()
        ciclo.columns = ["Ciclo de vida", "Quantidade"]

        fig = px.bar(
            ciclo,
            x="Ciclo de vida",
            y="Quantidade",
            title="Ciclo de Vida do Provável Autor",
            color_discrete_sequence=[CORES["azul"]]
        )

        col6.plotly_chart(fig, use_container_width=True)

    if "DT_OCOR" in df_filtrado.columns:
        st.header("📆 Série Temporal")

        serie_base = df_filtrado.dropna(subset=["DT_OCOR"]).copy()
        serie_base["MES"] = serie_base["DT_OCOR"].dt.to_period("M").astype(str)

        serie = (
            serie_base
            .groupby("MES")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("MES")
        )

        fig = px.line(
            serie,
            x="MES",
            y="Quantidade",
            markers=True,
            title="Ocorrências por Mês",
            color_discrete_sequence=[CORES["azul"]]
        )

        st.plotly_chart(fig, use_container_width=True)

    df_filtrado = adicionar_qualidade_ficha(
        df_filtrado,
        "Violência Interpessoal/Autoprovocada"
    )

    df_filtrado = colocar_qualidade_no_inicio(df_filtrado)

    resumo = resumo_qualidade_ficha(df_filtrado)

    st.header("🧾 Qualidade do Preenchimento das Fichas")

    q1, q2, q3, q4, q5 = st.columns(5)

    q1.metric("Média", f"{resumo['media']}%")
    q2.metric("🚩 Ruins", resumo["ruins"])
    q3.metric("🟨 Medianas", resumo["medianas"])
    q4.metric("🟩 Boas", resumo["boas"])
    q5.metric("⚠️ Obrigatórios ausentes", resumo["alertas"])

    st.header("📋 Dados Decodificados")

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=650,
        column_config={
            "PERCENTUAL_PREENCHIMENTO": st.column_config.ProgressColumn(
                "Preenchimento da ficha",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "QUALIDADE_PREENCHIMENTO": st.column_config.TextColumn(
                "Qualidade"
            ),
            "ALERTA_OBRIGATORIOS": st.column_config.TextColumn(
                "Campos obrigatórios"
            ),
        }
    )

    st.download_button(
        "📥 Baixar dados filtrados em CSV",
        data=df_filtrado.to_csv(index=False).encode("utf-8"),
        file_name="violencia_interpessoal_autoprovocada.csv",
        mime="text/csv"
    )
