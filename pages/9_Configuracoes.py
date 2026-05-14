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


# ============================================================
# MINHA CONTA
# ============================================================

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
        novo_nome = st.text_input(
            "Nome",
            value=dados_meu_usuario.get("nome", "")
        )

        novo_email = st.text_input(
            "E-mail",
            value=dados_meu_usuario.get("email", "")
        )

        municipio = st.text_input(
            "Município",
            value=dados_meu_usuario.get("municipio", "")
        )

        instituicao = st.text_input(
            "Instituição",
            value=dados_meu_usuario.get("instituicao", "")
        )

        cargo = st.text_input(
            "Cargo",
            value=dados_meu_usuario.get("cargo", "")
        )

        funcao = st.text_input(
            "Função",
            value=dados_meu_usuario.get("funcao", "")
        )

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
                caminho_avatar = salvar_avatar_usuario(
                    login_atual,
                    novo_avatar
                )

                if caminho_avatar:
                    dados_meu_usuario["avatar_path"] = caminho_avatar

            dados_meu_usuario["nome"] = novo_nome
            dados_meu_usuario["email"] = novo_email
            dados_meu_usuario["municipio"] = municipio
            dados_meu_usuario["instituicao"] = instituicao
            dados_meu_usuario["cargo"] = cargo
            dados_meu_usuario["funcao"] = funcao
            dados_meu_usuario["tema"] = tema

            ok = salvar_usuario_runtime(
                login_atual,
                dados_meu_usuario
            )

            if ok:
                st.success("Dados atualizados com sucesso.")
                st.rerun()
            else:
                st.error("Não foi possível salvar as alterações.")


# ============================================================
# SEGURANÇA
# ============================================================

with aba_seguranca:
    st.subheader("🔐 Segurança e acesso")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Perfil",
        dados_meu_usuario.get("perfil", "Usuário")
    )

    col2.metric(
        "E-mail verificado",
        "Sim" if dados_meu_usuario.get("verificado", False) else "Não"
    )

    col3.metric(
        "Último acesso",
        dados_meu_usuario.get("ultimo_acesso", "—") or "—"
    )

    st.markdown("### Trocar senha")

    nova_senha = st.text_input(
        "Nova senha",
        type="password"
    )

    confirmar_senha = st.text_input(
        "Confirmar nova senha",
        type="password"
    )

    if st.button("🔑 Alterar senha", use_container_width=True):
        if not nova_senha:
            st.error("Informe a nova senha.")

        elif nova_senha != confirmar_senha:
            st.error("As senhas não conferem.")

        else:
            dados_meu_usuario["senha"] = nova_senha

            ok = salvar_usuario_runtime(
                login_atual,
                dados_meu_usuario
            )

            if ok:
                st.success("Senha alterada com sucesso.")
            else:
                st.error("Não foi possível alterar a senha.")


# ============================================================
# LGPD
# ============================================================

with aba_lgpd:
    st.subheader("📜 Termos de uso e LGPD")

    aceite = st.checkbox(
        "Li e aceito os termos de uso e privacidade.",
        value=bool(dados_meu_usuario.get("aceitou_lgpd", False))
    )

    if st.button("Salvar aceite LGPD", use_container_width=True):
        dados_meu_usuario["aceitou_lgpd"] = bool(aceite)

        if aceite:
            dados_meu_usuario["data_aceite_lgpd"] = agora_iso()

        ok = salvar_usuario_runtime(
            login_atual,
            dados_meu_usuario
        )

        if ok:
            st.success("LGPD atualizado.")
            st.rerun()

    st.markdown("---")
    st.subheader("🗑️ Solicitar exclusão da conta")

    motivo_exclusao = st.text_area(
        "Motivo da solicitação"
    )

    confirmar_exclusao = st.checkbox(
        "Confirmo que desejo solicitar a exclusão."
    )

    if st.button("Solicitar exclusão", use_container_width=True):
        if not confirmar_exclusao:
            st.error("Confirme a solicitação.")
        else:
            ok = registrar_solicitacao_exclusao(
                login_atual,
                motivo_exclusao
            )

            if ok:
                st.success("Solicitação registrada.")


# ============================================================
# ADMINISTRAÇÃO
# ============================================================

if eh_admin:
    with aba_admin:
        st.subheader("🛡️ Administração de usuários")

        linhas = []

        for login, dados in usuarios.items():
            linhas.append({
                "Usuário": login,
                "Nome": dados.get("nome", ""),
                "Perfil": dados.get("perfil", ""),
                "E-mail": dados.get("email", ""),
                "Município": dados.get("municipio", ""),
                "Verificado": dados.get("verificado", False),
                "Bloqueado": dados.get("bloqueado", False),
            })

        df_usuarios = pd.DataFrame(linhas)

        st.dataframe(
            df_usuarios,
            use_container_width=True,
            height=400
        )


# ============================================================
# DIAGNÓSTICO
# ============================================================

if eh_admin:
    with aba_diagnostico:
        st.subheader("🧪 Diagnóstico da plataforma")

        st.markdown("### Supabase/PostgreSQL")

        if testar_conexao_supabase is not None:

            if st.button(
                "Testar conexão com Supabase",
                use_container_width=True
            ):
                try:
                    dados = testar_conexao_supabase()

                    st.success("Conexão realizada com sucesso.")

                    st.dataframe(
                        pd.DataFrame(dados),
                        use_container_width=True
                    )

                except Exception as e:
                    st.error("Erro ao conectar.")
                    st.exception(e)

        st.markdown("---")
        st.markdown("### Usuários no Supabase")

        if listar_usuarios_supabase is not None:

            if st.button(
                "Carregar usuários do Supabase",
                use_container_width=True
            ):
                try:
                    dados = listar_usuarios_supabase()

                    st.dataframe(
                        pd.DataFrame(dados),
                        use_container_width=True,
                        height=360
                    )

                except Exception as e:
                    st.error("Erro ao carregar usuários.")
                    st.exception(e)

        st.markdown("---")
        st.markdown("### Migração de usuários")

        confirmar_migracao = st.checkbox(
            "Confirmo a migração dos usuários locais."
        )

        if st.button(
            "Migrar usuários locais para Supabase",
            use_container_width=True
        ):
            if not confirmar_migracao:
                st.error("Confirme antes de continuar.")
            else:
                try:
                    resultado = migrar_usuarios_locais_para_supabase()

                    st.success(
                        f"Migrados: {resultado['migrados']} | "
                        f"Erros: {resultado['erros']}"
                    )

                    st.dataframe(
                        pd.DataFrame(resultado["detalhes"]),
                        use_container_width=True
                    )

                except Exception as e:
                    st.error("Erro na migração.")
                    st.exception(e)

        st.markdown("---")
        st.markdown("### Histórico de uploads")

        if historico_para_dataframe is not None:

            try:
                df_historico = historico_para_dataframe()

                st.dataframe(
                    df_historico,
                    use_container_width=True,
                    height=360
                )

            except Exception as e:
                st.error("Erro ao carregar histórico.")
                st.exception(e)

        confirmar_uploads = st.checkbox(
            "Confirmo a migração do histórico de uploads."
        )

        if st.button(
            "Migrar histórico de uploads",
            use_container_width=True
        ):
            if not confirmar_uploads:
                st.error("Confirme antes de continuar.")
            else:
                try:
                    resultado_uploads = (
                        migrar_historico_uploads_local_para_supabase()
                    )

                    st.success(
                        f"Migrados: {resultado_uploads['migrados']} | "
                        f"Erros: {resultado_uploads['erros']}"
                    )

                    st.dataframe(
                        pd.DataFrame(resultado_uploads["detalhes"]),
                        use_container_width=True
                    )

                except Exception as e:
                    st.error("Erro na migração.")
                    st.exception(e)

        st.markdown("---")
        st.markdown("### Municípios do Brasil — IBGE")

        if importar_municipios_ibge_para_supabase is not None:

            confirmar_importacao = st.checkbox(
                "Confirmo a importação dos municípios IBGE."
            )

            if st.button(
                "Importar municípios do IBGE",
                use_container_width=True
            ):
                if not confirmar_importacao:
                    st.error("Confirme antes de continuar.")
                else:
                    try:
                        resultado = (
                            importar_municipios_ibge_para_supabase()
                        )

                        st.success(
                            f"Importados: {resultado['importados']} | "
                            f"Erros: {resultado['erros']}"
                        )

                        st.dataframe(
                            pd.DataFrame(resultado["detalhes"]),
                            use_container_width=True,
                            height=360
                        )

                    except Exception as e:
                        st.error("Erro na importação.")
                        st.exception(e)

        st.markdown("#### Municípios cadastrados")

        if municipios_para_dataframe is not None:
            try:
                df_municipios = municipios_para_dataframe()

                st.dataframe(
                    df_municipios,
                    use_container_width=True,
                    height=360
                )

            except Exception as e:
                st.error("Erro ao carregar municípios.")
                st.exception(e)

        st.markdown("---")
        st.markdown("### Bases CNES/DATASUS")

        st.info(
            "Atualize aqui as bases de referência do CNES/DATASUS. "
            "Use os arquivos oficiais `tbMunicipio` e `tbEstabelecimento` em formato CSV."
        )

        col_cnes1, col_cnes2 = st.columns(2)

        with col_cnes1:
            arquivo_municipios_cnes = st.file_uploader(
                "Upload tbMunicipio CNES/DATASUS",
                type=["csv"],
                key="upload_municipios_cnes"
            )

            if st.button(
                "Atualizar municípios CNES",
                use_container_width=True
            ):
                if arquivo_municipios_cnes is None:
                    st.error("Envie o arquivo tbMunicipio em CSV.")
                elif importar_municipios_cnes_csv is None:
                    st.error("Função de importação de municípios CNES não localizada.")
                else:
                    with st.spinner("Importando municípios CNES..."):
                        resultado = importar_municipios_cnes_csv(
                            arquivo_municipios_cnes
                        )

                    st.success(
                        f"Importação concluída. "
                        f"Lidos: {resultado['total_lidos']} • "
                        f"Importados/atualizados: {resultado['importados']} • "
                        f"Erros: {resultado['erros']}"
                    )

                    st.dataframe(
                        pd.DataFrame(resultado["detalhes"]),
                        use_container_width=True
                    )

        with col_cnes2:
            arquivo_estabelecimentos_cnes = st.file_uploader(
                "Upload tbEstabelecimento CNES/DATASUS",
                type=["csv"],
                key="upload_estabelecimentos_cnes"
            )

            if st.button(
                "Atualizar estabelecimentos CNES",
                use_container_width=True
            ):
                if arquivo_estabelecimentos_cnes is None:
                    st.error("Envie o arquivo tbEstabelecimento em CSV.")
                elif importar_estabelecimentos_cnes_csv is None:
                    st.error("Função de importação de estabelecimentos CNES não localizada.")
                else:
                    with st.spinner(
                        "Importando estabelecimentos CNES. "
                        "Esse processo pode demorar por causa do tamanho do arquivo..."
                    ):
                        resultado = importar_estabelecimentos_cnes_csv(
                            arquivo_estabelecimentos_cnes
                        )

                    st.success(
                        f"Importação concluída. "
                        f"Lidos: {resultado['total_lidos']} • "
                        f"Importados/atualizados: {resultado['importados']} • "
                        f"Erros: {resultado['erros']}"
                    )

                    st.dataframe(
                        pd.DataFrame(resultado["detalhes"]),
                        use_container_width=True
                    )

        if contar_referencias_cnes is not None:
            try:
                contagens = contar_referencias_cnes()

                c1, c2 = st.columns(2)

                c1.metric(
                    "Municípios CNES cadastrados",
                    contagens.get("municipios_cnes", 0)
                )

                c2.metric(
                    "Unidades CNES cadastradas",
                    contagens.get("unidades_cnes", 0)
                )

            except Exception:
                st.warning("Não foi possível contar as referências CNES.")

        st.markdown("---")

        status_modulos = pd.DataFrame([
            {
                "Módulo": "Autenticação",
                "Status": "Ativo",
                "Observação": "Supabase integrado."
            },
            {
                "Módulo": "Histórico de uploads",
                "Status": "Ativo",
                "Observação": "Persistência híbrida funcionando."
            },
            {
                "Módulo": "Municípios IBGE",
                "Status": "Ativo",
                "Observação": "Importação automática habilitada."
            },
            {
                "Módulo": "CNES/DATASUS",
                "Status": "Ativo",
                "Observação": "Upload e atualização de referências habilitados."
            },
            {
                "Módulo": "Alertas inteligentes",
                "Status": "Ativo",
                "Observação": "Integrado ao Painel Universal."
            },
        ])

        st.dataframe(
            status_modulos,
            use_container_width=True,
            height=280
        )

st.caption("Horizonte Health Intelligence • Configurações")
