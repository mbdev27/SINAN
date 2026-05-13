import streamlit as st
import pandas as pd

from utils.auth import exigir_login, obter_usuario_atual, fazer_logout
from utils.tema import aplicar_tema_streamlit
from utils.supabase_client import testar_conexao_supabase


st.set_page_config(
    page_title="Teste Supabase",
    page_icon="🧪",
    layout="wide"
)

exigir_login()
aplicar_tema_streamlit(st)

usuario = obter_usuario_atual()

st.sidebar.markdown("## 👤 Sessão")
st.sidebar.write(f"**Usuário:** {usuario.get('nome', '—')}")
st.sidebar.write(f"**Perfil:** {usuario.get('perfil', '—')}")

if st.sidebar.button("🚪 Sair do sistema", use_container_width=True):
    fazer_logout()
    st.rerun()


st.title("🧪 Teste de conexão com Supabase")
st.caption("Horizonte Health Intelligence • Verificação inicial da conexão PostgreSQL/Supabase")

st.info(
    "Esta página serve apenas para confirmar que o Streamlit consegue conversar "
    "com o Supabase."
)

if st.button("Testar conexão", use_container_width=True):
    try:
        dados = testar_conexao_supabase()

        st.success("Conexão realizada com sucesso!")

        if dados:
            st.dataframe(
                pd.DataFrame(dados),
                use_container_width=True
            )
        else:
            st.warning("A conexão funcionou, mas a tabela usuarios não retornou registros.")

    except Exception as e:
        st.error("Não foi possível conectar ao Supabase.")
        st.exception(e)
