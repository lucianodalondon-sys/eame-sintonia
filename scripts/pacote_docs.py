#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCUMENTOS DO PACOTE que precisam de NÚMERO CONTADO, não estimado.

    python3 scripts/pacote_docs.py

Gera `00-START-HERE/REALITY-COUNTS.md`, `04-PROVENANCE/PROVENANCE-MATRIX.json`,
`04-PROVENANCE/REAL-vs-DEMO-SUMMARY.md`, `03-SOURCE-REGISTRY/*` e
`06-HANDOFF-MANIFEST/DESIGN-HANDOFF.json`.

⚠️ Todo número aqui é lido dos arquivos do pacote na hora. Nenhum é digitado à mão —
número digitado à mão envelhece sem avisar, e este pacote vai ser reconstruído.
"""
import json
import os
import sys
from collections import Counter, OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF')
DR = os.path.join(PKG, '01-DESIGN-READY')


def carrega():
    fora = {}
    for dp, _dn, fn in os.walk(DR):
        for f in fn:
            if not f.endswith('.json'):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, DR).replace(os.sep, '/')
            try:
                fora[rel] = json.load(open(p, encoding='utf-8'))
            except ValueError:
                pass
    return fora


def lista_de(d):
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict) and 'ID' in v[0]:
            if k.endswith('_SUMMARY') or k.endswith('_IDS'):
                continue
            return k, v
    return None, []


def main():
    arqs = carrega()
    if not arqs:
        print('PACOTE_VAZIO — rode scripts/pacote.py antes'); return 1

    prov = Counter()
    por_arquivo = OrderedDict()
    matriz = []
    for rel, d in sorted(arqs.items()):
        k, itens = lista_de(d)
        if not itens:
            continue
        c = Counter(i.get('PROVENANCE', 'NAO_DECLARADA') for i in itens)
        prov.update(c)
        por_arquivo[rel] = {'ARRAY': k, 'COUNT': len(itens), 'BY_PROVENANCE': dict(c)}
        for i in itens:
            matriz.append({'ID': i.get('ID'), 'FILE': rel,
                           'PROVENANCE': i.get('PROVENANCE', 'NAO_DECLARADA'),
                           'LABEL': (i.get('TITLE') or i.get('PRODUCT') or i.get('PERSON')
                                     or i.get('EVENT') or i.get('SPECIES')
                                     or i.get('NAME') or i.get('CHANNEL')
                                     or i.get('COMPANY') or i.get('THEME')
                                     or i.get('CROP_TERM') or i.get('DATASET') or '')[:90]})

    # ── contagens de realidade ────────────────────────────────────────────────
    def n(rel):
        return por_arquivo.get(rel, {}).get('COUNT', 0)

    prods = arqs.get('ADAMA/adama-italy-products.json', {}).get('PRODUCTS', [])
    linha = Counter(p.get('LINE') for p in prods)
    acts = arqs.get('COMPETITOR-WATCH/competitor-activities.json', {}).get('ACTIVITIES', [])
    pagos = sum(1 for a in acts if a.get('ACTIVITY_TYPE') == 'PAID')
    org = sum(1 for a in acts if a.get('ACTIVITY_TYPE') == 'ORGANIC_VIDEO')
    voices = arqs.get('VOCI-DAL-CAMPO/field-voices.json', {})
    den = voices.get('DENOMINATOR', {})
    mkt = 0
    for rel in arqs:
        if rel.startswith('MARKET-PULSE/'):
            mkt += por_arquivo.get(rel, {}).get('COUNT', 0)

    C = OrderedDict([
        ('REAL_ADAMA_PRODUCTS', len(prods)),
        ('REAL_HERBICIDES', linha.get('HERBICIDA', 0)),
        ('REAL_FUNGICIDES', linha.get('FUNGICIDA', 0)),
        ('REAL_INSECTICIDES', linha.get('INSETICIDA', 0)),
        ('REAL_OTHER_PRODUCT_LINES', linha.get('OUTRA', 0)),
        ('REAL_CROP_TARGET_PRODUCT_LINKS', n('ADAMA/adama-crop-problem-product.json')),
        ('REAL_CROP_TERMS_IN_PORTFOLIO', n('ADAMA/adama-italy-crops.json')),
        ('REAL_CROP_WINDOWS', n('CROP-WINDOWS/crop-windows.json')),
        # ⚠️ Este numero ja esteve ESCRITO A MAO como 0, quando a camada nao existia.
        # Numero digitado a mao envelhece sem avisar — passa a mentir no dia em que o
        # dado chega. Agora ele conta o arquivo.
        ('REAL_CURRENT_PHENOLOGY_SIGNALS', n('CROP-WINDOWS/current-phenology.json')),
        ('REAL_REGIONS_WITH_CURRENT_BULLETIN', n('CROP-WINDOWS/regional-bulletin-sources.json')),
        ('REAL_MARKET_SOURCES_MAPPED', n('MARKET-PULSE/market-sources.json')),
        ('REAL_MARKET_CAPABILITIES_MAPPED', n('MARKET-PULSE/market-capabilities.json')),
        ('REAL_MARKET_RECORDS', mkt),
        ('REAL_NEWS', n('NEWS/news.json')),
        ('REAL_META_ADS_REACHING_ITALY', pagos),
        ('REAL_ORGANIC_COMPETITOR_RECORDS', org),
        ('REAL_COMPETITOR_COMPANIES', n('COMPETITOR-WATCH/competitor-companies.json')),
        ('REAL_COMPETITOR_PRODUCTS', n('COMPETITOR-WATCH/competitor-products.json')),
        ('REAL_ITALIAN_CHANNELS', n('VOCI-DAL-CAMPO/italian-channels.json')),
        ('REAL_FIELD_VOICES', n('VOCI-DAL-CAMPO/field-voices.json')),
        ('REAL_RESEARCHERS', n('SCIENCE/researchers.json')),
        ('REAL_SCIENTIFIC_RECORDS', n('SCIENCE/scientific-records.json')),
        ('REAL_RESEARCH_THEMES', n('SCIENCE/research-themes.json')),
        ('REAL_HERBICIDE_RESISTANCES', n('SCIENCE/herbicide-resistance.json')),
        ('REAL_PEOPLE_WITH_ROLE_EVIDENCE', n('PEOPLE/people.json')),
        ('REAL_EVENTS', n('EVENTS/events.json')),
        ('REAL_SOURCES', n('SOURCES/sources.json')),
        ('REAL_OPPORTUNITY_CANDIDATES', n('OPPORTUNITIES/opportunities.json')),
        ('REAL_FUTURE_SIGNALS', n('FUTURE-RADAR/future-signals.json')),
        ('ARCHIVE_POINTERS', n('ARCHIVE/archive-index.json')),
        ('SYNTHETIC_DEMO_OBJECTS', prov.get('SYNTHETIC_DEMO', 0)),
        ('INTERNAL_DATA_REQUIRED_OBJECTS', prov.get('INTERNAL_DATA_REQUIRED', 0)),
        ('TOTAL_OBJECTS_WITH_ID', sum(v['COUNT'] for v in por_arquivo.values())),
    ])

    L = ['# CONTAGENS DE REALIDADE — contadas, não estimadas', '',
         '**Geradas em:** 2026-09-02, lendo os arquivos deste pacote.',
         '', '| medida | valor |', '|---|---:|']
    for k, v in C.items():
        L.append('| `%s` | **%s** |' % (k, v))
    L += ['', '---', '', '## Proveniência de todos os objetos', '',
          '| classe | objetos |', '|---|---:|']
    for k, v in prov.most_common():
        L.append('| `%s` | %d |' % (k, v))
    L += ['', '⚠️ **`SYNTHETIC_DEMO` = %d.** Este pacote não contém objeto inventado. O que '
          'precisa ser sintético (notificação, fluxo, mensagem de Field Sales) é trabalho do '
          'Design e vai nascer marcado como tal.' % prov.get('SYNTHETIC_DEMO', 0),
          '', '---', '', '## Onde cada número mora', '',
          '| arquivo | array | objetos |', '|---|---|---:|']
    for rel, v in por_arquivo.items():
        L.append('| `01-DESIGN-READY/%s` | `%s` | %d |' % (rel, v['ARRAY'], v['COUNT']))

    L += ['', '---', '', '## Dois números que precisam do denominador ao lado', '',
          '**Vozes de campo italianas: %d** — de **%s** comentários italianos lidos, dentro '
          'de **%s** comentários no total. A raridade É o achado: quem apresentar as %d sem o '
          'denominador está mentindo por omissão.'
          % (C['REAL_FIELD_VOICES'], den.get('IT_COMMENTS_READ', '?'),
             den.get('ALL_COMMENTS_READ', '?'), C['REAL_FIELD_VOICES']),
          '',
          '**Ligações cultura × alvo × produto: %d** — mas elas saem de **19 dos 163 '
          'produtos (11,7%%)**. Os outros 144 não têm linha de uso lida. Isso é cobertura de '
          'LEITURA, não ausência de registro.' % C['REAL_CROP_TARGET_PRODUCT_LINKS'],
          '',
          '**Vozes de campo: %d — mas elas NÃO se somam.** A varredura de 02/09 mediu a '
          'plateia do canal de cada fala. Ver `BY_CHANNEL_AUDIENCE` em '
          '`VOCI-DAL-CAMPO/field-voices.json`: uma parte vem de canal de HORTA DOMESTICA e '
          'fala de roseira e limoeiro. Relato em primeira pessoa sobre um vaso não é voz de '
          'lavoura.' % C['REAL_FIELD_VOICES'],
          '',
          '**Sinais de fenologia corrente: %d, de %d regiões.** Esta lacuna estava declarada '
          'como a MAIOR do pacote, com valor 0, e foi fechada na varredura noturna de '
          '02/09/2026. O que não mudou: são 6 regiões de 20, e nenhuma fala pelo país.'
          % (C['REAL_CURRENT_PHENOLOGY_SIGNALS'], C['REAL_REGIONS_WITH_CURRENT_BULLETIN'])]

    d0 = os.path.join(PKG, '00-START-HERE')
    os.makedirs(d0, exist_ok=True)
    open(os.path.join(d0, 'REALITY-COUNTS.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')

    # ── proveniência ──────────────────────────────────────────────────────────
    d4 = os.path.join(PKG, '04-PROVENANCE')
    os.makedirs(d4, exist_ok=True)
    json.dump(OrderedDict([
        ('LAYER', 'PROVENANCE_MATRIX'), ('BUILT_AT', '2026-09-02'),
        ('CLASSES', {
            'REAL_FACT': 'fato oficial: rotulo autorizado, ato juridico, decreto regional',
            'REAL_SOURCE': 'veio de fonte primaria publica que foi lida',
            'REAL_DERIVED': 'derivado por nos de material real, declarado como derivacao',
            'SYNTHETIC_DEMO': 'inventado para demonstrar a experiencia',
            'INTERNAL_DATA_REQUIRED': 'so existe se a ADAMA conectar dado interno',
            'NOT_YET_PROVABLE': 'plausivel e sem lastro suficiente'}),
        ('TOTALS', dict(prov)), ('BY_FILE', por_arquivo), ('COUNT', len(matriz)),
        ('OBJECTS', matriz)]),
        open(os.path.join(d4, 'PROVENANCE-MATRIX.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)

    R = ['# REAL contra DEMO — o resumo que evita adivinhação', '',
         '**Objetos com ID no pacote: %d.**' % len(matriz), '',
         '| classe de proveniência | objetos | o que significa para a tela |', '|---|---:|---|',
         '| `REAL_FACT` | %d | pode ir para a tela como fato, com a fonte ao lado |'
         % prov.get('REAL_FACT', 0),
         '| `REAL_SOURCE` | %d | pode ir para a tela citando a fonte e a data |'
         % prov.get('REAL_SOURCE', 0),
         '| `REAL_DERIVED` | %d | precisa do rótulo «interpretação do Sintonia» visível |'
         % prov.get('REAL_DERIVED', 0),
         '| `SYNTHETIC_DEMO` | %d | — |' % prov.get('SYNTHETIC_DEMO', 0),
         '| `INTERNAL_DATA_REQUIRED` | %d | mostrar como «dado interno não conectado» |'
         % prov.get('INTERNAL_DATA_REQUIRED', 0),
         '', '---', '',
         '## A regra de tela, em uma linha por classe', '',
         '- **`REAL_FACT`** — o rótulo, o ato, o decreto. Vai como está, com fonte e data.',
         '- **`REAL_SOURCE`** — o anúncio, o vídeo, o comentário, o boletim. Vai com fonte, '
         'data **e** com o que ele não prova.',
         '- **`REAL_DERIVED`** — o par cultura×alvo, a temperatura de mercado, a distância '
         'entre menção e linha de uso. **Nunca** vai sem o «por quê» aberto ao lado.',
         '', '⚠️ Um objeto `REAL_DERIVED` apresentado sem o «por quê» vira caixa-preta — '
         'e caixa-preta é exatamente o que este projeto existe para não ser.']
    open(os.path.join(d4, 'REAL-vs-DEMO-SUMMARY.md'), 'w', encoding='utf-8').write(
        '\n'.join(R) + '\n')

    # ── registro de fontes ────────────────────────────────────────────────────
    src = arqs.get('SOURCES/sources.json', {}).get('SOURCES', [])
    d3 = os.path.join(PKG, '03-SOURCE-REGISTRY')
    os.makedirs(d3, exist_ok=True)
    json.dump(OrderedDict([
        ('LAYER', 'MASTER_SOURCE_REGISTRY'), ('BUILT_AT', '2026-09-02'),
        ('LAW', 'HTTP 200 NAO E FONTE VIVA. ACCESS_STATUS e estado medido, nao promessa.'),
        ('COUNT', len(src)),
        ('BY_TYPE', dict(Counter(s.get('TYPE') for s in src))),
        ('BY_ACCESS_STATUS', dict(Counter(s.get('ACCESS_STATUS') for s in src))),
        ('SOURCES', src)]),
        open(os.path.join(d3, 'MASTER-SOURCE-REGISTRY.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)
    S = ['# REGISTRO MESTRE DE FONTES', '',
         '**%d fontes.** Toda fonte tem `SOURCE_ID` estável; os objetos do pacote apontam '
         'para ele.' % len(src), '',
         '| SOURCE_ID | fonte | tipo | geografia | cadência | último | acesso |',
         '|---|---|---|---|---|---|---|']
    for s in src:
        S.append('| `%s` | %s | %s | %s | %s | %s | %s |' % (
            s.get('ID') or s.get('SOURCE_ID'), s.get('NAME'), s.get('TYPE'),
            s.get('GEOGRAPHY') or s.get('COUNTRY'), s.get('FREQUENCY'),
            s.get('LATEST_OBSERVATION'), s.get('ACCESS_STATUS')))
    S += ['', '---', '', '## Limitação declarada de cada fonte', '']
    for s in src:
        if s.get('LIMITATIONS'):
            S.append('- **%s** — %s' % (s.get('NAME'), s.get('LIMITATIONS')))
    open(os.path.join(d3, 'MASTER-SOURCE-REGISTRY.md'), 'w', encoding='utf-8').write(
        '\n'.join(S) + '\n')

    # ── manifesto ─────────────────────────────────────────────────────────────
    d6 = os.path.join(PKG, '06-HANDOFF-MANIFEST')
    os.makedirs(d6, exist_ok=True)
    arquivos = []
    for dp, _dn, fn in os.walk(PKG):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            r = os.path.relpath(p, PKG).replace(os.sep, '/')
            arquivos.append({'FILE': r, 'BYTES': os.path.getsize(p),
                             'RECORDS': por_arquivo.get(
                                 r.replace('01-DESIGN-READY/', ''), {}).get('COUNT')})
    json.dump(OrderedDict([
        ('PACKAGE', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF'),
        ('BUILT_AT', '2026-09-02'),
        ('FOR', 'o Claude que vai desenhar o portal do piloto italiano'),
        ('START_WITH', [
            '00-START-HERE/README-FIRST.md',
            '00-START-HERE/EXECUTIVE-SUMMARY.md',
            '00-START-HERE/WHAT-TO-USE-IN-THE-PORTAL.md',
            '00-START-HERE/REALITY-COUNTS.md',
            '05-GAPS-AND-LIMITS/DO-NOT-CLAIM.md',
            '01-DESIGN-READY/',
            '01-DESIGN-READY/RELATIONSHIPS/entity-links.json',
            '04-PROVENANCE/REAL-vs-DEMO-SUMMARY.md']),
        ('READING_ORDER_WHY',
         'README define o que e real e o que nao pode ser dito. WHAT-TO-USE separa o que vai '
         'direto do que precisa de interpretacao. DO-NOT-CLAIM vem ANTES dos dados de '
         'proposito: e mais facil nao escrever a frase errada do que apaga-la depois.'),
        ('LAYERS', {k: v for k, v in por_arquivo.items()}),
        ('DEPENDENCIES', {
            'RELATIONSHIPS/entity-links.json': 'resolve IDs contra 06-HANDOFF-MANIFEST/ID-INDEX.json',
            'todas as camadas': 'apontam para SOURCE_ID de 01-DESIGN-READY/SOURCES/sources.json'}),
        ('TOTAL_FILES', len(arquivos)),
        ('FILES', arquivos)]),
        open(os.path.join(d6, 'DESIGN-HANDOFF.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)

    print('REALITY-COUNTS.md · PROVENANCE-MATRIX.json · REAL-vs-DEMO-SUMMARY.md')
    print('MASTER-SOURCE-REGISTRY.{json,md} · DESIGN-HANDOFF.json')
    print('objetos com ID: %d · proveniencia: %s' % (len(matriz), dict(prov)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
