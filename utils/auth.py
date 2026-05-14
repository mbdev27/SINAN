import json
    except Exception:
        return False


# ============================================================
# AVATAR
# ============================================================


def salvar_avatar_usuario(usuario, arquivo):
    pasta = Path("uploads/avatars")
    pasta.mkdir(parents=True, exist_ok=True)

    extensao = arquivo.name.split(".")[-1]

    caminho = pasta / f"{usuario}.{extensao}"

    with open(caminho, "wb") as f:
        f.write(arquivo.getbuffer())

    return str(caminho)


# ============================================================
# LGPD / EXCLUSÃO
# ============================================================


def carregar_solicitacoes_exclusao():
    if not ARQUIVO_SOLICITACOES.exists():
        return []

    with open(ARQUIVO_SOLICITACOES, "r", encoding="utf-8") as f:
        return json.load(f)



def salvar_solicitacoes_exclusao(dados):
    with open(ARQUIVO_SOLICITACOES, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)



def registrar_solicitacao_exclusao(usuario, motivo):
    usuarios = carregar_usuarios()

    if usuario not in usuarios:
        return False

    dados_usuario = usuarios[usuario]

    solicitacoes = carregar_solicitacoes_exclusao()

    solicitacoes.append({
        "usuario": usuario,
        "nome": dados_usuario.get("nome", ""),
        "email": dados_usuario.get("email", ""),
        "perfil": dados_usuario.get("perfil", "Usuário"),
        "motivo": motivo,
        "status": "Pendente",
        "data_solicitacao": agora_iso(),
    })

    salvar_solicitacoes_exclusao(solicitacoes)

    return True



def atualizar_status_solicitacao_exclusao(indice, status):
    solicitacoes = carregar_solicitacoes_exclusao()

    if indice >= len(solicitacoes):
        return False

    solicitacoes[indice]["status"] = status
    solicitacoes[indice]["data_atualizacao"] = agora_iso()

    salvar_solicitacoes_exclusao(solicitacoes)

    return True
