import streamlit as st
import pandas as pd
import plotly.express as px

from utils.tema import CORES, PALETA
from mappings.generico_sinan import gerar_tabela_publica_generica


def primeira_coluna_existente(df, candidatos):
    for coluna in candidatos:
        if coluna in df.columns:
            return coluna

    return None


def grafico_barras(df, coluna, titulo):
    if coluna not in df.columns:
        return

    base = (
        df[coluna]
        .fillna("Ignorado")
        .astype(str)
        .str.strip()
        .replace("", "Ignorado")
        .value_counts()
        .reset_index()
    )

    base.columns = ["Categoria", "Quantidade"]

    if base.empty:
        return

    fig = px.bar(
        base.head(20),
        x="Categoria",
        y="Quantidade",
        title=titulo,
        color_discrete_sequence=[CORES["emerald"]]
    )

    fig.update_layout(
        template="horizonte_dark",
        height=470
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def render_painel_generico_sinan(df, nome_agravo="Agravo SINAN"):
    st.markdown(
        f"""
        <div class="hz-hero">
            <span class="hz-kicker">Painel Universal SINAN</span>
            <h1>{nome_agravo}</h1>
            <p>
                Visão geral automática para bancos DBF do SINAN ainda sem painel
                específico. Este módulo apresenta indicadores básicos, perfil
                epidemiológico, série temporal, qualidade e estrutura do banco.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df is None or df.empty:
        st.warning("Nenhum banco DBF carregado.")
        return

    df = df.copy()
    df_publico = gerar_tabela_publica_generica(df)

    data_base = primeira_coluna_existente(
        df_publico,
        [
            "DT_SIN_PRI",
            "DT_NOTIFIC",
            "DT_OCOR",
            "DT_ACID",
            "DT_DIAG",
            "DT_INVEST",
        ]
    )

    unidade = primeira_coluna_existente(
        df_publico,
        [
            "ID_UNIDADE",
            "CO_UNI_NOT",
            "CNES",
            "UNIDADE_NOTIFICANTE",
        ]
    )

    municipio = primeira_coluna_existente(
        df_publico,
        [
            "ID_MUNICIP",
            "ID_MN_RESI",
            "MUNICIPIO",
            "MUNICIPIO_RESIDENCIA",
        ]
    )

    st.sidebar.header("🔎 Filtros — Painel Universal")

    df_filtrado = df_publico.copy()

    if data_base:
        df_filtrado[data_base] = pd.to_datetime(
            df_filtrado[data_base],
            errors="coerce"
        )

        min_d = df_filtrado[data_base].min()
        max_d = df_filtrado[data_base].max()

        usar_tudo = st.sidebar.checkbox(
            "Selecionar todo o período disponível",
            value=True,
            key="periodo_generico"
        )

        if pd.notna(min_d) and pd.notna(max_d) and not usar_tudo:
            data_ini, data_fim = st.sidebar.date_input(
                "Período",
                value=[min_d.date(), max_d.date()],
                min_value=min_d.date(),
                max_value=max_d.date(),
                key="datas_generico"
            )

            df_filtrado = df_filtrado[
                (df_filtrado[data_base].dt.date >= data_ini)
                &
                (df_filtrado[data_base].dt.date <= data_fim)
            ]

    for label, coluna, key in [
        ("Sexo", "CS_SEXO_DESC", "gen_sexo"),
        ("Raça/Cor", "CS_RACA_DESC", "gen_raca"),
        ("Gestante", "CS_GESTANT_DESC", "gen_gestante"),
        ("Faixa etária", "FAIXA_ETARIA_CALCULADA", "gen_faixa"),
        ("Unidade", unidade, "gen_unidade"),
        ("Município", municipio, "gen_municipio"),
    ]:
        if coluna and coluna in df_filtrado.columns:
            opcoes = (
                df_filtrado[coluna]
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
                df_filtrado = df_filtrado[
                    df_filtrado[coluna]
                    .astype(str)
                    .isin(selecionados)
                ]

    busca = st.text_input(
        "🔍 Pesquisar qualquer termo no banco",
        key="busca_generica"
    )

    if busca:
        mascara = df_filtrado.astype(str).apply(
            lambda col: col.str.contains(
                busca,
                case=False,
                na=False
            )
        ).any(axis=1)

        df_filtrado = df_filtrado[mascara]

    if df_filtrado.empty:
        st.warning("Nenhum registro encontrado com os filtros aplicados.")
        return

    st.header("📊 Indicadores Gerais")

    total = len(df_filtrado)
    colunas = len(df_filtrado.columns)

    duplicados = 0

    chaves_dup = [
        c for c in [
            "NM_PACIENT",
            "NM_MAE_PAC",
            "DT_SIN_PRI",
            "DT_OCOR",
            "DT_NOTIFIC"
        ]
        if c in df_filtrado.columns
    ]

    if len(chaves_dup) >= 2:
        duplicados = int(
            df_filtrado.duplicated(
                subset=chaves_dup,
                keep=False
            ).sum()
        )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Registros", total)
    c2.metric("Colunas", colunas)
    c3.metric("Duplicidades", duplicados)
    c4.metric("Data base", data_base or "Não localizada")

    st.header("📈 Série Temporal")

    if data_base:
        serie_base = df_filtrado.dropna(
            subset=[data_base]
        ).copy()

        if not serie_base.empty:
            serie_base["MES"] = (
                serie_base[data_base]
                .dt.to_period("M")
                .astype(str)
            )

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
                title="Registros por mês",
                color_discrete_sequence=[CORES["emerald"]]
            )

            fig.update_layout(
                template="horizonte_dark",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("Não há datas válidas para série temporal.")
    else:
        st.info("Não foi localizada uma coluna de data para série temporal.")

    st.header("👥 Perfil Epidemiológico")

    p1, p2 = st.columns(2)

    with p1:
        if "CS_SEXO_DESC" in df_filtrado.columns:
            grafico_barras(
                df_filtrado,
                "CS_SEXO_DESC",
                "Distribuição por sexo"
            )

        if "CS_RACA_DESC" in df_filtrado.columns:
            grafico_barras(
                df_filtrado,
                "CS_RACA_DESC",
                "Distribuição por raça/cor"
            )

    with p2:
        if "FAIXA_ETARIA_CALCULADA" in df_filtrado.columns:
            grafico_barras(
                df_filtrado,
                "FAIXA_ETARIA_CALCULADA",
                "Distribuição por faixa etária"
            )

        if unidade:
            grafico_barras(
                df_filtrado,
                unidade,
                "Registros por unidade notificadora"
            )

    st.header("🧱 Estrutura do Banco")

    estrutura = pd.DataFrame({
        "Campo": df_filtrado.columns,
        "Tipo": [
            str(df_filtrado[c].dtype)
            for c in df_filtrado.columns
        ],
        "Preenchidos": [
            int(df_filtrado[c].replace("", pd.NA).notna().sum())
            for c in df_filtrado.columns
        ],
        "Preenchimento (%)": [
            round(
                (
                    df_filtrado[c]
                    .replace("", pd.NA)
                    .notna()
                    .mean()
                ) * 100,
                1
            )
            for c in df_filtrado.columns
        ],
    })

    st.dataframe(
        estrutura.sort_values("Preenchimento (%)"),
        use_container_width=True,
        height=460
    )

    st.header("📋 Dados")

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=650
    )

    st.download_button(
        "📥 Baixar dados filtrados em CSV",
        data=df_filtrado.to_csv(index=False).encode("utf-8"),
        file_name="painel_universal_sinan.csv",
        mime="text/csv"
    )
