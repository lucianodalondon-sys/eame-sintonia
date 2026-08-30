#!/usr/bin/env python3
"""
VISÕES DO PORTFÓLIO PÚBLICO ADAMA ESPAÑA — seções 17 a 20 da missão.

O que este arquivo é: cinco recortes do MESMO artefato já construído. Ele não coleta,
não busca e não infere — lê ADAMA-ES-PRODUCT-INTELLIGENCE.json e reorganiza.

O que este arquivo NÃO é: fonte. Se o artefato disser NOT_COLLECTED, a visão diz
NOT_COLLECTED. Nenhuma visão preenche buraco do artefato.

    python3 scripts/adama_es_visoes.py --build

A LEI QUE ATRAVESSA AS CINCO VISÕES

    Cultivo DECLARADO no bloco "Cultivos" da ficha  !=  cultivo CITADO no corpo do texto

A primeira é a ADAMA dizendo "este produto é para este cultivo". A segunda é a palavra
ter aparecido na página — pode ser comparação, contexto ou nota de rodapé. As visões
por cultura usam SÓ a primeira. A segunda fica listada à parte, nomeada, para quem
quiser olhar; nunca somada à primeira.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
ARTEFATO = os.path.join(SAMPLES, 'ADAMA-ES-PRODUCT-INTELLIGENCE.json')

DECLARADO = 'DECLARADO_NO_BLOCO_CULTIVOS'

# Os rótulos são os OFICIAIS DO MAPA, que é como a relação sai do parser: o bloco da
# ficha escreve "Maíz" e o vocabulário oficial escreve "MAÍZ". Usar a forma da ficha aqui
# devolvia 0 produto em toda família — o casamento é feito contra o rótulo do registro
# espanhol, não contra a grafia da página. Conferido na captura de 2026-08-30, que tem
# 132 rótulos oficiais distintos declarados nas 56 fichas.
FAMILIAS = {
    'MAIZE': {
        'ROTULOS': ['MAÍZ', 'MAÍZ DULCE'],
        'PORQUE': ('secao 17 — a ADAMA EAME lancou portfolio de milho; esta visao mede '
                   'o que o site espanhol JA publica para milho, nada alem'),
    },
    'OLIVE': {
        'ROTULOS': ['OLIVO'],
        'PORQUE': 'secao 18 — a aba principal esta montando hero case em olivar',
    },
    'WINTER_CEREALS': {
        'ROTULOS': ['TRIGO', 'CEBADA', 'TRITICALE', 'CENTENO'],
        'PORQUE': 'secao 18 — cereais de inverno, os quatro rotulos que a ADAMA escreve',
    },
}


def _ler():
    if not os.path.exists(ARTEFATO):
        raise SystemExit('artefato ausente: %s — rode adama_intelligence.py --build antes'
                         % ARTEFATO)
    with open(ARTEFATO, encoding='utf-8') as f:
        return json.load(f)


def _por_produto(art):
    return {p['PRODUCT_ID']: p for p in art['PRODUCTS'] if p.get('PRODUCT_ID')}


def _agrupar(lista, chave):
    fora = {}
    for x in lista:
        fora.setdefault(x.get(chave), []).append(x)
    return fora


def visao_familia(art, nome, cfg):
    """Um recorte por família de cultivo. Produto só entra se DECLARAR o cultivo."""
    prods = _por_produto(art)
    alvo = set(cfg['ROTULOS'])
    # A comparação é por rótulo exato da ADAMA. "Maíz" e "Maíz dulce" são DOIS rótulos;
    # colapsar o segundo no primeiro seria decidir por ela que milho doce é milho.
    pids, por_rotulo = set(), {}
    for r in art['CROP_RELATIONS']:
        if r.get('DECLARATION_SOURCE') != DECLARADO or r['CROP'] not in alvo:
            continue
        pids.add(r['PRODUCT_ID'])
        por_rotulo.setdefault(r['CROP'], set()).add(r['PRODUCT_ID'])

    citados = sorted({r['PRODUCT_ID'] for r in art['CROP_RELATIONS']
                      if r['CROP'] in alvo and r.get('DECLARATION_SOURCE') != DECLARADO}
                     - pids)

    docs = _agrupar(art['DOCUMENTS'], 'PRODUCT_ID')
    linhas = []
    for pid in sorted(pids):
        p = prods.get(pid) or {}
        meus_docs = docs.get(pid, [])
        linhas.append({
            'PRODUCT_ID': pid,
            'DISPLAY_NAME': p.get('DISPLAY_NAME', 'NÃO SEI'),
            'CATEGORY': p.get('CATEGORY', 'NÃO SEI'),
            'PAGE_URL': p.get('PAGE_URL'),
            'REGISTRATION_ID': p.get('REGISTRATION_ID', 'NÃO SEI'),
            'FORMULATION': p.get('FORMULATION', 'NÃO SEI'),
            'ACTIVE_INGREDIENTS': p.get('ACTIVE_INGREDIENTS') or [],
            'COMPOSITION_TEXT_PUBLICADO': p.get('COMPOSITION_TEXT_PUBLICADO', 'NÃO SEI'),
            'ROTULOS_DE_CULTIVO_DECLARADOS': sorted(
                r for r in alvo if pid in por_rotulo.get(r, set())),
            'MODES_OF_ACTION': [m for m in art['MODES_OF_ACTION'] if m['PRODUCT_ID'] == pid],
            'ISSUES_CITADOS_NA_FICHA': sorted(
                {i['ISSUE'] for i in art['ISSUE_RELATIONS'] if i['PRODUCT_ID'] == pid}),
            'CROP_ISSUE_PARES': [r for r in art['CROP_ISSUE_RELATIONS']
                                 if r['PRODUCT_ID'] == pid and r['CROP'] in alvo],
            'CROP_DOSE': [r for r in art.get('CROP_DOSE_RELATIONS') or []
                          if r['PRODUCT_ID'] == pid and r['CROP'] in alvo],
            'CLAIMS': [c for c in art['CLAIMS'] if c['PRODUCT_ID'] == pid],
            'DOCUMENTOS': [{'TYPE': d['DOCUMENT_TYPE'], 'FILENAME': d['FILENAME'],
                            'SHA256': d.get('SHA256', 'NOT_COLLECTED'),
                            'DOWNLOAD_STATE': d.get('DOWNLOAD_STATE')}
                           for d in meus_docs],
            'MAPA_CONFIRMATION': 'ADAMA_ONLY_NOT_TESTED',
        })

    return {
        'SOURCE_ID': 'ADAMA-ES-%s-PUBLIC-PORTFOLIO-MAP' % nome,
        'DERIVADO_DE': 'data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json',
        'captured_at': art.get('captured_at'), 'CAPTURE_DATE': art.get('captured_at'),
        'COUNTRY': 'ES', 'ORIGINAL_LANGUAGE': 'ES',
        'PORQUE_ESTA_VISAO_EXISTE': cfg['PORQUE'],
        'ROTULOS_PROCURADOS': cfg['ROTULOS'],
        'REGRA_DE_ENTRADA': ('produto entra so se a ficha DECLARA o cultivo no bloco '
                             '"Cultivos". Citacao no corpo do texto nao entra.'),
        'PRODUTOS': len(linhas),
        'PRODUTOS_POR_ROTULO': {r: len(por_rotulo.get(r, set())) for r in cfg['ROTULOS']},
        'PRODUTOS_QUE_SO_CITAM_SEM_DECLARAR': citados,
        'O_QUE_ISTO_NAO_PROVA': ['estoque', 'venda', 'distribuicao', 'market share',
                                 'prioridade interna da ADAMA'],
        'LINHAS': linhas,
    }


def visao_por_cultivo(art):
    """Seção 19 — CULTIVO -> produtos, problemas, substâncias, modos de ação."""
    prods = _por_produto(art)
    porc = {}
    for r in art['CROP_RELATIONS']:
        if r.get('DECLARATION_SOURCE') != DECLARADO:
            continue
        porc.setdefault(r['CROP'], set()).add(r['PRODUCT_ID'])

    linhas = []
    for crop in sorted(porc):
        pids = sorted(porc[crop])
        ias, moas, tec, cats = set(), set(), set(), {}
        for pid in pids:
            p = prods.get(pid) or {}
            cats[p.get('CATEGORY', 'NÃO SEI')] = cats.get(p.get('CATEGORY', 'NÃO SEI'), 0) + 1
            for a in p.get('ACTIVE_INGREDIENTS') or []:
                ias.add(a['NAME'])
            tec.add(p.get('FORMULATION', 'NÃO SEI'))
        for m in art['MODES_OF_ACTION']:
            if m['PRODUCT_ID'] in pids:
                moas.add('%s %s' % (m['SCHEME'], m['CODE']))
        janelas = [j for j in art['APPLICATION_WINDOWS'] if j.get('CROP') == crop]
        doses = [d for d in art.get('CROP_DOSE_RELATIONS') or [] if d['CROP'] == crop]
        linhas.append({
            'CROP': crop,
            'PRODUTOS': len(pids),
            'PRODUCT_IDS': pids,
            'PRODUTOS_NOMES': [(prods.get(p) or {}).get('DISPLAY_NAME', 'NÃO SEI')
                               for p in pids],
            'CATEGORIAS': cats,
            'ACTIVE_INGREDIENTS': sorted(ias),
            'MODES_OF_ACTION': sorted(moas),
            'FORMULACOES': sorted(t for t in tec if t != 'NÃO SEI'),
            'APPLICATION_WINDOWS': janelas,
            'CROP_DOSE': doses,
            'ISSUES_PAREADOS': sorted({r['ISSUE'] for r in art['CROP_ISSUE_RELATIONS']
                                       if r['CROP'] == crop}),
        })
    return {
        'SOURCE_ID': 'ADAMA-ES-PORTFOLIO-POR-CULTIVO',
        'DERIVADO_DE': 'data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json',
        'captured_at': art.get('captured_at'),
        'CAPTURE_DATE': art.get('captured_at'), 'COUNTRY': 'ES',
        'REGRA_DE_ENTRADA': 'so cultivo DECLARADO no bloco "Cultivos" da ficha',
        'CULTIVOS': len(linhas),
        'LINHAS': linhas,
    }


def visao_por_issue(art):
    """Seção 20 — PROBLEMA -> cultivos, produtos, substâncias, confirmação MAPA."""
    prods = _por_produto(art)
    pori = {}
    for r in art['ISSUE_RELATIONS']:
        pori.setdefault(r['ISSUE'], set()).add(r['PRODUCT_ID'])

    linhas = []
    for issue in sorted(pori):
        pids = sorted(pori[issue])
        ias, moas = set(), set()
        for pid in pids:
            for a in (prods.get(pid) or {}).get('ACTIVE_INGREDIENTS') or []:
                ias.add(a['NAME'])
        for m in art['MODES_OF_ACTION']:
            if m['PRODUCT_ID'] in pids:
                moas.add('%s %s' % (m['SCHEME'], m['CODE']))
        pares = [r for r in art['CROP_ISSUE_RELATIONS'] if r['ISSUE'] == issue]
        linhas.append({
            'ISSUE': issue,
            'PRODUTOS': len(pids),
            'PRODUTOS_NOMES': [(prods.get(p) or {}).get('DISPLAY_NAME', 'NÃO SEI')
                               for p in pids],
            'CULTIVOS_PAREADOS': sorted({r['CROP'] for r in pares}),
            'PORQUE_PODE_NAO_HAVER_CULTIVO': (
                'a ficha cita o agente no corpo do texto sem tabela cultivo x agente; '
                'derivar o cultivo dai seria cartesiano (secao 8)'),
            'ACTIVE_INGREDIENTS': sorted(ias),
            'MODES_OF_ACTION': sorted(moas),
            'APPLICATION_WINDOWS': [j for j in art['APPLICATION_WINDOWS']
                                    if j.get('ISSUE') == issue],
            'MAPA_CONFIRMATION': sorted({r.get('MAPA_CONFIRMATION',
                                                'ADAMA_ONLY_NOT_TESTED') for r in pares})
            or ['ADAMA_ONLY_NOT_TESTED'],
        })
    return {
        'SOURCE_ID': 'ADAMA-ES-PORTFOLIO-POR-ISSUE',
        'DERIVADO_DE': 'data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json',
        'captured_at': art.get('captured_at'),
        'CAPTURE_DATE': art.get('captured_at'), 'COUNTRY': 'ES',
        'ISSUES': len(linhas),
        'LINHAS': linhas,
    }


def construir():
    art = _ler()
    saidas = {}
    for nome, cfg in FAMILIAS.items():
        saidas['ADAMA-ES-%s-PUBLIC-PORTFOLIO-MAP.json' % nome] = visao_familia(art, nome, cfg)
    saidas['ADAMA-ES-PORTFOLIO-POR-CULTIVO.json'] = visao_por_cultivo(art)
    saidas['ADAMA-ES-PORTFOLIO-POR-ISSUE.json'] = visao_por_issue(art)
    return saidas


if __name__ == '__main__':
    saidas = construir()
    if '--build' in sys.argv:
        for nome, dados in saidas.items():
            with open(os.path.join(SAMPLES, nome), 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=1)
            n = dados.get('PRODUTOS', dados.get('CULTIVOS', dados.get('ISSUES')))
            print('%-52s %s linhas' % (nome, n))
    else:
        print(__doc__)
