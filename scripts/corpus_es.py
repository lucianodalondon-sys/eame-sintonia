#!/usr/bin/env python3
"""
CORPUS CIENTÍFICO E DE PESSOAS — ESPANHA (ES-T5/T6).

Constrói o universo espanhol de ciência agrícola a partir do OpenAlex, que é a única
âncora de identidade que temos com ORCID, instituição declarada e país — os três campos
sem os quais o modelo de voz proíbe atribuir papel a alguém.

**A regra que este script existe para respeitar:** papel NUNCA é inferido. Um autor entra
como `RESEARCHER` porque a base declara a afiliação institucional dele, não porque escreve
sobre agricultura.

    python3 scripts/corpus_es.py buscar    # varre os temas e grava o corpus bruto
    python3 scripts/corpus_es.py resumo    # lê o corpus gravado e resume

Universo de busca, declarado (é o que permite auditar como chegamos à amostra):
  · base: OpenAlex (api.openalex.org), sem chave
  · filtro de país: instituição de qualquer autor em ES
  · janela: 2019–2026
  · termos: ver TEMAS abaixo, cada um com CROP e ISSUE explícitos
  · exclusão: trabalhos sem instituição espanhola declarada
  · deduplicação: por OpenAlex work id
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'raw', 'ES-T5-002')
API = 'https://api.openalex.org/works'
MAILTO = 'sintonia-eame@example.invalid'      # polite pool do OpenAlex
YEARS = '2019-2026'

# (chave, termo de busca, CROP, ISSUE) — o CROP e o ISSUE são declarados por nós na
# consulta, não adivinhados do texto. É o que torna a linha auditável.
TEMAS = [
    ('repilo',        '"Venturia oleaginea" OR "Spilocaea oleagina" OR repilo', 'OLIVE', 'REPILO'),
    ('olive_disease', '"olive" AND ("disease" OR "pathogen" OR "fungicide")',   'OLIVE', 'OLIVE_DISEASE'),
    ('xylella',       '"Xylella fastidiosa" AND olive',                          'OLIVE', 'XYLELLA'),
    ('verticillium',  '"Verticillium dahliae" AND olive',                        'OLIVE', 'VERTICILLIUM'),
    ('tuberculosis',  '"Pseudomonas savastanoi" OR "olive knot"',                'OLIVE', 'OLIVE_KNOT'),
    ('septoria',      '"Zymoseptoria tritici" OR "Septoria tritici"',            'CEREAL', 'SEPTORIA'),
    ('cereal_disease','wheat AND ("fungicide" OR "rust" OR "powdery mildew")',   'CEREAL', 'CEREAL_DISEASE'),
    ('mildiu_vid',    '"Plasmopara viticola"',                                   'VINE', 'DOWNY_MILDEW'),
    ('resistencia',   '"fungicide resistance" OR "herbicide resistance"',        'MULTI', 'RESISTANCE'),
    ('malas_hierbas', '"weed control" AND (olive OR cereal OR vineyard)',        'MULTI', 'WEEDS'),
    ('entomologia',   '"Bactrocera oleae" OR "olive fruit fly" OR "Prays oleae"','OLIVE', 'OLIVE_PESTS'),
    ('sanidad',       '"plant health" AND Spain',                                'MULTI', 'PLANT_HEALTH'),
]


def _get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': f'SintoniaEAME (mailto:{MAILTO})'})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:                                   # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(2 ** i)


def buscar(por_tema=200):
    os.makedirs(DEST, exist_ok=True)
    obras = {}
    log = []
    for chave, termo, crop, issue in TEMAS:
        f = f'institutions.country_code:es,publication_year:{YEARS}'
        url = (f'{API}?filter={urllib.parse.quote(f)}'
               f'&search={urllib.parse.quote(termo)}'
               f'&per-page=200&mailto={MAILTO}')
        d = _get(url)
        n = d['meta']['count']
        got = 0
        for w in d['results'][:por_tema]:
            wid = w['id']
            if wid not in obras:
                obras[wid] = {'work': w, 'temas': []}
            obras[wid]['temas'].append({'tema': chave, 'crop': crop, 'issue': issue})
            got += 1
        log.append({'tema': chave, 'termo': termo, 'crop': crop, 'issue': issue,
                    'universo_openalex': n, 'coletados': got})
        print(f'  {chave:<16} universo {n:>6}  coletados {got:>3}  ({crop} × {issue})')
        time.sleep(0.3)
    with open(os.path.join(DEST, 'openalex_works.json'), 'w', encoding='utf-8') as fh:
        json.dump({'search_universe': log, 'years': YEARS, 'country': 'ES',
                   'captured_at': time.strftime('%Y-%m-%d'),
                   'works': list(obras.values())}, fh, ensure_ascii=False)
    print(f'\ntrabalhos distintos: {len(obras)}')
    return obras


def carregar():
    with open(os.path.join(DEST, 'openalex_works.json'), encoding='utf-8') as fh:
        return json.load(fh)


def pessoas(d):
    """Autores com afiliação espanhola DECLARADA no próprio registro do trabalho."""
    p = defaultdict(lambda: {'works': [], 'orgs': Counter(), 'crops': Counter(),
                             'issues': Counter(), 'years': [], 'orcid': None})
    for item in d['works']:
        w = item['work']
        crops = {t['crop'] for t in item['temas']}
        issues = {t['issue'] for t in item['temas']}
        for a in w.get('authorships', []):
            insts = [i for i in a.get('institutions', []) if i.get('country_code') == 'ES']
            if not insts:
                continue
            au = a['author']
            k = au['id']
            p[k]['name'] = au.get('display_name')
            p[k]['orcid'] = p[k]['orcid'] or au.get('orcid')
            p[k]['works'].append({'id': w['id'], 'title': w.get('title'),
                                  'year': w.get('publication_year'), 'doi': w.get('doi')})
            p[k]['years'].append(w.get('publication_year'))
            for i in insts:
                p[k]['orgs'][i['display_name']] += 1
            for c in crops:
                p[k]['crops'][c] += 1
            for i in issues:
                p[k]['issues'][i] += 1
    return p


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'resumo'
    if cmd == 'buscar':
        buscar()
    else:
        d = carregar()
        p = pessoas(d)
        print('trabalhos:', len(d['works']), '| autores com afiliação ES:', len(p))
        top = sorted(p.items(), key=lambda kv: -len(kv[1]['works']))[:25]
        for k, v in top:
            print(f"  {len(v['works']):>3}  {v['name'][:34]:<36} {v['orgs'].most_common(1)[0][0][:40]}")
