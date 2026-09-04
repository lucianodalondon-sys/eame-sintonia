#!/usr/bin/env python3
"""
DESCOBERTA DE SENSORES HUMANOS — ITÁLIA. Rota gratuita, identidade primeiro.

    python3 scripts/sensor_descoberta_it.py universo     # ADAMA IT: produtos -> matriz
    python3 scripts/sensor_descoberta_it.py openalex     # pesquisadores por recorte
    python3 scripts/sensor_descoberta_it.py resumo

POR QUE ESTE ARQUIVO EXISTE, TENDO `speaker_universo.py`
--------------------------------------------------------
Aquele script serve ao piloto EARLY SIGNAL: **seis recortes congelados por um árbitro**,
lista curta, propósito de teste. Alterá-lo para caber a Itália inteira quebraria o
congelamento que ele mesmo publica (`FROZEN_BY: aba ÁRBITRA, 2026-08-30, ANTES da coleta`)
e invalidaria o artefato `SPEAKER-UNIVERSE-PILOT-V1`.

Aqui o recorte não é congelado por um árbitro: ele é **derivado do que a ADAMA tem
autorizado na Itália**, e muda quando o registro muda. São dois contratos diferentes.
A mecânica de coleta — pausa, teto de páginas, `THROTTLED_NOT_EMPTY`, afiliação no país —
é **importada** de `speaker_universo`, não recopiada.

A MATRIZ NÃO É INVENTADA
-------------------------
`CROP × TARGET` sai de duas fontes declaradas, e cada par carrega qual delas o sustenta:

    REGISTRY_ACTIVE   a ADAMA tem, HOJE, autorização em vigor na Itália com um ativo cujo
                      domínio de uso é esse. Fonte: IT-T4-001 (Ministero della Salute).
    PUBLIC_SIGNAL     a ADAMA falou publicamente disso em 2025-2026 na Itália.
                      Fonte: docs/adama/RADAR-ADAMA-EAME.md.

O que NÃO temos é a etiqueta: `fitosanitari.salute.gov.it` — a base que traria
`coltura x avversita` autorizada produto a produto — **não é alcançável desta saída**
(TLS falha no proxy; medido em 2026-09-04). Isso é `FAILED_WITH_REASON`, e por isso
nenhum par desta matriz afirma "uso autorizado". A matriz diz onde PROCURAR gente,
não o que a etiqueta permite.

O QUE ESTE ARQUIVO NÃO FAZ
---------------------------
Não chama rota paga, não coleta post, não ordena por seguidores, não cria authority score,
e não promove ninguém a sensor. Ele entrega CANDIDATOS com âncora técnica; a promoção é do
`sensor_humano.py`, contra critério escrito.
"""
import json
import os
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import speaker_universo as SU                                            # noqa: E402
from selo_de_amostra import selar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw', 'SENSOR-HUMANO-IT')
SAMPLES = os.path.join(ROOT, 'data', 'samples', 'IT-HUMAN-SENSORS')

# Registro italiano: o mesmo arquivo datado que o IT-T4-001 já contratou. Baixado por
# `chain.py`/curl para data/raw; o nome datado é DESCOBERTO, nunca chutado.
CSV_LOCAL = os.path.join(ROOT, 'data', 'raw', 'IT-T4-001', 'PROD_FTS.csv')

IN_FORCE = {
    'Ri-registrato', 'Autorizzato', 'Autorizzato con procedura zonale',
    'Autorizzato in regime di Riconoscimento Reciproco',
    'Autorizzato Art. 34 Reg. 1107/2009', 'Autorizzato Art. 10 D.P.R. 290/2001',
    'Ri-registrato (Air 1 Fase 1)', 'Rinnovato Art. 43 Reg. 1107/2009',
}

# ---------------------------------------------------------------------------------------
# A MATRIZ DE ONDE PROCURAR — cada linha declara o que a sustenta.
#
# (CROP, TARGET, BASIS, ANCHOR)  — ANCHOR é o ativo ADAMA em vigor ou o sinal público.
# REGIÕES entram por linha porque a pergunta "quem observa isso de perto?" é regional:
# carpocapsa em Trentino não é a mesma pergunta que carpocapsa em Emilia-Romagna.
# ---------------------------------------------------------------------------------------
MATRIZ = [
    ('WHEAT',       'SEPTORIA',            'REGISTRY_ACTIVE+PUBLIC_SIGNAL',
     'PROTHIOCONAZOLE|AZOXYSTROBIN|FLUXAPYROXAD (AVASTEL, MAXENTIS, MAGANIC)',
     ['EMILIA-ROMAGNA', 'VENETO', 'LOMBARDIA', 'PIEMONTE', 'MARCHE', 'UMBRIA']),
    ('WHEAT',       'FUSARIUM_HEAD_BLIGHT', 'REGISTRY_ACTIVE+PUBLIC_SIGNAL',
     'PROTHIOCONAZOLE|TEBUCONAZOLE',
     ['EMILIA-ROMAGNA', 'VENETO', 'PUGLIA', 'BASILICATA', 'MARCHE', 'SICILIA']),
    ('WHEAT',       'RUST',                'REGISTRY_ACTIVE',
     'PROTHIOCONAZOLE|AZOXYSTROBIN|TEBUCONAZOLE',
     ['EMILIA-ROMAGNA', 'PUGLIA', 'SICILIA', 'TOSCANA']),
    ('WHEAT',       'POWDERY_MILDEW',      'REGISTRY_ACTIVE',
     'FENPROPIDIN|PROTHIOCONAZOLE (FORAPRO-classe)',
     ['EMILIA-ROMAGNA', 'VENETO', 'PIEMONTE']),
    ('CEREAL',      'GRASS_WEEDS',         'REGISTRY_ACTIVE',
     'CLODINAFOP|PINOXADEN|MESOSULFURON-METHYL|CHLOROTOLURON (CELIO, HAWK)',
     ['EMILIA-ROMAGNA', 'VENETO', 'LOMBARDIA', 'PIEMONTE', 'PUGLIA']),
    ('CEREAL',      'HERBICIDE_RESISTANCE', 'REGISTRY_ACTIVE',
     'CLODINAFOP|PINOXADEN — ACCase/ALS, onde a resistência italiana está descrita',
     ['EMILIA-ROMAGNA', 'VENETO', 'LOMBARDIA', 'PIEMONTE']),
    ('CEREAL',      'APHIDS',              'REGISTRY_ACTIVE',
     'PIRIMICARB (APHOX)|FLONICAMID|LAMBDA-CYHALOTHRIN',
     ['EMILIA-ROMAGNA', 'VENETO', 'PUGLIA']),
    ('MAIZE',       'CORN_BORER',          'REGISTRY_ACTIVE',
     'CHLORANTRANILIPROLE|LAMBDA-CYHALOTHRIN|TEFLUTHRIN',
     ['LOMBARDIA', 'VENETO', 'PIEMONTE', 'FRIULI-VENEZIA GIULIA', 'EMILIA-ROMAGNA']),
    ('MAIZE',       'MYCOTOXIN',           'REGISTRY_ACTIVE',
     'PROTHIOCONAZOLE|AZOXYSTROBIN — Fusarium/aflatossina em mais',
     ['LOMBARDIA', 'VENETO', 'PIEMONTE', 'FRIULI-VENEZIA GIULIA']),
    ('MAIZE',       'MAIZE_WEEDS',         'REGISTRY_ACTIVE',
     'NICOSULFURON|MESOTRIONE|PENDIMETHALIN|DICAMBA',
     ['LOMBARDIA', 'VENETO', 'PIEMONTE', 'EMILIA-ROMAGNA']),
    ('MAIZE',       'ROOTWORM',            'REGISTRY_ACTIVE',
     'TEFLUTHRIN (geodisinfestante) — Diabrotica',
     ['LOMBARDIA', 'VENETO', 'FRIULI-VENEZIA GIULIA', 'PIEMONTE']),
    ('SUGAR_BEET',  'BEET_WEEDS',          'REGISTRY_ACTIVE',
     'METAMITRON (GOLTIX, GOLD-BEET, GOLTIX TOP) — 7 registros em vigor',
     ['EMILIA-ROMAGNA', 'VENETO', 'MARCHE', 'LOMBARDIA']),
    ('SUGAR_BEET',  'CERCOSPORA',          'REGISTRY_ACTIVE',
     'AZOXYSTROBIN|DIFENOCONAZOLE',
     ['EMILIA-ROMAGNA', 'VENETO', 'MARCHE']),
    ('VINE',        'DOWNY_MILDEW',        'REGISTRY_ACTIVE',
     'FOLPET (FOLPAN)|CYMOXANIL|METALAXYL-M — 6+6+2 registros em vigor',
     ['VENETO', 'PIEMONTE', 'TOSCANA', 'SICILIA', 'PUGLIA', 'FRIULI-VENEZIA GIULIA',
      'TRENTINO-ALTO ADIGE', 'EMILIA-ROMAGNA']),
    ('VINE',        'FLAVESCENCE_DOREE',   'REGISTRY_ACTIVE',
     'LAMBDA-CYHALOTHRIN|TAU-FLUVALINATE — vetor Scaphoideus titanus',
     ['PIEMONTE', 'VENETO', 'LOMBARDIA', 'FRIULI-VENEZIA GIULIA', 'EMILIA-ROMAGNA']),
    ('VINE',        'GRAPE_MOTH',          'REGISTRY_ACTIVE',
     'CHLORANTRANILIPROLE|LAMBDA-CYHALOTHRIN — Lobesia botrana',
     ['SICILIA', 'PUGLIA', 'TOSCANA', 'VENETO', 'PIEMONTE']),
    ('APPLE',       'SCAB',                'REGISTRY_ACTIVE',
     'CAPTAN (MERPAN)|DIFENOCONAZOLE',
     ['TRENTINO-ALTO ADIGE', 'PIEMONTE', 'VENETO', 'EMILIA-ROMAGNA']),
    ('APPLE',       'CODLING_MOTH',        'REGISTRY_ACTIVE',
     'CHLORANTRANILIPROLE|LAMBDA-CYHALOTHRIN — Cydia pomonella',
     ['TRENTINO-ALTO ADIGE', 'EMILIA-ROMAGNA', 'PIEMONTE', 'VENETO']),
    ('APPLE',       'FRUIT_THINNING',      'REGISTRY_ACTIVE',
     'METAMITRON (BREVIS) — único DIRADANTE do portfólio italiano',
     ['TRENTINO-ALTO ADIGE', 'EMILIA-ROMAGNA', 'PIEMONTE']),
    ('STONE_FRUIT', 'BROWN_ROT',           'REGISTRY_ACTIVE',
     'TEBUCONAZOLE|DIFENOCONAZOLE — Monilinia',
     ['EMILIA-ROMAGNA', 'CAMPANIA', 'PIEMONTE', 'BASILICATA']),
    ('STONE_FRUIT', 'BROWN_MARMORATED_STINK_BUG', 'REGISTRY_ACTIVE',
     'LAMBDA-CYHALOTHRIN — Halyomorpha halys',
     ['EMILIA-ROMAGNA', 'VENETO', 'PIEMONTE', 'FRIULI-VENEZIA GIULIA']),
    ('OLIVE',       'OLIVE_FRUIT_FLY',     'REGISTRY_ACTIVE',
     'LAMBDA-CYHALOTHRIN — Bactrocera oleae',
     ['PUGLIA', 'CALABRIA', 'SICILIA', 'TOSCANA', 'LAZIO', 'UMBRIA']),
    ('OLIVE',       'OLIVE_DISEASE',       'REGISTRY_ACTIVE',
     'AZOXYSTROBIN|DIFENOCONAZOLE — occhio di pavone/lebbra',
     ['PUGLIA', 'CALABRIA', 'SICILIA', 'TOSCANA']),
    ('POTATO',      'LATE_BLIGHT',         'REGISTRY_ACTIVE',
     'FLUAZINAM (AGHARTA)|CYMOXANIL|METALAXYL-M',
     ['EMILIA-ROMAGNA', 'CAMPANIA', 'ABRUZZO', 'SICILIA', 'VENETO']),
    ('TOMATO',      'TOMATO_DISEASE',      'REGISTRY_ACTIVE',
     'AZOXYSTROBIN|CYMOXANIL|METALAXYL-M',
     ['PUGLIA', 'EMILIA-ROMAGNA', 'CAMPANIA', 'LAZIO', 'SICILIA']),
    ('RICE',        'RICE_PROTECTION',     'REGISTRY_ACTIVE',
     'AZOXYSTROBIN|PROPAQUIZAFOP (AGIL)',
     ['LOMBARDIA', 'PIEMONTE']),
    ('MULTI',       'SLUGS',               'REGISTRY_ACTIVE',
     'METALDEHYDE (LUMA-KL) — único molusquicida do portfólio',
     ['EMILIA-ROMAGNA', 'VENETO', 'LOMBARDIA']),
]

# ------------------------------------------------------------------ recortes do OpenAlex
# A LEI: o termo é aspeado ou conjuntivo, nunca palavra solta — `speaker_universo` já
# mediu o custo (97,3x de população errada). CROP e ISSUE saem da CONSULTA.
RECORTES_IT = [
    ('wheat_septoria',   '"Zymoseptoria tritici" OR "Septoria tritici"', 'WHEAT', 'SEPTORIA'),
    ('wheat_fusarium',   '("durum wheat" OR "Triticum durum" OR "wheat") AND '
                         '("Fusarium head blight" OR "Fusarium graminearum" OR deoxynivalenol)',
     'WHEAT', 'FUSARIUM_HEAD_BLIGHT'),
    ('wheat_rust',       '("Puccinia triticina" OR "Puccinia striiformis" OR '
                         '"Puccinia graminis") AND wheat', 'WHEAT', 'RUST'),
    ('wheat_powdery',    '"Blumeria graminis" OR "Erysiphe graminis"', 'WHEAT', 'POWDERY_MILDEW'),
    ('cereal_weeds',     '("Lolium rigidum" OR "Avena sterilis" OR "Alopecurus myosuroides" '
                         'OR "Phalaris paradoxa") AND (wheat OR cereal)',
     'CEREAL', 'GRASS_WEEDS'),
    ('herbicide_resist', '"herbicide resistance" OR "herbicide-resistant weeds" OR '
                         '"ACCase-resistant" OR "ALS-resistant"', 'CEREAL', 'HERBICIDE_RESISTANCE'),
    ('cereal_aphids',    '("Sitobion avenae" OR "Rhopalosiphum padi" OR "Metopolophium '
                         'dirhodum") AND (cereal OR wheat OR barley)', 'CEREAL', 'APHIDS'),
    ('maize_borer',      '("Ostrinia nubilalis" OR "Sesamia nonagrioides") AND '
                         '(maize OR corn)', 'MAIZE', 'CORN_BORER'),
    ('maize_rootworm',   '"Diabrotica virgifera"', 'MAIZE', 'ROOTWORM'),
    ('maize_mycotoxin',  '(maize OR corn) AND ("aflatoxin" OR "fumonisin" OR '
                         '"Aspergillus flavus" OR "Fusarium verticillioides")',
     'MAIZE', 'MYCOTOXIN'),
    ('maize_weeds',      '("Sorghum halepense" OR "Echinochloa crus-galli" OR '
                         '"Abutilon theophrasti") AND (maize OR corn)', 'MAIZE', 'MAIZE_WEEDS'),
    ('beet_cercospora',  '"Cercospora beticola"', 'SUGAR_BEET', 'CERCOSPORA'),
    ('vine_downy',       '"Plasmopara viticola"', 'VINE', 'DOWNY_MILDEW'),
    ('vine_flavescence', '"flavescence doree" OR "Scaphoideus titanus" OR '
                         '("grapevine" AND "phytoplasma")', 'VINE', 'FLAVESCENCE_DOREE'),
    ('vine_moth',        '"Lobesia botrana"', 'VINE', 'GRAPE_MOTH'),
    ('apple_scab',       '"Venturia inaequalis"', 'APPLE', 'SCAB'),
    ('apple_codling',    '"Cydia pomonella"', 'APPLE', 'CODLING_MOTH'),
    ('stinkbug',         '"Halyomorpha halys"', 'STONE_FRUIT', 'BROWN_MARMORATED_STINK_BUG'),
    ('brown_rot',        '"Monilinia fructicola" OR "Monilinia laxa" OR "Monilinia fructigena"',
     'STONE_FRUIT', 'BROWN_ROT'),
    ('olive_fly',        '"Bactrocera oleae"', 'OLIVE', 'OLIVE_FRUIT_FLY'),
    ('olive_disease',    '"Venturia oleaginea" OR "Spilocaea oleagina" OR '
                         '"Colletotrichum" AND olive', 'OLIVE', 'OLIVE_DISEASE'),
    ('potato_blight',    '"Phytophthora infestans"', 'POTATO', 'LATE_BLIGHT'),
    ('tomato_disease',   '("Solanum lycopersicum" OR tomato) AND ("Alternaria" OR '
                         '"Phytophthora infestans" OR "Pseudomonas syringae")',
     'TOMATO', 'TOMATO_DISEASE'),
    ('rice_blast',       '"Pyricularia oryzae" OR "Magnaporthe oryzae"', 'RICE', 'RICE_PROTECTION'),
    ('resistance_fungi', '"fungicide resistance" AND (SDHI OR strobilurin OR '
                         '"demethylation inhibitor" OR QoI)', 'MULTI', 'FUNGICIDE_RESISTANCE'),
]


def universo():
    """A matriz de onde procurar, ancorada no registro italiano em vigor."""
    import csv
    os.makedirs(SAMPLES, exist_ok=True)
    produtos, motivo = [], None
    if os.path.exists(CSV_LOCAL):
        with open(CSV_LOCAL, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f, delimiter=';'):
                if 'ADAMA' in (r['ragione_sociale'] or '').upper() \
                        and (r['stato_amministrativo'] or '').strip() in IN_FORCE:
                    produtos.append({
                        'REGISTRATION_ID': r['num_registrazione'],
                        'REFERENCE_PRODUCT': r['denominazione_prodotto'],
                        'REFERENCE_HOLDER': r['ragione_sociale'],
                        'ACTIVITY': r['attivita'],
                        'ACTIVES': [s for s in (r['sostanze_attive'] or '').split('|')
                                    if s and s != '-'],
                        'STATUS': r['stato_amministrativo'],
                        'EXPIRY': r['data_scadenza_autorizzazione'],
                    })
    else:
        # FAIL CLOSED: ausência do CSV não vira "a ADAMA não tem produto".
        motivo = 'CSV_NOT_PRESENT_LOCALLY — baixar de dati.salute.gov.it antes'

    por_titular = defaultdict(int)
    ativos = defaultdict(int)
    for p in produtos:
        por_titular[p['REFERENCE_HOLDER']] += 1
        for a in p['ACTIVES']:
            ativos[a] += 1

    linhas = [{
        'CROP': c, 'TARGET': t, 'BASIS': b, 'ADAMA_ANCHOR': anc,
        'REGIONS_TO_SEARCH': regs,
    } for c, t, b, anc, regs in MATRIZ]

    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/UNIVERSE',
        'source': 'IT-T4-001 (Ministero della Salute, PROD_FTS datado) + '
                  'docs/adama/RADAR-ADAMA-EAME.md',
        'SOURCE_LOCATION': 'ITALY',
        'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'IT',
        'EVIDENCE_CLASS': 'DERIVED_FROM_PRIMARY_REGISTRY',
        'REGISTRY_STATE': 'READ' if produtos else 'FAILED_WITH_REASON',
        'REGISTRY_REASON': motivo,
        'LABEL_CROP_TARGET_STATE': 'FAILED_WITH_REASON',
        'LABEL_CROP_TARGET_REASON':
            'fitosanitari.salute.gov.it (coltura x avversita por produto) nao alcancavel '
            'desta saida: TLS falha no proxy e servizi.salute.gov.it devolve 502. '
            'Medido 2026-09-04. NENHUM par desta matriz afirma uso autorizado em etiqueta.',
        'ADAMA_PRODUCTS_IN_FORCE': len(produtos),
        'ADAMA_BY_HOLDER': dict(sorted(por_titular.items(), key=lambda kv: -kv[1])),
        'ADAMA_ACTIVES_DISTINCT': len(ativos),
        'ADAMA_ACTIVES': dict(sorted(ativos.items(), key=lambda kv: (-kv[1], kv[0]))),
        'MATRIX_ROWS': len(linhas),
        'CROPS': sorted({r['CROP'] for r in linhas}),
        'TARGETS': sorted({r['TARGET'] for r in linhas}),
        'REGIONS': sorted({g for r in linhas for g in r['REGIONS_TO_SEARCH']}),
        'MATRIX': linhas,
        'PRODUCTS': produtos,
    }
    caminho = os.path.join(SAMPLES, 'UNIVERSE.json')
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('%d produtos ADAMA em vigor · %d ativos · %d linhas de matriz -> %s' % (
        len(produtos), len(ativos), len(linhas), caminho))
    return corpo


def openalex():
    """Pesquisadores com afiliação italiana, um recorte por vez, pela rota gratuita."""
    os.makedirs(RAW, exist_ok=True)
    saida, agregado = [], {}
    for chave, termo, crop, issue in RECORTES_IT:
        r = SU.buscar_recorte(termo, 'IT', crop, issue)
        print('%-20s %-22s obras=%-6s autores=%-6s %s' % (
            chave, r['STATE'], r['WORKS_TRAVERSED'], r['AUTHORS_FOUND'], r['REASON'] or ''))
        for aid, a in r.pop('AUTHORS').items():
            g = agregado.setdefault(aid, {
                'PERSON_ID': aid, 'NAME': a['NAME'], 'ORCID': a['ORCID'],
                'WORKS_IN_SCOPE': 0, 'INSTITUTIONS': defaultdict(int),
                'LAST_YEAR': None, 'SCOPES': set(),
            })
            g['WORKS_IN_SCOPE'] += a['WORKS_IN_SCOPE']
            g['SCOPES'] |= a['SCOPES']
            if a['LAST_YEAR'] and (g['LAST_YEAR'] is None or a['LAST_YEAR'] > g['LAST_YEAR']):
                g['LAST_YEAR'] = a['LAST_YEAR']
            for nome, n in a['INSTITUTIONS'].items():
                g['INSTITUTIONS'][nome] += n
        r['SCOPE_KEY'] = chave
        saida.append(r)
        time.sleep(SU.PAUSA)

    pessoas = []
    for g in agregado.values():
        insts = sorted(g['INSTITUTIONS'].items(), key=lambda kv: (-kv[1], kv[0]))
        pessoas.append({
            'PERSON_ID': g['PERSON_ID'], 'NAME': g['NAME'], 'ORCID': g['ORCID'],
            'WORKS_IN_SCOPE': g['WORKS_IN_SCOPE'], 'LAST_YEAR': g['LAST_YEAR'],
            'INSTITUTION': insts[0][0] if insts else 'NÃO SEI',
            'ALL_INSTITUTIONS': [n for n, _ in insts],
            'ALL_INSTITUTIONS_COUNT': len(insts),
            'SCOPES': sorted(g['SCOPES']),
        })
    pessoas.sort(key=lambda p: (-p['WORKS_IN_SCOPE'], p['NAME'] or ''))

    corpo = {
        'SOURCE_ID': 'SENSOR-HUMANO-IT/OPENALEX',
        'source': 'OpenAlex (api.openalex.org), rota REST gratuita, sem chave',
        'SOURCE_LOCATION': 'global — índice bibliográfico',
        'FACT_LOCATION': 'NÃO SEI — a afiliação é do AUTOR, não do estudo',
        'ORIGINAL_LANGUAGE': 'EN',
        'COUNTRY_OF_AFFILIATION': 'IT',
        'WINDOW': SU.YEARS,
        'RATE_LIMIT_POLICY': 'pausa %.1fs · teto %d páginas por recorte' % (
            SU.PAUSA, SU.PAGINAS_MAX),
        'SCOPES': saida,
        'SCOPES_THROTTLED': [s['SCOPE_KEY'] for s in saida if s['STATE'] == SU.THROTTLED],
        'SCOPES_FAILED': [s['SCOPE_KEY'] for s in saida if s['STATE'] == SU.FAILED],
        'PEOPLE_COUNT': len(pessoas),
        'PEOPLE': pessoas,
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    caminho = os.path.join(RAW, 'openalex-IT.json')
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('\n%d pessoas -> %s' % (len(pessoas), caminho))
    return corpo


def resumo():
    p = os.path.join(RAW, 'openalex-IT.json')
    if not os.path.exists(p):
        print('sem coleta ainda: %s' % p)
        return
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    print('%d pessoas · estrangulados: %s · falhos: %s' % (
        d['PEOPLE_COUNT'], d['SCOPES_THROTTLED'] or 'nenhum',
        d['SCOPES_FAILED'] or 'nenhum'))
    for x in d['PEOPLE'][:30]:
        print('  %-32s %3d obras  %-5s %s' % (
            (x['NAME'] or '')[:32], x['WORKS_IN_SCOPE'],
            'ORCID' if x['ORCID'] else '  -  ', (x['INSTITUTION'] or '')[:46]))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'resumo'
    {'universo': universo, 'openalex': openalex, 'resumo': resumo}[cmd]()
