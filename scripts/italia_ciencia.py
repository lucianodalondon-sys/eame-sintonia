#!/usr/bin/env python3
"""
ITÁLIA — ciência primeiro, e a pergunta na ordem certa.

A ordem importa e é a da missão: `CROP × ISSUE × REGION` **antes** de pessoas. Não se
procura "pesquisadores italianos de milho": mede-se onde a ciência italiana se concentra
dentro de um par cultura×problema que já tem escala medida, e as pessoas SAEM dos
trabalhos. Instituição famosa não elege pessoa; recorrência dentro do recorte elege.

CAUTELAS HERDADAS DA ESPANHA, e cada uma custou uma medição lá:

  · **`REGION_OF_STUDY ≠ AUTHOR AFFILIATION`.** A afiliação diz onde a pessoa trabalha,
    não onde o estudo foi feito. Este módulo publica AFILIAÇÃO e nunca a chama de região
    do fenômeno.
  · **`OpenAlex author ID pode conflacionar homônimos`** — medido lá em 58 organizações.
    Por isso ORCID é publicado por pessoa: quem não tem ORCID sai como identidade fraca.
  · **Consulta dirigida, não paginação larga.** O denominador é o recorte, e o recorte
    é declarado junto com o número — contagem sem recorte não é denominador.
  · **`GEOGRAPHIC CONCORDANCE ≠ TEMPORAL ANTICIPATION`**, e mais: concordância entre
    onde a ciência está e onde a cultura está pode ser densidade institucional, não
    sinal agronômico. Na Espanha esse confundidor ficou aberto. Aqui ele nasce declarado.
"""
import collections
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

API = 'https://api.openalex.org/works'
SOURCE_ID = 'IT-T5-001'
MAILTO = 'sintonia-eame@research.example'
DESDE = '2019-01-01'


def _get(params):
    u = API + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(u, timeout=120) as r:
        return json.load(r)


def contar(busca, pais='it', desde=DESDE):
    f = 'institutions.country_code:%s,from_publication_date:%s,title_and_abstract.search:%s' % (
        pais, desde, busca)
    return _get({'filter': f, 'per-page': 1, 'mailto': MAILTO})['meta']['count']


def autores(busca, pais='it', desde=DESDE, teto=400):
    """Percorre o recorte e devolve autores por RECORRÊNCIA dentro dele."""
    f = 'institutions.country_code:%s,from_publication_date:%s,title_and_abstract.search:%s' % (
        pais, desde, busca)
    rec = collections.Counter()
    meta, inst = {}, collections.Counter()
    cursor, n = '*', 0
    while cursor and n < teto:
        d = _get({'filter': f, 'per-page': 100, 'cursor': cursor, 'mailto': MAILTO,
                  'select': 'id,publication_year,authorships'})
        for w in d['results']:
            n += 1
            for a in w.get('authorships', []):
                au = a.get('author') or {}
                aid = au.get('id')
                if not aid:
                    continue
                rec[aid] += 1
                afil = [i for i in a.get('institutions', []) if i.get('country_code') == pais.upper()]
                m = meta.setdefault(aid, {'PERSON': au.get('display_name'),
                                          'OPENALEX_ID': aid, 'ORCID': au.get('orcid'),
                                          'INSTITUTIONS': set(), 'LAST_ACTIVITY': 0})
                for i in afil:
                    m['INSTITUTIONS'].add(i.get('display_name'))
                    inst[i.get('display_name')] += 1
                m['LAST_ACTIVITY'] = max(m['LAST_ACTIVITY'], w.get('publication_year') or 0)
        cursor = d['meta'].get('next_cursor')
    saida = []
    for aid, c in rec.most_common():
        m = meta[aid]
        if not m['INSTITUTIONS']:
            continue
        saida.append({
            'PERSON': m['PERSON'], 'OPENALEX_ID': aid, 'ORCID': m['ORCID'] or 'NÃO SEI',
            'INSTITUTION_AFFILIATION_IT': sorted(m['INSTITUTIONS']),
            'PUBLICATIONS_IN_SCOPE': c, 'LAST_ACTIVITY': m['LAST_ACTIVITY'],
            # ORCID resolve homônimo; sem ele a identidade é FRACA, e dizer isso é
            # obrigatório — na Espanha um author ID conflacionou 58 organizações.
            'IDENTITY_STATUS': 'ORCID_PRESENT' if m['ORCID'] else 'WEAK_NO_ORCID',
            'PUBLIC_CHANNELS': 'NOT_COLLECTED',
        })
    return {'WORKS_TRAVERSED': n, 'AUTHORS': saida,
            'INSTITUTIONS_BY_AUTHOR_APPEARANCES': dict(inst.most_common(15))}


if __name__ == '__main__':
    busca = sys.argv[1] if len(sys.argv) > 1 else '(maize OR corn) AND (Fusarium OR aflatoxin OR mycotoxin)'
    print('RECORTE:', busca)
    print('OBRAS:', contar(busca))
