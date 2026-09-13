#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-RC-01 — A SUPERFÍCIE OPERACIONAL DA RELEASE V1, MEDIDA NO RUNTIME.

    py provas/superficie_do_scrap_v1.py

Uma lista escrita à mão diria o que se quer. Esta pergunta ao runtime o que ele
consegue — capacidade a capacidade, com o estado declarado, a política, a rota
ligada e o alvo de execução.

    SUPPORTED != TODO O MUNDO.
    READY != TODAS AS CAPACIDADES EXISTEM.
    FAIL_CLOSED É UM ESTADO VÁLIDO.

E a regra mais importante desta prova é o que ela NÃO faz: nunca transforma
`UNKNOWN` em `BLOCKED`. Não saber é uma confissão; bloquear é um julgamento.

    NOT_MEASURED != NOT_ALLOWED.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('coleta', 'leis', 'admissao', 'regras', 'ferramentas', 'medidas',
           'guarda', 'pedido', 'orquestrador', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import autorizacao_de_gasto as ag                                 # noqa: E402
import scrap_capacidades as cap                                   # noqa: E402
import scrap_executor as sx                                       # noqa: E402
import scrap_registo as reg                                       # noqa: E402
import social_matriz as mz                                        # noqa: E402

READY = 'READY'
READY_PENDING_CREDENTIAL = 'READY_PENDING_CREDENTIAL'
FAIL_CLOSED = 'FAIL_CLOSED'
NOT_IN_V1 = 'NOT_IN_V1'
DESCONHECIDO = 'UNKNOWN'

#: As plataformas da Release V1 NÃO são uma lista escrita à mão.
#:
#: ⚠️ ELAS ERAM, E A LISTA ESTAVA ERRADA. A primeira versão desta prova
#: nomeava quatro plataformas e deixava o TELEGRAM de fora — que tem capacidade
#: `PROVEN`, rota ligada, política `ALLOWED` e custo zero. Uma lista à mão diz
#: o que alguém lembrou; o runtime diz o que a casa consegue.
#:
#:     UMA SUPERFÍCIE ESCRITA À MÃO É A MEMÓRIA DE QUEM A ESCREVEU.
#:
#: É V1 a plataforma que tem PELO MENOS UMA capacidade com rota ligada e
#: política que não a proíbe. As outras ficam `NOT_IN_V1` — conhecidas, e fora
#: por não terem caminho, e não por castigo.
#:
#:     ESTAR FORA DA V1 NÃO É ESTAR BLOQUEADO.
def plataformas_v1(linhas):
    """→ as plataformas com pelo menos um caminho real."""
    return sorted({l['PLATFORM'] for l in linhas
                   if l['EDGE_EXISTS']
                   and l['POLICY_STATE'] not in ('NAO', 'NOT_ALLOWED', 'BLOCKED')})


def _politica(plataforma, capacidade):
    """→ (estado, porque) da política da rota. Nunca inventa."""
    alvo = cap.da_matriz(capacidade)
    if not alvo:
        return DESCONHECIDO, 'a capacidade não traduz para nenhuma da matriz'
    try:
        d = mz.decisao(plataforma, alvo)
    except Exception as e:                                        # noqa: BLE001
        return DESCONHECIDO, '%s: %s' % (type(e).__name__, e)
    return d.get('DECISAO') or DESCONHECIDO, (d.get('PORQUE') or '')[:70]


def medir():
    """→ uma linha por capacidade declarada, com o que se mediu."""
    reg.carregar_adaptadores()
    fora = []
    for capacidade in sorted(cap.DECLARADAS):
        estado = cap.estado(capacidade)
        alvo, _porque = cap.onde(capacidade)
        plat = None
        for p in sorted({k[0] for k in reg._MAPA}):
            if reg.adaptador_de(p, capacidade):
                plat = p
                break
        aresta = bool(plat and reg.tem_caminho(plat, capacidade))
        politica, porque_pol = _politica(plat or '?', capacidade)
        pronto = pode = None
        if plat:
            v = sx.CHECK(plat, capacidade)
            pronto, pode = v.get('STATE'), v.get('CAN')
        linha = {
            'PLATFORM': plat or DESCONHECIDO,
            'CAPABILITY': capacidade,
            'DECLARED_STATE': estado,
            'POLICY_STATE': politica,
            # MODULE EXISTS != EDGE EXISTS: o primeiro e haver adaptador
            # registado para o par; o segundo e haver ROTA ligada nele.
            'MODULE_EXISTS': bool(plat and reg.adaptador_de(plat, capacidade)),
            'EDGE_EXISTS': aresta,
            'FLOW_OBSERVED': _fluxo(capacidade),
            'EXECUTION_TARGET': alvo,
            'PROVIDER': _provider(plat, capacidade),
            'CREDENTIAL_STATE': ('MISSING' if pronto == 'CREDENTIAL_MISSING'
                                 else 'NOT_REQUIRED_OR_PRESENT'),
            'COST_STATE': _custo(plat, capacidade),
            'CHECK_STATE': pronto, 'CAN': pode,
            'PAID': _e_paga(plat, capacidade),
        }
        fora.append(linha)
    # A superfície decide-se DEPOIS de medir tudo: ela é uma propriedade do
    # conjunto, e não de cada linha isolada.
    v1 = plataformas_v1(fora)
    for l in fora:
        l['V1'] = _classificar(l, v1)
        l['V1_STATE'] = l['V1']
        l['FIRST_BREAK'] = _primeira_quebra(l)
    return fora


#: As capacidades cujo FLUXO esta OBSERVADO — e o que as põe aqui é uma prova
#: desta casa que as CORREU ponta a ponta, nomeada ao lado.
#:
#:     EDGE EXISTS != FLOW OBSERVED. Uma aresta lida na árvore não anda.
#:
#: `WIRED` é o degrau do meio: existe fase no caminho canônico que a pede, e
#: ninguém aqui afirma que ela já correu.
FLUXO_OBSERVADO = {
    'bluesky.author.incremental': 'provas/o_canario_do_scrap_v1.py',
    'linkedin.identity.discovery': 'provas/linkedin_local_first.py',
}


def _fluxo(capacidade):
    if capacidade in FLUXO_OBSERVADO:
        return 'OBSERVED'
    try:
        import scrap_colheita as _sc
        if any(l[1] == capacidade for l in _sc.FASES.values()):
            return 'WIRED'
    except Exception:                                             # noqa: BLE001
        pass
    return 'NO'


def _rota_da_matriz(plat, capacidade):
    if not plat:
        return None
    rotas = (mz.MATRIZ.get(plat) or {}).get(cap.da_matriz(capacidade))
    return mz._rota_padrao(rotas) if rotas else None


def _provider(plat, capacidade):
    escolhida = _rota_da_matriz(plat, capacidade)
    return (escolhida or {}).get('CLASSE') or DESCONHECIDO


def _custo(plat, capacidade):
    classe = _provider(plat, capacidade)
    if classe in ('APIFY', 'OFFICIAL_API_PAID'):
        return 'PAID'
    if classe == DESCONHECIDO:
        return DESCONHECIDO
    return 'FREE'


def _primeira_quebra(l):
    """O PRIMEIRO portão que diz não. → o nome dele, ou `NONE`.

    Saber que uma capacidade não corre vale pouco; saber ONDE ela para é o que
    diz de quem é a próxima decisão — da política, da engenharia, de quem tem a
    credencial, ou de ninguém.
    """
    if l['POLICY_STATE'] in ('NAO', 'NOT_ALLOWED', 'BLOCKED'):
        return 'ROUTE_POLICY'
    if not l['MODULE_EXISTS']:
        return 'NO_ADAPTER'
    if not l['EDGE_EXISTS']:
        return 'NO_ROUTE'
    if l['CREDENTIAL_STATE'] == 'MISSING':
        return 'CREDENTIAL'
    if l['CAN'] is not True:
        return l['CHECK_STATE'] or DESCONHECIDO
    if l['FLOW_OBSERVED'] == 'NO':
        return 'NO_REQUEST_PATH'
    return 'NONE'


def _e_paga(plat, capacidade):
    """→ True quando a rota ligada atravessa o dono do dinheiro."""
    r = reg.adaptador_de(plat, capacidade) if plat else None
    rota = (r or {}).get('ROTA')
    if rota is None:
        return None
    import inspect
    try:
        src = inspect.getsource(rota)
    except (OSError, TypeError):                                  # pragma: no cover
        return None
    return 'coletor' in src or 'ct.executar' in src


def _classificar(l, v1):
    """A classificação operacional. Cada `if` diz porquê, e nenhum adivinha.

    ⚠️ E A DECISÃO DE «CONSIGO AGORA?» NÃO É DESTA FUNÇÃO. Ela é do `CHECK`,
    que já a responde em `CAN`. A primeira versão desta prova comparava o
    `STATE` com uma lista de palavras que ELA achava que significavam sim — e
    `CAN_COLLECT_NOW` não estava na lista. Cinco capacidades a funcionar
    apareciam como fechadas.

        UMA SONDA QUE ADIVINHA O VOCABULÁRIO DE OUTRO DONO
        MEDE O QUE ELA IMAGINOU QUE ELE DIRIA.
    """
    if l['PLATFORM'] not in v1:
        return NOT_IN_V1
    if l['POLICY_STATE'] in ('NAO', 'NOT_ALLOWED', 'BLOCKED'):
        return FAIL_CLOSED
    if not l['EDGE_EXISTS']:
        # Declarada e sem rota ligada. Não é bloqueio: é ausência de caminho.
        return FAIL_CLOSED
    if l['CHECK_STATE'] == 'CREDENTIAL_MISSING':
        return READY_PENDING_CREDENTIAL
    if l['CAN'] is True:
        return READY
    if l['CAN'] is None:
        return DESCONHECIDO
    # Mediu-se, o `CHECK` correu, e recusou por um motivo escrito.
    return FAIL_CLOSED


def main():
    linhas = medir()
    print('SCRAP-RC-01 · SUPERFÍCIE OPERACIONAL V1')
    print('=' * 100)
    print('%-10s %-34s %-10s %-6s %-7s %s'
          % ('PLATFORM', 'CAPABILITY', 'DECLARED', 'EDGE', 'PAID', 'V1'))
    print('-' * 100)
    for l in linhas:
        print('%-10s %-34s %-10s %-6s %-7s %s'
              % (l['PLATFORM'][:10], l['CAPABILITY'][:34],
                 str(l['DECLARED_STATE'])[:10], 'sim' if l['EDGE_EXISTS'] else '—',
                 {True: 'paga', False: 'grátis', None: '—'}[l['PAID']],
                 l['V1']))
    print('=' * 100)
    conta = {}
    for l in linhas:
        conta[l['V1']] = conta.get(l['V1'], 0) + 1
    for k in (READY, READY_PENDING_CREDENTIAL, FAIL_CLOSED, NOT_IN_V1, DESCONHECIDO):
        print('%-26s %d' % (k, conta.get(k, 0)))
    print()
    print('    NOT_MEASURED != NOT_ALLOWED — e `UNKNOWN` fica `UNKNOWN`.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
