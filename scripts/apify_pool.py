#!/usr/bin/env python3
"""
POOL DE CHAVES APIFY — uma secret só, várias chaves, nenhuma exposta.

O contrato de leitura NÃO foi inventado aqui. Ele é portado do
`credenciais.py` do **portal-sintonia** (o projeto Brasil), onde cada regra
abaixo custou uma execução real. Reusar é a decisão certa: são quatro
maneiras diferentes de um colar dar errado, todas já pagas uma vez.

    `_separa`        o separador é do CÓDIGO, não da pessoa. Aceita vírgula,
                     ponto e vírgula, quebra de linha, tabulação e espaço.
                     No Brasil, exigir vírgula fez 13 chaves chegarem como UMA
                     string de 610 caracteres, e o sistema disse "1 chave, não
                     respondeu" — coleta paga parada parecendo falha de rede.

    `_descola`       chaves grudadas SEM separador nenhum. Corta ANTES de cada
                     prefixo conhecido (`apify_api_`), e só quando há mais de
                     uma ocorrência — cortar chave boa no meio a estragaria em
                     silêncio.

    `_sem_rotulo`    o rótulo vindo DENTRO do valor (`APIFY_TOKEN=apify_...`),
                     porque quem copia a linha do arquivo copia o nome junto.
                     Só corta rótulo de lista fechada: um token pode ter `=`.

    `formato_suspeito`  conta as letras e avisa. Um token da Apify tem 46
                     caracteres; 45 é letra perdida no colar, não chave
                     revogada. **Avisa, não recusa** — trava nossa não pode
                     derrubar coleta se a Apify mudar o tamanho amanhã.

O QUE É NOVO AQUI, E É O MOTIVO DESTE ARQUIVO EXISTIR
------------------------------------------------------
A rotação. O Brasil devolve a lista na ordem; aqui a lista vira uma **máquina
de estados** que decide QUANDO trocar de chave — e, principalmente, quando
**não** trocar.

    ROTACIONA          TOKEN_EXHAUSTED · TOKEN_INVALID
                       TOKEN_RATE_LIMITED_ACCOUNT · TOKEN_OTHER_AUTH_FAILURE

    NÃO ROTACIONA      PLATFORM_FAILURE · ACTOR_FAILURE · QUERY_FAILURE
                       PARSER_FAILURE · UNKNOWN_FAILURE

`UNKNOWN_FAILURE` não rotaciona **de propósito**. Um bug meu que lance exceção
genérica queimaria o pool inteiro em segundos, e o relatório diria "todas as
chaves falharam" quando nenhuma chave foi tocada. Chave gasta à toa não volta.

A ARMADILHA QUE O `coletor.py` JÁ CONHECIA
--------------------------------------------
Cota esgotada na Apify **se apresenta como sucesso**: `status = SUCCEEDED`,
`exitCode` limpo, ZERO itens e `statusMessage = "free user run limit reached"`.
O `coletor.py` já marcava isso como `PARTIAL` desde a rodada da Espanha. Aqui
esse mesmo sinal vira `TOKEN_EXHAUSTED` — que é o único jeito de a rotação
funcionar, porque a plataforma nunca devolve 402.

SEGREDO NUNCA SAI
------------------
`censo()` devolve presença, tamanho e formato — nunca valor. `redigir()`
existe para passar QUALQUER texto que vá para log, exceção ou artefato: ela
apaga qualquer coisa com cara de token, inclusive dentro de URL. Um traceback
de `urllib` carrega a URL inteira, e a URL pode carregar o token.

PROVENIÊNCIA
------------
infraestrutura COMUM, portada sem alteração do piloto italiano
(claude/sintonia-italy-pilot-b1l401). A aba principal passa a ser o dono
canônico; o piloto continua consumindo. Regra desta casa: uma
implementação só — reimplementar aqui criaria duas verdades sobre
rotação de chave, e a segunda divergiria na primeira pressa.
"""
import os
import re

# Prefixo documentado do token da Apify — é o que permite descolar chaves
# grudadas e o que a redação procura. Portado do Brasil.
PREFIXO = 'apify_api_'
TAMANHO_ESPERADO = 46

# Rótulos que podem vir colados na frente do valor. Lista FECHADA de propósito:
# um token pode conter `=`, e cortar no primeiro estragaria a chave.
ROTULOS = ('apify_token_pool', 'apify_keys', 'apify_token', 'apify', 'token', 'key')

# Qualquer coisa com cara de token, para a redação. Deliberadamente largo.
PADRAO_TOKEN = re.compile(r'apify_api_[A-Za-z0-9]{4,}')

# --------------------------------------------------------------------- estados
TOKEN_OK = 'TOKEN_OK'
TOKEN_EXHAUSTED = 'TOKEN_EXHAUSTED'
TOKEN_INVALID = 'TOKEN_INVALID'
TOKEN_RATE_LIMITED_ACCOUNT = 'TOKEN_RATE_LIMITED_ACCOUNT'
TOKEN_OTHER_AUTH_FAILURE = 'TOKEN_OTHER_AUTH_FAILURE'

PLATFORM_FAILURE = 'PLATFORM_FAILURE'
ACTOR_FAILURE = 'ACTOR_FAILURE'
QUERY_FAILURE = 'QUERY_FAILURE'
PARSER_FAILURE = 'PARSER_FAILURE'
UNKNOWN_FAILURE = 'UNKNOWN_FAILURE'

ROTACIONAM = (TOKEN_EXHAUSTED, TOKEN_INVALID, TOKEN_RATE_LIMITED_ACCOUNT,
              TOKEN_OTHER_AUTH_FAILURE)
NAO_ROTACIONAM = (PLATFORM_FAILURE, ACTOR_FAILURE, QUERY_FAILURE,
                  PARSER_FAILURE, UNKNOWN_FAILURE)

POOL_EMPTY = 'POOL_EMPTY'


# ------------------------------------------------------------------- leitura
def _sem_rotulo(v):
    if '=' not in v:
        return v
    antes, depois = v.split('=', 1)
    if antes.strip().lower().lstrip('#').strip() in ROTULOS and depois.strip():
        return depois.strip().strip('"').strip("'").strip()
    return v


def _limpa(v):
    return _sem_rotulo((v or '').strip().strip('"').strip("'").strip())


def _descola(k):
    """N chaves grudadas sem separador: corta ANTES de cada prefixo.

    Só corta com mais de uma ocorrência — chave sozinha passa intacta.
    """
    if not k:
        return []
    if k.count(PREFIXO) > 1:
        return [x for x in re.split('(?=%s)' % re.escape(PREFIXO), k) if x]
    return [k]


def separar(v):
    """Aceita qualquer separador. Remove repetidas MANTENDO a ordem de rotação."""
    fora, visto = [], set()
    for pedaco in re.split(r'[,;\s]+', v or ''):
        for k in _descola(_limpa(pedaco)):
            if k and k not in visto:
                visto.add(k)
                fora.append(k)
    return fora


def pool(env=None):
    """A lista de chaves, na ordem de rotação. Entrada única: APIFY_TOKEN_POOL."""
    amb = (env if env is not None else os.environ).get('APIFY_TOKEN_POOL', '')
    return separar(amb)


def formato_suspeito(k):
    """→ frase sobre o que parece errado, ou ''. NUNCA devolve a chave."""
    k = k or ''
    if not k:
        return 'chegou vazia'
    if '\n' in k or '\r' in k:
        return 'tem quebra de linha DENTRO'
    if not k.startswith(PREFIXO):
        return 'não começa com %s — pode não ser token da Apify' % PREFIXO
    if len(k) == TAMANHO_ESPERADO:
        return ''
    faltam = TAMANHO_ESPERADO - len(k)
    if faltam > 0:
        return ('tem %d letras e o token da Apify tem %d — faltou %d no colar. '
                'Recopie ela INTEIRA.' % (len(k), TAMANHO_ESPERADO, faltam))
    return ('tem %d letras e o token da Apify tem %d — vieram %d a mais, '
            'provavelmente duas coladas.' % (len(k), TAMANHO_ESPERADO, -faltam))


def censo(env=None):
    """Presença, tamanho e formato. NUNCA valor — é o que vai para o log."""
    ks = pool(env)
    return {
        'TOKEN_POOL_PRESENT': 'YES' if ks else 'NO',
        'TOKEN_POOL_SIZE': len(ks),
        'FORMAT_WARNINGS': [{'POOL_POSITION': i + 1, 'WARNING': w}
                            for i, w in enumerate(formato_suspeito(k) for k in ks) if w],
    }


def redigir(texto):
    """Apaga qualquer coisa com cara de token. Passar TUDO que vai para log.

    Um traceback de urllib carrega a URL inteira, e a URL pode carregar o
    token. Redigir só a mensagem que eu escrevo não bastaria.
    """
    return PADRAO_TOKEN.sub('apify_api_***REDACTED***', str(texto))


# ------------------------------------------------------------------ rotação
def classificar(*, http=None, status=None, status_message=None, itens=None,
                excecao=None):
    """Decide o estado a partir do que a plataforma devolveu.

    A ordem importa: a cota esgotada CHEGA COMO SUCESSO e precisa ser vista
    antes de qualquer leitura otimista de `SUCCEEDED`.
    """
    msg = (status_message or '').lower()
    if excecao is not None:
        e = str(excecao).lower()
        if 'parse' in e or 'json' in e or 'decode' in e:
            return PARSER_FAILURE
        return UNKNOWN_FAILURE

    if http == 401:
        return TOKEN_INVALID
    if http == 403:
        return TOKEN_OTHER_AUTH_FAILURE
    if http == 429:
        return TOKEN_RATE_LIMITED_ACCOUNT
    if http is not None and 500 <= http < 600:
        return PLATFORM_FAILURE

    # A cota esgotada da Apify: SUCCEEDED, zero itens, e a razão só no texto.
    if any(t in msg for t in ('run limit', 'usage limit', 'monthly usage',
                              'not enough', 'insufficient', 'exceeded')):
        return TOKEN_EXHAUSTED

    if status in ('FAILED', 'ABORTED', 'TIMED-OUT'):
        return ACTOR_FAILURE
    if status == 'SUCCEEDED':
        return TOKEN_OK
    if status is None and itens is not None:
        return TOKEN_OK
    return UNKNOWN_FAILURE


def executar_com_pool(unidades, trabalho, *, identidade, env=None, teto_itens=None):
    """Percorre `unidades` trocando de chave só quando a CHAVE é o problema.

    `trabalho(unidade, token)` -> (itens, estado). `identidade(item)` -> chave
    de dedupe. A dedupe é por CONTEÚDO, nunca por token: trocar de chave não
    pode fazer o mesmo post entrar duas vezes.

    Ao rotacionar, retoma da unidade em que parou — não reinicia a coleta.
    """
    ks = pool(env)
    if not ks:
        return {'STATE': POOL_EMPTY, 'TOKENS_AVAILABLE': 0, 'TOKENS_USED': 0,
                'ITEMS': [], 'DUPLICATES_REMOVED': 0, 'BY_POSITION': [],
                'UNITS_DONE': [], 'UNITS_PENDING': list(unidades)}

    pos = 0
    itens, vistos, dups = [], set(), 0
    feitas, pendentes = [], list(unidades)
    porpos = {}

    while pendentes and pos < len(ks):
        p = pos + 1
        porpos.setdefault(p, {'POOL_POSITION': p, 'RUNS': 0, 'ITEMS': 0,
                              'FINAL_STATE': TOKEN_OK})
        u = pendentes[0]
        try:
            novos, estado = trabalho(u, ks[pos])
        except Exception as e:                       # bug meu não queima chave
            porpos[p]['FINAL_STATE'] = UNKNOWN_FAILURE
            porpos[p]['ERROR'] = redigir('%s: %s' % (type(e).__name__, e))[:200]
            break
        porpos[p]['RUNS'] += 1
        porpos[p]['FINAL_STATE'] = estado

        if estado in ROTACIONAM:
            pos += 1                                  # troca e RETOMA a mesma unidade
            continue
        if estado in NAO_ROTACIONAM:
            break                                     # não é a chave: parar, não gastar

        for it in (novos or []):
            k = identidade(it)
            if k in vistos:
                dups += 1
                continue
            vistos.add(k)
            itens.append(it)
            porpos[p]['ITEMS'] += 1
            if teto_itens and len(itens) >= teto_itens:
                break
        feitas.append(pendentes.pop(0))
        if teto_itens and len(itens) >= teto_itens:
            break

    return {
        'STATE': 'DONE' if not pendentes else 'STOPPED',
        'TOKENS_AVAILABLE': len(ks),
        'TOKENS_USED': len(porpos),
        'POOL_POSITION_USED': sorted(porpos),
        'ITEMS': itens,
        'DUPLICATES_REMOVED': dups,
        'BY_POSITION': [porpos[k] for k in sorted(porpos)],
        'UNITS_DONE': feitas,
        'UNITS_PENDING': pendentes,
    }


if __name__ == '__main__':
    c = censo()
    print('TOKEN_POOL_PRESENT =', c['TOKEN_POOL_PRESENT'])
    print('TOKEN_POOL_SIZE    =', c['TOKEN_POOL_SIZE'])
    for w in c['FORMAT_WARNINGS']:
        print('  aviso posicao %d: %s' % (w['POOL_POSITION'], w['WARNING']))
    print('(nenhum valor de chave e impresso, por contrato)')
