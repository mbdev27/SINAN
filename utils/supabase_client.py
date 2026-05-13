import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def obter_supabase() -> Client:
    """
    Cria e reutiliza a conexão com o Supabase.

    Usa a service_role_key porque, nesta primeira fase,
    a aplicação Streamlit ainda está fazendo a gestão interna
    dos usuários, uploads e permissões.

    Nunca coloque a service_role_key direto no código.
    Ela deve ficar apenas no secrets.toml/local ou nos Secrets
    do Streamlit Cloud.
    """

    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["service_role_key"]

    return create_client(url, key)


def testar_conexao_supabase():
    """
    Teste simples para confirmar se o Supabase está respondendo.
    """

    supabase = obter_supabase()

    resposta = (
        supabase
        .table("usuarios")
        .select("id, usuario, nome, perfil")
        .limit(5)
        .execute()
    )

    return resposta.data
