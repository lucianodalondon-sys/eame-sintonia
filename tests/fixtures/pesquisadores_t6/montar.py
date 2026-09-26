#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta as respostas GRAVADAS do ensaio offline de `coleta/pesquisadores_t6.py`.

    py tests/fixtures/pesquisadores_t6/montar.py [--origem=C:/sc-hot/data/raw/RESEARCHER-CORPUS]

DE ONDE VEM (so leitura; o bruto nao e alterado)
-------------------------------------------------
Respostas REAIS do OpenAlex e do ORCID guardadas pela receita T6 (`corpus_pesquisador.py
coletar`) em 18/09/2026 18:25-18:27, em `C:/sc-hot/data/raw/RESEARCHER-CORPUS/`. O sha256
de cada original fica no MANIFEST.

O QUE MUDA NA COPIA, e porque
-----------------------------
1. Foram pedidas POR AUTOR (`filter=author.id:...`), nao pela consulta cultura+problema.
   A consulta nova nunca foi gravada: o envelope `meta` aqui diz isso, e o ensaio simula o
   filtro da consulta (o par tem de estar no titulo+resumo, e um autor com afiliacao IT).
2. Cada trabalho fica so com os campos que a consulta nova pede (`select=`), e so ficam os
   trabalhos que nomeiam pelo menos uma cultura OU um problema — para o ficheiro caber no Git.
3. Do ORCID fica so a lista de DOI declarados (`group[].external-ids`).
"""
import hashlib
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(AQUI)))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
import corpus_pesquisador as CP   # noqa: E402
import pesquisadores_t6 as T6     # noqa: E402

# Os 4 com afiliacao italiana no universo provado + 1 frances (controlo negativo: trabalho
# de videira x peronospora SEM autor italiano nao pode virar pesquisador italiano).
PESSOAS = [
    ('A5057322051', '0000-0001-8866-0633', 'F. Quaglino · University of Milan'),
    ('A5002982424', '0000-0002-5736-9584', 'Nicola Mori · University of Verona'),
    ('A5061913370', '0000-0003-3719-2520', 'Massimo Blandino · University of Turin'),
    ('A5030669619', '0000-0002-8606-451X', 'Antonio Logrieco · ISPA-CNR'),
    ('A5088752812', '0000-0002-7601-5685', 'François Delmotte · INRAE (controlo negativo)'),
]


def sha(f):
    return hashlib.sha256(open(f, 'rb').read()).hexdigest()


def cortar(w):
    return {
        'id': w.get('id'), 'doi': w.get('doi'), 'title': w.get('title'),
        'publication_date': w.get('publication_date'), 'type': w.get('type'),
        'abstract_inverted_index': w.get('abstract_inverted_index'),
        'primary_location': {'source': {k: ((w.get('primary_location') or {}).get('source') or {}).get(k)
                                        for k in ('type', 'display_name')}},
        'primary_topic': {'field': {'display_name': (((w.get('primary_topic') or {}).get('field')
                                                      or {}).get('display_name'))}},
        'authorships': [{
            'author': {k: (a.get('author') or {}).get(k) for k in ('id', 'display_name', 'orcid')},
            'institutions': [{k: i.get(k) for k in ('display_name', 'country_code', 'ror')}
                             for i in (a.get('institutions') or [])],
            'countries': a.get('countries') or [],
        } for a in (w.get('authorships') or [])],
    }


def nomeia_algo(w):
    t = CP._texto((w.get('title') or '') + ' . ' + CP._resumo_do_indice(w.get('abstract_inverted_index')))
    return any(CP._tem(x, t) for lex in (T6.CULTURAS, T6.PROBLEMAS) for ts in lex.values() for x in ts)


def main(argv):
    origem = next((a.split('=', 1)[1] for a in argv if a.startswith('--origem=')),
                  'C:/sc-hot/data/raw/RESEARCHER-CORPUS')
    man = {'ORIGEM': {
        'PASTA': origem, 'GRAVADO_EM': '2026-09-18 18:25-18:27 (-03), pela receita T6 corpus_pesquisador.py coletar',
        'PEDIDO_ORIGINAL': 'OpenAlex /works?filter=author.id:<A>,from_publication_date:2019-01-01 ; ORCID /v3.0/<orcid>/works',
        'O_QUE_MUDOU': 'so campos do select= e so trabalhos que nomeiam cultura ou problema; ORCID so os DOI'},
        'OPENALEX': [], 'ORCID': []}
    for aid, orcid, quem in PESSOAS:
        fo = os.path.join(origem, 'openalex', aid + '.json')
        d = json.load(open(fo, encoding='utf-8'))
        rs = [cortar(w) for w in d.get('results') or [] if nomeia_algo(w)]
        nome = 'openalex-%s.json' % aid
        json.dump({'meta': {'count_no_original': (d.get('meta') or {}).get('count'),
                            'na_copia': len(rs), 'FIXTURE': 'resposta real POR AUTOR, cortada (ver montar.py)'},
                   'results': rs},
                  open(os.path.join(AQUI, nome), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False)
        man['OPENALEX'].append({'FICHEIRO': nome, 'QUEM': quem, 'ORIGINAL': fo.replace('\\', '/'),
                                'ORIGINAL_SHA256': sha(fo), 'TRABALHOS_NO_ORIGINAL': len(d.get('results') or []),
                                'TRABALHOS_NA_COPIA': len(rs)})
        fc = os.path.join(origem, 'orcid', orcid + '-works.json')
        c = json.load(open(fc, encoding='utf-8'))
        dois = sorted(T6.dois_do_orcid(c))
        nome_c = 'orcid-%s-works.json' % orcid
        json.dump({'group': [{'external-ids': {'external-id': [
            {'external-id-type': 'doi', 'external-id-value': x, 'external-id-relationship': 'self'}]}}
            for x in dois]},
            open(os.path.join(AQUI, nome_c), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False)
        man['ORCID'].append({'FICHEIRO': nome_c, 'ORCID': orcid, 'QUEM': quem, 'ORIGINAL': fc.replace('\\', '/'),
                             'ORIGINAL_SHA256': sha(fc), 'DOIS_DECLARADOS': len(dois)})
    json.dump(man, open(os.path.join(AQUI, 'MANIFEST.json'), 'w', encoding='utf-8', newline='\n'),
              ensure_ascii=False, indent=1)
    print(json.dumps(man, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
