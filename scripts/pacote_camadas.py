#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMADAS RESTANTES DO PACOTE — vozes, competidor, ciência, oportunidade, futuro,
janelas, notícia, evento, fonte, pessoa, mercado e relações.

    python3 scripts/pacote_camadas.py

Reusa `pacote_normalizar` como biblioteca: `git_json`, `local_json`, `grava`, `env`,
`novo_id`. Um arquivo só ficaria longo demais para ser lido; dois ficam legíveis.
"""
import json
import os
import sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pacote_normalizar import (git_json, local_json, grava, env, novo_id,  # noqa: E402
                               camada_adama, DR, ROOT, SAMPLES)


# ══════════════════════════════════════════════════════════ VOCI DAL CAMPO
def camada_vozes():
    med = local_json('SENSOR-PILOT/MEDICAO.json')
    if not med:
        print('  !! sem MEDICAO'); return []
    V = {v.get('EXTERNAL_ID'): v for v in med['VIDEOS_ITEMS']}
    porurl = {v.get('SOURCE_URL'): v for v in med['VIDEOS_ITEMS']}
    it_com = [c for c in med['COMMENTS_ITEMS'] if str(c.get('CASE_ID', '')).startswith('IT-')]
    fora = []
    for c in it_com:
        if c.get('SPEECH_TYPE') not in ('FIRST_PERSON_FIELD_REPORT', 'TECHNICAL_REPLY'):
            continue
        v = V.get(c.get('VIDEO_ID')) or porurl.get(c.get('SOURCE_URL')) or {}
        prova = ('um comentarista escreveu isto sob este video'
                 if c['SPEECH_TYPE'] == 'FIRST_PERSON_FIELD_REPORT'
                 else 'alguem respondeu tecnicamente sob este video')
        fora.append(OrderedDict([
            ('ID', novo_id('IT-VOICE')),
            ('KIND', c.get('SPEECH_TYPE')),
            ('PERSON', c.get('COMMENTER_NAME')),
            ('PERSON_IDENTITY_STATE', 'NAO_ATRIBUIVEL — handle publico pseudonimizado'),
            ('ROLE', 'NAO SEI'), ('ORGANIZATION', 'NAO SEI'),
            ('PLATFORM', 'YOUTUBE'),
            ('CHANNEL', c.get('SOURCE_ENTITY') or v.get('CHANNEL')),
            ('CONTENT_TITLE', v.get('TITLE')),
            ('DATE', 'NAO SEI'),
            ('DATE_RELATIVE', c.get('DATE_RELATIVE')),
            ('DATE_NOTE', 'a rota devolve tempo RELATIVO. Converter inventaria precisao.'),
            ('CROP', c.get('CROP')), ('ISSUE', c.get('ISSUE')),
            ('CASE_ID', c.get('CASE_ID')),
            ('REGION', 'NAO SEI' if c.get('REGION_OF_FACT') in (None, 'NOT_KNOWN')
             else c.get('REGION_OF_FACT')),
            ('COUNTRY_OF_FACT', c.get('COUNTRY_OF_FACT')),
            ('TEXT_ORIGINAL', (c.get('COMMENT_TEXT_RAW') or '')[:900]),
            ('WHAT_IT_PROVES', prova),
            ('WHAT_IT_DOES_NOT_PROVE',
             'nao prova que quem escreveu e produtor; nao prova ocorrencia no campo; '
             'nao prova falha nem eficacia de produto; nao prova incidencia regional'),
            ('SOURCE_URL', c.get('SOURCE_URL')),
            ('SOURCE_ID', 'IT-SRC-YOUTUBE'),
            ('PROVENANCE', 'REAL_SOURCE'),
        ]))
    grava('VOCI-DAL-CAMPO', 'field-voices.json', OrderedDict(list(env(
        'FIELD_VOICES', 'data/samples/SENSOR-PILOT/MEDICAO.json', 'REAL_SOURCE',
        'O denominador vai junto: a raridade E o achado.').items()) + [
        ('LAYER_LAW', 'COMENTARIO E PLATEIA DAQUELE CANAL, NUNCA PRODUTOR'),
        ('COUNT', len(fora)),
        ('DENOMINATOR', {'IT_COMMENTS_READ': len(it_com),
                         'ALL_COMMENTS_READ': len(med['COMMENTS_ITEMS'])}),
        ('NEVER', 'nunca criar citacao para pessoa real. TEXT_ORIGINAL e literal.'),
        ('VOICES', fora)]))

    canais, vistos = [], set()
    for v in med['VIDEOS_ITEMS']:
        if not str(v.get('CASE_ID', '')).startswith('IT-'):
            continue
        if v.get('CONTENT_TYPE') in ('NOISE', 'NOT_ENOUGH_TEXT'):
            continue
        ch = v.get('CHANNEL')
        if not ch or ch in vistos:
            continue
        vistos.add(ch)
        canais.append(OrderedDict([
            ('ID', novo_id('IT-CHAN')), ('CHANNEL', ch),
            ('CHANNEL_URL', v.get('CHANNEL_URL')),
            ('IDENTITY_STATE', v.get('CHANNEL_IDENTITY_STATE')),
            ('CONTENT_TYPE_EXAMPLE', v.get('CONTENT_TYPE')),
            ('EXAMPLE_TITLE', v.get('TITLE')), ('EXAMPLE_URL', v.get('SOURCE_URL')),
            ('EXAMPLE_PUBLISHED_AT', v.get('PUBLISHED_AT')),
            ('VIEWS', v.get('VIEWS')), ('CASE_ID', v.get('CASE_ID')),
            ('PROVENANCE', 'REAL_SOURCE')]))
    grava('VOCI-DAL-CAMPO', 'italian-channels.json', OrderedDict(list(env(
        'ITALIAN_TECHNICAL_CHANNELS', 'data/samples/SENSOR-PILOT/MEDICAO.json',
        'REAL_SOURCE').items()) + [('COUNT', len(canais)), ('CHANNELS', canais)]))
    return fora


# ══════════════════════════════════════════════════════════ COMPETITOR
MARCAS = ['bayer', 'syngenta', 'corteva', 'basf', 'fmc', 'upl', 'sipcam',
          'certis', 'gowan', 'nufarm', 'belchim', 'sumitomo']


def camada_competidor():
    meta = git_json('data/samples/META-EAME/META-ADS-ENTITIES-EAME-V1.json')
    med = local_json('SENSOR-PILOT/MEDICAO.json')
    ativ, comp, prods = [], {}, {}
    if meta:
        for _k, a in meta['entities'].items():
            if 'IT' not in (a.get('countries_reached_observed') or []):
                continue
            r = a.get('reading', {})
            pv = [x['product_name'] for x in (r.get('product_candidates') or [])
                  if x.get('state') == 'PROVED']
            ativ.append(OrderedDict([
                ('ID', novo_id('IT-COMP-ACT')),
                ('ACTIVITY_TYPE', 'PAID'), ('PLATFORM', 'META_ADS_LIBRARY'),
                ('COMPANY', a.get('company')), ('PAGE', a.get('page_name_resolved')),
                ('PAGE_ID', a.get('page_id')), ('COUNTRY_REACHED', 'IT'),
                ('COUNTRY_SEMANTICS', 'AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY'),
                ('START_DATE', a.get('start_date')), ('END_DATE', a.get('end_date')),
                ('ACTIVE_STATUS', a.get('active_status')),
                ('MEDIA_TYPE', a.get('media_type')),
                ('PRODUCTS_PROVED', pv),
                ('CROP_TERMS', [(x.get('canonical') or x.get('term_matched'))
                                for x in (r.get('crop') or []) if isinstance(x, dict)]),
                ('ISSUE_TERMS', [(x.get('canonical') or x.get('term_matched'))
                                 for x in (r.get('issue') or []) if isinstance(x, dict)]),
                ('CREATIVE_TEXT', (a.get('creative_text') or '')[:700]),
                ('AD_URL', a.get('ad_snapshot_url')),
                ('SOURCE_ID', 'IT-SRC-META'), ('PROVENANCE', 'REAL_SOURCE')]))
            co = a.get('company')
            comp.setdefault(co, {'ads': 0, 'pages': set(), 'products': set(), 'organic': 0})
            comp[co]['ads'] += 1
            comp[co]['pages'].add(a.get('page_name_resolved'))
            for x in pv:
                comp[co]['products'].add(x)
                prods.setdefault(x, {'company': co, 'ads': 0})
                prods[x]['ads'] += 1
    if med:
        for v in med['VIDEOS_ITEMS']:
            ch = (v.get('CHANNEL') or '').lower()
            m = next((x for x in MARCAS if x in ch), None)
            if not m:
                continue
            nome = m.upper()
            ativ.append(OrderedDict([
                ('ID', novo_id('IT-COMP-ACT')),
                ('ACTIVITY_TYPE', 'ORGANIC_VIDEO'), ('PLATFORM', 'YOUTUBE'),
                ('COMPANY', nome), ('CHANNEL', v.get('CHANNEL')),
                ('TITLE', v.get('TITLE')), ('PUBLISHED_AT', v.get('PUBLISHED_AT')),
                ('VIEWS', v.get('VIEWS')), ('COMMENTS_COUNT', v.get('COMMENTS_COUNT')),
                ('DESCRIPTION', (v.get('DESCRIPTION') or '')[:500]),
                ('URL', v.get('SOURCE_URL')), ('CASE_ID', v.get('CASE_ID')),
                ('SOURCE_ID', 'IT-SRC-YOUTUBE'), ('PROVENANCE', 'REAL_SOURCE')]))
            comp.setdefault(nome, {'ads': 0, 'pages': set(), 'products': set(), 'organic': 0})
            comp[nome]['organic'] += 1
    grava('COMPETITOR-WATCH', 'competitor-activities.json', OrderedDict(list(env(
        'COMPETITOR_ACTIVITY',
        ['data/samples/META-EAME/META-ADS-ENTITIES-EAME-V1.json',
         'data/samples/SENSOR-PILOT/MEDICAO.json'], 'REAL_SOURCE',
        'PAID e ORGANIC_VIDEO sao tipos SEPARADOS e nunca somados. A Meta Ads Library '
        'nao e escuta de Facebook.').items()) + [
        ('COUNT', len(ativ)),
        ('BY_TYPE', {'PAID': sum(1 for a in ativ if a['ACTIVITY_TYPE'] == 'PAID'),
                     'ORGANIC_VIDEO': sum(1 for a in ativ
                                          if a['ACTIVITY_TYPE'] == 'ORGANIC_VIDEO')}),
        ('NEVER_CLAIM', ['gasto', 'share', 'sucesso de campanha', 'alcance real',
                         'que o anuncio foi DIRIGIDO a Italia']),
        ('ACTIVITIES', ativ)]))
    empresas = [OrderedDict([('ID', novo_id('IT-COMP')), ('COMPANY', k),
                             ('PAID_ADS_REACHING_IT', v['ads']),
                             ('ORGANIC_VIDEOS_IN_CORPUS', v['organic']),
                             ('PAGES', sorted(x for x in v['pages'] if x)),
                             ('PRODUCTS_PROVED', sorted(v['products'])),
                             ('PROVENANCE', 'REAL_DERIVED')])
                for k, v in sorted(comp.items(), key=lambda kv: -kv[1]['ads'])]
    grava('COMPETITOR-WATCH', 'competitor-companies.json', OrderedDict(list(env(
        'COMPETITOR_COMPANIES', 'derivado de competitor-activities.json',
        'REAL_DERIVED').items()) + [('COUNT', len(empresas)), ('COMPANIES', empresas)]))
    pl = [OrderedDict([('ID', novo_id('IT-COMP-PRD')), ('PRODUCT', k),
                       ('COMPANY', v['company']), ('ADS_REACHING_IT', v['ads']),
                       ('PROOF', 'MARCA_REGISTRADA_NO_TEXTO do anuncio'),
                       ('PROVENANCE', 'REAL_SOURCE')])
          for k, v in sorted(prods.items(), key=lambda kv: -kv[1]['ads'])]
    grava('COMPETITOR-WATCH', 'competitor-products.json', OrderedDict(list(env(
        'COMPETITOR_PRODUCTS', 'derivado de competitor-activities.json',
        'REAL_SOURCE').items()) + [('COUNT', len(pl)), ('PRODUCTS', pl)]))
    return ativ


# ══════════════════════════════════════════════════════════ CIENCIA
def camada_ciencia():
    uni = local_json('IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json')
    gire = local_json('IT-CIENCIA/IT-GIRE-RESISTENCIA-V2.json')
    corpus = local_json('RESEARCHER-CORPUS-EAME-V1.json')
    pesq, temas, regs = [], [], []
    if uni:
        for nome, r in (uni.get('RECORTES') or {}).items():
            temas.append(OrderedDict([
                ('ID', novo_id('IT-THEME')), ('THEME', nome), ('QUERY', r.get('QUERY')),
                ('WORKS', r.get('WORKS_TRAVERSED')),
                ('AUTHORS_IT', r.get('AUTHORS_WITH_IT_AFFILIATION')),
                ('AUTHORS_WITH_ORCID', r.get('AUTHORS_WITH_ORCID')),
                ('AUTHORS_ACTIVE_SINCE_2024', r.get('AUTHORS_ACTIVE_SINCE_2024')),
                ('INSTITUTIONS_TOP', r.get('INSTITUTIONS_TOP')),
                ('SOURCE_ID', 'IT-SRC-OPENALEX'), ('PROVENANCE', 'REAL_SOURCE')]))
            for p in (r.get('UNIVERSE') or [])[:12]:
                pesq.append(OrderedDict([
                    ('ID', novo_id('IT-PER')), ('CATEGORY', 'RESEARCHER'),
                    ('PERSON', p.get('PERSON')), ('ORCID', p.get('ORCID')),
                    ('OPENALEX_ID', p.get('OPENALEX_ID')),
                    ('INSTITUTIONS', p.get('INSTITUTIONS')),
                    ('THEME', nome), ('WORKS_IN_SCOPE', p.get('WORKS_IN_SCOPE')),
                    ('LAST_ACTIVITY', p.get('LAST_ACTIVITY')),
                    ('IDENTITY_STATUS', p.get('IDENTITY_STATUS')),
                    ('ROLE', p.get('ROLE')),
                    ('FACT_REGION', p.get('FACT_REGION')),
                    ('SOURCE_ID', 'IT-SRC-OPENALEX'), ('PROVENANCE', 'REAL_SOURCE')]))
    if corpus:
        for m in corpus['MATERIALS']:
            if m.get('COUNTRY_OF_FACT') != 'IT':
                continue
            regs.append(OrderedDict([
                ('ID', novo_id('IT-SCI')), ('TITLE', m.get('TITLE')),
                ('DOI', m.get('DOI')), ('AUTHOR', m.get('NAME')),
                ('ORCID', m.get('ORCID')), ('INSTITUTION', m.get('INSTITUTION')),
                ('PUBLISHED_AT', m.get('PUBLISHED_AT')), ('VENUE', m.get('VENUE')),
                ('MATERIAL_TYPE', m.get('MATERIAL_TYPE')),
                ('MATERIAL_ROLE', m.get('MATERIAL_ROLE')),
                ('CROP', m.get('QUERY_CROP')), ('ISSUE', m.get('QUERY_ISSUE')),
                ('COUNTRY_OF_FACT', 'IT'),
                ('SOURCE_URL', m.get('SOURCE_URL')),
                ('SOURCE_ID', 'IT-SRC-OPENALEX'), ('PROVENANCE', 'REAL_SOURCE')]))
    grava('SCIENCE', 'researchers.json', OrderedDict(list(env(
        'RESEARCHERS', 'data/samples/IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json',
        'REAL_SOURCE',
        'FACT_REGION e sempre NAO SEI: a afiliacao e do AUTOR, nao do estudo.').items()) + [
        ('COUNT', len(pesq)), ('RESEARCHERS', pesq)]))
    grava('SCIENCE', 'research-themes.json', OrderedDict(list(env(
        'RESEARCH_THEMES', 'data/samples/IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json',
        'REAL_SOURCE').items()) + [('COUNT', len(temas)), ('THEMES', temas)]))
    grava('SCIENCE', 'scientific-records.json', OrderedDict(list(env(
        'SCIENTIFIC_RECORDS', 'data/samples/RESEARCHER-CORPUS-EAME-V1.json',
        'REAL_SOURCE',
        'so os materiais cujo TEXTO nomeia a Italia — COUNTRY_OF_FACT=IT.').items()) + [
        ('COUNT', len(regs)), ('RECORDS', regs)]))
    res = []
    if gire:
        for l in gire['LINHAS']:
            res.append(OrderedDict([
                ('ID', novo_id('IT-RES')), ('SPECIES', l.get('ESPECIE')),
                ('SPECIES_IT', l.get('ESPECIE_COMUM_IT')),
                ('FAMILY', l.get('FAMILIA')), ('MECHANISM', l.get('MECANISMO')),
                ('CROP_DECLARED', l.get('CULTURA_DECLARADA')),
                ('FIRST_CASE_YEAR', l.get('PRIMEIRO_CASO_ANO')),
                ('REGIONS', l.get('REGIOES')),
                ('MULTIPLE_RESISTANCE', l.get('RESISTENCIA_MULTIPLA_DECLARADA')),
                ('CITATION', (l.get('CITACAO_LITERAL') or '')[:600]),
                ('AUTHORITY', 'GIRE (CNR-IPSP)'),
                ('SOURCE_URL', l.get('FONTE_URL')),
                ('SOURCE_ID', 'IT-SRC-GIRE'), ('PROVENANCE', 'REAL_FACT')]))
    grava('SCIENCE', 'herbicide-resistance.json', OrderedDict(list(env(
        'HERBICIDE_RESISTANCE', 'data/samples/IT-CIENCIA/IT-GIRE-RESISTENCIA-V2.json',
        'REAL_FACT',
        'diz ONDE FOI CONFIRMADA, nunca quanta area tem. Nao e mapa de incidencia.').items()) + [
        ('COUNT', len(res)), ('RESISTANCES', res)]))
    return {'pesquisadores': pesq, 'temas': temas, 'registros': regs, 'resistencia': res}


if __name__ == '__main__':
    os.makedirs(DR, exist_ok=True)
    print('CAMADA VOCI DAL CAMPO'); camada_vozes()
    print('CAMADA COMPETITOR'); camada_competidor()
    print('CAMADA CIENCIA'); camada_ciencia()
    print('\nok')
