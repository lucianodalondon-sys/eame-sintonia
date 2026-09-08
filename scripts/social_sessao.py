#!/usr/bin/env python3
"""
LOCAL_SESSION — usar um navegador JÁ logado no PC, sem que a senha viaje.

    py scripts/social_sessao.py preflight        # o perfil existe? o Chrome existe?
    py scripts/social_sessao.py health           # o que cada plataforma responde
    py scripts/social_sessao.py politica         # onde LOCAL_SESSION é PERMITIDA

    GITHUB DISPARA. O PC EXECUTA. O NAVEGADOR LOCAL MANTÉM A SESSÃO.
    A SENHA NÃO VIAJA. O COOKIE NÃO VAI PARA O REPO.

Este arquivo NÃO é uma arquitetura de autenticação nova. Ele é uma ROTA a mais
do SINTONIA SCRAP, ao lado de PUBLIC, OFFICIAL_API, OFFICIAL_PAID_API e APIFY.
O navegador já existe nesta casa (`navegador.py` acha o Chrome, `cdp.py` fala
com ele) e não foi reescrito — foi reusado.

A DISTINÇÃO QUE SUSTENTA O ARQUIVO INTEIRO
--------------------------------------------
    SESSION_AVAILABLE   →  existe uma sessão aberta nesta máquina
    AUTOMATION_ALLOWED  →  a plataforma permite automatizar AQUELA superfície

São coisas DIFERENTES e a segunda não decorre da primeira. Estar logado é um
fato sobre o meu computador; poder automatizar é um fato sobre o contrato com a
plataforma. Confundir os dois é como tratar "a porta está destrancada" como
"posso entrar".

    AUTENTICADO NÃO É AUTORIZADO A AUTOMATIZAR QUALQUER COISA.

SEIS PERGUNTAS, NAO UMA — E ELAS NAO SAO A MESMA
--------------------------------------------------
A primeira versao deste arquivo respondia com um eixo so: DE QUEM E A CONTA.
`OWN_PROPERTY` valia PERMITIDO e `THIRD_PARTY` valia PROIBIDO, nas sete
plataformas. Isso acerta o caso perigoso e erra os dois lados:

  · erra para MENOS: `THIRD_PARTY` nao e proibido em si. Ler comentario de canal
    alheio pela Data API oficial do YouTube, com chave, e exatamente o que a API
    existe para fazer. A recusa valia para a SESSAO, e a doutrina generalizou;
  · erra para MAIS: `OWN_PROPERTY` nao e autorizacao automatica. Os Termos §3 do
    YouTube proibem "any automated means" e NAO abrem excecao para o dono do
    canal. Ser dono muda o que se pode LER; nao muda o que se pode AUTOMATIZAR.

    AUTH E MODO DE ENTRAR. NAO E PERMISSAO DE AUTOMATIZAR.
    ROBOTS NAO E TERMS.
    SESSION_AVAILABLE NAO E AUTHORIZATION_ALLOWED.
    OWN_PROPERTY NAO E AUTOMATION_ALLOWED.

A pergunta certa nunca e "posso usar o Instagram?". E:

    (PLATAFORMA, CAPACIDADE, ROTA, DE QUEM E A CONTA) -> posso?

Uma estrutura de dados, seis campos, um veredito. Nao seis motores:

    TECHNICAL_STATUS       a rota funciona? (medido, vive na matriz)
    ROBOTS_STATUS          o robots.txt do host barra? So governa robo anonimo.
                           Para API contratada e para sessao de gente: NOT_APPLICABLE
    TERMS_STATUS           o contrato permite ESTA rota para ESTE alvo?
    AUTH_STATUS            temos a credencial? (fato sobre o nosso PC)
    AUTHORIZATION_STATUS   somos autorizados? (fato sobre o contrato)
    ROUTE_STATUS           o veredito: USABLE / NOT_USABLE / NEEDS_REVIEW

AUTH_STATUS e AUTHORIZATION_STATUS sao colunas separadas de proposito. Ter a
sessao aberta e um fato sobre esta maquina. Poder automatiza-la e um fato sobre
o contrato. Quando as duas moram na mesma variavel, a primeira decide — e foi
assim que "estou logado" virou "posso".

ONDE NAO HOUVE PROVA, SAI `NEEDS_REVIEW`
------------------------------------------
`OWN_PROPERTY` com `LOCAL_SESSION` sai `NEEDS_REVIEW`, nao `ALLOWED`. Nenhuma das
sete clausulas lidas abre excecao escrita para o dono, e a nota de cada
plataforma nesta tabela ja diz que a rota certa para conta propria e a API
oficial. Afirmar ALLOWED seria inventar uma permissao que ninguem leu.

O QUE ESTE ARQUIVO NUNCA FAZ
------------------------------
Não abre página de login. Não digita e-mail. Não digita senha. Não submete
credencial. Não lê OTP, SMS ou e-mail. Não resolve CAPTCHA. Não troca
fingerprint. Não esconde que é automação. Quando falta sessão, ele PARA e diz
`LOGIN_REQUIRED` — a autenticação humana acontece fora da coleta, uma vez.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import navegador                    # noqa: E402  — já sabe achar o Chrome
import cdp                          # noqa: E402  — já sabe falar com ele

# ── ESTADOS. Poucos de propósito: 40 estados não são vocabulário, são ruído. ──
SESSION_AVAILABLE = 'SESSION_AVAILABLE'
SESSION_MISSING = 'SESSION_MISSING'
SESSION_EXPIRED = 'SESSION_EXPIRED'
LOGIN_REQUIRED = 'LOGIN_REQUIRED'
MFA_REQUIRED = 'MFA_REQUIRED'
PLATFORM_BLOCKED = 'PLATFORM_BLOCKED'
AUTOMATION_NOT_ALLOWED = 'AUTOMATION_NOT_ALLOWED'
HEALTHY = 'LOCAL_SESSION_HEALTHY'
UNHEALTHY = 'LOCAL_SESSION_UNHEALTHY'
UNKNOWN = 'UNKNOWN'

# ── AUTH MODES canônicos, na ordem de preferência da casa. ──
PUBLIC = 'PUBLIC'
OFFICIAL_API = 'OFFICIAL_API'
LOCAL_SESSION = 'LOCAL_SESSION'
OFFICIAL_PAID_API = 'OFFICIAL_PAID_API'
APIFY = 'APIFY'
UNAVAILABLE = 'UNAVAILABLE'

AUTH_MODES = (PUBLIC, OFFICIAL_API, LOCAL_SESSION, OFFICIAL_PAID_API, APIFY, UNAVAILABLE)

OWN_PROPERTY = 'OWN_PROPERTY'
THIRD_PARTY = 'THIRD_PARTY'

# ══════════════════════════════════════════════════════════════════════════
# A POLÍTICA. Uma linha por plataforma, com a cláusula que a sustenta.
# `THIRD_PARTY` é False em todas as sete — e cada False cita o contrato.
# ══════════════════════════════════════════════════════════════════════════
POLITICA = {
    'LINKEDIN': {
        OWN_PROPERTY: True, THIRD_PARTY: False,
        'CLAUSULA': ('User Agreement §8.2: "Use bots or other unauthorized automated '
                     'methods to access the Services". O robots.txt repete: automação '
                     'sem permissão expressa é proibida. Sessão aberta não é permissão.'),
        'FONTE': 'https://www.linkedin.com/legal/user-agreement',
        'OWN_NOTA': ('a própria página da ADAMA se lê pela Community Management API com '
                     'papel de ADMINISTRATOR — API oficial ganha da sessão aqui.'),
    },
    'FACEBOOK': {
        OWN_PROPERTY: True, THIRD_PARTY: False,
        'CLAUSULA': ('robots.txt é `Disallow: /` para todo agente, e a coleta automatizada '
                     'sem permissão escrita é vedada. A rota certa para Página de terceiro '
                     'é PPCA, com App Review.'),
        'FONTE': 'https://developers.facebook.com/docs/features-reference/page-public-content-access',
        'OWN_NOTA': 'Página própria: Graph API com Page access token, sem navegador.',
    },
    'INSTAGRAM': {
        OWN_PROPERTY: True, THIRD_PARTY: False,
        'CLAUSULA': ('a rota pública desta casa (`instagram_janela.py`) roda DESLOGADA de '
                     'propósito: ela lê a moldura que o Instagram publica para qualquer '
                     'um. Logar para ver MAIS muda a natureza do ato — deixa de ser ler '
                     'página pública e vira usar credencial para ultrapassar um limite.'),
        'FONTE': 'scripts/instagram_janela.py',
        'OWN_NOTA': 'conta própria: Graph API (insights), não navegador.',
    },
    'X': {
        OWN_PROPERTY: True, THIRD_PARTY: False,
        'CLAUSULA': ('x.com e cdn.syndication.twimg.com são os dois `User-agent: * / '
                     'Disallow: /`. A rota permitida é a API paga por uso.'),
        'FONTE': 'https://x.com/robots.txt',
        'OWN_NOTA': 'conta própria: Owned Reads da API custam US$ 0,001 por objeto.',
    },
    'TIKTOK': {
        OWN_PROPERTY: True, THIRD_PARTY: False,
        'CLAUSULA': ('Termos §5: "use automated scripts to collect information from or '
                     'otherwise interact with the Services". E o robots.txt nomeia '
                     'ClaudeBot num bloco `Disallow: /`.'),
        'FONTE': 'https://www.tiktok.com/legal/page/row/terms-of-service/en',
        'OWN_NOTA': 'conta própria: Display API com OAuth do dono.',
    },
    'THREADS': {
        OWN_PROPERTY: True, THIRD_PARTY: False,
        'CLAUSULA': ('não há motivo para sessão: a Meta publica `keyword_search`, o único '
                     'endpoint da família desenhado para monitorar conteúdo público de '
                     'terceiro. Sessão seria a rota pior E proibida.'),
        'FONTE': 'https://developers.facebook.com/docs/threads/keyword-search',
        'OWN_NOTA': 'conta própria: API de perfil e insights.',
    },
    'YOUTUBE': {
        OWN_PROPERTY: True, THIRD_PARTY: False,
        'CLAUSULA': ('Termos §3: "access the Service using any automated means (such as '
                     'robots, botnets or scrapers)" fora do robots.txt ou de permissão '
                     'escrita. Vale logado e deslogado.'),
        'FONTE': 'https://www.youtube.com/t/terms',
        'OWN_NOTA': ('canal próprio: `captions.download` da Data API FUNCIONA para o dono — '
                     'é o único caso em que a legenda oficial está ao nosso alcance.'),
    },
}


# ══════════════════════════════════════════════════════════════════════════
# OS SEIS EIXOS. Vocabulário — cada um responde UMA pergunta, e só ela.
# ══════════════════════════════════════════════════════════════════════════
USABLE = 'USABLE'
NOT_USABLE = 'NOT_USABLE'
NEEDS_REVIEW = 'NEEDS_REVIEW'

ALLOWED = 'ALLOWED'
FORBIDDEN = 'FORBIDDEN'
NOT_APPLICABLE = 'NOT_APPLICABLE'

# `robots.txt` governa robô ANÔNIMO sobre HTTP. Não governa API contratada (outro
# host, outro contrato) nem sessão de gente logada. Dizer FORBIDDEN por robots numa
# chamada de API seria aplicar a regra errada — e dizer ALLOWED seria pior ainda.
ROBOTS_GOVERNA = ('PUBLIC',)

# A rota de sessão local, para conta de TERCEIRO, é a única fechada por contrato nas
# sete. Para conta PRÓPRIA fica `NEEDS_REVIEW`: nenhuma cláusula lida abre exceção
# escrita ao dono, e a nota de cada plataforma já manda usar a API oficial.
TERMS_LOCAL_SESSION = {THIRD_PARTY: FORBIDDEN, OWN_PROPERTY: NEEDS_REVIEW}


def _terms_status(plat, auth_mode, ownership):
    """O contrato permite ESTA rota, para ESTE tipo de alvo? Só o contrato."""
    p = POLITICA.get(plat)
    if auth_mode == 'LOCAL_SESSION':
        if not p:
            return FORBIDDEN, 'plataforma sem política declarada — o padrão é NÃO'
        veredito = TERMS_LOCAL_SESSION[ownership]
        if veredito == FORBIDDEN:
            return FORBIDDEN, p['CLAUSULA']
        return NEEDS_REVIEW, (
            'conta própria não é exceção escrita: %s Nenhuma cláusula lida abre '
            'exceção ao dono para automação por navegador — e a rota certa aqui é '
            'outra: %s' % (p['CLAUSULA'][:90] + '…', p.get('OWN_NOTA') or 'API oficial.'))
    if auth_mode in ('OFFICIAL_API', 'OFFICIAL_PAID_API'):
        # A API oficial existe PARA ser chamada por programa, inclusive sobre alvo de
        # terceiro. É o caso que a doutrina antiga recusava por generalização.
        return ALLOWED, ('API oficial: o acesso automatizado é o uso previsto, e o '
                         'alvo de terceiro é o que ela serve. Limite é quota, não contrato.')
    if auth_mode == 'APIFY':
        return NEEDS_REVIEW, ('rota terceirizada: quem executa é o fornecedor, e o '
                              'contrato dele com a plataforma não é legível daqui.')
    return NEEDS_REVIEW, 'rota pública: quem decide é o robots.txt lido na hora.'


def usabilidade(platform, capability, auth_mode, ownership=THIRD_PARTY,
                technical_status=None, auth_status=None):
    """(plataforma, capacidade, rota, de quem é a conta) -> os seis eixos + veredito.

    Não é um motor: é uma leitura de tabela. Devolve os seis campos SEPARADOS, para
    que quem lê o artefato veja POR QUE o veredito é o que é — e para que
    `AUTH_STATUS` (temos credencial) nunca seja confundido com
    `AUTHORIZATION_STATUS` (podemos usá-la).
    """
    plat = platform.upper()
    terms, porque = _terms_status(plat, auth_mode, ownership)
    robots = (UNKNOWN if auth_mode in ROBOTS_GOVERNA else NOT_APPLICABLE)
    r = {
        'PLATFORM': plat, 'CAPABILITY': capability.upper(), 'AUTH_MODE': auth_mode,
        'ACCOUNT_RELATION': ownership,
        'TECHNICAL_STATUS': technical_status or UNKNOWN,
        # UNKNOWN, e não ALLOWED: o robots é lido na hora por `social_rotas.permitido()`,
        # com o User-agent real. Afirmar aqui seria decorar o que precisa ser lido.
        'ROBOTS_STATUS': robots,
        'TERMS_STATUS': terms,
        'AUTH_STATUS': auth_status or UNKNOWN,
        'AUTHORIZATION_STATUS': ALLOWED if terms == ALLOWED else (
            FORBIDDEN if terms == FORBIDDEN else NEEDS_REVIEW),
        'FONTE': (POLITICA.get(plat) or {}).get('FONTE'),
        'PORQUE': porque,
    }
    if r['AUTHORIZATION_STATUS'] == FORBIDDEN:
        r['ROUTE_STATUS'] = NOT_USABLE
    elif r['AUTHORIZATION_STATUS'] == NEEDS_REVIEW:
        r['ROUTE_STATUS'] = NEEDS_REVIEW
    else:
        r['ROUTE_STATUS'] = USABLE
    return r


def automacao_permitida(platform, ownership=THIRD_PARTY, capability='*',
                        auth_mode='LOCAL_SESSION'):
    """A trava histórica, agora escrita em cima de `usabilidade()`. Devolve (bool, motivo).

    Continua com a mesma assinatura para não quebrar quem já chama — mas mudou de
    comportamento num ponto, de propósito: `OWN_PROPERTY` já NÃO é um sim automático.
    Só `USABLE` passa; `NEEDS_REVIEW` não passa, porque revisão pendente não é licença.
    """
    r = usabilidade(platform, capability, auth_mode, ownership)
    return r['ROUTE_STATUS'] == USABLE, r['PORQUE']


# ══════════════════════════════════════════════════════════════════════════
# PERFIL — nome lógico, nunca caminho pessoal no repositório.
# ══════════════════════════════════════════════════════════════════════════
ENV_PERFIL = 'SINTONIA_BROWSER_PROFILE_DIR'


def perfil_dir():
    """Onde o perfil dedicado vive NESTA máquina.

    A ordem é: variável de ambiente da máquina → o padrão de `navegador.py`
    (`~/.sintonia-browser/chrome-profile`). Nenhum caminho pessoal — nada de
    `C:\\Users\\<alguém>` — entra no repositório em nenhuma das duas.
    """
    return os.environ.get(ENV_PERFIL) or navegador.PERFIL_COLETA


def _dentro_do_repo(caminho):
    """Um perfil dentro do repositório é um acidente esperando commit."""
    raiz = os.path.dirname(HERE)
    try:
        return os.path.commonpath([os.path.abspath(caminho), raiz]) == raiz
    except ValueError:
        return False


# ══════════════════════════════════════════════════════════════════════════
# PREFLIGHT — barato, antes de abrir qualquer página.
# ══════════════════════════════════════════════════════════════════════════
def preflight():
    """Responde se a rota é sequer tentável, SEM abrir uma única página.

    Existe para não descobrir a ausência de login depois de cem navegações. E
    para não abrir o Chrome só para saber que não há perfil.
    """
    perfil = perfil_dir()
    achado = navegador.descobrir()
    r = {
        'QUANDO': _agora(),
        'PERFIL_CONFIGURADO_POR': (ENV_PERFIL if os.environ.get(ENV_PERFIL)
                                   else 'padrão de navegador.py'),
        # O caminho NUNCA sai daqui: o relatório carrega só o que é seguro
        # mostrar. Ver `redigir()`.
        'PERFIL_EXISTE': os.path.isdir(perfil),
        'PERFIL_LEGIVEL': os.access(perfil, os.R_OK) if os.path.isdir(perfil) else False,
        'PERFIL_DENTRO_DO_REPO': _dentro_do_repo(perfil),
        'BROWSER_ENCONTRADO': achado['FOUND'],
        'BROWSER_FAMILIA': achado.get('FAMILY'),
    }
    if r['PERFIL_DENTRO_DO_REPO']:
        r['ESTADO'] = UNHEALTHY
        r['PORQUE'] = ('o perfil aponta para DENTRO do repositório — isso põe cookie a um '
                       '`git add` de distância. Mova-o e reconfigure %s.' % ENV_PERFIL)
        return r
    if not r['BROWSER_ENCONTRADO']:
        r['ESTADO'] = UNHEALTHY
        r['PORQUE'] = 'sem Chrome nesta máquina: %s' % achado.get('WHY')
        return r
    if not r['PERFIL_EXISTE']:
        r['ESTADO'] = SESSION_MISSING
        r['PORQUE'] = ('o perfil dedicado ainda não foi criado nesta máquina. Ver '
                       'docs/operacao/HOW-TO-PROVISION-LOCAL-SESSION.md')
        return r
    if not r['PERFIL_LEGIVEL']:
        r['ESTADO'] = UNHEALTHY
        r['PORQUE'] = 'o perfil existe e não é legível por este usuário'
        return r
    # Perfil existe e Chrome existe. Isso é "tentável", não "logado".
    # SESSION_AVAILABLE de verdade só o `health` mede, e só onde for permitido.
    r['ESTADO'] = SESSION_AVAILABLE
    r['PORQUE'] = ('perfil e navegador presentes. Isto NÃO prova login: prova que a rota '
                   'pode ser tentada onde a automação for permitida.')
    return r


# ══════════════════════════════════════════════════════════════════════════
# HEALTH — e ele se recusa a medir onde não pode coletar.
# ══════════════════════════════════════════════════════════════════════════
def health(plataformas=None, ownership=THIRD_PARTY, porta=9231):
    """Estado por plataforma. Não clica em nada onde a automação é proibida.

    Medir saúde de uma rota que eu não posso usar seria gastar navegação para
    produzir um número que não autoriza nada. Onde a política diz não, o health
    responde `AUTOMATION_NOT_ALLOWED` sem abrir página — e isso é o resultado
    correto, não uma medição faltando.
    """
    pre = preflight()
    saida = {'PREFLIGHT': pre, 'OWNERSHIP': ownership, 'PLATAFORMAS': {}}
    for plat in (plataformas or sorted(POLITICA)):
        plat = plat.upper()
        ok, motivo = automacao_permitida(plat, ownership)
        if not ok:
            saida['PLATAFORMAS'][plat] = {
                'ESTADO': AUTOMATION_NOT_ALLOWED, 'NAVEGOU': False,
                'PORQUE': motivo, 'FONTE': (POLITICA.get(plat) or {}).get('FONTE')}
            continue
        if pre['ESTADO'] != SESSION_AVAILABLE:
            saida['PLATAFORMAS'][plat] = {
                'ESTADO': pre['ESTADO'], 'NAVEGOU': False, 'PORQUE': pre['PORQUE']}
            continue
        saida['PLATAFORMAS'][plat] = {
            'ESTADO': UNKNOWN, 'NAVEGOU': False,
            'PORQUE': ('permitido para %s, mas nenhum alvo próprio foi configurado nesta '
                       'missão — health de conta própria exige saber QUAL conta.' % ownership)}
    return saida


def classificar_pagina(html, url=''):
    """Traduz o que a página mostra em estado de sessão. Sem adivinhar.

    A regra que mais importa aqui é negativa: **sessão ruim NUNCA vira
    ausência de conteúdo**. Um muro de login não diz que a conta não tem posts;
    diz que eu não vi. Converter um em outro é o defeito que envenena corpus.

        LOGIN_WALL != CONTA VAZIA. MFA != LOGIN FALHOU. BLOQUEIO != NÃO EXISTE.
    """
    t = (html or '').lower()
    if not t:
        return UNKNOWN, 'página vazia — nada a concluir'
    # MFA primeiro: ele é um caso de LOGIN_WALL e precisa NÃO ser confundido
    # com "credencial errada". A ação é humana, e é diferente.
    for marca in ('two-factor', 'two_factor', 'verification code', 'codice di verifica',
                  'authentication code', 'checkpoint/challenge', 'security code'):
        if marca in t:
            return MFA_REQUIRED, 'a plataforma pede segundo fator — ação HUMANA, nunca nossa'
    for marca in ('log in', 'accedi', 'sign in', 'entrar', 'authwall', 'login_required'):
        if marca in t:
            return LOGIN_REQUIRED, 'muro de login — NÃO significa que o conteúdo não existe'
    for marca in ('session expired', 'sessione scaduta', 'please log in again'):
        if marca in t:
            return SESSION_EXPIRED, 'a sessão caducou — renovação é humana e é fora da coleta'
    for marca in ('unusual activity', 'attività insolita', 'temporarily blocked',
                  'rate limit', 'try again later'):
        if marca in t:
            return PLATFORM_BLOCKED, 'a plataforma barrou — parar, não insistir'
    return SESSION_AVAILABLE, 'a página renderizou sem muro'


# ══════════════════════════════════════════════════════════════════════════
# REDAÇÃO — o log pode dizer que há sessão; nunca pode dizer qual.
# ══════════════════════════════════════════════════════════════════════════
# O `(?:bearer|basic)\s+` no meio não é decoração. Sem ele, `Authorization:
# Bearer eyJhbGciOi...` redige a palavra "Bearer" e deixa o TOKEN inteiro no
# log — o valor casado para no primeiro espaço. Foi assim que o teste
# `test_bearer_e_apagado` pegou esta função em 2026-09-08.
#
#     REDIGIR O RÓTULO E DEIXAR O VALOR É PIOR QUE NÃO REDIGIR:
#     dá a impressão de que já foi tratado.
_SEGREDOS = re.compile(
    r'(?i)(cookie|set-cookie|authorization|csrf|x-csrf-token|sessionid|'
    r'sessid|session_token|access_token|refresh_token|auth_token|token|password|passwd|'
    r'senha|api[_-]?key|client[_-]?secret|ds_user_id|li_at|jsessionid|sid)'
    r'\s*[:=]\s*(?:bearer\s+|basic\s+)?["\']?([^\s"\'&;,}]{4,})')

# Rótulo=valor pega o caso comum. NÃO pega o caso que mais aparece em traceback:
# o segredo SOLTO dentro de uma URL, sem rótulo nenhum. `apify_pool` já conhecia a
# forma do token da Apify; aqui ela passa a valer para tudo que passe por `redigir`,
# porque esta função é a que `social_rotas` usa em TODA exceção.
#
#     REDIGIR POR RÓTULO NÃO BASTA. O VALOR TAMBÉM TEM FORMA.
_SEGREDOS_POR_FORMA = re.compile(
    r'(?i)(apify_api_[A-Za-z0-9]{10,}'          # token da Apify
    r'|eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}'   # JWT
    r'|gh[pousr]_[A-Za-z0-9]{20,}'              # token do GitHub
    r'|AIza[A-Za-z0-9_\-]{30,})')              # chave de API do Google

_CAMINHO_PESSOAL = re.compile(
    r'(?i)([A-Z]:\\Users\\[^\\\s"\']+|/home/[^/\s"\']+|/Users/[^/\s"\']+)')


def redigir(texto):
    """Apaga segredo e caminho pessoal de qualquer coisa que vá para log.

    Roda sobre stdout, sobre a mensagem de exceção e sobre o manifesto. Um
    traceback de `urllib` carrega a URL, e a URL carrega o token — é assim que
    segredo vaza sem ninguém ter escrito `print(cookie)`.
    """
    if texto is None:
        return None
    t = str(texto)
    t = _SEGREDOS.sub(lambda m: '%s=<REDIGIDO>' % m.group(1), t)
    # Depois do rótulo, a forma. A ordem importa: o passo acima já apagou a maioria,
    # e este pega o que sobrou solto — inclusive dentro de uma URL de traceback.
    t = _SEGREDOS_POR_FORMA.sub('<REDIGIDO>', t)
    t = _CAMINHO_PESSOAL.sub('<CAMINHO-LOCAL>', t)
    return t


def _agora():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


# ══════════════════════════════════════════════════════════════════════════
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'preflight'
    if cmd == 'preflight':
        r = preflight()
        print('\nPREFLIGHT DA SESSÃO LOCAL\n' + '─' * 66)
        for k, v in r.items():
            print('  %-26s %s' % (k, redigir(v)))
        print()
    elif cmd == 'health':
        h = health()
        print('\nHEALTH DA SESSÃO LOCAL · ownership=%s\n%s' % (h['OWNERSHIP'], '─' * 66))
        print('  preflight: %s' % h['PREFLIGHT']['ESTADO'])
        for plat, v in h['PLATAFORMAS'].items():
            print('\n  %-10s %-24s navegou=%s' % (plat, v['ESTADO'], v['NAVEGOU']))
            print('     %s' % redigir(v['PORQUE'])[:150])
        print()
    elif cmd == 'politica':
        print('\nLOCAL_SESSION · onde é PERMITIDA\n' + '═' * 74)
        print('  %-10s %-14s %-14s' % ('PLATAFORMA', 'CONTA PRÓPRIA', 'TERCEIRO'))
        print('  ' + '─' * 70)
        for plat in sorted(POLITICA):
            own, _ = automacao_permitida(plat, OWN_PROPERTY)
            tp, _ = automacao_permitida(plat, THIRD_PARTY)
            print('  %-10s %-14s %-14s' % (plat, 'PERMITIDO' if own else 'NÃO',
                                           'PERMITIDO' if tp else 'NÃO'))
        print('\n  Toda linha de TERCEIRO é NÃO, e cada NÃO cita uma cláusula:')
        for plat in sorted(POLITICA):
            print('\n  %s' % plat)
            print('    %s' % POLITICA[plat]['CLAUSULA'][:200])
            print('    fonte: %s' % POLITICA[plat]['FONTE'])
        print()
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
