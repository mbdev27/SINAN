import pandas as pd
import streamlit as st
import plotly.express as px

from utils.tema import CORES
from mappings.generico_sinan import gerar_tabela_publica_generica
from utils.auditoria_sinan import gerar_auditoria_sinan


def primeira_coluna_existente(df, candidatos):
    for coluna in candidatos:
        if coluna in df.columns:
            return coluna
    return None


def preparar_texto(serie):
    return (
        serie
        .fillna("Ignorado")
        .astype(str)
        .str.strip()
        .replace("", "Ignorado")
    )


def grafico_barras(df, coluna, titulo, limite=20):
    if coluna not in df.columns:
        st.info(f"Coluna não localizada: {coluna}")
        return

    base = (
        preparar_texto(df[coluna])
        .value_counts()
        .reset_index()
    )

    base.columns = ["Categoria", "Quantidade"]

    if base.empty:
        st.info("Sem dados disponíveis.")
        return

    fig = px.bar(
        base.head(limite),
        x="Categoria",
        y="Quantidade",
        title=titulo,
        color_discrete_sequence=[CORES["emerald"]]
    )

    fig.update_layout(
        template="horizonte_dark",
        height=470,
        xaxis_title="",
        yaxis_title="Registros"
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_pizza(df, coluna, titulo):
    if coluna not in df.columns:
        return

    base = (
        preparar_texto(df[coluna])
        .value_counts()
        .reset_index()
    )

    base.columns = ["Categoria", "Quantidade"]

    if base.empty:
        return

    fig = px.pie(
        base,
        names="Categoria",
        values="Quantidade",
        title=titulo,
        color_discrete_sequence=[
            CORES["emerald"],
            CORES["navy"],
            "#14B8A6",
            "#1D4ED8",
            "#F59E0B",
            "#DC2626",
        ]
    )

    fig.update_layout(
        template="horizonte_dark",
        height=470
    )

    st.plotly_chart(fig, use_container_width=True)


def montar_estrutura(df):
    return pd.DataFrame({
        "Campo": df.columns,
        "Tipo": [str(df[c].dtype) for c in df.columns],
        "Preenchidos": [
            int(df[c].replace("", pd.NA).notna().sum())
            for c in df.columns
        ],
        "Vazios": [
            int(df[c].replace("", pd.NA).isna().sum())
            for c in df.columns
        ],
        "Preenchimento (%)": [
            round(df[c].replace("", pd.NA).notna().mean() * 100, 1)
            for c in df.columns
        ],
    }).sort_values("Preenchimento (%)")


def detectar_colunas_principais(df):
    return {
        "data": primeira_coluna_existente(
            df,
            [
                "DT_SIN_PRI",
                "DT_NOTIFIC",
                "DT_OCOR",
                "DT_ACID",
                "DT_DIAG",
                "DT_INVEST",
                "DT_ENCERRA",
            ]
        ),
        "sexo": primeira_coluna_existente(
            df,
            [
                "CS_SEXO_DESC",
                "SEXO",
                "CS_SEXO",
            ]
        ),
        "idade": primeira_coluna_existente(
            df,
            [
                "FAIXA_ETARIA_CALCULADA",
                "FAIXA_ETARIA",
                "NU_IDADE_N",
                "IDADE",
                "IDADE_CALCULADA",
            ]
        ),
        "raca": primeira_coluna_existente(
            df,
            [
                "CS_RACA_DESC",
                "RACA_COR",
                "CS_RACA",
            ]
        ),
        "municipio": primeira_coluna_existente(
            df,
            [
                "ID_MUNICIP",
                "ID_MUNICIP_NOT",
                "ID_MN_RESI",
                "MUNICIPIO",
                "MUNICIPIO_RESIDENCIA",
                "MUNICIPIO_NOTIFICACAO",
            ]
        ),
        "bairro": primeira_coluna_existente(
            df,
            [
                "ID_BAIRRO",
                "NM_BAIRRO",
                "BAIRRO",
                "BAIRRO_RESIDENCIA",
            ]
        ),
        "unidade": primeira_coluna_existente(
            df,
            [
                "ID_UNIDADE",
                "CO_UNI_NOT",
                "CNES",
                "UNIDADE_NOTIFICANTE",
                "NM_UNID_NOT",
            ]
        ),
        "evolucao": primeira_coluna_existente(
            df,
            [
                "EVOLUCAO",
                "EVOLUCAO_DESC",
                "CLASSI_FIN",
                "CLASSIFICACAO_FINAL",
            ]
        ),
        "criterio": primeira_coluna_existente(
            df,
            [
                "CRITERIO",
                "CRITERIO_DESC",
                "CRIT_CONF",
            ]
        ),
    }


def filtrar_periodo(df, coluna_data):
    if not coluna_data or coluna_data not in df.columns:
        return df

    df = df.copy()
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")

    datas_validas = df[coluna_data].dropna()

    if datas_validas.empty:
        return df

    min_data = datas_validas.min().date()
    max_data = datas_validas.max().date()

    usar_tudo = st.sidebar.checkbox(
        "Usar todo o período",
        value=True,
        key="generico_usar_todo_periodo"
    )

    if usar_tudo:
        return df

    intervalo = st.sidebar.date_input(
        "Período",
        value=[min_data, max_data],
        min_value=min_data,
        max_value=max_data,
        key="generico_periodo"
    )

    if isinstance(intervalo, (list, tuple)) and len(intervalo) == 2:
        ini, fim = intervalo

        df = df[
            (df[coluna_data].dt.date >= ini)
            &
            (df[coluna_data].dt.date <= fim)
        ]

    return df


def aplicar_filtro_multiselect(df, coluna, label, key):
    if not coluna or coluna not in df.columns:
        return df

    opcoes = (
        preparar_texto(df[coluna])
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
        df = df[
            preparar_texto(df[coluna]).isin(selecionados)
        ]

    return df


def render_painel_generico_sinan(df, nome_agravo="Agravo SINAN"):
    st.markdown(
        f"""
        <div class="hz-hero">
            <span class="hz-kicker">Painel Universal SINAN</span>
            <h1>{nome_agravo}</h1>
            <p>
                Visão automática para bancos DBF do SINAN ainda sem painel específico.
                O painel identifica colunas-chave, gera indicadores, filtros, série temporal,
                perfil epidemiológico, qualidade dos dados e exportações.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df is None or df.empty:
        st.warning("Nenhum banco DBF carregado.")
        return

    df_publico = gerar_tabela_publica_generica(df.copy())
    colunas = detectar_colunas_principais(df_publico)

    st.sidebar.header("🔎 Filtros — Painel Universal")

    df_filtrado = df_publico.copy()
    df_filtrado = filtrar_periodo(df_filtrado, colunas["data"])

    df_filtrado = aplicar_filtro_multiselect(
        df_filtrado,
        colunas["sexo"],
        "Sexo",
        "gen_filtro_sexo"
    )

    df_filtrado = aplicar_filtro_multiselect(
        df_filtrado,
        colunas["idade"],
        "Faixa etária / idade",
        "gen_filtro_idade"
    )

    df_filtrado = aplicar_filtro_multiselect(
        df_filtrado,
        colunas["raca"],
        "Raça/cor",
        "gen_filtro_raca"
    )

    df_filtrado = aplicar_filtro_multiselect(
        df_filtrado,
        colunas["municipio"],
        "Município",
        "gen_filtro_municipio"
    )

    df_filtrado = aplicar_filtro_multiselect(
        df_filtrado,
        colunas["bairro"],
        "Bairro",
        "gen_filtro_bairro"
    )

    df_filtrado = aplicar_filtro_multiselect(
        df_filtrado,
        colunas["unidade"],
        "Unidade notificadora",
        "gen_filtro_unidade"
    )

    busca = st.sidebar.text_input(
        "Pesquisar termo no banco",
        key="gen_busca_geral"
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

    auditoria = gerar_auditoria_sinan(df_filtrado, agravo=nome_agravo)
    estrutura = montar_estrutura(df_filtrado)

    total = len(df_filtrado)
    colunas_qtd = len(df_filtrado.columns)
    score = auditoria.get("score_banco", 0)
    qualidade = auditoria.get("qualidade_banco", "—")

    duplicidades = auditoria.get("duplicidades", pd.DataFrame())
    duplicidades_qtd = len(duplicidades) if isinstance(duplicidades, pd.DataFrame) else 0

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric("Registros", total)
    k2.metric("Colunas", colunas_qtd)
    k3.metric("Score", f"{score}%")
    k4.metric("Qualidade", qualidade)
    k5.metric("Duplicidades", duplicidades_qtd)

    st.markdown("---")
    st.header("📈 Série temporal")

    if colunas["data"]:
        base = df_filtrado.copy()
        base[colunas["data"]] = pd.to_datetime(
            base[colunas["data"]],
            errors="coerce"
        )

        base = base.dropna(subset=[colunas["data"]])

        if not base.empty:
            base["MÊS"] = base[colunas["data"]].dt.to_period("M").astype(str)

            serie = (
                base
                .groupby("MÊS")
                .size()
                .reset_index(name="Registros")
                .sort_values("MÊS")
            )

            fig = px.line(
                serie,
                x="MÊS",
                y="Registros",
                markers=True,
                title="Registros por mês",
                color_discrete_sequence=[CORES["emerald"]]
            )

            fig.update_layout(
                template="horizonte_dark",
                height=500,
                xaxis_title="Mês",
                yaxis_title="Registros"
            )

            st.plotly_chart(fig, use_container_width=True)

            media = serie["Registros"].mean()
            ultimo = serie["Registros"].iloc[-1]

            if len(serie) >= 3 and ultimo > media * 1.5:
                st.warning(
                    "⚠️ O último período apresenta volume acima da média histórica filtrada."
                )
        else:
            st.info("Não há datas válidas para montar série temporal.")
    else:
        st.info("Não foi localizada uma coluna de data para série temporal.")

    st.markdown("---")
    st.header("👥 Perfil epidemiológico")

    p1, p2 = st.columns(2)

    with p1:
        if colunas["sexo"]:
            grafico_pizza(
                df_filtrado,
                colunas["sexo"],
                "Distribuição por sexo"
            )

        if colunas["raca"]:
            grafico_barras(
                df_filtrado,
                colunas["raca"],
                "Distribuição por raça/cor"
            )

    with p2:
        if colunas["idade"]:
            grafico_barras(
                df_filtrado,
                colunas["idade"],
                "Distribuição por faixa etária / idade"
            )

        if colunas["evolucao"]:
            grafico_barras(
                df_filtrado,
                colunas["evolucao"],
                "Classificação / evolução"
            )

    st.markdown("---")
    st.header("🗺️ Território e serviços notificadores")

    t1, t2 = st.columns(2)

    with t1:
        if colunas["municipio"]:
            grafico_barras(
                df_filtrado,
                colunas["municipio"],
                "Registros por município"
            )
        else:
            st.info("Coluna de município não localizada.")

    with t2:
        if colunas["bairro"]:
            grafico_barras(
                df_filtrado,
                colunas["bairro"],
                "Registros por bairro"
            )
        else:
            st.info("Coluna de bairro não localizada.")

    if colunas["unidade"]:
        grafico_barras(
            df_filtrado,
            colunas["unidade"],
            "Registros por unidade notificadora",
            limite=30
        )

    st.markdown("---")
    st.header("🧪 Qualidade dos dados")

    q1, q2 = st.columns(2)

    with q1:
        st.subheader("Campos com menor preenchimento")
        st.dataframe(
            estrutura.head(30),
            use_container_width=True,
            height=460
        )

    with q2:
        colunas_vazias = auditoria.get("colunas_vazias", pd.DataFrame())

        st.subheader("Colunas vazias / incompletas")

        if isinstance(colunas_vazias, pd.DataFrame) and not colunas_vazias.empty:
            st.dataframe(
                colunas_vazias.head(30),
                use_container_width=True,
                height=460
            )
        else:
            st.info("Não foram encontradas colunas vazias relevantes.")

    with st.expander("🔍 Ver inconsistências detalhadas"):
        st.markdown("### Duplicidades")
        st.dataframe(
            auditoria.get("duplicidades", pd.DataFrame()),
            use_container_width=True
        )

        st.markdown("### Sexo incompatível")
        st.dataframe(
            auditoria.get("sexo_incompativel", pd.DataFrame()),
            use_container_width=True
        )

        st.markdown("### Idade incompatível")
        st.dataframe(
            auditoria.get("idade_incompativel", pd.DataFrame()),
            use_container_width=True
        )

        st.markdown("### CID incompatível")
        st.dataframe(
            auditoria.get("cid_incompativel", pd.DataFrame()),
            use_container_width=True
        )

        st.markdown("### Município divergente")
        st.dataframe(
            auditoria.get("municipio_divergente", pd.DataFrame()),
            use_container_width=True
        )

    st.markdown("---")
    st.header("📋 Dados filtrados")

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=650
    )

    st.markdown("---")
    st.header("📥 Exportações")

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    with col_exp1:
        st.download_button(
            "Baixar dados filtrados",
            data=df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name="painel_universal_dados_filtrados.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_exp2:
        st.download_button(
            "Baixar qualidade dos campos",
            data=estrutura.to_csv(index=False).encode("utf-8"),
            file_name="painel_universal_qualidade_campos.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_exp3:
        resumo = pd.DataFrame([
            {
                "Agravo": nome_agravo,
                "Registros": total,
                "Colunas": colunas_qtd,
                "Score de qualidade": score,
                "Classificação": qualidade,
                "Duplicidades": duplicidades_qtd,
                "Coluna de data": colunas["data"] or "",
                "Coluna de município": colunas["municipio"] or "",
                "Coluna de unidade": colunas["unidade"] or "",
            }
        ])

        st.download_button(
            "Baixar resumo técnico",
            data=resumo.to_csv(index=False).encode("utf-8"),
            file_name="painel_universal_resumo_tecnico.csv",
            mime="text/csv",
            use_container_width=True
        )
