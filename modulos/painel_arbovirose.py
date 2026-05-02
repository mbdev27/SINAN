import streamlit as st
import pandas as pd
import plotly.express as px

from utils.tema import CORES, PALETA
from mappings.arbovirose import gerar_tabela_publica_arbovirose
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


def barras_sim(df, colunas, titulo):
    dados = []

    for col in colunas:
        col_desc = f"{col}_DESC"

        if col_desc in df.columns:
            qtd = (
                df[col_desc]
                .astype(str)
                .str.upper()
                .str.strip()
                .eq("SIM")
                .sum()
            )

            if qtd > 0:
                dados.append({
                    "Variável": col.replace("_", " ").title(),
                    "Quantidade": int(qtd)
                })

    if not dados:
        st.info(f"Não há dados suficientes para o gráfico: {titulo}.")
        return

    base = pd.DataFrame(dados).sort_values("Quantidade")

    fig = px.bar(
        base,
        x="Quantidade",
        y="Variável",
        orientation="h",
        title=titulo,
        color_discrete_sequence=[CORES["azul"]]
    )

    st.plotly_chart(fig, use_container_width=True)


def render_painel_arbovirose(df):
    st.markdown("""
    <div class="mb-header">
        <h1>🦟 Painel Analítico — Arboviroses</h1>
        <p>
            Análise dos registros de Dengue e Febre de Chikungunya,
            com indicadores clínicos, laboratoriais, classificação,
            evolução, hospitalização, sinais de alarme e dengue grave.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Nenhum banco DBF carregado.")
        return

    df = df.copy()
    df_publico = gerar_tabela_publica_arbovirose(df)

    for col in [
        "DT_NOTIFIC",
        "DT_SIN_PRI",
        "DT_NASC",
        "DT_INVEST",
        "DT_INTERNA",
        "DT_OBITO",
        "DT_ENCERRA",
        "DT_ALRM",
        "DT_GRAV",
    ]:
        if col in df_publico.columns:
            df_publico[col] = pd.to_datetime(df_publico[col], errors="coerce")

    st.sidebar.header("🔎 Filtros — Arboviroses")

    df_filtrado = df_publico.copy()

    usar_periodo_total = st.sidebar.checkbox(
        "Selecionar todo o período disponível",
        value=True,
        key="periodo_arbovirose"
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
                key="datas_arbovirose"
            )

            df_filtrado = df_filtrado[
                (df_filtrado[data_base].dt.date >= data_ini)
                &
                (df_filtrado[data_base].dt.date <= data_fim)
            ]

    df_filtrado = filtro_multiselect(df_filtrado, "Agravo", "AGRAVO_DESC", "arb_agravo")
    df_filtrado = filtro_multiselect(df_filtrado, "Classificação final", "CLASSI_FIN_DESC", "arb_classi")
    df_filtrado = filtro_multiselect(df_filtrado, "Critério", "CRITERIO_DESC", "arb_criterio")
    df_filtrado = filtro_multiselect(df_filtrado, "Evolução", "EVOLUCAO_DESC", "arb_evolucao")
    df_filtrado = filtro_multiselect(df_filtrado, "Hospitalização", "HOSPITALIZ_DESC", "arb_hosp")
    df_filtrado = filtro_multiselect(df_filtrado, "Sexo", "CS_SEXO_DESC", "arb_sexo")
    df_filtrado = filtro_multiselect(df_filtrado, "Raça/Cor", "CS_RACA_DESC", "arb_raca")
    df_filtrado = filtro_multiselect(df_filtrado, "Faixa Etária", "FAIXA_ETARIA_CALCULADA", "arb_faixa")

    busca = st.text_input(
        "🔍 Pesquisar qualquer termo no banco filtrado",
        key="busca_geral_arbovirose"
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

    dengue = 0
    chik = 0
    sinais_alarme = 0
    dengue_grave = 0
    obitos = 0
    hospitalizados = 0

    if "CLASSI_FIN_DESC" in df_filtrado.columns:
        dengue = df_filtrado["CLASSI_FIN_DESC"].astype(str).str.upper().eq("DENGUE").sum()
        sinais_alarme = df_filtrado["CLASSI_FIN_DESC"].astype(str).str.contains("SINAIS", case=False, na=False).sum()
        dengue_grave = df_filtrado["CLASSI_FIN_DESC"].astype(str).str.contains("GRAVE", case=False, na=False).sum()
        chik = df_filtrado["CLASSI_FIN_DESC"].astype(str).str.contains("CHIK", case=False, na=False).sum()

    if "EVOLUCAO_DESC" in df_filtrado.columns:
        obitos = df_filtrado["EVOLUCAO_DESC"].astype(str).str.contains("Óbito|Obito", case=False, na=False).sum()

    if "HOSPITALIZ_DESC" in df_filtrado.columns:
        hospitalizados = df_filtrado["HOSPITALIZ_DESC"].astype(str).str.upper().eq("SIM").sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Registros", total)
    c2.metric("Dengue", int(dengue))
    c3.metric("Chikungunya", int(chik))
    c4.metric("Sinais de alarme", int(sinais_alarme))
    c5.metric("Dengue grave", int(dengue_grave))
    c6.metric("Óbitos", int(obitos))

    st.metric("Hospitalizados", int(hospitalizados))

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

    st.header("🧬 Classificação e Evolução")

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

    st.header("🩺 Sinais Clínicos")

    sintomas = [
        "FEBRE",
        "MIALGIA",
        "CEFALEIA",
        "EXANTEMA",
        "VOMITO",
        "NAUSEA",
        "DOR_COSTAS",
        "CONJUNTVIT",
        "ARTRITE",
        "ARTRALGIA",
        "PETEQUIA_N",
        "LEUCOPENIA",
        "LACO",
        "DOR_RETRO",
    ]

    barras_sim(df_filtrado, sintomas, "Frequência de sinais clínicos")

    st.header("🧪 Resultados Laboratoriais")

    col5, col6 = st.columns(2)

    if "RESUL_SORO_DESC" in df_filtrado.columns:
        base = df_filtrado["RESUL_SORO_DESC"].value_counts().reset_index()
        base.columns = ["Sorologia Dengue", "Quantidade"]

        fig = px.bar(
            base,
            x="Sorologia Dengue",
            y="Quantidade",
            title="Sorologia IgM Dengue",
            color_discrete_sequence=[CORES["verde"]]
        )

        col5.plotly_chart(fig, use_container_width=True)

    if "RESUL_NS1_DESC" in df_filtrado.columns:
        base = df_filtrado["RESUL_NS1_DESC"].value_counts().reset_index()
        base.columns = ["NS1", "Quantidade"]

        fig = px.bar(
            base,
            x="NS1",
            y="Quantidade",
            title="Exame NS1",
            color_discrete_sequence=[CORES["laranja"]]
        )

        col6.plotly_chart(fig, use_container_width=True)

    st.header("⚠️ Dengue com Sinais de Alarme")

    sinais_alarme_cols = [
        "ALRM_HIPOT",
        "ALRM_PLAQ",
        "ALRM_VOM",
        "ALRM_SANG",
        "ALRM_HEMAT",
        "ALRM_ABDOM",
        "ALRM_LETAR",
        "ALRM_HEPAT",
        "ALRM_LIQ",
    ]

    barras_sim(df_filtrado, sinais_alarme_cols, "Sinais de alarme")

    st.header("🚨 Dengue Grave")

    dengue_grave_cols = [
        "GRAV_PULSO",
        "GRAV_CONV",
        "GRAV_ENCH",
        "GRAV_INSUF",
        "GRAV_TAQUI",
        "GRAV_EXTRE",
        "GRAV_HIPOT",
        "GRAV_HEMAT",
        "GRAV_MELEN",
        "GRAV_METRO",
        "GRAV_SANG",
        "GRAV_AST",
        "GRAV_MIOC",
        "GRAV_CONSC",
        "GRAV_ORGAO",
    ]

    barras_sim(df_filtrado, dengue_grave_cols, "Critérios de dengue grave")

    df_filtrado = adicionar_qualidade_ficha(
        df_filtrado,
        "Dengue/Chikungunya"
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
        file_name="arbovirose_dengue_chikungunya.csv",
        mime="text/csv"
    )
