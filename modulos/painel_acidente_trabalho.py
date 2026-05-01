import streamlit as st
import pandas as pd
import plotly.express as px

from utils.tema import CORES, PALETA
from utils.gerador_ficha_pdf import gerar_ficha_pdf
from mappings.acidente_trabalho_grave import gerar_tabela_publica


CAMINHO_FICHA = "assets/DRT_Acidente_Trabalho_Grave.pdf"


def render_painel_acidente_trabalho(df):
    st.markdown("""
    <div class="mb-header">
        <h1>👷 Painel Analítico — Acidente de Trabalho Grave</h1>
        <p>
            Análise interativa dos registros decodificados, com filtros específicos,
            indicadores, gráficos, qualidade do preenchimento e geração da ficha em PDF.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Nenhum banco DBF carregado.")
        return

    df = df.copy()
    df_publico = gerar_tabela_publica(df)

    for col in ["DT_NOTIFIC", "DT_ACID", "DT_NASC", "DT_OBITO"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        if col in df_publico.columns:
            df_publico[col] = pd.to_datetime(df_publico[col], errors="coerce")

    st.header("🔎 Localizar registro para gerar ficha")

    tipo_busca = st.selectbox(
        "Pesquisar por",
        ["Número da notificação", "Nome do paciente", "Nome da mãe"]
    )

    termo_busca = st.text_input("Digite o termo de busca", key="busca_ficha_acidente")

    resultado_ficha = pd.DataFrame()

    if termo_busca:
        if tipo_busca == "Número da notificação" and "NU_NOTIFIC" in df.columns:
            resultado_ficha = df[df["NU_NOTIFIC"].astype(str).str.contains(termo_busca, case=False, na=False)]

        elif tipo_busca == "Nome do paciente" and "NM_PACIENT" in df.columns:
            resultado_ficha = df[df["NM_PACIENT"].astype(str).str.contains(termo_busca, case=False, na=False)]

        elif tipo_busca == "Nome da mãe" and "NM_MAE_PAC" in df.columns:
            resultado_ficha = df[df["NM_MAE_PAC"].astype(str).str.contains(termo_busca, case=False, na=False)]

    if termo_busca and resultado_ficha.empty:
        st.warning("Nenhum registro encontrado para a busca informada.")

    if not resultado_ficha.empty:
        st.success(f"{len(resultado_ficha)} registro(s) encontrado(s).")

        resultado_ficha = resultado_ficha.copy()

        resultado_ficha["OPCAO_BUSCA"] = (
            resultado_ficha.get("NU_NOTIFIC", "").astype(str)
            + " | "
            + resultado_ficha.get("NM_PACIENT", "").astype(str)
            + " | "
            + resultado_ficha.get("NM_MAE_PAC", "").astype(str)
        )

        escolha = st.selectbox(
            "Selecione o registro para geração da ficha",
            resultado_ficha["OPCAO_BUSCA"].tolist()
        )

        registro_pdf = resultado_ficha[resultado_ficha["OPCAO_BUSCA"] == escolha].iloc[0]

        campos_preview = [
            "NU_NOTIFIC",
            "DT_NOTIFIC",
            "DT_ACID",
            "NM_PACIENT",
            "NM_MAE_PAC",
            "CS_SEXO_DESC",
            "CS_RACA_DESC",
            "IDADE_CALCULADA",
            "FAIXA_ETARIA_CALCULADA",
            "OCUPACAO_DESC",
            "SIT_TRAB_DESC",
            "LOCAL_ACID_DESC",
            "TIPO_ACID_DESC",
            "EVOLUCAO_DESC",
            "CAT_DESC"
        ]

        preview = {
            campo: registro_pdf[campo]
            for campo in campos_preview
            if campo in registro_pdf.index
        }

        st.dataframe(pd.DataFrame(preview.items(), columns=["Campo", "Valor"]), use_container_width=True)

        try:
            pdf_bytes = gerar_ficha_pdf(registro_pdf, CAMINHO_FICHA)

            st.download_button(
                "📥 Baixar ficha preenchida em PDF",
                data=pdf_bytes,
                file_name=f"ficha_acidente_trabalho_{registro_pdf.get('NU_NOTIFIC', 'registro')}.pdf",
                mime="application/pdf"
            )

        except FileNotFoundError:
            st.error("Ficha PDF base não encontrada em assets/DRT_Acidente_Trabalho_Grave.pdf")

        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

    st.sidebar.header("🔎 Filtros — Acidente de Trabalho")

    df_filtrado = df_publico.copy()

    usar_periodo_total = st.sidebar.checkbox(
        "Selecionar todo o período disponível",
        value=True,
        key="periodo_acidente"
    )

    if "DT_NOTIFIC" in df_filtrado.columns:
        df_filtrado["DT_NOTIFIC"] = pd.to_datetime(df_filtrado["DT_NOTIFIC"], errors="coerce")

        min_d = df_filtrado["DT_NOTIFIC"].min()
        max_d = df_filtrado["DT_NOTIFIC"].max()

        if pd.notna(min_d) and pd.notna(max_d) and not usar_periodo_total:
            data_ini, data_fim = st.sidebar.date_input(
                "Período da notificação",
                value=[min_d.date(), max_d.date()],
                min_value=min_d.date(),
                max_value=max_d.date(),
                key="datas_acidente"
            )

            df_filtrado = df_filtrado[
                (df_filtrado["DT_NOTIFIC"].dt.date >= data_ini) &
                (df_filtrado["DT_NOTIFIC"].dt.date <= data_fim)
            ]

    def preparar_opcoes(serie):
        serie = serie.fillna("Ignorado").astype(str).str.strip()
        serie = serie.replace("", "Ignorado")
        serie = serie.replace(["nan", "None", "NaT", "NULL", "null"], "Ignorado")
        return sorted(serie.unique())

    def filtro(label, coluna):
        nonlocal df_filtrado

        if coluna in df_filtrado.columns:
            df_filtrado[coluna] = (
                df_filtrado[coluna]
                .fillna("Ignorado")
                .astype(str)
                .str.strip()
                .replace("", "Ignorado")
            )

            opcoes = preparar_opcoes(df_filtrado[coluna])
            selecionados = st.sidebar.multiselect(label, opcoes, key=f"filtro_{coluna}")

            if selecionados:
                df_filtrado = df_filtrado[df_filtrado[coluna].isin(selecionados)]

    filtro("Sexo", "CS_SEXO_DESC")
    filtro("Raça/Cor", "CS_RACA_DESC")
    filtro("Gestante", "CS_GESTANT_DESC")
    filtro("Situação no Mercado de Trabalho", "SIT_TRAB_DESC")
    filtro("Local do Acidente", "LOCAL_ACID_DESC")
    filtro("Tipo de Acidente", "TIPO_ACID_DESC")
    filtro("Regime de Tratamento", "REGIME_DESC")
    filtro("Evolução", "EVOLUCAO_DESC")
    filtro("CAT", "CAT_DESC")
    filtro("Ocupação", "OCUPACAO_DESC")
    filtro("Faixa Etária", "FAIXA_ETARIA_CALCULADA")

    busca_geral = st.text_input("🔍 Pesquisar qualquer termo no banco filtrado", key="busca_geral_acidente")

    if busca_geral:
        mask = df_filtrado.astype(str).apply(
            lambda col: col.str.contains(busca_geral, case=False, na=False)
        ).any(axis=1)
        df_filtrado = df_filtrado[mask]

    if df_filtrado.empty:
        st.warning("Nenhum registro encontrado com os filtros aplicados.")
        return

    st.header("📊 Indicadores Principais")

    total = len(df_filtrado)

    obitos = 0
    if "EVOLUCAO_DESC" in df_filtrado.columns:
        obitos = df_filtrado["EVOLUCAO_DESC"].astype(str).str.contains("Óbito|Obito", case=False, na=False).sum()

    cat_emitida = 0
    if "CAT_DESC" in df_filtrado.columns:
        cat_emitida = (df_filtrado["CAT_DESC"].astype(str).str.upper().str.strip() == "SIM").sum()

    ocupacao_top = "—"
    if "OCUPACAO_DESC" in df_filtrado.columns and not df_filtrado["OCUPACAO_DESC"].dropna().empty:
        ocupacao_top = df_filtrado["OCUPACAO_DESC"].astype(str).value_counts().idxmax()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", total)
    c2.metric("Óbitos", int(obitos))
    c3.metric("CAT emitida", int(cat_emitida))
    c4.metric("Ocupação mais frequente", ocupacao_top)

    st.header("📈 Visualizações")

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

    if "EVOLUCAO_DESC" in df_filtrado.columns:
        evolucao = df_filtrado["EVOLUCAO_DESC"].value_counts().reset_index()
        evolucao.columns = ["Evolução", "Quantidade"]

        fig = px.bar(
            evolucao,
            x="Evolução",
            y="Quantidade",
            title="Evolução do Caso",
            color_discrete_sequence=[CORES["azul"]]
        )
        col2.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    if "SIT_TRAB_DESC" in df_filtrado.columns:
        sit = df_filtrado["SIT_TRAB_DESC"].value_counts().reset_index()
        sit.columns = ["Situação", "Quantidade"]

        fig = px.bar(
            sit,
            x="Situação",
            y="Quantidade",
            title="Situação no Mercado de Trabalho",
            color_discrete_sequence=[CORES["verde"]]
        )
        col3.plotly_chart(fig, use_container_width=True)

    if "LOCAL_ACID_DESC" in df_filtrado.columns:
        local = df_filtrado["LOCAL_ACID_DESC"].value_counts().reset_index()
        local.columns = ["Local", "Quantidade"]

        fig = px.bar(
            local,
            x="Local",
            y="Quantidade",
            title="Local onde ocorreu o acidente",
            color_discrete_sequence=[CORES["laranja"]]
        )
        col4.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)

    if "FAIXA_ETARIA_CALCULADA" in df_filtrado.columns:
        ordem_faixas = [
            "0 a 9 anos",
            "10 a 19 anos",
            "20 a 29 anos",
            "30 a 39 anos",
            "40 a 49 anos",
            "50 a 59 anos",
            "60 anos ou mais",
            "Ignorado"
        ]

        idade = df_filtrado["FAIXA_ETARIA_CALCULADA"].value_counts().reset_index()
        idade.columns = ["Faixa etária", "Quantidade"]
        idade["Faixa etária"] = pd.Categorical(
            idade["Faixa etária"],
            categories=ordem_faixas,
            ordered=True
        )
        idade = idade.sort_values("Faixa etária")

        fig = px.bar(
            idade,
            x="Faixa etária",
            y="Quantidade",
            title="Distribuição por Faixa Etária",
            color_discrete_sequence=[CORES["amarelo"]]
        )
        col5.plotly_chart(fig, use_container_width=True)

    if "OCUPACAO_DESC" in df_filtrado.columns:
        ocup = df_filtrado["OCUPACAO_DESC"].value_counts().reset_index().head(20)
        ocup.columns = ["Ocupação", "Quantidade"]

        fig = px.bar(
            ocup,
            x="Quantidade",
            y="Ocupação",
            orientation="h",
            title="Top 20 Ocupações",
            color_discrete_sequence=[CORES["azul"]]
        )
        col6.plotly_chart(fig, use_container_width=True)

    if "DT_NOTIFIC" in df_filtrado.columns:
        base_serie = df_filtrado.dropna(subset=["DT_NOTIFIC"]).copy()
        base_serie["MES"] = base_serie["DT_NOTIFIC"].dt.to_period("M").astype(str)

        serie = (
            base_serie
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
                title="Notificações por mês",
                color_discrete_sequence=[CORES["azul"]]
            )
            st.plotly_chart(fig, use_container_width=True)

    st.header("📋 Dados Decodificados")

    st.dataframe(df_filtrado, use_container_width=True)

    st.download_button(
        "📥 Baixar dados filtrados em CSV",
        data=df_filtrado.to_csv(index=False).encode("utf-8"),
        file_name="acidente_trabalho_grave_decodificado.csv",
        mime="text/csv"
    )
