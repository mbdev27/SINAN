import streamlit as st

st.set_page_config(
    page_title="SINAN Decoder",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 SINAN Decoder")
st.markdown("""
Sistema online para leitura, decodificação e análise de bancos DBF do SINAN.

A aplicação permite enviar um arquivo `.DBF`, selecionar a ficha correspondente,
traduzir campos codificados e gerar painéis interativos para análise em saúde pública.
""")

st.markdown("---")

st.subheader("Primeiro módulo disponível")
st.markdown("""
### Acidente de Trabalho Grave

Este módulo lê bancos DBF de Acidente de Trabalho Grave e cruza os campos
com a ficha oficial de investigação do Ministério da Saúde.
""")
