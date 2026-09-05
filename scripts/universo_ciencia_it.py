#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIVERSO CIENTÍFICO ITALIANO POR RECORTE — os 4 cortes que ficaram NOT_COLLECTED, e um novo.

    python3 scripts/universo_ciencia_it.py

POR QUE ISTO EXISTE
--------------------
`ITALY-RESEARCHER-UNIVERSE.json` construiu UM corte (MAIZE_MYCOTOXIN) e declarou quatro
como `NOT_COLLECTED` — não «sem pesquisadores»:

    VINE_FLAVESCENCE (135 obras) · DURUM_FUSARIUM (78) ·
    OLIVE_BACTROCERA (70) · MAIZE_BORER_DIABROTICA (30)

O motivo registrado foi HTTP 429, e o diagnóstico de então dizia: «IP compartilhado de
datacenter tem orçamento de rajada muito menor que o documentado», e «oito horas depois
da rajada original o IP deste ambiente continua recusado».

    MEDIDO AGORA, 02/09/2026, DESTE AMBIENTE: HTTP 200 na primeira tentativa,
    e a contagem devolvida bate exatamente com a declarada (135).

⚠️ Isto **reclassifica** o achado anterior, e o reclassifica para melhor: o bloqueio era
do **IP de saída daquele ambiente**, não da fonte e não da consulta. A régua que a casa já
tinha escrito estava certa desde o começo — `SOURCE FAILURE != ZERO`, e aquilo nem era
falha de fonte. Só faltava sair por outra porta.

O QUINTO CORTE, QUE É NOVO
---------------------------
`WEED_HERBICIDE_RESISTANCE`. A ciência italiana do acervo era toda de DOENÇA; 55% do
portfólio ADAMA na Itália é HERBICIDA. O corte existe para fechar essa assimetria — e
porque o corpus de vídeo já mostrou que o GIRE (CNR-IPSP) fala publicamente do assunto.

AS LEIS, HERDADAS E NÃO AFROUXADAS
-----------------------------------
    FACT_LOCATION = NÃO SEI    a afiliação é do AUTOR, não do ESTUDO
    SEM COTA, SEM SEGUIDOR     a ordem é RECORRÊNCIA no recorte, e só
    CONTAGEM != IMPORTÂNCIA    quem publica mais não é «o maior especialista»
    NOT_COLLECTED != ZERO      corte que não fechou fica com o nome, não vira ausência
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-CIENCIA')
OPENALEX = 'https://api.openalex.org/works'

# ⚠️ PAUSA GENEROSA DE PROPÓSITO. A lição de 30/08 custou quatro recortes: paginar de
# 100 em 100 a cada 1,6 s derrubou um IP inteiro. Aqui é 200 por página e 3 s entre
# chamadas — mais lento que o necessário, porque o custo de ser lento é tempo e o de ser
# rápido foi perder a missão.
POR_PAGINA = 200
PAUSA = 3.0
TETO_PAGINAS = 12          # 2.400 obras por recorte. Nenhum recorte daqui chega perto.
DESDE = '2019-01-01'

# ⚠️ mailto do «polite pool» do OpenAlex. É um endereço de projeto, NÃO o e-mail do dono
# — mandar e-mail pessoal para serviço de terceiro sem ele pedir seria decisão minha
# sobre dado dele.
MAILTO = 'sintonia-eame@example.invalid'

RECORTES = {
    'VINE_FLAVESCENCE': 'flavescence OR flavescenza OR Scaphoideus',
    'DURUM_FUSARIUM': '(durum OR "Triticum durum") AND (Fusarium OR deoxynivalenol)',
    'OLIVE_BACTROCERA': '(olive OR Olea) AND (Bactrocera OR "olive fly")',
    'MAIZE_BORER_DIABROTICA': '(maize OR corn) AND (Ostrinia OR Diabrotica)',
    # ⭐ novo — ver docstring
    'WEED_HERBICIDE_RESISTANCE': ('"herbicide resistance" AND (Lolium OR Amaranthus OR '
                                  'Avena OR Papaver OR Echinochloa OR Sorghum)'),
}


def _get(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'sintonia-eame/1.0 (mailto:%s)' % MAILTO,
        'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def _pagina(busca, cursor):
    q = urllib.parse.urlencode({
        'filter': 'institutions.country_code:it,from_publication_date:%s,'
                  'title_and_abstract.search:%s' % (DESDE, busca),
        'per-page': POR_PAGINA,
        'cursor': cursor,
        'mailto': MAILTO,
    })
    return _get(OPENALEX + '?' + q)


def construir(nome, busca):
    """→ (registro do recorte, erro). Erro NÃO vira zero: vira estado com nome."""
    autores = defaultdict(lambda: {
        'OPENALEX_ID': None, 'NAME': None, 'ORCID': None,
        'INSTITUTIONS': Counter(), 'WORKS_IN_SCOPE': 0, 'LAST_ACTIVITY': None,
        'ANY_IT_AFFILIATION': False})
    obras = 0
    cursor = '*'
    paginas = 0
    total_declarado = None
    try:
        while cursor and paginas < TETO_PAGINAS:
            d = _pagina(busca, cursor)
            if total_declarado is None:
                total_declarado = d.get('meta', {}).get('count')
            itens = d.get('results') or []
            for w in itens:
                obras += 1
                data = w.get('publication_date')
                for a in (w.get('authorships') or []):
                    au = a.get('author') or {}
                    aid = au.get('id')
                    if not aid:
                        continue
                    paises = a.get('countries') or []
                    insts = [i.get('display_name') for i in (a.get('institutions') or [])
                             if i.get('display_name')]
                    it_aqui = ('IT' in paises) or any(
                        (i.get('country_code') == 'IT') for i in (a.get('institutions') or []))
                    r = autores[aid]
                    r['OPENALEX_ID'] = aid
                    r['NAME'] = au.get('display_name')
                    r['ORCID'] = r['ORCID'] or au.get('orcid')
                    for i in insts:
                        r['INSTITUTIONS'][i] += 1
                    r['WORKS_IN_SCOPE'] += 1
                    if it_aqui:
                        r['ANY_IT_AFFILIATION'] = True
                    if data and (not r['LAST_ACTIVITY'] or data > r['LAST_ACTIVITY']):
                        r['LAST_ACTIVITY'] = data
            cursor = (d.get('meta') or {}).get('next_cursor')
            paginas += 1
            print('    pagina %d · %d obras acumuladas' % (paginas, obras))
            if not itens:
                break
            time.sleep(PAUSA)
    except Exception as e:                                   # noqa: BLE001
        return None, '%s: %s' % (type(e).__name__, str(e)[:160])

    # ⚠️ SÓ autor com afiliação italiana EM ALGUMA obra do recorte. Coautor estrangeiro
    # de artigo italiano não vira «pesquisador italiano».
    it = [r for r in autores.values() if r['ANY_IT_AFFILIATION']]
    it.sort(key=lambda r: (-r['WORKS_IN_SCOPE'], r['NAME'] or ''))
    com_orcid = [r for r in it if r['ORCID']]
    ativos = [r for r in it if (r['LAST_ACTIVITY'] or '') >= '2024-01-01']

    top = []
    for r in it[:30]:
        insts = [i for i, _ in r['INSTITUTIONS'].most_common(3)]
        top.append({
            'PERSON': r['NAME'],
            'OPENALEX_ID': r['OPENALEX_ID'],
            'ORCID': r['ORCID'] or 'NÃO SEI',
            'INSTITUTIONS': insts or ['NÃO SEI'],
            'WORKS_IN_SCOPE': r['WORKS_IN_SCOPE'],
            'LAST_ACTIVITY': r['LAST_ACTIVITY'] or 'NÃO SEI',
            'IDENTITY_STATUS': ('ORCID_PRESENT_NOT_RESOLVED_HERE' if r['ORCID']
                                else 'NO_ORCID_IN_SOURCE'),
            'ROLE': 'NÃO SEI — o índice não declara papel',
            'FACT_REGION': 'NÃO SEI — a afiliação é do AUTOR, não do estudo',
        })

    inst = Counter()
    for r in it:
        for i, n in r['INSTITUTIONS'].items():
            inst[i] += n

    return {
        'NAME': nome,
        'QUERY': busca,
        'WORKS_DECLARED_BY_SOURCE': total_declarado,
        'WORKS_TRAVERSED': obras,
        'TRAVERSAL_COMPLETE': (total_declarado is not None and obras >= total_declarado),
        'AUTHORS_WITH_IT_AFFILIATION': len(it),
        'AUTHORS_WITH_ORCID': len(com_orcid),
        'AUTHORS_ACTIVE_SINCE_2024': len(ativos),
        'INSTITUTIONS_TOP': dict(inst.most_common(12)),
        'DETAILED_HERE': len(top),
        'UNIVERSE': top,
    }, None


def main():
    os.makedirs(SAIDA, exist_ok=True)
    recortes, falhas = {}, []
    for nome, busca in RECORTES.items():
        print('%s' % nome)
        r, err = construir(nome, busca)
        if err:
            print('    FALHOU: %s' % err)
            falhas.append({'RECORTE': nome, 'ESTADO': 'NOT_COLLECTED', 'ERRO': err})
            continue
        recortes[nome] = r
        print('    obras %s/%s · autores IT %d · com ORCID %d · ativos desde 2024 %d'
              % (r['WORKS_TRAVERSED'], r['WORKS_DECLARED_BY_SOURCE'],
                 r['AUTHORS_WITH_IT_AFFILIATION'], r['AUTHORS_WITH_ORCID'],
                 r['AUTHORS_ACTIVE_SINCE_2024']))
        time.sleep(PAUSA)

    corpo = {
        'DATASET': 'IT-CIENCIA-UNIVERSO-POR-RECORTE-V1',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-T5-001-B',
        'SOURCE_NAME': 'OpenAlex — rota REST aberta, sem chave, sem custo',
        'SOURCE_LOCATION': 'GLOBAL (índice)',
        'FACT_LOCATION': 'NÃO SEI — a afiliação é do AUTOR, não do estudo',
        'ORIGINAL_LANGUAGE': 'en',
        'EVIDENCE_CLASS': 'SCIENTIFIC_LITERATURE',
        'CAPTURED_AT': '2026-09-02',
        'FILTER_BASE': 'institutions.country_code:it, from_publication_date:%s' % DESDE,
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'FECHA_A_LACUNA_DE': 'IT-T5-001 / ITALY-RESEARCHER-UNIVERSE.json · SCOPES_NOT_BUILT',
        'RECLASSIFICACAO_DO_ACHADO_ANTERIOR': {
            'ANTES': ('HTTP 429 mesmo 8h depois da rajada; anotado como bloqueio de IP de '
                      'duração maior. Os 4 recortes ficaram NOT_COLLECTED.'),
            'AGORA': ('HTTP 200 na primeira tentativa deste ambiente, e a contagem '
                      'devolvida bate com a declarada.'),
            'LEITURA': ('o limite era do IP DE SAÍDA daquele ambiente — não da fonte, não '
                        'da consulta e não do volume. NOT_COLLECTED estava certo como '
                        'estado; o diagnóstico da CAUSA é que muda.'),
            'O_QUE_NAO_MUDA': ('a lição de rajada continua valendo e é obedecida aqui: '
                               '200 por página, 3 s entre chamadas.'),
        },
        'METHOD': ('percorre as obras do recorte, coleta autoria, mantém só quem tem '
                   'afiliação italiana EM ALGUMA obra do recorte, e ordena por '
                   'RECORRÊNCIA. Sem cota, sem seguidores.'),
        'WHAT_THIS_DOES_NOT_PROVE': [
            'não prova onde o estudo foi feito — a afiliação é do autor',
            'não prova papel: o índice não declara cargo',
            'não prova importância: publicar mais não é ser o maior especialista',
            'não resolve identidade: ORCID aqui é o que o índice mostra, não o conferido '
            'em pub.orcid.org',
            'não prova pressão de campo nem ocorrência',
        ],
        'CONFOUNDER_DECLARED': ('instituição líder e região líder de área tendem a '
                                'coincidir. Concordância pode ser sinal ou pode ser o '
                                'mesmo viés medido duas vezes.'),
        'RECORTES_CONSTRUIDOS': len(recortes),
        'RECORTES_FALHOS': falhas,
        'RECORTES': recortes,
    }
    cam = os.path.join(SAIDA, 'IT-CIENCIA-UNIVERSO-V1.json')
    with open(cam, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('\ngravado: data/samples/IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
