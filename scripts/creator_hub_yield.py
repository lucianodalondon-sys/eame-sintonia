#!/usr/bin/env python3
"""
HUB_YIELD (§3) — quantas PESSOAS ÚTEIS cada porta revelou.

    python3 scripts/creator_hub_yield.py

POR QUE ESTA MÉTRICA E NÃO OUTRA
----------------------------------
"Hub bom" não é o que tem mais páginas, mais posts ou mais prestígio. É o que
entrega gente que o Marketing consegue avaliar. Uma universidade com cem
professores pode render zero creators; uma conta de prêmio com doze publicações
rendeu vinte e três nomes.

Medir por rendimento é o que permite dizer, na próxima rodada, **quais das 43
portas valem o custo** — em vez de varrer todas igualmente.

O QUE `INVALID` SIGNIFICA AQUI
--------------------------------
Não é "pessoa ruim". É **fora do universo desta pergunta**: patrocinador
financeiro, país diferente do hub, ou creator de pecuária num mapa de proteção
vegetal. Todos continuam registrados — `INVALID` é sobre o recorte, não sobre a
pessoa.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'


def montar():
    extraidos = cr.carregar('HUB-EXTRACTION.json')
    classificados = cr.carregar('HUB-DISCOVERED-CLASSIFIED.json')
    resolvidos = {p['HANDLE'].lower(): p
                  for p in cr.carregar('HUB-DISCOVERED-RESOLVED.json')}
    ident = cr.carregar('PRIMARY-IDENTITY-RESOLVED.json')
    es_fontes = cr.carregar('ES-MASTER-SOURCES.json')
    hubs_reg = cr.carregar('DISCOVERY-HUBS.json')

    porhub = {}

    # ── porta 1: a conta do prêmio, medida ponta a ponta
    for h in extraidos:
        nome = h['HUB']
        do_hub = [c for c in classificados
                  if nome in (c.get('DISCOVERY_ROUTES') or [])
                  or 'Premios AgroInfluye' in (c.get('DISCOVERY_ROUTES') or [])]
        com_perfil = [c for c in do_hub if c.get('HANDLE_EXISTS') == 'YES']
        ident_ok = [c for c in do_hub if c.get('IDENTITY_STATE') == 'PROVED']
        produtores = [c for c in do_hub if c.get('ACTUAL_FARMER') == 'PROVED']
        com_cultura = [c for c in do_hub if c.get('CROP_STATE') in ('PROVED', 'PARTIAL')]
        ativos = [c for c in do_hub if c.get('ACTIVITY_STATE') == 'ACTIVE_RECENT']
        prontos = [c for c in do_hub if c.get('RELEVANCE_STATE') == 'ACTIVATION_READY']
        promissores = [c for c in do_hub if c.get('RELEVANCE_STATE') == 'PROMISING']
        # fora do recorte: outro país, pecuária, ou não-creator já excluído
        fora_pais = [c for c in do_hub if c.get('COUNTRY') != h.get('COUNTRY')]
        pecu = [c for c in do_hub if c.get('LIVESTOCK_CREATOR') == 'YES']
        invalidos = {c['ORIGIN_ID'] for c in fora_pais} | {c['ORIGIN_ID'] for c in pecu}
        # duplicatas: já estavam na base por outra rota
        dup = [c for c in do_hub
               if any('JA_NA_BASE' in str(p) for p in (c.get('WHY_RELEVANT') or []))]

        validos = [c for c in do_hub
                   if c['ORIGIN_ID'] not in invalidos
                   and c.get('RELEVANCE_STATE') in ('ACTIVATION_READY', 'PROMISING')]

        porhub[nome] = {
            'HUB': nome, 'HUB_HANDLE': h.get('HUB_HANDLE'), 'COUNTRY': h.get('COUNTRY'),
            'ROUTE': 'apify: menções nas legendas da conta oficial',
            'POSTS_READ': h.get('POSTS_READ'),
            'PEOPLE_DISCOVERED': h.get('PEOPLE_DISCOVERED'),
            'PEOPLE_WITH_PUBLIC_PROFILE': len(com_perfil),
            'IDENTITIES_PROVED': len(ident_ok),
            'ACTUAL_FARMERS_PROVED': len(produtores),
            'CREATORS_PROVED': len(do_hub),
            'CROP_FIT_PROVED': len(com_cultura),
            'RECENTLY_ACTIVE': len(ativos),
            'ACTIVATION_READY': len(prontos),
            'PROMISING': len(promissores),
            'INVALID_OR_OUT_OF_SCOPE': len(invalidos),
            'INVALID_DETAIL': {'OUTRO_PAIS': [c['ORIGIN_ID'] for c in fora_pais],
                               'PECUARIA': [c['ORIGIN_ID'] for c in pecu]},
            'DUPLICATE': len(dup),
            'VALID_CREATORS_PER_HUB': len(validos),
            'ACTIVATION_READY_PER_HUB': len(prontos),
        }

    # ── portas medidas por rota nomeada (sem raspagem própria)
    for rota, n in (es_fontes if isinstance(es_fontes, dict) else {}).items():
        pass
    try:
        with open(os.path.join(cr.BASE, 'ES-MASTER-SOURCES.json'), encoding='utf-8') as f:
            rendimento_nomes = json.load(f).get('HUB_YIELD_NAMES_SO_FAR', {})
    except Exception:                                        # noqa: BLE001
        rendimento_nomes = {}
    for rota, n in rendimento_nomes.items():
        if rota in ('AGROINFLUYE_2026',):
            continue                                          # já medido acima, ponta a ponta
        porhub.setdefault(rota, {
            'HUB': rota, 'COUNTRY': 'ES',
            'ROUTE': 'nomes citados em fonte aberta; perfis NÃO resolvidos',
            'PEOPLE_DISCOVERED': n, 'PEOPLE_WITH_PUBLIC_PROFILE': 0,
            'IDENTITIES_PROVED': 0, 'ACTUAL_FARMERS_PROVED': 0,
            'CROP_FIT_PROVED': 0, 'RECENTLY_ACTIVE': 0,
            'ACTIVATION_READY': 0, 'PROMISING': 0,
            'VALID_CREATORS_PER_HUB': 0, 'ACTIVATION_READY_PER_HUB': 0,
            'NOTE': 'porta nomeou pessoas mas os perfis ainda não foram resolvidos',
        })

    # ── seed externa italiana, como comparação de rendimento
    it = cr.carregar('IT-CREATORS-CONSOLIDATED.json')
    if it:
        porhub['SEED_EXTERNA_IT'] = {
            'HUB': 'Seed externa (Itália)', 'COUNTRY': 'IT',
            'ROUTE': 'lista fornecida — não é hub, entra para comparar rendimento',
            'PEOPLE_DISCOVERED': len(it),
            'PEOPLE_WITH_PUBLIC_PROFILE': len([r for r in it
                                               if r.get('HANDLE_EXISTS') == 'RESOLVED']),
            'IDENTITIES_PROVED': len([r for r in it if r.get('IDENTITY_STATE') == 'PROVED']),
            'ACTUAL_FARMERS_PROVED': len([r for r in it if r.get('ACTUAL_FARMER') == 'PROVED']),
            'CROP_FIT_PROVED': len([r for r in it
                                    if r.get('CROP_STATE') in ('PROVED', 'PARTIAL')]),
            'RECENTLY_ACTIVE': 'ver CREATOR-ACTIVITY',
            'ACTIVATION_READY': 0, 'PROMISING': 0,
            'INVALID_OR_OUT_OF_SCOPE': len([r for r in it
                                            if r.get('CROP_STATE') == 'WRONG_ASSIGNMENT']),
            'VALID_CREATORS_PER_HUB': 0, 'ACTIVATION_READY_PER_HUB': 0,
            'NOTE': 'handles errados: 4 · perfis não devolvidos: 3 · presença ínfima: 2',
        }

    tentados = len(porhub)
    total_hubs = len(hubs_reg) if hubs_reg else 43
    ordenado = sorted(porhub.values(), key=lambda x: -(x.get('VALID_CREATORS_PER_HUB') or 0))

    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': '2026-08-30',
        'LAW': '"Hub bom" não é o que tem mais páginas ou prestígio: é o que entrega '
               'gente que o Marketing consegue avaliar.',
        'HUBS_REGISTERED': total_hubs,
        'HUBS_ATTEMPTED': tentados,
        'HUBS_STILL_UNTOUCHED': total_hubs - tentados,
        'INVALID_MEANING': 'fora do recorte desta pergunta (outro país, pecuária, '
                           'patrocinador) — nunca "pessoa ruim". Todos seguem registrados.',
        'YIELD': ordenado,
    }
    with open(os.path.join(cr.BASE, 'HUB-YIELD.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: HUB-YIELD.json')
    print('HUBS_REGISTRADOS=%d  TENTADOS=%d  INTOCADOS=%d'
          % (total_hubs, tentados, total_hubs - tentados))
    for y in ordenado:
        print('  %-26s desc=%-4s validos=%-4s ready=%-3s %s'
              % (str(y['HUB'])[:26], y.get('PEOPLE_DISCOVERED'),
                 y.get('VALID_CREATORS_PER_HUB'), y.get('ACTIVATION_READY_PER_HUB'),
                 y.get('NOTE', '')[:34]))


if __name__ == '__main__':
    montar()
