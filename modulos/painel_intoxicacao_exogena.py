import streamlit as st
import pandas as pd
import plotly.express as px

from utils.tema import CORES, PALETA
from mappings.intoxicacao_exogena import gerar_tabela_publica_intoxicacao_exogena
from utils.qualidade_ficha import (
    adicionar_qualidade_ficha,
    resumo_qualidade_ficha,
    colocar_qualidade_no_inicio,
)


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

    selecionados = st.sidebar.multiselect(label, opcoes, key=key)

    if selecionados:
        return df[df[coluna].isin(selecionados)]

    return df


def render_painel_intoxicacao_exogena(df):
    st.markdown("""
    <div class="mb-header">
        <h1>☣️ Painel Analítico — Intoxicação Exógena</h1>
        <p>
            Análise dos registros de intoxicação exógena, com foco em agente tóxico,
            circunstância da exposição, via de contaminação, relação com trabalho,
            hospitalização, classificação final, evolução e qualidade do preenchimento.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Nenhum banco DBF carregado.")
        return

    df = df.copy()
    df_publico = gerar_tabela_publica_intoxicacao_exogena(df)

    for col in [
        "DT_NOTIFIC",
        "DT_SIN_PRI",
        "DT_NASC",
        "DT_INVEST",
        "DT_INTERNA",
        "DT_OBITO",
        "DT_ENCERRA",
    ]:
        if col in df_publico.columns:
            df_publico[col] = pd.to_datetime(df_publico[col], errors="coerce")

    st.sidebar.header("🔎 Filtros — Intoxicação Exógena")

    df_filtrado = df_publico.copy()

    usar_periodo_total = st.sidebar.checkbox(
        "Selecionar todo o período disponível",
        value=True,
        key="periodo_intoxicacao"
    )

    data_base = None

    for candidato in ["DT_SIN_PRI", "DT_NOTIFIC"]:
        if candidato in df_filtrado.columns:
            data_base = candidato
            break

    if data_base:
        min_d = df_filtrado[data_base].min()
        max_d = df_filtrado[data_base].max()

        if pd.notna(min_d) and pd.notna(max_d) and not usar_periodo_total:
            data_ini, data_fim = st.sidebar.date_input(
                "Período",
                value=[min_d.date(), max_d.date()],
                min_value=min_d.date(),
                max_value=max_d.date(),
                key="datas_intoxicacao"
            )

            df_filtrado = df_filtrado[
                (df_filtrado[data_base].dt.date >= data_ini)
                &
                (df_filtrado[data_base].dt.date <= data_fim)
            ]

    df_filtrado = filtro_multiselect(df_filtrado, "Sexo", "CS_SEXO_DESC", "intox_sexo")
    df_filtrado = filtro_multiselect(df_filtrado, "Raça/Cor", "CS_RACA_DESC", "intox_raca")
    df_filtrado = filtro_multiselect(df_filtrado, "Faixa Etária", "FAIXA_ETARIA_CALCULADA", "intox_faixa")
    df_filtrado = filtro_multiselect(df_filtrado, "Situação no Trabalho", "SIT_TRAB_DESC", "intox_sit_trab")
    df_filtrado = filtro_multiselect(df_filtrado, "Local da Exposição", "LOCAL_EXPO_DESC", "intox_local")
    df_filtrado = filtro_multiselect(df_filtrado, "Grupo do Agente Tóxico", "GRUPO_AGENTE_DESC", "intox_agente")
    df_filtrado = filtro_multiselect(df_filtrado, "Via de Exposição", "VIA_EXPOSICAO_DESC", "intox_via")
    df_filtrado = filtro_multiselect(df_filtrado, "Circunstância", "CIRCUNSTANCIA_DESC", "intox_circ")
    df_filtrado = filtro_multiselect(df_filtrado, "Tipo de Exposição", "TIPO_EXPOSICAO_DESC", "intox_tipo")
    df_filtrado = filtro_multiselect(df_filtrado, "Tipo de Atendimento", "TIPO_ATENDIMENTO_DESC", "intox_atend")
    df_filtrado = filtro_multiselect(df_filtrado, "Hospitalização", "HOSPITALIZ_DESC", "intox_hosp")
    df_filtrado = filtro_multiselect(df_filtrado, "Relacionada ao Trabalho", "REL_TRAB_DESC", "intox_trab")
    df_filtrado = filtro_multiselect(df_filtrado, "Classificação Final", "CLASSI_FIN_DESC", "intox_classi")
    df_filtrado = filtro_multiselect(df_filtrado, "Evolução", "EVOLUCAO_DESC", "intox_evolucao")

    busca = st.text_input(
        "🔍 Pesquisar qualquer termo no banco filtrado",
        key="busca_geral_intoxicacao"
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

    confirmadas = 0
    hospitalizados = 0
    obitos = 0
    relacionadas_trabalho = 0
    tentativa_suicidio = 0

    if "CLASSI_FIN_DESC" in df_filtrado.columns:
        confirmadas = df_filtrado["CLASSI_FIN_DESC"].astype(str).str.contains(
            "Intoxicação confirmada",
            case=False,
            na=False
        ).sum()

    if "HOSPITALIZ_DESC" in df_filtrado.columns:
        hospitalizados = df_filtrado["HOSPITALIZ_DESC"].astype(str).str.upper().eq("SIM").sum()

    if "EVOLUCAO_DESC" in df_filtrado.columns:
        obitos = df_filtrado["EVOLUCAO_DESC"].astype(str).str.contains(
            "Óbito|Obito",
            case=False,
            na=False
        ).sum()

    if "REL_TRAB_DESC" in df_filtrado.columns:
        relacionadas_trabalho = df_filtrado["REL_TRAB_DESC"].astype(str).str.upper().eq("SIM").sum()

    if "CIRCUNSTANCIA_DESC" in df_filtrado.columns:
        tentativa_suicidio = df_filtrado["CIRCUNSTANCIA_DESC"].astype(str).str.contains(
            "Tentativa de suicídio",
            case=False,
            na=False
        ).sum()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Registros", total)
    c2.metric("Confirmadas", int(confirmadas))
    c3.metric("Hospitalizados", int(hospitalizados))
    c4.metric("Óbitos", int(obitos))
    c5.metric("Tentativa de suicídio", int(tentativa_suicidio))

    st.metric("Relacionadas ao trabalho", int(relacionadas_trabalho))

    st.header("📈 Série Temporal")

    if data_base:
        serie_base = df_filtrado.dropna(subset=[data_base]).copy()
        serie_base["MES"] = serie_base[data_base].dt.to_period("M").astype(str)

        serie = (
            serie_base
            .groupby("MES")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("MES")
        )

        if not serie.empty:
            fig = px.line(
                serie,
                x="MES",
                y="Quantidade",
                markers=True,
                title="Casos por mês",
                color_discrete_sequence=[CORES["azul"]]
            )

            st.plotly_chart(fig, use_container_width=True)

    st.header("☣️ Exposição e Agente Tóxico")

    col1, col2 = st.columns(2)

    if "GRUPO_AGENTE_DESC" in df_filtrado.columns:
        base = df_filtrado["GRUPO_AGENTE_DESC"].value_counts().reset_index()
        base.columns = ["Grupo do agente", "Quantidade"]

        fig = px.bar(
            base,
            x="Grupo do agente",
            y="Quantidade",
            title="Grupo do Agente Tóxico",
            color_discrete_sequence=[CORES["azul"]]
        )

        col1.plotly_chart(fig, use_container_width=True)

    if "LOCAL_EXPO_DESC" in df_filtrado.columns:
        base = df_filtrado["LOCAL_EXPO_DESC"].value_counts().reset_index()
        base.columns = ["Local", "Quantidade"]

        fig = px.bar(
            base,
            x="Local",
            y="Quantidade",
            title="Local da Exposição",
            color_discrete_sequence=[CORES["verde"]]
        )

        col2.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    if "VIA_EXPOSICAO_DESC" in df_filtrado.columns:
        base = df_filtrado["VIA_EXPOSICAO_DESC"].value_counts().reset_index()
        base.columns = ["Via", "Quantidade"]

        fig = px.bar(
            base,
            x="Via",
            y="Quantidade",
            title="Via de Exposição",
            color_discrete_sequence=[CORES["laranja"]]
        )

        col3.plotly_chart(fig, use_container_width=True)

    if "CIRCUNSTANCIA_DESC" in df_filtrado.columns:
        base = df_filtrado["CIRCUNSTANCIA_DESC"].value_counts().reset_index()
        base.columns = ["Circunstância", "Quantidade"]

        fig = px.bar(
            base,
            x="Circunstância",
            y="Quantidade",
            title="Circunstância da Exposição",
            color_discrete_sequence=[CORES["azul"]]
        )

        col4.plotly_chart(fig, use_container_width=True)

    st.header("🏥 Atendimento e Desfecho")

    col5, col6 = st.columns(2)

    if "TIPO_ATENDIMENTO_DESC" in df_filtrado.columns:
        base = df_filtrado["TIPO_ATENDIMENTO_DESC"].value_counts().reset_index()
        base.columns = ["Atendimento", "Quantidade"]

        fig = px.bar(
            base,
            x="Atendimento",
            y="Quantidade",
            title="Tipo de Atendimento",
            color_discrete_sequence=[CORES["verde"]]
        )

        col5.plotly_chart(fig, use_container_width=True)

    if "EVOLUCAO_DESC" in df_filtrado.columns:
        base = df_filtrado["EVOLUCAO_DESC"].value_counts().reset_index()
        base.columns = ["Evolução", "Quantidade"]

        fig = px.bar(
            base,
            x="Evolução",
            y="Quantidade",
            title="Evolução do Caso",
            color_discrete_sequence=[CORES["laranja"]]
        )

        col6.plotly_chart(fig, use_container_width=True)

    st.header("👥 Perfil Epidemiológico")

    col7, col8 = st.columns(2)

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

        col7.plotly_chart(fig, use_container_width=True)

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
            color_discrete_sequence=[CORES["azul"]]
        )

        col8.plotly_chart(fig, use_container_width=True)

    df_filtrado = adicionar_qualidade_ficha(
        df_filtrado,
        "Intoxicação Exógena"
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
        file_name="intoxicacao_exogena.csv",
        mime="text/csv"
    )
