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

import os
import sys

# ⚠️ A RAIZ, E NAO A PASTA DESTE FICHEIRO.
# Ate O9 esta linha punha `leis/` no caminho, e `_gavetas.py` mora na RAIZ:
# `python3 leis/telemetria.py` rebentava com ModuleNotFoundError. A suite
# inteira passava por cima disso, porque cada teste ja insere a raiz antes de
# importar — o defeito so existia para quem corresse o ficheiro sozinho.
#
#     PASSAR NO HARNESS NAO E CORRER.
#
# O padrao da casa esta em `leis/diagnostico.py`, e e este.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas   # noqa: E402,F401
import falhas     # noqa: E402
import diagnostico as dg   # noqa: E402

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

# ⚠️ AS ETAPAS CANONICAS DA AQUISICAO, E O DONO DELAS E ESTE FICHEIRO.
# Ate O9R esta tupla vivia em `medidas/rastro_da_coleta.py` — o WRITER. O
# contrato era dono do ESTADO da etapa e do DESTINO do item, e nao do NOME das
# etapas; e um vocabulario declarado pelo writer e um vocabulario que o
# contrato nao consegue defender. Foi a mesma classe de defeito que o O8C
# desfez em tres sitios; aqui esta o quarto.
#
# A fronteira termina em READY de proposito: INTELLIGENCE, PACKAGE, PORTAL e
# DELIVERY nao entram, porque exigi-las agora faria a fundacao da coleta
# depender de coisas que nao sao coleta. A `024` escreve o mesmo enum a mao, e
# `provas/paridade_da_lingua.py` reprova no minuto em que os dois divergirem.
ETAPAS_DA_COLETA = (
    'DECIDE', 'CHECK', 'DISCOVER', 'FETCH', 'RAW', 'DERIVED',
    'STRUCTURED', 'ADMISSION', 'READY',
)

# ⚠️ DERIVED STORED != READY.
#
# «O texto derivado aterrou no registo» NAO e `READY`. Aterrar e persistencia;
# `READY` e um VEREDITO — alguem olhou para o item e disse que ele entra. Quem
# julga e a porta de admissao, e o executor declara explicitamente que NAO
# julga. Emitir `READY PASS` sem `ADMISSION` e assinar um veredito por um dono
# que nao foi chamado, e faz a cadeia parecer fechada exatamente onde ela nao
# fecha.
#
#     STAGE EXISTS IN VOCABULARY != STAGE RAN.
#
# Isto nao e ordem cronologica generica — nao se declara aqui que FETCH exige
# DISCOVER, porque ha rotas legitimas que comecam noutro sitio. E uma lei sobre
# QUEM ASSINA: `READY` e a unica etapa cujo significado e um julgamento, e por
# isso e a unica que exige que o juiz tenha corrido.
EXIGE_QUEM_ASSINE = {
    'READY': ('ADMISSION',),
}

# Um `READY` so vale se a etapa ja tiver acontecido de verdade. `NOT_RUN`,
# `SKIPPED` e `NOT_APPLICABLE` nao sao «aconteceu».
ETAPA_ACONTECEU = ('PASS', 'PARTIAL')


def ready_sem_quem_assine(passagens):
    """As etapas que se declaram cumpridas sem o dono que as assina.

    Devolve a lista de violacoes; lista vazia = nada a apontar. Cada violacao
    diz a etapa, o estado com que ela se declarou, e quem faltava.

    `passagens` e uma lista de dicionarios com ETAPA e ESTADO — a forma que
    `medidas/rastro_da_coleta.passagens()` devolve, e a mesma que o banco a
    seco produz. Nao le banco nenhum: e uma lei, e leis nao abrem ligacoes.
    """
    aconteceu = {p.get('ETAPA') for p in passagens
                 if p.get('ESTADO') in ETAPA_ACONTECEU}
    fora = []
    for p in passagens:
        etapa, estado = p.get('ETAPA'), p.get('ESTADO')
        if estado not in ETAPA_ACONTECEU:
            continue
        for exigida in EXIGE_QUEM_ASSINE.get(etapa, ()):
            if exigida not in aconteceu:
                fora.append({
                    'ETAPA': etapa,
                    'ESTADO': estado,
                    'FALTA': exigida,
                    'DIAGNOSTIC_CODE': dg.ADMISSION_NOT_CONNECTED,
                    'PORQUE': (
                        '%s declarou-se %s e %s nunca aconteceu nesta corrida. '
                        'DERIVED STORED != READY: persistir nao e julgar.'
                        % (etapa, estado, exigida)),
                })
    return fora


# As portas por onde um item de entrada pode sair. Se um item nao sai por
# nenhuma, ele e UNACCOUNTED — e isso e o defeito que a reconciliacao caca.
DESTINOS_DO_ITEM = (
    'PASSED',
    'REJECTED',     # nao servia. NAO e erro do sistema
    'ERROR',        # o sistema falhou a processa-lo
    'NOT_RUN',
    'UNKNOWN',      # medido, e nao se sabe. NAO e zero
    # ⚠️ O NOME E `REUSED`, E NAO `DEDUPED`. Ate O8C este contrato dizia
    # DEDUPED, e a casa ja dizia REUSED em dois writers ANTERIORES a esta
    # missao — `guarda/preservar_coleta.py` (REUSED_METADATA) e
    # `guarda/preservar_derivado.py` (REUSED, REUSED_AFTER_RACE). Um contrato
    # novo nao renomeia o que o codigo que ja corre chama de outra coisa.
    'REUSED',       # ja existia, com prova de igualdade. NAO e PASSED novo
)

# ═════════════════════════════════════════════════════════════════════════
# ⚠️ ESTE CONTRATO NAO E DONO DE NENHUM CODIGO. ELE IMPORTA OS DONOS.
#
# Ate O8C, este ficheiro declarava um `CODIGOS_DE_DIAGNOSTICO` proprio, com
# doze nomes. Media-se: TRES desses nomes ja pertenciam a `falhas.py`
# — `EXECUTOR_UNAVAILABLE` e `QUOTA_EXHAUSTED` como ESTADO CANONICO, e
# `UNKNOWN_FAILURE` como alias de `UNKNOWN_ERROR`. E `falhas.py` e anterior as
# duas sessoes que escreveram esta missao, e ja e importado por quatro
# coletores reais.
#
#     DUAS PALAVRAS PARA O MESMO ESTADO, SEM TRADUCAO CANONICA,
#     E DUAS VERDADES — E O SCANNER LIA UMA, O WRITER LIA A OUTRA.
#
# Nao se apagou informacao. Cada um dos doze nomes esta abaixo, dito onde
# vive agora. Duas especies, e elas NAO se misturam:
#
#     FAILURE STATE   (falhas.py)      POR QUE o mundo/rota/executor parou.
#                                      Tem camada (SOURCE/ROUTE/EXECUTOR),
#                                      tem `esperado`, tem recuperacao.
#     DIAGNOSTIC CODE (diagnostico.py) ONDE no fluxo parou, e que buraco
#                                      estrutural isso denuncia.
#
#     FAILURE STATE != DIAGNOSTIC CODE.
#
# Uma falha de rede em FETCH tem AS DUAS: estado canonico
# `TRANSIENT_NETWORK_ERROR` (falhas) e codigo `FETCH_FAILED` (diagnostico).
# Perguntas diferentes, respostas diferentes, donos diferentes.
# ═════════════════════════════════════════════════════════════════════════

# Os donos, importados. Quem quiser o vocabulario le AQUI e nao copia.
ESTADOS_DE_FALHA = tuple(sorted(falhas.ESTADOS))
CODIGOS_DE_DIAGNOSTICO = tuple(sorted(dg.CODIGOS))

# O destino dos doze nomes que este ficheiro declarava sozinho. Nenhum foi
# perdido: cada linha diz o dono e o nome canonico, ou por que o nome foi
# recusado. E uma tabela conferivel, nao uma renomeacao de fe.
DE_ONDE_VIERAM = {
    # ── ja eram de `falhas.py`, com o mesmo nome ────────────────────────
    'EXECUTOR_UNAVAILABLE': ('falhas', 'EXECUTOR_UNAVAILABLE'),
    'QUOTA_EXHAUSTED':      ('falhas', 'QUOTA_EXHAUSTED'),
    # ── ja era alias conhecido de `falhas.py` ───────────────────────────
    'UNKNOWN_FAILURE':      ('falhas', 'UNKNOWN_ERROR'),
    # ── `falhas.py` ja distinguia MAIS FINO. Manter o nome grosso apagaria
    #    a diferenca que a casa pagou para descobrir, por isso ele e RECUSADO
    #    e nao absorvido: quem parou tem de dizer QUAL das quatro.
    'ACCESS_FAILURE':       ('falhas/RECUSADO',
                             'ROUTE_UNAVAILABLE | BLOCKED | '
                             'PERMANENT_HTTP_ERROR | TRANSIENT_NETWORK_ERROR'),
    'SHAPE_UNEXPECTED':     ('falhas', 'CONTRACT_DRIFT'),
    # ── condicao de ROTA que `falhas.py` ainda NAO tem. Fica declarada como
    #    buraco, e nao inventada aqui: acrescentar estado a uma lei que quatro
    #    coletores ja importam e missao propria, com o seu proprio red team.
    'EGRESS_MISMATCH':      ('falhas/BURACO_DECLARADO',
                             'sem equivalente; camada ROUTE'),
    # ── NAO E FALHA. E uma DECISAO, e por isso nao mora em nenhum dos dois
    #    registries de falha: a politica escolheu nao ir buscar. O item sai
    #    por NOT_RUN e a etapa fica SKIPPED, com a razao escrita.
    'POLICY_REFUSED':       ('politica_da_coleta/DECISAO',
                             'etapa SKIPPED; NAO e falha tecnica'),
    # ── especie de FLUXO: dizem ONDE parou, nao o que o mundo fez ───────
    'GRAIN_MISMATCH':       ('diagnostico', 'GRAIN_MISMATCH'),
    'UPSTREAM_NOT_RUN':     ('diagnostico', 'UPSTREAM_NOT_RUN'),
    'OWNER_NOT_CONNECTED':  ('diagnostico', 'OWNER_NOT_CONNECTED'),
    'STORAGE_MISSING':      ('diagnostico', 'STORAGE_MISSING'),
    'STORAGE_CONFLICT':     ('diagnostico', 'STORAGE_CONFLICT'),
}

# O que cada RUN tem de declarar para ser reconciliavel.
CAMPOS_DO_RUN = (
    'RUN_ID', 'ROUTE_CLASS_ID', 'SOURCE_ID', 'STARTED_AT', 'FINISHED_AT',
    'RUN_STATE', 'POLICY_VERSION', 'CODE_VERSION', 'LAST_GOOD_STAGE',
    'RESUME_SAFE', 'COST', 'COST_UNIT', 'DURATION_MS',
)

# O que cada STAGE tem de declarar.
# ⚠️ OS BALDES SAO OS DESTINOS, LITERALMENTE — nao uma copia deles.
# Ate O8C esta lista dizia `ERRORS` e a lista de destinos dizia `ERROR`. Uma
# letra, e `reconcilia()` teria lido um campo que nunca existiu: a conta
# fechava a zero por o balde estar sempre vazio, e o defeito era invisivel.
# Por isso os destinos entram aqui por INTERPOLACAO, e nao por transcricao.
CAMPOS_DA_ETAPA = (
    'RUN_ID', 'STAGE', 'STAGE_STATE', 'INPUT_GRAIN', 'OUTPUT_GRAIN',
    'INPUT_COUNT', 'OUTPUT_COUNT',
) + DESTINOS_DO_ITEM + (
    'UNACCOUNTED_INPUT', 'DIAGNOSTIC_CODE', 'DURATION_MS',
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
    saidas = DESTINOS_DO_ITEM
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
    'DERIVED STORED != READY — SEM ADMISSION NAO HA VEREDITO',
    'STAGE EXISTS IN VOCABULARY != STAGE RAN',
    'LEGACY REPLAY INSTRUMENTED != CANONICAL FORWARD INSTRUMENTED',
    'OBSERVABILITY FAILURE != COLLECTION FAILURE',
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
