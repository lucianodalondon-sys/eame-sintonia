#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGRI-FOOD DATA PORTAL DA COMISSÃO EUROPEIA — série de preço e produção, rota pública.

    python3 scripts/agrifood_ue.py cereal/prices IT 2024 2025 2026
    python3 scripts/agrifood_ue.py oliveOil/prices IT 2025 2026
    python3 scripts/agrifood_ue.py --lista

Sem chave, sem custo. É a mesma rota que o `EU-T10-001` do acervo já tinha provado —
974 registros italianos de cereal, em 16 praças.

DUAS ARMADILHAS, as duas medidas
---------------------------------
1. `www.ec.europa.eu/agrifood/api/...` responde **HTTP 302** para
   `api.tech.ec.europa.eu`. Sem seguir o redirecionamento, a resposta é uma página de
   redirect de 762 bytes — que não é erro e não é vazio. Parece coleta que não achou nada.

2. O preço vem como **texto com vírgula decimal e símbolo**: `"€237,00"`, não `237.0`.
   Somar isso como número dá zero em silêncio. A conversão é explícita aqui, e o valor
   original fica preservado em `PRICE_RAW` — quem quiser conferir, confere.

    PREÇO É TEXTO NA FONTE. TRATAR COMO NÚMERO SEM CONVERTER É INVENTAR ZERO.
"""
import json
import os
import re
import sys
import urllib.request
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://www.ec.europa.eu/agrifood/api/%s'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

ENDPOINTS = [
    'cereal/prices', 'cereal/production',
    'oliveOil/prices', 'oliveOil/productionAndStock',
    'wine/prices', 'wine/production',
    'fruitAndVegetable/prices',
    'sugar/prices', 'dairy/prices', 'beef/prices', 'pigmeat/prices',
]


def buscar(endpoint, pais, anos):
    url = BASE % endpoint + '?memberStateCodes=%s' % pais
    if anos:
        url += '&years=' + ','.join(anos)
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    # urllib segue 302 por padrão — mas deixo explícito no artefato que ele existe,
    # porque quem repetir com `curl` sem -L vai receber a página de redirect.
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r), r.geturl()


def num(txt):
    """'€237,00' -> 237.0. Formato que não reconheço vira None, nunca 0."""
    if txt is None:
        return None
    s = re.sub(r'[^\d,.\-]', '', str(txt))
    if not s:
        return None
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return None


def main():
    if '--lista' in sys.argv:
        print('\n'.join(ENDPOINTS)); return 0
    if len(sys.argv) < 3:
        print(__doc__); return 2
    endpoint, pais = sys.argv[1], sys.argv[2]
    anos = sys.argv[3:]
    try:
        dados, final = buscar(endpoint, pais, anos)
    except Exception as e:                                       # noqa: BLE001
        print('FALHA %s: %s' % (type(e).__name__, str(e)[:200])); return 1
    if not isinstance(dados, list):
        print('RESPOSTA_NAO_E_LISTA: %s' % str(dados)[:200]); return 1

    por_prod = defaultdict(list)
    for r in dados:
        r['PRICE_RAW'] = r.get('price')
        r['PRICE_NUM'] = num(r.get('price'))
        # ⚠️ O NOME DO CAMPO MUDA POR ENDPOINT. `cereal` usa productName/marketName;
        # `oliveOil` e `wine` usam product/market. Ler so o primeiro par devolve None em
        # tudo — e None nao parece erro, parece serie sem produto.
        chave = (r.get('productName') or r.get('product') or r.get('productCode'),
                 r.get('marketName') or r.get('market') or r.get('memberStateName'))
        por_prod[chave].append(r)

    # o mais recente de cada par produto × praça
    def chave_data(r):
        d = (r.get('endDate') or r.get('beginDate') or '')
        p = d.split('/')
        return (p[2], p[1], p[0]) if len(p) == 3 else ('', '', '')

    ultimos = []
    for (prod, praca), rs in por_prod.items():
        rs.sort(key=chave_data)
        u = rs[-1]
        ant = rs[-2] if len(rs) > 1 else None
        ano_atras = None
        if u.get('PRICE_NUM') is not None:
            alvo = chave_data(u)
            for r in rs:
                k = chave_data(r)
                if k[0] and alvo[0] and int(k[0]) == int(alvo[0]) - 1 and k[1] == alvo[1]:
                    ano_atras = r
                    break
        ultimos.append({
            'PRODUCT': prod, 'MARKET': praca,
            'MARKETING_YEAR': u.get('marketingYear'),
            'PRICE_RAW': u.get('PRICE_RAW'), 'PRICE_NUM': u.get('PRICE_NUM'),
            'UNIT': u.get('unit'), 'STAGE': u.get('stageName'),
            'BEGIN': u.get('beginDate'), 'END': u.get('endDate'),
            'REFERENCE_PERIOD': u.get('referencePeriod'),
            'PREV_PRICE_NUM': (ant or {}).get('PRICE_NUM'),
            'YEAR_AGO_PRICE_NUM': (ano_atras or {}).get('PRICE_NUM'),
            'YEAR_AGO_END': (ano_atras or {}).get('endDate'),
            'OBSERVATIONS_IN_SERIES': len(rs),
        })
    ultimos.sort(key=lambda x: (str(x['PRODUCT']), str(x['MARKET'])))

    saida = {
        'DATASET': 'EU-AGRIFOOD-%s-%s' % (endpoint.replace('/', '-').upper(), pais),
        'SOURCE_NAME': 'European Commission — Agri-food Data Portal',
        'SOURCE_ID': 'EU-T10-002',
        'source': BASE % endpoint,
        'RESOLVED_URL': final,
        'REDIRECT_NOTE': 'www.ec.europa.eu responde 302 para api.tech.ec.europa.eu. '
                         'Sem seguir o redirecionamento a resposta e uma pagina de 762 '
                         'bytes — que NAO e erro e NAO e vazio.',
        'SOURCE_LOCATION': 'EUROPEAN UNION',
        'FACT_LOCATION': 'mercado nomeado dentro do pais',
        'ORIGINAL_LANGUAGE': 'EN',
        'EVIDENCE_CLASS': 'OFFICIAL_MARKET_OBSERVATION',
        'CAPTURED_AT': '2026-09-02',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'MEMBER_STATE': pais, 'YEARS_REQUESTED': anos,
        'RECORDS': len(dados),
        'PRODUCT_MARKET_PAIRS': len(ultimos),
        'PRICE_IS_TEXT_IN_SOURCE': 'sim — "€237,00". PRICE_RAW preserva o original; '
                                   'PRICE_NUM e a conversao, e vem None quando o formato '
                                   'nao foi reconhecido. Nunca 0.',
        'O_QUE_ISTO_NAO_E': [
            'nao e preco pago pela ADAMA nem por ninguem em particular',
            'nao e o mesmo estagio comercial entre pracas — ver STAGE',
            'nao e serie continua: praca que nao cotou na semana nao aparece',
            'comparar pracas diferentes exige conferir STAGE e UNIT antes',
        ],
        'LATEST_BY_PRODUCT_MARKET': ultimos,
    }
    dest = os.path.join(ROOT, 'data', 'samples', 'IT-MERCADO')
    os.makedirs(dest, exist_ok=True)
    nome = 'EU-AGRIFOOD-%s-%s.json' % (endpoint.replace('/', '-'), pais)
    with open(os.path.join(dest, nome), 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print('%s · %d registros · %d pares produto x praca' % (nome, len(dados), len(ultimos)))
    for u in ultimos[:14]:
        print('   %-26s %-18s %10s  %s..%s' % (str(u['PRODUCT'])[:26], str(u['MARKET'])[:18],
                                               u['PRICE_RAW'], u['BEGIN'], u['END']))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:                                            # noqa: BLE001
        pass
    sys.exit(main())
