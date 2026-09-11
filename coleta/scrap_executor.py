#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O SINTONIA SCRAP COMO EXECUTOR — os seis verbos de `COL-LAW-013`.

    import scrap_executor as scrap
    scrap.CAPABILITIES()
    scrap.CHECK('YOUTUBE', 'youtube.search')     # nao gasta nada
    scrap.COLLECT(platform=..., capability=..., run_id=...)

ESTE FICHEIRO NAO E UM ORQUESTRADOR, E A DIFERENCA NAO E DE TAMANHO
--------------------------------------------------------------------
`orquestrador/orquestrador.py` continua a ser o dono unico da orquestracao, e
esta ACIMA disto. `COL-LAW-011`, e nao se reabre sem contraexemplo.

    COLLECTION_REQUEST
            ↓
    ORQUESTRADOR CANONICO        ← decide missao, dominio, universo, prioridade
            ↓
    SINTONIA SCRAP EXECUTOR      ← este ficheiro: executa a capacidade pedida
            ↓
    SCRAP ADAPTER ROUTER
            ↓
    ADAPTERS → PROVIDERS

O que este executor NAO decide, e nao ha excecao:

    qual missao global executar · que dominios coletar · que universo atender
    admissao · julgamento · prioridade global · a regra epistemologica da Collection

    COLETAR != ADMITIR != JULGAR. Ele faz o primeiro, e so o primeiro.

E NAO CRIA `COLLECTION_REQUEST`
--------------------------------
Um executor que fabrica o proprio pedido deixou de ser executor. Ha um teste
que le este ficheiro a procura disso, porque um comentario nao o impediria.

O VERBO QUE MAIS IMPORTA E O `CHECK`
-------------------------------------
`CHECK` responde «consigo chegar la agora?» SEM GASTAR. E ele que permite ao
orquestrador escolher a rota mais barata capaz — `COL-LAW-018` — em vez de
descobrir o custo depois de o ter pago.

    UM `CHECK` QUE GASTA NAO E UM CHECK. E UMA COLETA COM OUTRO NOME.

O AMBIENTE E DEVOLVIDO, NAO ESCOLHIDO
--------------------------------------
`CHECK` diz onde a capacidade corre — `ONLINE`, `LOCAL`, `EITHER`, `HYBRID` ou
`UNKNOWN` — e, quando e LOCAL ou HYBRID, por que. Quem decide executar la e
quem coordena; este ficheiro so informa.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_capacidades as cap    # noqa: E402
import scrap_registo as reg        # noqa: E402
import scrap_fornecedores as forn  # noqa: E402

EXECUTOR_ID = 'SINTONIA_SCRAP'
EXECUTOR_VERSION = '1.0.0'

#: `COL-LAW-016`: o orquestrador conhece tres escopos. A semantica do cursor de
#: cada fonte e assunto INTERNO deste executor, e nao sobe.
ESCOPOS = ('PONTUAL', 'INCREMENTAL', 'TOTAL')

#: Onde este executor larga o que traz. `COL-LAW-013` chama-lhe OUTPUT.
LARGA_EM = (
    'data/samples/COMPETITOR-PUBLIC-COMM',
    'data/raw/REEL-MIDIA',
    'data/samples/REEL-TRANSCRICOES',
)

# ── OS ESTADOS DO `CHECK` ─────────────────────────────────────────────────
PODE = 'CAN_COLLECT_NOW'
SEM_ROTA = 'DECLARED_WITHOUT_ROUTE'
NAO_DECLARADA = 'CAPABILITY_NOT_DECLARED'
SEM_PROMESSA = 'CAPABILITY_STATE_PROMISES_NOTHING'
AMBIENTE_ERRADO = 'WRONG_EXECUTION_ENVIRONMENT'


def CAPABILITIES(plataforma=None):
    """O que o SCRAP sabe fazer, com estado medido e ambiente declarado.

    `COL-LAW-014` pede capacidade declarada. Isto e a declaracao, e ela e
    honesta ate onde doi: quinze capacidades `PROVEN` e onze que nao prometem
    nada nenhuma.
    """
    reg.carregar_adaptadores()
    fonte = cap.da_plataforma(plataforma) if plataforma else cap.DECLARADAS
    saida = {}
    for nome, (plat, estado, alvo, porque, prova, grosso) in sorted(fonte.items()):
        r = reg.adaptador_de(plat, nome)
        saida[nome] = {
            'PLATFORM': plat,
            'CAPABILITY': nome,
            'CAPABILITY_STATE': estado,
            'EXECUTION_TARGET': alvo,
            'WHY_LOCAL': porque,
            'EVIDENCE': prova,
            'MATRIZ_CAPABILITY': grosso,
            'ADAPTER': r['ADAPTADOR'] if r else None,
            'HAS_ROUTE': bool(r and r['EXECUTA']),
            'PROMISES_RESULT': cap.promete_resultado(nome),
        }
    return saida


def CHECK(plataforma, capacidade, *, ambiente=None):
    """Consigo chegar la agora, SEM GASTAR? → o veredicto, sempre.

    Nao faz nenhuma requisicao, nao abre nenhum modelo, nao chama nenhuma rota
    paga. Le o que esta declarado e o que esta registado, e responde.
    """
    reg.carregar_adaptadores()
    plat = (plataforma or '').upper()
    alvo, porque = cap.onde(capacidade)
    veredicto = {
        'EXECUTOR_ID': EXECUTOR_ID,
        'EXECUTOR_VERSION': EXECUTOR_VERSION,
        'PLATFORM': plat,
        'CAPABILITY': capacidade,
        'CAPABILITY_STATE': cap.estado(capacidade),
        'EXECUTION_TARGET': alvo,
        'WHY_LOCAL': porque,
        'EVIDENCE': cap.prova(capacidade),
        'COST_TO_CHECK_USD': 0.0,
        'CAN': False,
        'STATE': None,
        'WHY': None,
    }
    if not cap.existe(capacidade):
        veredicto['STATE'] = NAO_DECLARADA
        veredicto['WHY'] = ('capacidade nao declarada. Isto nao e uma falha: e '
                            'a resposta certa para o que ninguem mediu.')
        return veredicto
    if not cap.promete_resultado(capacidade):
        veredicto['STATE'] = SEM_PROMESSA
        veredicto['WHY'] = ('estado medido %s. Existir adaptador para ela nao a '
                            'transforma em sucesso.' % cap.estado(capacidade))
        return veredicto
    r = reg.adaptador_de(plat, capacidade)
    if not r or not r['EXECUTA']:
        veredicto['STATE'] = SEM_ROTA
        veredicto['WHY'] = ('declarada e sem rota ligada nesta linhagem. '
                            'Declarar sem executar e honesto; executar sem '
                            'declarar e que nao e.')
        veredicto['ADAPTER'] = r['ADAPTADOR'] if r else None
        return veredicto
    veredicto['ADAPTER'] = r['ADAPTADOR']
    if ambiente and alvo not in (ambiente, cap.EITHER):
        veredicto['STATE'] = AMBIENTE_ERRADO
        veredicto['WHY'] = ('esta capacidade corre em %s e foi pedida em %s%s'
                            % (alvo, ambiente, ' — %s' % porque if porque else ''))
        return veredicto
    veredicto['CAN'] = True
    veredicto['STATE'] = PODE
    veredicto['WHY'] = 'declarada, com rota, e o estado medido promete resultado'
    return veredicto


def COLLECT(*, platform, capability, run_id, scope='PONTUAL', **kwargs):
    """Vai buscar. → (objetos, trace). NUNCA levanta por rota recusada.

    Recusa e bloqueio sao RESULTADO DE MEDICAO, nao ausencia de resultado — e
    por isso descem como estado, com trace, e nao como excecao.
    """
    if scope not in ESCOPOS:
        raise ValueError('escopo fora de COL-LAW-016: %r. Os tres sao %s'
                         % (scope, ', '.join(ESCOPOS)))
    pronto = CHECK(platform, capability)
    if not pronto['CAN']:
        percurso = forn.Percurso(capability)
        trace = percurso.selar(resultado=pronto['STATE'])
        trace.update({'EXECUTOR_ID': EXECUTOR_ID, 'RUN_ID': run_id,
                      'SCOPE': scope, 'CHECK': pronto})
        return [], trace
    executa = reg.executor_de((platform or '').upper(), capability)
    objetos, trace = executa(run_id=run_id, **kwargs)
    trace.update({'EXECUTOR_ID': EXECUTOR_ID, 'EXECUTOR_VERSION': EXECUTOR_VERSION,
                  'RUN_ID': run_id, 'SCOPE': scope, 'CHECK': pronto})
    forn.conferir(trace)
    return objetos, trace


def STATE(plataforma=None):
    """Onde parei. O cursor e SEMPRE interno — `COL-LAW-016`.

    O orquestrador conhece `PONTUAL`, `INCREMENTAL` e `TOTAL`, e mais nada. Que
    o cursor do LinkedIn seja um `urn:li:activity:` e o do YouTube um
    `page token` e assunto desta casa.
    """
    return {
        'EXECUTOR_ID': EXECUTOR_ID,
        'SCOPES_KNOWN_BY_ORCHESTRATOR': ESCOPOS,
        'CURSOR_SEMANTICS_ARE_INTERNAL': True,
        'CHECKPOINT_BACKEND': 'coleta/coleta_checkpoint.py',
        'CURSORS': 'NOT_IMPLEMENTED',
        'WHY': ('C1 desenha o contrato e nao liga o checkpoint por capacidade. '
                'Ligar sem ter rota para a maioria delas seria guardar a '
                'posicao de uma corrida que nunca aconteceu.'),
    }


def OUTPUT():
    """Onde larguei, e em que forma."""
    return {
        'EXECUTOR_ID': EXECUTOR_ID,
        'LARGA_EM': LARGA_EM,
        'ARTIFACT_CONTRACT': 'leis/artefato.py',
        'RAW_IS_NOT_DERIVED': ('RAW != DERIVED != STRUCTURED != ADMISSION != READY. '
                               'O SCRAP entrega RAW e derivados com pai declarado; '
                               'nao admite e nao julga.'),
        'TEXT_KINDS': ('CAPTION', 'TRANSCRIPT'),
        'TRANSLATION': 'NOT_RUN',
        'TRANSLATION_WHY': ('a casa tem a lei da traducao escrita e conferida e '
                            'nao tem motor nenhum. Ausente fica NOT_RUN — nunca '
                            'uma copia do original a fingir de traducao.'),
    }


def TRACE(trace):
    """O que aconteceu, com fornecedor, troca, motivo e custo.

    Nao inventa campo: confere o que ja veio e recusa a historia incompleta.
    """
    forn.conferir(trace)
    return {
        'EXECUTOR_ID': EXECUTOR_ID,
        'EXECUTOR_VERSION': EXECUTOR_VERSION,
        'RUN_ID': trace.get('RUN_ID'),
        'CAPABILITY': trace.get('CAPABILITY'),
        'PROVIDER_REQUESTED': trace.get('PROVIDER_REQUESTED'),
        'PROVIDER_USED': trace.get('PROVIDER_USED'),
        'WHY_FALLBACK': trace.get('WHY_FALLBACK'),
        'RESULT': trace.get('RESULT'),
        'PROVIDER_STEPS': trace.get('PROVIDER_STEPS'),
        'PAID_PROVIDER_USED': trace.get('PAID_PROVIDER_USED', False),
        'EXECUTION_TARGET': (trace.get('CHECK') or {}).get('EXECUTION_TARGET'),
        'WHY_LOCAL': (trace.get('CHECK') or {}).get('WHY_LOCAL'),
    }
