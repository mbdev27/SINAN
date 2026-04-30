from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter


def formatar_data(valor):
    """
    Converte datas para dd/mm/aaaa.
    """
    if valor is None:
        return ""

    try:
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y")
    except Exception:
        pass

    texto = str(valor)

    if texto in ["NaT", "nan", "None"]:
        return ""

    return texto


def valor_seguro(registro, coluna):
    """
    Busca valor em uma linha do DataFrame.
    """
    if coluna not in registro.index:
        return ""

    valor = registro[coluna]

    if str(valor) in ["nan", "None", "NaT"]:
        return ""

    return str(valor)


def criar_overlay_acidente_trabalho(registro):
    """
    Cria uma camada PDF transparente com os dados posicionados sobre a ficha.

    Observação:
    As coordenadas abaixo são aproximações iniciais.
    Elas serão refinadas depois com teste visual da ficha renderizada.
    """
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    c.setFont("Helvetica", 7)

    # ======================================================
    # PÁGINA 1 - CAMPOS PRINCIPAIS
    # ======================================================

    # Número da notificação
    c.drawString(470, 790, valor_seguro(registro, "NU_NOTIFIC"))

    # Campo 3 - Data da Notificação
    c.drawString(130, 702, formatar_data(registro.get("DT_NOTIFIC", "")))

    # Campo 7 - Data do Acidente
    c.drawString(465, 702, formatar_data(registro.get("DT_ACID", "")))

    # Município de Notificação
    c.drawString(260, 682, valor_seguro(registro, "ID_MUNICIP"))

    # Unidade notificadora
    c.drawString(105, 650, valor_seguro(registro, "ID_UNIDADE"))

    # Nome do paciente
    c.drawString(105, 613, valor_seguro(registro, "NM_PACIENT"))

    # Data de nascimento
    c.drawString(390, 613, formatar_data(registro.get("DT_NASC", "")))

    # Sexo
    c.drawString(525, 613, valor_seguro(registro, "CS_SEXO"))

    # Gestante
    c.drawString(105, 590, valor_seguro(registro, "CS_GESTANT"))

    # Raça/cor
    c.drawString(190, 590, valor_seguro(registro, "CS_RACA"))

    # Escolaridade
    c.drawString(280, 590, valor_seguro(registro, "CS_ESCOL_N"))

    # Nome da mãe
    c.drawString(105, 565, valor_seguro(registro, "NM_MAE_PAC"))

    # Município de residência
    c.drawString(110, 520, valor_seguro(registro, "ID_MN_RESI"))

    # Bairro
    c.drawString(105, 475, valor_seguro(registro, "NM_BAIRRO"))

    # Logradouro
    c.drawString(105, 455, valor_seguro(registro, "NM_LOGRADO"))

    # Número
    c.drawString(390, 455, valor_seguro(registro, "NU_NUMERO"))

    # CEP
    c.drawString(470, 455, valor_seguro(registro, "NU_CEP"))

    # Ocupação - Campo 31
    c.drawString(105, 390, valor_seguro(registro, "ID_OCUPA_N"))

    # Situação no Mercado - Campo 32
    c.drawString(105, 365, valor_seguro(registro, "SIT_TRAB"))

    # Tempo de trabalho na ocupação - Campo 33
    c.drawString(430, 365, valor_seguro(registro, "TEMP_TRAB"))

    # Local onde ocorreu o acidente - Campo 34
    c.drawString(105, 340, valor_seguro(registro, "LOCAL_ACID"))

    # CNPJ/CPF Empresa - Campo 35
    c.drawString(105, 295, valor_seguro(registro, "CNPJ_EMP"))

    # Nome da empresa - Campo 36
    c.drawString(270, 295, valor_seguro(registro, "NM_EMPRESA"))

    # CNAE - Campo 37
    c.drawString(105, 270, valor_seguro(registro, "CNAE"))

    c.showPage()

    # ======================================================
    # PÁGINA 2 - DADOS DO ACIDENTE E CONCLUSÃO
    # ======================================================

    c.setFont("Helvetica", 7)

    # Empresa terceirizada - Campo 46
    c.drawString(105, 770, valor_seguro(registro, "EMP_TERCE"))

    # CNAE empresa principal - Campo 47
    c.drawString(105, 748, valor_seguro(registro, "CNAE_PRINC"))

    # CNPJ empresa principal - Campo 48
    c.drawString(105, 725, valor_seguro(registro, "CNPJ_PRINC"))

    # Razão social - Campo 49
    c.drawString(270, 725, valor_seguro(registro, "RAZAO_SOC"))

    # Hora do acidente - Campo 50
    c.drawString(105, 690, valor_seguro(registro, "HORA_ACID"))

    # Horas após início da jornada - Campo 51
    c.drawString(260, 690, valor_seguro(registro, "HORAS_JOR"))

    # UF ocorrência - Campo 52
    c.drawString(105, 665, valor_seguro(registro, "UF_ACID"))

    # Município ocorrência - Campo 53
    c.drawString(160, 665, valor_seguro(registro, "MUN_ACID"))

    # CID causa do acidente - Campo 54
    c.drawString(105, 640, valor_seguro(registro, "CID_CAUSA"))

    # Tipo de acidente - Campo 55
    c.drawString(105, 615, valor_seguro(registro, "TIPO_ACID"))

    # Outros trabalhadores atingidos - Campo 56
    c.drawString(260, 615, valor_seguro(registro, "MAIS_TRAB"))

    # Quantos - Campo 57
    c.drawString(430, 615, valor_seguro(registro, "QTD_TRAB"))

    # Atendimento médico - Campo 58
    c.drawString(105, 585, valor_seguro(registro, "ATENDE_MED"))

    # Data do atendimento - Campo 59
    c.drawString(260, 585, formatar_data(registro.get("DT_ATEND", "")))

    # UF atendimento - Campo 60
    c.drawString(105, 560, valor_seguro(registro, "UF_ATEND"))

    # Município atendimento - Campo 61
    c.drawString(160, 560, valor_seguro(registro, "MUN_ATEND"))

    # Unidade de atendimento - Campo 62
    c.drawString(105, 535, valor_seguro(registro, "UNID_ATEND"))

    # Partes do corpo - Campo 63
    partes = " / ".join([
        valor_seguro(registro, "PART_CORP1"),
        valor_seguro(registro, "PART_CORP2"),
        valor_seguro(registro, "PART_CORP3")
    ]).strip(" / ")

    c.drawString(105, 500, partes)

    # CID lesão - Campo 64
    c.drawString(105, 465, valor_seguro(registro, "CID_LESAO"))

    # Regime - Campo 65
    c.drawString(260, 465, valor_seguro(registro, "REGIME"))

    # Evolução - Campo 66
    c.drawString(105, 430, valor_seguro(registro, "EVOLUCAO"))

    # Data do óbito - Campo 67
    c.drawString(300, 430, formatar_data(registro.get("DT_OBITO", "")))

    # CAT - Campo 68
    c.drawString(105, 395, valor_seguro(registro, "CAT"))

    # Observações
    obs = valor_seguro(registro, "DS_OBS")
    c.drawString(105, 330, obs[:120])
    c.drawString(105, 318, obs[120:240])

    c.save()

    packet.seek(0)
    return packet


def gerar_ficha_pdf(registro, caminho_pdf_base):
    """
    Mescla a ficha original com a camada preenchida.
    """
    overlay_pdf = criar_overlay_acidente_trabalho(registro)

    base = PdfReader(caminho_pdf_base)
    overlay = PdfReader(overlay_pdf)
    writer = PdfWriter()

    for i, pagina_base in enumerate(base.pages):
        if i < len(overlay.pages):
            pagina_base.merge_page(overlay.pages[i])
        writer.add_page(pagina_base)

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    return output.getvalue()
