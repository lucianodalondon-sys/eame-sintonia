#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O INVENTARIO QUE NAO CONTA 1 ONDE HA 421.

    python3 scripts/it_acervo_inventario_v2.py            conta e verifica
    python3 scripts/it_acervo_inventario_v2.py --semear   escreve o registo de chaves

POR QUE ESTE ARQUIVO EXISTE
----------------------------
A V1 tinha uma lista branca de treze chaves de coleccao. Um ficheiro cuja lista
se chamasse HITS, CROSSINGS, REJECTIONS ou WEB nao casava com nenhuma, e a V1
devolvia `[doc]` — o ficheiro inteiro contado como UM registo.

    IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json    contou 1     tem 421
    IT-FONTES-REJEICOES-LOTE2-V1.json           contou 1     tem  95

Nao foi erro de dados: foi o CONTADOR a nao reconhecer a forma. E um contador
que nao reconhece uma forma nao devolve erro — devolve um numero menor, que
parece um numero.

    UM TOTAL QUE ENCOLHE EM SILENCIO E PIOR QUE UM TOTAL QUE FALHA:
    O SEGUNDO ALGUEM CONSERTA.

O QUE MUDA
----------
Nao ha lista branca. Uma coleccao e QUALQUER chave de topo cujo valor seja uma
lista nao vazia de dicionarios — a forma, nao o nome. Todas as chaves
encontradas sao contadas, e cada uma tem de constar do REGISTO DE CHAVES
(`IT-ACERVO-CHAVES-V1.json`), que foi SEMEADO a partir do proprio acervo e nao
inventado.

Chave fora do registo = `UNKNOWN_COLLECTION_KEY`, declarada pelo nome e pelo
ficheiro, e a corrida REPROVA. Nunca conta como 1 em silencio.

O QUE ESTE FICHEIRO NAO FAZ
---------------------------
Nao reclassifica dados, nao cria taxonomia nova, nao mexe em nenhum artefacto.
Conta estruturas que ja existem.
"""
import json
import os
import re
import sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V2.json')
REGISTO = os.path.join(ROOT, 'data/samples/IT-PORTAL-V1/IT-ACERVO-CHAVES-V1.json')

# Identica a V1 de proposito: mudar o recorte junto com o contador tornaria os
# dois numeros incomparaveis, e a comparacao e o achado.
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
    ('IT-PORTAL',           r'IT-PORTAL'),
]


def familia(c):
    for nome, rx in FAMILIAS:
        if re.search(rx, c, re.I):
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


def coleccoes(doc):
    """A FORMA, nao o nome: chave de topo cujo valor e lista nao vazia de dicts."""
    if isinstance(doc, list):
        return [('(raiz e lista)', len(doc))] if doc else []
    if not isinstance(doc, dict):
        return []
    cols = [(k, len(v)) for k, v in doc.items()
            if isinstance(v, list) and v and isinstance(v[0], dict)]
    # Um artefacto agregado — sem lista nenhuma — E um registo, e vale 1. Nao e
    # o defeito da V1: o defeito era contar 1 onde havia 421, nao contar 1 onde
    # ha 1. Mas nao passa em silencio: leva chave propria e aparece no registo.
    return cols or [('(documento unico)', 1)]


# Um contador nao se conta a si proprio. A lista UNKNOWN_COLLECTION_KEY de uma
# corrida reprovada e, ela propria, uma coleccao com chave nova: sem esta
# excepcao o inventario passava a reprovar-se por causa do seu proprio relatorio,
# e o segundo numero nunca mais batia com o primeiro.
AS_MINHAS_PROPRIAS_SAIDAS = (
    'IT-ACERVO-INVENTARIO-V2.json',
    'IT-ACERVO-CHAVES-V1.json',
    'IT-FAMILIA-SUPERFICIE-VERIFICACAO-V1.json',
)


def varre():
    achado = []
    for base, _, nomes in os.walk(os.path.join(ROOT, 'data')):
        for n in sorted(nomes):
            if not n.endswith('.json') or n in AS_MINHAS_PROPRIAS_SAIDAS:
                continue
            p = os.path.join(base, n)
            try:
                d = json.load(open(p, encoding='utf-8'))
            except Exception:
                continue
            rel = os.path.relpath(p, ROOT)
            if not e_italiano(rel, d):
                continue
            achado.append((rel, coleccoes(d)))
    return achado


def main():
    achado = varre()

    if '--semear' in sys.argv:
        ch = sorted({k for _, cols in achado for k, _ in cols})
        json.dump({
            'DATASET': 'IT-ACERVO-CHAVES-V1',
            'LEI': 'registo das formas de coleccao que EXISTEM no acervo italiano. '
                   'Semeado a partir do proprio acervo, nunca inventado. Uma chave '
                   'nova nao entra aqui sozinha: o inventario reprova e alguem decide '
                   'se e coleccao ou nao.',
            'SEMEADO_EM': '2026-09-04',
            'N': len(ch),
            'CHAVES': ch,
        }, open(REGISTO, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('registo semeado: %d chaves -> %s' % (len(ch), os.path.relpath(REGISTO, ROOT)))
        return 0

    if not os.path.exists(REGISTO):
        print('falta o registo de chaves. Corra --semear primeiro.', file=sys.stderr)
        return 2
    conhecidas = set(json.load(open(REGISTO, encoding='utf-8'))['CHAVES'])

    por_fam, por_chave, por_sub = Counter(), Counter(), Counter()
    desconhecidas, ficheiros = [], 0
    for rel, cols in achado:
        ficheiros += 1
        fam = familia(rel)
        for k, n in cols:
            if k not in conhecidas:
                desconhecidas.append({'CHAVE': k, 'FICHEIRO': rel, 'REGISTOS': n})
            por_fam[fam] += n
            por_chave[k] += n
            por_sub['%s · %s' % (fam, k)] += n

    doc = OrderedDict([
        ('DATASET', 'IT-ACERVO-INVENTARIO-V2'),
        ('LAYER', 'PORTAL — o acervo contado pela FORMA das coleccoes, nao por lista branca'),
        ('COUNTRY', 'IT'),
        ('CAPTURED_AT', '2026-09-04'),
        ('LEI', 'uma coleccao e qualquer chave de topo cujo valor seja lista nao vazia '
                'de dicionarios. Chave fora do registo reprova a corrida e aparece '
                'como UNKNOWN_COLLECTION_KEY — nunca conta como 1 em silencio.'),
        ('FICHEIROS', ficheiros),
        ('TOTAL_REAL_ACERVO', sum(por_chave.values())),
        ('CHAVES_DE_COLECAO_ENCONTRADAS', len(por_chave)),
        ('CHAVES_NAO_RECONHECIDAS', len(desconhecidas)),
        ('UNKNOWN_COLLECTION_KEY', desconhecidas),
        ('TOTAL_POR_FAMILIA', OrderedDict(sorted(por_fam.items(), key=lambda x: -x[1]))),
        ('TOTAL_POR_SUBTIPO', OrderedDict(sorted(por_sub.items(), key=lambda x: -x[1]))),
        ('POR_CHAVE', OrderedDict(sorted(por_chave.items(), key=lambda x: -x[1]))),
    ])
    json.dump(doc, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== INVENTARIO DO ACERVO · V2 ==')
    print('  ficheiros italianos          %d' % ficheiros)
    print('  TOTAL_REAL_ACERVO            %d' % doc['TOTAL_REAL_ACERVO'])
    print('  CHAVES_DE_COLECAO            %d' % doc['CHAVES_DE_COLECAO_ENCONTRADAS'])
    print('  CHAVES_NAO_RECONHECIDAS      %d' % doc['CHAVES_NAO_RECONHECIDAS'])
    print()
    print('  %-20s %8s' % ('FAMILIA', 'REGISTOS'))
    for k, v in doc['TOTAL_POR_FAMILIA'].items():
        print('  %-20s %8d' % (k, v))
    if desconhecidas:
        print('\n  UNKNOWN_COLLECTION_KEY:')
        for u in desconhecidas[:8]:
            print('   · %s em %s (%d registos)' % (u['CHAVE'], u['FICHEIRO'], u['REGISTOS']))
    print('\n  gravado: %s' % os.path.relpath(SAIDA, ROOT))
    return 1 if desconhecidas else 0


if __name__ == '__main__':
    raise SystemExit(main())
