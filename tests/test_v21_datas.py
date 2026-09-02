# -*- coding: utf-8 -*-
"""R6 · A ORDEM DE DATA NÃO PODE DEPENDER DA ORDEM DE TEXTO.

    'N' > '2' EM ORDEM DE TEXTO, E ISSO NÃO É UMA DATA NO FUTURO.
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'scripts'))
import v21_datas as DT  # noqa: E402

CORTE = date(2026, 9, 2)


def test_prosa_nunca_vira_data():
    """O defeito exato: a prosa era lexicograficamente maior que a data."""
    prosa = 'NAO_SEI — pagina sem data de publicacao visivel'
    assert prosa > '2026-09-02', 'a premissa do teste mudou'      # ordem de TEXTO
    r = DT.analisar(('REFERENCE_DATE', prosa))
    assert r['DATE_PARSE_STATE'] == DT.UNKNOWN, r
    assert DT.e_futuro(r, CORTE) is False, 'prosa entrou como evento futuro'


def test_ordenacao_nao_depende_de_string():
    """Um evento de 2027 escrito em pt-BR ordena depois de um de 2026 em ISO."""
    a = DT.analisar(('DATE', '2026-11-10 a 2026-11-14'))
    b = DT.analisar(('DATE', '11/04/2027'))
    assert a['START_DATE'] < b['START_DATE'], (a, b)
    assert '11/04/2027' < '2026-11-10', 'a premissa do teste mudou'  # ordem de TEXTO


def test_intervalo_e_reconhecido():
    r = DT.analisar(('DATE', '2026-11-10 a 2026-11-14'))
    assert r['DATE_PARSE_STATE'] == DT.RANGE
    assert (r['START_DATE'], r['END_DATE']) == ('2026-11-10', '2026-11-14')


def test_mes_sem_dia_e_month_only():
    r = DT.analisar(('DATE', '2026-11'))
    assert r['DATE_PARSE_STATE'] == DT.MONTH_ONLY, r


def test_desconhecido_nunca_entra_em_proximos():
    r = DT.analisar(('DATE', ''), ('REFERENCE_DATE', 'conteudo NAO aberto'))
    assert r['DATE_PARSE_STATE'] == DT.UNKNOWN
    assert DT.e_futuro(r, CORTE) is False


def test_passado_nao_e_futuro():
    r = DT.analisar(('DATE', '2026-02-04 a 2026-02-07'))
    assert DT.e_futuro(r, CORTE) is False, r


def test_data_de_origem_fica_registrada():
    r = DT.analisar(('DATE', ''), ('REFERENCE_DATE', '2026-11-10'))
    assert r['DATE_SOURCE'] == 'REFERENCE_DATE', r
