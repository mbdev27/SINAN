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
    forcar_novo_aceite_termo_para_todos,
)

from utils.tema import aplicar_tema_streamlit, aplicar_tema_plotly
from utils.termos import VERSAO_TERMO_RESPONSABILIDADE

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

            dados_meu_usuario["nome"] = novo_nome
            dados_meu_usuario["email"] = novo_email
            dados_meu_usuario["municipio"] = municipio
            dados_meu_usuario["instituicao"] = instituicao
            dados_meu_usuario["cargo"] = cargo
            dados_meu_usuario["funcao"] = funcao
            dados_meu_usuario["tema"] = tema

            ok = salvar_usuario_runtime(login_atual, dados_meu_usuario)

            if ok:
                st.success("Dados atualizados com sucesso.")
                st.rerun()
            else:
                st.error("Não foi possível salvar as alterações.")


with aba_seguranca:
    st.subheader("🔐 Segurança e acesso")

    col1, col2, col3 = st.columns(3)

    col1.metric("Perfil", dados_meu_usuario.get("perfil", "Usuário"))
    col2.metric("E-mail verificado", "Sim" if dados_meu_usuario.get("verificado", False) else "Não")
    col3.metric("Último acesso", dados_meu_usuario.get("ultimo_acesso", "—") or "—")

    st.markdown("### Trocar senha")

    nova_senha = st.text_input("Nova senha", type="password")
    confirmar_senha = st.text_input("Confirmar nova senha", type="password")

    if st.button("🔑 Alterar senha", use_container_width=True):
        if not nova_senha:
            st.error("Informe a nova senha.")

        elif nova_senha != confirmar_senha:
            st.error("As senhas não conferem.")

        else:
            dados_meu_usuario["senha"] = nova_senha
            dados_meu_usuario["senha_hash"] = ""
            dados_meu_usuario["requer_troca_senha"] = False

            ok = salvar_usuario_runtime(login_atual, dados_meu_usuario)

            if ok:
                st.success("Senha alterada com sucesso.")
            else:
                st.error("Não foi possível alterar a senha.")


with aba_lgpd:
    st.subheader("📜 Termos de uso e LGPD")

    st.info(
        f"Versão atual do termo: {VERSAO_TERMO_RESPONSABILIDADE}. "
        "Usuários que ainda não aceitaram a versão atual serão obrigados a aceitar no próximo login."
    )

    aceitou = bool(dados_meu_usuario.get("aceitou_lgpd", False))
    versao_aceita = dados_meu_usuario.get("versao_termo_lgpd", "")
    data_aceite = dados_meu_usuario.get("data_aceite_lgpd", "")

    if aceitou and versao_aceita == VERSAO_TERMO_RESPONSABILIDADE:
        st.success(f"Termo atual aceito em: {data_aceite or 'data não registrada'}")
    else:
        st.warning("Você ainda não possui aceite registrado para a versão atual do termo.")

    st.markdown("---")
    st.subheader("🗑️ Solicitar exclusão da conta")

    motivo_exclusao = st.text_area("Motivo da solicitação")
    confirmar_exclusao = st.checkbox("Confirmo que desejo solicitar a exclusão.")

    if st.button("Solicitar exclusão", use_container_width=True):
        if not confirmar_exclusao:
            st.error("Confirme a solicitação.")
        else:
            ok = registrar_solicitacao_exclusao(login_atual, motivo_exclusao)

            if ok:
                st.success("Solicitação registrada.")


if eh_admin:
    with aba_admin:
        st.subheader("🛡️ Administração completa de usuários")

        linhas = []

        for login, dados in usuarios.items():
            linhas.append({
                "Usuário": login,
                "Nome": dados.get("nome", ""),
                "Perfil": dados.get("perfil", ""),
                "E-mail": dados.get("email", ""),
                "Município": dados.get("municipio", ""),
                "Instituição": dados.get("instituicao", ""),
                "Verificado": "Sim" if dados.get("verificado", False) else "Não",
                "Bloqueado": "Sim" if dados.get("bloqueado", False) else "Não",
                "Termo atual": "Sim" if (
                    dados.get("aceitou_lgpd", False)
                    and dados.get("versao_termo_lgpd", "") == VERSAO_TERMO_RESPONSABILIDADE
                ) else "Não",
                "Troca senha": "Sim" if dados.get("requer_troca_senha", False) else "Não",
            })

        df_usuarios = pd.DataFrame(linhas)

        k1, k2, k3, k4, k5 = st.columns(5)

        k1.metric("Total", len(df_usuarios))
        k2.metric("Admins", len(df_usuarios[df_usuarios["Perfil"] == "Admin"]))
        k3.metric("Bloqueados", len(df_usuarios[df_usuarios["Bloqueado"] == "Sim"]))
        k4.metric("Sem termo atual", len(df_usuarios[df_usuarios["Termo atual"] == "Não"]))
        k5.metric("Troca de senha", len(df_usuarios[df_usuarios["Troca senha"] == "Sim"]))

        st.dataframe(df_usuarios, use_container_width=True, height=360)

        st.markdown("---")
        st.subheader("⚙️ Editar usuário existente")

        lista_usuarios = sorted(list(usuarios.keys()))

        usuario_selecionado = st.selectbox(
            "Selecione o usuário",
            lista_usuarios,
            key="admin_usuario_selecionado"
        )

        dados_usuario = dict(usuarios.get(usuario_selecionado, {}))

        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome", value=dados_usuario.get("nome", ""), key="adm_nome")
            email = st.text_input("E-mail", value=dados_usuario.get("email", ""), key="adm_email")
            municipio_admin = st.text_input("Município", value=dados_usuario.get("municipio", ""), key="adm_municipio")
            instituicao_admin = st.text_input("Instituição", value=dados_usuario.get("instituicao", ""), key="adm_instituicao")
            cargo_admin = st.text_input("Cargo", value=dados_usuario.get("cargo", ""), key="adm_cargo")
            funcao_admin = st.text_input("Função", value=dados_usuario.get("funcao", ""), key="adm_funcao")

        with col2:
            perfis = ["Admin", "Gestor", "Técnico", "Demo", "Usuário"]

            perfil_atual_usuario = dados_usuario.get("perfil", "Usuário")

            if perfil_atual_usuario not in perfis:
                perfil_atual_usuario = "Usuário"

            novo_perfil = st.selectbox(
                "Perfil",
                perfis,
                index=perfis.index(perfil_atual_usuario),
                key="adm_perfil"
            )

            tema_atual_admin = dados_usuario.get("tema", "Escuro")

            if tema_atual_admin not in ["Escuro", "Claro", "Automático"]:
                tema_atual_admin = "Escuro"

            tema_admin = st.selectbox(
                "Tema",
                ["Escuro", "Claro", "Automático"],
                index=["Escuro", "Claro", "Automático"].index(tema_atual_admin),
                key="adm_tema"
            )

            verificado = st.checkbox(
                "E-mail verificado",
                value=bool(dados_usuario.get("verificado", False)),
                key="adm_verificado"
            )

            bloqueado = st.checkbox(
                "Usuário bloqueado",
                value=bool(dados_usuario.get("bloqueado", False)),
                key="adm_bloqueado"
            )

            requer_troca_senha = st.checkbox(
                "Exigir troca de senha no próximo login",
                value=bool(dados_usuario.get("requer_troca_senha", False)),
                key="adm_requer_troca_senha"
            )

            senha_manual = st.text_input(
                "Nova senha definida pelo administrador",
                type="password",
                key="adm_senha_manual"
            )

        b1, b2, b3, b4 = st.columns(4)

        with b1:
            if st.button("💾 Salvar alterações", use_container_width=True):
                dados_usuario["nome"] = nome
                dados_usuario["email"] = email
                dados_usuario["municipio"] = municipio_admin
                dados_usuario["instituicao"] = instituicao_admin
                dados_usuario["cargo"] = cargo_admin
                dados_usuario["funcao"] = funcao_admin
                dados_usuario["perfil"] = novo_perfil
                dados_usuario["tema"] = tema_admin
                dados_usuario["verificado"] = verificado
                dados_usuario["bloqueado"] = bloqueado
                dados_usuario["requer_troca_senha"] = requer_troca_senha

                if senha_manual:
                    dados_usuario["senha"] = senha_manual
                    dados_usuario["senha_hash"] = ""
                    dados_usuario["requer_troca_senha"] = False

                ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

                if ok:
                    st.success("Usuário atualizado.")
                    st.rerun()
                else:
                    st.error("Não foi possível salvar.")

        with b2:
            if st.button("🔑 Solicitar troca de senha", use_container_width=True):
                dados_usuario["requer_troca_senha"] = True
                ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

                if ok:
                    st.success("Troca de senha exigida no próximo login.")
                    st.rerun()
                else:
                    st.error("Não foi possível solicitar troca de senha.")

        with b3:
            if st.button("📜 Exigir novo aceite do termo", use_container_width=True):
                dados_usuario["aceitou_lgpd"] = False
                dados_usuario["data_aceite_lgpd"] = ""
                dados_usuario["versao_termo_lgpd"] = ""

                ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

                if ok:
                    st.success("Novo aceite será solicitado no próximo login.")
                    st.rerun()
                else:
                    st.error("Não foi possível atualizar termo.")

        with b4:
            if usuario_selecionado != login_atual:
                if st.button("🗑️ Excluir usuário", use_container_width=True):
                    ok = excluir_usuario_runtime(usuario_selecionado)

                    if ok:
                        st.success("Usuário excluído.")
                        st.rerun()
                    else:
                        st.error("Não foi possível excluir.")
            else:
                st.info("Você não pode excluir seu próprio usuário.")

        st.markdown("---")
        st.subheader("➕ Criar novo usuário")

        with st.form("form_criar_usuario_admin", clear_on_submit=True):
            novo_nome_admin = st.text_input("Nome completo")
            novo_email_admin = st.text_input("E-mail")
            novo_usuario_admin = st.text_input("Usuário")
            novo_municipio_admin = st.text_input("Município")
            novo_instituicao_admin = st.text_input("Instituição")
            novo_cargo_admin = st.text_input("Cargo")
            novo_funcao_admin = st.text_input("Função")

            novo_perfil_admin = st.selectbox(
                "Perfil do novo usuário",
                ["Admin", "Gestor", "Técnico", "Demo", "Usuário"],
                index=3
            )

            senha_inicial = st.text_input("Senha inicial", type="password")

            novo_verificado = st.checkbox("Criar como e-mail verificado", value=True)
            novo_requer_troca = st.checkbox("Exigir troca de senha no primeiro login", value=True)
            novo_bloqueado = st.checkbox("Criar bloqueado", value=False)

            criar = st.form_submit_button("Criar usuário", use_container_width=True)

            if criar:
                usuarios_existentes = carregar_usuarios()
                novo_usuario_admin = str(novo_usuario_admin).strip()

                if (
                    not novo_nome_admin
                    or not novo_email_admin
                    or not novo_usuario_admin
                    or not senha_inicial
                ):
                    st.error("Preencha nome, e-mail, usuário e senha.")

                elif "@" not in novo_email_admin:
                    st.error("Informe um e-mail válido.")

                elif novo_usuario_admin in usuarios_existentes:
                    st.error("Este usuário já existe.")

                else:
                    ok = salvar_usuario_runtime(
                        novo_usuario_admin,
                        {
                            "senha": senha_inicial,
                            "nome": novo_nome_admin,
                            "perfil": novo_perfil_admin,
                            "email": novo_email_admin,
                            "municipio": novo_municipio_admin,
                            "instituicao": novo_instituicao_admin,
                            "cargo": novo_cargo_admin,
                            "funcao": novo_funcao_admin,
                            "tema": "Escuro",
                            "aceitou_lgpd": False,
                            "data_aceite_lgpd": "",
                            "versao_termo_lgpd": "",
                            "requer_troca_senha": novo_requer_troca,
                            "avatar_path": "",
                            "ultimo_acesso": "",
                            "historico_acessos": [],
                            "verificado": novo_verificado,
                            "bloqueado": novo_bloqueado,
                        }
                    )

                    if ok:
                        st.success("Usuário criado com sucesso. O termo será exigido no primeiro login.")
                        st.rerun()
                    else:
                        st.error("Não foi possível criar o usuário.")

        st.markdown("---")
        st.subheader("📜 Termo de responsabilidade")

        st.warning(
            "Use esta ação quando houver nova versão do termo ou quando desejar "
            "obrigar todos os usuários a aceitarem novamente no próximo login."
        )

        confirmar_forcar_termo = st.checkbox(
            "Confirmo que desejo exigir novo aceite do termo para todos os usuários."
        )

        if st.button("Forçar aceite do termo para todos", use_container_width=True):
            if not confirmar_forcar_termo:
                st.error("Confirme a ação antes de continuar.")
            else:
                total = forcar_novo_aceite_termo_para_todos()
                st.success(f"Novo aceite será exigido para {total} usuário(s) no próximo login.")
                st.rerun()

        st.markdown("---")
        st.subheader("📄 Solicitações de exclusão")

        solicitacoes = carregar_solicitacoes_exclusao()

        if solicitacoes:
            df_solicitacoes = pd.DataFrame(solicitacoes)
            st.dataframe(df_solicitacoes, use_container_width=True, height=280)

            indice = st.number_input(
                "Índice da solicitação para atualizar",
                min_value=0,
                max_value=max(len(solicitacoes) - 1, 0),
                value=0
            )

            status = st.selectbox(
                "Novo status",
                ["Pendente", "Em análise", "Concluída", "Negada"]
            )

            if st.button("Atualizar status da solicitação", use_container_width=True):
                ok = atualizar_status_solicitacao_exclusao(int(indice), status)

                if ok:
                    st.success("Solicitação atualizada.")
                    st.rerun()
                else:
                    st.error("Não foi possível atualizar.")
        else:
            st.info("Nenhuma solicitação de exclusão registrada.")

        st.markdown("---")
        st.subheader("📥 Exportar usuários")

        csv_usuarios = df_usuarios.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📄 Baixar lista de usuários",
            data=csv_usuarios,
            file_name="usuarios_horizonte.csv",
            mime="text/csv",
            use_container_width=True
        )


if eh_admin:
    with aba_diagnostico:
        st.subheader("🧪 Diagnóstico da plataforma")

        st.markdown("### Supabase/PostgreSQL")

        if testar_conexao_supabase is not None:
            if st.button("Testar conexão com Supabase", use_container_width=True):
                try:
                    dados = testar_conexao_supabase()
                    st.success("Conexão realizada com sucesso.")
                    st.dataframe(pd.DataFrame(dados), use_container_width=True)

                except Exception as e:
                    st.error("Erro ao conectar.")
                    st.exception(e)

        st.markdown("---")
        st.markdown("### Usuários no Supabase")

        if listar_usuarios_supabase is not None:
            if st.button("Carregar usuários do Supabase", use_container_width=True):
                try:
                    dados = listar_usuarios_supabase()
                    st.dataframe(pd.DataFrame(dados), use_container_width=True, height=360)

                except Exception as e:
                    st.error("Erro ao carregar usuários.")
                    st.exception(e)

        st.markdown("---")
        st.markdown("### Migração de usuários")

        confirmar_migracao = st.checkbox("Confirmo a migração dos usuários locais.")

        if st.button("Migrar usuários locais para Supabase", use_container_width=True):
            if not confirmar_migracao:
                st.error("Confirme antes de continuar.")
            else:
                try:
                    resultado = migrar_usuarios_locais_para_supabase()

                    st.success(
                        f"Migrados: {resultado['migrados']} | "
                        f"Erros: {resultado['erros']}"
                    )

                    st.dataframe(pd.DataFrame(resultado["detalhes"]), use_container_width=True)

                except Exception as e:
                    st.error("Erro na migração.")
                    st.exception(e)

        st.markdown("---")
        st.markdown("### Histórico de uploads")

        if historico_para_dataframe is not None:
            try:
                df_historico = historico_para_dataframe()
                st.dataframe(df_historico, use_container_width=True, height=360)

            except Exception as e:
                st.error("Erro ao carregar histórico.")
                st.exception(e)

        confirmar_uploads = st.checkbox("Confirmo a migração do histórico de uploads.")

        if st.button("Migrar histórico de uploads", use_container_width=True):
            if not confirmar_uploads:
                st.error("Confirme antes de continuar.")
            else:
                try:
                    resultado_uploads = migrar_historico_uploads_local_para_supabase()

                    st.success(
                        f"Migrados: {resultado_uploads['migrados']} | "
                        f"Erros: {resultado_uploads['erros']}"
                    )

                    st.dataframe(pd.DataFrame(resultado_uploads["detalhes"]), use_container_width=True)

                except Exception as e:
                    st.error("Erro na migração.")
                    st.exception(e)

        st.markdown("---")
        st.markdown("### Municípios do Brasil — IBGE")

        if importar_municipios_ibge_para_supabase is not None:
            confirmar_importacao = st.checkbox("Confirmo a importação dos municípios IBGE.")

            if st.button("Importar municípios do IBGE", use_container_width=True):
                if not confirmar_importacao:
                    st.error("Confirme antes de continuar.")
                else:
                    try:
                        resultado = importar_municipios_ibge_para_supabase()

                        st.success(
                            f"Importados: {resultado['importados']} | "
                            f"Erros: {resultado['erros']}"
                        )

                        st.dataframe(pd.DataFrame(resultado["detalhes"]), use_container_width=True, height=360)

                    except Exception as e:
                        st.error("Erro na importação.")
                        st.exception(e)

        st.markdown("#### Municípios cadastrados")

        if municipios_para_dataframe is not None:
            try:
                df_municipios = municipios_para_dataframe()
                st.dataframe(df_municipios, use_container_width=True, height=360)

            except Exception as e:
                st.error("Erro ao carregar municípios.")
                st.exception(e)

        st.markdown("---")
        st.markdown("### Bases CNES/DATASUS")

        st.warning(
            "A importação de estabelecimentos CNES pode envolver arquivos grandes. "
            "O processamento ocorre em blocos para reduzir consumo de memória."
        )

        col_cnes1, col_cnes2 = st.columns(2)

        with col_cnes1:
            arquivo_municipios_cnes = st.file_uploader(
                "Upload tbMunicipio CNES/DATASUS",
                type=["csv"],
                key="upload_municipios_cnes"
            )

            if st.button("Atualizar municípios CNES", use_container_width=True):
                if arquivo_municipios_cnes is None:
                    st.error("Envie o arquivo tbMunicipio em CSV.")
                elif importar_municipios_cnes_csv is None:
                    st.error("Função de importação de municípios CNES não localizada.")
                else:
                    with st.spinner("Importando municípios CNES..."):
                        resultado = importar_municipios_cnes_csv(arquivo_municipios_cnes)

                    st.success(
                        f"Lidos: {resultado['total_lidos']} • "
                        f"Importados/atualizados: {resultado['importados']} • "
                        f"Erros: {resultado['erros']}"
                    )

                    st.dataframe(pd.DataFrame(resultado["detalhes"]), use_container_width=True)

        with col_cnes2:
            arquivo_estabelecimentos_cnes = st.file_uploader(
                "Upload tbEstabelecimento CNES/DATASUS",
                type=["csv"],
                key="upload_estabelecimentos_cnes"
            )

            if arquivo_estabelecimentos_cnes is not None:
                tamanho_mb = round(arquivo_estabelecimentos_cnes.size / (1024 * 1024), 2)
                st.caption(f"Tamanho do arquivo: {tamanho_mb} MB")

            if st.button("Atualizar estabelecimentos CNES", use_container_width=True):
                if arquivo_estabelecimentos_cnes is None:
                    st.error("Envie o arquivo tbEstabelecimento em CSV.")
                elif importar_estabelecimentos_cnes_csv is None:
                    st.error("Função de importação de estabelecimentos CNES não localizada.")
                else:
                    with st.spinner("Importando estabelecimentos CNES..."):
                        resultado = importar_estabelecimentos_cnes_csv(arquivo_estabelecimentos_cnes)

                    st.success(
                        f"Lidos: {resultado['total_lidos']} • "
                        f"Importados/atualizados: {resultado['importados']} • "
                        f"Erros: {resultado['erros']}"
                    )

                    st.dataframe(pd.DataFrame(resultado["detalhes"]), use_container_width=True)

        if contar_referencias_cnes is not None:
            try:
                contagens = contar_referencias_cnes()

                st.markdown("---")
                st.markdown("### Referências CNES carregadas")

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
                "Observação": "Supabase integrado com aceite obrigatório de termo."
            },
            {
                "Módulo": "Gestão de usuários",
                "Status": "Ativo",
                "Observação": "Administração completa disponível para administradores."
            },
            {
                "Módulo": "Histórico de uploads",
                "Status": "Ativo",
                "Observação": "Persistência híbrida funcionando."
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

        st.dataframe(status_modulos, use_container_width=True, height=280)

st.caption("Horizonte Health Intelligence • Configurações")
