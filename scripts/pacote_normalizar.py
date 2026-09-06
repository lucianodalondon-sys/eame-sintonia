#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NORMALIZA O ACERVO ITALIANO PARA `01-DESIGN-READY/` — o pacote de entrega ao Design.

    python3 scripts/pacote_normalizar.py

O que ele faz, e o que ele NÃO faz
-----------------------------------
Ele LÊ os artefatos canônicos (deste worktree e das outras branches, via `git show`),
normaliza cada camada num JSON com **ID estável**, e liga tudo por referência.

    ⛔ Ele não coleta nada, não altera nenhum artefato canônico e não deleta nada do
       repositório. O pacote é uma SELEÇÃO, não uma mudança.

A LEI DO ID
------------
Todo objeto entregável tem `ID` estável no formato `IT-<CAMADA>-NNN`. As relações vivem
num arquivo próprio e só carregam IDs — nunca cópias do registro. Duplicar o registro
dentro da relação é como o mesmo fato passa a ter duas versões que divergem em silêncio.

A LEI DA PROVENIÊNCIA
----------------------
Todo objeto carrega `PROVENANCE`, com um destes valores, e eles não se misturam:

    REAL_SOURCE            veio de fonte primária lida
    REAL_FACT              fato oficial (rótulo, ato, decreto)
    REAL_DERIVED           derivado por nós de material real, e declarado como derivação
    SYNTHETIC_DEMO         inventado para demonstrar a experiência
    INTERNAL_DATA_REQUIRED só existe se a ADAMA conectar dado interno
    NOT_YET_PROVABLE       plausível e sem lastro suficiente

⛔ Nada neste pacote sai como `SYNTHETIC_DEMO` sem estar escrito no próprio objeto.
"""
import json
import os
import re
import subprocess
import sys
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
PKG = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF')
DR = os.path.join(PKG, '01-DESIGN-READY')

_cache_branch = {}


def git_json(rel):
    """Lê um artefato que pode estar só em outra branch. Nunca troca de branch."""
    if rel in _cache_branch:
        return _cache_branch[rel]
    br = subprocess.run(['git', 'branch', '-r'], capture_output=True, text=True,
                        cwd=ROOT).stdout.split()
    for b in br:
        if 'HEAD' in b or '->' in b:
            continue
        if subprocess.run(['git', 'cat-file', '-e', '%s:%s' % (b, rel)],
                          cwd=ROOT, capture_output=True).returncode == 0:
            raw = subprocess.run(['git', 'show', '%s:%s' % (b, rel)], cwd=ROOT,
                                 capture_output=True).stdout.decode('utf-8')
            d = json.loads(raw)
            _cache_branch[rel] = d
            return d
    _cache_branch[rel] = None
    return None


def local_json(rel):
    p = os.path.join(SAMPLES, rel)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def grava(sub, nome, corpo):
    d = os.path.join(DR, sub)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    n = corpo.get('COUNT')
    if n is None:
        for v in corpo.values():
            if isinstance(v, list):
                n = len(v)
                break
    print('  %-46s %s registros' % ('%s/%s' % (sub, nome), n))
    return corpo


def env(tipo, fonte, prov, nota=None):
    """O envelope que todo arquivo do pacote carrega."""
    e = OrderedDict()
    e['LAYER'] = tipo
    e['COUNTRY'] = 'IT'
    e['BUILT_AT'] = '2026-09-02'
    e['SOURCE_ARTIFACTS'] = fonte if isinstance(fonte, list) else [fonte]
    e['PROVENANCE_DEFAULT'] = prov
    if nota:
        e['NOTE'] = nota
    return e


IDS = defaultdict(int)


def novo_id(pref):
    IDS[pref] += 1
    return '%s-%03d' % (pref, IDS[pref])


# ══════════════════════════════════════════════════════════ ADAMA
def camada_adama():
    reg = git_json('data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json')
    cat = git_json('data/samples/IT-CATALOGO/IT-ADAMA-CATALOG-CENSUS.json')
    if not reg:
        print('  !! sem regulatorio — camada ADAMA nao construida'); return {}

    por_reg = {p.get('REGISTRATION_ID'): p for p in cat['PRODUCTS']} if cat else {}
    cat_por_id = {}
    if cat:
        for p in cat['PRODUCTS']:
            rid = str(p.get('MANUFACTURER_CLAIM_REGISTRATION_ID') or '').lstrip('0')
            if rid:
                cat_por_id[rid] = p

    produtos = []
    for p in reg['PRODUCTS']:
        rid = str(p.get('REGISTRATION_ID') or '')
        c = cat_por_id.get(rid.lstrip('0'))
        produtos.append(OrderedDict([
            ('ID', novo_id('IT-PRD')),
            ('PRODUCT', p.get('PRODUCT')),
            ('REGISTRATION_ID', rid),
            ('HOLDER', p.get('HOLDER')),
            ('ACTIVE_INGREDIENTS', p.get('ACTIVE_INGREDIENTS') or []),
            ('FORMULATION', p.get('FORMULATION')),
            ('REGULATORY_CATEGORY', p.get('REGULATORY_CATEGORY')),
            ('LINE', linha_de(p.get('REGULATORY_CATEGORY'))),
            ('STATUS', p.get('STATUS')),
            ('EXPIRY', p.get('EXPIRY')),
            ('MODE_OF_ACTION_DECLARED', p.get('MODE_OF_ACTION_DECLARED') or {}),
            ('CROP_TERMS_PRESENT', p.get('CROP_TERMS_PRESENT') or []),
            ('TARGETS_FROM_LABEL', p.get('TARGETS_FROM_LABEL') or []),
            ('AUTHORIZED_USE_ROWS', p.get('AUTHORIZED_USE_ROWS') or 0),
            ('LABEL_URL', p.get('LABEL_URL')),
            ('IN_PUBLIC_CATALOG', bool(c)),
            ('CATALOG_URL', (c or {}).get('PRODUCT_URL')),
            ('CATALOG_CATEGORY', (c or {}).get('CATEGORY_DISPLAY')),
            ('SOURCE_ID', 'IT-SRC-MINISTERO'),
            ('PROVENANCE', 'REAL_FACT'),
        ]))

    grava('ADAMA', 'adama-italy-products.json', OrderedDict(list(env(
        'ADAMA_PRODUCTS',
        ['data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json',
         'data/samples/IT-CATALOGO/IT-ADAMA-CATALOG-CENSUS.json'],
        'REAL_FACT',
        'Registro do Ministero della Salute, versao PROD_FTS_6_20260824, capturado em '
        '2026-08-30. 163 vigentes. IN_PUBLIC_CATALOG=false NAO significa fora de '
        'mercado — significa que a pagina publica nao o lista.').items()) + [
        ('CRITICAL_COVERAGE_WARNING', {
            'LABELS_DOWNLOADED': '163/163 (100%)',
            'PRODUCTS_WITH_AT_LEAST_ONE_USE_ROW_READ': '19/163 (11,7%)',
            'PRODUCTS_WITH_ZERO_USE_ROW': '144/163 (88,3%)',
            'WHY_THIS_MATTERS': 'o 100% conta ROTULO BAIXADO, nao USO LIDO. Sao numeros '
                                'de coisas diferentes e o primeiro engana.',
            'FORBIDDEN_SENTENCE': 'a ADAMA nao tem produto para <alvo> em <cultura>',
            'ALLOWED_SENTENCE': 'nesta leitura do rotulo nao encontramos linha ligando '
                                'cultura e alvo para este produto. NAO SEI se o registro '
                                'contem.',
        }),
        ('COUNT', len(produtos)),
        ('PRODUCTS', produtos)]))

    # por linha
    for linha, nome in (('HERBICIDA', 'adama-herbicides.json'),
                        ('FUNGICIDA', 'adama-fungicides.json'),
                        ('INSETICIDA', 'adama-insecticides.json'),
                        ('OUTRA', 'adama-other-lines.json')):
        sel = [p for p in produtos if p['LINE'] == linha]
        ai = defaultdict(int)
        for p in sel:
            for a in p['ACTIVE_INGREDIENTS']:
                ai[a] += 1
        grava('ADAMA', nome, OrderedDict(list(env(
            'ADAMA_LINE_' + linha,
            'data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json',
            'REAL_FACT').items()) + [
            ('LINE', linha),
            ('COUNT', len(sel)),
            ('ACTIVE_INGREDIENTS_BY_PRODUCT_COUNT', dict(sorted(ai.items(), key=lambda kv: -kv[1]))),
            ('PRODUCT_IDS', [p['ID'] for p in sel]),
            ('RESOLVE_WITH', 'ADAMA/adama-italy-products.json — o registro completo vive '
                             'la, e SO la. Repetir o objeto aqui criaria duas versoes do '
                             'mesmo produto que divergem em silencio na primeira correcao.'),
            ('PRODUCTS_SUMMARY', [{'ID': x['ID'], 'PRODUCT': x['PRODUCT'],
                                   'ACTIVE_INGREDIENTS': x['ACTIVE_INGREDIENTS'],
                                   'EXPIRY': x['EXPIRY']} for x in sel])]))

    # crop x problem x product
    linhas = []
    for row in reg['AUTHORIZED_USE_ROWS']:
        for t in (row.get('TARGETS') or []):
            linhas.append(OrderedDict([
                ('ID', novo_id('IT-CPP')),
                ('CROP', row.get('CROP')),
                ('CROP_TERM_MATCHED', row.get('CROP_TERM_MATCHED')),
                ('TARGET', t),
                ('PRODUCT', row.get('PRODUCT')),
                ('REGISTRATION_ID', row.get('REGISTRATION_ID')),
                ('ACTIVE_INGREDIENTS', row.get('ACTIVE_INGREDIENTS') or []),
                ('REGULATORY_CATEGORY', row.get('REGULATORY_CATEGORY')),
                ('DOSES', row.get('DOSES') or []),
                ('MAX_APPLICATIONS', row.get('MAX_APPLICATIONS')),
                ('INTERVAL_DAYS', row.get('INTERVAL_DAYS')),
                ('MODE_OF_ACTION_DECLARED', row.get('MODE_OF_ACTION_DECLARED') or {}),
                ('EXPIRY', row.get('EXPIRY')),
                ('APPLICATION_TIMING', 'NAO SEI — a coluna de epoca do rotulo nao foi extraida'),
                ('LABEL_URL', row.get('LABEL_URL')),
                ('EVIDENCE_CLASS', 'REGULATORY_FACT'),
                ('PROVENANCE', 'REAL_FACT'),
            ]))
    grava('ADAMA', 'adama-crop-problem-product.json', OrderedDict(list(env(
        'ADAMA_CROP_TARGET_PRODUCT',
        'data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json',
        'REAL_FACT',
        'linha de uso autorizado = cultura, alvo e (quando presente) dose na MESMA linha '
        'da tabela do rotulo. E a unica classe DESTE LEITOR que liga cultura a alvo — '
        'nao a unica da casa: ver LEITOR_CANONICO_DA_CASA abaixo.').items()) + [
        # `CANONICAL_AUTHORITY = NO` estava escrito dentro do artefacto de origem e em dois
        # documentos, e o pipeline que produz o pacote entregue continuava a tratar esse
        # artefacto como autoridade unica, carimbando REAL_FACT. Uma demissao que so vale
        # dentro do ficheiro demitido nao vale.
        ('LEITOR_CANONICO_DA_CASA', {
            'ESTA_CAMADA_VEM_DE': 'LEGACY_READER / HISTORICAL_INPUT',
            'CANONICAL_AUTHORITY': 'NO',
            'LEITOR_CANONICO': 'IT-ROTULOS-PARES-V3 (data/samples/IT-ROTULOS-V1/), '
                               'it_rotulo_parser/3.4.0, portao IT-ROTULOS-PORTAO-V1 = PASS',
            'ESCALA': 'o canonico le 128 rotulos com par; esta camada vem de 19',
            'O_QUE_ESTA_CAMADA_TEM_E_O_CANONICO_NAO': 'DOSES, INTERVAL_DAYS, '
                                                      'MAX_APPLICATIONS, EVIDENCE, ROW_STATE, '
                                                      'CROP_TERM_MATCHED, REGULATORY_CATEGORY',
            'LEI': 'OLDER_SMALLER_READER != CANONICAL_READER',
        }),
        ('COUNT', len(linhas)),
        ('SOURCE_ROWS', len(reg['AUTHORIZED_USE_ROWS'])),
        ('ROWS_WITH_DOSE', reg.get('AUTHORIZED_USE_ROWS_WITH_DOSE')),
        ('CLASS_DEFINITION_CONFLICT', 'a definicao da classe exige dose; so 13 das 49 '
                                      'linhas tem. 36 (73,5%) nao cumprem a propria '
                                      'definicao — registrado, nao corrigido.'),
        ('PAIR_INTEGRITY_WARNING', 'alvos como `Avena sp`, `Sorghum halepense`, '
                                   '`Raphanus sp` e `Lolium sp` sao generos que TAMBEM '
                                   'nomeiam cultura. O par pode estar certo; a auditoria '
                                   'os marcou como suspeitos de colisao, nao como erro.'),
        ('LINKS', linhas)]))

    # crops
    crops = []
    for termo, n in (reg.get('PRODUCTS_BY_CROP_TERM') or {}).items():
        com_linha = len({r['PRODUCT'] for r in linhas if r['CROP'] == termo})
        crops.append(OrderedDict([
            ('ID', novo_id('IT-CROP')),
            ('CROP_TERM', termo),
            ('PRODUCTS_MENTIONING_CROP', n),
            ('PRODUCTS_WITH_USE_ROW_READ', com_linha),
            ('DISTANCE', n - com_linha),
            ('READING', 'PRODUCTS_MENTIONING_CROP conta rotulo que CITA a cultura. '
                        'PRODUCTS_WITH_USE_ROW_READ conta ligacao cultura-alvo LIDA. '
                        'A distancia e o que ainda nao sabemos, nao o que nao existe.'),
            ('PROVENANCE', 'REAL_DERIVED'),
        ]))
    crops.sort(key=lambda c: -c['DISTANCE'])
    grava('ADAMA', 'adama-italy-crops.json', OrderedDict(list(env(
        'ADAMA_CROPS', 'data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json',
        'REAL_DERIVED').items()) + [('COUNT', len(crops)), ('CROPS', crops)]))
    return {'produtos': produtos, 'links': linhas, 'crops': crops}


def linha_de(cat):
    c = (cat or '').upper()
    if 'DISERBANTE' in c:
        return 'HERBICIDA'
    if 'FUNGICIDA' in c:
        return 'FUNGICIDA'
    if 'INSETTICIDA' in c or 'AFICIDA' in c or 'ACARICIDA' in c:
        return 'INSETICIDA'
    return 'OUTRA'


if __name__ == '__main__':
    os.makedirs(DR, exist_ok=True)
    print('CAMADA ADAMA')
    camada_adama()
    print('\nok')
