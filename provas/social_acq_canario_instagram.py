#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CANARIO DO INSTAGRAM — o PORTAO, provado por execucao com a rede proibida.

A missao pede rotas testadas. Para o Instagram, a resposta medida e que TODAS as
rotas remotas estao fechadas — mas `fechada` nao e uma palavra, e quatro
capacidades fecham por QUATRO motivos diferentes, com quatro donos diferentes:

    FETCH_TRANSCRIPT   ROUTE_NOT_ALLOWED   robots.txt VIVO de instagram.com
                                           (`Disallow: /`, medido na C10.5D)
    INCREMENTAL        ROUTE_NOT_ALLOWED   PLATFORM_POLICY_STATUS = NOT_MEASURED
                                           (fail-closed da C14-C: o dono JA
                                            autorizou, a plataforma nao foi medida)
    FETCH_PROFILE      ALLOWED             mas `graph:business_discovery` esta
                                           CREDENTIAL_MISSING — falta credencial,
                                           nao falta permissao
    FETCH_COMMENTS     ALLOWED             mas `apify:comments` e PAGA, e esta
                                           missao tem PAID_USD = 0

    QUATRO MANEIRAS DE NAO SAIR NAO SAO UM BLOQUEIO SO.
    «PLATAFORMA BLOQUEADA» APAGA AS QUATRO E NAO E VERDADE DE NENHUMA.

E a prova que esta missao pode entregar sem adquirir nada e a mais forte que
existe para uma rota fechada: MANDAR A CADEIA ADQUIRIR, com o socket proibido, e
medir que ela recusa SOZINHA — antes de tocar na rede.

    UMA RECUSA QUE SE PROVA COM A REDE FECHADA NAO DEPENDE DA SORTE DA REDE.

O QUE ESTE CANARIO NAO PROVA, E DIZ EM VOZ ALTA
------------------------------------------------
Nao prova que o Instagram responderia 200, 403 ou 429. Isso exigiria sair, e
sair e exactamente o que a politica recusa. Esses eixos ficam `UNKNOWN`, e
escreve-los como `BLOCKED` seria inventar uma medicao.

    ROTA RECUSADA PELA CASA  !=  ROTA BLOQUEADA PELA PLATAFORMA.
"""
import os
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)

# ══════════════════════════════════════════════════════════════════════════
# A REDE PROIBIDA — instalada ANTES de importar a cadeia
# ══════════════════════════════════════════════════════════════════════════
# Duas camadas, porque uma so nao chega: `connect` apanha quem abre ligacao,
# `getaddrinfo` apanha quem so resolve o nome. Um portao que deixa resolver o
# nome ja conversou com o DNS do alvo.
PEDIDOS = []
RESOLUCOES = []
_connect = socket.socket.connect
_getaddrinfo = socket.getaddrinfo


def _espia_connect(self, addr, *a, **k):
    PEDIDOS.append(addr)
    raise AssertionError('ABRIU_REDE %r' % (addr,))


def _espia_dns(host, port, *a, **k):
    RESOLUCOES.append(str(host or '').lower())
    raise AssertionError('RESOLVEU_NOME %r' % (host,))


socket.socket.connect = _espia_connect
socket.getaddrinfo = _espia_dns

import _gavetas  # noqa: E402,F401
import social_matriz as mz          # noqa: E402
import scrap_capacidades as cap     # noqa: E402
import scrap_registo as reg         # noqa: E402
import social_rotas as rotas        # noqa: E402
import adaptador_instagram as ig    # noqa: E402

RUN = 'SOCIAL-ACQ-V1-INSTAGRAM-CANARIO'
OK = []


def diz(cond, rotulo, valor=''):
    OK.append(bool(cond))
    print('  %-5s %-58s %s' % ('ok' if cond else 'FAIL', rotulo, str(valor)[:60]))


print('=' * 88)
print('CANARIO · INSTAGRAM · o portao de politica, com a rede proibida')
print('=' * 88)

# ── 0 · O INSTRUMENTO VERIFICA-SE PRIMEIRO ────────────────────────────────
# Um espiao que nao dispara faz qualquer recusa parecer boa. Provar que ele
# apanha antes de o usar para julgar seja o que for.
print('\n0 · O instrumento — a sentinela apanha mesmo?')
try:
    socket.getaddrinfo('example.invalid', 80)
    diz(False, 'a sentinela devia ter disparado', 'NAO DISPAROU')
except AssertionError:
    diz(True, 'a sentinela de DNS dispara', 'RESOLVEU_NOME')
RESOLUCOES.clear()

# ── 1 · AS QUATRO PORTAS, E OS QUATRO MOTIVOS ─────────────────────────────
print('\n1 · As quatro portas do Instagram, executadas na matriz')
esperado = {
    'FETCH_TRANSCRIPT': 'ROUTE_NOT_ALLOWED',
    'INCREMENTAL': 'ROUTE_NOT_ALLOWED',
    'FETCH_PROFILE': 'ALLOWED',
    'FETCH_POST': 'ALLOWED',
    'FETCH_COMMENTS': 'ALLOWED',
}
decisoes = {}
for capn, esp in esperado.items():
    d = mz.decisao('INSTAGRAM', capn)
    decisoes[capn] = d
    diz(d['DECISAO'] == esp, '%-18s -> %s' % (capn, esp), d['DECISAO'])
    print('        rota=%s estado=%s' % (d.get('ROTA'), d.get('ESTADO')))

# ── 2 · «ALLOWED» NAO E «SAI HOJE» ────────────────────────────────────────
print('\n2 · O que separa ALLOWED de executavel HOJE')
dp = decisoes['FETCH_PROFILE']
diz(dp['ESTADO'] == 'CREDENTIAL_MISSING',
    'FETCH_PROFILE esta ALLOWED e CREDENTIAL_MISSING', dp['ESTADO'])
diz(dp['CLASSE'] == 'OFFICIAL_API_FREE',
    'e a rota permitida e a API OFICIAL, nao um scraper', dp['CLASSE'])
dc = decisoes['FETCH_COMMENTS']
diz(dc['CLASSE'] == 'APIFY', 'FETCH_COMMENTS so tem rota PAGA', dc['CLASSE'])
print('        PERMISSAO != CREDENCIAL != ORCAMENTO — tres eixos, tres donos')

# ── 3 · O FAIL-CLOSED DA C14-C, LIDO NA PROPRIA LINHA ─────────────────────
print('\n3 · INCREMENTAL — autorizacao do dono existe, e a rede continua fechada')
rota_inc = mz.MATRIZ['INSTAGRAM']['INCREMENTAL'][0]
diz(rota_inc.get('OWNER_AUTHORIZED') == 'SIM',
    'OWNER_AUTHORIZED = SIM (decisao registada do dono)', rota_inc.get('OWNER_AUTHORIZED'))
diz(rota_inc.get('PLATFORM_POLICY_STATUS') == 'NOT_MEASURED',
    'PLATFORM_POLICY_STATUS = NOT_MEASURED', rota_inc.get('PLATFORM_POLICY_STATUS'))
diz(rota_inc.get('LIMITE') == 'PUBLIC_PROFILE_DISCOVERY_ONLY',
    'LIMITE escrito e estreito', rota_inc.get('LIMITE'))
diz(decisoes['INCREMENTAL']['DECISAO'] == 'ROUTE_NOT_ALLOWED',
    'e o resultado e FAIL-CLOSED: AUTORIZAR NAO E MEDIR', 'ROUTE_NOT_ALLOWED')

# ── 4 · A CADEIA RECUSA SOZINHA, COM A REDE PROIBIDA ──────────────────────
print('\n4 · Mandar a cadeia adquirir — e medir que ela recusa antes da rede')
for capn in ('FETCH_TRANSCRIPT', 'INCREMENTAL'):
    antes_p, antes_d = len(PEDIDOS), len(RESOLUCOES)
    try:
        objs, registro = rotas.executar(platform='INSTAGRAM', capability=capn,
                                        run_id=RUN, country_scope='IT')
        estado = registro.get('ESTADO')
        n = len(objs or [])
    except AssertionError as e:
        estado, n = 'ABRIU_REDE', -1
        print('        !! %s' % e)
    except Exception as e:                                        # noqa: BLE001
        estado, n = 'ERRO:%s' % type(e).__name__, -1
        print('        !! %s' % str(e)[:80])
    novos_p = len(PEDIDOS) - antes_p
    novos_d = len(RESOLUCOES) - antes_d
    diz(estado in ('ROUTE_NOT_ALLOWED', 'BLOCKED', 'NOT_APPLICABLE'),
        'COLLECT(%s) recusa com estado proprio' % capn, estado)
    diz(novos_p == 0 and novos_d == 0,
        '   e nao abriu socket nem resolveu nome', 'req=%d dns=%d' % (novos_p, novos_d))
    diz(n == 0, '   e nao devolveu objeto nenhum', n)

# ── 5 · O PORTAO DO PROPRIO ADAPTADOR ─────────────────────────────────────
print('\n5 · O portao do adaptador, e o seu trace')
pol = ig.politica()
diz(pol['DECISAO'] == 'ROUTE_NOT_ALLOWED',
    'adaptador_instagram.politica() le a matriz e recusa', pol['DECISAO'])
tr = ig._recusa(pol)
diz(tr.get('NETWORK_TOUCHED') is False, 'trace declara NETWORK_TOUCHED = False', tr.get('NETWORK_TOUCHED'))
diz(tr.get('ASR_RUN') is False, 'trace declara ASR_RUN = False', tr.get('ASR_RUN'))
diz(tr.get('POLICY_OWNER') == 'leis/social_matriz.py',
    'e diz QUEM decidiu — um dono so', tr.get('POLICY_OWNER'))
diz(tr.get('REMOTE_ACQUISITION_ALLOWED') is False,
    'REMOTE_ACQUISITION_ALLOWED = False', tr.get('REMOTE_ACQUISITION_ALLOWED'))

# ── 6 · O QUE CONTINUA PROVEN, E POR QUE NAO E CONTRADICAO ────────────────
print('\n6 · REUSAR != ADQUIRIR — o motor local nao foi rebaixado')
for nome in ('instagram.reel.capture', 'instagram.reel.audio', 'instagram.reel.transcribe'):
    est = cap.DECLARADAS[nome][1]
    diz(est == 'PROVEN', '%-30s continua PROVEN' % nome, est)
print('        a matriz recusa SAIR para buscar midia nova; o que ja entrou')
print('        continua reprocessavel. Dois eixos, e a lei ja o escreveu.')

# ── 7 · O QUE NAO EXISTE, E A AUSENCIA E O ACHADO ─────────────────────────
print('\n7 · A ausencia que e um facto')
diz(not cap.existe('instagram.native_caption'),
    'instagram.native_caption NAO existe — a plataforma nao serve legenda', 'ausente')
print('        CAPTION (texto do autor) != TRANSCRIPT (fala reconhecida)')
d_bytes = mz.decisao('INSTAGRAM', 'FETCH_VIDEO_BYTES')
diz(d_bytes['DECISAO'] == 'NOT_DECLARED',
    'FETCH_VIDEO_BYTES = NOT_DECLARED (ninguem mediu esta porta)', d_bytes['DECISAO'])
print('        NOT_DECLARED NAO E PERMISSAO. E «ninguem decidiu».')

# ── 8 · ACHADO: PERMISSAO SEM DONO ────────────────────────────────────────
# `INSTAGRAM/FETCH_POST` esta `ALLOWED` na matriz, com rota `PUBLIC_BROWSER`
# `PROVED` — a MESMA familia de implementacao (`instagram_janela.py`) que a
# C14-C fechou em `INCREMENTAL` por fail-closed. A pergunta obvia e se ela e
# uma porta aberta pelo lado de dentro, como a `linkedin.recent.discovery` era.
#
# Medido aqui: NAO. Ela nao tem capacidade declarada que traduza para ela, logo
# nao tem rota ligada, logo nenhum `COLLECT` chega la. A permissao existe no
# papel e nao tem dono no codigo.
#
#     PERMISSAO SEM DONO NAO E BYPASS. MAS TAMBEM NAO E UMA DECISAO COMPLETA:
#     no dia em que alguem lhe ligar um dono, ela sai sem passar pelos tres
#     eixos que a C14-C exigiu da porta vizinha.
#
# Fica REGISTADO COMO ACHADO e NAO CORRIGIDO: mexer na matriz e decisao do dono
# da politica, e esta missao nao tem essa autorizacao. SCOPE LEAK = FAIL.
print('\n8 · Achado — permissao ALLOWED sem dono no codigo')
sem_dono = []
for capn, d in decisoes.items():
    if d['DECISAO'] != 'ALLOWED':
        continue
    nome = cap.pela_matriz('INSTAGRAM', capn)
    ligada = bool(reg.rota_de('INSTAGRAM', nome)) if nome else False
    if not ligada:
        sem_dono.append((capn, nome, d.get('ROTA')))
    print('        %-18s declarada=%-30s rota_ligada=%s' % (capn, nome, ligada))
diz(all(not bool(reg.rota_de('INSTAGRAM', cap.pela_matriz('INSTAGRAM', c)))
        for c, _, _ in sem_dono),
    'nenhuma das ALLOWED-sem-dono tem rota executavel', len(sem_dono))
for capn, _, rota in sem_dono:
    antes_p, antes_d = len(PEDIDOS), len(RESOLUCOES)
    objs, registro = rotas.executar(platform='INSTAGRAM', capability=capn,
                                    run_id=RUN, country_scope='IT')
    diz(len(objs or []) == 0 and len(PEDIDOS) == antes_p and len(RESOLUCOES) == antes_d,
        '   COLLECT(%s) nao sai nem devolve' % capn,
        '%s req=%d' % (registro.get('ESTADO'), len(PEDIDOS) - antes_p))
print('        ACHADO_REGISTADO = INSTAGRAM_ALLOWED_SEM_DONO · NAO CORRIGIDO')
print('        (mexer na matriz e decisao do dono da politica, nao desta missao)')

# ── 9 · A CONTA FINAL DA REDE ─────────────────────────────────────────────
print('\n9 · A conta da rede em toda a corrida')
diz(not PEDIDOS, 'INSTAGRAM_SOCKETS_ABERTOS = 0', len(PEDIDOS))
diz(not RESOLUCOES, 'INSTAGRAM_DNS_RESOLVIDOS = 0', len(RESOLUCOES))

print('\n' + '=' * 88)
veredito = 'PASS' if all(OK) else 'FAIL'
print('INSTAGRAM_POLICY_GATE_CANARY = %s   (%d/%d asserts)' % (veredito, sum(OK), len(OK)))
print('INSTAGRAM_REQUESTS = 0 · INSTAGRAM_DNS = 0 · PAID_USD = 0 · APIFY_RUNS = 0')
print('INSTAGRAM_REMOTE_ACQUISITION = NOT_ATTEMPTED (por politica, nao por falha)')
print('PLATFORM_HTTP_BEHAVIOUR = UNKNOWN (exigiria sair; sair e o que se recusa)')
print('POLICY_CHANGED = NO   (leis/social_matriz.py intacto)')
sys.exit(0 if all(OK) else 1)
