from datetime import datetime, timezone


VERSAO_TERMO_RESPONSABILIDADE = "2026.05.29"


TERMO_RESPONSABILIDADE_SIGILO = """
TERMO DE RESPONSABILIDADE, SIGILO E USO ACEITÁVEL DE DADOS SENSÍVEIS

Pelo presente instrumento, O USUÁRIO, ao realizar o login e acessar o ambiente restrito da plataforma da Horizonte Soluções Tecnológicas, declara ter ciência, concordar e se comprometer com as diretrizes de privacidade e confidencialidade aqui estabelecidas, em conformidade com a Lei Geral de Proteção de Dados Pessoais (LGPD - Lei nº 13.709/2018).

1. DO OBJETO E DA NATUREZA DOS DADOS

1.1. O USUÁRIO reconhece que, por meio desta plataforma, terá acesso a dados, relatórios, informações e indicadores que contêm ou podem conter Dados Pessoais Sensíveis (conforme o Art. 5º, inciso II, da LGPD), incluindo, mas não se limitando a, dados referentes à saúde, histórico clínico, notificações epidemiológicas (como bases DBF/SINAN) e informações biométricas ou genéticas de cidadãos.

1.2. O acesso a essas informações é concedido única e exclusivamente para a finalidade de execução de políticas públicas, auditoria epidemiológica, gestão em saúde e tomada de decisão institucional, sendo terminantemente proibido o uso para fins particulares, comerciais ou discriminatórios.

2. DAS OBRIGAÇÕES DE CONFIDENCIALIDADE E SIGILO

2.1. O USUÁRIO obriga-se a manter o mais absoluto sigilo sobre quaisquer dados pessoais e sensíveis aos quais tenha acesso na plataforma, não podendo revelá-los, reproduzi-los, publicá-los ou compartilhá-los com terceiros não autorizados, seja por meio físico, digital, verbal ou qualquer outro.

2.2. A obrigação de sigilo assumida neste termo é contínua e permanecerá em vigor mesmo após o encerramento do vínculo do USUÁRIO com a instituição pública ou com a plataforma Horizonte.

3. DO USO ACEITÁVEL E DA SEGURANÇA DA INFORMAÇÃO

Para garantir a integridade e a segurança do ambiente, o USUÁRIO compromete-se expressamente a:

a) Não compartilhar, emprestar ou divulgar suas credenciais de acesso, login e senha, a terceiros, reconhecendo que seu uso é pessoal e intransferível.

b) Não realizar o download, extração, cópia, inclusive capturas de tela, ou exportação de bases de dados contendo informações nominais ou identificáveis fora dos fluxos estritamente autorizados pela sua instituição.

c) Acessar a plataforma preferencialmente através de equipamentos e redes institucionais seguras, evitando redes públicas ou computadores de uso compartilhado sem a devida higienização, como logoff após o uso.

d) Notificar imediatamente os administradores da plataforma e o Encarregado de Dados, DPO, da sua instituição caso suspeite de qualquer vazamento de senha, acesso indevido ou falha de segurança.

4. DAS RESPONSABILIDADES E SANÇÕES

4.1. O USUÁRIO tem ciência de que todos os seus acessos, consultas e ações dentro da plataforma são registrados, logs, para fins de auditoria de segurança e rastreabilidade.

4.2. O descumprimento das condições estabelecidas neste Termo caracteriza infração gravíssima e sujeita o infrator a:

a) Bloqueio imediato e preventivo de acesso à plataforma.

b) Sanções administrativas e disciplinares no âmbito de sua instituição.

c) Responsabilização civil por danos materiais ou morais causados a titulares de dados ou ao Estado.

d) Responsabilização penal, quando a conduta configurar crime tipificado na legislação brasileira, como violação de sigilo funcional, Art. 325 do Código Penal, ou invasão de dispositivo informático, Art. 154-A do Código Penal.

5. DO CONSENTIMENTO E ACEITE

Ao prosseguir com o acesso e utilizar a plataforma da Horizonte Soluções Tecnológicas, o USUÁRIO declara ter lido, compreendido e aceitado integralmente todas as disposições deste Termo de Responsabilidade e Sigilo, submetendo-se às suas condições sob as penas da lei.


def agora_aceite_iso():
    return datetime.now(timezone.utc).isoformat()


def texto_resumido_aceite():
    return (
        "Declaro que li, compreendi e concordo integralmente com o Termo de "
        "Responsabilidade, Sigilo e Uso Aceitável de Dados Sensíveis da Horizonte."
    )
