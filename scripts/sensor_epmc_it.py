#!/usr/bin/env python3
"""
ROTA CIENTÍFICA ITALIANA — Europe PMC. Substituta declarada da rota OpenAlex.

    python3 scripts/sensor_epmc_it.py buscar
    python3 scripts/sensor_epmc_it.py resumo

POR QUE NÃO É O OpenAlex
-------------------------
`speaker_universo.py` chama o OpenAlex de "rota REST gratuita, sem chave". **Essa premissa
morreu.** Medido em 2026-09-04, desta saída, com e sem `mailto`:

    HTTP 429 · {"error":"Rate limit exceeded",
                "message":"Insufficient budget. This request costs $0.0001 but you only
                           have $0 remaining. Resets at midnight UTC.",
                "retryAfter":49093, "dailyRemainingUsd":0}

Não é rajada nem estrangulamento por IP: é **orçamento diário zerado**, com preço por
requisição e página de tarifa. Os 25 recortes italianos saíram todos
`THROTTLED_NOT_EMPTY` — nenhum com zero, porque `SOURCE FAILURE != ZERO`.

Isso é `FAILED_WITH_REASON` do OpenAlex, não ausência de pesquisadores italianos. A rota
substituta é o **Europe PMC** (EBI), que responde 200 sem chave e entrega o que a missão
precisa e o OpenAlex não dava tão diretamente: **a string de afiliação por autor**, com a
cidade dentro.

O QUE A CIDADE NA AFILIAÇÃO PROVA — e o que ela não prova
----------------------------------------------------------
    "Research and Innovation Centre, Fondazione Edmund Mach, San Michele all'Adige, Italy."

Isso prova o **endereço declarado da instituição do autor**. `REGION_BASIS` sai como
`INSTITUTION_ADDRESS_DECLARED_IN_AFFILIATION`, e é a única coisa que a região significa
aqui. **Não** é onde o experimento foi feito, **não** é onde a pessoa observa campo, e
`FACT_LOCATION` continua `NÃO SEI` — a mesma lei que o `speaker_universo` já escreveu.

A LEI DO TERMO CONTINUA VALENDO
--------------------------------
`CROP` e `ISSUE` saem da CONSULTA, nunca de leitura livre do título. Os termos são os
mesmos 25 recortes de `sensor_descoberta_it.RECORTES_IT`, importados — não redigitados.
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sensor_descoberta_it import RECORTES_IT                             # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw', 'SENSOR-HUMANO-IT')
API = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'

JANELA = '[2022-01-01 TO 2026-12-31]'   # quem fala HOJE; obra de 2019 não é sensor atual
PAUSA = 1.2
PAGINAS_MAX = 3
POR_PAGINA = 100

THROTTLED = 'THROTTLED_NOT_EMPTY'
OK = 'COLLECTED'
FAILED = 'FAILED_WITH_REASON'

# --------------------------------------------------------------------- cidade -> região
# Derivação declarada: a cidade aparece na string de afiliação. O mapa cobre as cidades
# com instituição agronômica italiana relevante. Cidade fora do mapa sai `NÃO SEI` —
# nunca é chutada por proximidade de nome.
CIDADE_REGIAO = {
    'bologna': 'EMILIA-ROMAGNA', 'cesena': 'EMILIA-ROMAGNA', 'piacenza': 'EMILIA-ROMAGNA',
    'parma': 'EMILIA-ROMAGNA', 'modena': 'EMILIA-ROMAGNA', 'ferrara': 'EMILIA-ROMAGNA',
    'reggio emilia': 'EMILIA-ROMAGNA', 'ravenna': 'EMILIA-ROMAGNA', 'forli': 'EMILIA-ROMAGNA',
    'forlì': 'EMILIA-ROMAGNA', 'imola': 'EMILIA-ROMAGNA', 'rimini': 'EMILIA-ROMAGNA',
    'padova': 'VENETO', 'padua': 'VENETO', 'legnaro': 'VENETO', 'verona': 'VENETO',
    'venezia': 'VENETO', 'venice': 'VENETO', 'treviso': 'VENETO', 'vicenza': 'VENETO',
    'conegliano': 'VENETO', 'rovigo': 'VENETO',
    'milano': 'LOMBARDIA', 'milan': 'LOMBARDIA', 'pavia': 'LOMBARDIA',
    'brescia': 'LOMBARDIA', 'bergamo': 'LOMBARDIA', 'cremona': 'LOMBARDIA',
    'mantova': 'LOMBARDIA', 'lodi': 'LOMBARDIA', 'sondrio': 'LOMBARDIA',
    'torino': 'PIEMONTE', 'turin': 'PIEMONTE', 'grugliasco': 'PIEMONTE',
    'alessandria': 'PIEMONTE', 'asti': 'PIEMONTE', 'cuneo': 'PIEMONTE',
    'novara': 'PIEMONTE', 'vercelli': 'PIEMONTE',
    'san michele': 'TRENTINO-ALTO ADIGE', "san michele all'adige": 'TRENTINO-ALTO ADIGE',
    'trento': 'TRENTINO-ALTO ADIGE', 'bolzano': 'TRENTINO-ALTO ADIGE',
    'bozen': 'TRENTINO-ALTO ADIGE', 'laimburg': 'TRENTINO-ALTO ADIGE',
    'pfatten': 'TRENTINO-ALTO ADIGE', 'vadena': 'TRENTINO-ALTO ADIGE',
    'udine': 'FRIULI-VENEZIA GIULIA', 'trieste': 'FRIULI-VENEZIA GIULIA',
    'gorizia': 'FRIULI-VENEZIA GIULIA', 'pordenone': 'FRIULI-VENEZIA GIULIA',
    'firenze': 'TOSCANA', 'florence': 'TOSCANA', 'pisa': 'TOSCANA', 'siena': 'TOSCANA',
    'grosseto': 'TOSCANA', 'arezzo': 'TOSCANA', 'lucca': 'TOSCANA',
    'perugia': 'UMBRIA', 'terni': 'UMBRIA',
    'ancona': 'MARCHE', 'macerata': 'MARCHE', 'ascoli piceno': 'MARCHE',
    'roma': 'LAZIO', 'rome': 'LAZIO', 'viterbo': 'LAZIO', 'latina': 'LAZIO',
    'napoli': 'CAMPANIA', 'naples': 'CAMPANIA', 'portici': 'CAMPANIA',
    'salerno': 'CAMPANIA', 'caserta': 'CAMPANIA', 'benevento': 'CAMPANIA',
    'bari': 'PUGLIA', 'foggia': 'PUGLIA', 'lecce': 'PUGLIA', 'valenzano': 'PUGLIA',
    'taranto': 'PUGLIA', 'brindisi': 'PUGLIA', 'turi': 'PUGLIA',
    'potenza': 'BASILICATA', 'matera': 'BASILICATA', 'metaponto': 'BASILICATA',
    'catanzaro': 'CALABRIA', 'reggio calabria': 'CALABRIA', 'rende': 'CALABRIA',
    'cosenza': 'CALABRIA', 'crotone': 'CALABRIA',
    'palermo': 'SICILIA', 'catania': 'SICILIA', 'messina': 'SICILIA',
    'acireale': 'SICILIA', 'ragusa': 'SICILIA', 'agrigento': 'SICILIA',
    'sassari': 'SARDEGNA', 'cagliari': 'SARDEGNA', 'oristano': 'SARDEGNA',
    'teramo': 'ABRUZZO', "l'aquila": 'ABRUZZO', 'chieti': 'ABRUZZO', 'pescara': 'ABRUZZO',
    'campobasso': 'MOLISE', 'aosta': "VALLE D'AOSTA", 'genova': 'LIGURIA',
    'sanremo': 'LIGURIA', 'la spezia': 'LIGURIA', 'savona': 'LIGURIA',
}

# Organização declarada na afiliação. A chave é a forma que APARECE na string; o valor é
# o nome canônico e o tipo. Sem casamento, `ORGANIZATION = NÃO SEI` — nome de cidade
# nunca vira organização, e prosa livre nunca decide papel.
ORG_CANONICA = [
    ('fondazione edmund mach', 'Fondazione Edmund Mach', 'RESEARCH_CENTRE'),
    ('edmund mach', 'Fondazione Edmund Mach', 'RESEARCH_CENTRE'),
    ('laimburg', 'Laimburg Research Centre', 'RESEARCH_CENTRE'),
    ('crea', 'CREA — Consiglio per la ricerca in agricoltura', 'PUBLIC_RESEARCH'),
    ('consiglio per la ricerca in agricoltura', 'CREA', 'PUBLIC_RESEARCH'),
    ('ipsp', 'CNR — Istituto per la Protezione Sostenibile delle Piante', 'PUBLIC_RESEARCH'),
    ('istituto di scienze delle produzioni alimentari', 'CNR — ISPA', 'PUBLIC_RESEARCH'),
    ('national research council', 'CNR', 'PUBLIC_RESEARCH'),
    ('consiglio nazionale delle ricerche', 'CNR', 'PUBLIC_RESEARCH'),
    ('università cattolica del sacro cuore', 'Università Cattolica del Sacro Cuore', 'UNIVERSITY'),
    ('catholic university of the sacred heart', 'Università Cattolica del Sacro Cuore', 'UNIVERSITY'),
    ('university of bologna', 'Università di Bologna', 'UNIVERSITY'),
    ('università di bologna', 'Università di Bologna', 'UNIVERSITY'),
    ('alma mater studiorum', 'Università di Bologna', 'UNIVERSITY'),
    ('university of padova', 'Università di Padova', 'UNIVERSITY'),
    ('university of padua', 'Università di Padova', 'UNIVERSITY'),
    ('università degli studi di padova', 'Università di Padova', 'UNIVERSITY'),
    ('university of turin', 'Università di Torino', 'UNIVERSITY'),
    ('università degli studi di torino', 'Università di Torino', 'UNIVERSITY'),
    ('university of milan', 'Università di Milano', 'UNIVERSITY'),
    ('università degli studi di milano', 'Università di Milano', 'UNIVERSITY'),
    ('university of naples', 'Università di Napoli Federico II', 'UNIVERSITY'),
    ('federico ii', 'Università di Napoli Federico II', 'UNIVERSITY'),
    ('university of bari', 'Università di Bari Aldo Moro', 'UNIVERSITY'),
    ('università degli studi di bari', 'Università di Bari Aldo Moro', 'UNIVERSITY'),
    ('university of catania', 'Università di Catania', 'UNIVERSITY'),
    ('university of palermo', 'Università di Palermo', 'UNIVERSITY'),
    ('university of pisa', 'Università di Pisa', 'UNIVERSITY'),
    ('university of florence', 'Università di Firenze', 'UNIVERSITY'),
    ('università degli studi di firenze', 'Università di Firenze', 'UNIVERSITY'),
    ('university of perugia', 'Università di Perugia', 'UNIVERSITY'),
    ('university of udine', 'Università di Udine', 'UNIVERSITY'),
    ('university of verona', 'Università di Verona', 'UNIVERSITY'),
    ('university of foggia', 'Università di Foggia', 'UNIVERSITY'),
    ('university of sassari', 'Università di Sassari', 'UNIVERSITY'),
    ('university of trento', 'Università di Trento', 'UNIVERSITY'),
    ('university of basilicata', 'Università della Basilicata', 'UNIVERSITY'),
    ('university of tuscia', 'Università della Tuscia', 'UNIVERSITY'),
    ('university of molise', 'Università del Molise', 'UNIVERSITY'),
    ('university of reggio calabria', 'Università Mediterranea di Reggio Calabria', 'UNIVERSITY'),
    ('scuola superiore sant', "Scuola Superiore Sant'Anna", 'UNIVERSITY'),
    ('iasma', 'Fondazione Edmund Mach (IASMA)', 'RESEARCH_CENTRE'),
    ('servizio fitosanitario', 'Servizio Fitosanitario Regionale', 'PLANT_HEALTH_SERVICE'),
    ('phytosanitary service', 'Servizio Fitosanitario Regionale', 'PLANT_HEALTH_SERVICE'),
    ('centro di saggio', 'Centro di Saggio', 'TRIAL_CENTRE'),
    ('council for agricultural research and economics', 'CREA', 'PUBLIC_RESEARCH'),
    ('marche polytechnic university', 'Università Politecnica delle Marche', 'UNIVERSITY'),
    ('polytechnic university of marche', 'Università Politecnica delle Marche', 'UNIVERSITY'),
    ('universita politecnica delle marche', 'Università Politecnica delle Marche', 'UNIVERSITY'),
    ('tuscia university', 'Università della Tuscia', 'UNIVERSITY'),
    ('sapienza', 'Sapienza Università di Roma', 'UNIVERSITY'),
    ('university of parma', 'Università di Parma', 'UNIVERSITY'),
    ('university of salento', 'Università del Salento', 'UNIVERSITY'),
    ('university of camerino', 'Università di Camerino', 'UNIVERSITY'),
    ('university of pavia', 'Università di Pavia', 'UNIVERSITY'),
    ('university of siena', 'Università di Siena', 'UNIVERSITY'),
    ('university of calabria', 'Università della Calabria', 'UNIVERSITY'),
    ('university of messina', 'Università di Messina', 'UNIVERSITY'),
    ('university of torino', 'Università di Torino', 'UNIVERSITY'),
    ('university of milano', 'Università di Milano', 'UNIVERSITY'),
    ('university of genoa', 'Università di Genova', 'UNIVERSITY'),
    ('university of cagliari', 'Università di Cagliari', 'UNIVERSITY'),
    ('university of teramo', 'Università di Teramo', 'UNIVERSITY'),
    ('university of bolzano', 'Libera Università di Bolzano', 'UNIVERSITY'),
    ('free university of bozen', 'Libera Università di Bolzano', 'UNIVERSITY'),
    ('disafa', 'Università di Torino — DISAFA', 'UNIVERSITY'),
    ('distal', 'Università di Bologna — DISTAL', 'UNIVERSITY'),
    ('dafnae', 'Università di Padova — DAFNAE', 'UNIVERSITY'),
    ('disaa', 'Università di Milano — DiSAA', 'UNIVERSITY'),
    ('cirve', 'CIRVE — Centro Interdipartimentale per la Ricerca in Viticoltura', 'UNIVERSITY'),
    ('ibbr', 'CNR — IBBR', 'PUBLIC_RESEARCH'),
    ('istituto zooprofilattico', 'Istituto Zooprofilattico Sperimentale', 'VETERINARY_PUBLIC_HEALTH'),
    ('enea', 'ENEA', 'PUBLIC_RESEARCH'),
    ('fondazione bruno kessler', 'Fondazione Bruno Kessler', 'RESEARCH_CENTRE'),
    ('barilla', 'Barilla G. e R. Fratelli S.p.A.', 'FOOD_INDUSTRY'),
    ('bbca', 'BBCA Onlus — Biological Control Agency', 'RESEARCH_CENTRE'),
    ('agrion', 'Fondazione Agrion', 'RESEARCH_CENTRE'),
    ('mach', 'Fondazione Edmund Mach', 'RESEARCH_CENTRE'),
]

# --------------------------------------------------------------- o portão agronômico
# MEDIDO NESTA MISSÃO, e é a mesma armadilha que o repositório já pagou uma vez: consulta
# técnica traz OUTRA POPULAÇÃO com cara de sucesso. Aqui, `aflatoxin`, `deoxynivalenol`,
# `Monilinia` e `fungicide resistance` puxaram para dentro do corpus italiano:
#
#     IBD unit - Digestive Disease Center (CeMAD), Policlinico Gemelli        12 autores
#     Human Nutrition Unit, Department of Food and Drug, University of Parma   8 autores
#     Department of Veterinary Sciences, University of Messina                 7 autores
#     Istituto Zooprofilattico Sperimentale dell'Umbria e delle Marche         8 autores
#
# São autores reais, italianos, do assunto — e NÃO são sensores agrícolas. Gastroenterologia
# publica sobre micotoxina porque a micotoxina chega ao paciente, não porque alguém olhou
# a lavoura.
#
# O portão é POSITIVO: a afiliação precisa DECLARAR domínio agronômico. Ausência de marcador
# não vira "provavelmente agrícola" — vira `AGRO_AFFILIATION = NOT_DECLARED`, e a pessoa
# não é promovida. Esta é a regra do modelo de identidade aplicada à afiliação: o papel sai
# de campo declarado, nunca do assunto do trabalho.
MARCADORES_AGRO = (
    'agricultur', 'agrar', 'agro', 'agronom', 'plant protection', 'plant patholog',
    'plant scien', 'crop scien', 'entomolog', 'phytopatholog', 'fitopatolog',
    'viticultur', 'viticolt', 'enolog', 'oenolog', 'horticultur', 'orticolt',
    'forest', 'sustainable plant protection', 'edmund mach', 'laimburg', 'crea',
    'council for agricultural research', 'servizio fitosanitario', 'phytosanitary',
    'centro di saggio', 'disafa', 'distal', 'dafnae', 'disaa', 'cirve', 'agrion',
    'weed scien', 'soil scien', 'food and environmental scien', 'ibbr',
    'produzioni vegetali', 'scienze agrarie', 'protezione delle piante',
    # ------------------------------------------------------------------ correção medida
    # A primeira versão do portão barrou três nomes que esta camada existe para achar,
    # e o motivo em cada caso foi a FORMA da afiliação, não o domínio:
    #
    #   Vittorio Rossi   "Department of Sustainable CROP PRODUCTION" e "Research Center
    #                    for PLANT HEALTH Modelling" — o departamento que constrói os
    #                    modelos de previsão de doença italianos (Piacenza)
    #   A. F. Logrieco   "Institute of Sciences of Food Production (ISPA)" do CNR — a
    #                    referência italiana de micotoxina em cereal
    #
    # Os termos abaixo são específicos e não abrem a porta para clínica: nenhum
    # departamento médico se chama "crop production" ou "plant health".
    'crop production', 'crop protection', 'plant health', 'ispa',
)

# Marcador que, sozinho, NÃO sustenta sensor agrícola. Só desqualifica quando NENHUM
# marcador agronômico está presente — coautoria entre agronomia e medicina existe e é
# legítima; o que não pode é uma unidade puramente clínica virar sensor de campo.
MARCADORES_NAO_AGRO = (
    'digestive disease', 'gastroenterol', 'human nutrition', 'veterinary',
    'zooprofilattico', 'policlinico', 'medicine', 'medical', 'pharmac', 'dental',
    'hospital', 'oncolog', 'cardiolog', 'psychiatr', 'nursing', 'radiolog',
    'occupational', 'epidemiology and hygiene', 'biomorf', 'irccs',
)


def agro_declarado(afiliacoes):
    """→ (ESTADO, motivo). Portão positivo: precisa DECLARAR domínio agronômico."""
    n = ' ; '.join(_norm(a) for a in (afiliacoes or []))
    tem = sorted({m for m in MARCADORES_AGRO if m in n})
    nao = sorted({m for m in MARCADORES_NAO_AGRO if m in n})
    if tem:
        return 'DECLARED', 'marcadores: %s' % ', '.join(tem[:4])
    if nao:
        return 'NOT_DECLARED_NON_AGRO', 'afiliação declara domínio não agrícola: %s' % ', '.join(nao[:3])
    return 'NOT_DECLARED', 'nenhum marcador agronômico na afiliação declarada'


def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def regiao_de(afil):
    """Região a partir da CIDADE declarada na afiliação. Sem cidade conhecida: NÃO SEI."""
    n = _norm(afil)
    achadas = {r for c, r in CIDADE_REGIAO.items() if re.search(r'\b%s\b' % re.escape(_norm(c)), n)}
    if len(achadas) == 1:
        return achadas.pop(), 'INSTITUTION_ADDRESS_DECLARED_IN_AFFILIATION'
    if len(achadas) > 1:
        # Afiliação múltipla no mesmo campo. Ambíguo é um ESTADO, não um empate a desfazer.
        return 'AMBIGUOUS:' + '|'.join(sorted(achadas)), 'MULTIPLE_CITIES_IN_AFFILIATION'
    return 'NÃO SEI', 'NO_KNOWN_CITY_IN_AFFILIATION'


def org_de(afil):
    n = _norm(afil)
    for chave, canon, tipo in ORG_CANONICA:
        if _norm(chave) in n:
            return canon, tipo
    return 'NÃO SEI', 'NÃO SEI'


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'SintoniaEAME/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode('utf-8')), None
    except urllib.error.HTTPError as e:
        return None, 'HTTP %d' % e.code
    except Exception as e:                                               # noqa: BLE001
        return None, type(e).__name__


def buscar_recorte(termo, crop, issue):
    q = '(%s) AND AFF:"Italy" AND FIRST_PDATE:%s' % (termo, JANELA)
    pessoas, obras, cursor, pags, motivo, hits = {}, 0, '*', 0, None, None
    while cursor and pags < PAGINAS_MAX:
        url = '%s?%s' % (API, urllib.parse.urlencode({
            'query': q, 'format': 'json', 'resultType': 'core',
            'pageSize': POR_PAGINA, 'cursorMark': cursor}))
        d, err = _get(url)
        if err:
            motivo = err
            break
        if hits is None:
            hits = d.get('hitCount')
        pags += 1
        itens = (d.get('resultList') or {}).get('result') or []
        if not itens:
            break
        obras += len(itens)
        for w in itens:
            ano = w.get('pubYear')
            data = w.get('firstPublicationDate') or ''
            for a in ((w.get('authorList') or {}).get('author') or []):
                afs = [x.get('affiliation') or '' for x in
                       ((a.get('authorAffiliationDetailsList') or {}).get('authorAffiliation') or [])]
                # Só entra quem declara afiliação NA ITÁLIA neste trabalho. Coautor
                # estrangeiro num paper italiano não vira pesquisador italiano.
                it = [x for x in afs if re.search(r'\bital(y|ia)\b', _norm(x))]
                if not it:
                    continue
                nome = a.get('fullName') or ''
                dado = (a.get('firstName'), a.get('lastName'))
                if not dado[1]:
                    continue                        # sem sobrenome não há pessoa
                chave = _norm('%s|%s' % (dado[0] or '', dado[1]))
                p = pessoas.setdefault(chave, {
                    'NAME': ('%s %s' % (dado[0] or '', dado[1])).strip(),
                    'NAME_AS_INDEXED': nome,
                    'ORCID': (a.get('authorId') or {}).get('value')
                             if (a.get('authorId') or {}).get('type') == 'ORCID' else None,
                    'WORKS_IN_SCOPE': 0, 'AFFILIATIONS': defaultdict(int),
                    'LAST_YEAR': None, 'LAST_DATE': None, 'SCOPES': set(),
                    'WORK_IDS': [],
                })
                if not p['ORCID'] and (a.get('authorId') or {}).get('type') == 'ORCID':
                    p['ORCID'] = (a.get('authorId') or {}).get('value')
                p['WORKS_IN_SCOPE'] += 1
                p['SCOPES'].add('%s|%s' % (crop, issue))
                if len(p['WORK_IDS']) < 6:
                    p['WORK_IDS'].append({'ID': w.get('id'), 'SOURCE': w.get('source'),
                                          'DOI': w.get('doi'), 'TITLE': w.get('title'),
                                          'DATE': data})
                try:
                    ano_i = int(ano)
                except (TypeError, ValueError):
                    ano_i = None
                if ano_i and (p['LAST_YEAR'] is None or ano_i > p['LAST_YEAR']):
                    p['LAST_YEAR'] = ano_i
                if data and (p['LAST_DATE'] is None or data > p['LAST_DATE']):
                    p['LAST_DATE'] = data
                for x in it:
                    p['AFFILIATIONS'][x.strip()] += 1
        cursor = d.get('nextCursorMark')
        time.sleep(PAUSA)
    estado = THROTTLED if motivo in ('HTTP 429', 'HTTP 503') else (FAILED if motivo else OK)
    return {
        'TERM': termo, 'CROP': crop, 'ISSUE': issue, 'STATE': estado, 'REASON': motivo,
        'HITS_REPORTED': hits,
        'WORKS_TRAVERSED': obras if estado == OK else None,
        'AUTHORS_FOUND': len(pessoas) if estado == OK else None,
        'PAGES_READ': pags, 'PEOPLE': pessoas,
    }


def buscar():
    os.makedirs(RAW, exist_ok=True)
    escopos, agg = [], {}
    for chave, termo, crop, issue in RECORTES_IT:
        r = buscar_recorte(termo, crop, issue)
        print('%-20s %-22s hits=%-6s obras=%-5s pessoas=%-5s %s' % (
            chave, r['STATE'], r['HITS_REPORTED'], r['WORKS_TRAVERSED'],
            r['AUTHORS_FOUND'], r['REASON'] or ''))
        for k, p in r.pop('PEOPLE').items():
            g = agg.setdefault(k, {
                'NAME': p['NAME'], 'ORCID': p['ORCID'], 'WORKS_IN_SCOPE': 0,
                'AFFILIATIONS': defaultdict(int), 'LAST_YEAR': None, 'LAST_DATE': None,
                'SCOPES': set(), 'WORK_IDS': [],
            })
            g['ORCID'] = g['ORCID'] or p['ORCID']
            g['WORKS_IN_SCOPE'] += p['WORKS_IN_SCOPE']
            g['SCOPES'] |= p['SCOPES']
            for w in p['WORK_IDS']:
                if len(g['WORK_IDS']) < 8 and w['ID'] not in [x['ID'] for x in g['WORK_IDS']]:
                    g['WORK_IDS'].append(w)
            if p['LAST_YEAR'] and (g['LAST_YEAR'] is None or p['LAST_YEAR'] > g['LAST_YEAR']):
                g['LAST_YEAR'] = p['LAST_YEAR']
            if p['LAST_DATE'] and (g['LAST_DATE'] is None or p['LAST_DATE'] > g['LAST_DATE']):
                g['LAST_DATE'] = p['LAST_DATE']
            for a, n in p['AFFILIATIONS'].items():
                g['AFFILIATIONS'][a] += n
        r['SCOPE_KEY'] = chave
        escopos.append(r)

    pessoas = []
    for g in agg.values():
        afs = sorted(g['AFFILIATIONS'].items(), key=lambda kv: (-kv[1], kv[0]))
        principal = afs[0][0] if afs else ''
        org, tipo = org_de(principal)
        reg, base = regiao_de(principal)
        pessoas.append({
            'NAME': g['NAME'], 'ORCID': g['ORCID'],
            'WORKS_IN_SCOPE': g['WORKS_IN_SCOPE'],
            'LAST_YEAR': g['LAST_YEAR'], 'LAST_DATE': g['LAST_DATE'],
            'AFFILIATION_PRIMARY': principal,
            'AFFILIATIONS_DISTINCT': len(afs),
            'AFFILIATIONS': [a for a, _ in afs[:5]],
            'ORGANIZATION': org, 'ORGANIZATION_TYPE': tipo,
            'REGION': reg, 'REGION_BASIS': base,
            'SCOPES': sorted(g['SCOPES']),
            'WORKS': g['WORK_IDS'],
        })
    pessoas.sort(key=lambda p: (-p['WORKS_IN_SCOPE'], p['NAME']))

    corpo = {
        'SOURCE_ID': 'SENSOR-HUMANO-IT/EPMC',
        'source': 'Europe PMC REST (ebi.ac.uk/europepmc), rota gratuita, sem chave',
        'SOURCE_LOCATION': 'global — índice bibliográfico',
        'FACT_LOCATION': 'NÃO SEI — afiliação do autor não é geografia do estudo',
        'ORIGINAL_LANGUAGE': 'EN',
        'COUNTRY_FILTER': 'AFF:"Italy" — afiliação declarada, não nacionalidade',
        'WINDOW': JANELA,
        'REPLACES': 'OpenAlex — FAILED_WITH_REASON: orçamento diário zerado (HTTP 429, '
                    '"Insufficient budget", retryAfter 49093s), medido 2026-09-04',
        'RATE_LIMIT_POLICY': 'pausa %.1fs · teto %d páginas · %d por página' % (
            PAUSA, PAGINAS_MAX, POR_PAGINA),
        'SCOPES': escopos,
        'SCOPES_THROTTLED': [s['SCOPE_KEY'] for s in escopos if s['STATE'] == THROTTLED],
        'SCOPES_FAILED': [s['SCOPE_KEY'] for s in escopos if s['STATE'] == FAILED],
        'PEOPLE_COUNT': len(pessoas),
        'PEOPLE': pessoas,
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    caminho = os.path.join(RAW, 'epmc-IT.json')
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('\n%d pessoas -> %s' % (len(pessoas), caminho))
    return corpo


def resumo():
    with open(os.path.join(RAW, 'epmc-IT.json'), encoding='utf-8') as f:
        d = json.load(f)
    print('%d pessoas · estrangulados %s · falhos %s' % (
        d['PEOPLE_COUNT'], d['SCOPES_THROTTLED'] or 'nenhum', d['SCOPES_FAILED'] or 'nenhum'))
    for p in d['PEOPLE'][:30]:
        print('  %-30s %3d  %-5s %-22s %s' % (
            p['NAME'][:30], p['WORKS_IN_SCOPE'], 'ORCID' if p['ORCID'] else '  -  ',
            p['REGION'][:22], p['ORGANIZATION'][:40]))


if __name__ == '__main__':
    {'buscar': buscar, 'resumo': resumo}[sys.argv[1] if len(sys.argv) > 1 else 'resumo']()
