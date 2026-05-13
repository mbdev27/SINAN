from io import BytesIO
from pathlib import Path
from datetime import datetime

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)


CORES_PDF = {
    "navy": "#0A2647",
    "emerald": "#00ED64",
    "titanium": "#E1E8ED",
    "midnight": "#101820",
    "white": "#F8FAFC",
    "muted": "#64748B",
    "danger": "#DC2626",
    "warning": "#F59E0B",
}


def limpar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor)

    substituicoes = {
        "🟢": "",
        "🟡": "",
        "🟠": "",
        "🔴": "",
        "⚪": "",
        "✅": "Sim",
        "❌": "Não",
        "🔒": "Sim",
        "🔓": "Não",
        "⚠️": "Atenção:",
    }

    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)

    return texto.strip()


def estilo_titulo():
    return ParagraphStyle(
        "TituloHorizonte",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        textColor=colors.HexColor(CORES_PDF["navy"]),
        spaceAfter=14,
    )


def estilo_subtitulo():
    return ParagraphStyle(
        "SubtituloHorizonte",
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor(CORES_PDF["muted"]),
        spaceAfter=18,
    )


def estilo_secao():
    return ParagraphStyle(
        "SecaoHorizonte",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=20,
        alignment=TA_LEFT,
        textColor=colors.HexColor(CORES_PDF["navy"]),
        spaceBefore=14,
        spaceAfter=10,
    )


def estilo_normal():
    return ParagraphStyle(
        "NormalHorizonte",
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
        textColor=colors.HexColor(CORES_PDF["midnight"]),
        spaceAfter=8,
    )


def estilo_destaque():
    return ParagraphStyle(
        "DestaqueHorizonte",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.HexColor(CORES_PDF["navy"]),
        spaceAfter=10,
    )


def adicionar_logo(elementos):
    caminhos = [
        Path("assets/horizonte_logo.png"),
        Path("horizonte_logo.png"),
        Path("assets/logo.png"),
    ]

    for caminho in caminhos:
        if caminho.exists():
            try:
                logo = Image(str(caminho), width=5.2 * cm, height=2.2 * cm)
                logo.hAlign = "CENTER"
                elementos.append(logo)
                elementos.append(Spacer(1, 0.4 * cm))
                return
            except Exception:
                return


def rodape(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor(CORES_PDF["muted"]))

    texto = f"Horizonte Health Intelligence - Relatório Técnico - Página {doc.page}"

    canvas.drawCentredString(
        A4[0] / 2,
        1.0 * cm,
        texto,
    )

    canvas.restoreState()


def limitar_dataframe(df, linhas=20, colunas=6):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    df_temp = df.copy()
    df_temp = df_temp.iloc[:linhas, :colunas]

    for coluna in df_temp.columns:
        df_temp[coluna] = df_temp[coluna].apply(limpar_texto)

    return df_temp


def dataframe_para_tabela(df, linhas=20, colunas=6, largura_total=17 * cm):
    df = limitar_dataframe(df, linhas=linhas, colunas=colunas)

    if df.empty:
        return Paragraph("Sem dados disponíveis para esta seção.", estilo_normal())

    dados = [list(df.columns)] + df.astype(str).values.tolist()

    qtd_colunas = len(dados[0])
    largura_coluna = largura_total / max(qtd_colunas, 1)

    tabela = Table(
        dados,
        colWidths=[largura_coluna] * qtd_colunas,
        repeatRows=1,
    )

    tabela.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(CORES_PDF["navy"])),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),

            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor(CORES_PDF["midnight"])),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D6DEE6")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    return tabela


def tabela_kpis(kpis):
    dados = []

    linha_rotulos = []
    linha_valores = []

    for item in kpis:
        linha_rotulos.append(limpar_texto(item.get("label", "")))
        linha_valores.append(limpar_texto(item.get("value", "")))

    dados.append(linha_rotulos)
    dados.append(linha_valores)

    tabela = Table(
        dados,
        colWidths=[4.2 * cm] * len(kpis),
    )

    tabela.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(CORES_PDF["navy"])),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
            ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor(CORES_PDF["midnight"])),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 1), (-1, 1), 12),

            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D6DEE6")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(CORES_PDF["emerald"])),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    return tabela


def tabela_alertas_resumo(alertas_df):
    if alertas_df is None or not isinstance(alertas_df, pd.DataFrame) or alertas_df.empty:
        return Paragraph("Nenhum alerta automático informado.", estilo_normal())

    colunas = [
        c for c in ["Nível", "Tipo", "Título", "Recomendação"]
        if c in alertas_df.columns
    ]

    if not colunas:
        return Paragraph("Nenhum alerta automático informado.", estilo_normal())

    df = alertas_df[colunas].head(8).copy()

    return dataframe_para_tabela(
        df,
        linhas=8,
        colunas=len(colunas),
        largura_total=17 * cm,
    )


def gerar_resumo_executivo_pdf(
    nome_agravo,
    usuario,
    municipio,
    total_registros,
    total_colunas,
    score_qualidade,
    classificacao_qualidade,
    duplicidades,
    coluna_data="",
    coluna_municipio="",
    coluna_unidade="",
    alertas_df=None,
    observacoes=None,
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.6 * cm,
        title=f"Resumo Executivo - {nome_agravo}",
        author="Horizonte Health Intelligence",
    )

    elementos = []

    adicionar_logo(elementos)

    elementos.append(
        Paragraph(
            "Resumo Executivo",
            estilo_titulo()
        )
    )

    elementos.append(
        Paragraph(
            f"{limpar_texto(nome_agravo)}",
            estilo_subtitulo()
        )
    )

    elementos.append(
        Paragraph(
            f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}",
            estilo_normal()
        )
    )

    elementos.append(
        Paragraph(
            f"Responsável: <b>{limpar_texto(usuario)}</b>",
            estilo_normal()
        )
    )

    elementos.append(
        Paragraph(
            f"Município/Instituição: <b>{limpar_texto(municipio)}</b>",
            estilo_normal()
        )
    )

    elementos.append(Spacer(1, 0.35 * cm))

    kpis = [
        {"label": "Registros", "value": total_registros},
        {"label": "Colunas", "value": total_colunas},
        {"label": "Score", "value": f"{score_qualidade}%"},
        {"label": "Qualidade", "value": classificacao_qualidade},
    ]

    elementos.append(tabela_kpis(kpis))
    elementos.append(Spacer(1, 0.45 * cm))

    elementos.append(Paragraph("Síntese executiva", estilo_secao()))

    texto_sintese = (
        f"O banco analisado corresponde ao agravo <b>{limpar_texto(nome_agravo)}</b>. "
        f"Foram identificados <b>{total_registros}</b> registros distribuídos em "
        f"<b>{total_colunas}</b> colunas. O score de qualidade foi de "
        f"<b>{score_qualidade}%</b>, classificado como "
        f"<b>{limpar_texto(classificacao_qualidade)}</b>. "
        f"Foram identificadas <b>{duplicidades}</b> duplicidades prováveis no recorte avaliado."
    )

    elementos.append(Paragraph(texto_sintese, estilo_normal()))

    elementos.append(Paragraph("Colunas estratégicas identificadas", estilo_secao()))

    dados_colunas = pd.DataFrame([
        {
            "Elemento": "Data principal",
            "Coluna": coluna_data or "Não localizada",
        },
        {
            "Elemento": "Município",
            "Coluna": coluna_municipio or "Não localizada",
        },
        {
            "Elemento": "Unidade notificadora",
            "Coluna": coluna_unidade or "Não localizada",
        },
    ])

    elementos.append(dataframe_para_tabela(dados_colunas, linhas=3, colunas=2))
    elementos.append(Spacer(1, 0.35 * cm))

    elementos.append(Paragraph("Principais alertas inteligentes", estilo_secao()))
    elementos.append(tabela_alertas_resumo(alertas_df))
    elementos.append(Spacer(1, 0.35 * cm))

    elementos.append(Paragraph("Recomendações automáticas", estilo_secao()))

    if observacoes:
        for item in observacoes[:8]:
            elementos.append(
                Paragraph(
                    f"• {limpar_texto(item)}",
                    estilo_normal()
                )
            )
    else:
        elementos.append(
            Paragraph(
                "Manter rotina de monitoramento, auditoria e qualificação periódica dos bancos.",
                estilo_normal()
            )
        )

    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(Paragraph("Uso recomendado", estilo_secao()))

    elementos.append(
        Paragraph(
            "Este resumo foi elaborado para apoio rápido em reuniões técnicas, "
            "discussões de gestão, pactuações internas e priorização de ações. "
            "Para análise detalhada, recomenda-se utilizar também o Relatório Técnico completo.",
            estilo_normal()
        )
    )

    doc.build(
        elementos,
        onFirstPage=rodape,
        onLaterPages=rodape,
    )

    buffer.seek(0)

    return buffer.getvalue()


def gerar_relatorio_tecnico_pdf(
    nome_agravo,
    usuario,
    municipio,
    total_registros,
    total_colunas,
    score_qualidade,
    classificacao_qualidade,
    duplicidades,
    coluna_data="",
    coluna_municipio="",
    coluna_unidade="",
    estrutura_campos=None,
    colunas_vazias=None,
    inconsistencias=None,
    resumo_extra=None,
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.6 * cm,
        title=f"Relatório Técnico - {nome_agravo}",
        author="Horizonte Health Intelligence",
    )

    elementos = []

    adicionar_logo(elementos)

    elementos.append(
        Paragraph(
            "Relatório Técnico Institucional",
            estilo_titulo()
        )
    )

    elementos.append(
        Paragraph(
            f"{limpar_texto(nome_agravo)}",
            estilo_subtitulo()
        )
    )

    elementos.append(
        Paragraph(
            f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}",
            estilo_normal()
        )
    )

    elementos.append(
        Paragraph(
            f"Usuário responsável: <b>{limpar_texto(usuario)}</b>",
            estilo_normal()
        )
    )

    elementos.append(
        Paragraph(
            f"Município/Instituição: <b>{limpar_texto(municipio)}</b>",
            estilo_normal()
        )
    )

    elementos.append(Spacer(1, 0.4 * cm))

    kpis = [
        {"label": "Registros", "value": total_registros},
        {"label": "Colunas", "value": total_colunas},
        {"label": "Score", "value": f"{score_qualidade}%"},
        {"label": "Qualidade", "value": classificacao_qualidade},
    ]

    elementos.append(tabela_kpis(kpis))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph("1. Síntese técnica", estilo_secao()))

    texto_sintese = (
        f"O banco analisado corresponde ao agravo {limpar_texto(nome_agravo)}. "
        f"Foram identificados {total_registros} registros e {total_colunas} colunas. "
        f"O score geral de qualidade foi de {score_qualidade}%, classificado como "
        f"{limpar_texto(classificacao_qualidade)}. "
        f"Foram detectadas {duplicidades} duplicidades prováveis no recorte analisado."
    )

    elementos.append(Paragraph(texto_sintese, estilo_normal()))

    elementos.append(Paragraph("2. Colunas estruturantes identificadas", estilo_secao()))

    dados_colunas = pd.DataFrame([
        {
            "Elemento": "Data principal",
            "Coluna identificada": coluna_data or "Não localizada",
        },
        {
            "Elemento": "Município",
            "Coluna identificada": coluna_municipio or "Não localizada",
        },
        {
            "Elemento": "Unidade notificadora",
            "Coluna identificada": coluna_unidade or "Não localizada",
        },
    ])

    elementos.append(dataframe_para_tabela(dados_colunas, linhas=3, colunas=2))
    elementos.append(Spacer(1, 0.3 * cm))

    if resumo_extra:
        elementos.append(Paragraph("3. Observações automáticas", estilo_secao()))

        for item in resumo_extra:
            elementos.append(
                Paragraph(
                    f"• {limpar_texto(item)}",
                    estilo_normal()
                )
            )

    elementos.append(PageBreak())

    elementos.append(Paragraph("4. Qualidade dos campos", estilo_secao()))

    if estrutura_campos is not None and isinstance(estrutura_campos, pd.DataFrame):
        elementos.append(dataframe_para_tabela(estrutura_campos, linhas=25, colunas=5))
    else:
        elementos.append(Paragraph("Sem estrutura de campos disponível.", estilo_normal()))

    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(Paragraph("5. Colunas com maior incompletude", estilo_secao()))

    if colunas_vazias is not None and isinstance(colunas_vazias, pd.DataFrame):
        elementos.append(dataframe_para_tabela(colunas_vazias, linhas=25, colunas=4))
    else:
        elementos.append(Paragraph("Sem tabela de colunas vazias disponível.", estilo_normal()))

    elementos.append(PageBreak())

    elementos.append(Paragraph("6. Inconsistências e alertas", estilo_secao()))

    if inconsistencias:
        for titulo, tabela in inconsistencias.items():
            elementos.append(Paragraph(limpar_texto(titulo), estilo_secao()))

            if isinstance(tabela, pd.DataFrame) and not tabela.empty:
                elementos.append(dataframe_para_tabela(tabela, linhas=12, colunas=6))
            else:
                elementos.append(Paragraph("Nenhum registro encontrado.", estilo_normal()))

            elementos.append(Spacer(1, 0.3 * cm))
    else:
        elementos.append(Paragraph("Não foram informadas inconsistências detalhadas.", estilo_normal()))

    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph("7. Considerações finais", estilo_secao()))

    elementos.append(
        Paragraph(
            "Este relatório foi gerado automaticamente pela plataforma Horizonte Health Intelligence. "
            "Os resultados devem ser utilizados como apoio técnico para qualificação da informação, "
            "monitoramento epidemiológico, planejamento de ações e discussão institucional.",
            estilo_normal()
        )
    )

    doc.build(
        elementos,
        onFirstPage=rodape,
        onLaterPages=rodape,
    )

    buffer.seek(0)

    return buffer.getvalue()
