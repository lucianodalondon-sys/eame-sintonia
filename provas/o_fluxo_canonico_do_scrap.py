#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O FLUXO CANÔNICO DO SCRAP ATRAVESSA? — prova offline, ponta a ponta.

    python3 provas/o_fluxo_canonico_do_scrap.py

A SCRAP-SR-02 fechou a porta do DINHEIRO: nenhuma compra nasce sem autorização
que se possa ler. O que ela NÃO fechou foi o CAMINHO — e a diferença tem nome:

    MODULE CAN'T SPEND  !=  FLOW IS CANONICAL.

Até esta prova, a única fase paga desta casa era despachada assim:

    sintonia-scrap.yml  ->  coleta/social_scrap.py coletar yt-legenda-paga
                        ->  scrap_executor.COLLECT

Atravessava o executor do SCRAP, e mais nada. Sem PEDIDO, sem plano, sem portão
de relevância da fonte, sem RUN_ID cunhado antes da corrida, sem recibo, sem
ingresso, sem admissão. Agora:

    sintonia-scrap.yml  ->  orquestrador  ->  PEDIDO  ->  plano + portão
                        ->  subprocesso do executor  ->  scrap_executor.COLLECT
                        ->  envelope declarado (COL-LAW-505)  ->  ingresso  ->  recibo

O QUE É FALSO AQUI, E O QUE NÃO PODE SER
-----------------------------------------
Falso: **só o mundo lá fora**. Três coisas, e nenhuma delas é nossa:

    curl                 um binário FALSO à frente no `PATH`. É o cliente HTTP
                         que o `coletor` usa para falar com a Apify. Nenhum
                         pacote sai desta máquina, e cada invocação fica escrita
                         num ficheiro que esta prova LÊ para contar os POST.
    APIFY_TOKEN_POOL     uma chave obviamente falsa, para um provider falso.
    o livro de relevância um livro de FIXTURE, com UMA fonte obviamente falsa.
                         O livro é ENTRADA de um dono EXTERNO ao SCRAP
                         (`leis/relevancia_da_fonte.py`). Dar-lhe a entrada não
                         é decidir por ele: a regra continua a ser dele, e é ele
                         que responde.

    ⚠️ NENHUMA DAS 77 FONTES DESTA CASA É AVALIADA AQUI, E O LIVRO DESTA CASA
    NÃO É TOCADO. A fonte da fixture chama-se `fake~fonte-da-prova` para que
    ninguém a confunda com uma fonte real, e ela vive num ficheiro temporário
    que desaparece no fim.

NÃO é falso — e falsificá-lo invalidaria a prova inteira:

    pedido · receitas · orquestrador · scrap_executor · social_rotas · coletor
    autorizacao_de_gasto · orcamento_de_rede · orcamento_financeiro
    retorno_da_coleta · ingresso

    UM FAKE ACIMA DO GATE MEDE O FAKE. Por isso o fake é o `curl`: mais fundo
    do que ele só existe o socket, e o socket é que não queremos abrir.

AS QUATRO PROVAS
----------------
    P1  POSITIVA · MUNDO FALSO      a cadeia inteira corre e devolve recibo
    P2  NEGATIVA · AUTORIZAÇÃO      sem autorização, nenhum POST sai
    P3  NEGATIVA · ORÇAMENTO DE REDE  com teto de rede a zero, nenhum POST sai
    P4  NEGATIVA · ORÇAMENTO FINANCEIRO  com teto de gasto a zero, nenhum POST sai

As três negativas são MUTAÇÕES da declaração versionada — altera-se o ficheiro
REAL, corre-se a cadeia REAL, e exige-se que ela RECUSE. Depois restaura-se, e
confere-se pelo sha256.

    mutante que sobrevive = regra sem guarda.

⚠️ ESTA PROVA ALTERA CÓDIGO EM DISCO nas três negativas. Restaura sempre, em
`finally`, e confere o hash. Se o hash não bater, devolve 3 e diz para verificar
à mão — nunca finge que restaurou.

EXECUÇÃO REAL
-------------
    REAL_NETWORK = 0 · APIFY_REAL_RUNS = 0 · PAID_REAL_RUNS = 0
    META_REAL_REQUESTS = 0 · REAL_COST_USD = 0
"""

import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import pedido as ped                    # noqa: E402
import receitas as rec                  # noqa: E402
import orquestrador as orq              # noqa: E402
import relevancia_da_fonte as rel       # noqa: E402

FALHAS = []
PROVAS = 0

#: A fonte da fixture. O `~` está lá de propósito: `conferir_source_id` aceita-o,
#: e nenhuma das 77 fontes desta casa se parece com isto.
FONTE_FALSA = 'fake~fonte-da-prova'
TOKEN_FALSO = 'fake~token-da-prova'
FASE = 'yt-legenda-paga'
CLI = os.path.join('coleta', 'social_scrap.py')
RETORNO = os.path.join('data', 'colheita', 'scrap', 'RETORNO.json')


def diz(ok, titulo, detalhe=''):
    global PROVAS
    PROVAS += 1
    print('  %s  %-52s %s' % ('OK   ' if ok else 'FALHA', titulo[:52], detalhe))
    if not ok:
        FALHAS.append('%s · %s' % (titulo, detalhe))
    return ok


# ══════════════════════════════════════════════════════════════════════════
# O MUNDO FALSO — um `curl` que não abre socket nenhum
# ══════════════════════════════════════════════════════════════════════════
FALSO_CURL = r'''#!/usr/bin/env python3
"""O `curl` FALSO desta prova. Não abre ligação nenhuma: responde de memória.

Escreve CADA invocação no ficheiro que `FAKE_CURL_LOG` nomeia, uma linha JSON
por chamada. É esse ficheiro que a prova lê para contar os POST — a contagem é
MEDIDA na camada mais funda, e não deduzida do que o runtime disse.
"""
import json, os, sys

argv = sys.argv[1:]
url = argv[-1]
metodo = argv[argv.index('-X') + 1] if '-X' in argv else 'GET'
corpo = argv[argv.index('-d') + 1] if '-d' in argv else None

log = os.environ.get('FAKE_CURL_LOG')
if log:
    with open(log, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'METODO': metodo.upper(), 'URL': url,
                            'CORPO': corpo}) + '\n')

m = metodo.upper()
if m == 'POST' and '/acts/' in url:
    sys.stdout.write(json.dumps({'data': {
        'id': 'fake-run-1', 'status': 'SUCCEEDED',
        'startedAt': '2026-09-12T00:00:00.000Z',
        'finishedAt': '2026-09-12T00:00:05.000Z',
        'buildNumber': '0.0.1',
        'defaultDatasetId': 'fake-ds-1',
        'defaultKeyValueStoreId': 'fake-kv-1',
        'usageTotalUsd': 0.0}}))
    raise SystemExit(0)
if '/datasets/' in url:
    sys.stdout.write(json.dumps([{
        'url': 'https://www.youtube.com/watch?v=EAkcA_2FDN8',
        'transcript': 'FALSO: esta legenda nunca existiu fora desta prova.',
        'chars': 51}]))
    raise SystemExit(0)
if '/key-value-stores/' in url:
    sys.stdout.write(json.dumps({'data': {'items': []}}))
    raise SystemExit(0)
sys.stdout.write(json.dumps({'data': {}}))
'''


class MundoFalso(object):
    """Instala o `curl` falso, a chave falsa e o registo das invocações."""

    def __init__(self):
        self.pasta = None
        self.log = None
        self._antes = {}

    def __enter__(self):
        self.pasta = tempfile.mkdtemp(prefix='fluxo-canonico-')
        alvo = os.path.join(self.pasta, 'curl')
        with open(alvo, 'w', encoding='utf-8') as f:
            f.write(FALSO_CURL)
        os.chmod(alvo, os.stat(alvo).st_mode | stat.S_IEXEC | stat.S_IXGRP
                 | stat.S_IXOTH)
        self.log = os.path.join(self.pasta, 'invocacoes.jsonl')
        for k, v in (('PATH', self.pasta + os.pathsep + os.environ.get('PATH', '')),
                     ('FAKE_CURL_LOG', self.log),
                     ('APIFY_TOKEN_POOL', TOKEN_FALSO),
                     # Sem DSN não se abre banco: a prova não precisa de um, e
                     # inventar durabilidade seria dizer que houve retomada.
                     ('SUPABASE_DB_URL', '')):
            self._antes[k] = os.environ.get(k)
            os.environ[k] = v
        return self

    def __exit__(self, *a):
        for k, v in self._antes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.pasta, ignore_errors=True)
        return False

    def invocacoes(self):
        if not os.path.isfile(self.log):
            return []
        with open(self.log, encoding='utf-8') as f:
            return [json.loads(l) for l in f if l.strip()]

    def posts(self):
        return [i for i in self.invocacoes()
                if i['METODO'] == 'POST' and '/acts/' in i['URL']]

    def limpar(self):
        if os.path.isfile(self.log):
            os.remove(self.log)


def livro_que_autoriza():
    """O livro de FIXTURE. UMA decisão, sobre UMA fonte obviamente falsa.

    Escrito pelo dono da lei — `relevancia_da_fonte.Decisao` — e não à mão: uma
    linha montada à mão passaria por cima das regras que ele impõe ao que se
    pode escrever num livro.
    """
    d = rel.Decisao(
        source_id=FONTE_FALSA, proposito='T9', resultado=rel.SIM,
        motivo='fonte INVENTADA por provas/o_fluxo_canonico_do_scrap.py para '
               'exercitar o portao num mundo falso. NAO e uma fonte desta casa, '
               'e este livro nao e o livro desta casa.',
        metodo='FIXTURE_DE_PROVA_OFFLINE',
        evidencia={'ONDE': 'provas/o_fluxo_canonico_do_scrap.py',
                   'O_QUE': 'o proprio ficheiro da prova, que inventa a fonte'},
        corrida='NAO SEI')
    return [d.para_livro()]


def pedido_da_fase(*, com_fonte):
    p = ped.de_uma_frase('colete concorrentes')
    p.filtros['fase'] = FASE
    if com_fonte:
        p.filtros['fonte'] = FONTE_FALSA
    return p


# ══════════════════════════════════════════════════════════════════════════
# A CASA FICA COMO ESTAVA — e isso é medido, não prometido
# ══════════════════════════════════════════════════════════════════════════
#
# ⚠️ MEDIDO NA PRIMEIRA VOLTA DESTA PROVA, E É POR ISSO QUE ISTO EXISTE.
# A prova positiva atravessa a cadeia INTEIRA — e a cadeia inteira inclui o
# ingresso e a porta de admissão. Resultado: a corrida do MUNDO FALSO escreveu
# TRÊS decisões no `LIVRO-DE-DECISOES.json` desta casa, e reescreveu o registo
# da corrida paga REAL da C10.8B-LIVE.
#
#     UMA PROVA QUE DEIXA OBSERVAÇÃO FALSA NO LIVRO DA CASA
#     NÃO PROVOU A CASA: CONTAMINOU-A.
#
# O mundo pode ser falso. O que ele escreve nos livros REAIS não pode ficar.
# Estes ficheiros são fotografados antes e repostos depois, e o sha256 de cada
# um é conferido no fim — se não bater, a prova reprova e diz qual.
ESCRITOS_PELA_CADEIA = (
    os.path.join('data', 'samples', 'LIVRO-DE-DECISOES.json'),
    os.path.join('data', 'samples', 'SCRAP-YOUTUBE', 'yt-legenda-paga.json'),
    RETORNO,
)


class CasaIntacta(object):
    """Fotografa os ficheiros que a cadeia escreve, e repõe-nos à saída."""

    def __init__(self):
        self.antes = {}

    def __enter__(self):
        for rel_ in ESCRITOS_PELA_CADEIA:
            caminho = os.path.join(RAIZ, rel_)
            self.antes[rel_] = (open(caminho, 'rb').read()
                                if os.path.isfile(caminho) else None)
        return self

    def __exit__(self, *a):
        self.repor()
        return False

    def repor(self):
        for rel_, corpo in self.antes.items():
            caminho = os.path.join(RAIZ, rel_)
            if corpo is None:
                if os.path.isfile(caminho):
                    os.remove(caminho)
            else:
                os.makedirs(os.path.dirname(caminho), exist_ok=True)
                with open(caminho, 'wb') as f:
                    f.write(corpo)
        # O bruto que a compra falsa gravou. `.gitignore` ignora-o, e é
        # exactamente por isso que ele passaria despercebido para sempre.
        raw = os.path.join(RAIZ, 'data', 'samples', 'raw-paid')
        for n in os.listdir(raw) if os.path.isdir(raw) else []:
            if n.startswith(('XX-T9-', 'IT-T9-')):
                os.remove(os.path.join(raw, n))

    def confere(self):
        """→ os ficheiros que NÃO voltaram ao que eram."""
        mal = []
        for rel_, corpo in self.antes.items():
            caminho = os.path.join(RAIZ, rel_)
            agora = (open(caminho, 'rb').read()
                     if os.path.isfile(caminho) else None)
            if agora != corpo:
                mal.append(rel_)
        return mal


CASA = CasaIntacta()


def limpar_o_que_a_prova_deixou():
    """O envelope desta volta sai; os livros da casa voltam ao que eram."""
    CASA.repor()


# ══════════════════════════════════════════════════════════════════════════
# P0 · A CADEIA ESTÁ LIGADA? — medida antes de correr o que quer que seja
# ══════════════════════════════════════════════════════════════════════════
def p0_a_cadeia_esta_ligada():
    print('\nP0 · A CADEIA ESTÁ LIGADA\n' + '-' * 72)
    p = pedido_da_fase(com_fonte=False)
    plano = rec.resolver(p)
    e = plano.escolhido or {}
    diz(e.get('id') == 'scrap-yt-legenda-paga',
        'o PEDIDO escolhe o executor do SCRAP', e.get('id'))
    diz(e.get('roda') == [CLI, 'coletar'],
        'e o executor escolhido é a CLI do SCRAP', ' '.join(e.get('roda') or []))
    diz(e.get('recebe_run_id') is True,
        'ele declara que recebe a corrida de quem a cunhou')
    diz((e.get('retorno') or {}).get('ENVELOPE') == RETORNO.replace(os.sep, '/'),
        'e declara ONDE a corrida diz o que produziu',
        (e.get('retorno') or {}).get('ENVELOPE'))

    # O outro registo de T9 continua a ser o de sempre para quem não nomeia fase.
    outro = rec.escolher(rec.EXECUTORES['T9'], ped.de_uma_frase('colete concorrentes'))
    diz(outro.get('id') == 'comunicacao-publica',
        'quem NÃO nomeia a fase leva o executor de sempre', outro.get('id'))

    # ⚠️ E O ESTADO DE PRODUÇÃO, MEDIDO E DITO.
    r = plano.relevancia
    diz(plano.bloqueia_a_corrida is True,
        'SEM fonte nomeada, a rota paga é BARRADA',
        '%s · %s' % (r.get('VEREDITO'), r.get('ESTADO_DA_RELEVANCIA')))
    diz(r.get('SOURCE_ID') is None,
        'e o plano NÃO inventa uma fonte para o portão julgar')


# ══════════════════════════════════════════════════════════════════════════
# P1 · POSITIVA · MUNDO FALSO — a cadeia inteira atravessa
# ══════════════════════════════════════════════════════════════════════════
def p1_positiva():
    print('\nP1 · POSITIVA · MUNDO FALSO\n' + '-' * 72)
    with MundoFalso() as mundo:
        p = pedido_da_fase(com_fonte=True)
        recibo = orq.correr(p, livro=livro_que_autoriza())
        plano = recibo.pop('_plano')

        r = recibo['RELEVANCIA_DA_FONTE']
        diz(r['VEREDITO'] == rel.AUTORIZA,
            'o portão AUTORIZOU, e o veredito ficou no recibo',
            '%s · %s' % (r['VEREDITO'], r['SOURCE_ID']))
        diz(recibo['STATUS'] == 'SUCCESS', 'a corrida terminou em SUCCESS',
            '%s · %s' % (recibo['STATUS'], (recibo['ERROR'] or '')[:60]))
        diz(recibo['ACTOR'] == CLI, 'quem correu foi a CLI do SCRAP',
            recibo['ACTOR'])
        diz('coletar %s' % FASE in recibo['COMANDO'],
            'e a fase veio do PEDIDO, não de quem chamou', recibo['COMANDO'])
        diz('--run-id=%s' % recibo['RUN_ID'] in recibo['COMANDO'],
            'a corrida cunhada pelo orquestrador desceu ao executor',
            recibo['RUN_ID'])

        # ── O ENVELOPE QUE A CORRIDA DECLAROU ──────────────────────────────
        alvo = os.path.join(RAIZ, RETORNO)
        existe = os.path.isfile(alvo)
        diz(existe, 'a corrida DECLAROU o que produziu (COL-LAW-505)', RETORNO)
        env = json.load(open(alvo, encoding='utf-8')) if existe else {}
        diz(env.get('RUN_ID') == recibo['RUN_ID'],
            'e o envelope diz a MESMA corrida que o orquestrador cunhou',
            '%s vs %s' % (env.get('RUN_ID'), recibo['RUN_ID']))
        diz(recibo.get('COLHEITA_ENCONTRADA') == 1,
            'a colheita declarada foi encontrada pelo orquestrador',
            str(recibo.get('COLHEITA_ENCONTRADA')))
        diz((recibo.get('RETORNO') or {}).get('ESTADO') == 'SUCCESS'
            and (recibo.get('RETORNO') or {}).get('COLHEITA') == 1,
            'e o recibo regista a ESPÉCIE do retorno, não só a contagem',
            str(recibo.get('RETORNO')))
        diz('INGRESSO' in recibo,
            'a colheita foi à PORTA DE ENTRADA antes de alguém a julgar')

        # ── E O PROVIDER? ──────────────────────────────────────────────────
        posts = mundo.posts()
        diz(len(posts) == 1, 'UM POST de criação — nem zero, nem dois',
            '%d POST(s)' % len(posts))
        diz(all('maxTotalChargeUsd=' in i['URL'] for i in posts),
            'e o POST levou o tecto do provider que o orçamento decidiu',
            posts[0]['URL'].split('?')[-1] if posts else '')
        limpar_o_que_a_prova_deixou()


# ══════════════════════════════════════════════════════════════════════════
# AS TRÊS NEGATIVAS — mutação da declaração versionada, cadeia real
# ══════════════════════════════════════════════════════════════════════════
NEGATIVAS = (
    {
        'NOME': 'P2 · NEGATIVA · AUTORIZAÇÃO DE GASTO',
        'AFROUXA': 'a compra passa a nascer sem autorização que se possa ler',
        'FICHEIRO': CLI,
        'ONDE': "        kw['autorizacao'] = _ag.trial(",
        'PARA': "        _ = _ag.trial(  # mutante: a autorizacao nao chega ao gasto",
        'ESPERA': ('SPEND_NOT_AUTHORIZED',),
    },
    {
        'NOME': 'P3 · NEGATIVA · ORÇAMENTO DE REDE',
        'AFROUXA': 'a corrida deixa de ter tecto de acessos',
        'FICHEIRO': CLI,
        'ONDE': "        'TETO_DE_REDE': 5,",
        'PARA': "        'TETO_DE_REDE': 0,  # mutante",
        'ESPERA': ('NETWORK_BUDGET_EXHAUSTED',),
    },
    {
        'NOME': 'P4 · NEGATIVA · ORÇAMENTO FINANCEIRO',
        'AFROUXA': 'a corrida deixa de ter tecto de gasto',
        'FICHEIRO': CLI,
        'ONDE': "        'TETO_DE_GASTO_USD': 0.10,",
        'PARA': "        'TETO_DE_GASTO_USD': 0.0,  # mutante",
        'ESPERA': ('FINANCIAL_BUDGET_EXHAUSTED',),
    },
)


def _sha(caminho):
    with open(caminho, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def negativas():
    print('\nP2 · P3 · P4 — AS NEGATIVAS, PELA CADEIA CANÓNICA\n' + '-' * 72)
    print('  Cada uma altera o ficheiro REAL, corre a cadeia REAL e exige que')
    print('  ela RECUSE. Um POST que saia aqui é um mutante vivo.\n')
    caminho = os.path.join(RAIZ, CLI)
    original = open(caminho, encoding='utf-8').read()
    sha_antes = _sha(caminho)
    try:
        for m in NEGATIVAS:
            if original.count(m['ONDE']) != 1:
                diz(False, m['NOME'],
                    'ÂNCORA NÃO É ÚNICA (%d) — a mutação não se aplicou'
                    % original.count(m['ONDE']))
                continue
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(original.replace(m['ONDE'], m['PARA'], 1))
            with MundoFalso() as mundo:
                p = pedido_da_fase(com_fonte=True)
                recibo = orq.correr(p, livro=livro_que_autoriza())
                recibo.pop('_plano', None)
                saida = (recibo.get('SAIDA') or '') + (recibo.get('ERROR') or '')
                posts = mundo.posts()
                # A ÚNICA MEDIDA QUE NÃO SE DISCUTE: saiu POST ou não saiu.
                # Ela é lida do `curl` falso, a camada mais funda desta casa.
                diz(len(posts) == 0, m['NOME'] + ' · zero POST de criação',
                    '%d POST(s)' % len(posts))
                diz(any(x in saida for x in m['ESPERA']),
                    m['NOME'] + ' · a recusa tem NOME próprio',
                    ' / '.join(m['ESPERA']))
                limpar_o_que_a_prova_deixou()
    finally:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(original)
    sha_depois = _sha(caminho)
    if sha_antes != sha_depois:
        print('\n  !! O FICHEIRO NÃO FICOU COMO ESTAVA. Verifique à mão: %s' % CLI)
        raise SystemExit(3)
    diz(True, 'o ficheiro mutado voltou ao que era (sha256 confere)',
        sha_depois[:12])


if __name__ == '__main__':
    print('=' * 72)
    print('O FLUXO CANÓNICO DO SCRAP ATRAVESSA? — prova offline, ponta a ponta')
    print('=' * 72)
    with CASA:
        try:
            p0_a_cadeia_esta_ligada()
            p1_positiva()
            negativas()
        finally:
            CASA.repor()
    print('\nA CASA FICOU COMO ESTAVA\n' + '-' * 72)
    sujos = CASA.confere()
    diz(not sujos, 'os livros desta casa voltaram ao que eram',
        ', '.join(sujos) if sujos else '%d ficheiro(s) conferido(s)'
        % len(ESCRITOS_PELA_CADEIA))

    print('\nEXECUÇÃO REAL\n' + '-' * 72)
    print('  REAL_NETWORK         = 0  (o `curl` desta prova não abre socket)')
    print('  APIFY_REAL_RUNS      = 0')
    print('  PAID_REAL_RUNS       = 0')
    print('  META_REAL_REQUESTS   = 0')
    print('  REAL_COST_USD        = 0')
    print('  FONTES_AVALIADAS     = 0  (o livro desta casa não foi tocado)')

    print('\n' + '=' * 72)
    print('PROVAS = %d · FALHAS = %d' % (PROVAS, len(FALHAS)))
    if FALHAS:
        for f in FALHAS:
            print('  !!', f)
        raise SystemExit(1)
    print('FLUXO_CANONICO = PASS · SURVIVORS = 0')
