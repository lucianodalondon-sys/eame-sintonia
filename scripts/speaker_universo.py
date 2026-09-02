#!/usr/bin/env python3
"""
UNIVERSO DE SPEAKERS TÉCNICOS — IT e FR, pela rota gratuita (OpenAlex).

Este script existe para uma missão só: montar a lista de PESSOAS que entram no piloto
EARLY SIGNAL antes de qualquer execução paga. Ele **não coleta voz pública**. Ele resolve
identidade, que é o que a casa exige antes de olhar conteúdo:

    PERSON primeiro. CANAL depois. POST por último.

POR QUE ELE NÃO É O `corpus_es.py`
-----------------------------------
O `corpus_es.py` monta o corpus **de documentos** espanhol. Aqui o produto é outro: a
unidade de saída é a **pessoa**, com âncora técnica verificável, e o documento é só o
caminho até ela. Reaproveitar aquele script obrigaria a mudá-lo para produzir duas coisas,
e a segunda divergiria na primeira pressa.

A LEI QUE ESTE ARQUIVO OBEDECE, E QUE JÁ CUSTOU UMA MEDIÇÃO
------------------------------------------------------------
`CROP` e `ISSUE` saem da CONSULTA que trouxe o trabalho, nunca de leitura livre do título.
O motivo está medido em `EU-T5-001-openalex-people.json`, no bloco `spain_query_drift`:

    "wheat septoria OR Zymoseptoria"   -> 2.627 obras, e os autores do topo são de
                                         fisiologia de cultura e sensoriamento remoto
    "Zymoseptoria tritici"             ->    27 obras, e os autores são da doença

    razão: 97,3x

Consulta frouxa não traz mais do mesmo. Traz **outra população**, com cara de sucesso.
Por isso todo termo aqui é aspeado ou conjuntivo, e nunca uma palavra solta.

O 429 QUE APAGAVA TRABALHO — corrigido no piloto italiano, repetido aqui de propósito
--------------------------------------------------------------------------------------
O coletor italiano deixava o 429 escapar e matar o processo, levando junto os recortes já
coletados NAQUELA execução. O efeito é pior que perder trabalho:

    um recorte que SOME do artefato é indistinguível de um que devolveu ZERO pesquisadores

Aqui o recorte estrangulado sai com `STATE = THROTTLED_NOT_EMPTY` e contagem `None`, nunca
`0`. É a lei `SOURCE FAILURE != ZERO` aplicada ao próprio coletor.

E a causa medida lá foi **rajada, não volume diário**: paginar de 100 em 100 a cada 1,6 s
derrubou o IP inteiro por mais de oito horas. Por isso `PAUSA` é folgada e o teto de
páginas é baixo. Coletar devagar é o que mantém a rota viva.

AFILIAÇÃO NÃO É GEOGRAFIA DO ESTUDO
------------------------------------
`institutions.country_code` filtra por afiliação do AUTOR. Um trabalho sobre olivar
marroquino assinado em Córdoba continua Córdoba. Nenhum campo daqui afirma onde o
experimento foi feito, e `FACT_LOCATION` sai como `NÃO SEI` por contrato.

    python3 scripts/speaker_universo.py buscar IT
    python3 scripts/speaker_universo.py buscar FR
    python3 scripts/speaker_universo.py resumo IT
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'raw', 'SPEAKER-UNIVERSO')
API = 'https://api.openalex.org/works'
MAILTO = 'sintonia-eame@example.invalid'      # polite pool do OpenAlex

# Janela deliberadamente curta. O piloto pergunta quem fala HOJE, e um autor com obra
# forte em 2019 e silêncio desde 2022 não é candidato a sensor cotidiano.
YEARS = '2022-2026'

PAUSA = 3.0          # segundos entre chamadas — a rajada é o que derruba o IP
PAGINAS_MAX = 2      # teto por recorte; piloto é pequeno por decisão, não por limite
POR_PAGINA = 200

THROTTLED = 'THROTTLED_NOT_EMPTY'
OK = 'COLLECTED'
FAILED = 'FAILED_WITH_REASON'

# ---------------------------------------------------------------------------- recortes
# (chave, termo, CROP, ISSUE). Os recortes italianos são EXATAMENTE os quatro que o piloto
# italiano declarou `NOT_COLLECTED` por estrangulamento — não recortes novos inventados
# aqui. Fechar a lacuna que já está escrita vale mais que abrir outra.
RECORTES = {
    # Espanha: os DOIS recortes congelados pelo árbitro, e só eles. A fila espanhola que
    # já existe no repositório (`RESEARCHER-PUBLIC-VOICE-QUEUE-ES`) cobre olivar, mas foi
    # construída com âncora de olivar inteira — não serve para septoriose em trigo, que é
    # o segundo recorte congelado e é justamente onde a voz falta.
    'ES': [
        ('olive_repilo', '"Venturia oleaginea" OR "Spilocaea oleagina" OR "peacock spot" '
                         'OR repilo', 'OLIVE', 'REPILO'),
        ('cereal_septoria', '"Zymoseptoria tritici" OR "Septoria tritici"',
         'CEREAL', 'SEPTORIA'),
    ],
    'IT': [
        ('vine_flavescence', '"flavescence doree" OR ("grapevine" AND "phytoplasma")',
         'VINE', 'FLAVESCENCE'),
        ('durum_fusarium', '("durum wheat" OR "Triticum durum") AND "Fusarium"',
         'DURUM_WHEAT', 'FUSARIUM'),
        ('olive_bactrocera', '"Bactrocera oleae" OR "olive fruit fly"',
         'OLIVE', 'OLIVE_PESTS'),
        ('maize_borer', '("Ostrinia nubilalis" OR "Diabrotica virgifera") AND (maize OR corn)',
         'MAIZE', 'MAIZE_PESTS'),
        ('maize_mycotoxin', '(maize OR corn) AND ("Fusarium" OR "aflatoxin" OR "mycotoxin")',
         'MAIZE', 'MYCOTOXIN'),
    ],
    # A França é o país mais magro do acervo: `EU-T5-001` só tem UM recorte francês, com
    # 4 autores de 3+ obras. Os recortes abaixo saem do que o repositório já declarou que
    # importa na França — milho (6,7x a área espanhola), cereal de inverno e resistência a
    # herbicida (a rota por onde Christophe Délye já apareceu).
    'FR': [
        ('herbicide_resistance', '"herbicide resistance" OR "herbicide-resistant weeds"',
         'MULTI', 'HERBICIDE_RESISTANCE'),
        ('cereal_septoria', '"Zymoseptoria tritici" OR "Septoria tritici"',
         'CEREAL', 'SEPTORIA'),
        ('vine_mildew', '"Plasmopara viticola"',
         'VINE', 'DOWNY_MILDEW'),
        ('maize_pests', '("Ostrinia nubilalis" OR "Diabrotica virgifera") AND (maize OR corn)',
         'MAIZE', 'MAIZE_PESTS'),
        ('cereal_rust', '("Puccinia triticina" OR "Puccinia striiformis") AND wheat',
         'CEREAL', 'RUST'),
    ],
}


def _url(termo, pais, cursor):
    filtro = ','.join([
        'institutions.country_code:%s' % pais.lower(),
        'publication_year:%s' % YEARS,
        'title_and_abstract.search:%s' % termo,
    ])
    return '%s?%s' % (API, urllib.parse.urlencode({
        'filter': filtro, 'per-page': POR_PAGINA, 'cursor': cursor, 'mailto': MAILTO,
    }))


def _get(url):
    """→ (json, None) ou (None, motivo). NUNCA levanta: 429 não pode matar o processo."""
    req = urllib.request.Request(
        url, headers={'User-Agent': 'SintoniaEAME (mailto:%s)' % MAILTO})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode('utf-8')), None
    except urllib.error.HTTPError as e:
        return None, ('HTTP %d' % e.code)
    except Exception as e:                                   # noqa: BLE001
        return None, ('%s' % type(e).__name__)


def buscar_recorte(termo, pais, crop, issue):
    """Um recorte. Devolve autores com afiliação no país, e o ESTADO do recorte."""
    autores, obras, cursor, paginas, motivo = {}, 0, '*', 0, None
    while cursor and paginas < PAGINAS_MAX:
        d, err = _get(_url(termo, pais, cursor))
        if err:
            # SOURCE FAILURE != ZERO. O recorte sai sem contagem, não com zero.
            motivo = err
            break
        paginas += 1
        itens = d.get('results') or []
        obras += len(itens)
        for w in itens:
            ano = w.get('publication_year')
            for a in (w.get('authorships') or []):
                au = a.get('author') or {}
                aid = au.get('id')
                if not aid:
                    continue
                # Só conta quem declara afiliação NO PAÍS neste trabalho. Coautor
                # estrangeiro num paper italiano não vira pesquisador italiano.
                paises = [c.upper() for c in (a.get('countries') or [])]
                insts = [i for i in (a.get('institutions') or [])
                         if (i.get('country_code') or '').upper() == pais.upper()]
                if pais.upper() not in paises and not insts:
                    continue
                r = autores.setdefault(aid, {
                    'PERSON_ID': aid, 'NAME': au.get('display_name'),
                    'ORCID': au.get('orcid'), 'WORKS_IN_SCOPE': 0,
                    'INSTITUTIONS': {}, 'LAST_YEAR': None, 'SCOPES': set(),
                })
                r['WORKS_IN_SCOPE'] += 1
                r['SCOPES'].add('%s|%s' % (crop, issue))
                if ano and (r['LAST_YEAR'] is None or ano > r['LAST_YEAR']):
                    r['LAST_YEAR'] = ano
                for i in insts:
                    nome = i.get('display_name')
                    if nome:
                        r['INSTITUTIONS'][nome] = r['INSTITUTIONS'].get(nome, 0) + 1
        cursor = (d.get('meta') or {}).get('next_cursor')
        time.sleep(PAUSA)
    estado = THROTTLED if motivo == 'HTTP 429' else (FAILED if motivo else OK)
    return {
        'TERM': termo, 'CROP': crop, 'ISSUE': issue, 'COUNTRY': pais,
        'STATE': estado,
        'REASON': motivo,
        # A contagem só existe quando o recorte fechou. Estrangulado sai None, nunca 0.
        'WORKS_TRAVERSED': obras if estado == OK else None,
        'AUTHORS_FOUND': len(autores) if estado == OK else None,
        'PAGES_READ': paginas,
        'AUTHORS': autores,
    }


def buscar(pais):
    os.makedirs(DEST, exist_ok=True)
    saida, agregado = [], {}
    for chave, termo, crop, issue in RECORTES[pais]:
        r = buscar_recorte(termo, pais, crop, issue)
        print('%-22s %-22s obras=%-6s autores=%-6s %s' % (
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
        time.sleep(PAUSA)

    pessoas = []
    for g in agregado.values():
        insts = sorted(g['INSTITUTIONS'].items(), key=lambda kv: (-kv[1], kv[0]))
        pessoas.append({
            'PERSON_ID': g['PERSON_ID'], 'NAME': g['NAME'], 'ORCID': g['ORCID'],
            'WORKS_IN_SCOPE': g['WORKS_IN_SCOPE'],
            'LAST_YEAR': g['LAST_YEAR'],
            'INSTITUTION': insts[0][0] if insts else 'NÃO SEI',
            'ALL_INSTITUTIONS_COUNT': len(insts),
            'SCOPES': sorted(g['SCOPES']),
        })
    pessoas.sort(key=lambda p: (-p['WORKS_IN_SCOPE'], p['NAME'] or ''))

    corpo = {
        'SOURCE_ID': 'SPEAKER-UNIVERSO-%s' % pais,
        'source': 'OpenAlex (api.openalex.org), rota REST gratuita, sem chave',
        'SOURCE_LOCATION': 'global — índice bibliográfico',
        'FACT_LOCATION': 'NÃO SEI — a afiliação é do AUTOR, não do estudo',
        'ORIGINAL_LANGUAGE': 'EN',
        'COUNTRY_OF_AFFILIATION': pais,
        'WINDOW': YEARS,
        'METHOD': ('filter=institutions.country_code + publication_year + '
                   'title_and_abstract.search; CROP e ISSUE vêm da CONSULTA'),
        'RATE_LIMIT_POLICY': 'pausa de %.1fs, teto de %d páginas por recorte' % (
            PAUSA, PAGINAS_MAX),
        'SCOPES': saida,
        'SCOPES_THROTTLED': [s['SCOPE_KEY'] for s in saida if s['STATE'] == THROTTLED],
        'PEOPLE_COUNT': len(pessoas),
        'PEOPLE': pessoas,
    }
    caminho = os.path.join(DEST, 'universo-%s.json' % pais)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('\n%d pessoas -> %s' % (len(pessoas), caminho))
    return corpo


def resumo(pais):
    with open(os.path.join(DEST, 'universo-%s.json' % pais), encoding='utf-8') as f:
        d = json.load(f)
    print('%s · %d pessoas · recortes estrangulados: %s' % (
        pais, d['PEOPLE_COUNT'], d['SCOPES_THROTTLED'] or 'nenhum'))
    for p in d['PEOPLE'][:25]:
        print('  %-34s %-2s obras  %s  %s' % (
            (p['NAME'] or '')[:34], p['WORKS_IN_SCOPE'],
            'ORCID' if p['ORCID'] else '  -  ', (p['INSTITUTION'] or '')[:44]))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'resumo'
    pais = (sys.argv[2] if len(sys.argv) > 2 else 'IT').upper()
    {'buscar': buscar, 'resumo': resumo}[cmd](pais)
