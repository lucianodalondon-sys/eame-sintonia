#!/usr/bin/env python3
"""
ITÁLIA — o universo de pesquisadores, construído a partir dos casos e não de uma cota.

A pergunta NÃO é "quem são os 20 maiores pesquisadores italianos". Essa pergunta produz
uma lista de celebridades e nenhuma decisão. A pergunta é: **dentro dos pares
cultura×problema que a medição já elegeu, quem publica com recorrência e ainda está
ativo.** As pessoas saem dos trabalhos; a cota não existe.

    CROP × ISSUE  →  PAPER  →  AUTHOR  →  RECORRÊNCIA  →  ORCID  →  INSTITUIÇÃO/ROR

CAUTELAS HERDADAS, cada uma paga com uma medição na Espanha:

  · `REGION_OF_STUDY ≠ AUTHOR AFFILIATION`. A afiliação diz onde a pessoa trabalha, não
    onde o fenômeno ocorre. Este módulo publica AFILIAÇÃO e nunca a chama de região do
    fato. `INSTITUTION_REGION` existe; `FACT_REGION` não é derivado dele.
  · **`OpenAlex author ID pode conflacionar homônimos`** — medido lá em 58 organizações.
    ORCID é publicado por pessoa, e quem não tem sai como identidade fraca.
  · **Consulta dirigida, nunca paginação larga.** O denominador é o recorte, e o recorte
    viaja junto com o número.
  · **`RESEARCH AUTHORITY ≠ PUBLIC REACH`.** Seguidor não entra aqui, nem como campo.

`ROR` vem do próprio OpenAlex quando ele o declara — é o identificador estável da
instituição, e sem ele o nome da instituição é só uma string.
"""
import collections
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

API = 'https://api.openalex.org/works'
MAILTO = 'sintonia-eame@research.example'
DESDE = '2019-01-01'
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-T5-001', 'ITALY-RESEARCHER-UNIVERSE.json')

# Os recortes vêm dos casos JÁ MEDIDOS, não de curiosidade temática.
ESCOPOS = {
    'VINE_FLAVESCENCE': {
        'CASE': 'IT-HERO-001', 'CROP': 'Videira',
        'ISSUE': 'Flavescência dourada / Scaphoideus titanus',
        'Q': 'grapevine AND (phytoplasma OR flavescence OR Scaphoideus)'},
    'MAIZE_BORER_DIABROTICA': {
        'CASE': 'IT-HERO-002', 'CROP': 'Milho',
        'ISSUE': 'Piralide / Diabrotica',
        'Q': '(maize OR corn) AND (Ostrinia OR "corn borer" OR Diabrotica)'},
    'MAIZE_MYCOTOXIN': {
        'CASE': 'IT-HERO-002 (contexto)', 'CROP': 'Milho',
        'ISSUE': 'Micotoxina / Fusarium',
        'Q': '(maize OR corn) AND (Fusarium OR aflatoxin OR mycotoxin)'},
    'OLIVE_BACTROCERA': {
        'CASE': 'IT-DEMO-001', 'CROP': 'Oliveira', 'ISSUE': 'Bactrocera oleae',
        'Q': 'olive AND (Bactrocera OR "olive fly")'},
    'DURUM_FUSARIUM': {
        'CASE': 'candidato', 'CROP': 'Trigo duro', 'ISSUE': 'Fusarium / micotoxina',
        'Q': '"durum wheat" AND (Fusarium OR mycotoxin OR deoxynivalenol)'},
}


def _get(params, tentativas=6):
    u = API + '?' + urllib.parse.urlencode(params)
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(u, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tentativas - 1:
                # O OpenAlex estrangula por rajada, não por volume diário. Medido:
                # 12s não bastou. A espera cresce e a paginação anda devagar de
                # propósito — consulta dirigida não precisa ser rápida.
                time.sleep(25 * (i + 1))
                continue
            raise
    return None


def percorrer(busca, pais='it', desde=DESDE, teto=400):
    f = ('institutions.country_code:%s,from_publication_date:%s,'
         'title_and_abstract.search:%s' % (pais, desde, busca))
    obras, cursor, n = [], '*', 0
    while cursor and n < teto:
        d = _get({'filter': f, 'per-page': 100, 'cursor': cursor, 'mailto': MAILTO,
                  'select': 'id,doi,publication_year,authorships'})
        if not d:
            break
        for w in d['results']:
            n += 1
            obras.append(w)
        cursor = d['meta'].get('next_cursor')
        time.sleep(1.6)
    return obras, n


def pessoas(obras, pais='IT'):
    rec = collections.Counter()
    meta = {}
    for w in obras:
        ano = w.get('publication_year') or 0
        for a in w.get('authorships', []):
            au = a.get('author') or {}
            aid = au.get('id')
            if not aid:
                continue
            insts = [i for i in a.get('institutions', []) if i.get('country_code') == pais]
            if not insts:
                continue           # sem afiliação italiana declarada, fora do recorte
            rec[aid] += 1
            m = meta.setdefault(aid, {
                'PERSON': au.get('display_name'), 'OPENALEX_ID': aid,
                'ORCID': au.get('orcid'), 'INSTITUTIONS': {}, 'LAST_ACTIVITY': 0,
                'FIRST_SEEN': 9999})
            for i in insts:
                m['INSTITUTIONS'][i.get('display_name')] = i.get('ror')
            m['LAST_ACTIVITY'] = max(m['LAST_ACTIVITY'], ano)
            m['FIRST_SEEN'] = min(m['FIRST_SEEN'], ano or 9999)
    return rec, meta


def montar(teto=400):
    universo = {}
    por_escopo = {}
    for chave, cfg in ESCOPOS.items():
        obras, n = percorrer(cfg['Q'], teto=teto)
        rec, meta = pessoas(obras)
        por_escopo[chave] = {
            'CASE': cfg['CASE'], 'CROP': cfg['CROP'], 'ISSUE': cfg['ISSUE'],
            'QUERY': cfg['Q'], 'WORKS_TRAVERSED': n,
            'AUTHORS_WITH_IT_AFFILIATION': len(rec),
        }
        for aid, c in rec.items():
            m = meta[aid]
            p = universo.setdefault(aid, {
                'ORIGIN_ID': 'IT-RES-%s' % aid.rsplit('/', 1)[-1],
                'TYPE': 'RESEARCHER',
                'PERSON': m['PERSON'], 'OPENALEX_ID': aid,
                'ORCID': m['ORCID'] or 'NÃO SEI',
                'INSTITUTIONS': [], 'ROR': [],
                'COUNTRY': 'IT',
                'INSTITUTION_REGION': 'NÃO SEI',
                'FACT_REGION': 'NÃO DERIVADO — afiliação não é região do fenômeno',
                'CROPS': set(), 'ISSUES': set(), 'SCOPES': {},
                'PUBLICATIONS_IN_SCOPES': 0,
                'LAST_ACTIVITY': 0, 'FIRST_SEEN': 9999,
                'PUBLIC_CHANNELS': 'NOT_COLLECTED',
                'REACH': 'NÃO MEDIDO — e não entra: RESEARCH AUTHORITY ≠ PUBLIC REACH',
            })
            for nome, ror in m['INSTITUTIONS'].items():
                if nome and nome not in p['INSTITUTIONS']:
                    p['INSTITUTIONS'].append(nome)
                if ror and ror not in p['ROR']:
                    p['ROR'].append(ror)
            p['CROPS'].add(cfg['CROP'])
            p['ISSUES'].add(cfg['ISSUE'])
            p['SCOPES'][chave] = c
            p['PUBLICATIONS_IN_SCOPES'] += c
            p['LAST_ACTIVITY'] = max(p['LAST_ACTIVITY'], m['LAST_ACTIVITY'])
            p['FIRST_SEEN'] = min(p['FIRST_SEEN'], m['FIRST_SEEN'])

    for p in universo.values():
        p['CROPS'] = sorted(p['CROPS'])
        p['ISSUES'] = sorted(p['ISSUES'])
        p['SCOPE_COUNT'] = len(p['SCOPES'])
        p['IDENTITY_STATUS'] = ('ORCID_PRESENT' if p['ORCID'] != 'NÃO SEI'
                                else 'WEAK_NO_ORCID')
        p['ROLE'] = 'RESEARCHER'
        p['ROLE_EVIDENCE'] = ('autoria em %d trabalho(s) do recorte, com afiliação '
                              'italiana declarada no próprio registro OpenAlex'
                              % p['PUBLICATIONS_IN_SCOPES'])
        p['SELECTION_REASON'] = ('recorrência dentro de CROP×ISSUE já medido — não cota, '
                                 'não ranking de fama')
    return universo, por_escopo


def main():
    teto = 400
    for a in sys.argv[1:]:
        if a.startswith('--teto='):
            teto = int(a.split('=')[1])
    universo, escopos = montar(teto)
    lista = sorted(universo.values(), key=lambda p: -p['PUBLICATIONS_IN_SCOPES'])
    com_orcid = [p for p in lista if p['IDENTITY_STATUS'] == 'ORCID_PRESENT']
    recorrentes = [p for p in lista if p['PUBLICATIONS_IN_SCOPES'] >= 3]
    ativos = [p for p in lista if p['LAST_ACTIVITY'] >= 2024]
    inst = collections.Counter()
    for p in lista:
        for i in p['INSTITUTIONS']:
            inst[i] += 1

    out = {
        'DATASET': 'ITALY-RESEARCHER-UNIVERSE', 'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-T5-001', 'SOURCE': 'OpenAlex',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'FILTER_BASE': 'institutions.country_code:it, from_publication_date:%s' % DESDE,
        'EVIDENCE_CLASS': 'SCIENTIFIC_LITERATURE',
        'SOURCE_LOCATION': 'GLOBAL (índice)',
        'FACT_LOCATION': 'NÃO SEI — a afiliação é do AUTOR, não do estudo',
        'METHOD': ('CROP×ISSUE já medido → obras → autores → recorrência. Sem cota, sem '
                   'ranking de fama, sem seguidores.'),
        'SCOPES': escopos,
        'UNIVERSE_TOTAL': len(lista),
        'WITH_ORCID': len(com_orcid),
        'ORCID_RATE_PCT': round(100.0 * len(com_orcid) / len(lista), 1) if lista else 0,
        'RECURRENT_3_PLUS': len(recorrentes),
        'ACTIVE_SINCE_2024': len(ativos),
        'IN_MULTIPLE_SCOPES': sum(1 for p in lista if p['SCOPE_COUNT'] > 1),
        'INSTITUTIONS_TOP': dict(inst.most_common(20)),
        'PUBLIC_CHANNELS_STATUS': 'NOT_COLLECTED — camada seguinte, e não por nome',
        'WHAT_THIS_DOES_NOT_PROVE': [
            'pressão de campo', 'demanda', 'região do fenômeno',
            'alcance público', 'disposição a falar'],
        'SHORTLIST_RECURRENT_AND_ACTIVE': [
            {k: v for k, v in p.items() if k != 'SCOPES'}
            for p in lista if p['PUBLICATIONS_IN_SCOPES'] >= 3 and p['LAST_ACTIVITY'] >= 2024
        ][:60],
        'UNIVERSE': lista,
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('universo %d · com ORCID %d (%.1f%%) · recorrentes>=3 %d · ativos>=2024 %d · '
          'em >1 recorte %d' % (out['UNIVERSE_TOTAL'], out['WITH_ORCID'],
                                out['ORCID_RATE_PCT'], out['RECURRENT_3_PLUS'],
                                out['ACTIVE_SINCE_2024'], out['IN_MULTIPLE_SCOPES']))
    for k, v in escopos.items():
        print('  %-24s obras %4d · autores IT %4d' % (k, v['WORKS_TRAVERSED'],
                                                      v['AUTHORS_WITH_IT_AFFILIATION']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
