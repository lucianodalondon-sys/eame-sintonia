#!/usr/bin/env python3
"""PARIDADE DA LINGUA — contrato = storage = writer = scanner, ou reprova.

    UM CONCEITO, UM DONO.
    OUTROS MODULOS IMPORTAM OU DERIVAM. NAO REDEFINEM.

Esta prova existe porque a fundacao da observabilidade foi escrita por duas
sessoes em paralelo, e o resultado tinha DOIS registries de diagnostico com
ZERO nomes em comum, um enum de banco que misturava duas perguntas, e o writer
a declarar pela terceira vez um vocabulario que o contrato ja tinha.

    WRITER TRUTH = A e SCANNER TRUTH = B e a mesma casa a mentir-se.

O que ela recusa, e o que cada recusa custou quando aconteceu:

  · um estado canonico de telemetria que o banco nao consegue guardar
  · um destino legitimo de item que fica de fora da contabilidade — foi este
    que inventou um UNACCOUNTED=40 num fluxo correto, so por falta de coluna
  · um diagnostic code aceite pelo writer e invisivel ao scanner
  · um diagnostic code publicado pelo scanner e recusado pelo writer
  · um enum do banco a divergir em silencio do dono canonico

NAO gera o enum do banco a partir do Python. Gerar amarraria o SQL a um passo
de build, e uma migration tem de poder ser lida e aplicada sozinha. O que se
exige e PARIDADE: o SQL continua escrito a mao, e esta prova reprova no minuto
em que ele deixar de dizer o mesmo que o dono.

Nao toca a rede, nao toca producao, nao precisa de banco: le o SQL como texto.
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                     # noqa: E402,F401
import falhas                       # noqa: E402
import diagnostico as dg            # noqa: E402
import telemetria as tel            # noqa: E402
import rastro_da_coleta as rastro   # noqa: E402

MIGRATION = os.path.join(RAIZ, 'supabase', 'migrations',
                         '024_a_corrida_conta_o_que_passou.sql')
SCANNER = os.path.join(RAIZ, 'system-map', 'scripts',
                       'censo_da_observabilidade.py')

falhou = []


def ok(nome, detalhe=''):
    print('  PASS  %-52s %s' % (nome, detalhe))


def mal(nome, detalhe=''):
    print('  FAIL  %-52s %s' % (nome, detalhe))
    falhou.append(nome)


def _sql():
    return open(MIGRATION, encoding='utf-8').read()


def _enum(sql, nome):
    """Le os valores de um `create type <nome> as enum (...)` do SQL."""
    m = re.search(r"create type %s as enum\s*\((.*?)\);" % nome, sql, re.S)
    if not m:
        return None
    return tuple(re.findall(r"'([A-Z_]+)'", m.group(1)))


def _colunas_de_contagem(sql):
    """As colunas que entram na soma de `accounted_input`, lidas do SQL."""
    m = re.search(r"accounted_input\s+integer generated always as\s*\((.*?)\)\s*stored",
                  sql, re.S)
    if not m:
        return None
    return tuple(re.findall(r"[a-z_]+", m.group(1)))


# Como um destino do contrato se chama na coluna do banco. A traducao e
# EXPLICITA de proposito: um destino novo sem linha aqui reprova em P3, e nao
# entra na conta em silencio.
COLUNA_DO_DESTINO = {
    'PASSED': 'passed',
    'REJECTED': 'rejected',
    'ERROR': 'error_count',
    'NOT_RUN': 'not_run_count',
    'UNKNOWN': 'unknown_count',
    'REUSED': 'reused',
}


def main():
    sql = _sql()
    print('PARIDADE DA LINGUA — contrato = storage = writer = scanner')
    print('=' * 70)

    # ── P1. UM DONO POR PERGUNTA ────────────────────────────────────────
    # Nenhum diagnostic code pode ter o nome de um estado de falha: sao duas
    # perguntas, e um nome que serve as duas nao responde a nenhuma.
    colisao = set(dg.CODIGOS) & (set(falhas.ESTADOS) | set(falhas._DE_PARA))
    if colisao:
        mal('P1_FAILURE_STATE_NAO_E_DIAGNOSTIC_CODE', 'colidem: %s' % sorted(colisao))
    else:
        ok('P1_FAILURE_STATE_NAO_E_DIAGNOSTIC_CODE',
           '%d falhas · %d codigos · 0 nomes partilhados'
           % (len(falhas.ESTADOS), len(dg.CODIGOS)))

    # O contrato nao pode ter registry proprio: tem de expor o do dono.
    if tuple(sorted(dg.CODIGOS)) != tuple(tel.CODIGOS_DE_DIAGNOSTICO):
        mal('P1_CONTRATO_IMPORTA_O_DONO', 'telemetria publica lista propria')
    else:
        ok('P1_CONTRATO_IMPORTA_O_DONO', 'telemetria expoe diagnostico.CODIGOS')

    # ── P2. ESTADO DE ETAPA != DESTINO DE ITEM ──────────────────────────
    partilham = set(tel.ESTADOS_DE_ETAPA) & set(tel.DESTINOS_DO_ITEM)
    if partilham - {'NOT_RUN'}:
        mal('P2_STAGE_STATE_NAO_E_ITEM_DESTINATION',
            'partilham alem de NOT_RUN: %s' % sorted(partilham - {'NOT_RUN'}))
    else:
        ok('P2_STAGE_STATE_NAO_E_ITEM_DESTINATION',
           'so NOT_RUN e comum, e e de proposito')

    # ── P3. O BANCO GUARDA TODOS E SO OS ESTADOS CANONICOS ──────────────
    enum = _enum(sql, 'etapa_estado')
    if enum is None:
        mal('P3_ENUM_LEGIVEL', 'nao achei create type etapa_estado')
    elif set(enum) != set(tel.ESTADOS_DE_ETAPA):
        mal('P3_ENUM_BATE_COM_O_DONO',
            'so no banco=%s · so no contrato=%s'
            % (sorted(set(enum) - set(tel.ESTADOS_DE_ETAPA)),
               sorted(set(tel.ESTADOS_DE_ETAPA) - set(enum))))
    else:
        ok('P3_ENUM_BATE_COM_O_DONO', '%d estados, exatamente os do contrato' % len(enum))

    # ── P4. TODO DESTINO LEGITIMO TEM BALDE, E ENTRA NA CONTA ───────────
    somadas = _colunas_de_contagem(sql)
    if somadas is None:
        mal('P4_ACCOUNTED_LEGIVEL', 'nao achei a coluna gerada accounted_input')
    else:
        sem_traducao = [d for d in tel.DESTINOS_DO_ITEM if d not in COLUNA_DO_DESTINO]
        fora = [d for d in tel.DESTINOS_DO_ITEM
                if COLUNA_DO_DESTINO.get(d) not in somadas]
        if sem_traducao:
            mal('P4_DESTINO_TEM_COLUNA', 'destino sem coluna declarada: %s' % sem_traducao)
        elif fora:
            mal('P4_DESTINO_ENTRA_NA_CONTA',
                'destino legitimo fora de accounted_input: %s' % fora)
        else:
            ok('P4_DESTINO_ENTRA_NA_CONTA',
               '%d destinos, todos somados' % len(tel.DESTINOS_DO_ITEM))
        # E o inverso: uma coluna a somar que nao e destino de ninguem.
        conhecidas = set(COLUNA_DO_DESTINO.values())
        intrusas = [c for c in somadas if c not in conhecidas]
        if intrusas:
            mal('P4_CONTA_SO_SOMA_DESTINOS', 'somam sem ser destino: %s' % intrusas)
        else:
            ok('P4_CONTA_SO_SOMA_DESTINOS', 'nada entra na conta sem ser destino')

    # ── P5. O WRITER NAO REDEFINE — IMPORTA ─────────────────────────────
    if rastro.ESTADOS is not tel.ESTADOS_DE_ETAPA:
        mal('P5_WRITER_IMPORTA_ESTADOS', 'writer tem tupla propria')
    else:
        ok('P5_WRITER_IMPORTA_ESTADOS', 'rastro.ESTADOS E telemetria.ESTADOS_DE_ETAPA')
    if rastro.DESTINOS is not tel.DESTINOS_DO_ITEM:
        mal('P5_WRITER_IMPORTA_DESTINOS', 'writer tem tupla propria')
    else:
        ok('P5_WRITER_IMPORTA_DESTINOS', 'rastro.DESTINOS E telemetria.DESTINOS_DO_ITEM')

    # ── P6. WRITER E SCANNER LEEM O MESMO REGISTRY ──────────────────────
    # O writer aceita um codigo? Entao o scanner tem de o conhecer, e ao
    # contrario. Como os dois passam a ler `diagnostico`, prova-se que o
    # scanner NAO le uma lista escrita a mao noutro sitio.
    fonte_scanner = open(SCANNER, encoding='utf-8').read()
    aceita_todos = all(dg.valido(c) for c in dg.CODIGOS)
    if not aceita_todos:
        mal('P6_WRITER_ACEITA_OS_CANONICOS', 'writer recusa codigo do proprio registry')
    else:
        ok('P6_WRITER_ACEITA_OS_CANONICOS', '%d codigos aceites' % len(dg.CODIGOS))
    if re.search(r"^\s*CODIGOS_DE_DIAGNOSTICO\s*=\s*[\(\{\[]", fonte_scanner, re.M):
        mal('P6_SCANNER_NAO_TEM_LISTA_PROPRIA', 'scanner declara registry proprio')
    else:
        ok('P6_SCANNER_NAO_TEM_LISTA_PROPRIA', 'scanner nao declara lista')

    # ── P7. NENHUM NOME ANTIGO FOI PERDIDO ──────────────────────────────
    # Os doze nomes que `telemetria` declarava sozinha tem de continuar
    # explicaveis: ou sao de um dono, ou foram recusados com razao escrita.
    sem_destino = []
    for nome, (dono, alvo) in tel.DE_ONDE_VIERAM.items():
        if dono == 'falhas' and alvo not in falhas.ESTADOS:
            sem_destino.append('%s -> %s (nao e estado de falhas)' % (nome, alvo))
        elif dono == 'diagnostico' and alvo not in dg.CODIGOS:
            sem_destino.append('%s -> %s (nao e codigo de diagnostico)' % (nome, alvo))
        elif not alvo:
            sem_destino.append('%s sem destino escrito' % nome)
    if sem_destino:
        mal('P7_NENHUM_NOME_PERDIDO', '; '.join(sem_destino))
    else:
        ok('P7_NENHUM_NOME_PERDIDO',
           '%d nomes antigos, todos com dono ou recusa escrita' % len(tel.DE_ONDE_VIERAM))

    print('=' * 70)
    if falhou:
        print('PARIDADE=FAIL · %d prova(s) reprovada(s)' % len(falhou))
        return 1
    print('PARIDADE=PASS · contrato, storage, writer e scanner falam a mesma lingua')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
