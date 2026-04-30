from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def valor_bruto(registro, coluna):
    """
    Retorna o valor bruto do banco, sem descrição.
    Usado para preencher quadrículos codificados.
    """
    if coluna not in registro.index:
        return ""

    valor = registro[coluna]

    if valor is None:
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["", "nan", "none", "nat", "null", "ignorado"]:
        return ""

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto


def valor_texto(registro, coluna):
    """
    Retorna texto seguro para campos textuais.
    """
    if coluna not in registro.index:
        return ""

    valor = registro[coluna]

    if valor is None:
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["", "nan", "none", "nat", "null", "ignorado"]:
        return ""

    return texto


def formatar_data(valor):
    """
    Formata data em dd/mm/aaaa.
    """
    if valor is None:
        return ""

    try:
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y")
    except Exception:
        pass

    texto = str(valor).strip()

    if texto.lower() in ["", "nan", "none", "nat", "null", "ignorado"]:
        return ""

    return texto


def escrever(c, x, y, texto, tamanho=6.2, max_chars=None):
    """
    Escreve texto simples.
    """
    texto = "" if texto is None else str(texto)

    if max_chars:
        texto = texto[:max_chars]

    c.setFont("Helvetica", tamanho)
    c.drawString(x, y, texto)


def escrever_codigo(c, x, y, codigo, tamanho=7):
    """
    Escreve código curto dentro de quadrículo.
    """
    codigo = "" if codigo is None else str(codigo).strip()

    if codigo.lower() in ["", "nan", "none", "nat", "null", "ignorado"]:
        return

    if codigo.endswith(".0"):
        codigo = codigo[:-2]

    c.setFont("Helvetica-Bold", tamanho)
    c.drawCentredString(x, y, codigo)


def escrever_multilinha(c, x, y, texto, largura_chars=95, tamanho=6.2, entrelinha=9, max_linhas=6):
    """
    Escreve texto longo respeitando linhas.
    """
    if texto is None:
        return

    texto = str(texto).replace("\n", " ").strip()

    if texto.lower() in ["", "nan", "none", "nat", "null", "ignorado"]:
        return

    palavras = texto.split()
    linhas = []
    atual = ""

    for palavra in palavras:
        tentativa = f"{atual} {palavra}".strip()

        if len(tentativa) <= largura_chars:
            atual = tentativa
        else:
            linhas.append(atual)
            atual = palavra

    if atual:
        linhas.append(atual)

    linhas = linhas[:max_linhas]

    c.setFont("Helvetica", tamanho)

    for i, linha in enumerate(linhas):
        c.drawString(x, y - (i * entrelinha), linha)


# ============================================================
# OVERLAY DA FICHA
# ============================================================

def criar_overlay_acidente_trabalho(registro):
    """
    Cria camada de preenchimento da ficha de Acidente de Trabalho Grave.

    Observação:
    Esta versão corrige a lógica:
    - campos de texto recebem texto;
    - campos com quadrículo recebem apenas código;
    - "Ignorado" não é escrito como texto solto.
    """

    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    # ========================================================
    # PÁGINA 1
    # ========================================================

    # Número da notificação no topo
    escrever(c, 485, 794, valor_bruto(registro, "NU_NOTIFIC"), tamanho=7)

    # Campo 1 - Tipo de Notificação
    escrever_codigo(c, 56, 662, valor_bruto(registro, "TP_NOT"))

    # Campo 2 - Agravo/doença
    escrever(c, 135, 632, "ACIDENTE DE TRABALHO", tamanho=7, max_chars=35)

    # CID Y96
    escrever(c, 400, 632, "Y96", tamanho=7)

    # Campo 3 - Data da Notificação
    escrever(c, 468, 632, formatar_data(registro.get("DT_NOTIFIC", "")), tamanho=6.5)

    # Campo 4 - UF
    escrever(c, 62, 608, valor_bruto(registro, "SG_UF_NOT"), tamanho=6)

    # Campo 5 - Município de Notificação
    escrever(c, 105, 608, valor_bruto(registro, "ID_MUNICIP"), tamanho=6)

    # Campo 6 - Unidade notificadora
    escrever(c, 92, 580, valor_bruto(registro, "ID_UNIDADE"), tamanho=6)

    # Campo 7 - Data do Acidente
    escrever(c, 470, 580, formatar_data(registro.get("DT_ACID", "")), tamanho=6.5)

    # Campo 8 - Nome do Paciente
    escrever(c, 82, 548, valor_texto(registro, "NM_PACIENT"), tamanho=6.2, max_chars=55)

    # Campo 9 - Data de Nascimento
    escrever(c, 468, 548, formatar_data(registro.get("DT_NASC", "")), tamanho=6.5)

    # Campo 10 - Idade
    idade = valor_bruto(registro, "NU_IDADE_N")
    if not idade:
        idade = valor_bruto(registro, "IDADE_CALCULADA")
    escrever(c, 82, 518, idade, tamanho=6.2, max_chars=8)

    # Campo 11 - Sexo
    escrever_codigo(c, 250, 518, valor_bruto(registro, "CS_SEXO"))

    # Campo 12 - Gestante
    escrever_codigo(c, 326, 518, valor_bruto(registro, "CS_GESTANT"))

    # Campo 13 - Raça/Cor
    escrever_codigo(c, 548, 518, valor_bruto(registro, "CS_RACA"))

    # Campo 14 - Escolaridade
    escrever_codigo(c, 548, 486, valor_bruto(registro, "CS_ESCOL_N"))

    # Campo 15 - Cartão SUS
    escrever(c, 82, 458, valor_bruto(registro, "ID_CNS_SUS"), tamanho=6.0, max_chars=18)

    # Campo 16 - Nome da mãe
    escrever(c, 285, 458, valor_texto(registro, "NM_MAE_PAC"), tamanho=6.2, max_chars=58)

    # Campo 17 - UF residência
    escrever(c, 62, 414, valor_bruto(registro, "SG_UF"), tamanho=6)

    # Campo 18 - Município de Residência
    escrever(c, 120, 414, valor_bruto(registro, "ID_MN_RESI"), tamanho=6)

    # Campo 19 - Distrito
    escrever(c, 460, 414, valor_bruto(registro, "ID_RG_RESI"), tamanho=6)

    # Campo 20 - Bairro
    escrever(c, 82, 384, valor_texto(registro, "NM_BAIRRO"), tamanho=6.0, max_chars=35)

    # Campo 21 - Logradouro
    escrever(c, 190, 384, valor_texto(registro, "NM_LOGRADO"), tamanho=6.0, max_chars=48)

    # Campo 22 - Número
    escrever(c, 82, 358, valor_bruto(registro, "NU_NUMERO"), tamanho=6)

    # Campo 23 - Complemento
    escrever(c, 170, 358, valor_texto(registro, "NM_COMPLEM"), tamanho=6.0, max_chars=42)

    # Campo 24 - Geo campo 1
    escrever(c, 435, 358, valor_bruto(registro, "GEO_CAMPO1"), tamanho=6)

    # Campo 25 - Geo campo 2
    escrever(c, 82, 330, valor_bruto(registro, "GEO_CAMPO2"), tamanho=6)

    # Campo 26 - Ponto de Referência
    escrever(c, 210, 330, valor_texto(registro, "NM_REFEREN"), tamanho=6.0, max_chars=50)

    # Campo 27 - CEP
    escrever(c, 470, 330, valor_bruto(registro, "NU_CEP"), tamanho=6)

    # Campo 28 - Telefone
    tel = f"{valor_bruto(registro, 'NU_DDD_TEL')} {valor_bruto(registro, 'NU_TELEFON')}".strip()
    escrever(c, 82, 300, tel, tamanho=6, max_chars=18)

    # Campo 29 - Zona
    escrever_codigo(c, 333, 300, valor_bruto(registro, "CS_ZONA"))

    # Campo 30 - País
    escrever(c, 410, 300, valor_texto(registro, "ID_PAIS"), tamanho=6)

    # Campo 31 - Ocupação
    escrever(c, 82, 246, valor_bruto(registro, "ID_OCUPA_N"), tamanho=6.2, max_chars=12)

    # Campo 32 - Situação no Mercado de Trabalho
    escrever_codigo(c, 548, 208, valor_bruto(registro, "SIT_TRAB"))

    # Campo 33 - Tempo de Trabalho na Ocupação
    escrever(c, 82, 170, valor_bruto(registro, "TEMPO_TRAB"), tamanho=6.2, max_chars=10)

    # Campo 34 - Local onde ocorreu o acidente
    escrever_codigo(c, 548, 170, valor_bruto(registro, "LOCAL_ACID"))

    # Campo 35 - Registro/CNPJ/CPF
    escrever(c, 82, 122, valor_bruto(registro, "CNPJ_EMP"), tamanho=6.0, max_chars=20)

    # Campo 36 - Nome da Empresa ou Empregador
    escrever(c, 250, 122, valor_texto(registro, "NM_EMPRESA"), tamanho=6.0, max_chars=58)

    # Campo 37 - CNAE
    escrever(c, 82, 94, valor_bruto(registro, "CNAE"), tamanho=6.0, max_chars=10)

    # Campo 38 - UF
    escrever(c, 237, 94, valor_bruto(registro, "UF_EMP"), tamanho=6)

    # Campo 39 - Município
    escrever(c, 282, 94, valor_bruto(registro, "MUN_EMP"), tamanho=6)

    # Campo 40 - Distrito
    escrever(c, 82, 67, valor_texto(registro, "DISTRITO_EMP"), tamanho=5.5, max_chars=24)

    # Campo 41 - Bairro
    escrever(c, 210, 67, valor_texto(registro, "BAIRRO_EMP"), tamanho=5.5, max_chars=28)

    # Campo 42 - Endereço
    escrever(c, 365, 67, valor_texto(registro, "END_EMP"), tamanho=5.5, max_chars=36)

    # Campo 43 - Número
    escrever(c, 82, 40, valor_bruto(registro, "NUM_EMP"), tamanho=5.5)

    # Campo 44 - Ponto de referência
    escrever(c, 145, 40, valor_texto(registro, "REF_EMP"), tamanho=5.5, max_chars=36)

    # Campo 45 - Telefone
    escrever(c, 455, 40, valor_bruto(registro, "TEL_EMP"), tamanho=5.5, max_chars=15)

    c.showPage()

    # ========================================================
    # PÁGINA 2
    # ========================================================

    # Campo 46 - Empregador é empresa terceirizada
    escrever_codigo(c, 548, 794, valor_bruto(registro, "EMP_TERCE"))

    # Campo 47 - CNAE empresa principal
    escrever(c, 82, 744, valor_bruto(registro, "CNAE_PRINC"), tamanho=6.0, max_chars=12)

    # Campo 48 - CNPJ empresa principal
    escrever(c, 310, 744, valor_bruto(registro, "CNPJ_PRINC"), tamanho=6.0, max_chars=20)

    # Campo 49 - Razão Social
    escrever(c, 82, 716, valor_texto(registro, "RAZAO_SOC"), tamanho=6.0, max_chars=80)

    # Campo 50 - Hora do Acidente
    escrever(c, 82, 662, valor_bruto(registro, "HORA_ACID"), tamanho=6.2, max_chars=8)

    # Campo 51 - Horas após início da jornada
    escrever(c, 388, 662, valor_bruto(registro, "HORAS_JOR"), tamanho=6.2, max_chars=8)

    # Campo 52 - UF ocorrência
    escrever(c, 82, 620, valor_bruto(registro, "UF_ACID"), tamanho=6)

    # Campo 53 - Município ocorrência
    escrever(c, 135, 620, valor_bruto(registro, "MUN_ACID"), tamanho=6)

    # Campo 54 - CID causa do acidente
    escrever(c, 430, 620, valor_bruto(registro, "CID_CAUSA"), tamanho=6.2, max_chars=8)

    # Campo 55 - Tipo de Acidente
    escrever_codigo(c, 548, 590, valor_bruto(registro, "TIPO_ACID"))

    # Campo 56 - Outros trabalhadores atingidos
    escrever_codigo(c, 548, 560, valor_bruto(registro, "MAIS_TRAB"))

    # Campo 57 - Quantos
    escrever(c, 520, 530, valor_bruto(registro, "QTD_TRAB"), tamanho=6.2, max_chars=4)

    # Campo 58 - Atendimento Médico
    escrever_codigo(c, 548, 500, valor_bruto(registro, "ATENDE_MED"))

    # Campo 59 - Data atendimento
    escrever(c, 365, 500, formatar_data(registro.get("DT_ATEND", "")), tamanho=6.2)

    # Campo 60 - UF atendimento
    escrever(c, 525, 500, valor_bruto(registro, "UF_ATEND"), tamanho=6)

    # Campo 61 - Município atendimento
    escrever(c, 82, 470, valor_bruto(registro, "MUN_ATEND"), tamanho=6)

    # Campo 62 - Unidade atendimento
    escrever(c, 285, 470, valor_texto(registro, "UNID_ATEND"), tamanho=6.0, max_chars=50)

    # Campo 63 - Partes do corpo atingidas
    escrever_codigo(c, 345, 404, valor_bruto(registro, "PART_CORP1"))
    escrever_codigo(c, 345, 390, valor_bruto(registro, "PART_CORP2"))
    escrever_codigo(c, 345, 376, valor_bruto(registro, "PART_CORP3"))

    # Campo 64 - Diagnóstico da Lesão
    escrever(c, 420, 378, valor_bruto(registro, "CID_LESAO"), tamanho=6.2, max_chars=8)

    # Campo 65 - Regime de Tratamento
    escrever_codigo(c, 548, 378, valor_bruto(registro, "REGIME"))

    # Campo 66 - Evolução do Caso
    escrever_codigo(c, 548, 318, valor_bruto(registro, "EVOLUCAO"))

    # Campo 67 - Data do óbito
    escrever(c, 82, 284, formatar_data(registro.get("DT_OBITO", "")), tamanho=6.2)

    # Campo 68 - CAT
    escrever_codigo(c, 548, 284, valor_bruto(registro, "CAT"))

    # Descrição sumária
    obs = valor_texto(registro, "DS_OBS")
    escrever_multilinha(
        c,
        x=35,
        y=220,
        texto=obs,
        largura_chars=118,
        tamanho=5.8,
        entrelinha=9,
        max_linhas=6
    )

    c.save()
    packet.seek(0)
    return packet


# ============================================================
# GERAÇÃO FINAL
# ============================================================

def gerar_ficha_pdf(registro, caminho_pdf_base):
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
