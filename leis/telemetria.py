#!/usr/bin/env python3
"""O CONTRATO DA TELEMETRIA — o minimo para o sistema saber contar-se.

    MODULE WORKS  !=  EDGE WORKS  !=  FLOW WORKS.

Cada modulo pode passar nos seus testes, cada ligacao pode existir, e o fluxo
inteiro continuar sem trazer nada. Tres missoes desta casa acharam estado
publicado sem medicao — e sempre tarde. Isto e o contrato que torna a terceira
pergunta respondivel.

O QUE ISTO E, E O QUE NAO E
---------------------------
E um CONTRATO: o vocabulario e as leis que qualquer emissor de telemetria tem
de cumprir. NAO instala nada. OpenTelemetry, OpenLineage, Grafana, Prometheus e
Tempo serviram de referencia conceitual e ficam de fora: instalar ferramenta
antes de saber o que se quer medir e comprar a tampa antes de medir o buraco.

    NAO SE INSTRUMENTA O QUE AINDA NAO SE SABE PERGUNTAR.

A LEI DO 100%
-------------
    100% NAO PRECISA CHEGAR.
    100% PRECISA SER EXPLICADO.

Uma coleta que traz 40 de 100 nao esta errada por trazer 40. Esta errada se
ninguem souber onde foram os outros 60. Por isso a conta que importa nao e o
rendimento — e a RECONCILIACAO:

    UNACCOUNTED_INPUT = 0

Tudo o que entrou saiu por alguma porta com nome: passou, foi rejeitado, deu
erro, nao correu, ou ficou desconhecido. O que nao tem porta e o defeito.

E O GRAO MUDA NO CAMINHO
------------------------
    INPUT != OUTPUT QUANDO O GRAO MUDA.

Um PDF entra e saem 40 paginas de texto. `OUTPUT/INPUT = 40` nao e 4000% de
rendimento — e uma divisao entre duas unidades diferentes. Por isso cada etapa
declara o grao da entrada e o grao da saida, e so se comparam contagens do
mesmo grao.

AS QUATRO CONFUSOES QUE ESTE CONTRATO RECUSA
--------------------------------------------
    ERROR    != REJECTED    o sistema falhou / o item nao servia
    UNKNOWN  != ZERO        ninguem mediu / mediu-se e deu nada
    NOT_RUN  != ERROR       nao chegou a correr / correu e falhou
    LATE     != MISSING     ainda nao veio / nao vem

Cada uma delas ja foi achatada nalgum relatorio desta casa, e o resultado foi
sempre o mesmo: um numero que parecia bom porque escondia o que nao sabia.
"""

CONTRATO = 'TELEMETRIA/v1'

# ─────────────────────────────────────────────────────────────────────────
# AS ESPECIES DE EVENTO — cada uma responde a uma pergunta diferente
# ─────────────────────────────────────────────────────────────────────────
ESPECIES = {
    'RUN': 'uma execucao inteira, com principio e fim declarados',
    'STAGE': 'uma etapa dentro da corrida (DISCOVER, FETCH, RAW, ...)',
    'EDGE_PASSAGE': 'a passagem de um artefato de uma etapa para a seguinte',
    'FAILURE': 'a etapa parou, e por que codigo',
    'FAILURE_SNAPSHOT': 'o que estava a mao no momento em que parou',
}

# ⚠️ O ESTADO DE UMA ETAPA NAO E UM BOOLEANO.
# `NOT_RUN` existe porque uma etapa a jusante de uma que falhou NAO falhou —
# ela nunca comecou. Chamar-lhe erro faria um defeito parecer cinco.
ESTADOS_DE_ETAPA = (
    'NOT_RUN',      # nunca comecou (a montante falhou, ou nao chegou a vez)
    'RUNNING',
    'PASS',
    'PARTIAL',      # correu e trouxe parte, com o resto explicado
    'FAIL',
    'SKIPPED',      # decidido nao correr, com razao escrita
    'NOT_APPLICABLE',   # nao existe nesta rota, com razao escrita
)

# As portas por onde um item de entrada pode sair. Se um item nao sai por
# nenhuma, ele e UNACCOUNTED — e isso e o defeito que a reconciliacao caca.
DESTINOS_DO_ITEM = (
    'PASSED',
    'REJECTED',     # nao servia. NAO e erro do sistema
    'ERROR',        # o sistema falhou a processa-lo
    'NOT_RUN',
    'UNKNOWN',      # medido, e nao se sabe. NAO e zero
    'DEDUPED',      # ja existia, com prova de igualdade
)

# ⚠️ CODIGO DE DIAGNOSTICO E DECLARADO, NAO INVENTADO NA HORA.
# Uma mensagem livre por falha e uma mensagem que ninguem consegue contar.
CODIGOS_DE_DIAGNOSTICO = {
    'EXECUTOR_UNAVAILABLE': 'a ferramenta nao esta na maquina',
    'ACCESS_FAILURE': 'a porta nao abriu — NAO prova que a fonte nao existe',
    'EGRESS_MISMATCH': 'saida de rede errada para esta fonte; sinal FRACO',
    'SHAPE_UNEXPECTED': 'veio, e nao tem a forma que o contrato declara',
    'GRAIN_MISMATCH': 'contou-se entrada e saida em unidades diferentes',
    'UPSTREAM_NOT_RUN': 'a etapa anterior nao correu',
    'OWNER_NOT_CONNECTED': 'ha dono para a etapa, e ele nao toca o artefato',
    'STORAGE_MISSING': 'a linha existe e o byte nao esta la',
    'STORAGE_CONFLICT': 'o byte existe e nao e o que a linha diz',
    'QUOTA_EXHAUSTED': 'rota com quota, e ela acabou',
    'POLICY_REFUSED': 'a politica proibiu — NAO e falha tecnica',
    'UNKNOWN_FAILURE': 'parou, e o codigo ainda nao existe. Fica visivel assim',
}

# O que cada RUN tem de declarar para ser reconciliavel.
CAMPOS_DO_RUN = (
    'RUN_ID', 'ROUTE_CLASS_ID', 'SOURCE_ID', 'STARTED_AT', 'FINISHED_AT',
    'RUN_STATE', 'POLICY_VERSION', 'CODE_VERSION', 'LAST_GOOD_STAGE',
    'RESUME_SAFE', 'COST', 'COST_UNIT', 'DURATION_MS',
)

# O que cada STAGE tem de declarar.
CAMPOS_DA_ETAPA = (
    'RUN_ID', 'STAGE', 'STAGE_STATE', 'INPUT_GRAIN', 'OUTPUT_GRAIN',
    'INPUT_COUNT', 'OUTPUT_COUNT', 'PASSED', 'REJECTED', 'ERRORS',
    'NOT_RUN', 'UNKNOWN', 'DEDUPED', 'UNACCOUNTED_INPUT',
    'DIAGNOSTIC_CODE', 'DURATION_MS',
)

# ⚠️ RETOMAR NAO E RECOMECAR.
# `LAST_GOOD_STAGE` existe para uma corrida interrompida continuar de onde
# parou. Recomecar do zero criaria uma SEGUNDA corrida — e ja aconteceu aqui:
# um relatorio rebentou depois de a producao estar correta, e a tentacao foi
# correr tudo outra vez.
RESUME = {
    'RESUME_SAFE': 'a etapa e idempotente e pode ser repetida sem duplicar',
    'RESUME_UNSAFE': 'repetir criaria artefato novo; exige decisao humana',
    'RESUME_UNKNOWN': 'ninguem provou nenhuma das duas',
}


def reconcilia(etapa):
    """A conta que tem de fechar. Devolve (fecha?, sobra).

    Nao e rendimento. E reconciliacao: tudo o que entrou saiu por alguma porta
    com nome. O que sobra e o que ninguem consegue explicar.
    """
    saidas = ('PASSED', 'REJECTED', 'ERRORS', 'NOT_RUN', 'UNKNOWN', 'DEDUPED')
    entrada = etapa.get('INPUT_COUNT')
    if entrada is None:
        return False, None            # UNKNOWN != ZERO: sem entrada, nao fecha
    sobra = entrada - sum(etapa.get(k) or 0 for k in saidas)
    return sobra == 0, sobra


def compara_contagens(etapa):
    """So se comparam entrada e saida se o GRAO for o mesmo.

    ⚠️ Um PDF que vira 40 paginas nao tem 4000% de rendimento. Tem duas
    unidades diferentes, e dividir uma pela outra e uma conta sem sentido.
    """
    if etapa.get('INPUT_GRAIN') != etapa.get('OUTPUT_GRAIN'):
        return None, 'GRAIN_MISMATCH: graos diferentes nao se dividem'
    entrada = etapa.get('INPUT_COUNT') or 0
    if not entrada:
        return None, 'UNKNOWN: sem entrada nao ha razao a calcular'
    return (etapa.get('OUTPUT_COUNT') or 0) / entrada, None


LEIS = (
    'MODULE WORKS != EDGE WORKS != FLOW WORKS',
    'INPUT != OUTPUT QUANDO O GRAO MUDA',
    '100% NAO PRECISA CHEGAR — 100% PRECISA SER EXPLICADO',
    'UNACCOUNTED_INPUT DEVE SER 0',
    'ERROR != REJECTED',
    'UNKNOWN != ZERO',
    'NOT_RUN != ERROR',
    'RETOMAR NAO E RECOMECAR',
)

NAO_INSTALAR = (
    'OpenTelemetry', 'OpenLineage', 'Grafana', 'Prometheus', 'Tempo',
)
PORQUE_NAO_INSTALAR = (
    'serviram de referencia conceitual. Instalar ferramenta antes de saber o '
    'que se quer perguntar e comprar a tampa antes de medir o buraco — e esta '
    'casa ja pagou por isso uma vez.'
)


def main():
    print('CONTRATO %s' % CONTRATO)
    print('especies %d · estados de etapa %d · destinos %d · diagnosticos %d'
          % (len(ESPECIES), len(ESTADOS_DE_ETAPA), len(DESTINOS_DO_ITEM),
             len(CODIGOS_DE_DIAGNOSTICO)))
    for l in LEIS:
        print('  · %s' % l)
    print('NAO INSTALAR: %s' % ', '.join(NAO_INSTALAR))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
