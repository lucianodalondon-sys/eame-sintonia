# -*- coding: utf-8 -*-
"""O CONTRATO DE GEOGRAFIA, com mentiras plantadas de propósito.

    python3 -c "import sys;sys.path[:0]=['tests','scripts'];import test_v21_geografia as T;[getattr(T,n)() for n in dir(T) if n.startswith('test_')];print('ok')"

POR QUE ESTES TESTES EXISTEM
-----------------------------
Porque a lei `PROVINCIAL != REGIONAL` já estava escrita — no cabeçalho do próprio
arquivo que a quebrava, e nos 73 registros da fonte, que declaram «boletim
provincial NAO representa a regiao». Estava escrita e não era medida.

    LEI QUE NINGUÉM MEDE É COMENTÁRIO.

Cada teste aqui reproduz um defeito real que chegou a sair no pacote V2.1.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
import v21_normalizar as N  # noqa: E402


def test_rotulo_de_lote_nao_e_geografia():
    """B05/B12 · «TOSCANA-FVG» é pasta do coletor, não geografia do boletim."""
    g = N.geografia('Bollettino di produzione integrata MELO (ERSA Friuli-Venezia Giulia)',
                    'https://difesafitosanitaria.ersa.fvg.it/x',
                    rotulo_de_lote='TOSCANA-FVG')
    assert g['REGION_IDS'] == ['REGION_FRIULI_VENEZIA_GIULIA'], g
    assert 'REGION_TOSCANA' not in g['REGION_IDS'], 'o rotulo de lote vazou para a geografia'
    assert g['GEOGRAPHY_BATCH_LABEL'] == 'TOSCANA-FVG', 'o rotulo tem de ficar registrado como nota'


def test_boletim_da_toscana_nao_vira_friuli():
    g = N.geografia('Bollettino Vite Integrato — Provincia di Grosseto (Regione Toscana)',
                    rotulo_de_lote='TOSCANA-FVG')
    assert 'REGION_FRIULI_VENEZIA_GIULIA' not in g['REGION_IDS'], g


def test_provincia_nunca_sobe_a_regiao():
    """B13/B35 · Grosseto não fala pela Toscana."""
    g = N.geografia('Bollettino Vite Integrato — Provincia di Grosseto (Regione Toscana)')
    assert g['GEOGRAPHY_STATE'] == N.GEO_PROVINCE, g
    assert g['GEOGRAPHIC_SCOPE'] == 'PROVINCIAL', g
    assert g['PROVINCE_IDS'] == ['PROV_GROSSETO'], g
    assert g['REGION_REPRESENTS'] is False, 'um boletim provincial nao pode representar a regiao'


def test_marche_nao_vira_umbria():
    g = N.geografia('Notiziario Agrometeorologico per la provincia di Ancona',
                    'https://meteo.regione.marche.it/x.pdf', rotulo_de_lote='MARCHE-UMBRIA')
    assert g['REGION_IDS'] == ['REGION_MARCHE'], g
    assert 'REGION_UMBRIA' not in g['REGION_IDS'], g


def test_trentino_nao_vira_trentino_alto_adige_sozinho():
    """B06 · «Trentino» no texto não autoriza carimbar a região inteira."""
    g = N.geografia('Bollettino della provincia di Trento')
    assert g['GEOGRAPHY_STATE'] == N.GEO_PROVINCE, g
    assert g['PROVINCE_IDS'] == ['PROV_TRENTO'], g
    assert g['REGION_REPRESENTS'] is False, g


def test_bolzano_e_trento_nao_duplicam_a_regiao():
    """B25 · somar as duas províncias autônomas não pode contar a região duas vezes."""
    a = N.geografia('Bollettino provincia di Bolzano')
    b = N.geografia('Bollettino provincia di Trento')
    assert a['PROVINCE_IDS'] == ['PROV_BOLZANO'] and b['PROVINCE_IDS'] == ['PROV_TRENTO']
    assert a['REGION_REPRESENTS'] is False and b['REGION_REPRESENTS'] is False
    assert a['GEOGRAPHIC_SCOPE'] == 'PROVINCIAL' and b['GEOGRAPHIC_SCOPE'] == 'PROVINCIAL'


def test_regional_de_verdade_continua_regional():
    """A correção não pode rebaixar quem é regional de verdade."""
    g = N.geografia('Catture di Popillia japonica sul territorio della regione Lombardia',
                    'https://fitosanitario.regione.lombardia.it/x')
    assert g['GEOGRAPHY_STATE'] == N.GEO_REGION, g
    assert g['REGION_REPRESENTS'] is True, g
    assert g['GEOGRAPHIC_SCOPE'] == 'REGIONAL', g


def test_sem_evidencia_e_desconhecido_nao_e_palpite():
    """Painel de fornecedor privado: nem host, nem título, nem corpo dizem a região."""
    g = N.geografia('BOLLETTINO AGROMETEOROLOGICO E FITOSANITARIO — COMPARTO SEMINATIVI',
                    'https://dashboard01.green-planet.it/bollettini.php?Id=1',
                    rotulo_de_lote='PIEMONTE')
    assert g['GEOGRAPHY_STATE'] == N.GEO_UNKNOWN, g
    assert g['REGION_IDS'] == [], 'o rotulo de lote PIEMONTE nao pode virar geografia'
    assert g['GEOGRAPHIC_SCOPE'] == 'NAO_SEI', g


def test_areal_nao_representa_a_regiao():
    """GARGANO é recorte dentro da Puglia, e não fala pela Puglia."""
    g = N.geografia('Notiziario Regionale — TERRITORIO GARGANO, bloco AGRUMI',
                    'https://www.agrometeopuglia.it/x.pdf')
    assert g['AREAL_IDS'] == ['AREA_GARGANO'], g
    assert g['GEOGRAPHIC_SCOPE'] == 'AREALE', g
    assert g['REGION_REPRESENTS'] is False, g


def test_multi_regiao_so_com_duas_regioes_nomeadas_no_documento():
    g = N.geografia('Accordo interregionale Veneto e Lombardia')
    assert g['GEOGRAPHY_STATE'] == N.GEO_MULTI, g
    assert sorted(g['REGION_IDS']) == ['REGION_LOMBARDIA', 'REGION_VENETO'], g
    assert g['REGION_REPRESENTS'] is True, g


def test_substring_nao_casa():
    """A lei que matou o TOP-CROSSINGS do V2: «riso» dentro de «comparison»."""
    g = N.geografia('comparison of marchetti data')
    assert g['REGION_IDS'] == [], f'casou por substring: {g}'
    assert g['PROVINCE_IDS'] == [], f'casou por substring: {g}'


def test_host_de_fornecedor_nao_entra_na_tabela():
    """Saber de cabeça não é evidência no arquivo."""
    assert 'dashboard01.green-planet.it' not in N.HOST_GEO


def test_sinonimos_da_mesma_provincia_sao_um_id():
    """Defeito introduzido pela própria correção: «Pesaro», «Urbino» e «Pesaro e
    Urbino» chegaram a sair como TRÊS províncias, inflando a cobertura de um
    cruzamento. Três nomes da mesma coisa são um ID, ou a contagem mente."""
    assert N.province_ids('per la provincia di Pesaro e Urbino') == ['PROV_PESARO_E_URBINO']
    assert N.province_ids('provincia di Pesaro') == ['PROV_PESARO_E_URBINO']
    assert N.province_ids('provincia di Urbino') == ['PROV_PESARO_E_URBINO']
    g = N.geografia('Notiziario per le province di Pesaro e Urbino')
    assert len(g['PROVINCE_IDS']) == 1, g


def test_cobertura_nao_conta_a_mesma_provincia_duas_vezes():
    g = N.geografia('Bollettino FORLI-CESENA, RAVENNA E RIMINI')
    assert len(g['PROVINCE_IDS']) == len(set(g['PROVINCE_IDS'])), g
    assert 'PROV_FORLI_CESENA' in g['PROVINCE_IDS'], g
