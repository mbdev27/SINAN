from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def valor_seguro(registro, coluna):
    """
    Retorna valor seguro do registro.
    """
    if coluna not in registro.index:
        return ""

    valor = registro[coluna]

    if str(valor) in ["nan", "None", "NaT", "Ignorado"]:
        return ""

    return str(valor)


def formatar_data(valor):
    """
    Formata datas para dd/mm/aaaa.
    """
    if valor is None:
        return ""

    try:
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y")
    except Exception:
        pass

    texto = str(valor)

    if texto in ["NaT", "nan", "None", "Ignorado"]:
        return ""

    return texto


def escrever(c, x, y, texto, tamanho=6.2, max_chars=None):
    """
    Escreve texto simples no PDF.
    """
    if texto is None:
        texto = ""

    texto = str(texto)

    if max_chars:
        texto = texto[:max_chars]

    c.setFont("Helvetica", tamanho)
    c.drawString(x, y, texto)


def escrever_multilinha(c, x, y, texto, largura_chars=95, tamanho=6.2, entrelinha=9, max_linhas=5):
    """
    Escreve texto longo em múltiplas linhas.
    """
    if texto is None:
        return

    texto = str(texto).replace("\n", " ").strip()

    if not texto:
        return

    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        tentativa = f"{linha_atual} {palavra}".strip()

        if len(tentativa) <= largura_chars:
            linha_atual = tentativa
        else:
            linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    linhas = linhas[:max_linhas]

    c.setFont("Helvetica", tamanho)

    for i, linha in enumerate(linhas):
        c.drawString(x, y - (i * entrelinha), linha)


# ============================================================
# OVERLAY DA FICHA
# ============================================================

def criar_overlay_acidente_trabalho(registro):
    """
    Cria camada de preenchimento para a ficha de Acidente de Trabalho Grave.

    As coordenadas foram ajustadas a partir do PDF gerado anteriormente,
    mas ainda podem receber refinamento fino após novo teste visual.
    """
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    # A4 reportlab: largura 595, altura 842

    # ========================================================
    # PÁGINA 1
    # ========================================================

    # Nº notificação
    escrever(c, 485, 794, valor_seguro(registro, "NU_NOTIFIC"), tamanho=7)

    # Campo 1 - Tipo notificação
    escrever(c, 65, 667, valor_seguro(registro, "TP_NOT"), tamanho=6)

    # Campo 2 - Agravo
    escrever(c, 92, 642, valor_seguro(registro, "ID_AGRAVO"), tamanho=6)

    # Campo 3 - Data notificação
    escrever(c, 250, 667, formatar_data(registro.get("DT_NOTIFIC", "")), tamanho=6)

    # Campo 4 - UF
    escrever(c, 397, 667, valor_seguro(registro, "SG_UF_NOT"), tamanho=6)

    # Campo 5 - Município notificação
    escrever(c, 435, 667, valor_seguro(registro, "ID_MUNICIP"), tamanho=6)

    # Campo 6 - Unidade notificadora
    escrever(c, 90, 622, valor_seguro(registro, "ID_UNIDADE"), tamanho=6)

    # Campo 7 - Data do acidente
    escrever(c, 360, 642, formatar_data(registro.get("DT_ACID", "")), tamanho=6)

    # Campo 8 - Nome do paciente
    escrever(c, 88, 598, valor_seguro(registro, "NM_PACIENT"), tamanho=6, max_chars=42)

    # Campo 9 - Data nascimento
    escrever(c, 382, 598, formatar_data(registro.get("DT_NASC", "")), tamanho=6)

    # Campo 10 - Idade
    escrever(c, 492, 598, valor_seguro(registro, "NU_IDADE_N"), tamanho=6)

    # Campo 11 - Sexo
    escrever(c, 545, 598, valor_seguro(registro, "CS_SEXO"), tamanho=6)

    # Campo 12 - Gestante
    escrever(c, 85, 573, valor_seguro(registro, "CS_GESTANT"), tamanho=6)

    # Campo 13 - Raça/cor
    escrever(c, 158, 573, valor_seguro(registro, "CS_RACA"), tamanho=6)

    # Campo 14 - Escolaridade
    escrever(c, 245, 573, valor_seguro(registro, "CS_ESCOL_N"), tamanho=6)

    # Campo 15 - CNS
    escrever(c, 430, 573, valor_seguro(registro, "ID_CNS_SUS"), tamanho=6)

    # Campo 16 - Nome da mãe
    escrever(c, 90, 548, valor_seguro(registro, "NM_MAE_PAC"), tamanho=6, max_chars=55)

    # Campo 17 - UF residência
    escrever(c, 70, 500, valor_seguro(registro, "SG_UF"), tamanho=6)

    # Campo 18 - Município residência
    escrever(c, 115, 500, valor_seguro(registro, "ID_MN_RESI"), tamanho=6)

    # Campo 19 - Distrito
    escrever(c, 315, 500, valor_seguro(registro, "ID_RG_RESI"), tamanho=6)

    # Campo 20 - Bairro
    escrever(c, 90, 475, valor_seguro(registro, "NM_BAIRRO"), tamanho=6, max_chars=35)

    # Campo 21 - Logradouro
    escrever(c, 90, 452, valor_seguro(registro, "NM_LOGRADO"), tamanho=6, max_chars=44)

    # Campo 22 - Número
    escrever(c, 380, 452, valor_seguro(registro, "NU_NUMERO"), tamanho=6)

    # Campo 23 - Complemento
    escrever(c, 455, 452, valor_seguro(registro, "NM_COMPLEM"), tamanho=6, max_chars=20)

    # Campo 26 - Ponto de referência
    escrever(c, 90, 427, valor_seguro(registro, "NM_REFEREN"), tamanho=6, max_chars=55)

    # Campo 27 - Telefone
    tel = f"{valor_seguro(registro, 'NU_DDD_TEL')} {valor_seguro(registro, 'NU_TELEFON')}".strip()
    escrever(c, 415, 427, tel, tamanho=6, max_chars=18)

    # Campo 30 - Zona
    escrever(c, 530, 427, valor_seguro(registro, "CS_ZONA"), tamanho=6)

    # Campo 31 - Ocupação
    escrever(c, 88, 365, valor_seguro(registro, "ID_OCUPA_N"), tamanho=6)

    # Campo 32 - Situação no mercado
    escrever(c, 88, 330, valor_seguro(registro, "SIT_TRAB"), tamanho=6)

    # Campo 33 - Tempo trabalho ocupação
    escrever(c, 430, 365, valor_seguro(registro, "TEMPO_TRAB"), tamanho=6)

    # Campo 34 - Local acidente
    escrever(c, 390, 330, valor_seguro(registro, "LOCAL_ACID"), tamanho=6)

    # Campo 35 - Registro/CNPJ/CPF
    escrever(c, 90, 275, valor_seguro(registro, "CNPJ_EMP"), tamanho=6, max_chars=18)

    # Campo 36 - Empresa/Empregador
    escrever(c, 250, 275, valor_seguro(registro, "NM_EMPRESA"), tamanho=6, max_chars=45)

    # Campo 37 - CNAE
    escrever(c, 90, 247, valor_seguro(registro, "CNAE"), tamanho=6)

    # Campos endereço empresa
    escrever(c, 170, 247, valor_seguro(registro, "NM_BAIRRO_EMP"), tamanho=6, max_chars=25)
    escrever(c, 300, 247, valor_seguro(registro, "ID_MUNIC_EMP"), tamanho=6)
    escrever(c, 440, 247, valor_seguro(registro, "SG_UF_EMP"), tamanho=6)

    c.showPage()

    # ========================================================
    # PÁGINA 2
    # ========================================================

    # Campo 46 - Empresa terceirizada
    escrever(c, 90, 760, valor_seguro(registro, "EMP_TERCE"), tamanho=6)

    # Campo 47 - CNAE empresa principal
    escrever(c, 90, 733, valor_seguro(registro, "CNAE_PRINC"), tamanho=6)

    # Campo 48 - CNPJ principal
    escrever(c, 90, 705, valor_seguro(registro, "CNPJ_PRINC"), tamanho=6, max_chars=18)

    # Campo 49 - Razão social
    escrever(c, 255, 705, valor_seguro(registro, "RAZAO_SOC"), tamanho=6, max_chars=48)

    # Campo 50 - Hora acidente
    escrever(c, 90, 668, valor_seguro(registro, "HORA_ACID"), tamanho=6)

    # Campo 51 - Horas após jornada
    escrever(c, 230, 668, valor_seguro(registro, "HORAS_JOR"), tamanho=6)

    # Campo 52 - UF ocorrência
    escrever(c, 90, 640, valor_seguro(registro, "UF_ACID"), tamanho=6)

    # Campo 53 - Município ocorrência
    escrever(c, 150, 640, valor_seguro(registro, "MUN_ACID"), tamanho=6)

    # Campo 54 - CID causa
    escrever(c, 90, 610, valor_seguro(registro, "CID_CAUSA"), tamanho=6)

    # Campo 55 - Tipo acidente
    escrever(c, 230, 610, valor_seguro(registro, "TIPO_ACID"), tamanho=6)

    # Campo 56 - Outros trabalhadores
    escrever(c, 355, 610, valor_seguro(registro, "MAIS_TRAB"), tamanho=6)

    # Campo 57 - Quantos
    escrever(c, 500, 610, valor_seguro(registro, "QTD_TRAB"), tamanho=6)

    # Campo 58 - Atendimento médico
    escrever(c, 90, 570, valor_seguro(registro, "ATENDE_MED"), tamanho=6)

    # Campo 59 - Data atendimento
    escrever(c, 210, 570, formatar_data(registro.get("DT_ATEND", "")), tamanho=6)

    # Campo 60 - UF atendimento
    escrever(c, 90, 540, valor_seguro(registro, "UF_ATEND"), tamanho=6)

    # Campo 61 - Município atendimento
    escrever(c, 150, 540, valor_seguro(registro, "MUN_ATEND"), tamanho=6)

    # Campo 62 - Unidade atendimento
    escrever(c, 90, 512, valor_seguro(registro, "UNID_ATEND"), tamanho=6, max_chars=55)

    # Campo 63 - Partes corpo
    partes = " / ".join([
        valor_seguro(registro, "PART_CORP1"),
        valor_seguro(registro, "PART_CORP2"),
        valor_seguro(registro, "PART_CORP3")
    ]).strip(" / ")

    escrever(c, 90, 465, partes, tamanho=6, max_chars=40)

    # Campo 64 - CID lesão
    escrever(c, 90, 425, valor_seguro(registro, "CID_LESAO"), tamanho=6)

    # Campo 65 - Regime
    escrever(c, 230, 425, valor_seguro(registro, "REGIME"), tamanho=6)

    # Campo 66 - Evolução
    escrever(c, 90, 385, valor_seguro(registro, "EVOLUCAO"), tamanho=6)

    # Campo 67 - Data óbito
    escrever(c, 295, 385, formatar_data(registro.get("DT_OBITO", "")), tamanho=6)

    # Campo 68 - CAT
    escrever(c, 90, 345, valor_seguro(registro, "CAT"), tamanho=6)

    # Descrição sumária
    obs = valor_seguro(registro, "DS_OBS")
    escrever_multilinha(
        c,
        x=55,
        y=230,
        texto=obs,
        largura_chars=105,
        tamanho=6,
        entrelinha=9,
        max_linhas=7
    )

    c.save()
    packet.seek(0)
    return packet


# ============================================================
# GERAÇÃO FINAL
# ============================================================

def gerar_ficha_pdf(registro, caminho_pdf_base):
    """
    Mescla a ficha original com o overlay preenchido.
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
