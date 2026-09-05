# -*- coding: utf-8 -*-
"""
O TESTE MINIMO DO HANDOFF — prova que os 38 ISSUE_ID fariam o motor reconhecer
o que hoje ele nao reconhece, e que nao tiram nada do que ele ja reconhece.

Este teste NAO testa o motor. Testa a PROPOSTA contra o motor, carregado da
branch dele so para leitura. E o teste que o dono do motor copia para o lado de
la depois de aceitar as chaves — e o unico artefacto deste handoff que sabe
dizer 'passou' sem uma pessoa a ler prosa.

    ANCORA: cada ID novo tem uma frase REAL do acervo, com SOURCE_ID.
    Sem frase, nao ha prova de que o ID reconhece alguma coisa.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import it_vocab_handoff as H  # noqa: E402
HANDOFF = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1/IT-VOCAB-HANDOFF-V1.json')

pytestmark = pytest.mark.skipif(
    not os.path.exists(HANDOFF),
    reason='rode scripts/it_vocab_handoff.py primeiro')


@pytest.fixture(scope='module')
def cenario():
    d = json.load(open(HANDOFF))
    M, _, sha = H.motor()
    assert sha.startswith(d['MOTOR_SHA'][:12]), (
        'o motor mudou desde que o handoff foi medido: remeça a medicao')
    velho = {k: list(v) for k, v in M.ISSUE_ALIAS.items()}
    novo = dict(velho)
    for r in d['ROWS']:
        if r['APELIDOS_PROPOSTOS']:
            novo[r['ISSUE_ID_PROPOSTO']] = r['APELIDOS_PROPOSTOS']
    return M, velho, novo, d


def test_o_motor_hoje_nao_conhece_nenhum_dos_ids_propostos(cenario):
    _, velho, _, d = cenario
    for r in d['ROWS']:
        assert r['ISSUE_ID_PROPOSTO'] not in velho, (
            '%s ja existe no motor: a proposta seria uma renomeacao, nao uma adicao'
            % r['ISSUE_ID_PROPOSTO'])


def test_cada_id_novo_reconhece_a_sua_frase_ancora(cenario):
    M, velho, novo, d = cenario
    assert d['TESTE_MINIMO'], 'nenhuma ancora: o handoff nao prova nada'
    for t in d['TESTE_MINIMO']:
        antes = M._todos(t['FRASE'], velho)
        depois = M._todos(t['FRASE'], novo)
        assert t['ISSUE_ID'] not in antes, (
            '%s ja saia desta frase antes da mudanca (%s)' % (t['ISSUE_ID'], t['SOURCE_ID']))
        assert t['ISSUE_ID'] in depois, (
            '%s nao sai de %r (%s): o apelido nao casa'
            % (t['ISSUE_ID'], t['FRASE'][:120], t['SOURCE_ID']))


def test_nenhum_id_existente_perde_a_sua_frase(cenario):
    M, velho, novo, d = cenario
    for t in d['TESTE_MINIMO']:
        antes = set(M._todos(t['FRASE'], velho))
        depois = set(M._todos(t['FRASE'], novo))
        assert not (antes - depois), (
            'a frase de %s deixou de dar %s: a adicao roubou texto a um ID existente'
            % (t['ISSUE_ID'], antes - depois))


def test_apelido_proposto_e_literal_e_nao_regex(cenario):
    M, _, novo, d = cenario
    for r in d['ROWS']:
        for a in r['APELIDOS_PROPOSTOS']:
            assert M._n(a), '%s: apelido %r desaparece na normalizacao' % (r['ISSUE_ID_PROPOSTO'], a)
            assert '(?' not in a and '|' not in a, (
                '%s: apelido %r e expressao regular, e o motor casa literal'
                % (r['ISSUE_ID_PROPOSTO'], a))


def test_nenhum_apelido_tem_dois_donos(cenario):
    M, _, novo, _ = cenario
    dono = {}
    for eid, apel in novo.items():
        for a in apel:
            na = M._n(a)
            assert na not in dono or dono[na] == eid, (
                'o apelido %r pertence a %s e a %s: _casa desempataria pela ordem do '
                'dicionario, que nao e regra defensavel' % (na, dono[na], eid))
            dono[na] = eid


def test_o_handoff_declara_o_que_exige_decisao_humana(cenario):
    _, _, _, d = cenario
    assert set(d['PODE_ENTRAR_SEM_JULGAMENTO_HUMANO']) & set(d['EXIGE_DECISAO_HUMANA']) == set()
    assert (len(d['PODE_ENTRAR_SEM_JULGAMENTO_HUMANO'])
            + len(d['EXIGE_DECISAO_HUMANA'])) == d['ISSUE_IDS_PROPOSTOS']
