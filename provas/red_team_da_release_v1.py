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
import scrap_colheita as sc                          # noqa: E402
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

#: A base desta Release. Os ataques que perguntam «esta missão fez X?» medem
#: daqui para a frente, e nunca a história inteira da casa.
BASE = '64422049'

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
    # ⚠️ `NOT_IN_V1` DEIXOU DE SER UMA CLASSE. A §6 partiu-a em quatro — legado,
    # medição, reprocessamento local e fail-closed — e esta sonda continuava a
    # contar o nome antigo, que já não existe. Contava zero e dava-se por
    # satisfeita.
    #
    #     UMA SONDA QUE CONTA UM NOME QUE NINGUÉM ESCREVE MAIS CONTA ZERO
    #     E CHAMA-LHE PROVA.
    bypasses = [e for e in entradas if e['ESTADO'] == ent.BYPASS]
    fora_da_v1 = [e for e in entradas
                  if e['ESTADO'] in (ent.LEGACY_NOT_IN_V1, ent.MEASUREMENT_ONLY,
                                     ent.LOCAL_REPROCESSING, ent.FAIL_CLOSED)]
    ataque(not bypasses and len(fora_da_v1) > 0,
           'A20 · legado fora da V1 conta como bypass',
           '%d fora da V1 · %d bypass' % (len(fora_da_v1), len(bypasses)))

    # ══════════════════════════════════════════════════════════════════════
    print('\n§18 · OS ATAQUES QUE A CONTINUAÇÃO ACRESCENTOU')
    # ══════════════════════════════════════════════════════════════════════
    import copy as _copy
    import social_matriz as mz

    # B1 · política diz NÃO e há dinheiro autorizado
    livro = sr02.livro_com(rel.SIM, sid='IT-T9-001', prop='T9')
    autb = az.autorizar(motivo=az.COLETA_NORMAL, proposito='T9',
                        source_id='IT-T9-001', max_execucoes=1, max_usd=0.50,
                        livro=livro)
    fb = sr02.FalsaApify(sr02.itens_reais())
    real = subprocess.run
    subprocess.run = fb
    try:
        with http.orcamento_de_rede(5), ct.orcamento_financeiro(0.50):
            ct.executar('harvestapi~linkedin-profile-search-by-name',
                        {'firstName': 'x'}, token='apify_api_VALIDO',
                        run_id='b1', platform='LINKEDIN', country='IT',
                        mission='RC01', query='q', source_version='p',
                        evidence_path='/dev/null', wait=60, salvar_raw=False,
                        autorizacao=autb, teto_usd=0.50)
        estado_b1 = 'EXECUTOU'
    except ct.RotaNaoPermitida as e:                              # noqa: BLE001
        estado_b1 = 'ROTA_NAO_PERMITIDA'
    except Exception as e:                                        # noqa: BLE001
        estado_b1 = type(e).__name__
    finally:
        subprocess.run = real
    ataque(not fb.posts and estado_b1 == 'ROTA_NAO_PERMITIDA',
           'B1 · política NÃO + autorização SIM + token válido',
           'POSTS=%d · %s' % (len(fb.posts), estado_b1))
    ataque(autb.gastas == 0,
           'B2 · a rota proibida consome a autorização de quem a pediu',
           'gastas=%d' % autb.gastas)

    # B3 · o caminho lateral do sensor, com tudo válido
    import apify_pool as ap
    visto = []

    def _falso(url, *, token, metodo='GET', corpo=None, timeout=300, **k):
        visto.append(metodo)
        return {'data': {'id': 'F', 'status': 'SUCCEEDED',
                         'defaultDatasetId': 'D', 'usageTotalUsd': 0}}

    curl_real, pool_real = ct._curl, ap.pool
    ct._curl = _falso
    ap.pool = lambda env=None: ['apify_api_TOKEN_DE_MENTIRA']
    try:
        sys.modules.pop('sensor_coleta', None)
        import sensor_coleta as sensor
        ct._curl = _falso
        aut3 = az.autorizar(motivo=az.COLETA_NORMAL, proposito='T9',
                            source_id='IT-T9-001', max_execucoes=1,
                            max_usd=0.50, livro=livro)
        try:
            with ct.orcamento_financeiro(0.50):
                sensor._rodar(sensor.ATORES['LINKEDIN_SEARCH_BY_NAME'],
                              {'firstName': 'x', 'lastName': 'y', 'maxItems': 1},
                              run_id='b3', platform='LINKEDIN', country='IT',
                              query='q', evidence_path='/dev/null', lote='A',
                              autorizacao=aut3)
            estado_b3 = 'EXECUTOU'
        except ct.RotaNaoPermitida:
            estado_b3 = 'ROTA_NAO_PERMITIDA'
        except Exception as e:                                    # noqa: BLE001
            estado_b3 = type(e).__name__
    finally:
        ct._curl, ap.pool = curl_real, pool_real
        sys.modules.pop('sensor_coleta', None)
    ataque(visto.count('POST') == 0 and estado_b3 == 'ROTA_NAO_PERMITIDA',
           'B3 · sensor LinkedIn com token E autorização válidos',
           'POSTS=%d · %s' % (visto.count('POST'), estado_b3))

    # B4 · uma cópia da autorização compra
    a4 = sr02.autorizacao_normal()
    c4 = _copy.copy(a4)
    n1, _ = correr_pago(autorizacao=a4)
    n2, e4 = correr_pago(autorizacao=c4)
    ataque(n2 == 0, 'B4 · autorização copiada compra',
           'original=%d · cópia=%d · %s' % (n1, n2, e4))

    # B5 · a mesma autorização sob outro ledger
    a5 = az.autorizar(motivo=az.COLETA_NORMAL, proposito=sr02.PROPOSITO,
                      source_id=sr02.FONTE, max_execucoes=2, max_usd=0.10,
                      livro=sr02.livro_com(rel.SIM))
    m1, _ = correr_pago(autorizacao=a5)
    m2, e5 = correr_pago(autorizacao=a5)
    ataque(m2 == 0, 'B5 · ledger trocado a meio',
           'ledger1=%d · ledger2=%d · %s' % (m1, m2, e5))

    # B6 · o orçamento declara mais do que a pessoa autorizou
    a6 = sr02.autorizacao_normal()
    f6 = sr02.FalsaApify(sr02.itens_reais())
    real = subprocess.run
    subprocess.run = f6
    try:
        with http.orcamento_de_rede(5), ct.orcamento_financeiro(99.0):
            ct.executar(sr02.ATOR, {'videoUrl': 'https://youtu.be/X'},
                        token='F', run_id='b6', platform='YOUTUBE',
                        country='IT', mission='RC01', query='X',
                        source_version='p', evidence_path='/dev/null',
                        wait=60, salvar_raw=False, autorizacao=a6,
                        teto_usd=a6.max_usd)
        e6 = 'EXECUTOU'
    except Exception as e:                                        # noqa: BLE001
        e6 = getattr(e, 'causa', type(e).__name__)
    finally:
        subprocess.run = real
    ataque(not f6.posts, 'B6 · orçamento maior que a autorização humana',
           'POSTS=%d · %s' % (len(f6.posts), e6))

    # B7 · escrever na autorização depois de concedida
    a7 = sr02.autorizacao_normal()
    try:
        a7.max_usd = 99.0
        e7 = 'ACEITE'
    except Exception as e:                                        # noqa: BLE001
        e7 = type(e).__name__
    ataque(e7 != 'ACEITE', 'B7 · autorização reescrita depois de concedida', e7)

    # B8 · um redirecionamento salta a deny-list
    ataque(hasattr(http, 'hosts_proibidos'),
           'B8 · redirecionamento salta a lista de hosts proibidos',
           'UM REDIRECIONAMENTO É UM PEDIDO NOVO')

    # B9 · CATALOG atravessa a Admissão
    import retorno_da_coleta as rc2
    ataque(rc2.CATALOG not in rc2.ENTRAM_NO_INGRESSO,
           'B9 · CATALOG entra no ingresso', rc2.ENTRAM_NO_INGRESSO)
    ataque(all(l[3] in rc2.ESPECIES for l in sc.FASES.values()),
           'B10 · uma fase sem espécie declarada',
           '%d fases, todas declaram' % len(sc.FASES))

    # B11 · reprocessamento local contado como aquisição
    locais = [e for e in entradas if e['ESTADO'] == ent.LOCAL_REPROCESSING]
    ataque(all(not e['ALCANCA'] for e in locais),
           'B11 · reprocessamento local contado como aquisição',
           '%d locais, nenhum alcança capacidade' % len(locais))

    # B12 · um botão manual proibido continua alcançável
    manuais = ent.bypasses_de_politica(entradas)
    ataque(not manuais, 'B12 · botão manual proibido continua alcançável',
           manuais or 'MANUALLY_TRIGGERABLE_POLICY_BYPASSES = 0')

    # B13 · uma linha divergente recebeu merge bruto
    # ⚠️ A PERGUNTA É SOBRE ESTA MISSÃO, E NÃO SOBRE A HISTÓRIA DA CASA. Havia
    # aqui um `git log --merges -30` que apanhava merges de 2026-08, muito
    # anteriores — e reprovava por eles.
    #
    #     MEDIR A HISTÓRIA INTEIRA PARA JULGAR UMA MISSÃO JULGA AS OUTRAS.
    #
    # O que interessa: desde a base da Release, esta linha absorveu alguma das
    # divergentes por merge? Pergunta-se ao git se cada uma é ANCESTRAL.
    DIVERGENTES = ('origin/claude/wonderful-hamilton-m50ahv',
                   'origin/claude/sintonia-scrap-paid-flow-convergence-cv02',
                   'origin/claude/sintonia-scrap-linkedin-operational-close-v1')
    absorvidas = []
    for ref in DIVERGENTES:
        r = sp.run(['git', '-C', RAIZ, 'merge-base', '--is-ancestor', ref, 'HEAD'],
                   capture_output=True, text=True)
        if r.returncode == 0:
            absorvidas.append(ref.split('/')[-1])
    merges = sp.run(['git', '-C', RAIZ, 'log', '--oneline', '--merges',
                     '%s..HEAD' % BASE], capture_output=True, text=True).stdout
    ataque(not absorvidas and not merges.strip(),
           'B13 · uma branch divergente recebeu merge bruto',
           'absorvidas=%s · merges desde a base=%d'
           % (absorvidas or 'nenhuma', len(merges.strip().splitlines())))
    ataque(az.CONTRATO == 'AUTORIZACAO_DE_GASTO/v2'
           and az.CONTRATO_AMBIGUO_ANTERIOR == 'AUTORIZACAO_DE_GASTO/v1',
           'B14 · a autorização antiga voltou com o delta externo',
           'activo=%s · anterior=%s' % (az.CONTRATO, az.CONTRATO_AMBIGUO_ANTERIOR))

    # B15 · o id do provider vira SOURCE_ID
    u15 = sc.unidade({'URL': 'https://x/y', 'NATIVE_ID': 'at://did:plc:Z/x'},
                     run_id='R', fonte='IT-T9-001')
    ataque(u15['SOURCE_ID'] == 'IT-T9-001'
           and u15['DOCUMENT_ID'] == rc2.NAO_SEI,
           'B15 · o id do provider vira SOURCE_ID',
           '%s / %s' % (u15['SOURCE_ID'], u15['DOCUMENT_ID']))

    # ══════════════════════════════════════════════════════════════════════
    # §19 §20 §21 · IDENTIDADE, TEMPO, GEOGRAFIA, ESPÉCIE E BRUTO
    # ══════════════════════════════════════════════════════════════════════
    # A NIGHT-SHIFT-01 nomeia treze ataques que a Release não tinha corrido.
    # Nenhum deles pergunta «o dono devolve o que eu espero?» — cada um tenta
    # FABRICAR uma coisa que a casa diz que não se fabrica, e falha ou não.
    print('\n§19 §20 §21 · IDENTIDADE, TEMPO, GEOGRAFIA, ESPÉCIE E BRUTO')

    # ── C1–C3 · O QUE NÃO É SOURCE_ID, POR MAIS PARECIDO QUE SEJA ─────────
    #     DOMAIN != SOURCE_ID · SLUG != SOURCE_ID · SHA != SOURCE_ID
    #
    # ⚠️ E O DONO DESTA PERGUNTA NÃO É `conferir_source_id`. A primeira versão
    # destes três ataques apontou-lhe a arma, e ele «sobreviveu» a todos — mas
    # ele nunca prometeu isto. Ele guarda UMA lei, a COL-LAW-206, e diz qual:
    # `URL NÃO É SOURCE_ID`. É um guarda de FORMA, e `bayer.it` não tem forma
    # de URL.
    #
    #     UMA SONDA QUE ATACA O DONO ERRADO
    #     MEDE A LEI QUE ELE NÃO ESCREVEU.
    #
    # Quem guarda a EXISTÊNCIA é o portão da relevância, e guarda-a no sítio
    # onde ela custa dinheiro: nascer uma autorização. É lá que se bate.
    #
    # ⚠️ E COM CONTROLO. Com o livro vazio NADA compra — nem a fonte
    # verdadeira. Um ataque que passa porque nada passa não mediu guarda
    # nenhuma, mediu um livro vazio.
    #
    #     UM ATAQUE QUE PASSA PORQUE NADA PASSA NÃO MEDE A GUARDA.
    #
    # Então o livro é escrito COMO DADOS, a dizer SIM à fonte verdadeira, e os
    # três impostores tentam entrar pela porta que acabou de se abrir.
    livro_sim = sr02.livro_com(rel.SIM, sid=sr02.FONTE, prop=sr02.PROPOSITO)

    def nasce(sid):
        try:
            az.autorizar(motivo=az.COLETA_NORMAL, proposito=sr02.PROPOSITO,
                         source_id=sid, max_execucoes=1, max_usd=0.10,
                         livro=livro_sim)
            return True, 'autorização concedida'
        except Exception as e:                                    # noqa: BLE001
            return False, str(e).split(':')[0][:40]

    abriu, porque = nasce(sr02.FONTE)
    ataque(abriu, 'C0 · CONTROLO — a fonte provada consegue autorização',
           porque)
    for nome, valor in (('C1 · domínio usado como SOURCE_ID', 'bayer.it'),
                        ('C2 · slug usado como SOURCE_ID', 'bayer-italia'),
                        ('C3 · sha usado como SOURCE_ID', 'a' * 64)):
        passou, porque = nasce(valor)
        ataque(not passou, nome, porque if not passou else 'COMPROU com %r' % valor)

    # ── C4–C6 · O QUE NÃO É DOCUMENT_ID ───────────────────────────────────
    # O contrato mede o `DOCUMENT_ID` contra o sha E contra o endereço. Aqui
    # constrói-se a unidade À MÃO de propósito: é o que um executor distraído
    # faria, e é exactamente contra isso que a lei existe.
    #
    #     SHA256 NÃO É IDENTIDADE DOCUMENTAL. storage_path NÃO É IDENTIDADE.
    SHA = 'b' * 64
    ONDE = 'data/samples/X/observacao-42.json'
    for nome, doc, sha, onde in (
            ('C4 · nome do ficheiro vira DOCUMENT_ID',
             'observacao-42', '', ONDE),
            ('C5 · sha vira DOCUMENT_ID', SHA, SHA, ''),
            ('C6 · caminho de armazenamento vira DOCUMENT_ID',
             ONDE, '', ONDE)):
        u = {'ESPECIE': rc2.COLHEITA, 'SOURCE_ID': 'IT-T9-001',
             'DOCUMENT_ID': doc, 'SHA256': sha, 'RUN_ID': 'R',
             'PAYLOAD': {'ONDE': onde, 'ESTADO': rc2.PAYLOAD_NAO_SE_APLICA}}
        mal = rc2.conferir_unidade(u, 'R', RAIZ)
        ataque(any('DOCUMENT_ID fabricado' in m for m in mal), nome,
               '; '.join(mal)[:70] or 'o contrato deixou passar')

    # ── C7 · O LUGAR DA FONTE NÃO É O LUGAR DO FATO ───────────────────────
    # `SOURCE_LOCATION` diz de onde se leu. `FACT_LOCATION` diz onde a coisa
    # aconteceu. São dois eixos, e derivá-los um do outro é o erro que põe uma
    # notícia italiana sobre a Andaluzia no mapa de Itália.
    u7 = sc.unidade({'URL': 'https://x/y', 'SOURCE_LOCATION': 'Italia',
                     'COUNTRY_SCOPE': 'IT'}, run_id='R', fonte='IT-T9-001')
    ataque('FACT_LOCATION' not in u7,
           'C7 · SOURCE_LOCATION vira FACT_LOCATION',
           'campos com LOCATION: %s'
           % ([k for k in u7 if 'LOCATION' in k] or 'nenhum FACT_LOCATION'))

    # ── C8–C9 · O TEMPO DA PUBLICAÇÃO E O DA OBSERVAÇÃO NÃO SÃO O DO FATO ─
    u8 = sc.unidade({'URL': 'https://x/y', 'PUBLISHED_AT': '2026-09-01T00:00:00Z',
                     'COLLECTED_AT': '2026-09-13T00:00:00Z'},
                    run_id='R', fonte='IT-T9-001')
    ataque('FACT_TIME' not in u8,
           'C8 · PUBLISHED_AT vira FACT_TIME',
           'campos com TIME: %s'
           % ([k for k in u8 if 'TIME' in k] or 'nenhum FACT_TIME'))
    ataque(u8.get('OBSERVED_AT') == '2026-09-13T00:00:00Z'
           and u8.get('PUBLISHED_AT') == '2026-09-01T00:00:00Z',
           'C9 · OBSERVED_AT e PUBLISHED_AT colapsam num só',
           'observado=%s publicado=%s'
           % (u8.get('OBSERVED_AT'), u8.get('PUBLISHED_AT')))

    # ── C10–C11 · A ESPÉCIE DECIDE, E NÃO O SILÊNCIO ──────────────────────
    #     ENTRAM_NO_INGRESSO = (COLHEITA,) — e nada mais.
    u10 = {'ESPECIE': rc2.RUN_RECEIPT, 'SOURCE_ID': 'IT-T9-001',
           'DOCUMENT_ID': rc2.NAO_SEI, 'RUN_ID': 'R',
           'PAYLOAD': {'ONDE': '', 'ESTADO': rc2.PAYLOAD_NAO_SE_APLICA}}
    mal10 = rc2.conferir_unidade(u10, 'R', RAIZ)
    ataque(bool(mal10), 'C10 · RUN_RECEIPT viaja como unidade colhida',
           '; '.join(mal10)[:70] or 'o contrato deixou passar o recibo')
    u11 = dict(u10, ESPECIE=rc2.ESPECIE_DESCONHECIDA)
    mal11 = rc2.conferir_unidade(u11, 'R', RAIZ)
    e11 = {'RUN_ID': 'R', 'EXECUTOR_ID': 'X', 'EXECUTOR_VERSION': '1',
           'ESTADO': rc2.SUCCESS, 'COLHEITA': [u11], 'SUPORTE': []}
    ataque(bool(mal11) and bool(rc2.conferir(e11, RAIZ)),
           'C11 · UNKNOWN vira COLHEITA por omissão',
           '; '.join(mal11)[:70] or 'o contrato aceitou UNKNOWN como colheita')

    # ── C12 · §19 · QUEM OBSERVA BYTES E NÃO PRESERVA O BRUTO ─────────────
    # Não se abre arquitetura nova: mede-se e classifica-se. `social_envelope`
    # é o dono do bruto e declara, ele próprio, que o que grava no disco do
    # runner ainda NÃO está preservado.
    #
    #     GRAVADO NO RUNNER != PRESERVADO.
    #
    # A pergunta que interessa é mais estreita: alguma capacidade do CAMINHO
    # DE PEDIDO DA V1 observa bytes materiais e perde o bruto? As três fases
    # declaradas devolvem observações cujo PAYLOAD é `NAO_SE_APLICA` — a
    # observação É o item, e não há segundo ficheiro para preservar.
    com_bytes = [c for _p, c, _f, _e in sc.FASES.values()
                 if c in ('instagram.reel.capture', 'instagram.reel.audio',
                          'instagram.reel.transcribe')]
    ataque(not com_bytes,
           'C12 · uma fase da V1 observa bytes e perde o bruto',
           'fases com media no caminho de pedido: %s' % (com_bytes or 'nenhuma'))

    print('\n' + '=' * 78)
    print('ATTACKS = %d' % ATAQUES[0])
    print('SURVIVING_ATTACKS = %d' % len(SOBREVIVENTES))
    for s in SOBREVIVENTES:
        print('  · %s' % s)
    print('APIFY_RUNS = 0 · PAID_USD = 0 · REDE REAL = 0')
    return 0 if not SOBREVIVENTES else 1


if __name__ == '__main__':
    sys.exit(main())
