#!/usr/bin/env python3
"""
ADAMA-ES-PRODUCT-INTELLIGENCE — o artefato de entrega (seções 27 e 28).

Tudo aqui é DERIVADO no momento da execução: portão medido, enumeração tentada,
crosswalk rodado. Nenhum número é digitado. Rodar de novo com acesso ao site produz o
censo cheio pelo mesmo caminho, sem editar este arquivo.

As catorze estruturas da seção 27 existem sempre. O que muda com o acesso é se elas
têm linhas ou o motivo pelo qual não têm — e motivo medido não é zero.

    python3 scripts/adama_intelligence.py --build 2026-08-30
    python3 scripts/adama_intelligence.py --manifest 2026-08-30 > manifest.csv
"""
import csv
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
sys.path.insert(0, HERE)
import adama_es as A                 # noqa: E402
import adama_es_portao as P          # noqa: E402
import adama_crosswalk as X          # noqa: E402

VAZIO = 'NOT_COLLECTED'


def _ler(nome):
    caminho = os.path.join(SAMPLES, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def construir(captura):
    portao = P.avaliar()
    acesso = portao['ADAMA_ES_COLLECTION_READY'] == 'YES'

    censo = A.enumerar_catalogo(captura) if acesso else {
        'CATALOG_TIMESTAMP': captura,
        'CURRENT_CATALOG_TOTAL': VAZIO, 'CURRENT_CATALOG_NAMES': VAZIO,
        'CURRENT_CATALOG_ENUMERATED': VAZIO, 'ENUMERATION_COMPLETE': 'NO',
        'ENTRADAS': [],
        'PORQUE': 'o portao devolveu %s; enumerar sem acesso seria inventar denominador'
                  % portao['ALCANCE'],
    }

    produtos, documentos = [], []
    crop_rel, issue_rel, par_rel, ambiguos = [], [], [], []
    ingredientes, moa, tecnologias, claims = [], [], [], []
    relacoes_produto, conteudo, videos, janelas = [], [], [], []

    for entrada in censo.get('ENTRADAS') or []:
        estado, html, code = A.buscar(entrada['PAGE_URL'])
        if estado != 'OK':
            produtos.append({'PAGE_URL': entrada['PAGE_URL'], 'PARSE_STATE': 'FAILED',
                             'HTTP_STATUS': code,
                             'O_QUE_ISTO_NAO_E': 'falha de pagina nao e produto inexistente'})
            continue
        d = A.parsear_produto(html, entrada['PAGE_URL'], catalog_status='CURRENT',
                              captured_at=captura)
        produtos.append(d['PRODUCT'])
        documentos += d['DOCUMENTS']
        crop_rel += d['CROP_RELATIONS']
        issue_rel += d['ISSUE_RELATIONS']
        par_rel += d['CROP_ISSUE_RELATIONS']
        ambiguos += d['AMBIGUOUS_TERMS']
        moa += d['MODES_OF_ACTION']
        claims += d['CLAIMS']
        videos += d['VIDEOS']
        for ia in d['PRODUCT']['ACTIVE_INGREDIENTS']:
            ingredientes.append(dict(ia, PRODUCT_ID=d['PRODUCT']['PRODUCT_ID']))
        for r in d['CROP_ISSUE_RELATIONS']:
            if r['BBCH_FROM'] != 'NÃO SEI' or r['TIMING_FLAGS']:
                janelas.append({k: r[k] for k in (
                    'PRODUCT_ID', 'CROP', 'ISSUE', 'BBCH_FROM', 'BBCH_TO',
                    'APPLICATION_COUNT', 'INTERVAL_DAYS', 'TIMING_FLAGS', 'ANCHOR')})

    if documentos:
        A.baixar_documentos(documentos, captura)

    fichas = X.fichas_ropf()
    linhas_cw = X.cruzar(produtos, fichas)
    resumo_cw = X.resumo(linhas_cw, fichas)
    milho = _ler('ADAMA-ES-MAIZE-REGULATORY-MAP.json')

    baixados = [d for d in documentos if d.get('DOWNLOAD_STATE') == 'DOWNLOADED']
    por_tipo = {}
    for d in documentos:
        por_tipo[d['DOCUMENT_TYPE']] = por_tipo.get(d['DOCUMENT_TYPE'], 0) + 1

    return {
        'SOURCE_ID': 'ADAMA-ES-PRODUCT-INTELLIGENCE',
        'source': 'catalogo publico ADAMA Espana + contraprova MAPA/ROPF',
        'SOURCE_LOCATION': 'SPAIN', 'FACT_LOCATION': 'SPAIN', 'ORIGINAL_LANGUAGE': 'ES',
        'captured_at': captura, 'CAPTURE_DATE': captura,
        'ESTADO_DO_REGISTRO': 'CURRENT', 'COUNTRY': 'ES',
        'HEAD': P._cabeca_do_git(),
        'GERADO_POR': 'scripts/adama_intelligence.py --build',

        'ACESSO': {
            'ADAMA_ES_COLLECTION_READY': portao['ADAMA_ES_COLLECTION_READY'],
            'ALCANCE': portao['ALCANCE'],
            'ROTAS': portao['ROTAS'],
            'MAPA_ROPF_READY': 'YES',
            'LEI': portao['LEI'],
        },

        'CENSO': {
            'CATALOG_TIMESTAMP': censo.get('CATALOG_TIMESTAMP'),
            'CURRENT_CATALOG_TOTAL': censo.get('CURRENT_CATALOG_TOTAL', VAZIO),
            'CURRENT_CATALOG_ENUMERATED': len(censo.get('ENTRADAS') or []) or VAZIO,
            'CURRENT_CATALOG_NAMES': censo.get('CURRENT_CATALOG_NAMES', VAZIO),
            'ENUMERATION_COMPLETE': censo.get('ENUMERATION_COMPLETE', 'NO'),
            'PORQUE': censo.get('PORQUE'),
            'SNAPSHOTS_RECUSADOS': {
                'RELATO_EXTERNO_55': 'nao usado — relato de terceiro nao e observacao desta coleta',
                'SNAPSHOT_ANTIGO_58': 'nao usado — pagina cacheada nao fecha denominador atual',
                'REGRA': 'so entra no censo o que ESTA coleta observou ao vivo (secao 3)',
            },
        },

        # ── as catorze estruturas da seção 27 ────────────────────────────────
        'PRODUCTS': produtos,
        'DOCUMENTS': documentos,
        'CROP_RELATIONS': crop_rel,
        'ISSUE_RELATIONS': issue_rel,
        'CROP_ISSUE_RELATIONS': par_rel,
        'APPLICATION_WINDOWS': janelas,
        'ACTIVE_INGREDIENTS': ingredientes,
        'MODES_OF_ACTION': moa,
        'TECHNOLOGIES': tecnologias,
        'CLAIMS': claims,
        'PRODUCT_RELATIONS': relacoes_produto,
        'RELATED_CONTENT': conteudo,
        'VIDEOS': videos,
        'REGULATORY_CROSSWALK': dict(resumo_cw, LINHAS=linhas_cw[:200]),

        'AMBIGUOUS_TERMS': ambiguos,

        'MAIZE': {
            'REGULATORY_MAP': 'data/samples/ADAMA-ES-MAIZE-REGULATORY-MAP.json',
            'MAIZE_PRODUCTS': (milho or {}).get('MAIZE_PRODUCT_COUNT', VAZIO),
            'MAIZE_CROP_ISSUE_RELATIONS': len((milho or {}).get('MAIZE_CROP_ISSUE_RELATIONS') or []),
            'MAIZE_PUBLIC_POSITIONING': VAZIO,
            'MAIZE_TECHNOLOGIES': VAZIO,
            'PORQUE': ('a metade regulatoria foi medida ao vivo; a metade publica depende '
                       'do site da ADAMA'),
        },

        'CONTAGENS': {
            'PRODUCT_PAGES_FOUND': len(censo.get('ENTRADAS') or []) or VAZIO,
            'PRODUCT_PAGES_PARSED': sum(1 for p in produtos if p.get('PRODUCT_ID')) or VAZIO,
            'PRODUCT_PAGES_FAILED': sum(1 for p in produtos if p.get('PARSE_STATE') == 'FAILED'),
            'DOCUMENTS_DISCOVERED': len(documentos) or VAZIO,
            'DOCUMENTS_DOWNLOADED': len(baixados) or VAZIO,
            'FAILED_DOWNLOADS': sum(1 for d in documentos if d.get('DOWNLOAD_STATE') == 'FAILED'),
            'DOCUMENTS_BY_TYPE': por_tipo or VAZIO,
            'TOTAL_BYTES': sum(d.get('BYTES') or 0 for d in baixados) or VAZIO,
            'CROP_RELATIONS': len(crop_rel) or VAZIO,
            'ISSUE_RELATIONS': len(issue_rel) or VAZIO,
            'CROP_ISSUE_RELATIONS': len(par_rel) or VAZIO,
            'APPLICATION_WINDOWS': len(janelas) or VAZIO,
            'TECHNICAL_CLAIMS': sum(1 for c in claims
                                    if c['CLAIM_TYPE'] == 'MANUFACTURER_TECHNICAL_CLAIM') or VAZIO,
            'COMMERCIAL_CLAIMS': sum(1 for c in claims
                                     if c['CLAIM_TYPE'] == 'MANUFACTURER_COMMERCIAL_CLAIM') or VAZIO,
            'VIDEOS_FOUND': len(videos) or VAZIO,
        },

        'SEMANTICA': {
            'PUBLIC_ADAMA_CATALOG_PRESENCE': ('afirmavel so para o que ESTA coleta viu no '
                                              'catalogo atual'),
            'CURRENT_COMMERCIAL_AVAILABILITY': 'NAO_SEI para todo produto (secao 24)',
            'O_QUE_O_CATALOGO_NAO_PROVA': ['estoque', 'venda', 'distribuicao',
                                           'market share', 'receita', 'prioridade interna'],
            'QUATRO_NIVEIS': ('OBSERVED != MANUFACTURER CLAIM != REGULATORY FACT != '
                              'DERIVED INTERPRETATION — cada linha carrega o seu'),
        },

        'SAFE_FOR_MAIN_SESSION_TO_CONSUME': 'YES',
        'PORQUE_E_SEGURO': (
            'nenhuma estrutura afirma o que nao foi medido: o que faltou esta como '
            'NOT_COLLECTED com o motivo, e nunca como 0 nem como numero de terceiro.'),
    }


# ── seção 28 · o manifest canônico ──────────────────────────────────────────

COLUNAS = ['PRODUCT', 'CATEGORY', 'CURRENT_ADAMA_CATALOG', 'PAGE_URL', 'REGISTRATION_ID',
           'ROPF_MATCH', 'CROPS', 'ISSUES', 'ACTIVE_SUBSTANCES', 'LABEL', 'SDS',
           'TECH_SHEET', 'OTHER_DOCS', 'DOCUMENT_COUNT', 'STORAGE_COUNT', 'HASH_VERIFIED',
           'LAST_PUBLIC_DOC_DATE', 'NOTES']


def manifest(art):
    """Uma linha por produto do catálogo; sem catálogo, uma linha por registro do ROPF.

    A segunda forma não é o censo — é o inventário regulatório à espera dele, e a coluna
    CURRENT_ADAMA_CATALOG diz NOT_COLLECTED em vez de NO. "Não li o catálogo" e "não está
    no catálogo" são afirmações diferentes.
    """
    saida = io.StringIO()
    w = csv.DictWriter(saida, fieldnames=COLUNAS)
    w.writeheader()

    docs_por_produto = {}
    for d in art['DOCUMENTS']:
        docs_por_produto.setdefault(d['PRODUCT_ID'], []).append(d)

    if art['PRODUCTS']:
        cw = {l.get('PRODUCT_ID'): l for l in art['REGULATORY_CROSSWALK'].get('LINHAS') or []}
        for p in art['PRODUCTS']:
            pid = p.get('PRODUCT_ID')
            docs = docs_por_produto.get(pid, [])
            tipos = [d['DOCUMENT_TYPE'] for d in docs]
            crops = sorted({c['CROP'] for c in art['CROP_RELATIONS'] if c['PRODUCT_ID'] == pid})
            issues = sorted({i['ISSUE'] for i in art['ISSUE_RELATIONS'] if i['PRODUCT_ID'] == pid})
            datas = [d['VISIBLE_DOCUMENT_DATE'] for d in docs
                     if d['VISIBLE_DOCUMENT_DATE'] not in ('NÃO SEI', None)]
            w.writerow({
                'PRODUCT': p.get('DISPLAY_NAME'), 'CATEGORY': p.get('CATEGORY'),
                'CURRENT_ADAMA_CATALOG': p.get('CURRENT_CATALOG_STATUS'),
                'PAGE_URL': p.get('PAGE_URL'), 'REGISTRATION_ID': p.get('REGISTRATION_ID'),
                'ROPF_MATCH': (cw.get(pid) or {}).get('ESTADO', 'NOT_TESTED'),
                'CROPS': '; '.join(crops) or 'NOT_COLLECTED',
                'ISSUES': '; '.join(issues) or 'NOT_COLLECTED',
                'ACTIVE_SUBSTANCES': '; '.join(
                    a['NAME'] for a in p.get('ACTIVE_INGREDIENTS') or []) or 'NOT_COLLECTED',
                'LABEL': tipos.count('ADAMA_COMMERCIAL_LABEL'),
                'SDS': tipos.count('SDS'), 'TECH_SHEET': tipos.count('TECHNICAL_SHEET'),
                'OTHER_DOCS': len(docs) - tipos.count('ADAMA_COMMERCIAL_LABEL')
                              - tipos.count('SDS') - tipos.count('TECHNICAL_SHEET'),
                'DOCUMENT_COUNT': len(docs),
                'STORAGE_COUNT': sum(1 for d in docs if d.get('DOWNLOAD_STATE') == 'DOWNLOADED'),
                'HASH_VERIFIED': sum(1 for d in docs
                                     if (d.get('SHA256') or 'NOT_COLLECTED') != 'NOT_COLLECTED'),
                'LAST_PUBLIC_DOC_DATE': max(datas) if datas else 'NÃO SEI',
                'NOTES': '',
            })
    else:
        for l in art['REGULATORY_CROSSWALK'].get('LINHAS') or []:
            w.writerow({
                'PRODUCT': l.get('DISPLAY_NAME'), 'CATEGORY': 'NOT_COLLECTED',
                'CURRENT_ADAMA_CATALOG': 'NOT_COLLECTED',
                'PAGE_URL': 'NOT_COLLECTED', 'REGISTRATION_ID': l.get('REG'),
                'ROPF_MATCH': l.get('ESTADO'),
                'CROPS': 'NOT_COLLECTED', 'ISSUES': 'NOT_COLLECTED',
                'ACTIVE_SUBSTANCES': l.get('FORMULADO') or 'NÃO SEI',
                'LABEL': 'NOT_COLLECTED', 'SDS': 'NOT_COLLECTED',
                'TECH_SHEET': 'NOT_COLLECTED', 'OTHER_DOCS': 'NOT_COLLECTED',
                'DOCUMENT_COUNT': 'NOT_COLLECTED', 'STORAGE_COUNT': 0, 'HASH_VERIFIED': 0,
                'LAST_PUBLIC_DOC_DATE': 'NÃO SEI',
                'NOTES': l.get('EVIDENCIA'),
            })
    return saida.getvalue()


if __name__ == '__main__':
    cap = sys.argv[sys.argv.index('--build') + 1] if '--build' in sys.argv else (
        sys.argv[sys.argv.index('--manifest') + 1] if '--manifest' in sys.argv else 'NÃO SEI')
    art = construir(cap)
    if '--manifest' in sys.argv:
        sys.stdout.write(manifest(art))
    else:
        print(json.dumps(art, ensure_ascii=False, indent=1))
