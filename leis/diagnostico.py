#!/usr/bin/env python3
"""OS CODIGOS DE DIAGNOSTICO — o que o alerta le, e o que a pessoa depura.

    ERROR MESSAGE NAO E DIAGNOSTIC CODE.

A mensagem pode mudar: alguem melhora o texto, a biblioteca muda a redacao, a
plataforma traduz. O codigo e ESTAVEL, e e por ele que se encaminha. Guardar so
a mensagem faz o alerta quebrar na primeira vez que alguem escreve melhor.

ESTE FICHEIRO NAO SUBSTITUI `leis/falhas.py`
--------------------------------------------
`falhas.py` responde O QUE ACONTECEU com um item ou uma chamada — 23 estados
canonicos, tres camadas (SOURCE / ROUTE / EXECUTOR), e o que cada um pede de
recuperacao. Ele continua sendo o dono disso.

Um DIAGNOSTIC_CODE responde outra pergunta: O QUE ESTA QUEBRADO NO FLUXO, e
quem tem de agir. Um `TRANSIENT_NETWORK_ERROR` (falha) numa etapa de FETCH
produz o diagnostico `FETCH_FAILED`; o mesmo estado numa etapa de DERIVED
produz `DERIVATION_FAILED`. Mesmo fato, encaminhamentos diferentes.

    O ESTADO E DO ITEM. O DIAGNOSTICO E DA ETAPA.

A LISTA E CURTA DE PROPOSITO
-----------------------------
Comeca pelos modos de falha que os testes desta missao conseguem PROVAR.
Inventar cem codigos criaria noventa que ninguem sabe reproduzir — e um codigo
que ninguem reproduziu nao ajuda quem for depurar as tres da manha.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import falhas    # noqa: E402

# ── OS CODIGOS ───────────────────────────────────────────────────────────
# (codigo, quem tem de agir, o que significa)
FLOW_UNACCOUNTED_INPUT = 'FLOW_UNACCOUNTED_INPUT'
RAW_PERSISTENCE_FAILED = 'RAW_PERSISTENCE_FAILED'
DERIVATION_FAILED = 'DERIVATION_FAILED'
FETCH_FAILED = 'FETCH_FAILED'
DISCOVER_FAILED = 'DISCOVER_FAILED'
STRUCTURED_NOT_CONNECTED = 'STRUCTURED_NOT_CONNECTED'
ADMISSION_NOT_CONNECTED = 'ADMISSION_NOT_CONNECTED'
CHECKPOINT_NOT_ADVANCED = 'CHECKPOINT_NOT_ADVANCED'
ROUTE_NO_LONGER_WORKS = 'ROUTE_NO_LONGER_WORKS'
UPSTREAM_ARTIFACT_CHANGED = 'UPSTREAM_ARTIFACT_CHANGED'
GRAIN_NOT_DECLARED = 'GRAIN_NOT_DECLARED'
DECISION_MISSING = 'DECISION_MISSING'
# ── Chegados em O8C, de `telemetria.py`. Nao sao nomes novos inventados aqui:
#    eram declarados la, e la nao era o sitio — dizem ONDE no fluxo parou, que
#    e a pergunta desta lei, e nao POR QUE o mundo parou, que e a de `falhas`.
GRAIN_MISMATCH = 'GRAIN_MISMATCH'
UPSTREAM_NOT_RUN = 'UPSTREAM_NOT_RUN'
OWNER_NOT_CONNECTED = 'OWNER_NOT_CONNECTED'
STORAGE_MISSING = 'STORAGE_MISSING'
STORAGE_CONFLICT = 'STORAGE_CONFLICT'

# Quem age. Um codigo sem dono e um alerta que fica no ecra.
NOS = 'NOSSO_CODIGO'
FONTE = 'A_FONTE'
ROTA = 'A_ROTA'
PESSOA = 'UMA_PESSOA'

CODIGOS = {
    FLOW_UNACCOUNTED_INPUT: (NOS, 'entraram itens que nao terminaram em nenhum balde: '
                                  'nem passaram, nem foram recusados, nem deram erro. '
                                  'Sumiram sem explicacao.'),
    RAW_PERSISTENCE_FAILED: (NOS, 'a fonte respondeu e o bruto nao ficou guardado. '
                                  'Seguir daqui criaria conteudo sem bruto.'),
    DERIVATION_FAILED: (NOS, 'o bruto esta guardado e a derivacao nao produziu. '
                             'O RAW continua bom: da para retomar daqui.'),
    FETCH_FAILED: (ROTA, 'a busca nao trouxe. Pode ser a rota, nao a fonte.'),
    DISCOVER_FAILED: (ROTA, 'nao foi possivel enumerar o que existe na fonte.'),
    STRUCTURED_NOT_CONNECTED: (NOS, 'a etapa estruturada nao recebe o artefato da '
                                    'anterior: a aresta nao existe.'),
    ADMISSION_NOT_CONNECTED: (NOS, 'a porta de admissao existe e nada desta estrada '
                                   'entra nela.'),
    CHECKPOINT_NOT_ADVANCED: (NOS, 'houve persistencia e o checkpoint nao andou: a '
                                   'proxima corrida vai pagar de novo.'),
    ROUTE_NO_LONGER_WORKS: (ROTA, 'a rota funcionava e parou. A fonte pode estar bem.'),
    UPSTREAM_ARTIFACT_CHANGED: (NOS, 'o artefato de cima mudou desde a tentativa '
                                     'anterior: retomar seria costurar duas verdades.'),
    GRAIN_NOT_DECLARED: (NOS, 'ha contagem sem grao declarado, e contagem sem grao '
                              'nao se compara com contagem.'),
    DECISION_MISSING: (PESSOA, 'a corrida existe e nao ha recibo de decisao: sabemos '
                               'o resultado e nao por que se gastou.'),
    # ── vindos de `telemetria.py` em O8C ─────────────────────────────────
    # `GRAIN_NOT_DECLARED` e `GRAIN_MISMATCH` NAO sao o mesmo defeito, e por
    # isso convivem: um e nao ter dito o grao, o outro e ter dito dois graos
    # diferentes e dividido um pelo outro na mesma conta.
    GRAIN_MISMATCH: (NOS, 'contou-se entrada e saida em unidades diferentes. '
                          'A razao entre elas nao e rendimento.'),
    UPSTREAM_NOT_RUN: (NOS, 'a etapa anterior nao correu. Esta nao falhou — nunca '
                            'comecou, e chamar-lhe erro faria um defeito parecer dois.'),
    OWNER_NOT_CONNECTED: (NOS, 'ha dono declarado para a etapa e ele nao toca o '
                               'artefato. OWNER EXISTS != EDGE EXISTS.'),
    STORAGE_MISSING: (NOS, 'a linha existe no banco e o byte nao esta no armazem.'),
    STORAGE_CONFLICT: (NOS, 'o byte existe e nao e o que a linha diz que ele e.'),
}

# Quando a falha e de item, o estado canonico de `falhas.py` sugere o codigo da
# etapa. O mapa e por ETAPA, porque a mesma falha em etapas diferentes manda a
# pessoa a sitios diferentes.
POR_ETAPA = {
    'DISCOVER': DISCOVER_FAILED,
    'FETCH': FETCH_FAILED,
    'RAW': RAW_PERSISTENCE_FAILED,
    'DERIVED': DERIVATION_FAILED,
    'STRUCTURED': STRUCTURED_NOT_CONNECTED,
    'ADMISSION': ADMISSION_NOT_CONNECTED,
}


def valido(codigo):
    return codigo in CODIGOS


def dono(codigo):
    """Quem tem de agir. Um codigo sem dono e um alerta que fica no ecra."""
    return CODIGOS[codigo][0] if codigo in CODIGOS else None


def explicar(codigo):
    return CODIGOS[codigo][1] if codigo in CODIGOS else None


def da_etapa(etapa, estado_canonico=None):
    """O codigo que esta etapa produz quando falha.

    `estado_canonico` vem de `falhas.py` e nao e ignorado: ele decide quando a
    falha e da ROTA e nao nossa. Uma rota que respondia e parou de responder e
    `ROUTE_NO_LONGER_WORKS`, e nao `FETCH_FAILED` — o primeiro diz «mude de
    porta», o segundo diz «tente de novo».
    """
    if estado_canonico and falhas.camada(estado_canonico) == falhas.ROUTE:
        if falhas.recuperacao(estado_canonico) == falhas.CHANGE_ROUTE:
            return ROUTE_NO_LONGER_WORKS
    return POR_ETAPA.get(str(etapa).upper())


if __name__ == '__main__':
    print('CODIGOS DE DIAGNOSTICO — %d' % len(CODIGOS))
    for c, (d, o) in sorted(CODIGOS.items()):
        print('  %-28s %-14s %s' % (c, d, o[:60]))
