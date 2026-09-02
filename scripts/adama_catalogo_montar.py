#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTA O CATÁLOGO COMERCIAL DA ADAMA ITÁLIA — colhido pelas PÁGINAS DE CULTURA.

    python3 scripts/adama_catalogo_montar.py

COMO ESTE DADO FOI OBTIDO, E POR QUE POR AÍ
--------------------------------------------
A listagem por categoria (`/products/crop-protection`) está atrás de Akamai Bot
Manager: devolve `Access Denied` com `bm-verify`, e o `robots.txt` dá 403. Não se
contorna detecção de robô.

Mas o site tem OUTRO caminho, aberto e servido normalmente: as **páginas de
cultura** (`/italia/it/vite`, `/mais`, `/riso`, `/cereali`, `/pomodoro`,
`/pomacee`, `/soia`). Elas listam os produtos daquela linha técnica — e para este
projeto valem MAIS que a listagem por categoria, porque já vêm com a cultura
amarrada, que é a unidade do Sintonia.

O menu do próprio site (visível até na página 404) revelou esses sete caminhos.

⚠️ A ARMADILHA QUE ESTA MONTAGEM TEM DE BARRAR
-----------------------------------------------
`fullpage` e `max-ace` aparecem nas SETE páginas de cultura — inclusive na de
pomáceas e na de soja. Não é porque são herbicidas de maçã e de soja: é porque
são **banner fixo do site**, promoção de linha que o template repete em toda
página.

    PRODUTO QUE APARECE EM TODAS AS CULTURAS NÃO ESTÁ ASSOCIADO A NENHUMA.
    É moldura, não conteúdo.

Sem essa trava, o Sintonia diria que a ADAMA tem solução de arroz para maçã.
É a mesma família de `CROP_TERM_PRESENT ≠ ABOUT_THAT_CROP`.

E A LEI QUE JÁ ESTAVA ESCRITA
------------------------------
    CATALOG_PRODUCT e REGULATORY_PRODUCT são classes diferentes.

Este arquivo é a classe COMERCIAL. Cruzar com os 163 do registro é feito no fim,
e as três listas — nos dois, só no catálogo, só no registro — nunca são subtração
uma da outra. «Só no registro» significa NÃO SEI, nunca «descontinuado».
"""
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')
REGISTRO = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                        '01-DESIGN-READY', 'ADAMA', 'adama-italy-products.json')
BASE = 'https://www.adama.com'

# Colhido em 02/09/2026, navegando as páginas de cultura uma a uma.
CULTURA_PAGINA = {
    'VITE': ('/italia/it/vite', [
        'prodotti-adama/erbicidi/taifun-mk-cl', 'prodotti-adama/erbicidi/agil',
        'prodotti-adama/fungicidi/folpan-80-wdg', 'prodotti-adama/fungicidi/folpan-gold',
        'prodotti/erbicidi/folpan-energy', 'prodotti/fungicidi/nimrodr-250-ew',
        'prodotti-adama/fungicidi/mavita-250-ec', 'prodotti-adama/fungicidi/banjo',
        'prodotti-adama/insetticidi/mavrik-smart',
        'prodotti-adama/insetticidi/lamdex-extra',
        'prodotti-adama/speciali/exelgrow']),
    'MAIS': ('/italia/it/mais', [
        'prodotti-adama/erbicidi/activus-me', 'prodotti-adama/erbicidi/sulcotrek',
        'prodotti-adama/erbicidi/nicogan-vo', 'prodotti-adama/insetticidi/schermo-0-5-g',
        'prodotti-adama/insetticidi/lamdex-extra', 'prodotti/speciali/budge']),
    'RISO': ('/italia/it/riso', [
        'prodotti-adama/erbicidi/activus-me', 'prodotti-adama/erbicidi/clematis',
        'prodotti/speciali/powerfilmr', 'prodotti/erbicidi/highcardr',
        'prodotti-adama/speciali/parleaf', 'prodotti-adama/fungicidi/mirador-sc',
        'prodotti/speciali/budge']),
    'CEREALI': ('/italia/it/cereali', [
        'prodotti-adama/erbicidi/taifun-mk-cl', 'prodotti-adama/erbicidi/stopper-p',
        'prodotti-adama/erbicidi/timeline-trio', 'prodotti/erbicidi/edaptisr',
        'prodotti/fungicidi/stavento', 'prodotti/fungicidi/maxentisr',
        'prodotti/fungicidi/maganicr', 'prodotti-adama/insetticidi/mavrik-smart',
        'prodotti-adama/insetticidi/pirimor-50', 'prodotti/speciali/budge']),
    'POMODORO': ('/italia/it/pomodoro', [
        'prodotti/erbicidi/sonavior', 'prodotti-adama/erbicidi/activus-me',
        'prodotti-adama/erbicidi/agil', 'prodotti/erbicidi/arrodimr',
        'prodotti-adama/fungicidi/zakeo-250-sc', 'prodotti-adama/fungicidi/folpan-80-wdg',
        'prodotti-adama/fungicidi/mavita-250-ec', 'prodotti/fungicidi/nimrodr-250-ew',
        'prodotti-adama/insetticidi/lamdex-extra', 'prodotti-adama/insetticidi/pirimor-50',
        'prodotti-adama/insetticidi/schermo-0-5-g', 'prodotti-adama/speciali/exelgrow']),
    'POMACEE': ('/italia/it/pomacee', [
        'prodotti-adama/speciali/brevis', 'prodotti-adama/erbicidi/agil',
        'prodotti-adama/fungicidi/merpan-80-wdg', 'prodotti-adama/fungicidi/banjo',
        'prodotti/fungicidi/nimrodr-250-ew', 'prodotti-adama/fungicidi/mavita-250-ec',
        'prodotti-adama/insetticidi/mavrik-smart', 'prodotti-adama/insetticidi/pirimor-50',
        'prodotti-adama/speciali/exelgrow']),
    'SOIA': ('/italia/it/soia', [
        'prodotti-adama/erbicidi/activus-me', 'prodotti-adama/erbicidi/clematis',
        'prodotti-adama/erbicidi/valley', 'prodotti-adama/erbicidi/davai',
        'prodotti-adama/erbicidi/agil', 'prodotti-adama/speciali/parleaf',
        'prodotti/speciali/budge']),
}

# Aparecem em TODAS as páginas: são moldura do template, não associação de cultura.
BANNER_DO_SITE = {
    'prodotti/erbicidi/fullpager-rice-cropping-solution',
    'prodotti/erbicidi/max-acer-rice-cropping-solution',
}

# Fichas lidas por dentro, uma a uma. Citação literal da própria página.
FICHAS = {
    'prodotti-adama/fungicidi/mirador-sc': {
        'NOME': 'Mirador® SC', 'CATEGORIA': 'FUNGICIDI',
        'ATIVOS': 'Azoxystrobin puro 23,2 g (250g/l)',
        'REGISTRO_NA_PAGINA': 'n° 15111 del 25-03-2011',
        'ATUALIZADO_EM': '2026-03-24',
        'CITACAO': 'Fungicida contro le malattie della parte aerea di frumento, orzo e '
                   'riso e contro le maggiori patologie di solanacee e cucurbitacee in '
                   'pieno campo e in serra',
        'ESPECTRO_DECLARADO': 'Frumento e orzo: Ruggini, Septoria, Rincosporiosi e '
                              'Oidio · Riso: Brusone e Elmintosporiosi · Cucurbitacee: '
                              'Oidio e Pseudoperonospora · Solanacee: Alternaria, '
                              'Peronospora e Oidio',
    },
    'prodotti/fungicidi/avastelr': {
        'NOME': 'Avastel®', 'CATEGORIA': 'FUNGICIDI', 'ATUALIZADO_EM': '2026-03-24',
        'CITACAO': 'Fungicida per il controllo delle principali malattie dei cereali '
                   'dalle prime fasi di sviluppo alla botticella',
    },
    'prodotti/fungicidi/maganicr': {
        'NOME': 'Maganic®', 'CATEGORIA': 'FUNGICIDI',
        'ATIVOS': 'Difenoconazolo puro (125 g/L) + Protioconazolo puro (175 g/L)',
        'ATUALIZADO_EM': '2026-03-24',
        'CITACAO': 'fungicida per la protezione della spiga dei cereali con tecnologia '
                   'formulativa Asorbital®. Per frumento tenero e duro, orzo, segale e '
                   'triticale',
    },
    'prodotti/fungicidi/stavento': {
        'NOME': 'Stavento®', 'CATEGORIA': 'FUNGICIDI',
        'ATIVOS': 'Folpet puro 39.7 g (500 g/l)',
        'REGISTRO_NA_PAGINA': 'n° 17752 del 21.12.2021',
        'ATUALIZADO_EM': '2026-07-07',
    },
    'prodotti/erbicidi/sonavior': {
        'NOME': 'Sonavio®', 'CATEGORIA': 'ERBICIDI',
        'ATIVOS': 'Bifenox puro 40.7 g (=480 g/l)',
        'REGISTRO_NA_PAGINA': 'n° 18072 del 08.02.2024',
        'ATUALIZADO_EM': '2026-07-21',
    },
    'prodotti/erbicidi/goltixr-top-0': {
        'NOME': 'Goltix® TOP', 'CATEGORIA': 'ERBICIDI',
        'ATIVOS': 'Metamitron puro 57,9 g (700 g/L)',
        'REGISTRO_NA_PAGINA': 'n° 18814 del 25.11.2024',
        'ATUALIZADO_EM': '2026-03-24',
    },
    'prodotti/erbicidi/dioder': {
        'NOME': 'Diode®', 'CATEGORIA': 'ERBICIDI',
        'ATIVOS': 'Mesotrione puro g 9,4 (=100 g/L)',
        'REGISTRO_NA_PAGINA': 'n° 18694 del 26-03-2025',
        'CITACAO': 'Erbicida selettivo per mais, mais dolce e sorgo.',
    },
    'prodotti/erbicidi/highcardr': {
        'NOME': 'Highcard®', 'CATEGORIA': 'ERBICIDI',
        'ATIVOS': 'Isoxadifen etile (antidoto agronomico) puro 7.1 (74 g/L) + '
                  'Quizalofop-P-ethyl puro 10.0 g (105 g/l)',
        'REGISTRO_NA_PAGINA': 'n° 17995 del 8/02/2024',
        'CITACAO': 'Erbicida per varietà ed ibridi di riso Max-Ace® e tolleranti agli '
                   'erbicidi arilossifenossipropionati',
    },
    'prodotti/erbicidi/folpan-energy': {
        'NOME': 'Folpan® Energy', 'CATEGORIA': 'FUNGICIDI',
        'ATIVOS': 'Folpet puro 300 g/l + Fosfonato di potassio 450 g/l',
        'REGISTRO_NA_PAGINA': 'n° 16749 del 02.12.2022',
        'NOTA': 'a URL diz «erbicidi» mas o produto e FUNGICIDA (folpet + fosfonato). '
                'O caminho do CMS nao e classificacao — a pagina e a etiqueta mandam.',
    },
    'prodotti-adama/insetticidi/schermo-0-5-g': {
        'NOME': 'Schermo® 0.5 G', 'CATEGORIA': 'INSETTICIDI',
        'ATUALIZADO_EM': '2026-03-25',
        'CITACAO': 'Geoinsetticida granulare per barbabietola da zucchero, frumento, '
                   'mais, oleaginose, ortaggi e tabacco. Contro elateridi, nottue e '
                   'diabrotica',
    },
    'prodotti-adama/insetticidi/lamdex-extra': {
        'NOME': 'Lamdex® Extra', 'CATEGORIA': 'INSETTICIDI',
        'ATIVOS': 'Lambda-cialotrina pura 2,5 g (25 g/kg)',
        'REGISTRO_NA_PAGINA': 'n° 8259 del 04-05-1993',
        'CITACAO': 'Insetticida ad ampio spettro per orticole, cereali, mais, '
                   'barbabietola da zucchero, oleaginose, vite, frutticole',
    },
    'prodotti/erbicidi/max-acer-rice-cropping-solution': {
        'NOME': 'Max-Ace® Rice Cropping Solution', 'CATEGORIA': 'ERBICIDI',
        'ATUALIZADO_EM': '2026-02-03',
        'CITACAO': 'HIGHCARD® e Max-Ace®: la coppia vincente del riso',
        'NOTA': 'e SISTEMA (variedade + herbicida), nao um produto de registro',
    },
}

CAT_DO_CAMINHO = [('ERBICIDI', 'erbicidi'), ('FUNGICIDI', 'fungicidi'),
                  ('INSETTICIDI', 'insetticidi'), ('SPECIALI', 'speciali')]


def _n(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', t or '')
                if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()


def nome_do_slug(slug):
    s = slug.rsplit('/', 1)[-1].replace('-', ' ')
    s = re.sub(r'\b(\w{3,})r\b', r'\1', s)      # goltixr → goltix, avastelr → avastel
    s = re.sub(r'\s+\d+$', '', s)
    return s.upper().strip()


def categoria(slug):
    for k, p in CAT_DO_CAMINHO:
        if '/%s/' % p in slug:
            return k
    return 'NAO_SEI'


def main():
    # ── 1 · produtos, e a cultura de cada um ──────────────────────────────────
    culturas_de = defaultdict(list)
    for cult, (_url, slugs) in CULTURA_PAGINA.items():
        for s in slugs:
            if s in BANNER_DO_SITE:
                continue
            culturas_de[s].append(cult)

    n_paginas = len(CULTURA_PAGINA)
    produtos = []
    for slug, culturas in sorted(culturas_de.items()):
        f = FICHAS.get(slug, {})
        cat = f.get('CATEGORIA') or categoria(slug)
        produtos.append({
            'NOME_NO_CATALOGO': f.get('NOME') or nome_do_slug(slug),
            'CATEGORIA': cat,
            'CATEGORIA_VEM_DE': ('a ficha do produto' if f.get('CATEGORIA')
                                 else 'o caminho da URL — menos confiavel'),
            'CULTURAS_DECLARADAS_NO_SITE': sorted(culturas),
            'N_PAGINAS_DE_CULTURA': len(culturas),
            'URL': BASE + '/' + slug.lstrip('/') if slug.startswith('italia') else
                   BASE + '/italia/it/' + slug,
            'FICHA_LIDA': bool(f),
            'ATIVOS_NA_PAGINA': f.get('ATIVOS'),
            'REGISTRO_NA_PAGINA': f.get('REGISTRO_NA_PAGINA'),
            'ATUALIZADO_EM': f.get('ATUALIZADO_EM'),
            'CITACAO_LITERAL': f.get('CITACAO'),
            'ESPECTRO_DECLARADO': f.get('ESPECTRO_DECLARADO'),
            'NOTA': f.get('NOTA'),
            'ENTITY_CLASS': 'CATALOG_PRODUCT',
            'PROVENANCE': 'REAL_SOURCE',
        })
    # os que só apareceram por ficha, sem página de cultura
    for slug, f in FICHAS.items():
        if slug in culturas_de or slug in BANNER_DO_SITE:
            continue
        produtos.append({
            'NOME_NO_CATALOGO': f.get('NOME') or nome_do_slug(slug),
            'CATEGORIA': f.get('CATEGORIA') or categoria(slug),
            'CATEGORIA_VEM_DE': 'a ficha do produto',
            'CULTURAS_DECLARADAS_NO_SITE': [],
            'CULTURA_LEIA_ASSIM': 'chegamos a este produto por link de outra ficha, nao '
                                  'por pagina de cultura. Nao ter cultura aqui NAO '
                                  'significa que ele nao tenha.',
            'N_PAGINAS_DE_CULTURA': 0,
            'URL': BASE + '/italia/it/' + slug,
            'FICHA_LIDA': True,
            'ATIVOS_NA_PAGINA': f.get('ATIVOS'),
            'REGISTRO_NA_PAGINA': f.get('REGISTRO_NA_PAGINA'),
            'ATUALIZADO_EM': f.get('ATUALIZADO_EM'),
            'CITACAO_LITERAL': f.get('CITACAO'),
            'ESPECTRO_DECLARADO': f.get('ESPECTRO_DECLARADO'),
            'NOTA': f.get('NOTA'),
            'ENTITY_CLASS': 'CATALOG_PRODUCT',
            'PROVENANCE': 'REAL_SOURCE',
        })

    # ── 2 · cruzamento com os 163 do registro ─────────────────────────────────
    reg = json.load(open(REGISTRO, encoding='utf-8'))['PRODUCTS'] \
        if os.path.exists(REGISTRO) else []
    reg_norm = {_n(p['PRODUCT']): p for p in reg}
    nos_dois, so_cat = [], []
    casados = set()
    for p in produtos:
        c = _n(re.sub(r'[®]', '', p['NOME_NO_CATALOGO']))
        alvo = reg_norm.get(c)
        if not alvo:
            for rn, rp in reg_norm.items():
                if c and rn and (rn.startswith(c) or c.startswith(rn)) \
                        and abs(len(rn) - len(c)) <= 9:
                    alvo = rp
                    break
        if alvo:
            casados.add(_n(alvo['PRODUCT']))
            nos_dois.append(dict(p, REGISTRATION_ID=alvo['REGISTRATION_ID'],
                                 NOME_NO_REGISTRO=alvo['PRODUCT'],
                                 EXPIRY=alvo.get('EXPIRY'),
                                 ATIVOS_NO_REGISTRO=alvo.get('ACTIVE_INGREDIENTS')))
        else:
            so_cat.append(p)
    so_reg = [{'NOME_NO_REGISTRO': p['PRODUCT'], 'REGISTRATION_ID': p['REGISTRATION_ID'],
               'EXPIRY': p.get('EXPIRY'), 'LINE': p.get('LINE')}
              for p in reg if _n(p['PRODUCT']) not in casados]

    cat = Counter(p['CATEGORIA'] for p in produtos)
    especiais = [p['NOME_NO_CATALOGO'] for p in produtos if p['CATEGORIA'] == 'SPECIALI']

    saida = {
        'DATASET': 'IT-ADAMA-CATALOGO-COMERCIAL',
        'FAMILIA_DA_MISSAO': '4 · CATALOGO COMERCIAL ADAMA ITALIA',
        'CAPTURADO_EM': '2026-09-02',
        'COMO_FOI_OBTIDO':
            'navegando as 7 PAGINAS DE CULTURA do site (vite, mais, riso, cereali, '
            'pomodoro, pomacee, soia) e as fichas de produto ligadas a elas. A '
            'listagem por categoria esta atras de Akamai Bot Manager (Access Denied '
            '+ bm-verify; robots.txt da 403) e NAO foi contornada.',
        'POR_QUE_ESTE_CAMINHO_E_MELHOR':
            'a pagina de cultura ja amarra produto a CULTURA, que e a unidade do '
            'Sintonia. A listagem por categoria nao amarra.',
        'LEI': 'CATALOG_PRODUCT e REGULATORY_PRODUCT sao classes diferentes',
        'BANNER_DO_SITE_EXCLUIDO': sorted(BANNER_DO_SITE),
        'BANNER_POR_QUE':
            'aparecem nas SETE paginas de cultura, inclusive pomaceas e soja. E '
            'moldura do template, nao associacao de cultura. PRODUTO QUE APARECE EM '
            'TODAS AS CULTURAS NAO ESTA ASSOCIADO A NENHUMA.',
        'PAGINAS_DE_CULTURA_LIDAS': {k: BASE + v[0] for k, v in CULTURA_PAGINA.items()},
        'PRODUTOS_NO_CATALOGO': len(produtos),
        'POR_CATEGORIA': dict(cat),
        'FICHAS_LIDAS_POR_DENTRO': sum(1 for p in produtos if p['FICHA_LIDA']),
        'SPECIALI_ENCONTRADOS': sorted(especiais),
        'SPECIALI_ESPERADOS': 5,
        'SPECIALI_CONFIRMA': len(especiais) == 5,
        'COBERTURA_LEIA_ASSIM':
            'sao os produtos alcancados pelas 7 paginas de cultura. O catalogo pode '
            'ter mais — culturas sem pagina propria (olivo, barbabietola, drupacee) '
            'nao foram alcancadas. NAO e censo do catalogo.',
        'CULTURAS_SEM_PAGINA_NO_SITE': ['OLIVO', 'BARBABIETOLA', 'DRUPACEE', 'AGRUMI',
                                        'ORTICOLE', 'TABACCO'],
        'NOS_DOIS': nos_dois,
        'SO_NO_CATALOGO': so_cat,
        'SO_NO_CATALOGO_LEIA_ASSIM':
            'aparece no catalogo comercial e nao casou com nenhum dos 163 do registro. '
            'Pode ser nome comercial diferente, sistema (nao produto), produto novo, '
            'ou falha do nosso casamento de nome. NAO concluir que e irregular.',
        'SO_NO_REGISTRO': so_reg,
        'SO_NO_REGISTRO_LEIA_ASSIM':
            'registrado no Ministero e nao alcancado por estas 7 paginas. NAO significa '
            'descontinuado. Significa NAO SEI.',
        'AFIRMACAO_PROIBIDA': 'a ADAMA descontinuou o produto X',
        'PRODUTOS': produtos,
    }
    os.makedirs(SAIDA, exist_ok=True)
    d = os.path.join(SAIDA, 'IT-ADAMA-CATALOGO.json')
    json.dump(saida, open(d, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('produtos no catalogo: %d  (fichas lidas por dentro: %d)'
          % (len(produtos), saida['FICHAS_LIDAS_POR_DENTRO']))
    for k, v in cat.most_common():
        print('   %-14s %d' % (k, v))
    print()
    print('SPECIALI: %d %s' % (len(especiais),
                               'CONFIRMA os 5 esperados' if len(especiais) == 5
                               else '<== nao sao 5'))
    for e in sorted(especiais):
        print('   ·', e)
    print()
    print('produto por cultura:')
    for cult, (_u, s) in CULTURA_PAGINA.items():
        print('   %-10s %d' % (cult, len([x for x in s if x not in BANNER_DO_SITE])))
    print()
    print('cruzamento com os 163 do registro:')
    print('   nos dois ......... %d' % len(nos_dois))
    print('   so no catalogo ... %d' % len(so_cat))
    print('   so no registro ... %d  (NAO SEI, nunca «descontinuado»)' % len(so_reg))
    print()
    print('gravado:', os.path.relpath(d, ROOT))


if __name__ == '__main__':
    main()
