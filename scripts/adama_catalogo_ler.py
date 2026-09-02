#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LÊ O CATÁLOGO COMERCIAL DA ADAMA ITÁLIA a partir das páginas SALVAS À MÃO.

    python3 scripts/adama_catalogo_ler.py

Lê tudo que estiver em `.tmp/adama-catalogo/` (arquivos `.html` salvos com Ctrl+S)
e monta o inventário do §4 da missão LAST-MILE.

POR QUE AS PÁGINAS SÃO SALVAS À MÃO
------------------------------------
O `adama.com` usa Akamai Bot Manager. Cliente automático leva `Access Denied` com
`bm-verify` — inclusive no `robots.txt`, que devolve 403. O navegador do dono do
projeto abre tudo normalmente, porque a proteção lê o NAVEGADOR, não o país nem
o IP.

    DETECÇÃO DE ROBÔ NÃO SE CONTORNA. É limite do trabalho, não obstáculo técnico.

Então o dono abre e salva; este script só processa o que já está no disco dele.

A LEI QUE MANDA AQUI
---------------------
    CATALOG_PRODUCT e REGULATORY_PRODUCT SÃO CLASSES DIFERENTES.

Um produto pode estar registrado no Ministero e não ser comercializado. Pode estar
no catálogo com nome comercial diferente do nome do registro. Pode ser de outra
empresa do grupo.

    ⛔ NÃO INFERIR STATUS COMERCIAL A PARTIR DO REGISTRO — nem o contrário.

Por isso a saída tem três listas separadas, e nenhuma delas é subtração das outras:
`SO_NO_CATALOGO`, `SO_NO_REGISTRO` e `NOS_DOIS`. E `SO_NO_REGISTRO` sai com a
frase que impede a leitura errada: não significa descontinuado, significa NÃO SEI.
"""
import html
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(ROOT, '.tmp', 'adama-catalogo')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')
REGISTRO = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                        '01-DESIGN-READY', 'ADAMA', 'adama-italy-products.json')

CATEGORIAS = [
    ('ERBICIDI', r'erbicid'),
    ('FUNGICIDI', r'fungicid'),
    ('INSETTICIDI', r'insetticid|acaricid|aficid'),
    ('SPECIALI', r'special'),
    ('BIOSOLUTIONS', r'biosolution|biologic'),
]

# O link de ficha de produto tem sempre esta forma nos dois caminhos que o site usa.
LINK_PRODUTO = re.compile(
    r'href=["\'](?P<h>[^"\']*?/italia/it/(?:prodotti|prodotti-adama)/'
    r'(?P<cat>[a-z\-]+)/(?P<slug>[a-z0-9\-]+))["\']', re.I)

# Lixo que não é produto: compartilhamento social, âncora, categoria sem slug.
NAO_E_PRODUTO = re.compile(
    r'linkedin|facebook|twitter|whatsapp|share|mailto|^#|javascript:', re.I)


def _n(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', t or '')
                if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()


def limpa(t):
    t = re.sub(r'<sup>.*?</sup>', '', t or '', flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def categoria_de(slug_cat, texto_perto):
    for chave, rx in CATEGORIAS:
        if re.search(rx, slug_cat or '', re.I) or re.search(rx, texto_perto or '', re.I):
            return chave
    return 'NAO_SEI'


def nome_do_slug(slug):
    """`goltixr-top-0` → `GOLTIX TOP`. O `r` colado é o ® que o slug engoliu."""
    s = slug.replace('-', ' ')
    s = re.sub(r'\b(\w+)r\b', r'\1', s)          # goltixr → goltix
    s = re.sub(r'\s+\d+$', '', s)                 # sufixo de desambiguação do CMS
    return s.upper().strip()


def ler_arquivos():
    if not os.path.isdir(PASTA):
        return []
    achados = []
    for f in sorted(os.listdir(PASTA)):
        if not f.lower().endswith(('.html', '.htm', '.txt')):
            continue
        p = os.path.join(PASTA, f)
        try:
            bruto = open(p, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        achados.append((f, bruto))
    return achados


def main():
    arquivos = ler_arquivos()
    if not arquivos:
        print('nenhum arquivo em %s' % os.path.relpath(PASTA, ROOT))
        print()
        print('Salve as paginas de categoria do catalogo (Ctrl+S, «somente HTML») ali,')
        print('e rode de novo. O script le qualquer nome de arquivo.')
        return

    produtos = {}
    por_arquivo = {}
    for nome_arq, bruto in arquivos:
        n_antes = len(produtos)
        for m in LINK_PRODUTO.finditer(bruto):
            href, cat, slug = m.group('h'), m.group('cat'), m.group('slug')
            if NAO_E_PRODUTO.search(href):
                continue
            # o rótulo visível costuma estar no texto que segue o link
            trecho = bruto[m.end():m.end() + 400]
            rotulo = limpa(re.sub(r'.*?>', '', trecho, count=1).split('<')[0])[:70]
            url = href if href.startswith('http') else 'https://www.adama.com' + href
            chave = slug.lower()
            if chave not in produtos:
                produtos[chave] = {
                    'SLUG': slug,
                    'NOME_NO_CATALOGO': rotulo if len(rotulo) > 2 else nome_do_slug(slug),
                    'NOME_DEDUZIDO_DO_SLUG': nome_do_slug(slug),
                    'CATEGORIA': categoria_de(cat, bruto[max(0, m.start() - 600):m.start()]),
                    'CAMINHO_DO_SITE': cat,
                    'URL': url,
                    'VISTO_EM': [nome_arq],
                }
            elif nome_arq not in produtos[chave]['VISTO_EM']:
                produtos[chave]['VISTO_EM'].append(nome_arq)
        por_arquivo[nome_arq] = len(produtos) - n_antes

    # ── cruzamento com o registro, SEM inferir status ─────────────────────────
    reg = []
    if os.path.exists(REGISTRO):
        reg = json.load(open(REGISTRO, encoding='utf-8'))['PRODUCTS']
    reg_norm = {_n(p['PRODUCT']): p for p in reg}

    nos_dois, so_catalogo = [], []
    casados = set()
    for k, p in produtos.items():
        alvo = None
        for cand in (p['NOME_NO_CATALOGO'], p['NOME_DEDUZIDO_DO_SLUG']):
            c = _n(cand)
            if c in reg_norm:
                alvo = reg_norm[c]
                break
            # o catálogo abrevia: «GOLTIX TOP» x «GOLTIX TOP SC»
            for rn, rp in reg_norm.items():
                if c and (rn.startswith(c) or c.startswith(rn)) and abs(len(rn) - len(c)) <= 8:
                    alvo = rp
                    break
            if alvo:
                break
        if alvo:
            casados.add(_n(alvo['PRODUCT']))
            nos_dois.append(dict(p, REGISTRATION_ID=alvo['REGISTRATION_ID'],
                                 NOME_NO_REGISTRO=alvo['PRODUCT'],
                                 EXPIRY=alvo.get('EXPIRY')))
        else:
            so_catalogo.append(p)

    so_registro = [{'NOME_NO_REGISTRO': p['PRODUCT'],
                    'REGISTRATION_ID': p['REGISTRATION_ID'],
                    'EXPIRY': p.get('EXPIRY'),
                    'LINE': p.get('LINE')}
                   for p in reg if _n(p['PRODUCT']) not in casados]

    cat_conta = Counter(p['CATEGORIA'] for p in produtos.values())
    especiais = [p for p in produtos.values() if p['CATEGORIA'] == 'SPECIALI']

    saida = {
        'DATASET': 'IT-ADAMA-CATALOGO-COMERCIAL',
        'FAMILIA_DA_MISSAO': '4 · CATALOGO COMERCIAL',
        'COMO_FOI_OBTIDO': ('paginas salvas a mao pelo dono do projeto. O adama.com '
                            'usa Akamai Bot Manager e recusa cliente automatico com '
                            'Access Denied / bm-verify, inclusive no robots.txt. '
                            'Deteccao de robo nao se contorna.'),
        'ARQUIVOS_LIDOS': [{'ARQUIVO': k, 'PRODUTOS_NOVOS': v}
                           for k, v in por_arquivo.items()],
        'LEI': 'CATALOG_PRODUCT e REGULATORY_PRODUCT sao classes diferentes e nunca '
               'se misturam',
        'PRODUTOS_NO_CATALOGO': len(produtos),
        'POR_CATEGORIA': dict(cat_conta),
        'SPECIALI_ENCONTRADOS': [p['NOME_NO_CATALOGO'] for p in especiais],
        'SPECIALI_ESPERADOS': 5,
        'SPECIALI_BATE': len(especiais) == 5,
        'NOS_DOIS': nos_dois,
        'SO_NO_CATALOGO': so_catalogo,
        'SO_NO_CATALOGO_LEIA_ASSIM':
            'aparece no catalogo comercial e NAO casou com nenhum dos 163 do registro. '
            'Pode ser nome comercial diferente, produto de outra empresa do grupo, ou '
            'falha do nosso casamento de nome. NAO concluir que e irregular.',
        'SO_NO_REGISTRO': so_registro,
        'SO_NO_REGISTRO_LEIA_ASSIM':
            'esta registrado no Ministero e NAO apareceu nas paginas de catalogo que '
            'lemos. NAO significa descontinuado. Significa NAO SEI -- pode estar numa '
            'pagina que nao foi salva, ou nao ser comercializado, ou ter outro nome.',
        'AFIRMACAO_PROIBIDA': 'a ADAMA descontinuou o produto X',
    }
    os.makedirs(SAIDA, exist_ok=True)
    destino = os.path.join(SAIDA, 'IT-ADAMA-CATALOGO.json')
    json.dump(saida, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('arquivos lidos: %d' % len(arquivos))
    for k, v in por_arquivo.items():
        print('   %-52s +%d produtos' % (k[:52], v))
    print()
    print('produtos no catalogo: %d' % len(produtos))
    for k, v in cat_conta.most_common():
        print('   %-16s %d' % (k, v))
    print()
    print('SPECIALI: %d %s' % (len(especiais), '(bate com os 5 esperados)'
                               if len(especiais) == 5 else '<== NAO sao 5'))
    for p in especiais:
        print('   ·', p['NOME_NO_CATALOGO'])
    print()
    print('cruzamento com os 163 do registro:')
    print('   nos dois ......... %d' % len(nos_dois))
    print('   so no catalogo ... %d' % len(so_catalogo))
    print('   so no registro ... %d  (NAO SEI, nunca «descontinuado»)' % len(so_registro))
    print()
    print('gravado:', os.path.relpath(destino, ROOT))


if __name__ == '__main__':
    main()
