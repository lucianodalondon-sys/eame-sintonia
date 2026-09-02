# -*- coding: utf-8 -*-
"""R4 · A SEMÂNTICA DE MERCADO, com o defeito real plantado.

    PREÇO DE AZEITE != PREÇO DA AZEITONA != OPORTUNIDADE NA OLIVEIRA.

As 42 observações de mercado da oliveira eram, todas, azeite — nenhuma era
azeitona — e sustentavam o cruzamento de mercado da OLIVEIRA como se fossem preço
da cultura. A causa: a cultura vinha de `crop_id(CROP or PRODUCT)`, e
«Extra virgin olive oil» casa o apelido `oliv`.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'scripts'))
import v21_normalizar as N  # noqa: E402


def test_azeite_nao_e_azeitona():
    assert N.estagio_da_mercadoria('Extra virgin olive oil (up to 0.8%)') == N.PROCESSED_PRODUCT
    assert N.estagio_da_mercadoria('Lampante olive oil (2%)') == N.PROCESSED_PRODUCT
    assert N.estagio_da_mercadoria('Refined olive-pomace oil (up to 0.3%)') == N.PROCESSED_PRODUCT


def test_azeitona_de_mesa_e_a_cultura():
    """A correção não pode rebaixar quem é matéria-prima de verdade."""
    assert N.estagio_da_mercadoria('Table olives') == N.RAW_CROP


def test_graos_continuam_materia_prima():
    for p in ('Feed barley', 'Durum wheat', 'Breadmaking common wheat', 'Feed maize'):
        assert N.estagio_da_mercadoria(p) == N.RAW_CROP, p


def test_vinho_nao_e_uva():
    assert N.estagio_da_mercadoria('Vino bianco comune') == N.PROCESSED_PRODUCT
    assert N.estagio_da_mercadoria('Mosto concentrato') == N.PROCESSED_PRODUCT


def test_farinha_nao_e_trigo():
    assert N.estagio_da_mercadoria('Farina di frumento tenero') == N.PROCESSED_PRODUCT
    assert N.estagio_da_mercadoria('Semolina') == N.PROCESSED_PRODUCT


def test_campo_vazio_nao_inventa_estagio():
    assert N.estagio_da_mercadoria('') is None
    assert N.estagio_da_mercadoria(None) is None
