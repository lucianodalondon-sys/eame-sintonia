#!/usr/bin/env python3
"""
FALHAS — a única língua em que o SINTONIA SCRAP diz por que uma coleta não trouxe dado.

Por que existe: até aqui cada rota tinha o próprio vocabulário. A rota paga sabia
distinguir `PARSER_FAILURE` de `PLATFORM_FAILURE` — e essa distinção, que é a mais
valiosa que esta casa produziu sobre coleta, só funcionava se o caminho passasse pela
Apify. A rota gratuita colapsava tudo em `FAILED`. O navegador falava `LOGIN_WALL`.
A sessão falava `SESSION_EXPIRED`. Ninguém conseguia somar.

    ERRO NÃO É ZERO.
    BLOCKED NÃO É EMPTY.
    AUTH EXPIRED NÃO É NO CONTENT.
    PARSER QUEBRADO NÃO É FONTE VAZIA.
    ROTA CAÍDA NÃO É FONTE CAÍDA.

AS TRÊS CAMADAS — E POR QUE ELAS PRECISAM SER TRÊS
----------------------------------------------------
Um estado não diz só "deu errado". Ele diz DE QUEM é o problema, e isso muda o que se
faz a seguir e o que se pode afirmar sobre a fonte:

    SOURCE      a fonte em si. Sumiu, morreu, respondeu vazio.
    ROUTE       o caminho até ela. Quota acabou, sessão venceu, termo proíbe.
    EXECUTOR    a nossa ferramenta. Chrome não subiu, ator não existe, parser quebrou.

Os três exemplos que obrigaram esta separação, todos medidos nesta casa:

    YouTube vivo + quota da Data API esgotada
        -> SOURCE=HEALTHY, ROUTE=UNAVAILABLE. Amanhã volta sozinho.
    YouTube vivo + sessão do navegador vencida
        -> SOURCE=HEALTHY, ROUTE=UNHEALTHY. Precisa de gente, uma vez.
    Fonte respondeu 200 e o parser não achou os campos
        -> SOURCE=HEALTHY, EXECUTOR=BROKEN. É defeito NOSSO, e ninguém avisa.

O terceiro é o caro. Sem ele, coletor quebrado vira "a fonte está vazia", e a casa
publica um zero que não mediu nada. `degrada_fonte()` existe só para impedir isso.

A FLAG `esperado` — O BIT QUE SEPARA NOTÍCIA DE DEFEITO
--------------------------------------------------------
`esperado=True` quer dizer "isto é comportamento do mundo, não defeito nosso": a
plataforma recusou, a quota acabou, o termo proíbe, não havia conteúdo. Sai no
relatório e ninguém é acordado.

`esperado=False` quer dizer "alguém precisa olhar": o parser não achou o campo, o
contrato mudou, o executor sumiu. É a única classe que pede pessoa.

O vocabulário abaixo é o MENOR que preserva as diferenças que os módulos desta casa
JÁ faziam. Cada estado carrega, no campo `absorve`, o nome antigo que ele substitui —
para que a migração seja conferível e não uma renomeação de fé.
"""

# ══════════════════════════════════════════════════════════════════════════
# CAMADAS
# ══════════════════════════════════════════════════════════════════════════
SOURCE = 'SOURCE'
ROUTE = 'ROUTE'
EXECUTOR = 'EXECUTOR'
NENHUMA = 'NENHUMA'          # nada quebrou — houve resultado, ou zero legítimo

CAMADAS = (SOURCE, ROUTE, EXECUTOR, NENHUMA)

# Saúde por camada.
HEALTHY = 'HEALTHY'
UNAVAILABLE = 'UNAVAILABLE'      # existe, não dá para usar agora (quota, teto, termo)
UNHEALTHY = 'UNHEALTHY'          # existe, está doente (sessão vencida, 5xx)
BROKEN = 'BROKEN'                # é nosso e está quebrado (parser, contrato)
GONE = 'GONE'                    # não existe mais
DESCONHECIDA = 'UNKNOWN'


class Estado:
    """Uma linha do vocabulário. Imutável de fato: ninguém deve alterá-la em runtime."""

    __slots__ = ('nome', 'camada', 'esperado', 'saude', 'rotaciona', 'retentavel', 'absorve', 'nota')

    def __init__(self, nome, camada, esperado, saude, rotaciona, retentavel, absorve, nota):
        self.nome = nome
        self.camada = camada
        self.esperado = esperado
        self.saude = saude
        self.rotaciona = rotaciona          # trocar credencial/token adianta?
        self.retentavel = retentavel        # repetir o MESMO pedido adianta?
        self.absorve = absorve              # nomes antigos que este estado substitui
        self.nota = nota

    def __repr__(self):
        return 'Estado(%s)' % self.nome


def _e(nome, camada, esperado, saude, rotaciona, retentavel, absorve, nota):
    return Estado(nome, camada, esperado, saude, rotaciona, retentavel, tuple(absorve), nota)


# ══════════════════════════════════════════════════════════════════════════
# O VOCABULÁRIO
# ══════════════════════════════════════════════════════════════════════════
_TABELA = [
    # ── NÃO É FALHA ────────────────────────────────────────────────────────
    _e('OK', NENHUMA, True, HEALTHY, False, False,
       ['OK'], 'a rota respondeu e trouxe pelo menos um objeto. É o único estado '
              'que autoriza contar coleta como feita.'),
    _e('ZERO_RESULTS', NENHUMA, True, HEALTHY, False, False,
       ['ZERO_RESULTS', 'SOURCE_EMPTY', 'REQUESTED_EMPTY'],
       'a fonte respondeu e não tinha nada. É MEDIÇÃO, não falha — e é por isso que '
       'a camada é NENHUMA e a saúde é HEALTHY. Pedida e vazia é um ESTADO.'),

    # ── NÃO CHEGAMOS A TENTAR ──────────────────────────────────────────────
    _e('NOT_APPLICABLE', NENHUMA, True, DESCONHECIDA, False, False,
       ['NOT_APPLICABLE'],
       'a matriz não declara esta capacidade para esta plataforma. Não é falha de '
       'ninguém: é pergunta que não existe.'),
    _e('FEATURE_DISABLED', NENHUMA, True, HEALTHY, False, False,
       ['FEATURE_DISABLED', 'COMMENTS_DISABLED'],
       'a capacidade EXISTE na plataforma e está desligada NESTE objeto — o dono do '
       'vídeo fechou os comentários. A fonte respondeu, a rota funcionou, o nosso '
       'código funcionou: nada quebrou. Separado de NOT_APPLICABLE porque aquilo é '
       '"a plataforma não tem isso" e isto é "tem, e está desligado aqui"; e separado '
       'de ZERO_RESULTS porque zero é AUSÊNCIA DE FALA OBSERVADA e desligado é '
       'AUSÊNCIA DE SUPERFÍCIE DE FALA. Para o FIELD VOICES futuro essas duas '
       'ausências não são a mesma evidência, e quem juntar as duas hoje apaga a '
       'diferença para sempre. Não retentável enquanto o dono não reabrir.'),
    _e('ROUTE_NOT_ALLOWED', ROUTE, True, UNAVAILABLE, False, False,
       ['ROUTE_NOT_ALLOWED'],
       'a rota funcionaria e nós escolhemos não usar — robots.txt ou termo. '
       'DIFERENTE de BLOCKED: lá a plataforma nos impediu; aqui nós paramos.'),
    _e('AUTOMATION_NOT_ALLOWED', ROUTE, True, UNAVAILABLE, False, False,
       ['AUTOMATION_NOT_ALLOWED'],
       'o contrato proíbe automatizar esta capacidade por esta rota. Recusa por '
       'termo não depende de ter ferramenta instalada.'),
    _e('CREDENTIAL_MISSING', ROUTE, True, UNAVAILABLE, False, False,
       ['CREDENTIAL_MISSING', 'SESSION_MISSING', 'LOGIN_REQUIRED'],
       'falta chave, token ou sessão. A rota está viva; nós é que não temos como entrar.'),
    _e('QUOTA_EXHAUSTED', ROUTE, True, UNAVAILABLE, True, False,
       ['QUOTA_EXHAUSTED', 'TOKEN_EXHAUSTED'],
       'a cota DESTA credencial acabou. Rotaciona: outra chave do pool, ou outro '
       'projeto de API, pode ter cota. É por isso que este estado existe separado '
       'de BUDGET_EXHAUSTED — colapsar os dois faria a casa parar de rotacionar '
       'chave, que é justamente o que a rota paga já sabia fazer.'),
    _e('BUDGET_EXHAUSTED', ROUTE, True, UNAVAILABLE, False, False,
       ['BUDGET_EXHAUSTED', 'PAID_ROUTE_REFUSED', 'JA_CONCLUIDO'],
       'teto NOSSO: gasto, itens, ou a missão não autorizou pagar. Trocar de chave '
       'não resolve — a recusa é da casa, não da plataforma. A fonte não tem nada '
       'a ver com isso.'),

    # ── A ROTA FALHOU (a fonte continua sã) ────────────────────────────────
    _e('AUTH_EXPIRED', ROUTE, True, UNHEALTHY, True, False,
       ['AUTH_EXPIRED', 'SESSION_EXPIRED', 'MFA_REQUIRED', 'TOKEN_INVALID',
        'TOKEN_OTHER_AUTH_FAILURE', 'LOGIN_WALL'],
       'a credencial existia e não vale mais. NUNCA é fonte vazia — e repetir o mesmo '
       'pedido não adianta: precisa de credencial nova, às vezes de gente.'),
    _e('RATE_LIMITED', ROUTE, True, UNHEALTHY, True, True,
       ['RATE_LIMITED', 'TOKEN_RATE_LIMITED_ACCOUNT'],
       'pedimos rápido demais. Retentável COM espera. Não é fonte caída.'),
    _e('BLOCKED', ROUTE, True, UNHEALTHY, True, False,
       ['BLOCKED', 'PLATFORM_BLOCKED'],
       'a plataforma nos impediu tecnicamente — desafio de bot, 403 de agente. '
       'Repetir igual só piora; trocar de rota ou de identidade é o caminho.'),
    _e('ROUTE_UNAVAILABLE', ROUTE, True, UNAVAILABLE, True, True,
       ['ROUTE_UNAVAILABLE', 'ATOR_NAO_ALCANCADO'],
       'a rota específica não respondeu, e outra rota da mesma capacidade pode servir.'),
    _e('TRANSIENT_NETWORK_ERROR', ROUTE, True, UNHEALTHY, False, True,
       ['TRANSIENT_NETWORK_ERROR', 'NAVIGATION_FAILED'],
       'o túnel caiu no meio. Retentável — e é a ÚNICA falha de transporte que '
       'autoriza repetir sozinha. Falha de transporte não é falha de rota.'),

    # ── A FONTE FALHOU ─────────────────────────────────────────────────────
    _e('SOURCE_UNAVAILABLE', SOURCE, True, UNHEALTHY, False, True,
       ['SOURCE_UNAVAILABLE', 'SOURCE_FAILED'],
       'a fonte respondeu 5xx ou não respondeu. Ela está doente, não nós.'),
    _e('SOURCE_GONE', SOURCE, True, GONE, False, False,
       ['SOURCE_GONE', 'NOT_FOUND'],
       '404 sobre um alvo que existia. AUSÊNCIA NUMA RODADA NÃO É REMOÇÃO — só use '
       'este estado quando o alvo foi pedido nominalmente e negado nominalmente.'),

    # ── NÓS QUEBRAMOS (esperado=False: pede gente) ─────────────────────────
    _e('PARSER_DRIFT', EXECUTOR, False, BROKEN, False, False,
       ['PARSER_DRIFT', 'PARSER_FAILURE'],
       'a fonte respondeu e o nosso extrator não achou os campos. É defeito NOSSO, '
       'e é o único que ninguém avisa. Sem este estado, isto vira "fonte vazia".'),
    _e('CONTRACT_DRIFT', EXECUTOR, False, BROKEN, False, False,
       ['CONTRACT_DRIFT', 'ENTRADA_REPROVADA', 'SCHEMA_NAO_PUBLICADO', 'QUERY_FAILURE',
        'NEW_VERSION_CHANGED'],
       'o contrato de entrada ou de saída mudou debaixo de nós. '
       'ENTRADA PROVADA ONTEM NÃO É ENTRADA VÁLIDA HOJE.'),
    _e('EXECUTOR_UNAVAILABLE', EXECUTOR, False, BROKEN, False, False,
       ['EXECUTOR_UNAVAILABLE', 'BROWSER_NOT_REACHED', 'ATOR_NAO_ENCONTRADO',
        'ACTOR_FAILURE'],
       'a nossa ferramenta não está lá — Chrome não subiu, ator não existe. '
       'Nada foi medido sobre a fonte.'),
    _e('PERMANENT_HTTP_ERROR', EXECUTOR, False, BROKEN, False, False,
       ['PERMANENT_HTTP_ERROR'],
       '4xx que não é auth nem rate limit: pedimos errado. Repetir igual nunca passa.'),
    _e('ITEM_ERROR', EXECUTOR, False, HEALTHY, False, False,
       ['ITEM_ERROR'],
       'um item do lote falhou e os outros vieram. A fonte e a rota continuam sãs — '
       'por isso a saúde aqui é HEALTHY. Falha parcial não condena a coleta.'),

    # ── NÃO SEI ────────────────────────────────────────────────────────────
    _e('UNKNOWN_ERROR', EXECUTOR, False, DESCONHECIDA, False, False,
       ['UNKNOWN_ERROR', 'UNKNOWN_FAILURE', 'FAILED', 'PLATFORM_FAILURE'],
       'não classificado. `PLATFORM_FAILURE` cai aqui de propósito: o nome antigo '
       'ACUSAVA a plataforma sem prova. NÃO SEI é mais honesto que culpar a fonte.'),
]

ESTADOS = {e.nome: e for e in _TABELA}
NOMES = tuple(e.nome for e in _TABELA)

# Índice do nome antigo -> nome canônico. É o que torna a migração conferível.
_DE_PARA = {}
for _e_ in _TABELA:
    for _velho in _e_.absorve:
        _DE_PARA.setdefault(_velho, _e_.nome)

# Os dois estados que NÃO são falha. Tudo o mais é.
NAO_SAO_FALHA = ('OK', 'ZERO_RESULTS', 'NOT_APPLICABLE', 'FEATURE_DISABLED')


# ══════════════════════════════════════════════════════════════════════════
# CONSULTA
# ══════════════════════════════════════════════════════════════════════════
def estado(nome):
    """Devolve a linha canônica. Aceita nome antigo. Nunca inventa."""
    if nome in ESTADOS:
        return ESTADOS[nome]
    canon = _DE_PARA.get(nome)
    if canon:
        return ESTADOS[canon]
    return ESTADOS['UNKNOWN_ERROR']


def traduzir(nome):
    """Nome antigo -> nome canônico, para adaptar coletor sem reescrevê-lo."""
    return estado(nome).nome


def e_falha(nome):
    return traduzir(nome) not in NAO_SAO_FALHA


def esperado(nome):
    """False = alguém precisa olhar. É o bit que separa notícia de defeito."""
    return estado(nome).esperado


def camada(nome):
    return estado(nome).camada


def degrada_fonte(nome):
    """A fonte pode ser considerada pior por causa deste estado?

    Esta é a pergunta que impede a casa de publicar um zero que não mediu nada.
    Só falha da CAMADA SOURCE degrada a fonte. Sessão vencida, quota esgotada,
    termo proibido e parser quebrado NÃO dizem nada sobre a fonte.
    """
    return estado(nome).camada == SOURCE


def saude(nome):
    """(camada, saude) — para alimentar SOURCE_HEALTH / ROUTE_HEALTH / EXECUTOR_HEALTH."""
    e = estado(nome)
    return e.camada, e.saude


def rotaciona(nome):
    """Trocar de credencial/token adianta? (é a regra que a rota paga já tinha)"""
    return estado(nome).rotaciona


def retentavel(nome):
    """Repetir o MESMO pedido adianta?

    4xx permanente, parser quebrado e recusa por termo devolvem False de propósito:
    retentar aí é queimar cota e tempo por um resultado que não muda.
    """
    return estado(nome).retentavel


# ══════════════════════════════════════════════════════════════════════════
# RECUPERAÇÃO — o que FAZER, que é pergunta diferente de o que ACONTECEU
# ══════════════════════════════════════════════════════════════════════════
# `AUTH_EXPIRED` absorve chave inválida, sessão vencida e MFA. Os três são o
# mesmo FATO (a credencial não vale mais) e três CONSERTOS diferentes: um é
# trocar de chave sozinho, outro é uma pessoa relogar, o terceiro é uma pessoa
# com o telefone na mão. Tratar os três como "rotaciona" faria a máquina girar
# o pool a noite inteira esperando que uma sessão de navegador se conserte.
#
#     O MESMO ESTADO PODE TER RECUPERAÇÕES DIFERENTES.
#
# Escolha deliberada: NÃO separar os estados. Medido nesta casa em 2026-09-08,
# `falhas.rotaciona()` não tem NENHUM consumidor em produção — os cinco
# chamadores reais (`apify_pool`, `apify_recuperar`, `sensor_coleta`,
# `coleta_checkpoint`, `instagram_coleta`) usam a tupla `ap.ROTACIONAM` direto.
# Então acrescentar uma coluna não muda comportamento de ninguém, e separar
# estados mudaria — e ainda incharia a taxonomia. Menor correção que preserva
# a diferença material.
ROTATE_CREDENTIAL = 'ROTATE_CREDENTIAL'    # outra chave do pool; a máquina resolve
HUMAN_RELOGIN = 'HUMAN_RELOGIN'            # uma pessoa precisa logar de novo
# Separado de HUMAN_RELOGIN de propósito: "falta chave de API" e "sessão do
# navegador venceu" mandam a pessoa fazer coisas DIFERENTES. Quem lê
# HUMAN_RELOGIN vai abrir o Chrome; quem precisa é de um projeto no console da
# plataforma. Um verbo errado custa uma tarde.
HUMAN_PROVISION_CREDENTIAL = 'HUMAN_PROVISION_CREDENTIAL'
HUMAN_MFA = 'HUMAN_MFA'                    # uma pessoa COM O SEGUNDO FATOR na mão
CHANGE_ROUTE = 'CHANGE_ROUTE'              # insistir aqui piora; tentar outra porta
WAIT = 'WAIT'                              # o tempo resolve — e só ele
NO_RETRY = 'NO_RETRY'                      # repetir nunca passa
NEEDS_HUMAN_FIX = 'NEEDS_HUMAN_FIX'        # defeito nosso; código precisa mudar

RECUPERACOES = (ROTATE_CREDENTIAL, HUMAN_RELOGIN, HUMAN_PROVISION_CREDENTIAL,
                HUMAN_MFA, CHANGE_ROUTE, WAIT, NO_RETRY, NEEDS_HUMAN_FIX)

# Recuperação por ESTADO canônico. É o padrão quando não há razão nativa.
_POR_ESTADO = {
    'OK': NO_RETRY, 'ZERO_RESULTS': NO_RETRY, 'NOT_APPLICABLE': NO_RETRY,
    'FEATURE_DISABLED': NO_RETRY,
    'ROUTE_NOT_ALLOWED': NO_RETRY, 'AUTOMATION_NOT_ALLOWED': NO_RETRY,
    'CREDENTIAL_MISSING': HUMAN_PROVISION_CREDENTIAL, 'QUOTA_EXHAUSTED': ROTATE_CREDENTIAL,
    'BUDGET_EXHAUSTED': NO_RETRY, 'AUTH_EXPIRED': ROTATE_CREDENTIAL,
    'RATE_LIMITED': WAIT, 'BLOCKED': CHANGE_ROUTE,
    'ROUTE_UNAVAILABLE': CHANGE_ROUTE, 'TRANSIENT_NETWORK_ERROR': WAIT,
    'SOURCE_UNAVAILABLE': WAIT, 'SOURCE_GONE': NO_RETRY,
    'PARSER_DRIFT': NEEDS_HUMAN_FIX, 'CONTRACT_DRIFT': NEEDS_HUMAN_FIX,
    'EXECUTOR_UNAVAILABLE': NEEDS_HUMAN_FIX, 'PERMANENT_HTTP_ERROR': NEEDS_HUMAN_FIX,
    'ITEM_ERROR': NO_RETRY, 'UNKNOWN_ERROR': NO_RETRY,
}

# A razão NATIVA refina. É aqui que os três `AUTH_EXPIRED` deixam de ser um só.
_POR_RAZAO_NATIVA = {
    'TOKEN_INVALID': ROTATE_CREDENTIAL,
    'TOKEN_EXHAUSTED': ROTATE_CREDENTIAL,
    'TOKEN_OTHER_AUTH_FAILURE': ROTATE_CREDENTIAL,
    'SESSION_EXPIRED': HUMAN_RELOGIN,
    'SESSION_MISSING': HUMAN_RELOGIN,
    'CREDENTIAL_MISSING': HUMAN_PROVISION_CREDENTIAL,
    'LOGIN_REQUIRED': HUMAN_RELOGIN,
    'LOGIN_WALL': HUMAN_RELOGIN,
    'MFA_REQUIRED': HUMAN_MFA,
    'PLATFORM_BLOCKED': CHANGE_ROUTE,
}


def recuperacao(nome, nativo=None):
    """O que FAZER com esta falha. `nativo` refina quando o estado é genérico."""
    if nativo and nativo in _POR_RAZAO_NATIVA:
        return _POR_RAZAO_NATIVA[nativo]
    if nome in _POR_RAZAO_NATIVA:
        return _POR_RAZAO_NATIVA[nome]
    return _POR_ESTADO.get(traduzir(nome), NO_RETRY)


def pede_gente(nome, nativo=None):
    """A máquina consegue sozinha, ou precisa de uma pessoa?"""
    return recuperacao(nome, nativo) in (HUMAN_RELOGIN, HUMAN_PROVISION_CREDENTIAL,
                                        HUMAN_MFA, NEEDS_HUMAN_FIX)


def pode_julgar_a_fonte(nome):
    """Este resultado autoriza dizer alguma coisa sobre a SAÚDE DA FONTE?

    Existe por causa de uma armadilha concreta: `source_health.version_state()`
    recebe `fetch_ok` e, se ele for falso, devolve `SOURCE_FAILED`. Passar
    qualquer falha para lá faria sessão vencida, quota esgotada e parser quebrado
    virarem "a fonte falhou" — que é exatamente o erro que esta taxonomia existe
    para impedir.

        SÓ QUEM OLHOU A FONTE PODE OPINAR SOBRE ELA.

    Verdadeiro quando a fonte respondeu (com dado ou vazia) ou quando ela própria
    falhou. Falso quando paramos antes, ou quando quem quebrou fomos nós.
    """
    e = estado(nome)
    # `NOT_APPLICABLE` e `FEATURE_DISABLED` ficam de fora apesar da camada NENHUMA:
    # nos dois a fonte está sã e NÃO houve payload. Mandá-los para o contrato de
    # fonte faria comparar o hash de coisa nenhuma.
    return (e.camada in (SOURCE, NENHUMA)
            and e.nome not in ('NOT_APPLICABLE', 'FEATURE_DISABLED'))


def fetch_ok_para_source_health(nome):
    """Adapter para `source_health.version_state(fetch_ok=...)`, sem alterá-lo.

    Devolve (avaliar, fetch_ok). Quando `avaliar` é False, NÃO chame
    `version_state`: a saúde da fonte fica UNKNOWN, e UNKNOWN é a resposta certa.
    """
    if not pode_julgar_a_fonte(nome):
        return False, None
    return True, estado(nome).camada != SOURCE


def classificar(*, http=None, erro=None, itens=None, nativo=None):
    """Classificação de último recurso, para quem não sabe o próprio estado.

    Deliberadamente burra e conservadora: quando não há prova, devolve
    `UNKNOWN_ERROR`, nunca um palpite que acuse a fonte. Quem tem informação
    melhor — `apify_pool`, `social_rotas`, `cdp` — deve classificar por conta
    própria e só usar `traduzir()`.
    """
    if erro is None and http is None and itens is not None:
        return 'OK' if itens else 'ZERO_RESULTS'
    if http is not None:
        if http in (401, 403):
            return 'AUTH_EXPIRED'
        if http == 404:
            return 'SOURCE_GONE'
        if http == 429:
            return 'RATE_LIMITED'
        if 500 <= http < 600:
            return 'SOURCE_UNAVAILABLE'
        if 400 <= http < 500:
            return 'PERMANENT_HTTP_ERROR'
        if 200 <= http < 300:
            return 'OK' if itens else 'ZERO_RESULTS'
    if nativo:
        t = traduzir(nativo)
        if t != 'UNKNOWN_ERROR':
            return t
    return 'UNKNOWN_ERROR'


def resumo():
    print('TAXONOMIA CANONICA DE FALHAS — %d estados' % len(NOMES))
    print('%-24s %-9s %-9s %-10s %s' % ('ESTADO', 'CAMADA', 'ESPERADO', 'SAUDE', 'DEGRADA_FONTE'))
    for e in _TABELA:
        print('%-24s %-9s %-9s %-10s %s' % (
            e.nome, e.camada, 'SIM' if e.esperado else 'NAO', e.saude,
            'SIM' if e.camada == SOURCE else 'nao'))
    print('\nNao sao falha: %s' % ', '.join(NAO_SAO_FALHA))
    print('Pedem gente (esperado=NAO): %s' % ', '.join(
        n for n in NOMES if not ESTADOS[n].esperado))
    print('%d nomes antigos mapeados para os %d canonicos.' % (len(_DE_PARA), len(NOMES)))
    return 0


if __name__ == '__main__':
    raise SystemExit(resumo())
