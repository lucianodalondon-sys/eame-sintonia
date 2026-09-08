#!/usr/bin/env python3
"""A POLITICA DA COLETA — o conteudo da decisao: o que, quando, e por que.

DUAS SESSOES ESCREVERAM ESTA MISSAO EM PARALELO, e as duas chamaram
`leis/gestao_da_coleta.py` ao seu ficheiro. Nao eram a mesma coisa:

    gestao_da_coleta.py  desenha a FRONTEIRA — quem decide o que, o que o
                         gestor nao pode fazer, o que fica no orquestrador.
    politica_da_coleta.py (aqui) preenche o CONTEUDO dessa decisao — tiers,
                         ciclo de vida da fonte, acoes, dimensoes, e a
                         politica V1 deterministica em modo SHADOW.

As duas definiam SATISFACAO, com sentidos diferentes. Fundi-las num ficheiro
so daria duas verdades com o mesmo nome, que e pior do que duas leis. A
fronteira ficou com o nome original; o conteudo mudou de nome. Nada foi
descartado dos dois lados.

    O COLLECTION MANAGER NAO E UM SEGUNDO ORQUESTRADOR.

A fronteira e dura, e existe porque a tentacao de a atravessar e grande:

    MANAGER      responde O QUE, QUANDO, COM QUE PRIORIDADE, e SE JA TEMOS
    ORQUESTRADOR responde COMO, POR QUAL ROTA, COM QUE EXECUTOR
    EXECUTOR     so executa

O Manager entrega uma DECISAO. Ele nunca chama coletor, navegador, API ou
Apify — se chamasse, seria um segundo orquestrador, e dois orquestradores
divergem na primeira pressa.

O QUE ESTE FICHEIRO E, E O QUE NAO E
-------------------------------------
E o CONTRATO: o vocabulario, os estados, os portoes e a politica V1
deterministica. Nada aqui dispara coleta, altera agendamento ou promove
politica.

    A POLITICA V1 PODE PLANEAR, RECOMENDAR, EXPLICAR E SIMULAR.
    ELA NAO EXECUTA.

E nao ha aprendizagem automatica aqui. Ha o suficiente para que uma futura
aprenda: decisao versionada, resultado ligavel, baseline, e o par
champion/challenger representavel.

    AUTOMATIC LEARNING NAO E AUTOMATIC PROMOTION.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401

POLICY_VERSION = 'coleta-v1:deterministica'

# ── O PORTAO DA SATISFACAO ───────────────────────────────────────────────
#     ALREADY HELD MUST BE CHECKED BEFORE NEW COLLECTION.
JA_TENHO_FRESCO = 'YES_FRESH'
JA_TENHO_VELHO = 'YES_BUT_STALE'
TENHO_PARTE = 'PARTIAL'
NAO_TENHO = 'NO'
NAO_SEI = 'UNKNOWN'
SATISFACAO = (JA_TENHO_FRESCO, JA_TENHO_VELHO, TENHO_PARTE, NAO_TENHO, NAO_SEI)

# ── AS ACOES ─────────────────────────────────────────────────────────────
# `CHECK` existe separado de `FETCH` de proposito:
#
#     CHECK_FOR_CHANGE NAO E FETCH_CONTENT.
#
# E outra distincao que se perde facil:
#
#     CONTENT_ALREADY_KNOWN NAO E NEW_OBSERVATION_USELESS.
#
# Reencontrar o mesmo conteudo e um FATO de procedencia que vale registrar —
# sem baixar nem reprocessar os mesmos bytes.
CHECK = 'CHECK'
FETCH = 'FETCH'
SKIP = 'SKIP'
TRIAL = 'TRIAL'
RETRY = 'RETRY'
ACOES = (CHECK, FETCH, SKIP, TRIAL, RETRY)

# ── AS PRIORIDADES ───────────────────────────────────────────────────────
TIERS = {
    'P0': 'lacuna critica: falta informacao que alguem pediu e nao temos',
    'P1': 'importante e velho: temos, e ja nao serve',
    'P2': 'fonte boa e ativa, na hora dela',
    'P3': 'exploracao: fonte ou rota nova, em teste',
    'P4': 'baixo rendimento, redundante, ou adiavel',
}

# ── AS DIMENSOES ─────────────────────────────────────────────────────────
# Preservadas, e NUNCA colapsadas num numero.
#
#     SOURCE_SCORE = 87 NAO EXISTE AQUI.
#
# Uma nota unica esconde POR QUE a fonte vale, e nota que ninguem desmonta nao
# se audita nem se melhora. Duas fontes com 87 podem ser boas por motivos
# opostos — uma por render muito, outra por custar quase nada.
DIMENSOES = ('REQUIREMENT_PRIORITY', 'GAP_SEVERITY', 'STALENESS',
             'EXPECTED_CHANGE', 'SOURCE_HEALTH', 'SOURCE_QUALITY',
             'UNIQUE_YIELD', 'READY_YIELD', 'COST', 'ROUTE_HEALTH')

# ── O CICLO DE VIDA DA FONTE ─────────────────────────────────────────────
#     DISCOVERED NAO E ACTIVE.
CICLO = ('DISCOVERED', 'SCREENED', 'TRIAL', 'PROBATION', 'ACTIVE',
         'DEGRADED', 'QUARANTINED', 'RETIRED')

# Uma candidata nao salta para ACTIVE: passa por teste e por medicao. Cada
# transicao permitida esta escrita, e o que nao esta escrito nao acontece.
TRANSICOES = {
    'DISCOVERED': ('SCREENED', 'QUARANTINED'),
    'SCREENED': ('TRIAL', 'QUARANTINED'),
    'TRIAL': ('PROBATION', 'QUARANTINED', 'SCREENED'),
    'PROBATION': ('ACTIVE', 'DEGRADED', 'QUARANTINED'),
    'ACTIVE': ('DEGRADED', 'QUARANTINED'),
    'DEGRADED': ('ACTIVE', 'QUARANTINED'),
    'QUARANTINED': ('SCREENED', 'RETIRED'),
    'RETIRED': (),
}

# ── OS PAPEIS ────────────────────────────────────────────────────────────
#     BAD EVIDENCE SOURCE NAO E USELESS SOURCE.
# Uma fonte que so replica o que outras dizem e ma para corroborar — e pode ser
# otima para DESCOBRIR a original. Um papel so apagaria a segunda.
PAPEIS = ('EVIDENCE', 'DISCOVERY', 'EARLY_WARNING', 'CORROBORATION',
          'CONTEXT', 'REFERENCE')

# ── DESCOBERTA DE CANDIDATAS ─────────────────────────────────────────────
#     DISCOVERY SOURCE NAO E EVIDENCE SOURCE.
# Nao ha crawler nesta missao. Ha o contrato do que uma candidata TEM de dizer
# de si — sem procedencia, ninguem consegue julgar depois se valeu a pena.
CANDIDATA_EXIGE = ('DISCOVERED_FROM', 'DISCOVERED_AT', 'DISCOVERY_METHOD',
                   'DISCOVERY_QUERY_OR_GAP', 'DISCOVERED_BY',
                   'WHY_ADAMA_RELEVANT')

# ── EXPLORACAO x EXPLORACAO DO CONHECIDO ─────────────────────────────────
# O orcamento e CONFIGURAVEL e nao tem valor padrao aqui: 90/10 e 80/20 sao
# numeros que alguem inventou, e inventar um agora seria fingir medicao.
ORCAMENTO_DE_EXPLORACAO = None      # NOT_MEASURED

# ── EVOLUCAO ─────────────────────────────────────────────────────────────
CHAMPION = 'CHAMPION'
CHALLENGER = 'CHALLENGER'
SHADOW = 'SHADOW_ONLY'
PROMOCAO_EXIGE = ('FROM_VERSION', 'TO_VERSION', 'WHY', 'BASELINE',
                  'EXPECTED_IMPROVEMENT', 'PROMOTED_AT', 'ROLLBACK_TO',
                  'ROLLBACK_REASON')
SEM_HISTORICO = 'NOT_ENOUGH_HISTORY'


def satisfacao(tem_conteudo, idade_horas, janela_horas, completo=True):
    """Ja temos? E ainda serve? Esta pergunta vem ANTES de gastar."""
    if tem_conteudo is None:
        return NAO_SEI
    if not tem_conteudo:
        return NAO_TENHO
    if not completo:
        return TENHO_PARTE
    if idade_horas is None or janela_horas is None:
        return NAO_SEI
    return JA_TENHO_FRESCO if idade_horas < janela_horas else JA_TENHO_VELHO


def decidir(*, source_id, satisfaction, source_health='UNKNOWN',
            route_health='UNKNOWN', requirement_priority='P2',
            suporta_check=False, em_trial=False):
    """A politica V1: DETERMINISTICA e explicavel. Devolve a decisao, nao a executa.

    Sem nota magica: cada ramo diz em uma frase por que escolheu, e a mesma
    entrada produz sempre a mesma saida — sem o que nao ha como comparar uma
    politica nova com esta.
    """
    if em_trial:
        return _d(source_id, TRIAL, 'P3',
                  'a fonte esta em teste e ainda nao tem medicao propria',
                  satisfaction, True)
    if satisfaction == JA_TENHO_FRESCO:
        return _d(source_id, SKIP, 'P4',
                  'ja temos, e ainda esta dentro da janela: buscar de novo '
                  'gastaria sem acrescentar', satisfaction, False)
    if satisfaction == NAO_SEI:
        return _d(source_id, CHECK, 'P2',
                  'nao sabemos se ja temos — perguntar custa menos do que buscar',
                  satisfaction, False)
    if satisfaction == JA_TENHO_VELHO and suporta_check:
        # CHECK antes de FETCH: se nada mudou, nao se baixa.
        return _d(source_id, CHECK, 'P1',
                  'venceu a janela, e a rota sabe dizer se mudou sem baixar',
                  satisfaction, False)
    if satisfaction in (NAO_TENHO, TENHO_PARTE):
        tier = 'P0' if requirement_priority == 'P0' else 'P1'
        return _d(source_id, FETCH, tier,
                  'falta informacao pedida e nao a temos', satisfaction, False)
    return _d(source_id, FETCH, 'P2',
              'venceu a janela e a rota nao sabe dizer se mudou sem baixar',
              satisfaction, False)


def _d(source_id, acao, tier, porque, satisfaction, exploracao):
    return {
        'SOURCE_ID': source_id, 'ACAO': acao, 'PRIORITY_TIER': tier,
        'WHY_NOW': porque, 'SATISFACTION_BEFORE': satisfaction,
        'IS_EXPLORATION': exploracao, 'POLICY_VERSION': POLICY_VERSION,
        'MODE': SHADOW,
        # A decisao NAO carrega executor nem rota concreta: isso e do
        # orquestrador. Se carregasse, o Manager viraria o segundo.
        'EXECUTOR': None, 'ROTA_CONCRETA': None,
    }


def transicao_permitida(de, para):
    """DISCOVERED nao vira ACTIVE. O que nao esta escrito nao acontece."""
    return para in TRANSICOES.get(de, ())


def pode_promover_sozinho(*_a, **_k):
    """Nunca. Existe para que a pergunta tenha uma resposta escrita."""
    return False, ('AUTOMATIC LEARNING NAO E AUTOMATIC PROMOTION: uma candidata '
                   'melhor numa metrica pode ser pior noutra, e escolher entre '
                   'as duas e decisao de gente.')


if __name__ == '__main__':
    print(__doc__)
    print('POLICY_VERSION  %s' % POLICY_VERSION)
    print('CICLO           %s' % ' -> '.join(CICLO))
    print('DIMENSOES       %d, nenhuma colapsada' % len(DIMENSOES))
    print('EXPLORACAO      %s' % (ORCAMENTO_DE_EXPLORACAO or 'NOT_MEASURED'))
