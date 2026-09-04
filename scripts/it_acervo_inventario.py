#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INVENTARIO DO ACERVO ITALIANO — o que existe, por familia, e quanto e apresentavel.

    python3 scripts/it_acervo_inventario.py

POR QUE ESTE FICHEIRO EXISTE
-----------------------------
Antes de encher um portal e preciso saber com o que se enche. A pergunta desta
missao nao e 'o que falta recolher' — e 'quanto do que ja temos nunca chegou ao
ecra'. Se ha centenas de registos canonicos e o portal mostra dezenas, o problema
e de ingestao, nao de coleta.

AS SEIS CONTAGENS, E O QUE CADA UMA RECUSA
-------------------------------------------
TOTAL              registos na familia
CLIENT_SAFE        o registo declara CLIENT_SAFE, ou a familia inteira ja foi
                   declarada segura na sua propria ficha
QA_PASS            passou por uma regua e a regua deixou-o passar
QA_CORRECTED       passou por uma regua, foi corrigido, e a correccao esta escrita
NAO_SEI            o registo diz NAO_SEI, ou o campo que decidiria nao existe
NAO_APRESENTAVEL   sem proveniencia, sem data, ou explicitamente marcado interno

    UM NAO_SEI NUNCA SOBE PARA CONTEUDO AFIRMATIVO.

E por isso que NAO_SEI e uma coluna e nao um resto: quem soma 'total menos
problemas' acaba a apresentar duvida como facto.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = 'data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V1.json'

# Familia por caminho/dataset. A ordem importa: a primeira que casa ganha.
FAMILIAS = [
    ('RADAR_FUTURO',        r'IT-FUTURO'),
    ('ROTULOS_PORTFOLIO',   r'IT-ROTULOS|IT-VOCAB|IT-PAIRSET|productsRegulatory|productRelationships'),
    ('SINAIS_DE_CAMPO',     r'IT-CAMPO|CURRENT-FIELD|IT-CRUZAMENTO'),
    ('FITOSSANITARIO',      r'IT-CONVEGNO|IT-VIDEO|IT-VOZ-AUDIO|falas/|testemunhas/'),
    ('FONTES',              r'IT-FONTES'),
    ('CONCORRENCIA',        r'COMPETITOR|CONCORREN'),
    ('SOCIAL_INSTAGRAM',    r'IT-INSTAGRAM'),
    ('SENSORES_HUMANOS',    r'SENSOR-PILOT|EARLY_SIGNAL|RESEARCHER|SPEAKER'),
    ('GEOGRAFIA',           r'TERRITORIAL|nuts2|GEOGRAF'),
    ('MERCADO',             r'MARKET|PRICES|ECONOMIC'),
    ('OPORTUNIDADES',       r'IT-RADAR-V21|OPPORTUNIT|IT-SNAPSHOT'),
    ('HANDOFF_METODO',      r'IT-HANDOFF|RUN-MANIFEST|DATA-CLOCK|POLITICA|AUDITORIA|ROTAS-EXTERNAS'),
]

INTERNO = re.compile(r'NOTES_INTERNAL|_INTERNAL|scratch', re.I)


def familia(caminho):
    for nome, rx in FAMILIAS:
        if re.search(rx, caminho, re.I):
            return nome
    return 'OUTROS'


def e_italiano(caminho, doc):
    if re.search(r'(^|/)IT-|italia|italy', caminho, re.I):
        return True
    if isinstance(doc, dict):
        c = str(doc.get('COUNTRY') or doc.get('country') or '')
        if c.upper() in ('IT', 'ITALY', 'ITALIA'):
            return True
        if 'ITALY' in str(doc.get('SOURCE_LOCATION') or '').upper():
            return True
    return False


def registos(doc):
    """As linhas de um artefacto. Um ficheiro nao e um registo: um ficheiro com
    2.928 pares vale 2.928, e dizer que vale 1 esconderia todo o acervo."""
    if not isinstance(doc, dict):
        return doc if isinstance(doc, list) else []
    for k in ('ROWS', 'RECORDS', 'PAIRS', 'SOURCES', 'ITEMS', 'RULED', 'ENTITIES',
              'CANDIDATES', 'SIGNALS', 'APPROVED', 'PRODUCTS', 'VIDEOS', 'POSTS'):
        v = doc.get(k)
        if isinstance(v, list) and v:
            return v
    return [doc]


def classifica(r, doc, caminho):
    """→ (client_safe, qa, nao_sei, nao_apresentavel)"""
    txt = json.dumps(r, ensure_ascii=False) if isinstance(r, (dict, list)) else str(r)
    d = r if isinstance(r, dict) else {}

    cs = d.get('CLIENT_SAFE', doc.get('CLIENT_SAFE'))
    client_safe = str(cs).upper() in ('YES', 'SIM', 'TRUE') if cs is not None else None

    # proveniencia: o registo ou o documento tem de dizer de onde veio e quando
    prov = any(d.get(k) for k in ('SOURCE', 'SOURCE_ID', 'PROVENANCE', 'SOURCE_URL',
                                  'EVIDENCE', 'PRIMARY_URL', 'LABEL_ID', 'REGISTRATION_ID'))
    prov = prov or bool(doc.get('SOURCE_ID') or doc.get('SOURCE'))
    data = bool(d.get('CAPTURED_AT') or d.get('DATE') or d.get('SOURCE_DATE')
                or doc.get('CAPTURED_AT'))

    nao_sei = bool(re.search(r'NAO_SEI|NÃO SEI|NAO SEI|\bUNKNOWN\b|NOT_IN_SOURCE', txt))
    interno = bool(INTERNO.search(caminho))

    qa = None
    for k in ('VERDICT', 'VEREDITO', 'ESTADO', 'STATE', 'QA', 'RELATION', 'PASSES'):
        if k in d:
            qa = str(d[k])
            break
    return client_safe, qa, nao_sei, (not (prov and data)) or interno


def main():
    fam = defaultdict(lambda: Counter())
    ficheiros = defaultdict(list)
    for base, _, nomes in os.walk(os.path.join(ROOT, 'data')):
        for n in nomes:
            if not n.endswith('.json'):
                continue
            p = os.path.join(base, n)
            rel = os.path.relpath(p, ROOT)
            try:
                doc = json.load(open(p, encoding='utf-8'))
            except Exception:
                continue
            if not e_italiano(rel, doc):
                continue
            f = familia(rel)
            rs = registos(doc)
            fam[f]['FICHEIROS'] += 1
            ficheiros[f].append(rel)
            for r in rs:
                fam[f]['TOTAL'] += 1
                cs, qa, ns, na = classifica(r, doc if isinstance(doc, dict) else {}, rel)
                if cs:
                    fam[f]['CLIENT_SAFE'] += 1
                elif cs is None:
                    fam[f]['CLIENT_SAFE_NAO_DECLARADO'] += 1
                if qa and re.search(r'PASS|SUPPORTED|SINAL_COMPLETO|APROVAD|True', str(qa), re.I):
                    fam[f]['QA_PASS'] += 1
                elif qa and re.search(r'CORRECT|PARCIAL|AMBIG', str(qa), re.I):
                    fam[f]['QA_CORRECTED'] += 1
                if ns:
                    fam[f]['NAO_SEI'] += 1
                if na:
                    fam[f]['NAO_APRESENTAVEL'] += 1

    ordem = sorted(fam, key=lambda f: -fam[f]['TOTAL'])
    doc = {
        'DATASET': 'IT-ACERVO-INVENTARIO-V1',
        'LAYER': 'PORTAL — inventario do que existe, antes de encher o ecra',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-PORTAL-V1',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'varredura dos artefactos italianos desta branch, contando REGISTOS e nao '
                  'ficheiros — um ficheiro com 2.928 pares vale 2.928',
        'LEI': 'um NAO_SEI nunca sobe para conteudo afirmativo; por isso e coluna e nao resto',
        'FICHEIROS': sum(fam[f]['FICHEIROS'] for f in fam),
        'REGISTOS': sum(fam[f]['TOTAL'] for f in fam),
        'POR_FAMILIA': {f: dict(fam[f]) for f in ordem},
        'FICHEIROS_POR_FAMILIA': {f: sorted(ficheiros[f]) for f in ordem},
    }
    os.makedirs(os.path.join(ROOT, 'data/samples/IT-PORTAL-V1'), exist_ok=True)
    json.dump(doc, open(os.path.join(ROOT, SAIDA), 'w'), ensure_ascii=False, indent=1)

    print('%-22s %8s %8s %8s %8s %8s %8s' % ('FAMILIA', 'FICH', 'REGISTOS', 'CLIENT', 'QA_PASS', 'NAO_SEI', 'N_APRES'))
    for f in ordem:
        c = fam[f]
        print('%-22s %8d %8d %8d %8d %8d %8d' % (f, c['FICHEIROS'], c['TOTAL'],
              c['CLIENT_SAFE'], c['QA_PASS'], c['NAO_SEI'], c['NAO_APRESENTAVEL']))
    print('%-22s %8d %8d' % ('TOTAL', doc['FICHEIROS'], doc['REGISTOS']))
    print('->', SAIDA)


if __name__ == '__main__':
    main()
