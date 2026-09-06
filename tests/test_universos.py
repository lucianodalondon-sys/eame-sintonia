#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGRESSÕES DO EXPECTED_UNIVERSE.

Roda com ou sem pytest (não há pytest nem pip neste ambiente).

    python3 tests/test_universos.py
"""

from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.environ.get('PASSAPORTE_REF', r'C:\eame-sintonia-passport-ref')
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

from passaporte_universos import (                             # noqa: E402
    DIMENSOES, DONOS, SEM_DONO, avaliar, universo_acervo_it,
    universo_execucoes, universo_passaporte)


def _completo(**troca):
    """Um universo com as CINCO dimensões declaradas e batendo. É o único que passa."""
    u = {
        'DECLARED': True,
        'EXPECTED_FILE_COUNT': 10, 'SCANNED_FILE_COUNT': 10,
        'EXPECTED_RECORD_COUNT': 100, 'SCANNED_RECORD_COUNT': 100,
        'EXPECTED_FAMILIES': ['A', 'B'], 'SCANNED_FAMILIES': ['A', 'B'],
        'EXPECTED_COLLECTIONS': ['K1', 'K2'], 'SCANNED_COLLECTIONS': ['K1', 'K2'],
        'EXPECTED_FINGERPRINT': 'abc', 'SCANNED_FINGERPRINT': 'abc',
        'MISSING': [], 'EXTRA': [],
    }
    u.update(troca)
    return u


# ══════════════════════════════════════════════════════════════════════════════════
# O caso que PASSA — sem ele, os outros não provam nada
# ══════════════════════════════════════════════════════════════════════════════════

def test_universo_correto_passa():
    v = avaliar('X', _completo())
    assert v['PASS'] is True, f'um universo íntegro reprovou: {v}'


# ══════════════════════════════════════════════════════════════════════════════════
# Os casos que TÊM de reprovar
# ══════════════════════════════════════════════════════════════════════════════════

def test_arquivo_esperado_ausente_reprova():
    v = avaliar('X', _completo(MISSING=['a.json'], SCANNED_FILE_COUNT=9))
    assert v['PASS'] is False
    assert 'MISSING' in v['PROBLEMAS']


def test_arquivo_extra_nao_declarado_reprova():
    v = avaliar('X', _completo(EXTRA=['novo.json'], SCANNED_FILE_COUNT=11))
    assert v['PASS'] is False
    assert 'EXTRA' in v['PROBLEMAS']


def test_novo_arquivo_sem_atualizar_o_contrato_reprova():
    """O contrato diz 10; alguém acrescentou o 11º e não atualizou. Tem de cair."""
    v = avaliar('X', _completo(SCANNED_FILE_COUNT=11, EXTRA=['acrescentado.json']))
    assert v['PASS'] is False
    assert v['MOTIVO'] == 'UNIVERSE_DRIFT'


def test_familia_esperada_ausente_reprova():
    v = avaliar('X', _completo(EXPECTED_FAMILIES=None))
    assert v['PASS'] is False
    assert v['MOTIVO'] == 'EXPECTED_DIMENSIONS_MISSING'
    assert 'EXPECTED_FAMILIES' in v['DIMENSOES_AUSENTES']


def test_zero_registros_reprova():
    v = avaliar('X', _completo(SCANNED_RECORD_COUNT=0))
    assert v['PASS'] is False
    assert 'EXPECTED_RECORD_COUNT' in v['PROBLEMAS']


def test_universo_vazio_reprova():
    v = avaliar('X', _completo(EXPECTED_FILE_COUNT=0, SCANNED_FILE_COUNT=0,
                               EXPECTED_RECORD_COUNT=0, SCANNED_RECORD_COUNT=0,
                               EXPECTED_FAMILIES=[], EXPECTED_COLLECTIONS=[]))
    assert v['PASS'] is False, 'universo vazio recebeu PASS — aprova qualquer coisa'


def test_fingerprint_divergente_reprova():
    v = avaliar('X', _completo(SCANNED_FINGERPRINT='outro'))
    assert v['PASS'] is False or 'EXPECTED_FINGERPRINT' in str(v), \
        'digital divergente passou'


def test_chave_de_colecao_desconhecida_reprova():
    v = avaliar('X', _completo(UNKNOWN_COLLECTION_KEY=[{'CHAVE': 'Z'}]))
    assert v['PASS'] is False
    assert 'UNKNOWN_COLLECTION_KEY' in v['PROBLEMAS']


def test_universo_nao_declarado_reprova():
    v = avaliar('X', {'DECLARED': False, 'MOTIVO': 'EXPECTED_UNIVERSE_NOT_DECLARED'})
    assert v['PASS'] is False
    assert v['MOTIVO'] == 'EXPECTED_UNIVERSE_NOT_DECLARED'


def test_faltar_uma_dimensao_ja_reprova():
    """As cinco dimensões são obrigatórias. Quatro não bastam."""
    for d in DIMENSOES:
        v = avaliar('X', _completo(**{d: None}))
        assert v['PASS'] is False, f'passou sem {d}'
        assert d in v['DIMENSOES_AUSENTES']


# ══════════════════════════════════════════════════════════════════════════════════
# Os universos REAIS — e a lei de não fundir universos distintos
# ══════════════════════════════════════════════════════════════════════════════════

def test_os_tres_universos_tem_donos_distintos():
    donos = {d['OWNER_FILE'] for d in DONOS.values()}
    assert len(donos) == 3, 'dois universos apontam para o mesmo dono'
    escopos = {d['SCOPE'] for d in DONOS.values()}
    assert len(escopos) == 3, 'dois universos declaram o mesmo escopo'


def test_a_uniao_dos_universos_nao_tem_dono_e_isso_esta_declarado():
    assert 'UNIVERSE_DATA_SAMPLES_INTEIRO' in SEM_DONO
    assert SEM_DONO['UNIVERSE_DATA_SAMPLES_INTEIRO']['POR_QUE_NAO_TEM_DONO']


def test_nenhum_universo_real_recebe_pass_hoje():
    """Se algum passar, é porque um dono foi atualizado — e aí este teste tem de cair,
    para que a mudança seja notada em vez de escorregar."""
    if not os.path.isfile(os.path.join(REF, 'scripts', 'passaporte_backfill.py')):
        print('      (pulado: NAO_MEDIDO — worktree de referência ausente)')
        return
    us = {'P': universo_passaporte(RAIZ, REF),
          'A': universo_acervo_it(RAIZ),
          'E': universo_execucoes(RAIZ)}
    for k, u in us.items():
        assert avaliar(k, u)['PASS'] is False, \
            f'{k} passou — um dono foi atualizado, reveja o contrato'


def test_o_universo_do_passaporte_nao_declara_registros_nem_digital():
    """O dono declara arquivos, e só. Dizer que ele declara mais seria inventar."""
    if not os.path.isfile(os.path.join(REF, 'scripts', 'passaporte_backfill.py')):
        print('      (pulado: NAO_MEDIDO — worktree de referência ausente)')
        return
    u = universo_passaporte(RAIZ, REF)
    assert u['DECLARED'] is True
    assert u['EXPECTED_FILE_COUNT'] > 0
    assert u['EXPECTED_RECORD_COUNT'] is None
    assert u['EXPECTED_FINGERPRINT'] is None


def test_o_universo_de_execucoes_declara_forma_e_nao_extensao():
    u = universo_execucoes(RAIZ)
    assert u['DECLARED'] is False
    assert u['MOTIVO'] == 'OWNER_DECLARES_SHAPE_NOT_EXTENT'
    assert u['SCANNED_RUN_COUNT'] >= 0


def test_o_gate_nao_escreve_no_acervo():
    """O portão é leitura. Se ganhar uma escrita, este teste cai."""
    import re as _re
    fonte = open(os.path.join(RAIZ, 'scripts', 'passaporte_universos.py'),
                 encoding='utf-8').read()
    corpo = fonte.split("if args.json:")[0]
    assert not _re.search(r"open\([^)]*['\"][wa]", corpo), \
        'passaporte_universos.py ganhou uma escrita fora do relatório --json'


# ══════════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass
    testes = [(n, o) for n, o in sorted(globals().items())
              if n.startswith('test_') and callable(o)]
    passou, falhou = 0, []
    for nome, funcao in testes:
        try:
            funcao()
            passou += 1
            print(f'  ok    {nome}')
        except AssertionError as erro:
            falhou.append(nome)
            print(f'  FALHA {nome}: {erro}')
        except Exception as erro:                              # noqa: BLE001
            falhou.append(nome)
            print(f'  ERRO  {nome}: {type(erro).__name__}: {erro}')
    print('')
    print(f'{passou} passaram · {len(falhou)} falharam · {len(testes)} regressões')
    raise SystemExit(1 if falhou else 0)
