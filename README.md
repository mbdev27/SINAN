# 🧬 SINAN Decoder

Sistema inteligente para leitura, decodificação, análise e visualização de bancos de dados do **SINAN (Sistema de Informação de Agravos de Notificação)**.

O projeto transforma arquivos `.DBF` brutos em um ambiente visual, intuitivo e interativo, permitindo que profissionais da Vigilância em Saúde consultem, filtrem, interpretem e exportem informações epidemiológicas com facilidade.

---

# 🌎 Visão Geral

O SINAN utiliza bancos estruturados em formato `.DBF`, contendo informações codificadas.

Esses códigos só fazem sentido quando cruzados com a respectiva **Ficha de Investigação/Notificação do Ministério da Saúde**, que funciona como um verdadeiro “dicionário secreto” do banco.

Exemplo:

| Campo na Ficha | Coluna no DBF | Significado                         |
| -------------- | ------------- | ----------------------------------- |
| 3              | DT_NOTIFIC    | Data da Notificação                 |
| 31             | ID_OCUPA_N    | Ocupação                            |
| 32             | SIT_TRAB      | Situação no Mercado de Trabalho     |
| 66             | EVOLUCAO      | Evolução do Caso                    |
| 68             | CAT           | Comunicação de Acidente de Trabalho |

O objetivo do projeto é automatizar esse cruzamento.

---

# 🎯 Objetivos do Projeto

O sistema foi criado para:

* Ler bancos `.DBF` do SINAN
* Traduzir códigos automaticamente
* Cruzar dados com fichas oficiais do Ministério da Saúde
* Construir painéis epidemiológicos interativos
* Gerar análises situacionais
* Permitir buscas rápidas por notificação
* Exportar dados tratados
* Gerar fichas preenchidas em PDF
* Facilitar o trabalho das vigilâncias municipais e estaduais
* Democratizar o acesso à informação em saúde

---

# 🏗️ Arquitetura do Projeto

```text
sinan-decoder/
│
├── Home.py
├── requirements.txt
├── README.md
│
├── pages/
│   └── 1_Leitor_DBF.py
│
├── mappings/
│   └── acidente_trabalho_grave.py
│
└── utils/
    └── leitor_dbf.py
```

---

# ⚙️ Tecnologias Utilizadas

## Backend e processamento

* Python
* Pandas
* NumPy
* dbfread

## Frontend

* Streamlit
* Plotly
* HTML + CSS customizados

## Geração de documentos

* reportlab
* pypdf

## Hospedagem

* GitHub
* Streamlit Cloud

---

# 🧠 Como o Sistema Funciona

## 1. Upload do banco DBF

O usuário envia um arquivo `.DBF` exportado do SINAN.

Exemplo:

```text
ATGR2025.DBF
```

---

## 2. Seleção da ficha correspondente

O usuário escolhe qual ficha do Ministério da Saúde corresponde ao banco.

Exemplo:

* Acidente de Trabalho Grave
* Dengue
* Violência
* Intoxicação Exógena
* Oropouche
* Tuberculose
* Sífilis
* etc.

---

## 3. Tradução automática dos códigos

O sistema utiliza um dicionário de tradução.

Exemplo:

```python
"CS_SEXO": {
    "M": "Masculino",
    "F": "Feminino",
    "I": "Ignorado"
}
```

O banco deixa de exibir:

```text
CS_SEXO = M
```

e passa a mostrar:

```text
Sexo = Masculino
```

---

## 4. Construção do painel analítico

Após a tradução:

* gráficos são gerados
* indicadores são calculados
* filtros ficam disponíveis
* dados sensíveis são ocultados

---

# 🔒 Proteção de Dados

O sistema possui ocultação automática de informações sensíveis.

Campos como:

* Nome do paciente
* Nome da mãe
* Endereço
* Telefone
* CNS
* CPF

podem ser removidos automaticamente da visualização pública.

---

# 📊 Funcionalidades

## ✅ Leitura de arquivos DBF

Compatível com:

* SINAN Net
* exportações DBF
* LibreOffice Calc
* arquivos históricos

---

## ✅ Tradução automática

Transforma códigos em descrições compreensíveis.

---

## ✅ Filtros dinâmicos

Permite filtrar por:

* sexo
* raça/cor
* bairro
* município
* ocupação
* evolução
* semana epidemiológica
* faixa etária
* classificação

---

## ✅ Busca inteligente

Busca por:

* número da notificação
* termos livres
* CID
* ocupação
* bairro
* CNAE
* qualquer palavra existente no banco

---

## ✅ Indicadores epidemiológicos

Exemplos:

* total de casos
* letalidade
* acidentes típicos
* acidentes de trajeto
* CAT emitida
* hospitalizações
* evolução dos casos

---

## ✅ Gráficos interativos

* pizza
* barras
* linhas temporais
* mapas
* histogramas
* heatmaps

---

## ✅ Exportação CSV

O usuário pode baixar os dados tratados.

---

## 🚧 Em desenvolvimento

### 🔥 Geração automática de ficha preenchida em PDF

O sistema irá:

1. localizar a notificação
2. abrir a ficha oficial do Ministério da Saúde
3. preencher automaticamente os campos
4. gerar PDF pronto para impressão

---

# 🎨 Identidade Visual

O projeto utiliza identidade visual inspirada na Prefeitura do Ipojuca.

## Paleta institucional

| Cor                   | Hex       |
| --------------------- | --------- |
| Azul principal        | `#004A8D` |
| Azul secundário       | `#0073CF` |
| Verde Ipojuca         | `#009D4A` |
| Amarelo institucional | `#FFC20E` |
| Fundo claro           | `#F6F9FC` |

---

# 📂 Mapeamentos

Cada agravo possui:

```text
mappings/
```

Exemplo:

```text
acidente_trabalho_grave.py
```

Esse arquivo contém:

* nomes dos campos
* traduções
* regras de interpretação
* dicionários
* ocultação de dados sensíveis

---

# 🧩 Estrutura Modular

O sistema foi pensado para crescer.

Novos agravos podem ser adicionados facilmente.

Exemplo:

```text
mappings/
├── dengue.py
├── tuberculose.py
├── violencia.py
├── sifilis.py
├── intoxicacao.py
```

---

# 🌐 Implantação Online

## GitHub

O código é hospedado no GitHub.

---

## Streamlit Cloud

A aplicação é publicada automaticamente online.

---

# 🚀 Como Executar Localmente

## 1. Clonar repositório

```bash
git clone https://github.com/seu-usuario/sinan-decoder.git
```

---

## 2. Entrar na pasta

```bash
cd sinan-decoder
```

---

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 4. Rodar Streamlit

```bash
streamlit run Home.py
```

---

# 📌 Roadmap do Projeto

## Fase 1 — MVP

* [x] Leitura DBF
* [x] Tradução automática
* [x] Filtros
* [x] Dashboard inicial

---

## Fase 2 — Inteligência Epidemiológica

* [ ] Indicadores avançados
* [ ] Séries temporais
* [ ] Georreferenciamento
* [ ] Busca universal

---

## Fase 3 — Biblioteca SINAN

* [ ] Todas as fichas do Ministério da Saúde
* [ ] Sistema modular de agravos

---

## Fase 4 — PDF Inteligente

* [ ] Geração automática de ficha preenchida
* [ ] Exportação PDF oficial

---

## Fase 5 — Plataforma Completa

* [ ] Login
* [ ] Controle de acesso
* [ ] Multiusuário
* [ ] Banco SQL
* [ ] API
* [ ] Integração com e-SUS
* [ ] Integração com GAL
* [ ] Integração com SIM
* [ ] Integração com SIH

---

# 🏥 Aplicações na Saúde Pública

O sistema pode ser usado por:

* Vigilância Epidemiológica
* Vigilância em Saúde do Trabalhador
* Vigilância Sanitária
* CIEVS
* Secretarias Municipais
* Secretarias Estaduais
* Hospitais
* CEREST
* Núcleos de Epidemiologia Hospitalar
* Universidades
* Pesquisadores

---

# 📚 Exemplos de Uso

## Acidente de Trabalho Grave

* ocupações mais atingidas
* acidentes fatais
* análise territorial
* acidentes por CNAE

---

## Dengue

* bairros mais afetados
* curvas epidêmicas
* sazonalidade

---

## Violência

* perfil das vítimas
* reincidência
* vínculo com agressor

---

# 👨‍💻 Desenvolvimento

Projeto idealizado para transformar bancos epidemiológicos complexos em inteligência acessível.

---

# ❤️ Filosofia do Projeto

“Todo banco de dados em saúde conta uma história.
O papel deste sistema é traduzir códigos em cuidado,
e transformar informação em ação.”
