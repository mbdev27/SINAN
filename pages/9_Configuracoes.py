import pandas as pd
import streamlit as st

from utils.auth import (
    exigir_login,
    obter_usuario_atual,
    carregar_usuarios,
    salvar_usuario_runtime,
    excluir_usuario_runtime,
    salvar_avatar_usuario,
    carregar_solicitacoes_exclusao,
    registrar_solicitacao_exclusao,
    atualizar_status_solicitacao_exclusao,
    fazer_logout,
    agora_iso,
)

from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly

try:
    from utils.supabase_client import (
        testar_conexao_supabase,
        listar_usuarios_supabase,
        migrar_usuarios_locais_para_supabase,
    )
except Exception:
    testar_conexao_supabase = None
    listar_usuarios_supabase = None
    migrar_usuarios_locais_para_supabase = None

try:
    from utils.historico_uploads import (
        migrar_historico_uploads_local_para_supabase,
        historico_para_dataframe,
    )
except Exception:
    migrar_historico_uploads_local_para_supabase = None
    historico_para_dataframe = None

try:
    from utils.referencias_ibge import (
        importar_municipios_ibge_para_supabase,
        municipios_para_dataframe,
    )
except Exception:
    importar_municipios_ibge_para_supabase = None
    municipios_para_dataframe = None

try:
    from utils.referencias_cnes import (
        importar_municipios_cnes_csv,
        importar_estabelecimentos_cnes_csv,
        contar_referencias_cnes,
    )
except Exception:
    importar_municipios_cnes_csv = None
    importar_estabelecimentos_cnes_csv = None
    contar_referencias_cnes = None


st.set_page_config(
    page_title="Configurações",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

exigir_login()
aplicar_tema_streamlit(st)
aplicar_tema_plotly()


usuario_atual = obter_usuario_atual()
login_atual = usuario_atual.get("usuario")
perfil_atual = str(usuario_atual.get("perfil", "")).strip()
eh_admin = perfil_atual.lower() == "admin"


st.sidebar.markdown("## 👤 Sessão")
st.sidebar.write(f"**Usuário:** {usuario_atual.get('nome', '—')}")
st.sidebar.write(f"**Perfil:** {usuario_atual.get('perfil', '—')}")

if st.sidebar.button("🚪 Sair do sistema", use_container_width=True):
    fazer_logout()
    st.rerun()


st.title("⚙️ Configurações")
st.caption(
    "Horizonte Health Intelligence • Conta, preferências, LGPD, administração e diagnóstico técnico."
)

usuarios = carregar_usuarios()

if login_atual not in usuarios:
    st.error("Usuário atual não localizado na base.")
    st.stop()

dados_meu_usuario = dict(usuarios[login_atual])

if eh_admin:
    abas = [
        "👤 Minha conta",
        "🔐 Segurança e acesso",
        "📜 LGPD",
        "🛡️ Administração",
        "🧪 Diagnóstico",
    ]
else:
    abas = [
        "👤 Minha conta",
        "🔐 Segurança e acesso",
        "📜 LGPD",
    ]

abas_renderizadas = st.tabs(abas)

aba_conta = abas_renderizadas[0]
aba_seguranca = abas_renderizadas[1]
aba_lgpd = abas_renderizadas[2]

if eh_admin:
    aba_admin = abas_renderizadas[3]
    aba_diagnostico = abas_renderizadas[4]


with aba_conta:
    st.subheader("👤 Dados cadastrais")

    col_avatar, col_dados = st.columns([1, 2])

    with col_avatar:
        avatar_path = dados_meu_usuario.get("avatar_path", "")

        if avatar_path:
            try:
                st.image(avatar_path, width=180)
            except Exception:
                st.info("Avatar não localizado.")
        else:
            st.info("Nenhum avatar cadastrado.")

        novo_avatar = st.file_uploader(
            "Foto/avatar",
            type=["png", "jpg", "jpeg", "webp"]
        )

    with col_dados:
        novo_nome = st.text_input("Nome", value=dados_meu_usuario.get("nome", ""))
        novo_email = st.text_input("E-mail", value=dados_meu_usuario.get("email", ""))
        municipio = st.text_input("Município", value=dados_meu_usuario.get("municipio", ""))
        instituicao = st.text_input("Instituição", value=dados_meu_usuario.get("instituicao", ""))
        cargo = st.text_input("Cargo", value=dados_meu_usuario.get("cargo", ""))
        funcao = st.text_input("Função", value=dados_meu_usuario.get("funcao", ""))

        tema_atual = dados_meu_usuario.get("tema", "Escuro")
        if tema_atual not in ["Escuro", "Claro", "Automático"]:
            tema_atual = "Escuro"

        tema = st.selectbox(
            "Tema preferido",
            ["Escuro", "Claro", "Automático"],
            index=["Escuro", "Claro", "Automático"].index(tema_atual)
        )

    if st.button("💾 Salvar dados da conta", use_container_width=True):
        if not novo_nome or not novo_email:
            st.error("Nome e e-mail são obrigatórios.")
        elif "@" not in novo_email:
            st.error("Informe um e-mail válido.")
        else:
            if novo_avatar is not None:
                caminho_avatar = salvar_avatar_usuario(login_atual, novo_avatar)
                if caminho_avatar:
                    dados_meu_usuario["avatar_path"] = caminho_avatar

            dados_meu_usuario.update({
                "nome": novo_nome,
                "email": novo_email,
                "municipio": municipio,
                "instituicao": instituicao,
                "cargo": cargo,
                "funcao": funcao,
                "tema": tema,
            })

            ok = salvar_usuario_runtime(login_atual, dados_meu_usuario)

            if ok:
                st.success("Dados atualizados com sucesso.")
                st.rerun()
            else:
                st.error("Não foi possível salvar as alterações.")


with aba_seguranca:
    st.subheader("🔐 Segurança e acesso")

    col1
