#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGRESSÕES DA REGRA DE PERTENÇA DO `UNIVERSE_PASSAPORTE`.

O ponto que estas regressões travam: **o universo se atualiza pela REGRA, não por
alguém editar uma lista à mão.** Arquivo novo que satisfaça a regra passa a ser
esperado sozinho, e aparece como `MISSING` até ganhar passaporte.

Roda sem pytest.
    python3 tests/test_universo_passaporte.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.environ.get('PASSAPORTE_REF', r'C:\eame-sintonia-passport-ref')
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

from passaporte_universo_regra import (                        # noqa: E402
    DECISAO_POR_ITEM, EXECUCAO_PROPRIA, classificar, lista_historica,
    listas_de_registros, portao, universo, varrer)


def _tmp_acervo():
    """Um acervo mínimo de mentira, para exercer a regra sem tocar no de verdade."""
    d = tempfile.mkdtemp(prefix='universo_')
    os.makedirs(os.path.join(d, 'data', 'samples'), exist_ok=True)
    return d


def _por(caminho, obj):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════════════
# A REGRA, exercida em arquivos sintéticos
# ══════════════════════════════════════════════════════════════════════════════════

def test_regra_a_execucao_propria_inclui():
    d = _tmp_acervo()
    try:
        p = os.path.join(d, 'data', 'samples', 'x.json')
        _por(p, {'ITEMS': [{'RUN_ID': 'R1', 'TITLE': 'a'}, {'RUN_ID': 'R2', 'TITLE': 'b'}]})
        e, m, _ = classificar(p)
        assert e == 'IN_UNIVERSE_PASSAPORTE' and m == 'REGRA_A_EXECUCAO_PROPRIA'
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_regra_b_decisao_por_item_inclui():
    d = _tmp_acervo()
    try:
        p = os.path.join(d, 'data', 'samples', 'x.json')
        _por(p, {'ITEMS': [{'IDENTITY_STATE': 'PROVED', 'NOME': 'a'}]})
        e, m, _ = classificar(p)
        assert e == 'IN_UNIVERSE_PASSAPORTE' and m == 'REGRA_B_DECISAO_POR_ITEM'
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_nem_a_nem_b_fica_fora():
    d = _tmp_acervo()
    try:
        p = os.path.join(d, 'data', 'samples', 'x.json')
        _por(p, {'COISAS': [{'NOME': 'a', 'VALOR': 1}]})
        e, m, _ = classificar(p)
        assert e == 'OUT_OF_SCOPE' and m == 'NEM_A_NEM_B'
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_execucao_pertence_a_outro_universo_e_nao_a_este():
    d = _tmp_acervo()
    try:
        p = os.path.join(d, 'data', 'samples', 'runs.json')
        _por(p, {'RUNS': [{'RUN_ID': 'R1', 'ACTOR': 'x', 'INPUT': {}, 'COST_USD': 1,
                           'DATASET_ID': 'D', 'FINISHED_AT': 'z'}]})
        e, m, _ = classificar(p)
        assert e == 'OUT_OF_SCOPE'
        assert m == 'E_UMA_EXECUCAO_PERTENCE_A_UNIVERSE_EXECUCOES'
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_arquivo_ilegivel_e_unknown_scope_e_nao_out_of_scope():
    """Não saber não é estar fora. São estados diferentes, e o portão trata diferente."""
    d = _tmp_acervo()
    try:
        p = os.path.join(d, 'data', 'samples', 'quebrado.json')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write('{ isto nao e json')
        e, m, _ = classificar(p)
        assert e == 'UNKNOWN_SCOPE'
        assert m.startswith('ILEGIVEL')
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_o_leitor_encontra_lista_aninhada():
    """O bug que classificou PUBLIC-COMM errado: a primeira lista não é a certa."""
    obj = {'EXECUTION_ORDER': [{'STEP': 1}],
           'DADOS': {'ACCOUNTS': [{'ACCOUNT_IDENTITY_STATE': 'PROVED'}]}}
    nomes = [n for n, _ in listas_de_registros(obj)]
    assert 'EXECUTION_ORDER' in nomes
    assert any(n.endswith('ACCOUNTS') for n in nomes), 'a lista aninhada sumiu'


# ══════════════════════════════════════════════════════════════════════════════════
# O PONTO: o universo se atualiza pela regra, não editando lista
# ══════════════════════════════════════════════════════════════════════════════════

def test_arquivo_novo_que_satisfaz_a_regra_vira_esperado_sozinho():
    d = _tmp_acervo()
    try:
        base = os.path.join(d, 'data', 'samples')
        _por(os.path.join(base, 'a.json'), {'I': [{'RUN_ID': 'R1'}]})
        antes = universo(d, varrer(d))
        _por(os.path.join(base, 'b.json'), {'I': [{'RUN_ID': 'R2'}]})
        depois = universo(d, varrer(d))
        assert depois['FILE_COUNT'] == antes['FILE_COUNT'] + 1, \
            'arquivo novo que satisfaz a regra NÃO virou esperado'
        assert depois['FINGERPRINT'] != antes['FINGERPRINT'], \
            'a digital não mudou quando o universo mudou'
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_arquivo_fora_do_escopo_nao_altera_o_universo():
    d = _tmp_acervo()
    try:
        base = os.path.join(d, 'data', 'samples')
        _por(os.path.join(base, 'a.json'), {'I': [{'RUN_ID': 'R1'}]})
        antes = universo(d, varrer(d))
        _por(os.path.join(base, 'doc.json'), {'TEXTO': 'nota', 'COISAS': [{'X': 1}]})
        depois = universo(d, varrer(d))
        assert depois['FILE_COUNT'] == antes['FILE_COUNT'], \
            'arquivo fora do escopo entrou no universo'
        assert depois['FINGERPRINT'] == antes['FINGERPRINT'], \
            'a digital mudou por causa de arquivo fora do escopo'
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_universo_vazio_nao_e_universo():
    d = _tmp_acervo()
    try:
        u = universo(d, varrer(d))
        assert u['FILE_COUNT'] == 0 and u['RECORD_COUNT'] == 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_a_soma_da_classificacao_fecha():
    r = varrer(RAIZ)
    estados = [v[0] for v in r.values()]
    validos = {'IN_UNIVERSE_PASSAPORTE', 'OUT_OF_SCOPE', 'UNKNOWN_SCOPE'}
    assert set(estados) <= validos, 'apareceu um estado fora dos três'
    assert len(estados) == len(r), 'a soma não fecha'


def test_todo_out_of_scope_tem_motivo():
    r = varrer(RAIZ)
    for rel, (estado, motivo, _) in r.items():
        if estado == 'OUT_OF_SCOPE':
            assert motivo, f'{rel} está fora do escopo sem motivo declarado'


# ══════════════════════════════════════════════════════════════════════════════════
# A LISTA HISTÓRICA NÃO VENCE A REGRA
# ══════════════════════════════════════════════════════════════════════════════════

def _tem_ref():
    return os.path.isfile(os.path.join(REF, 'scripts', 'passaporte_backfill.py'))


def test_a_regra_cobre_toda_a_lista_historica():
    """Nenhum arquivo que a lista declara item pode escapar da regra."""
    if not _tem_ref():
        print('      (pulado: NAO_MEDIDO — referência ausente)')
        return
    carrega, _ = lista_historica(REF)
    dentro = set(universo(RAIZ, varrer(RAIZ))['FILES'])
    escaparam = sorted(carrega - dentro)
    assert not escaparam, f'a regra não pega o que a lista declara: {escaparam}'


def test_a_regra_encontra_mais_do_que_a_lista_e_a_lista_nao_vence():
    if not _tem_ref():
        print('      (pulado: NAO_MEDIDO — referência ausente)')
        return
    carrega, _ = lista_historica(REF)
    dentro = set(universo(RAIZ, varrer(RAIZ))['FILES'])
    assert len(dentro) > len(carrega), \
        'a regra virou a lista — se isso acontecer, alguém trocou a regra pela história'


def test_o_portao_compara_as_cinco_dimensoes():
    if not _tem_ref():
        print('      (pulado: NAO_MEDIDO — referência ausente)')
        return
    g, _, _ = portao(RAIZ, REF)
    for dim in ('FILES', 'RECORDS', 'FAMILIES', 'COLLECTIONS', 'FINGERPRINT'):
        assert g.get('EXPECTED_' + dim) is not None, f'EXPECTED_{dim} não declarado'
        assert g.get('SCANNED_' + dim) is not None, f'SCANNED_{dim} não medido'


def test_arquivo_que_pertence_e_nao_tem_passaporte_reprova():
    if not _tem_ref():
        print('      (pulado: NAO_MEDIDO — referência ausente)')
        return
    g, _, _ = portao(RAIZ, REF)
    assert g['PASS'] is False
    assert len(g['MISSING']) > 0, 'não há MISSING — o portão perdeu a capacidade de ver'


def test_fingerprint_esperada_difere_da_coberta_hoje():
    if not _tem_ref():
        print('      (pulado: NAO_MEDIDO — referência ausente)')
        return
    g, _, _ = portao(RAIZ, REF)
    assert g['EXPECTED_FINGERPRINT'] != g['SCANNED_FINGERPRINT'], \
        'as digitais coincidem — o portão estaria comparando uma conta consigo mesma'


def test_o_unknown_critico_mantem_o_portao_vermelho():
    """A condição de PERTENÇA não está declarada. Enquanto não estiver, FAIL."""
    if not _tem_ref():
        print('      (pulado: NAO_MEDIDO — referência ausente)')
        return
    g, _, _ = portao(RAIZ, REF)
    assert g['MOTIVO'] == 'MEMBERSHIP_CONDITION_NOT_DECLARED'
    assert len(g['UNKNOWN_CRITICO']) > 0


def test_universo_nao_e_pasta():
    """`data/samples` é diretório físico. Estar nele não põe ninguém no universo."""
    r = varrer(RAIZ)
    fora = sum(1 for v in r.values() if v[0] == 'OUT_OF_SCOPE')
    assert fora > 0, 'todo arquivo do diretório entrou — o universo virou a pasta'


def test_o_script_nao_escreve_no_acervo():
    import re as _re
    fonte = open(os.path.join(RAIZ, 'scripts', 'passaporte_universo_regra.py'),
                 encoding='utf-8').read()
    corpo = fonte.split("if args.json:")[0]
    assert not _re.search(r"open\([^)]*['\"][wa]", corpo), \
        'o script ganhou uma escrita fora do relatório --json'


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
