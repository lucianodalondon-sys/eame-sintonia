#!/usr/bin/env python3
"""
CATÁLOGO ADAMA FRANCE — o que a empresa APRESENTA, colhido pela porta que abre.

    python scripts/adama_fr_catalogo.py --listar        # só o índice do catálogo
    python scripts/adama_fr_catalogo.py --coletar 10    # colhe 10 produtos
    python scripts/adama_fr_catalogo.py --coletar 0     # colhe todos
    python scripts/adama_fr_catalogo.py --medir         # mede o que já está em disco

A PORTA
--------
Contra `https://www.adama.com/france/fr`, medido em 2026-08-30:

    curl com User-Agent de Chrome ....... 403, 143 bytes
    chrome --headless=new --dump-dom .... 403, 186 bytes
    Chrome COM JANELA ................... 200, a página inteira

    HTTP_ROUTE ≠ HEADLESS_ROUTE ≠ HEADED_ROUTE

Não é WAF burlado: é o mesmo navegador que qualquer pessoa usa para ler a página,
com o perfil e a porta reservados para a França. Nada de `--no-sandbox`, nada de
CAPTCHA, nada de cookie exportado.

O QUE A PAGINAÇÃO ESCONDE, E ISSO QUASE CUSTOU 35% DO CATÁLOGO
----------------------------------------------------------------
A listagem mostra três links de página: `?page=0`, `?page=1`, `?page=2`. Existem
SEIS. Parar onde o site diz que acaba traria 72 dos 111 produtos, e os 72
pareceriam o catálogo inteiro.

    VISIBLE_PAGER ≠ LAST_PAGE

Então a varredura anda até a página devolver zero produto novo, e não até o
paginador acabar.

A ARMADILHA CENTRAL DESTA FONTE
---------------------------------
Cada ficha traz DUAS listas separadas:

    Cultures ............ Blé dur d'hiver, Orge d'hiver, Triticale, ...
    Cibles principales .. Septoriose, Rouille brune, Fusarioses, ...

No AVASTEL são 10 e 10. Multiplicar dá CEM pares, e a fonte não autorizou
nenhum deles — ela nem diz que estão relacionados dois a dois. "Cibles
principales" é uma vitrine, não uma tabela de usos.

    CO_PRESENCE ≠ AUTHORIZED_PAIR

Quem quiser o par cultura×alvo francês tem de ir ao E-Phy, onde a ANSES o
publica amarrado — `Vigne*Trt Part.Aer.*Mildiou(s)`. É por isso que este arquivo
guarda as duas listas SEPARADAS e marca `PAIRS: []` com o motivo junto.

E O AMM QUE A FICHA PUBLICA
-----------------------------
A ficha traz `AMM N° : 2240236`. É ouro para o cruzamento — e continua sendo
afirmação do fabricante até a autoridade confirmar:

    MANUFACTURER_CLAIM ≠ REGULATORY_FACT

CONTAR FICHA NÃO É CONTAR REGISTRO
------------------------------------
Na amostra de dez, DUAS fichas diferentes — `Balesta` e `Gusto 3` — publicam o
MESMO AMM 2180260. No E-Phy esse AMM se chama CARAKOL 3, e o campo de segundos
nomes comerciais lista seis: OPPOSUM, SURIKATE, GUSTO 3, TASTE, ALFARO, BALESTA.

    CATALOG_ENTRY ≠ REGISTRATION
    NOME DIFERENTE ≠ REGISTRO DIFERENTE

Somar as fichas e chamar o total de "produtos registrados na França" contaria o
mesmo registro várias vezes. Os 111 são apresentações comerciais; quantos
registros distintos existem por trás disso é outra conta, e ela é feita pelo AMM.

E o inverso também mordeu: cinco dos dez nomes de catálogo NÃO são o nome
registrado. Casar por nome sem olhar os segundos nomes erraria metade — e o erro
sairia como "registro não provado", que tem cara de prudência.
"""
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import adama_fr as fr                                            # noqa: E402
import navegador as nav                                          # noqa: E402
from runtime_python import conferir_saida                        # noqa: E402

COUNTRY = 'FR'
SCRIPT_VERSION = 'adama_fr_catalogo-v1-2026-08-30'
BASE = 'https://www.adama.com'
LISTAGEM = BASE + '/france/fr/produits/protection-cultures'
# Trava de segurança: a varredura para quando uma página não traz produto novo.
# Este número existe só para o caso de o site paginar para sempre.
MAX_PAGINAS = 40

RAW = os.path.join(ROOT, 'data', 'raw', COUNTRY, 'adama-website')
PAGINAS = os.path.join(RAW, 'paginas')
DOCUMENTOS = os.path.join(RAW, 'documentos')
INDICE = os.path.join(RAW, 'INDICE-CATALOGO.json')
MANIFESTO = os.path.join(RAW, 'MANIFESTO-CATALOGO.json')

# Campos do Drupal. O site nomeia os próprios campos, e ler por nome é muito mais
# estável do que contar posição de div.
CAMPOS = {
    'CATEGORY': '.field--name-treatment',
    'ACTIVE_INGREDIENT': '.field--name-active-ingredients',
    'FORMULATION': '.field--name-formulation-type',
    'CROPS': '.field--name-crops',
    'KEY_TARGETS': '.field--name-key-targets',
    'SUBTITLE': '.field--name-product-subtitle',
}

_AMM = re.compile(r'AMM\s*N[°ºo]?\s*:?\s*([0-9]{6,9})', re.I)
_COND = re.compile(r'Conditionnement\(s\)\s*:?\s*([^\n]{1,120})', re.I)


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def _sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _slug(url):
    partes = [x for x in urllib.parse.urlparse(url).path.split('/') if x]
    return '-'.join(partes[-2:]) if len(partes) >= 2 else (partes[-1] if partes else 'produto')


_ILEGAIS_NOME = re.compile(r'[^A-Za-z0-9._-]+')


def nome_local_documento(url):
    """Nome de arquivo em disco ÚNICO POR URL.

    A primeira versão nomeava o arquivo com `<ficha>__<basename da URL>`. A rota
    de documentos da ADAMA France é `/france/fr/media/NNNN/download?attachment`,
    e o basename dela é literalmente `download` para TODOS os documentos. Quatro
    documentos diferentes na mesma ficha viravam quatro gravações no MESMO
    arquivo, e sobrava o último.

    Medido: 153 referências, 122 URLs distintas, e apenas 100 arquivos em disco.
    53 conteúdos baixados foram apagados por cima — e o manifesto seguia
    afirmando 153, porque cada um tinha sido hasheado ANTES de ser sobrescrito.
    O manifesto estava certo sobre o passado e errado sobre o disco.

        DOWNLOADED ≠ STILL ON DISK

    Agora o nome sai da URL inteira, com um sufixo de hash dela: duas fichas que
    apontam para o MESMO documento continuam compartilhando um arquivo só (é o
    mesmo documento), e dois documentos diferentes nunca dividem nome.
    """
    u = urllib.parse.urlparse(url)
    partes = [x for x in urllib.parse.unquote(u.path).split('/') if x]
    base = partes[-1] if partes else 'documento'
    raiz, ext = os.path.splitext(base)
    ext = _ILEGAIS_NOME.sub('', ext)[:12] or '.pdf'
    trilha = '-'.join(partes[-2:]) if len(partes) >= 2 else base
    trilha = _ILEGAIS_NOME.sub('-', trilha).strip('-')[:60] or 'documento'
    digest = hashlib.sha256(url.encode('utf-8')).hexdigest()[:10]
    return '%s-%s%s' % (trilha, digest, ext)


# ══════════════════════════════════════════════════════════════════════════════
# 1 · A JANELA — Chrome de verdade, perfil e porta da França
# ══════════════════════════════════════════════════════════════════════════════

def abrir(p):
    """Contexto do Chrome com o perfil francês. O PID sai anotado."""
    ctx = p.chromium.launch_persistent_context(
        nav.perfil(COUNTRY), headless=False, channel='chrome',
        args=['--remote-debugging-port=%d' % nav.porta(COUNTRY),
              '--no-first-run', '--no-default-browser-check'])
    return ctx


def _pids():
    """Quem está rodando com o perfil francês. Registrado antes de coletar."""
    try:
        import subprocess
        r = subprocess.run(
            ['powershell.exe', '-NoProfile', '-Command',
             "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | "
             "Where-Object { $_.CommandLine -match 'sintonia-browser.fr' } | "
             "Select-Object -ExpandProperty ProcessId"],
            capture_output=True, text=True, timeout=60)
        return [int(x) for x in r.stdout.split() if x.strip().isdigit()]
    except Exception:                                             # noqa: BLE001
        return []


# ══════════════════════════════════════════════════════════════════════════════
# 2 · A LISTAGEM — anda até secar, não até o paginador acabar
# ══════════════════════════════════════════════════════════════════════════════

def _e_pagina_de_produto(url):
    """/france/fr/protection-des-cultures/<categoria>/<produto> — cinco pedaços."""
    u = urllib.parse.urlparse(url)
    if 'adama.com' not in u.netloc:
        return False
    partes = [x for x in u.path.split('/') if x]
    return (len(partes) == 5 and partes[0] == 'france'
            and partes[2] == 'protection-des-cultures')


def listar(pagina):
    """Índice do catálogo. Devolve produtos e a prova de que a varredura secou."""
    achados = {}
    paginas = []
    n = 0
    while n < MAX_PAGINAS:
        r = pagina.goto('%s?page=%d' % (LISTAGEM, n), wait_until='networkidle',
                        timeout=180000)
        hrefs = pagina.eval_on_selector_all('a[href]', 'e=>e.map(x=>x.href)')
        nesta = {h.split('?')[0].split('#')[0] for h in hrefs if _e_pagina_de_produto(h)}
        antes = len(achados)
        for h in nesta:
            achados.setdefault(h, n)
        paginas.append({'PAGE': n, 'HTTP': r.status if r else None,
                        'PRODUCTS_ON_PAGE': len(nesta),
                        'NEW': len(achados) - antes})
        if not nesta:
            break
        n += 1
    return {
        'SOURCE': fr.FONTE_CATALOGO['SOURCE_ID'],
        'LISTING_URL': LISTAGEM,
        'CAPTURED_AT': agora(),
        'PAGES_WALKED': len(paginas),
        'PAGES': paginas,
        'SWEEP_ENDED_BY': ('página vazia' if n < MAX_PAGINAS else 'trava MAX_PAGINAS'),
        'CATALOG_PRODUCTS': len(achados),
        'PRODUCTS': [{'URL': u, 'FOUND_ON_PAGE': p,
                      'CATEGORY_FROM_PATH': urllib.parse.urlparse(u).path.split('/')[4],
                      'SLUG': _slug(u)}
                     for u, p in sorted(achados.items())],
    }


# ══════════════════════════════════════════════════════════════════════════════
# 3 · A FICHA — o que a fonte diz, e nada além
# ══════════════════════════════════════════════════════════════════════════════

_JS_CAMPOS = """(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const itens = [...el.querySelectorAll('li, a, .field__item, .paragraph')]
      .map(x => (x.textContent||'').trim()).filter(Boolean);
  const unicos = [...new Set(itens)];
  return {texto: (el.textContent||'').trim(), itens: unicos};
}"""

_JS_DOCS = """() => [...document.querySelectorAll('a[href]')]
   .map(a => ({href: a.href, texto: (a.textContent||'').trim()}))
   .filter(d => /\\.pdf(\\?|$)|\\/media\\/\\d+\\/download|product-documents/i.test(d.href))"""


def ficha(pagina, url):
    """Colhe uma ficha. As duas listas saem SEPARADAS, e o par sai vazio."""
    r = pagina.goto(url, wait_until='networkidle', timeout=180000)
    html = pagina.content()
    texto = pagina.inner_text('body')

    campos = {}
    for chave, sel in CAMPOS.items():
        campos[chave] = pagina.evaluate(_JS_CAMPOS, sel)

    amm = _AMM.search(texto)
    cond = _COND.search(texto)
    docs = pagina.evaluate(_JS_DOCS)

    crops = (campos.get('CROPS') or {}).get('itens') or []
    alvos = (campos.get('KEY_TARGETS') or {}).get('itens') or []

    return {
        'SOURCE': fr.FONTE_CATALOGO['SOURCE_ID'],
        'SOURCE_ROLE': fr.FONTE_CATALOGO['ROLE'],
        'URL': url,
        'HTTP': r.status if r else None,
        'CAPTURED_AT': agora(),
        # O bruto fica, sempre. O limpo é derivado, e derivação que apaga a
        # origem tira de quem vier depois a chance de descobrir que ela errou.
        'PAGE_TITLE_RAW': (pagina.title() or '').strip(),
        'PRODUCT_NAME': fr.nome_comercial((pagina.title() or '').split('|')[0]),
        'CATEGORY': (campos.get('CATEGORY') or {}).get('texto'),
        'CATEGORY_FROM_PATH': urllib.parse.urlparse(url).path.split('/')[4],
        'SUBTITLE': (campos.get('SUBTITLE') or {}).get('texto'),
        'ACTIVE_INGREDIENT_PUBLISHED': (campos.get('ACTIVE_INGREDIENT') or {}).get('texto'),
        'FORMULATION': (campos.get('FORMULATION') or {}).get('texto'),
        'REGISTRATION_ID_CLAIMED': amm.group(1) if amm else None,
        'REGISTRATION_CLAIM_STATE': ('MANUFACTURER_CLAIM' if amm else 'NOT_PUBLISHED'),
        'PACKAGING': cond.group(1).strip() if cond else None,
        'CROPS_LISTED': crops,
        'KEY_TARGETS_LISTED': alvos,
        'CROP_RELATION_ORIGIN': fr.CROP_DECLARED,
        'CROP_ISSUE_PAIRS': {
            'PAIRS': [],
            'STATE': 'NOT_ANCHORED_BY_SOURCE',
            'CROPS_AVAILABLE': len(crops),
            'ISSUES_AVAILABLE': len(alvos),
            'CARTESIAN_WOULD_BE': len(crops) * len(alvos),
            'WHY': ('a ficha traz duas listas e NÃO diz qual alvo vale para qual '
                    'cultura. CO_PRESENCE ≠ AUTHORIZED_PAIR. O par francês existe '
                    'no E-Phy, amarrado pela ANSES'),
        },
        'DOSES': {'STATE': 'NOT_PUBLISHED_IN_CATALOG',
                  'WHY': 'a ficha não publica dose; a dose está no E-Phy e no rótulo'},
        'APPLICATION_WINDOWS': {'STATE': 'NOT_PUBLISHED_IN_CATALOG',
                                'WHY': 'a ficha não publica BBCH nem janela'},
        'DOCUMENTS': [{'URL': d['href'], 'LINK_TEXT': d['texto'],
                       'DOC_TYPE': fr.tipo_de_documento(d['texto'] or d['href'])}
                      for d in {x['href']: x for x in docs}.values()],
        'PORTFOLIO_COUNTRY': COUNTRY,
        'HTML_BYTES': len(html.encode('utf-8')),
        'HTML_SHA256': _sha_bytes(html.encode('utf-8')),
    }, html


# ══════════════════════════════════════════════════════════════════════════════
# 4 · RAW — o plano nasce com o arquivo, não depois
# ══════════════════════════════════════════════════════════════════════════════

def _gravar(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'wb') as fh:
        fh.write(dados)
    return {'BYTES': len(dados), 'SHA256': _sha_bytes(dados)}


def _amm_da_chave(amms):
    """Qual AMM abre o caminho de um documento compartilhado por várias fichas.

    Um PDF citado por oito fichas de AMMs diferentes não pertence a nenhum deles
    em particular. Escolher o primeiro seria arbitrário e pareceria um fato.
    """
    distintos = sorted({a for a in amms if a})
    if not distintos:
        return 'SEM-AMM'
    if len(distintos) == 1:
        return distintos[0]
    return 'PARTAGE'


def baixar_documento(ctx, url, referencias):
    """Baixa UM documento e pendura nele todas as fichas que o citam.

    `referencias` são as fichas que apontam para esta URL — porque um documento
    pode cobrir mais de um produto:

        1 PDF ≠ 1 ficha ≠ 1 AMM

    Medido: 7 URLs são citadas por mais de uma ficha, e uma delas aparece em
    OITO. Baixar uma vez por ficha duplicaria a evidência e faria parecer que há
    oito documentos onde há um.
    """
    doc_type = fr.tipo_de_documento(
        (referencias[0].get('LINK_TEXT') or '') + ' ' + url)
    amms = [r.get('AMM') for r in referencias]
    base = {
        'URL': url,
        'DOC_TYPE_FROM_NAME': doc_type,
        'REFERENCED_BY': referencias,
        'CATALOG_PAGE_COUNT': len(referencias),
        'CATALOG_NAMES': sorted({r.get('CATALOG_NAME') for r in referencias
                                 if r.get('CATALOG_NAME')}),
        'AMMS_FROM_REFERRING_PAGES': sorted({a for a in amms if a}),
        'COUNTRY': COUNTRY,
    }
    try:
        resp = ctx.request.get(url, timeout=180000)
    except Exception as e:                                        # noqa: BLE001
        return dict(base, STATE='FAILED', WHY=str(e)[:160])
    if resp.status != 200:
        return dict(base, STATE='FAILED', HTTP=resp.status,
                    WHY='a rota do documento respondeu %d' % resp.status)
    corpo = resp.body()
    nome_url = urllib.parse.unquote(
        os.path.basename(urllib.parse.urlparse(url).path)) or 'documento.pdf'
    destino = os.path.join(DOCUMENTOS, nome_local_documento(url))
    medido = _gravar(destino, corpo)
    return dict(base, STATE='LOCAL_ONLY', HTTP=200,
                ORIGINAL_FILENAME=nome_url,
                CONTENT_TYPE=(resp.headers or {}).get('content-type'),
                LOCAL_PATH=os.path.relpath(destino, ROOT),
                RELATED_REGISTRATION=_amm_da_chave(amms),
                # A chave é aberta pelo sha do CONTEÚDO: a rota
                # `/media/NNNN/download` dá o nome "download" a 122 PDFs
                # diferentes, e chave por nome os empilharia num objeto só.
                STORAGE_KEY=fr.storage_key(COUNTRY, _amm_da_chave(amms), doc_type,
                                           nome_url, medido['SHA256']),
                CAPTURED_AT=agora(), **medido)


def referencias_de_documento(fichas):
    """→ {URL: [referências]}. Uma entrada por documento, não por citação."""
    porurl = {}
    for f in fichas:
        for d in f.get('DOCUMENTS') or []:
            porurl.setdefault(d['URL'], []).append({
                'PAGE_URL': f['URL'],
                'CATALOG_NAME': f.get('PRODUCT_NAME'),
                'AMM': f.get('REGISTRATION_ID_CLAIMED'),
                'LINK_TEXT': d.get('LINK_TEXT'),
            })
    return porurl


def baixar_documentos(ctx, porurl):
    fora = []
    for i, (url, refs) in enumerate(sorted(porurl.items()), 1):
        d = baixar_documentos_um(ctx, url, refs)
        fora.append(d)
        if i % 20 == 0 or i == len(porurl):
            print('  documentos %d/%d' % (i, len(porurl)))
    return fora


def baixar_documentos_um(ctx, url, refs):
    return baixar_documento(ctx, url, refs)


def rebaixar_documentos():
    """Refaz SÓ os documentos, a partir das fichas já capturadas.

    Existe porque o defeito de nome fez 53 conteúdos serem gravados por cima. As
    111 fichas em disco estão intactas — o slug delas é único — então recensear
    o catálogo inteiro seria refazer 111 páginas boas para consertar documentos.
    """
    from playwright.sync_api import sync_playwright
    with open(MANIFESTO, encoding='utf-8') as fh:
        m = json.load(fh)
    porurl = referencias_de_documento(m['PRODUCTS'])
    print('referências:', sum(len(v) for v in porurl.values()),
          '| URLs distintas:', len(porurl))
    os.makedirs(DOCUMENTOS, exist_ok=True)
    with sync_playwright() as p:
        ctx = abrir(p)
        pids = _pids()
        print('PID do Chrome frances:', pids or '(nao medido)')
        documentos = baixar_documentos(ctx, porurl)
        ctx.close()
    m['DOCUMENTS'] = documentos
    m['DOCUMENT_REFERENCES'] = sum(len(v) for v in porurl.values())
    m['DOCUMENTS_DISTINCT_URLS'] = len(porurl)
    m['CAPTURED_AT'] = agora()
    with open(MANIFESTO, 'w', encoding='utf-8') as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1)
    return m


def coletar(quantos=10):
    from playwright.sync_api import sync_playwright
    os.makedirs(PAGINAS, exist_ok=True)
    os.makedirs(DOCUMENTOS, exist_ok=True)

    with sync_playwright() as p:
        ctx = abrir(p)
        pids = _pids()
        print('PID do Chrome frances:', pids or '(nao medido)')
        pg = ctx.new_page()

        print('varrendo a listagem...')
        indice = listar(pg)
        indice['CHROME_PIDS'] = pids
        with open(INDICE, 'w', encoding='utf-8') as fh:
            json.dump(indice, fh, ensure_ascii=False, indent=1)
        print('  paginas andadas :', indice['PAGES_WALKED'])
        print('  produtos        :', indice['CATALOG_PRODUCTS'])

        alvos = indice['PRODUCTS'] if quantos == 0 else indice['PRODUCTS'][:quantos]
        # Amostra de categorias diferentes quando o recorte é pequeno: dez
        # herbicidas seguidos não testam o parser contra o resto do catálogo.
        if quantos and quantos < indice['CATALOG_PRODUCTS']:
            alvos = _amostra_diversa(indice['PRODUCTS'], quantos)

        fichas = []
        for i, alvo in enumerate(alvos, 1):
            f, html = ficha(pg, alvo['URL'])
            caminho = os.path.join(PAGINAS, alvo['SLUG'] + '.html')
            _gravar(caminho, html.encode('utf-8'))
            f['LOCAL_PATH'] = os.path.relpath(caminho, ROOT)
            f['STORAGE_KEY'] = fr.storage_key(
                COUNTRY, f['REGISTRATION_ID_CLAIMED'], 'PAGE_CAPTURE',
                alvo['SLUG'] + '.html', f['HTML_SHA256'])
            fichas.append(f)
            print('  %2d/%d  %-22s AMM %-9s culturas %2d  alvos %2d  docs %d'
                  % (i, len(alvos), f['PRODUCT_NAME'][:22],
                     f['REGISTRATION_ID_CLAIMED'] or '-',
                     len(f['CROPS_LISTED']), len(f['KEY_TARGETS_LISTED']),
                     len(f['DOCUMENTS'])))

        # Documentos DEPOIS das fichas, e uma vez por URL — não uma por citação.
        documentos = baixar_documentos(ctx, referencias_de_documento(fichas))
        ctx.close()

    manifesto = {
        'SOURCE': fr.FONTE_CATALOGO,
        'SCRIPT_VERSION': SCRIPT_VERSION,
        'CAPTURED_AT': agora(),
        'ROUTE': 'HEADED_BROWSER_ONLY',
        'CHROME_PIDS': pids,
        'CATALOG_PRODUCTS': indice['CATALOG_PRODUCTS'],
        'PRODUCTS_CAPTURED': len(fichas),
        'PRODUCTS': fichas,
        'DOCUMENT_REFERENCES': sum(len(f.get('DOCUMENTS') or []) for f in fichas),
        'DOCUMENTS_DISTINCT_URLS': len(documentos),
        'DOCUMENTS': documentos,
    }
    with open(MANIFESTO, 'w', encoding='utf-8') as fh:
        json.dump(manifesto, fh, ensure_ascii=False, indent=1)
    return manifesto


def _amostra_diversa(produtos, quantos):
    """Um de cada categoria primeiro, e só depois repete categoria.

    Dez herbicidas seguidos provariam o parser contra um molde só. A missão pediu
    categorias diferentes de propósito.
    """
    porcat = {}
    for p in produtos:
        porcat.setdefault(p['CATEGORY_FROM_PATH'], []).append(p)
    fora, rodada = [], 0
    while len(fora) < quantos:
        acrescentou = False
        for cat in sorted(porcat):
            if rodada < len(porcat[cat]) and len(fora) < quantos:
                fora.append(porcat[cat][rodada])
                acrescentou = True
        if not acrescentou:
            break
        rodada += 1
    return fora


def medir():
    if not os.path.isfile(MANIFESTO):
        return {'STATE': 'NOT_COLLECTED', 'WHY': 'não há manifesto em disco'}
    with open(MANIFESTO, encoding='utf-8') as fh:
        m = json.load(fh)
    locais = [os.path.join(ROOT, p['LOCAL_PATH']) for p in m['PRODUCTS']]
    locais += [os.path.join(ROOT, d['LOCAL_PATH']) for d in m['DOCUMENTS']
               if d.get('LOCAL_PATH')]
    pos = conferir_saida(caminhos=locais, exit_code=0, contagem=len(m['PRODUCTS']))
    baixados = [d for d in m['DOCUMENTS'] if d.get('LOCAL_PATH')]
    return {
        'CATALOG_PRODUCTS': m['CATALOG_PRODUCTS'],
        'PRODUCTS_CAPTURED': m['PRODUCTS_CAPTURED'],
        'PRODUCTS_WITH_AMM_CLAIM': sum(1 for p in m['PRODUCTS']
                                       if p['REGISTRATION_ID_CLAIMED']),
        'DOCUMENTS_FOUND': len(m['DOCUMENTS']),
        'DOCUMENTS_DOWNLOADED': len(baixados),
        'DOCUMENTS_FAILED': sum(1 for d in m['DOCUMENTS'] if d.get('STATE') == 'FAILED'),
        'RAW_EXPECTED': len(locais),
        'RAW_BYTES': sum(os.path.getsize(c) for c in locais if os.path.isfile(c)),
        'LARGEST_ASSET_BYTES': max([os.path.getsize(c) for c in locais
                                    if os.path.isfile(c)] or [0]),
        'CROP_ISSUE_PAIRS_CREATED': sum(len(p['CROP_ISSUE_PAIRS']['PAIRS'])
                                        for p in m['PRODUCTS']),
        'CARTESIAN_AVOIDED': sum(p['CROP_ISSUE_PAIRS']['CARTESIAN_WOULD_BE']
                                 for p in m['PRODUCTS']),
        'POSTCONDITION': pos,
    }


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else '--medir'
    if modo == '--listar':
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            ctx = abrir(p)
            i = listar(ctx.new_page())
            ctx.close()
        os.makedirs(RAW, exist_ok=True)
        with open(INDICE, 'w', encoding='utf-8') as fh:
            json.dump(i, fh, ensure_ascii=False, indent=1)
        print('CATALOG_PRODUCTS:', i['CATALOG_PRODUCTS'],
              '| paginas:', i['PAGES_WALKED'])
        return 0
    if modo == '--documentos':
        rebaixar_documentos()
    elif modo == '--coletar':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        coletar(n)
    m = medir()
    for k, v in m.items():
        if k == 'POSTCONDITION':
            print('%-26s : %s' % (k, v['STATE']))
            continue
        print('%-26s : %s' % (k, v))
    return 0


if __name__ == '__main__':
    sys.exit(main())
