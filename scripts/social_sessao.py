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

O EIXO QUE DECIDE DE VERDADE: DE QUEM É A CONTA
-------------------------------------------------
Medindo os termos das sete plataformas prioritárias (pesquisa de 2026-09-08,
registrada em `docs/capacidades/SINTONIA-SCRAP-SOCIAL.md`), o que separa o
permitido do proibido não é a plataforma — é a PROPRIEDADE do alvo:

    OWN_PROPERTY    a conta/página é da ADAMA. Ler o próprio dado com a própria
                    sessão é o que qualquer administrador faz. PERMITIDO.
    THIRD_PARTY     a conta é de outra pessoa ou empresa. Aqui a sessão
                    autenticada vira exatamente o que os termos proíbem:
                    LinkedIn §8.2 ("bots or other unauthorized automated
                    methods"), TikTok §5 ("automated scripts to collect
                    information"), YouTube §3 ("any automated means").
                    NÃO PERMITIDO — e estar logado piora, não melhora.

Por isso a política aqui não tem exceção escondida: **LOCAL_SESSION contra
terceiro está fechada em todas as sete plataformas prioritárias.** Isso não é
timidez; é o que os contratos dizem. A rota existe, está pronta, e liga no dia
em que houver permissão escrita ou uma conta própria a ler.

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


def automacao_permitida(platform, ownership=THIRD_PARTY):
    """A pergunta que precede qualquer uso de sessão. Devolve (bool, motivo)."""
    p = POLITICA.get(platform.upper())
    if not p:
        return False, 'plataforma sem política declarada — o padrão é NÃO'
    if p.get(ownership):
        return True, p.get('OWN_NOTA') or 'propriedade própria'
    return False, p['CLAUSULA']


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
    r'sessid|session_token|access_token|refresh_token|auth_token|password|passwd|'
    r'senha|api[_-]?key|client[_-]?secret|ds_user_id|li_at|jsessionid|sid)'
    r'\s*[:=]\s*(?:bearer\s+|basic\s+)?["\']?([^\s"\'&;,}]{4,})')

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
