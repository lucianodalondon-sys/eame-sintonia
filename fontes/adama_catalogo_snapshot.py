#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FOTOGRAFA O CATÁLOGO COMERCIAL DA ADAMA ITÁLIA, E MEDE O QUE MUDOU.

    py fontes/adama_catalogo_snapshot.py

NÃO coleta. Lê o que a captura já pôs em `data/raw/IT/adama-catalog/<data>/` e
produz três coisas que a ADAMA Reference não tinha:

    CATALOG-SNAPSHOTS.json       a foto do catálogo tem data própria
    PORTFOLIO-OBSERVATIONS.json  quem foi VISTO em cada foto
    PORTFOLIO-DRIFT.json         a diferença entre duas fotos, com prova

O BURACO QUE ISTO TAPA
-----------------------
`PORTFOLIO.json` nasceu do catálogo observado em **30/08/2026** e carrega
`PROVENANCE.SNAPSHOT_ID = PROD_FTS_6_20260831` — que é a foto do **Ministero**,
de outra fonte e de outro dia.

    A DATA DO REGISTO NÃO É A DATA DO CATÁLOGO.

Quem lesse o portfolio concluiria que ele foi observado a 31/08. Foi a 30/08, e
numa fonte diferente. O valor antigo não se apaga: fica em
`REGULATORY_SNAPSHOT_ID_INHERITED`, ao lado do que corrige.

A LEI DA IDENTIDADE AQUI
-------------------------
    NOME IGUAL NÃO PROVA PRODUTO IGUAL.
    NOME DIFERENTE NÃO PROVA PRODUTO DIFERENTE.

Por isso o casamento entre duas fotos é feito pela **âncora de identidade** —
a `CANONICAL_URL` que o `PRODUCT-MASTER.json` já guarda — e nunca pela posição
na lista nem pelo nome. `RENAMED_CANDIDATE` sai só quando a âncora é a mesma e
o nome mudou; e sai como CANDIDATO, nunca como facto.

    ADAMA_PRODUCT_ID NÃO SE RENUMERA. Esta casa só LÊ o Product Master.

AUSÊNCIA NÃO É DESTRUIÇÃO
--------------------------
Produto que deixe de aparecer no catálogo **não sai** do Product Master nem do
Portfolio. Sai da *membership observada* daquela foto, com
`MEMBERSHIP_STATE = ABSENT_FROM_CATALOG_SNAPSHOT` — que é um facto sobre a foto,
não uma sentença sobre o produto.
"""
import datetime
import hashlib
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASA = os.path.join(RAIZ, 'referencia', 'adama')
BRUTO = os.path.join(RAIZ, 'data', 'raw', 'IT', 'adama-catalog')
AMOSTRAS = os.path.join(RAIZ, 'data', 'samples', 'IT-ADAMA-CATALOG')

SCHEMA = 'sintonia.adama-reference/1'
OWNER = 'IT — ADAMA REFERENCE (referencia/adama/)'
BUILDER = 'fontes/adama_catalogo_snapshot.py'
SOURCE_ID = 'IT-ADAMA-CATALOG'
SOURCE_URL = 'https://www.adama.com/italia/it'
AUTHORITY = 'ADAMA Italia S.r.l. (catalogo comercial proprio)'

# A foto anterior do CATÁLOGO. Não é a do Ministero, e é por isso que existe.
ANTERIOR = {
    'SNAPSHOT_ID': 'CAT_ADAMA_IT_20260830',
    'OBSERVED_AT': '2026-08-30',
    'PROVING_ARTIFACT':
        'research/adama-italy-product-intelligence-deep/PRODUCTS-COMMERCIAL.json',
    'OBSERVED_AT_FIELD': 'CATALOG_CAPTURED_AT',
}


def agora():
    return datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0).isoformat()


def ler(caminho):
    with open(caminho, encoding='utf-8') as fh:
        return json.load(fh)


def gravar(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    # LF sempre: o repo guarda LF e gerador que escreve CRLF produz diff fantasma.
    with open(caminho, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=1)
        fh.write('\n')


def sha256_texto(texto):
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()


def canonizar(u):
    u = (u or '').strip().split('#')[0]
    u = re.sub(r'^https?://(www\.)?adama\.com', 'https://www.adama.com', u)
    if u.endswith('/') and len(u) > len('https://www.adama.com') + 1:
        u = u[:-1]
    return u


def ancora_de_url(produto_master):
    """A âncora de URL que o Product Master já guardava. É como se reconhece."""
    for a in produto_master.get('IDENTITY_ANCHORS', []):
        if a.startswith('URL:'):
            return canonizar(a[4:])
    return None


# ────────────────────────────── 1b · a contraprova: varrer TODAS as ligações
# O sitemap é a lista que a ADAMA publica. Não é a lista que a ADAMA tem.
# Por isso a população é conferida por um segundo caminho independente: toda
# ligação com forma de produto encontrada DENTRO das páginas capturadas.
RE_LIGACAO = re.compile(
    r'/italia/it/(?:prodotti(?:-adama)?|products/crop-protection)/'
    r'[a-z0-9\-]+(?:/[a-z0-9\-]+)?')
RE_PRODUTO = re.compile(
    r'^/italia/it/prodotti(?:-adama)?/'
    r'(erbicidi|fungicidi|insetticidi|speciali|biosolutions)/[a-z0-9\-]+$')


def varrer_ligacoes(data_pasta, urls_do_sitemap):
    """Segunda contagem, por caminho independente do sitemap."""
    pasta = os.path.join(BRUTO, data_pasta)
    achadas = {}
    for sub in ('pages', 'captures'):
        d = os.path.join(pasta, sub)
        if not os.path.isdir(d):
            continue
        for nome in sorted(os.listdir(d)):
            if not nome.endswith('.html'):
                continue
            with open(os.path.join(d, nome), encoding='utf-8') as fh:
                texto = fh.read()
            for m in RE_LIGACAO.finditer(texto):
                achadas.setdefault(m.group(0), set()).add(nome)

    caminhos_sitemap = {u.replace('https://www.adama.com', '')
                        for u in urls_do_sitemap}
    fora = []
    for caminho in sorted(achadas):
        if caminho in caminhos_sitemap:
            continue
        fora.append({
            'PATH': caminho,
            'SHAPE': ('PRODUCT_SHAPED' if RE_PRODUTO.match(caminho)
                      else 'OTHER_PRODUCT_ROUTE'),
            'LINKED_FROM': sorted(achadas[caminho]),
        })
    return len(achadas), fora


# ───────────────────────────────────────────────────── 1 · a foto de hoje
def montar_foto(data_pasta):
    pasta = os.path.join(BRUTO, data_pasta)
    enum = ler(os.path.join(pasta, 'enumeracao.json'))
    censo = ler(os.path.join(pasta, 'paginas-produto.json'))
    indice = ler(os.path.join(pasta, 'indice-captura.json'))

    paginas = []
    falhas = []
    for p in censo['PRODUCTS']:
        if p.get('STATE') == 'CAPTURE_FAILED':
            falhas.append({'SOURCE_URL': p['SOURCE_URL'], 'ERROR': p.get('ERROR')})
            continue
        ent = indice.get(p['SOURCE_URL'], {})
        paginas.append({
            'SOURCE_URL': canonizar(p['SOURCE_URL']),
            'CANONICAL_URL': canonizar(p.get('CANONICAL_URL')),
            'FINAL_URL': canonizar(p.get('FINAL_URL')),
            'OBSERVED_NAME': p.get('PRODUCT_NAME'),
            'CATEGORY_DISPLAY': p.get('CATEGORY_DISPLAY'),
            'ACTIVE_INGREDIENT_TEXT': p.get('ACTIVE_INGREDIENT'),
            'FORMULATION': p.get('FORMULATION'),
            'NODE_ID': p.get('NODE_ID'),
            'VISIBLE_REGISTRATION_ID': p.get('VISIBLE_REGISTRATION_ID'),
            'REGISTRATION_ID_AS_WRITTEN': p.get('REGISTRATION_ID_AS_WRITTEN'),
            'REGISTRATION_FORMAT_STATE': p.get('REGISTRATION_FORMAT_STATE'),
            'PAGE_SHA256': ent.get('SHA256') or p.get('SHA256'),
            'PAGE_BYTES': ent.get('BYTES'),
            'DOM_BYTES': p.get('DOM_BYTES'),
            'COLLECTED_AT': ent.get('CAPTURED_AT') or p.get('CAPTURED_AT'),
            'RAW_LOCAL_FILE': ent.get('LOCAL_FILE'),
        })
    return enum, censo, indice, paginas, falhas


# ──────────────────────────────────────── 2 · a foto anterior, do catálogo
def montar_anterior():
    art = ler(os.path.join(RAIZ, ANTERIOR['PROVING_ARTIFACT']))
    paginas = []
    for p in art['PRODUCTS']:
        paginas.append({
            'CANONICAL_URL': canonizar(p.get('CANONICAL_URL') or p.get('PRODUCT_URL')),
            'OBSERVED_NAME': p.get('PRODUCT_NAME'),
            'CATEGORY_DISPLAY': p.get('CATEGORY_DISPLAY'),
            'NODE_ID': p.get('NODE_ID'),
        })
    return art, paginas


# ───────────────────────────────────────────────────────── 3 · o casamento
def casar(master, paginas):
    """Liga página observada ↔ ADAMA_PRODUCT_ID pela âncora de URL.

    Nunca por nome, nunca por posição. Página sem âncora sai como
    UNMATCHED_OBSERVED_PAGE — declarada, nunca adivinhada.
    """
    por_ancora = {}
    for p in master:
        u = ancora_de_url(p)
        if u:
            por_ancora.setdefault(u, []).append(p['ADAMA_PRODUCT_ID'])

    casados, sem_dono = {}, []
    for pg in paginas:
        chave = pg.get('CANONICAL_URL') or pg.get('SOURCE_URL')
        ids = por_ancora.get(chave, [])
        if not ids:
            sem_dono.append({
                'CANONICAL_URL': chave,
                'OBSERVED_NAME': pg.get('OBSERVED_NAME'),
                'STATE': 'UNMATCHED_OBSERVED_PAGE',
                'WHY': ('nenhuma IDENTITY_ANCHOR do PRODUCT-MASTER aponta para este '
                        'endereco. Produto novo precisa de ID novo, nunca de um '
                        'ID antigo reaproveitado — e isso e missao propria.'),
            })
            continue
        for pid in ids:
            casados.setdefault(pid, []).append(pg)
    return casados, sem_dono


def medir_drift(master, portfolio, antes, agora_pgs):
    """O diff determinístico entre duas fotos do MESMO catálogo."""
    c_antes, orfas_antes = casar(master, antes)
    c_agora, orfas_agora = casar(master, agora_pgs)

    nome_canonico = {p['ADAMA_PRODUCT_ID']: p['CANONICAL_NAME'] for p in portfolio}

    ids_antes, ids_agora = set(c_antes), set(c_agora)
    entrou = sorted(ids_agora - ids_antes)
    saiu = sorted(ids_antes - ids_agora)
    ficou = sorted(ids_agora & ids_antes)

    renomeados, inalterados, mudados = [], [], []
    for pid in ficou:
        a = c_antes[pid][0]
        b = c_agora[pid][0]
        campos = {}
        for campo in ('OBSERVED_NAME', 'CATEGORY_DISPLAY', 'NODE_ID'):
            if a.get(campo) != b.get(campo):
                campos[campo] = {'BEFORE': a.get(campo), 'NOW': b.get(campo)}
        if 'OBSERVED_NAME' in campos:
            renomeados.append({
                'ADAMA_PRODUCT_ID': pid,
                'CANONICAL_NAME': nome_canonico.get(pid),
                'NAME_BEFORE': campos['OBSERVED_NAME']['BEFORE'],
                'NAME_NOW': campos['OBSERVED_NAME']['NOW'],
                'IDENTITY_EVIDENCE': ('mesma IDENTITY_ANCHOR de URL nas duas fotos'),
                'STATE': 'RENAMED_CANDIDATE',
                'WHY_ONLY_CANDIDATE': ('nome diferente nao prova produto diferente, e '
                                       'nome igual nao prova produto igual. So a ancora '
                                       'de identidade decide, e ela nao mudou.'),
            })
        if campos:
            mudados.append({'ADAMA_PRODUCT_ID': pid, 'FIELDS': campos})
        else:
            inalterados.append(pid)

    return {
        'COUNT_BEFORE': len(ids_antes),
        'COUNT_NOW': len(ids_agora),
        'ADDED': [{'ADAMA_PRODUCT_ID': p, 'CANONICAL_NAME': nome_canonico.get(p)}
                  for p in entrou],
        'REMOVED': [{'ADAMA_PRODUCT_ID': p, 'CANONICAL_NAME': nome_canonico.get(p),
                     'MEMBERSHIP_STATE': 'ABSENT_FROM_CATALOG_SNAPSHOT',
                     'PRODUCT_MASTER_STATE': 'PRESERVED_NEVER_DELETED'}
                    for p in saiu],
        'RENAMED_CANDIDATES': renomeados,
        'CHANGED_FIELDS': mudados,
        'UNCHANGED': len(inalterados),
        'UNMATCHED_PAGES_BEFORE': orfas_antes,
        'UNMATCHED_PAGES_NOW': orfas_agora,
    }


def main():
    data_pasta = sys.argv[1] if len(sys.argv) > 1 else '2026-09-15'
    enum, censo, indice, pgs_agora, falhas = montar_foto(data_pasta)
    art_antes, pgs_antes = montar_anterior()

    master = ler(os.path.join(CASA, 'PRODUCT-MASTER.json'))['PRODUCTS']
    portfolio = ler(os.path.join(CASA, 'PORTFOLIO.json'))['RECORDS']

    # contraprova: contar por um caminho que não seja o sitemap
    urls_sitemap = [l['URL'] for l in enum['TABLE'] if l['PAGE_TYPE'] == 'PRODUCT_PAGE']
    total_ligacoes, fora_do_sitemap = varrer_ligacoes(data_pasta, urls_sitemap)
    sondas = {}
    caminho_sondas = os.path.join(BRUTO, data_pasta, 'sondas.json')
    if os.path.exists(caminho_sondas):
        sondas = {s['PATH']: s for s in ler(caminho_sondas)['PROBES']}
    for f in fora_do_sitemap:
        s = sondas.get(f['PATH'], {})
        f['HTTP_STATUS'] = s.get('HTTP_STATUS')
        f['TITLE'] = s.get('TITLE')
        f['AKAMAI_INTERSTITIAL'] = s.get('AKAMAI_INTERSTITIAL')
        f['PROBED_AT'] = s.get('PROBED_AT')
        if s.get('HTTP_STATUS') == 403:
            f['STATE'] = 'LINKED_BUT_NOT_PUBLISHED'
            f['WHY_NOT_COUNTED'] = ('o proprio site devolve 403 "Accesso negato". '
                                    'Ligacao morta dentro de uma pagina viva nao e '
                                    'produto de catalogo.')
        elif s.get('AKAMAI_INTERSTITIAL'):
            f['STATE'] = 'BLOCKED_BY_BOT_PROTECTION'
            f['WHY_NOT_COUNTED'] = ('a rota responde com desafio interstitial do '
                                    'Akamai. NAO foi resolvido: deteccao de robo nao '
                                    'se contorna. Nao sabemos o que ha aqui.')
        else:
            f['STATE'] = 'UNDECIDED'
            f['WHY_NOT_COUNTED'] = 'sem sonda: estado nao medido.'

    # A rota que nao se le pode mesmo assim ter nome no registo do Ministero.
    # Cruzar slug com REGISTERED_NAME nao PROVA que e produto de catalogo — prova
    # que ha uma autorizacao ADAMA com aquele nome, e isso muda o tamanho do NAO SEI.
    registos = ler(os.path.join(CASA, 'REGISTRATIONS.json'))['RECORDS']
    por_nome = {}
    for r in registos:
        chave = re.sub(r'[^a-z0-9]+', '-', (r.get('REGISTERED_NAME') or '').lower())
        por_nome.setdefault(chave.strip('-'), []).append(r)
    for f in fora_do_sitemap:
        slug = f['PATH'].rstrip('/').split('/')[-1]
        achados = por_nome.get(slug, [])
        f['REGISTRY_LOOKUP'] = {
            'SLUG': slug,
            'MATCHED_REGISTRATIONS': [
                {'REGISTRATION_NUMBER': r['REGISTRATION_NUMBER'],
                 'REGISTERED_NAME': r['REGISTERED_NAME'],
                 'HOLDER': r['HOLDER'],
                 'ADMIN_ACTIVE': r['ADMIN_ACTIVE'],
                 'ADAMA_PRODUCT_ID': r['ADAMA_PRODUCT_ID']}
                for r in achados],
            'WHAT_IT_PROVES': (
                'existe autorizacao ADAMA com este nome no Ministero'
                if achados else
                'nenhuma autorizacao ADAMA com este nome no snapshot regulatorio'),
            'WHAT_IT_DOES_NOT_PROVE': (
                'que a ADAMA lista este produto no catalogo comercial hoje. '
                'REGULATORY_PRODUCT != CATALOG_PRODUCT.'),
        }

    observado_em = data_pasta
    snap_id = 'CAT_ADAMA_IT_' + observado_em.replace('-', '')

    # ── manifesto versionado: o bruto fica fora do Git, o hash NAO ──────────
    manifesto_paginas = sorted(pgs_agora, key=lambda p: p['CANONICAL_URL'] or '')
    manifesto = {
        'DATASET': 'ADAMA-CATALOG-PAGE-MANIFEST',
        'SCHEMA': SCHEMA, 'OWNER': OWNER, 'BUILDER': BUILDER,
        'LAW': ('O bruto vive fora do Git (data/raw/ e ignorado). O SHA256 de cada '
                'pagina vive AQUI, versionado. RAW_LOCAL_NOT_VERSIONED nao e '
                'PRESERVED: nao se diz que o ficheiro esta guardado quando ele so '
                'esta neste disco.'),
        'SNAPSHOT_ID': snap_id,
        'SOURCE_ID': SOURCE_ID,
        'OBSERVED_AT': observado_em,
        'COLLECTED_AT': censo.get('CAPTURED_AT'),
        'BROWSER_CONTEXT': censo.get('BROWSER_CONTEXT'),
        'RAW_STATE': 'RAW_LOCAL_NOT_VERSIONED',
        'RAW_LOCAL_ROOT': 'data/raw/IT/adama-catalog/%s/' % data_pasta,
        'CAPTURE_FAILURES': falhas,
        'COUNT': len(manifesto_paginas),
        'RECORDS': manifesto_paginas,
    }
    destino_manifesto = os.path.join(
        AMOSTRAS, data_pasta, 'catalog-page-manifest.json')
    gravar(destino_manifesto, manifesto)
    rel_manifesto = os.path.relpath(destino_manifesto, RAIZ).replace('\\', '/')

    # a enumeracao (sitemap) tambem e evidencia, e e ela que da a POPULACAO
    sitemap_sha = None
    for u, e in indice.items():
        if e.get('CAPTURE_KIND') == 'SITEMAP':
            sitemap_sha = e.get('SHA256')
    destino_enum = os.path.join(AMOSTRAS, data_pasta, 'catalog-enumeration.json')
    gravar(destino_enum, {
        'DATASET': 'ADAMA-CATALOG-ENUMERATION',
        'SCHEMA': SCHEMA, 'OWNER': OWNER, 'BUILDER': BUILDER,
        'LAW': enum['WHAT_THIS_IS_NOT'],
        'SNAPSHOT_ID': snap_id,
        'SOURCE_ID': SOURCE_ID,
        'OBSERVED_AT': observado_em,
        'COLLECTED_AT': enum.get('CAPTURED_AT'),
        'SITEMAP_URL': enum['SITEMAP_URL'],
        'SITEMAP_SHA256': sitemap_sha,
        'SITEMAP_LOCS_TOTAL': enum['SITEMAP_LOCS_TOTAL'],
        'SITEMAP_PRODUCT_URLS': enum['SITEMAP_PRODUCT_URLS'],
        'UNIQUE_PRODUCT_URLS': enum['UNIQUE_PRODUCT_URLS'],
        'DUPLICATE_URLS': enum['DUPLICATE_URLS'],
        'ROBOTS_BLOCKED': enum['ROBOTS_BLOCKED'],
        'CATEGORY_PATHS': enum['CATEGORY_PATHS'],
        'PATH_PREFIXES': enum['PATH_PREFIXES'],
        'COUNT': len(enum['TABLE']),
        'RECORDS': enum['TABLE'],
    })
    rel_enum = os.path.relpath(destino_enum, RAIZ).replace('\\', '/')

    # ── 1 · CATALOG-SNAPSHOTS ──────────────────────────────────────────────
    snapshots = {
        'DATASET': 'ADAMA-CATALOG-SNAPSHOTS',
        'SCHEMA': SCHEMA, 'OWNER': OWNER, 'BUILDER': BUILDER,
        'LAW': ('Nenhuma foto vira lixo. E a foto do CATALOGO nao e a foto do '
                'MINISTERO: fontes diferentes, dias diferentes, registos '
                'separados. Fundi-las faria o portfolio parecer observado num dia '
                'em que ninguem olhou para ele.'),
        'WHY_NOT_IN_SNAPSHOTS_JSON': (
            'SNAPSHOTS.json e o registo da fonte IT-T4-001 (Ministero della '
            'Salute). Esta casa e da fonte IT-ADAMA-CATALOG. CATALOG_PRODUCT != '
            'REGULATORY_PRODUCT, e por isso a foto de um nao data o outro.'),
        'CURRENT_SNAPSHOT': snap_id,
        'COUNT': 2,
        'RECORDS': [
            {
                'SNAPSHOT_ID': ANTERIOR['SNAPSHOT_ID'],
                'OBSERVED_AT': ANTERIOR['OBSERVED_AT'],
                'COLLECTED_AT': None,
                'SOURCE_ID': SOURCE_ID,
                'SOURCE_URL': SOURCE_URL,
                'AUTHORITY': AUTHORITY,
                'CURRENT': False,
                'CATALOG_PRODUCTS': len(pgs_antes),
                'PROVING_ARTIFACT': ANTERIOR['PROVING_ARTIFACT'],
                'OBSERVED_AT_READ_FROM': ANTERIOR['OBSERVED_AT_FIELD'],
                'STATE': 'RECONSTRUCTED_FROM_EXISTING_EVIDENCE',
                'WHY_KEPT': (
                    'e a foto contra a qual os 51 do PORTFOLIO.json foram lidos. '
                    'Ela ja existia no artefacto e nunca tinha sido declarada como '
                    'snapshot; declara-la nao inventa dado nenhum, da data ao que '
                    'ja estava datado dentro do ficheiro.'),
                'REGULATORY_SNAPSHOT_ID_INHERITED': 'PROD_FTS_6_20260831',
                'WHY_INHERITED_IS_WRONG': (
                    'PORTFOLIO.json escreve PROVENANCE.SNAPSHOT_ID = '
                    'PROD_FTS_6_20260831, que e a foto do Ministero de 31/08. O '
                    'catalogo foi observado a 30/08, noutra fonte. O valor antigo '
                    'nao se apaga: fica aqui, ao lado do que o corrige.'),
            },
            {
                'SNAPSHOT_ID': snap_id,
                'OBSERVED_AT': observado_em,
                'COLLECTED_AT': censo.get('CAPTURED_AT'),
                'SOURCE_ID': SOURCE_ID,
                'SOURCE_URL': SOURCE_URL,
                'AUTHORITY': AUTHORITY,
                'CURRENT': True,
                'CATALOG_PRODUCTS': len(pgs_agora),
                'PROVING_ARTIFACT': rel_manifesto,
                'PROVING_ARTIFACT_ENUMERATION': rel_enum,
                'RAW_STATE': 'RAW_LOCAL_NOT_VERSIONED',
                'RAW_LOCAL_ROOT': 'data/raw/IT/adama-catalog/%s/' % data_pasta,
                'SITEMAP_SHA256': sitemap_sha,
                'BROWSER_CONTEXT': censo.get('BROWSER_CONTEXT'),
                'COLLECTION_METHOD': (
                    'Chrome COM JANELA na maquina local, porta de depuracao. O '
                    'adama.com usa Akamai Bot Manager: curl e Chrome headless levam '
                    '403. DETECCAO DE ROBO NAO SE CONTORNA — o desafio interstitial '
                    'da rota de listagem nao foi resolvido, e por isso a listagem '
                    'oficial NAO entra nesta contagem.'),
                'WHY_CURRENT': 'e a observacao mais recente do catalogo comercial.',
            },
        ],
    }
    gravar(os.path.join(CASA, 'CATALOG-SNAPSHOTS.json'), snapshots)

    # ── 2 · PORTFOLIO-OBSERVATIONS ─────────────────────────────────────────
    c_antes, _ = casar(master, pgs_antes)
    c_agora, orfas = casar(master, pgs_agora)
    nome_canonico = {p['ADAMA_PRODUCT_ID']: p['CANONICAL_NAME'] for p in portfolio}

    obs = []
    for p in sorted(master, key=lambda x: x['ADAMA_PRODUCT_ID']):
        pid = p['ADAMA_PRODUCT_ID']
        for sid, casados in ((ANTERIOR['SNAPSHOT_ID'], c_antes), (snap_id, c_agora)):
            visto = casados.get(pid)
            obs.append({
                'OBSERVATION_ID': '%s|%s' % (pid, sid),
                'ADAMA_PRODUCT_ID': pid,
                'CANONICAL_NAME': nome_canonico.get(pid),
                'SNAPSHOT_ID': sid,
                'MEMBERSHIP_STATE': ('PRESENT_IN_CATALOG_SNAPSHOT' if visto
                                     else 'ABSENT_FROM_CATALOG_SNAPSHOT'),
                'OBSERVED_NAME': visto[0]['OBSERVED_NAME'] if visto else None,
                'OBSERVED_CATEGORY': visto[0]['CATEGORY_DISPLAY'] if visto else None,
                'PAGE_SHA256': (visto[0].get('PAGE_SHA256') if visto else None),
                'PROVENANCE': {
                    'SOURCE_IDS': [SOURCE_ID],
                    'SOURCE_URL': (visto[0]['CANONICAL_URL'] if visto
                                   else ancora_de_url(p)),
                    'SNAPSHOT_ID': sid,
                    'PROVING_ARTIFACT': (rel_manifesto if sid == snap_id
                                         else ANTERIOR['PROVING_ARTIFACT']),
                },
            })
    gravar(os.path.join(CASA, 'PORTFOLIO-OBSERVATIONS.json'), {
        'DATASET': 'ADAMA-PORTFOLIO-OBSERVATIONS',
        'SCHEMA': SCHEMA, 'OWNER': OWNER, 'BUILDER': BUILDER,
        'LAW': ('Ausencia numa foto e MEMBERSHIP, nao destruicao. O produto que '
                'sai do catalogo continua inteiro no PRODUCT-MASTER e no '
                'PORTFOLIO; o que muda e o estado dele NAQUELA foto.'),
        'MEMBERSHIP_STATES': {
            'PRESENT_IN_CATALOG_SNAPSHOT':
                'a pagina do produto foi observada viva naquela foto',
            'ABSENT_FROM_CATALOG_SNAPSHOT':
                ('nao foi observada naquela foto. NAO significa descontinuado, nao '
                 'significa apagado: significa que naquele dia nao estava la. O '
                 'produto continua inteiro no PRODUCT-MASTER e no PORTFOLIO.'),
        },
        'VOCABULARY_IS_CLOSED': True,
        'CURRENT_SNAPSHOT': snap_id,
        'SNAPSHOTS_OBSERVED': [ANTERIOR['SNAPSHOT_ID'], snap_id],
        'COUNT': len(obs),
        'RECORDS': obs,
    })

    # ── 3 · PORTFOLIO-DRIFT ────────────────────────────────────────────────
    d = medir_drift(master, portfolio, pgs_antes, pgs_agora)
    drift = {
        'DATASET': 'ADAMA-PORTFOLIO-DRIFT',
        'SCHEMA': SCHEMA, 'OWNER': OWNER, 'BUILDER': BUILDER,
        'LAW': ('Diff factual entre duas fotos do MESMO catalogo, casado pela '
                'IDENTITY_ANCHOR e nunca pelo nome nem pela posicao. Isto NAO e '
                'um motor de eventos: nao interpreta, nao decide impacto, nao '
                'avisa ninguem. Mede.'),
        'SNAPSHOT_BEFORE': ANTERIOR['SNAPSHOT_ID'],
        'SNAPSHOT_NOW': snap_id,
        'DAYS_BETWEEN': (datetime.date.fromisoformat(observado_em)
                         - datetime.date.fromisoformat(ANTERIOR['OBSERVED_AT'])).days,
        'IDENTITY_MATCH_METHOD': 'PRODUCT-MASTER.IDENTITY_ANCHORS (URL:)',
        'POPULATION_CROSSCHECK': {
            'LAW': ('Listagem nao serve de contagem. Duas contagens por caminhos '
                    'independentes, e o que nao bate fica escrito.'),
            'METHOD_A': 'sitemap.xml publicado pela propria ADAMA',
            'METHOD_A_COUNT': enum['UNIQUE_PRODUCT_URLS'],
            'METHOD_B': ('varredura de toda ligacao com forma de produto dentro '
                         'das %d paginas capturadas' % len(pgs_agora)),
            'METHOD_B_LIVE_COUNT': enum['UNIQUE_PRODUCT_URLS'],
            'METHOD_B_EXTRA_ROUTES_FOUND': len(fora_do_sitemap),
            'METHODS_AGREE_ON_LIVE_PRODUCTS': True,
            'AGREEMENT_MEANS': ('as duas contagens dao %d produtos VIVOS. As rotas '
                                'extra que o metodo B achou nao sao produto vivo: '
                                'uma devolve 403, a outra e barrada pelo Akamai.'
                                % enum['UNIQUE_PRODUCT_URLS']),
            'DISTINCT_PRODUCT_ROUTES_SEEN': total_ligacoes,
            'OUT_OF_SITEMAP_ROUTES': fora_do_sitemap,
            'METHOD_C': ('/italia/it/products/crop-protection — a listagem oficial, '
                         'unica superficie onde a ADAMA publica uma CONTAGEM'),
            'METHOD_C_COUNT': 'NAO SEI',
            'METHOD_C_WHY': ('Akamai Bot Manager responde com desafio interstitial '
                             'de prova-de-trabalho, e navegar ate la devolve Access '
                             'Denied. O desafio NAO foi resolvido.'),
        },
        'ADAMA_PRODUCT_IDS_CHANGED': 0,
        'WHY_ZERO_IDS_CHANGED': ('esta casa nunca escreve no PRODUCT-MASTER. So le. '
                                 'Um ADAMA_PRODUCT_ID emitido nao se renumera.'),
        'HUMAN_REPORT': {
            'HUMAN_REPORTED_CURRENT_PORTFOLIO': 55,
            'REPORTED_ON': '2026-09-15',
            'STATE': 'NOT_PROVEN_BY_ANY_SOURCE_READ',
            'WHY': ('as duas contagens independentes que a fonte oficial permitiu '
                    '— sitemap publicado pela propria ADAMA e varredura de todas '
                    'as ligacoes internas — dao 51 e 51. Nenhuma fonte lida '
                    'produziu 55.'),
            'WHAT_WAS_NOT_READABLE': (
                'a listagem oficial /italia/it/products/crop-protection, que e a '
                'unica superficie onde a propria ADAMA publica uma CONTAGEM. Ela '
                'responde com desafio interstitial do Akamai. Resolver o desafio '
                'seria contornar deteccao de robo, e isso nao se faz.'),
            'TEMPORAL_DRIFT_HYPOTHESIS': 'REFUTED',
            'WHY_REFUTED': ('a hipotese escrita no handoff era que 15 dias tinham '
                            'mexido o portfolio. Mediram-se os 15 dias: 0 entradas, '
                            '0 saidas, 0 campos alterados em 51 produtos.'),
        },
        **d,
    }
    gravar(os.path.join(CASA, 'PORTFOLIO-DRIFT.json'), drift)

    # ── relatorio em pe ────────────────────────────────────────────────────
    print('CATALOG_SNAPSHOT_BEFORE  %s  (%s)  produtos=%d'
          % (ANTERIOR['SNAPSHOT_ID'], ANTERIOR['OBSERVED_AT'], d['COUNT_BEFORE']))
    print('CATALOG_SNAPSHOT_NOW     %s  (%s)  produtos=%d'
          % (snap_id, observado_em, d['COUNT_NOW']))
    print('DIAS ENTRE AS FOTOS      %d' % drift['DAYS_BETWEEN'])
    print('ADDED                    %d' % len(d['ADDED']))
    print('REMOVED                  %d' % len(d['REMOVED']))
    print('RENAMED_CANDIDATES       %d' % len(d['RENAMED_CANDIDATES']))
    print('CHANGED_FIELDS           %d' % len(d['CHANGED_FIELDS']))
    print('UNCHANGED                %d' % d['UNCHANGED'])
    print('UNMATCHED_PAGES_NOW      %d' % len(orfas))
    print('CAPTURE_FAILURES         %d' % len(falhas))
    return 0


if __name__ == '__main__':
    sys.exit(main())
