import streamlit as st
import pandas as pd
import plotly.express as px

from utils.tema import CORES, PALETA
from mappings.toxoplasmose import gerar_tabela_publica_toxoplasmose
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


def render_painel_toxoplasmose(df):
    st.markdown("""
    <div class="mb-header">
        <h1>🧬 Painel Analítico — Toxoplasmose</h1>
        <p>
            Análise de notificações de toxoplasmose adquirida, gestacional e congênita,
            com indicadores de classificação, critério de confirmação, evolução,
            perfil epidemiológico e qualidade do preenchimento.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Nenhum banco DBF carregado.")
        return

    df = df.copy()
    df_publico = gerar_tabela_publica_toxoplasmose(df)

    for col in [
        "DT_NOTIFIC",
        "DT_SIN_PRI",
        "DT_NASC",
        "DT_INVEST",
        "DT_OBITO",
        "DT_ENCERRA",
    ]:
        if col in df_publico.columns:
            df_publico[col] = pd.to_datetime(df_publico[col], errors="coerce")

    st.sidebar.header("🔎 Filtros — Toxoplasmose")

    df_filtrado = df_publico.copy()

    usar_periodo_total = st.sidebar.checkbox(
        "Selecionar todo o período disponível",
        value=True,
        key="periodo_toxo"
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
                key="datas_toxo"
            )

            df_filtrado = df_filtrado[
                (df_filtrado[data_base].dt.date >= data_ini)
                &
                (df_filtrado[data_base].dt.date <= data_fim)
            ]

    df_filtrado = filtro_multiselect(df_filtrado, "Tipo de toxoplasmose", "TIPO_TOXOPLASMOSE", "toxo_tipo")
    df_filtrado = filtro_multiselect(df_filtrado, "Sexo", "CS_SEXO_DESC", "toxo_sexo")
    df_filtrado = filtro_multiselect(df_filtrado, "Raça/Cor", "CS_RACA_DESC", "toxo_raca")
    df_filtrado = filtro_multiselect(df_filtrado, "Gestante", "CS_GESTANT_DESC", "toxo_gestante")
    df_filtrado = filtro_multiselect(df_filtrado, "Faixa Etária", "FAIXA_ETARIA_CALCULADA", "toxo_faixa")
    df_filtrado = filtro_multiselect(df_filtrado, "Classificação Final", "CLASSI_FIN_DESC", "toxo_classi")
    df_filtrado = filtro_multiselect(df_filtrado, "Critério", "CRITERIO_DESC", "toxo_criterio")
    df_filtrado = filtro_multiselect(df_filtrado, "Autóctone", "TPAUTOCTO_DESC", "toxo_autoctone")
    df_filtrado = filtro_multiselect(df_filtrado, "Relacionada ao trabalho", "REL_TRAB_DESC", "toxo_trab")
    df_filtrado = filtro_multiselect(df_filtrado, "Evolução", "EVOLUCAO_DESC", "toxo_evolucao")

    busca = st.text_input(
        "🔍 Pesquisar qualquer termo no banco filtrado",
        key="busca_geral_toxo"
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

    confirmados = 0
    descartados = 0
    obitos = 0
    gestacionais = 0
    congenitas = 0

    if "CLASSI_FIN_DESC" in df_filtrado.columns:
        confirmados = df_filtrado["CLASSI_FIN_DESC"].astype(str).str.contains(
            "Confirmado",
            case=False,
            na=False
        ).sum()

        descartados = df_filtrado["CLASSI_FIN_DESC"].astype(str).str.contains(
            "Descartado",
            case=False,
            na=False
        ).sum()

    if "EVOLUCAO_DESC" in df_filtrado.columns:
        obitos = df_filtrado["EVOLUCAO_DESC"].astype(str).str.contains(
            "Óbito|Obito",
            case=False,
            na=False
        ).sum()

    if "TIPO_TOXOPLASMOSE" in df_filtrado.columns:
        gestacionais = df_filtrado["TIPO_TOXOPLASMOSE"].astype(str).str.contains(
            "Gestacional",
            case=False,
            na=False
        ).sum()

        congenitas = df_filtrado["TIPO_TOXOPLASMOSE"].astype(str).str.contains(
            "Congênita|Congenita",
            case=False,
            na=False
        ).sum()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Registros", total)
    c2.metric("Confirmados", int(confirmados))
    c3.metric("Descartados", int(descartados))
    c4.metric("Gestacional", int(gestacionais))
    c5.metric("Congênita", int(congenitas))

    st.metric("Óbitos", int(obitos))

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

    st.header("🧪 Classificação e Critério")

    col1, col2 = st.columns(2)

    if "CLASSI_FIN_DESC" in df_filtrado.columns:
        base = df_filtrado["CLASSI_FIN_DESC"].value_counts().reset_index()
        base.columns = ["Classificação", "Quantidade"]

        fig = px.bar(
            base,
            x="Classificação",
            y="Quantidade",
            title="Classificação Final",
            color_discrete_sequence=[CORES["verde"]]
        )

        col1.plotly_chart(fig, use_container_width=True)

    if "CRITERIO_DESC" in df_filtrado.columns:
        base = df_filtrado["CRITERIO_DESC"].value_counts().reset_index()
        base.columns = ["Critério", "Quantidade"]

        fig = px.bar(
            base,
            x="Critério",
            y="Quantidade",
            title="Critério de Confirmação/Descarte",
            color_discrete_sequence=[CORES["laranja"]]
        )

        col2.plotly_chart(fig, use_container_width=True)

    st.header("👥 Perfil Epidemiológico")

    col3, col4 = st.columns(2)

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

        col3.plotly_chart(fig, use_container_width=True)

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

        col4.plotly_chart(fig, use_container_width=True)

    st.header("🧬 Tipo de Toxoplasmose")

    if "TIPO_TOXOPLASMOSE" in df_filtrado.columns:
        base = df_filtrado["TIPO_TOXOPLASMOSE"].value_counts().reset_index()
        base.columns = ["Tipo", "Quantidade"]

        fig = px.bar(
            base,
            x="Tipo",
            y="Quantidade",
            title="Distribuição por tipo de toxoplasmose",
            color_discrete_sequence=[CORES["azul"]]
        )

        st.plotly_chart(fig, use_container_width=True)

    df_filtrado = adicionar_qualidade_ficha(
        df_filtrado,
        "Toxoplasmose"
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
        file_name="toxoplasmose.csv",
        mime="text/csv"
    )
