#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ÚLTIMAS CAMADAS DO PACOTE — oportunidade, futuro, janela, notícia, evento, fonte,
pessoa, acervo, mercado e as RELAÇÕES.

    python3 scripts/pacote_camadas2.py

A camada de RELAÇÕES é a que o Design mais vai usar, e a regra dela é dura:
ela guarda **só IDs**. Duplicar o registro dentro do link é como o mesmo fato passa a ter
duas versões que divergem em silêncio.
"""
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pacote_normalizar import (git_json, local_json, grava, env, novo_id,  # noqa: E402
                               DR, ROOT)

REAL, DERIV, FACT, SYNTH, INTERNAL = ('REAL_SOURCE', 'REAL_DERIVED', 'REAL_FACT',
                                      'SYNTHETIC_DEMO', 'INTERNAL_DATA_REQUIRED')


# ══════════════════════════════════════════════════════════ FONTES
def camada_fontes():
    probe = git_json('data/samples/IT-FONTES/ITALY-SOURCE-PROBE.json')
    fixas = [
        ('IT-SRC-MINISTERO', 'Ministero della Salute — Banca dati prodotti fitosanitari',
         'OFFICIAL', 'registro nacional de produto e rotulo autorizado', 'IT',
         'https://www.salute.gov.it/', 'continua', '2026-08-24 (PROD_FTS_6)', 'GREEN',
         'o rotulo e PDF; a coluna de epoca de aplicacao nao foi extraida'),
        ('IT-SRC-CELLAR', 'EU Publications Office — CELLAR / SPARQL',
         'OFFICIAL', 'ato juridico da UE, aprovacao de substancia ativa', 'EU',
         'https://publications.europa.eu/webapi/rdf/sparql', 'continua', '2026-07-28',
         'GREEN', 'so acha ato cujo titulo nomeia a substancia'),
        ('IT-SRC-AGRIFOOD', 'European Commission — Agri-food Data Portal',
         'MARKET', 'preco por praca, producao, comercio', 'EU/IT',
         'https://www.ec.europa.eu/agrifood/api/', 'semanal', '2026-08-23', 'GREEN',
         'responde 302; sem -L devolve pagina de redirect. Preco vem como TEXTO.'),
        ('IT-SRC-GIRE', 'GIRE — Gruppo Italiano Resistenza Erbicidi (CNR-IPSP)',
         'RESEARCH', 'resistencia a herbicida confirmada por especie', 'IT',
         'http://gire.mlib.cnr.it', 'irregular', '2025-06', 'GREEN',
         'o host com TLS (gire.ipsp.cnr.it) tem certificado expirado; use o espelho'),
        ('IT-SRC-OPENALEX', 'OpenAlex', 'RESEARCH', 'obra cientifica e autoria', 'GLOBAL',
         'https://api.openalex.org', 'continua', '2026-07-30', 'GREEN',
         'afiliacao e do AUTOR, nao do estudo. 429 depende do IP de saida.'),
        ('IT-SRC-META', 'Meta Ads Library', 'COMPANY',
         'anuncio pago que ALCANCOU o pais', 'IT/ES/FR',
         'https://www.facebook.com/ads/library/', 'continua', '2026-08-31', 'PARTIAL',
         'so abre em navegador com janela grafica. Nao publica gasto nem alcance.'),
        ('IT-SRC-YOUTUBE', 'YouTube', 'PEOPLE',
         'video publico, transcricao e comentario', 'GLOBAL',
         'https://www.youtube.com', 'continua', '2026-08-28', 'GREEN',
         'comentario devolve tempo RELATIVO, nao data. Coleta e paga (Apify).'),
        ('IT-SRC-MODENA', 'Consorzio Fitosanitario Provinciale di Modena',
         'FIELD', 'boletim de producao integrada e alerta fitossanitario', 'Emilia-Romagna',
         'https://www.fitosanitario.mo.it', 'semanal', '2026-08-18', 'GREEN',
         'e UMA provincia. Nao representa a regiao nem o pais.'),
        ('IT-SRC-PIEMONTE', 'Regione Piemonte — Settore Fitosanitario',
         'OFFICIAL', 'lotta obbligatoria, zonas, substancias admitidas', 'Piemonte',
         'https://www.regione.piemonte.it', 'anual + boletins', '2026-03-16', 'GREEN',
         'o ato e PDF'),
        ('IT-SRC-ISTAT', 'ISTAT — esploradati (SDMX)', 'OFFICIAL',
         'superficie e producao por regiao', 'IT', 'https://esploradati.istat.it',
         'anual', '2024', 'GREEN', 'ano de referencia atrasa em relacao a safra corrente'),
        ('IT-SRC-EUROSTAT', 'Eurostat', 'OFFICIAL', 'area, rendimento, indice de preco',
         'EU', 'https://ec.europa.eu/eurostat', 'anual/mensal', '2024', 'GREEN',
         'rendimento so por pais, nao por NUTS2'),
    ]
    fontes = []
    for sid, nome, tipo, papel, geo, url, freq, ultimo, estado, lim in fixas:
        fontes.append(OrderedDict([
            ('ID', sid), ('SOURCE_ID', sid), ('NAME', nome), ('TYPE', tipo), ('ROLE', papel),
            ('COUNTRY', 'IT' if geo.startswith('IT') else geo), ('GEOGRAPHY', geo),
            ('URL', url), ('FREQUENCY', freq), ('LATEST_OBSERVATION', ultimo),
            ('ACCESS_STATUS', estado), ('LIMITATIONS', lim), ('PROVENANCE', REAL)]))
    if probe:
        for s in probe.get('SOURCES', []):
            fontes.append(OrderedDict([
                ('ID', novo_id('IT-SRC-PROBE')), ('NAME', s.get('NAME')),
                ('TYPE', s.get('CLASS')), ('ROLE', s.get('WHAT_IT_MEASURES')),
                ('COUNTRY', 'IT'), ('GEOGRAPHY', 'IT'),
                ('URL', s.get('URL')), ('FREQUENCY', s.get('FRESHNESS')),
                ('LATEST_OBSERVATION', str(s.get('DATES_SEEN'))[:60]),
                ('ACCESS_STATUS', s.get('ACCESS_STATUS') or s.get('STATUS')),
                ('LIMITATIONS', 'sondada em 2026-08-30; estado pode ter mudado'),
                ('PROVENANCE', REAL)]))
    grava('SOURCES', 'sources.json', OrderedDict(list(env(
        'SOURCES', ['data/samples/IT-FONTES/ITALY-SOURCE-PROBE.json', 'registro manual'],
        REAL, 'HTTP 200 NAO E FONTE VIVA. ACCESS_STATUS e o estado medido, nao promessa.'
    ).items()) + [('COUNT', len(fontes)), ('SOURCES', fontes)]))
    return fontes


# ══════════════════════════════════════════════════════════ JANELAS
def camada_janelas():
    lotta = git_json('data/samples/IT-T3-LOTTA/IT-lotta-obbligatoria-flavescenza-2026.json')
    regioes = local_json('IT-CAMPO-ATUAL/IT-FLAVESCENZA-REGIOES-V1.json')
    sinais = local_json('IT-CAMPO-ATUAL/IT-SINAIS-CAMPO-SETEMBRO-2026.json')
    jan = []
    if regioes:
        for r in regioes['REGIOES']:
            jan.append(OrderedDict([
                ('ID', novo_id('IT-WIN')), ('CROP', 'VITE'),
                ('REGION', r.get('REGIAO')),
                ('ISSUE', 'Flavescenza dorata (vetor Scaphoideus titanus)'),
                ('EXPECTED_CYCLE', 'vetor com uma geracao anual; nascimento fim de abril a '
                                   'inicio de junho, escalonado'),
                ('OBSERVED_STAGE', 'NAO SEI — nenhum boletim de fenologia lido para 2026-09'),
                ('FIELD_REPORTED_STAGE', 'NAO SEI'),
                ('REGULATORY_WINDOW', r.get('JANELAS_2026') or 'ver ato da regiao'),
                ('REGULATORY_ACT', '%s %s' % (r.get('ATO'), r.get('DATA') or '')),
                ('REGULATORY_ACT_STATE', r.get('ESTADO')),
                ('MONITORING_WINDOW', 'aberta — inicio de agosto a fim de setembro, '
                                      'reconhecimento de sintoma foliar e captura de adulto'),
                ('APPLICATION_WINDOW_2026', 'FECHADA — as janelas obrigatorias terminaram em junho'),
                ('NEXT_IMPORTANT_WINDOW', '2027 — a obrigacao recorre por norma europeia; '
                                          'as DATAS sao fixadas a cada ano pelo monitoramento'),
                ('PREPARATION_WINDOW', 'ate 2027-05-31, quando historicamente sai o ato'),
                ('ADAMA_PRODUCTS_NOTE', '6 registros ADAMA nomeiam Scaphoideus titanus no '
                                        'rotulo (tau-fluvalinate); 4 mais trazem «cicaline» '
                                        '(lambda-cialotrina)'),
                ('COVERAGE_STATE', 'REGULATORY_READ_FIELD_NOT_READ'),
                ('SOURCE_ID', 'IT-SRC-PIEMONTE' if r.get('REGIAO') == 'Piemonte'
                 else 'IT-SRC-REGIONAL'),
                ('PROVENANCE', FACT)]))
    if sinais:
        for s in sinais['SINAIS']:
            jan.append(OrderedDict([
                ('ID', novo_id('IT-WIN')), ('CROP', s.get('CROP')),
                ('REGION', s.get('REGIAO')), ('ISSUE', s.get('ALVO')),
                ('EXPECTED_CYCLE', 'NAO SEI'),
                ('OBSERVED_STAGE', s.get('ESTADO')),
                ('FIELD_REPORTED_STAGE', '; '.join(s.get('O_QUE_A_FONTE_DIZ') or [])[:600]),
                ('OBSERVATION_DATE', s.get('DATA_DA_EVIDENCIA')),
                ('FACT_DATE', s.get('DATA_DO_FATO')),
                ('MONITORING_WINDOW', 'corrente — a fonte publica semanalmente'),
                ('NEXT_IMPORTANT_WINDOW', 'NAO SEI'),
                ('COVERAGE_STATE', 'FIELD_READ_ONE_PROVINCE_ONLY'),
                ('WHAT_IT_DOES_NOT_PROVE', s.get('O_QUE_ISTO_NAO_PROVA')),
                ('SOURCE_ID', 'IT-SRC-MODENA'), ('PROVENANCE', REAL)]))
    grava('CROP-WINDOWS', 'crop-windows.json', OrderedDict(list(env(
        'CROP_WINDOWS',
        ['data/samples/IT-CAMPO-ATUAL/', 'data/samples/IT-T3-LOTTA/'], FACT,
        'EXPECTED != OBSERVED. LABEL WINDOW != CURRENT CROP STAGE. '
        'BUSINESS PREPARATION != AGRONOMIC WINDOW.').items()) + [
        ('COUNT', len(jan)),
        ('BIG_GAP', 'nenhuma janela de fenologia CORRENTE foi lida para setembro de 2026. '
                    'O que existe e regulatorio (datas do ato) e sinal pontual de UMA '
                    'provincia. Isto e cobertura, nao ausencia de campo.'),
        ('WINDOWS', jan)]))
    return jan


# ══════════════════════════════════════════════════════════ OPORTUNIDADE
def camada_oportunidades():
    hero = git_json('data/samples/IT-CASOS/ITALY-HERO-CASES-V1.json')
    ops = []
    if hero:
        for c in hero['CASES']:
            ops.append(OrderedDict([
                ('ID', novo_id('IT-OPP')),
                ('LEGACY_CASE_ID', c.get('CASE_ID')),
                ('TITLE', '%s x %s' % (c.get('CROP'), c.get('ISSUE'))),
                ('CROP', c.get('CROP')), ('REGION', c.get('REGION')),
                ('ISSUE', c.get('ISSUE')),
                ('ISSUE_TYPE', tipo_issue(c.get('ISSUE'))),
                ('CASE_LABEL', hero.get('CASES') and c.get('CASE_LABEL')
                 or 'CONVERGENCIA QUE MERECE INVESTIGACAO'),
                ('FORBIDDEN_LABEL', 'nao chamar de "oportunidade Italia" nem de '
                                    '"oportunidade comercial"'),
                ('WHAT_IS_HAPPENING', json.dumps(c.get('SIGNAL'), ensure_ascii=False)[:900]),
                ('WHY_IT_MATTERS', json.dumps(c.get('REGULATORY_RESPONSE') or
                                              c.get('SCALE'), ensure_ascii=False)[:900]),
                ('CURRENT_EVIDENCE', c.get('FACTS') or []),
                ('ADAMA_PRODUCTS', (c.get('ADAMA_REGISTERED_RESPONSE') or {})
                 .get('PRODUCT_NAMES') or []),
                ('ADAMA_ACTIVE_SUBSTANCE', (c.get('ADAMA_REGISTERED_RESPONSE') or {})
                 .get('ACTIVE_SUBSTANCE')),
                ('WINDOW', {'APPLICATION': (c.get('APPLICATION_WINDOW') or {}).get('STATE'),
                            'MONITORING': (c.get('MONITORING_WINDOW') or {}).get('STATE'),
                            'NEXT_CYCLE': (c.get('NEXT_CYCLE_WINDOW') or {}).get('STATE')}),
                ('MARKET_CONTEXT', 'ver 01-DESIGN-READY/MARKET-PULSE/'),
                ('COMPETITOR_CONTEXT', 'ver 01-DESIGN-READY/COMPETITOR-WATCH/'),
                ('SCIENCE_CONTEXT', json.dumps(c.get('SCIENCE'), ensure_ascii=False)[:400]),
                ('FIELD_VOICES', 'ver 01-DESIGN-READY/VOCI-DAL-CAMPO/'),
                ('WHAT_WE_KNOW', c.get('FACTS') or []),
                ('WHAT_WE_DO_NOT_KNOW', c.get('UNKNOWNS') or []),
                ('INTERPRETATIONS', c.get('INTERPRETATIONS') or []),
                ('SOURCE_IDS', ['IT-SRC-MINISTERO', 'IT-SRC-PIEMONTE', 'IT-SRC-OPENALEX']),
                ('PROVENANCE', DERIV)]))
    grava('OPPORTUNITIES', 'opportunities.json', OrderedDict(list(env(
        'OPPORTUNITIES', 'data/samples/IT-CASOS/ITALY-HERO-CASES-V1.json', DERIV,
        'O proprio artefato de origem se recusa a chamar isto de «oportunidade»: o rotulo '
        'e CONVERGENCIA QUE MERECE INVESTIGACAO. Mantido.').items()) + [
        ('COUNT', len(ops)), ('OPPORTUNITIES', ops)]))
    return ops


def tipo_issue(txt):
    t = (txt or '').lower()
    if 'flavesc' in t or 'fitoplasma' in t:
        return 'FITOPLASMA'
    if 'piralide' in t or 'diabrotica' in t or 'insett' in t:
        return 'PEST'
    if 'fusari' in t or 'septor' in t or 'peronospor' in t:
        return 'DISEASE'
    if 'infestant' in t or 'daninh' in t or 'amaranth' in t:
        return 'WEED'
    return 'NAO SEI'


# ══════════════════════════════════════════════════════════ FUTURO
def camada_futuro():
    rad = git_json('data/samples/ITALY-RADAR-DO-FUTURO-V1.json')
    eu = local_json('IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V2.json')
    sig = []
    if rad:
        for t in rad['THEMES']:
            sig.append(OrderedDict([
                ('ID', novo_id('IT-FUT')), ('LEGACY_ID', t.get('THEME_ID')),
                ('WHO_IS_TALKING', 'ciencia italiana indexada no OpenAlex'),
                ('WHAT_CHANGED', t.get('THEME_TYPE')),
                ('CROP', t.get('CROP')), ('ISSUE', t.get('ISSUE')),
                ('REGION', t.get('REGION')),
                ('WHY_WATCH', t.get('WHAT_WOULD_PROMOTE_TO_RADAR')),
                ('HOW_SINTONIA_GOT_HERE', (t.get('SCIENCE_SIGNAL') or {}).get('EVIDENCIA')),
                ('OBSERVED_FACTS', t.get('WHAT_WE_KNOW') or []),
                ('SINTONIA_INTERPRETATION', t.get('MATURITY_STATE')),
                ('UNKNOWN', t.get('WHAT_WE_DONT_KNOW') or []),
                ('NEXT_WINDOW', t.get('HORIZON')),
                ('PORTFOLIO_CONNECTION', (t.get('PORTFOLIO_SIGNAL') or {}).get('EVIDENCIA')),
                ('WHAT_WOULD_MAKE_IT_AN_OPPORTUNITY', t.get('WHAT_WOULD_PROMOTE_TO_RADAR')),
                ('PROMOTED_TO_RADAR', False),
                ('SOURCE_IDS', ['IT-SRC-OPENALEX', 'IT-SRC-MINISTERO']),
                ('PROVENANCE', DERIV)]))
    # sinal novo: a fronteira europeia
    if eu:
        proximos = []
        for a in eu['ATOS']:
            for s in (a.get('SUBSTANCES') or []):
                d = str(s.get('new_expiry_date') or '')
                if any(y in d for y in ('2026', '2027')):
                    proximos.append('%s = %s (%s)' % (s.get('name'), d, a['CELEX']))
        sig.append(OrderedDict([
            ('ID', novo_id('IT-FUT')),
            ('WHO_IS_TALKING', 'Comissao Europeia, por ato juridico publicado'),
            ('WHAT_CHANGED', 'a aprovacao europeia de varias substancias ativas do '
                             'portfolio italiano da ADAMA expira antes de 2028, e varios '
                             'atos declaram a renovacao ainda em avaliacao'),
            ('CROP', 'TRANSVERSAL'), ('ISSUE', 'REGULATORIO'), ('REGION', 'UE'),
            ('WHY_WATCH', 'o vencimento NACIONAL de parte do portfolio coincide com a '
                          'fronteira europeia da substancia. Registro nacional nao '
                          'sobrevive a aprovacao UE vencida.'),
            ('HOW_SINTONIA_GOT_HERE', '15 atos lidos na integra pela rota CELLAR/SPARQL e '
                                      'cada um relido por um refutador independente'),
            ('OBSERVED_FACTS', proximos[:25]),
            ('SINTONIA_INTERPRETATION', 'EMERGING_THEME — merece um analista abrir, nao e '
                                        'previsao de retirada'),
            ('UNKNOWN', ['o RESULTADO de cada renovacao — o ato nao decide, so estende',
                         'se havera nova extensao antes do vencimento',
                         'se a decisao mantem o uso italiano de cada produto']),
            ('NEXT_WINDOW', '2027-01-31 e a data mais proxima (tau-fluvalinate, bupirimate)'),
            ('PORTFOLIO_CONNECTION', '7 produtos ADAMA com tau-fluvalinate, 5 com bupirimate'),
            ('WHAT_WOULD_MAKE_IT_AN_OPPORTUNITY', 'nao e oportunidade: e exposicao. '
                                                  'O que a destravaria e um ato de decisao.'),
            ('PROMOTED_TO_RADAR', False),
            ('SOURCE_IDS', ['IT-SRC-CELLAR', 'IT-SRC-MINISTERO']),
            ('PROVENANCE', FACT)]))
    grava('FUTURE-RADAR', 'future-signals.json', OrderedDict(list(env(
        'FUTURE_SIGNALS',
        ['data/samples/ITALY-RADAR-DO-FUTURO-V1.json',
         'data/samples/IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V2.json'], DERIV,
        'FATO e INTERPRETACAO ficam em campos separados, e nenhum sinal esta promovido.'
    ).items()) + [('COUNT', len(sig)), ('SIGNALS', sig)]))
    return sig


if __name__ == '__main__':
    os.makedirs(DR, exist_ok=True)
    print('CAMADA FONTES'); camada_fontes()
    print('CAMADA JANELAS'); camada_janelas()
    print('CAMADA OPORTUNIDADES'); camada_oportunidades()
    print('CAMADA FUTURO'); camada_futuro()
    print('\nok')
