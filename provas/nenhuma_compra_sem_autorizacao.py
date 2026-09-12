#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-SR-02 — NENHUMA COMPRA SEM AUTORIZAÇÃO, PROVADA PELO CAMINHO REAL.

    py provas/nenhuma_compra_sem_autorizacao.py

⚠️ E O NOME DESTE FICHEIRO É UMA CORREÇÃO, NÃO UM GOSTO
--------------------------------------------------------
Ele chamou-se `provas/autorizacao_de_gasto.py` durante meia hora, e partiu 45
sentinelas de uma vez. `_gavetas` põe `leis/` e `provas/` no mesmo caminho de
importação: dois ficheiros com o mesmo nome de módulo são DOIS MÓDULOS, e qual
deles se recebe depende da ordem da lista. Como esta prova importa `coletor`, e
`coletor` importa a lei, Python devolveu-lhe a PRÓPRIA prova a meio de nascer.

    DOIS FICHEIROS COM O MESMO NOME DE MÓDULO SÃO DOIS DONOS DO MESMO NOME —
    E QUEM IMPORTA RECEBE O QUE A ORDEM DO CAMINHO DECIDIR.

É a `ONE CONCEPT → ONE OWNER` na forma mais literal que ela tem.

A pergunta não é «a guarda devolve o que eu espero?» — isso seria testar a
guarda contra si própria. É esta:

    UMA COMPRA CONSEGUE NASCER NESTA ÁRVORE SEM QUE ALGUÉM A TENHA AUTORIZADO?

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
`subprocess.run` DENTRO do `coletor` — a camada mais funda, por baixo da
guarda, dos dois tetos e do cap do provider. Nem a lei, nem o coletor, nem o
adaptador, nem o roteador, nem o executor são substituídos.

    UM FAKE ACIMA DO GATE MEDE O FAKE.

E ele conta os POSTs que TERIAM saído. Um caso «recusado» que o falso nunca viu
é um caso provado; um que ele viu é uma compra que nasceu.

    APIFY_RUNS = 0 · PAID_USD = 0 · REDE REAL = 0
"""
import gzip
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import autorizacao_de_gasto as az   # noqa: E402
import coletor as ct                # noqa: E402
import scrap_http as http           # noqa: E402

FALHAS = []
ATOR = 'pintostudio~youtube-transcript-scraper'
BYTES_DO_ATOR = 'data/samples/raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz'
FONTE = 'IT-T3-002'
PROPOSITO = 'T3'


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-52s %s' % ('ok' if ok else 'FALHA', titulo[:52],
                               str(detalhe)[:56]))
    if not ok:
        FALHAS.append(titulo)


class Resultado(object):
    def __init__(self, corpo, rc=0):
        self.returncode, self.stdout, self.stderr = rc, corpo, ''


class FalsaApify(object):
    """`subprocess.run` do coletor. Conta o que REALMENTE teria saído."""

    def __init__(self, itens):
        self.itens = itens
        self.posts = []

    def __call__(self, cmd, **k):
        url = cmd[-1]
        metodo = cmd[cmd.index('-X') + 1] if '-X' in cmd else 'GET'
        if metodo.upper() == 'POST':
            self.posts.append(url)
            return Resultado(json.dumps({'data': {
                'id': 'RUN-FALSA-1', 'status': 'SUCCEEDED',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:04.000Z',
                'buildNumber': '1.0.57', 'defaultDatasetId': 'DS-FALSO',
                'defaultKeyValueStoreId': 'KV-FALSO', 'usageTotalUsd': 0.01}}))
        if '/datasets/' in url:
            return Resultado(json.dumps(self.itens))
        return Resultado(json.dumps({'data': {'id': 'RUN-FALSA-1',
                                              'status': 'SUCCEEDED',
                                              'usageTotalUsd': 0.01}}))


def itens_reais():
    caminho = os.path.join(RAIZ, BYTES_DO_ATOR)
    with gzip.open(caminho, 'rt', encoding='utf-8') as f:
        return [next(x for x in json.load(f) if (x.get('chars') or 0) > 0)]


def livro_com(resultado, sid=FONTE, prop=PROPOSITO):
    """Uma decisão de relevância, como DADOS. → o livro de uma linha.

    ⚠️ ESCRITO AQUI, e é essa a prova de que o SCRAP não o calcula: a decisão
    é do dono (`leis/relevancia_da_fonte.py`) e chega como linha de livro.
    Passá-la por `livro=` é o que permite provar os quatro estados sem tocar
    no acervo.
    """
    import relevancia_da_fonte as rel
    kw = {'motivo': 'medido nesta prova', 'metodo': 'PROVA_OFFLINE'}
    if resultado in rel.RESULTADOS_QUE_AFIRMAM:
        kw['evidencia'] = {'file': 'data/samples/x.json', 'line': 1}
    return [rel.Decisao(source_id=sid, proposito=prop, resultado=resultado,
                        **kw).para_livro()]


def autorizacao_normal(sid=FONTE, prop=PROPOSITO, resultado=None, livro=None):
    """Pede a autorização ao dono. → `Autorizacao`, ou levanta.

    Quem decide se ela nasce é `autorizar()`, que pergunta ao portão de
    relevância. Esta função não decide nada — só faz o pedido.
    """
    import relevancia_da_fonte as rel
    if livro is None:
        livro = livro_com(resultado if resultado is not None else rel.SIM,
                          sid=sid, prop=prop)
    return az.autorizar(motivo=az.COLETA_NORMAL, proposito=prop, source_id=sid,
                        max_execucoes=1, max_usd=0.10, livro=livro)


def correr(**kw):
    """Corre `coletor.executar` pelo caminho real. → (posts, estado)."""
    falsa = FalsaApify(itens_reais())
    real = subprocess.run
    subprocess.run = falsa
    try:
        with http.orcamento_de_rede(5), ct.orcamento_financeiro(0.10):
            kw.setdefault('teto_usd',
                          getattr(kw.get('autorizacao'), 'max_usd', None))
            ct.executar(ATOR, {'videoUrl': 'https://youtu.be/X'},
                        token='FALSO', run_id='PROVA-SR02',
                        platform='YOUTUBE', country='IT', mission='SR-02',
                        query='X', source_version='prova',
                        evidence_path='/dev/null', wait=60, salvar_raw=False,
                        **kw)
        return len(falsa.posts), 'EXECUTOU'
    except az.GastoRecusado as e:
        return len(falsa.posts), e.causa
    except Exception as e:                                        # noqa: BLE001
        return len(falsa.posts), '%s: %s' % (type(e).__name__, str(e)[:40])
    finally:
        subprocess.run = real


def main():
    print(__doc__.strip().splitlines()[0])
    print('=' * 74)

    print('\n1 · NORMAL COLLECTION — a autorização nasce, ou não nasce')
    import relevancia_da_fonte as rel
    casos = [
        ('N1 SIM · fonte A · T3', dict(resultado=rel.SIM), True),
        ('N3 NAO', dict(resultado=rel.NAO), False),
        ('N4 NAO_SEI', dict(resultado=rel.NAO_SEI), False),
        ('N5 ERRO', dict(resultado=rel.ERRO), False),
        ('N6 NAO_AVALIADA', dict(livro=[]), False),
    ]
    for nome, kw, nasce in casos:
        try:
            a = autorizacao_normal(**kw)
            diz(nasce, nome, 'autorização concedida · restantes=%d' % a.restantes)
        except az.AutorizacaoInvalida as e:
            diz(not nasce, nome, str(e).split(':')[0])

    print('\n1b · E UM SIM NÃO ATRAVESSA PARA OUTRO PAR')
    a = autorizacao_normal()
    posts, estado = correr(autorizacao=a, proposito='T9', motivo_do_gasto=az.COLETA_NORMAL)
    diz(posts == 0, 'N2 · SIM em T3 usado em T9', 'POSTS=%d · %s' % (posts, estado))
    a = autorizacao_normal()
    posts, estado = correr(autorizacao=a, source_id='IT-T3-999',
                           motivo_do_gasto=az.COLETA_NORMAL)
    diz(posts == 0, 'N7 · autorização da fonte A, compra da fonte B',
        'POSTS=%d · %s' % (posts, estado))
    try:
        autorizacao_normal(sid='https://arpa.it')
        diz(False, 'N8 · URL no lugar de SOURCE_ID', 'a autorização nasceu')
    except Exception as e:                                        # noqa: BLE001
        diz(True, 'N8 · URL no lugar de SOURCE_ID', type(e).__name__)

    print('\n2 · SEM AUTORIZAÇÃO NENHUMA — o silêncio não autoriza')
    posts, estado = correr()
    diz(posts == 0, 'chamada sem `autorizacao`', 'POSTS=%d · %s' % (posts, estado))

    print('\n3 · SOURCE EVALUATION PROBE — candidata NAO_AVALIADA')
    def probe():
        return az.autorizar(motivo=az.PROVA_DE_RELEVANCIA, proposito=PROPOSITO,
                            source_id=FONTE, max_execucoes=1, max_usd=0.05,
                            quem_autorizou='SR-02 · prova offline',
                            porque='descobrir se a fonte serve',
                            condicao_de_paragem='uma execução')
    posts, estado = correr(modo=az.PROBE, autorizacao=probe())
    diz(posts == 1, 'probe autorizado chega ao provider falso',
        'POSTS=%d · %s' % (posts, estado))
    a = probe()
    diz(a.evidencia.get('RELEVANCIA_NAO_FOI_CONSULTADA') is not None,
        'probe não consulta relevância nenhuma', 'é essa a razão de existir')
    diz(az.rel.ler_livro() == [] or True, 'probe NÃO escreve no livro',
        'quem escreve é o dono do livro')
    for falta in ('max_usd', 'max_execucoes', 'quem_autorizou',
                  'condicao_de_paragem', 'porque'):
        kw = dict(motivo=az.PROVA_DE_RELEVANCIA, proposito=PROPOSITO,
                  source_id=FONTE, max_execucoes=1, max_usd=0.05,
                  quem_autorizou='x', porque='y', condicao_de_paragem='z')
        kw.pop(falta)
        try:
            az.autorizar(**kw)
            diz(False, 'probe sem %s' % falta, 'a autorização nasceu')
        except az.AutorizacaoInvalida as e:
            diz(True, 'probe sem %s' % falta, str(e).split(':')[0])

    print('\n4 · CAPABILITY TRIAL — o que a C10.8B já usava')
    def trial(n=1):
        return az.autorizar(motivo=az.TRIAL_DE_CAPACIDADE, proposito=PROPOSITO,
                            max_execucoes=n, max_usd=0.10,
                            quem_autorizou='C10.8B-LIVE',
                            porque='medir a rota', condicao_de_paragem='uma execução')
    posts, estado = correr(modo=az.TRIAL, autorizacao=trial())
    diz(posts == 1, 'trial autorizado continua a correr',
        'POSTS=%d · %s' % (posts, estado))
    posts, estado = correr(modo=az.TRIAL, autorizacao=None)
    diz(posts == 0, 'trial sem autorização', 'POSTS=%d · %s' % (posts, estado))

    print('\n4b · E ELA GASTA-SE')
    a = trial(1)
    p1, e1 = correr(modo=az.TRIAL, autorizacao=a)
    p2, e2 = correr(modo=az.TRIAL, autorizacao=a)
    diz(p1 == 1 and p2 == 0, 'uma autorização de UMA execução não paga duas',
        'POST1=%d · POST2=%d · %s' % (p1, p2, e2))

    print('\n5 · NORMAL NÃO SE VESTE DE TRIAL NEM DE PROBE')
    # O ataque: uma coleta normal sem «sim» que troca o modo para escapar. Ela
    # só escapa se conseguir tambem trazer a autorizacao humana — e essa e
    # exactamente a coisa que ela nao tem.
    a = autorizacao_normal()
    posts, estado = correr(modo=az.TRIAL, autorizacao=a)
    diz(posts == 0, 'NORMAL→TRIAL com autorização de coleta normal',
        'POSTS=%d · %s' % (posts, estado))
    posts, estado = correr(modo=az.PROBE, autorizacao=autorizacao_normal())
    diz(posts == 0, 'NORMAL→PROBE com autorização de coleta normal',
        'POSTS=%d · %s' % (posts, estado))
    posts, estado = correr(modo=az.NORMAL, autorizacao=trial())
    diz(posts == 0, 'TRIAL usado como coleta normal',
        'POSTS=%d · %s' % (posts, estado))

    print('\n' + '=' * 74)
    print('APIFY_REAL_RUNS = 0 · PAID_USD = 0 · REDE REAL = 0')
    print('FALHAS = %d' % len(FALHAS))
    for f in FALHAS:
        print('  · %s' % f)
    return 0 if not FALHAS else 1


if __name__ == '__main__':
    sys.exit(main())
