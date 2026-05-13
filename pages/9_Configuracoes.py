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
    "Horizonte Health Intelligence • Conta, preferências, LGPD e administração de usuários."
)


usuarios = carregar_usuarios()

if login_atual not in usuarios:
    st.error("Usuário atual não localizado na base.")
    st.stop()


dados_meu_usuario = dict(usuarios[login_atual])


aba_conta, aba_seguranca, aba_lgpd, aba_admin = st.tabs([
    "👤 Minha conta",
    "🔐 Segurança e acesso",
    "📜 LGPD",
    "🛡️ Administração" if eh_admin else "ℹ️ Administração",
])


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

        tema = st.selectbox(
            "Tema preferido",
            ["Escuro", "Claro", "Automático"],
            index=["Escuro", "Claro", "Automático"].index(
                dados_meu_usuario.get("tema", "Escuro")
                if dados_meu_usuario.get("tema", "Escuro") in ["Escuro", "Claro", "Automático"]
                else "Escuro"
            )
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
                st.session_state["nome_usuario"] = novo_nome
                st.session_state["tema_usuario"] = tema
                st.success("Dados atualizados com sucesso.")
                st.rerun()
            else:
                st.error("Não foi possível salvar as alterações.")


with aba_seguranca:
    st.subheader("🔐 Segurança e acesso")

    col1, col2, col3 = st.columns(3)

    col1.metric("Perfil", dados_meu_usuario.get("perfil", "Usuário"))
    col2.metric(
        "E-mail verificado",
        "Sim" if dados_meu_usuario.get("verificado", False) else "Não"
    )
    col3.metric(
        "Último acesso",
        dados_meu_usuario.get("ultimo_acesso", "—") or "—"
    )

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

            ok = salvar_usuario_runtime(login_atual, dados_meu_usuario)

            if ok:
                st.success("Senha alterada com sucesso.")
            else:
                st.error("Não foi possível alterar a senha.")

    st.markdown("### Histórico de acessos")

    historico = dados_meu_usuario.get("historico_acessos", [])

    if historico:
        st.dataframe(
            pd.DataFrame({"Data/hora de acesso": historico[::-1]}),
            use_container_width=True,
            height=300
        )
    else:
        st.info("Ainda não há histórico de acesso registrado.")


with aba_lgpd:
    st.subheader("📜 Termos de uso e LGPD")

    st.info(
        "Esta plataforma trata dados operacionais e epidemiológicos para fins de "
        "análise, auditoria, qualificação da informação e apoio à decisão em saúde pública."
    )

    aceitou_lgpd = dados_meu_usuario.get("aceitou_lgpd", False)
    data_aceite = dados_meu_usuario.get("data_aceite_lgpd", "")

    if aceitou_lgpd:
        st.success(f"Termo aceito. Data do aceite: {data_aceite or 'não registrada'}")
    else:
        st.warning("Você ainda não registrou aceite do termo de uso/LGPD.")

    aceite = st.checkbox(
        "Li e aceito os termos de uso, privacidade e tratamento de dados da plataforma.",
        value=bool(aceitou_lgpd)
    )

    if st.button("✅ Salvar aceite LGPD", use_container_width=True):
        dados_meu_usuario["aceitou_lgpd"] = bool(aceite)

        if aceite and not dados_meu_usuario.get("data_aceite_lgpd"):
            dados_meu_usuario["data_aceite_lgpd"] = agora_iso()

        if not aceite:
            dados_meu_usuario["data_aceite_lgpd"] = ""

        ok = salvar_usuario_runtime(login_atual, dados_meu_usuario)

        if ok:
            st.success("Preferência de LGPD salva.")
            st.rerun()
        else:
            st.error("Não foi possível salvar.")

    st.markdown("---")
    st.subheader("🗑️ Solicitar exclusão da conta")

    motivo_exclusao = st.text_area(
        "Motivo da solicitação",
        placeholder="Descreva brevemente o motivo da solicitação."
    )

    confirmar_exclusao = st.checkbox(
        "Confirmo que desejo solicitar a exclusão da minha conta."
    )

    if st.button("Solicitar exclusão da conta", use_container_width=True):
        if not confirmar_exclusao:
            st.error("Confirme a solicitação antes de continuar.")
        else:
            ok = registrar_solicitacao_exclusao(login_atual, motivo_exclusao)

            if ok:
                st.success("Solicitação registrada. Um administrador deverá avaliar o pedido.")
            else:
                st.error("Não foi possível registrar a solicitação.")


with aba_admin:
    if not eh_admin:
        st.info("A administração de usuários é restrita a perfis de administrador.")
        st.stop()

    st.subheader("🛡️ Administração de usuários")

    linhas = []

    for login, dados in usuarios.items():
        linhas.append({
            "Usuário": login,
            "Nome": dados.get("nome", ""),
            "E-mail": dados.get("email", ""),
            "Município": dados.get("municipio", ""),
            "Instituição": dados.get("instituicao", ""),
            "Cargo": dados.get("cargo", ""),
            "Perfil": dados.get("perfil", "Usuário"),
            "Último acesso": dados.get("ultimo_acesso", ""),
            "LGPD": "✅ Sim" if dados.get("aceitou_lgpd", False) else "❌ Não",
            "Verificado": "✅ Sim" if dados.get("verificado", False) else "❌ Não",
            "Bloqueado": "🔒 Sim" if dados.get("bloqueado", False) else "🔓 Não",
        })

    df_usuarios = pd.DataFrame(linhas)

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Total de usuários", len(df_usuarios))
    k2.metric("Administradores", len(df_usuarios[df_usuarios["Perfil"] == "Admin"]))
    k3.metric("Bloqueados", len(df_usuarios[df_usuarios["Bloqueado"] == "🔒 Sim"]))
    k4.metric("Sem LGPD", len(df_usuarios[df_usuarios["LGPD"] == "❌ Não"]))

    st.dataframe(
        df_usuarios,
        use_container_width=True,
        height=420
    )

    st.markdown("---")
    st.subheader("⚙️ Editar usuário")

    lista_usuarios = list(usuarios.keys())

    usuario_selecionado = st.selectbox(
        "Selecione o usuário",
        lista_usuarios
    )

    dados_usuario = dict(usuarios[usuario_selecionado])

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input(
            "Nome do usuário selecionado",
            value=dados_usuario.get("nome", "")
        )

        email = st.text_input(
            "E-mail do usuário selecionado",
            value=dados_usuario.get("email", "")
        )

        municipio_admin = st.text_input(
            "Município do usuário",
            value=dados_usuario.get("municipio", "")
        )

        instituicao_admin = st.text_input(
            "Instituição do usuário",
            value=dados_usuario.get("instituicao", "")
        )

        cargo_admin = st.text_input(
            "Cargo do usuário",
            value=dados_usuario.get("cargo", "")
        )

        funcao_admin = st.text_input(
            "Função do usuário",
            value=dados_usuario.get("funcao", "")
        )

        perfis = ["Admin", "Gestor", "Técnico", "Demo", "Usuário"]

        perfil = dados_usuario.get("perfil", "Usuário")

        if perfil not in perfis:
            perfil = "Usuário"

        novo_perfil = st.selectbox(
            "Perfil",
            perfis,
            index=perfis.index(perfil)
        )

    with col2:
        verificado = st.checkbox(
            "E-mail verificado",
            value=bool(dados_usuario.get("verificado", False))
        )

        bloqueado = st.checkbox(
            "Usuário bloqueado",
            value=bool(dados_usuario.get("bloqueado", False))
        )

        lgpd_admin = st.checkbox(
            "LGPD aceita",
            value=bool(dados_usuario.get("aceitou_lgpd", False))
        )

        tema_admin = st.selectbox(
            "Tema do usuário",
            ["Escuro", "Claro", "Automático"],
            index=["Escuro", "Claro", "Automático"].index(
                dados_usuario.get("tema", "Escuro")
                if dados_usuario.get("tema", "Escuro") in ["Escuro", "Claro", "Automático"]
                else "Escuro"
            )
        )

        senha_manual = st.text_input(
            "Nova senha manual",
            type="password"
        )

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("💾 Salvar usuário", use_container_width=True):
            dados_usuario["nome"] = nome
            dados_usuario["email"] = email
            dados_usuario["municipio"] = municipio_admin
            dados_usuario["instituicao"] = instituicao_admin
            dados_usuario["cargo"] = cargo_admin
            dados_usuario["funcao"] = funcao_admin
            dados_usuario["perfil"] = novo_perfil
            dados_usuario["verificado"] = verificado
            dados_usuario["bloqueado"] = bloqueado
            dados_usuario["aceitou_lgpd"] = lgpd_admin
            dados_usuario["tema"] = tema_admin

            if lgpd_admin and not dados_usuario.get("data_aceite_lgpd"):
                dados_usuario["data_aceite_lgpd"] = agora_iso()

            if senha_manual:
                dados_usuario["senha"] = senha_manual

            ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

            if ok:
                st.success("Usuário atualizado.")
                st.rerun()
            else:
                st.error("Não foi possível salvar.")

    with b2:
        if st.button("🔓 Desbloquear e verificar", use_container_width=True):
            dados_usuario["bloqueado"] = False
            dados_usuario["verificado"] = True

            ok = salvar_usuario_runtime(usuario_selecionado, dados_usuario)

            if ok:
                st.success("Usuário desbloqueado e verificado.")
                st.rerun()
            else:
                st.error("Não foi possível atualizar.")

    with b3:
        if usuario_selecionado != login_atual:
            if st.button("🗑️ Excluir usuário", use_container_width=True):
                ok = excluir_usuario_runtime(usuario_selecionado)

                if ok:
                    st.success("Usuário excluído.")
                    st.rerun()
                else:
                    st.warning("Não foi possível excluir.")
        else:
            st.info("Você não pode excluir o próprio usuário.")

    st.markdown("---")
    st.subheader("➕ Criar usuário manualmente")

    with st.form("form_criar_usuario_admin", clear_on_submit=True):
        novo_nome_admin = st.text_input("Nome completo")
        novo_email_admin = st.text_input("E-mail")
        novo_usuario_admin = st.text_input("Usuário")
        novo_municipio_admin = st.text_input("Município")
        novo_instituicao_admin = st.text_input("Instituição")
        novo_cargo_admin = st.text_input("Cargo")
        novo_funcao_admin = st.text_input("Função")

        novo_perfil_admin = st.selectbox(
            "Perfil",
            ["Admin", "Gestor", "Técnico", "Demo", "Usuário"],
            index=3
        )

        senha_inicial = st.text_input("Senha inicial", type="password")

        criar = st.form_submit_button("Criar usuário", use_container_width=True)

        if criar:
            usuarios_existentes = carregar_usuarios()
            novo_usuario_admin = str(novo_usuario_admin).strip()

            if not novo_nome_admin or not novo_email_admin or not novo_usuario_admin or not senha_inicial:
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
                        "avatar_path": "",
                        "ultimo_acesso": "",
                        "historico_acessos": [],
                        "verificado": True,
                        "bloqueado": False,
                    }
                )

                if ok:
                    st.success("Usuário criado com sucesso.")
                    st.rerun()
                else:
                    st.error("Não foi possível criar o usuário.")

    st.markdown("---")
    st.subheader("📄 Solicitações de exclusão")

    solicitacoes = carregar_solicitacoes_exclusao()

    if solicitacoes:
        df_solicitacoes = pd.DataFrame(solicitacoes)

        st.dataframe(
            df_solicitacoes,
            use_container_width=True,
            height=300
        )

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


st.caption("Horizonte Health Intelligence • Configurações")
