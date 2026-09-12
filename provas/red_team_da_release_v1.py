#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-RC-01 §12 §14 — ATACAR A RELEASE CANDIDATE NA ÁRVORE FINAL.

    python3 provas/red_team_da_release_v1.py

§12 pede sete portões na porta paga. §14 pede vinte ataques, no mínimo. Correm
juntos e num ficheiro só, porque são a mesma pergunta feita de dois ângulos:

    ESTA ÁRVORE DEIXA ALGUMA COISA NASCER SEM QUEM A DEVIA AUTORIZAR?

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
`subprocess.run` DENTRO do `coleta/coletor.py` — a camada mais funda, por
baixo da guarda, dos dois tetos e do cap do provider. E, para o canário,
`urllib.request.urlopen`. Nada acima deles.

    UM FAKE ACIMA DO GATE MEDE O FAKE.

O falso conta os POSTs que TERIAM saído. Um caso recusado que ele nunca viu é
um caso provado; um que ele viu é uma compra que nasceu.

    APIFY_RUNS = 0 · PAID_USD = 0 · REDE REAL = 0
"""
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('provas', 'coleta', 'leis', 'medidas', 'ferramentas', 'guarda',
           'pedido', 'orquestrador', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

# ⚠️ O BANCO DA PROVA ABRE ANTES DE TUDO, E FORA DO ACERVO. Esta bateria corre
# a rota grátis de verdade, e essa rota GRAVA o bruto. A primeira versão gravou
# no acervo verdadeiro e deixou lá um ficheiro com um handle inventado.
#
#     UMA PROVA QUE ESCREVE NO ACERVO MEDE O QUE ELA PRÓPRIA PÔS LÁ.
BANCO = tempfile.mkdtemp(prefix='rc01-redteam-')
atexit.register(shutil.rmtree, BANCO, True)
os.environ['RC01_MARCA'] = BANCO

import _rc01_mundo_falso as mundo                    # noqa: E402
# ⚠️ O SOCKET FECHA-SE ANTES DE QUALQUER ATAQUE CORRER. A primeira versão
# destas linhas atacou a rota grátis contra um host reservado e o que ela mediu
# foi uma resolução de DNS a falhar — que É uma ida à rede, e esta missão
# declara `REDE REAL = 0`.
#
#     UM ATAQUE QUE SAI PARA A REDE JÁ FALHOU ANTES DE COMEÇAR.
mundo.instalar()

import autorizacao_de_gasto as az                    # noqa: E402
import coletor as ct                                 # noqa: E402
import entradas_do_scrap_v1 as ent                   # noqa: E402
import nenhuma_compra_sem_autorizacao as sr02        # noqa: E402
import relevancia_da_fonte as rel                    # noqa: E402
import scrap_capacidades as cap                      # noqa: E402
import scrap_executor as sx                          # noqa: E402
import scrap_http as http                            # noqa: E402
import social_envelope as envelope                   # noqa: E402
import superficie_do_scrap_v1 as sup                 # noqa: E402

# O bruto desta bateria vai para o banco da prova, e não para `data/samples/`.
# `RAW_DIR` é variável de módulo: quem a reaponta depois ganha. Aqui não há
# outra bateria a correr no mesmo processo, mas a linha fica ao lado do uso
# pela mesma razão que na bateria — o acervo não é lugar de prova.
envelope.RAW_DIR = os.path.join(BANCO, 'raw-free')

SOBREVIVENTES = []
ATAQUES = [0]


def ataque(morreu, nome, detalhe=''):
    """`morreu=True` quer dizer que o ataque FALHOU — que é o que se quer."""
    ATAQUES[0] += 1
    print('  %-5s %-52s %s' % ('ok' if morreu else 'PASSOU', nome[:52],
                               str(detalhe)[:56]))
    if not morreu:
        SOBREVIVENTES.append(nome)


def correr_pago(**kw):
    """A porta paga pelo caminho real, com o `subprocess` falso. → (posts, estado)."""
    return sr02.correr(**kw)


def main():
    print(__doc__.strip().splitlines()[0])
    print('=' * 78)

    # ══════════════════════════════════════════════════════════════════════
    print('\n§12 · OS SETE PORTÕES DA PORTA PAGA')
    # ══════════════════════════════════════════════════════════════════════
    posts, estado = correr_pago()
    ataque(posts == 0, 'G1 · sem autorização nenhuma → POST 0',
           'POSTS=%d · %s' % (posts, estado))

    # G2 · autorização FABRICADA. Sem o selo privado do módulo, o dataclass
    # recusa nascer — e um dicionário com os campos certos não é autorização.
    #
    #     CAMPO PREENCHIDO PELO CHAMADOR != AUTORIZAÇÃO.
    forjada = None
    try:
        forjada = az.Autorizacao(
            motivo=az.COLETA_NORMAL, proposito=sr02.PROPOSITO,
            source_id=sr02.FONTE, max_execucoes=9, max_usd=99.0,
            quem_autorizou='EU', porque='porque sim',
            condicao_de_paragem='nenhuma')
    except Exception as e:                                        # noqa: BLE001
        forjada = e
    ataque(isinstance(forjada, Exception),
           'G2 · autorização fabricada à mão não nasce',
           type(forjada).__name__)
    # E um dicionário com a MESMA forma também não passa na porta.
    posts, estado = correr_pago(autorizacao={
        'motivo': az.COLETA_NORMAL, 'proposito': sr02.PROPOSITO,
        'source_id': sr02.FONTE, 'max_execucoes': 9, 'max_usd': 99.0})
    ataque(posts == 0, 'G2b · dicionário com forma de autorização → POST 0',
           'POSTS=%d · %s' % (posts, estado))

    a = sr02.autorizacao_normal()
    p1, _e1 = correr_pago(autorizacao=a)
    p2, e2 = correr_pago(autorizacao=a)
    ataque(p1 == 1 and p2 == 0, 'G3 · autorização esgotada → POST 0',
           'POST1=%d · POST2=%d · %s' % (p1, p2, e2))

    try:
        sr02.autorizacao_normal(livro=[])
        nasceu = True
    except az.AutorizacaoInvalida:
        nasceu = False
    ataque(not nasceu, 'G4 · relevância ausente → nem autorização nasce',
           'livro vazio · NAO_AVALIADA')

    # G5 · NORMAL sem orçamento financeiro. `teto_usd=None` com `max_usd`
    # declarado é exactamente o buraco `SEM_TETO_NO_FORNECEDOR`.
    a5 = sr02.autorizacao_normal()
    posts, estado = correr_pago(autorizacao=a5, teto_usd=None)
    ataque(posts == 0, 'G5 · sem teto financeiro em NORMAL → POST 0',
           'POSTS=%d · %s' % (posts, estado))

    # G6 · o teto de REDE recusa antes de o socket existir.
    falsa = sr02.FalsaApify(sr02.itens_reais())
    real = subprocess.run
    subprocess.run = falsa
    try:
        a6 = sr02.autorizacao_normal()
        with http.orcamento_de_rede(0), ct.orcamento_financeiro(0.10):
            ct.executar(sr02.ATOR, {'videoUrl': 'https://youtu.be/X'},
                        token='FALSO', run_id='RC01-G6', platform='YOUTUBE',
                        country='IT', mission='RC-01', query='X',
                        source_version='prova', evidence_path='/dev/null',
                        wait=60, salvar_raw=False, autorizacao=a6,
                        teto_usd=a6.max_usd)
        estado = 'EXECUTOU'
    except Exception as e:                                        # noqa: BLE001
        estado = type(e).__name__
    finally:
        subprocess.run = real
    ataque(len(falsa.posts) == 0, 'G6 · teto de rede recusa → POST 0',
           'POSTS=%d · %s' % (len(falsa.posts), estado))

    a7 = sr02.autorizacao_normal()
    posts, estado = correr_pago(autorizacao=a7)
    ataque(posts == 1, 'G7 · todos os portões passam → no máximo 1 POST',
           'POSTS=%d · %s' % (posts, estado))

    # ══════════════════════════════════════════════════════════════════════
    print('\n§14 · OS VINTE ATAQUES')
    # ══════════════════════════════════════════════════════════════════════
    entradas = ent.medir({})
    v1 = [e for e in entradas if e['V1']]

    # A1 · o pedido chama o executor direto
    ataque(all(not any('scrap_executor' in x for x in e['ALVOS']) for e in v1),
           'A1 · entrypoint V1 chama o executor direto',
           '%d entrypoints V1' % len(v1))
    # A2 · o disparador chama o adaptador direto
    ataque(all(not any('adaptador_' in x for x in e['ALVOS']) for e in v1),
           'A2 · entrypoint V1 chama o adaptador direto', 'nenhum')
    # A3 · fonte sem relevância entra em NORMAL
    try:
        az.autorizar(motivo=az.COLETA_NORMAL, proposito='T3',
                     source_id='IT-T3-999', max_execucoes=1, max_usd=0.1,
                     livro=[])
        entrou = True
    except az.AutorizacaoInvalida:
        entrou = False
    ataque(not entrou, 'A3 · fonte sem relevância entra em NORMAL', 'recusada')
    # A4 · URL usada como SOURCE_ID
    try:
        rel.conferir_source_id('https://bsky.app/profile/x')
        passou = True
    except rel.SourceIdInvalido:
        passou = False
    ataque(not passou, 'A4 · URL usada como SOURCE_ID', 'SourceIdInvalido')
    # A5 · DOCUMENT_ID fabricado
    import retorno_da_coleta as rc
    import scrap_colheita as sc
    u = sc.unidade({'URL': 'https://x/y'}, run_id='R', fonte='IT-T9-001')
    ataque(u['DOCUMENT_ID'] == rc.NAO_SEI, 'A5 · DOCUMENT_ID fabricado',
           u['DOCUMENT_ID'])
    # A6 · rota GRÁTIS exige autorização de gasto. Corre-se o canário inteiro
    # SEM passar autorização nenhuma: se a rota grátis exigisse uma, ela parava
    # aqui. O mundo falso serve esta rota, e mais nenhuma.
    #
    #     UMA ROTA GRATUITA NÃO PRECISA DE AUTORIZAÇÃO DE GASTO
    #     PORQUE NÃO EXISTE GASTO.
    objetos, trace = sx.COLLECT(platform='BLUESKY',
                                capability='bluesky.author.incremental',
                                run_id='RC01-A6', limit=1,
                                handle=mundo.FEED['feed'][0]['post']['author']['handle'])
    ataque(len(objetos or []) == 1
           and 'AUTORIZACAO' not in str(trace.get('RESULT') or ''),
           'A6 · rota grátis exige autorização de gasto',
           '%d objetos · %s' % (len(objetos or []), trace.get('RESULT')))
    # A7 · rota PAGA não exige autorização — já é o G1, contado de novo por
    # ser um ataque distinto na lista da §14.
    posts, estado = correr_pago()
    ataque(posts == 0, 'A7 · rota paga sem autorização',
           'POSTS=%d · %s' % (posts, estado))
    # A8 · autorização fabricada (o par do G2, pelo caminho do consumo)
    try:
        az.conferir_e_consumir({'motivo': az.COLETA_NORMAL},
                               motivo=az.COLETA_NORMAL,
                               proposito=sr02.PROPOSITO, source_id=sr02.FONTE,
                               teto_usd=0.1)
        passou = True
    except Exception:                                             # noqa: BLE001
        passou = False
    ataque(not passou, 'A8 · autorização fabricada no consumo', 'recusada')
    # A9 · autorização reutilizada (o par do G3)
    a9 = sr02.autorizacao_normal()
    correr_pago(autorizacao=a9)
    posts, estado = correr_pago(autorizacao=a9)
    ataque(posts == 0, 'A9 · autorização reutilizada',
           'POSTS=%d · %s' % (posts, estado))
    # A10 · orçamento financeiro MAIOR que a autorização humana
    a10 = sr02.autorizacao_normal()
    posts, estado = correr_pago(autorizacao=a10, teto_usd=a10.max_usd * 100)
    ataque(posts == 0, 'A10 · teto maior que a autorização humana',
           'POSTS=%d · %s' % (posts, estado))
    # A11 · transporte alternativo salta a guarda
    ataque(getattr(ct, '_CURL_DA_CASA', None) is not None
           and ct._curl is ct._CURL_DA_CASA,
           'A11 · transporte alternativo salta a guarda',
           'o coletor fixa o próprio transporte')
    # A12 · a retentativa duplica o POST
    ataque(hasattr(ct, 'PostTalvezCriado'),
           'A12 · a retentativa duplica o POST',
           'REPETIR UM POST É COMPRAR DE NOVO')
    # A13 · política diz ROUTE_NOT_ALLOWED e um fallback executa
    objetos, trace = sx.COLLECT(platform='YOUTUBE', capability='youtube.media',
                                run_id='RC01-A13')
    ataque(not objetos, 'A13 · política recusa e um fallback executa',
           '%d objetos · %s' % (len(objetos or []), trace.get('RESULT')))
    # A14 · UNKNOWN vira ZERO_RESULTS
    pronto = sx.CHECK('BLUESKY', 'bluesky.capacidade.que.nao.existe')
    ataque(pronto['CAPABILITY_STATE'] == cap.UNKNOWN and not pronto['CAN'],
           'A14 · UNKNOWN vira ZERO_RESULTS', pronto['CAPABILITY_STATE'])
    # A15 · ERROR vira REJECTED
    # ⚠️ A PRIMEIRA VERSÃO DESTE ATAQUE INVENTOU A LEI QUE IA MEDIR: pediu que
    # `ROUTE_NOT_ALLOWED` NÃO fosse falha. `leis/falhas.py` diz que é — e é o
    # dono. Medi o que eu imaginei que ele diria, e não o que ele diz.
    #
    #     UMA SONDA QUE ADIVINHA O VOCABULÁRIO DE OUTRO DONO
    #     MEDE O QUE ELA IMAGINOU QUE ELE DIRIA.
    #
    # O ataque verdadeiro é o outro: um ERRO que se disfarça de resultado. Um
    # host que cai tem de sair do outro lado como falha, e nunca como «a fonte
    # não tinha nada» — que é o que faria a casa arquivar um silêncio técnico
    # como se fosse uma medição da fonte.
    #
    #     ESGOTAR, CAIR E SER RECUSADO NÃO É A FONTE ESTAR VAZIA.
    import falhas as fx
    objetos15, trace15 = sx.COLLECT(platform='MASTODON',
                                    capability='mastodon.hashtag.search',
                                    run_id='RC01-A15', instancia='nao.servido',
                                    tag='t', limit=1)
    resultado15 = str(trace15.get('RESULT') or '')
    ataque(not objetos15 and resultado15 not in fx.NAO_SAO_FALHA
           and fx.e_falha(resultado15),
           'A15 · ERROR vira ZERO_RESULTS / REJECTED', resultado15)
    # A16 · capacidade declarada SEM aresta aparece READY
    linhas = sup.medir()
    sem_aresta = [l for l in linhas
                  if l['V1'] == sup.READY and not l['EDGE_EXISTS']]
    ataque(not sem_aresta, 'A16 · declarada sem aresta aparece READY',
           [l['CAPABILITY'] for l in sem_aresta][:2] or 'nenhuma')
    # A17 · aresta SEM execução aparece como fluxo observado
    ataque(all('FLOW_OBSERVED' not in str(l.get('V1')) for l in linhas),
           'A17 · aresta sem corrida vira FLOW_OBSERVED',
           'a superfície não promete fluxo observado')
    # A18/A19 · uma linha externa em movimento é absorvida
    import subprocess as sp
    log = sp.run(['git', '-C', RAIZ, 'log', '--oneline', '-40'],
                 capture_output=True, text=True).stdout.lower()
    ataque('meta-op' not in log, 'A18 · branch Meta em movimento é absorvida',
           'nenhum commit META-OP no histórico')
    ataque('linkedin-op' not in log,
           'A19 · branch LinkedIn em movimento é absorvida',
           'nenhum commit LINKEDIN-OP no histórico')
    # A20 · legado fora da V1 contado como bypass operacional
    bypasses = [e for e in entradas if e['ESTADO'] == 'ACTIVE_V1_BYPASS']
    legado = [e for e in entradas if e['ESTADO'] == 'NOT_IN_V1']
    ataque(not bypasses and len(legado) > 0,
           'A20 · legado fora da V1 conta como bypass',
           '%d legado · %d bypass' % (len(legado), len(bypasses)))

    print('\n' + '=' * 78)
    print('ATTACKS = %d' % ATAQUES[0])
    print('SURVIVING_ATTACKS = %d' % len(SOBREVIVENTES))
    for s in SOBREVIVENTES:
        print('  · %s' % s)
    print('APIFY_RUNS = 0 · PAID_USD = 0 · REDE REAL = 0')
    return 0 if not SOBREVIVENTES else 1


if __name__ == '__main__':
    sys.exit(main())
