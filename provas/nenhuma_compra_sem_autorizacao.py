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


def autorizacao_sim(sid=FONTE, prop=PROPOSITO):
    """O veredito que `leis/relevancia_da_fonte.portao()` devolveria.

    ⚠️ CONSTRUÍDO AQUI, e é essa a prova de que o SCRAP NÃO o calcula: esta
    linhagem não tem o livro nem a lei, e não precisa de nenhum dos dois para
    obedecer ao veredito.

        O GUARDA CONFERE O BILHETE. ELE NÃO É O DONO DO ESPECTÁCULO.
    """
    return {'VEREDITO': az.AUTORIZA, 'SOURCE_ID': sid, 'PROPOSITO': prop,
            'ESTADO_DA_RELEVANCIA': az.SIM, 'VERSAO_DO_PORTAO': '1',
            'CONTRATO': 'RELEVANCIA_DA_FONTE/v1',
            'DECISAO': {'EVIDENCIA': {'FICHEIRO': 'LIVRO-DE-RELEVANCIA'}}}


def correr(**kw):
    """Corre `coletor.executar` pelo caminho real. → (posts, estado)."""
    falsa = FalsaApify(itens_reais())
    real = subprocess.run
    subprocess.run = falsa
    try:
        with http.orcamento_de_rede(5), ct.orcamento_financeiro(0.10):
            ct.executar(ATOR, {'videoUrl': 'https://youtu.be/X'},
                        token='FALSO', run_id='PROVA-SR02',
                        platform='YOUTUBE', country='IT', mission='SR-02',
                        query='X', source_version='prova',
                        evidence_path='/dev/null', wait=60, salvar_raw=False,
                        **kw)
        return len(falsa.posts), 'EXECUTOU'
    except az.SemAutorizacaoDeGasto as e:
        return len(falsa.posts), e.estado
    except Exception as e:                                        # noqa: BLE001
        return len(falsa.posts), '%s: %s' % (type(e).__name__, str(e)[:40])
    finally:
        subprocess.run = real


def main():
    print(__doc__.strip().splitlines()[0])
    print('=' * 74)

    print('\n1 · NORMAL COLLECTION — oito casos, pelo caminho real')
    casos = [
        ('N1 SIM · fonte A · T3',
         dict(modo=az.NORMAL, autorizacao=autorizacao_sim(),
              source_id=FONTE, proposito=PROPOSITO), 1),
        ('N2 SIM T3 usado em T9',
         dict(modo=az.NORMAL, autorizacao=autorizacao_sim(),
              source_id=FONTE, proposito='T9'), 0),
        ('N3 NAO',
         dict(modo=az.NORMAL, source_id=FONTE, proposito=PROPOSITO,
              autorizacao=dict(autorizacao_sim(), VEREDITO=az.BARRA,
                               ESTADO_DA_RELEVANCIA=az.NAO)), 0),
        ('N4 NAO_SEI',
         dict(modo=az.NORMAL, source_id=FONTE, proposito=PROPOSITO,
              autorizacao=dict(autorizacao_sim(), VEREDITO=az.EXIGE_AVALIACAO,
                               ESTADO_DA_RELEVANCIA=az.NAO_SEI)), 0),
        ('N5 ERRO',
         dict(modo=az.NORMAL, source_id=FONTE, proposito=PROPOSITO,
              autorizacao=dict(autorizacao_sim(), VEREDITO=az.EXIGE_AVALIACAO,
                               ESTADO_DA_RELEVANCIA=az.ERRO)), 0),
        ('N6 NAO_AVALIADA',
         dict(modo=az.NORMAL, source_id=FONTE, proposito=PROPOSITO,
              autorizacao=dict(autorizacao_sim(), VEREDITO=az.EXIGE_AVALIACAO,
                               ESTADO_DA_RELEVANCIA=az.NAO_AVALIADA)), 0),
        ('N7 autorização da fonte A, compra da fonte B',
         dict(modo=az.NORMAL, autorizacao=autorizacao_sim(),
              source_id='IT-T3-999', proposito=PROPOSITO), 0),
        ('N8 URL no lugar de SOURCE_ID',
         dict(modo=az.NORMAL, autorizacao=autorizacao_sim(sid='https://a.it'),
              source_id='https://a.it', proposito=PROPOSITO), 0),
    ]
    for nome, kw, esperado in casos:
        posts, estado = correr(**kw)
        diz(posts == esperado, nome, 'POSTS=%d · %s' % (posts, estado))

    print('\n2 · SEM AUTORIZAÇÃO NENHUMA — o silêncio não autoriza')
    posts, estado = correr()
    diz(posts == 0, 'chamada sem `autorizacao`', 'POSTS=%d · %s' % (posts, estado))

    print('\n3 · SOURCE EVALUATION PROBE — candidata NAO_AVALIADA')
    probe = {'AUTORIZACAO_HUMANA': 'SR-02 · prova offline',
             'MAX_PROVIDER_RUNS': 1, 'MAX_START_POSTS': 1,
             'MAX_USD': 0.05, 'MAX_ITEMS': 10}
    posts, estado = correr(modo=az.PROBE, autorizacao=probe)
    diz(posts == 1, 'probe autorizado chega ao provider falso',
        'POSTS=%d · %s' % (posts, estado))
    recibo = az.pode_comprar(modo=az.PROBE, autorizacao=probe)
    diz(recibo['PROMOTES_RELEVANCE'] is False,
        'probe NÃO promove relevância', 'PROMOTES_RELEVANCE=%s'
        % recibo['PROMOTES_RELEVANCE'])
    diz(recibo['SOURCE_RELEVANCE_CONSULTED'] is False,
        'probe não consulta relevância nenhuma', 'é essa a razão de existir')
    for falta in ('MAX_USD', 'MAX_PROVIDER_RUNS', 'MAX_START_POSTS',
                  'MAX_ITEMS', 'AUTORIZACAO_HUMANA'):
        magro = {k: v for k, v in probe.items() if k != falta}
        posts, estado = correr(modo=az.PROBE, autorizacao=magro)
        diz(posts == 0, 'probe sem %s' % falta, 'POSTS=%d · %s' % (posts, estado))

    print('\n4 · CAPABILITY TRIAL — o que a C10.8B já usava')
    trial = {'AUTORIZACAO_HUMANA': 'C10.8B-LIVE', 'MAX_PROVIDER_RUNS': 1,
             'MAX_START_POSTS': 1, 'MAX_USD': 0.10}
    posts, estado = correr(modo=az.TRIAL, autorizacao=trial)
    diz(posts == 1, 'trial autorizado continua a correr',
        'POSTS=%d · %s' % (posts, estado))
    posts, estado = correr(modo=az.TRIAL, autorizacao=None)
    diz(posts == 0, 'trial sem autorização humana', 'POSTS=%d · %s' % (posts, estado))

    print('\n5 · NORMAL NÃO SE VESTE DE TRIAL NEM DE PROBE')
    # O ataque: uma coleta normal sem «sim» que troca o modo para escapar. Ela
    # só escapa se conseguir tambem trazer a autorizacao humana — e essa e
    # exactamente a coisa que ela nao tem.
    posts, estado = correr(modo=az.TRIAL, autorizacao=autorizacao_sim(),
                           source_id=FONTE, proposito=PROPOSITO)
    diz(posts == 0, 'NORMAL→TRIAL com veredito de relevância no lugar dos limites',
        'POSTS=%d · %s' % (posts, estado))
    posts, estado = correr(modo=az.PROBE, autorizacao=autorizacao_sim(),
                           source_id=FONTE, proposito=PROPOSITO)
    diz(posts == 0, 'NORMAL→PROBE com veredito no lugar dos limites',
        'POSTS=%d · %s' % (posts, estado))

    print('\n' + '=' * 74)
    print('APIFY_REAL_RUNS = 0 · PAID_USD = 0 · REDE REAL = 0')
    print('FALHAS = %d' % len(FALHAS))
    for f in FALHAS:
        print('  · %s' % f)
    return 0 if not FALHAS else 1


if __name__ == '__main__':
    sys.exit(main())
