#!/usr/bin/env python3
"""
O ARTEFATO DERIVADO — e a placa dizendo que ele e derivado.

`META-COMPETITOR-PILOT-EAME.json` e uma LEITURA do acervo, feita para que uma
integracao futura do portal possa consumir sem varrer tudo. Ele nao e dono de
nada. Se contradisser as entidades, quem esta errado e ele, e o conserto e
regerar — nunca editar o derivado.

    DERIVADO != FONTE DA VERDADE

O QUE ELE MOSTRA, E COM QUE DENOMINADOR
----------------------------------------
Toda contagem sai com o de-que-total do lado. "3 anuncios ativos" sozinho nao
diz nada; "3 ativos em 41 observados da pagina X na Espanha" diz. Numero sem
denominador e o jeito mais barato de fazer decisao ruim parecer boa.

E toda contagem e de ANUNCIO. Nao ha, e nao pode haver, escore de pressao
competitiva, share of voice ou estimativa de investimento — a missao proibe, e
o dado nao sustentaria mesmo:

    AD_COUNT != SPEND != PRESSURE

INACTIVE_LAST_365D
-------------------
Conta anuncio inativo cuja veiculacao terminou nos ultimos 365 dias, pela data
que a FONTE declara. Anuncio inativo sem data de fim legivel nao entra nem de
um lado nem do outro: vira `END_DATE_NOT_READ`, porque supor que terminou
ontem seria inventar recencia.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PASTA = os.path.join(ROOT, 'data', 'samples', 'META-EAME')
ENTIDADES = os.path.join(PASTA, 'META-ADS-ENTITIES-EAME-V1.json')
EVENTOS = os.path.join(PASTA, 'META-ADS-EVENTS-EAME-V1.json')
ANUNCIANTES = os.path.join(PASTA, 'META-ADVERTISERS-EAME-V1.json')
DEST = os.path.join(PASTA, 'META-COMPETITOR-PILOT-EAME.json')
DEST_METRICAS = os.path.join(PASTA, 'META-PILOT-METRICS-V1.json')

END_DATE_NOT_READ = 'END_DATE_NOT_READ'
PROVED = 'PROVED'


def _ler(caminho, padrao=None):
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _conta(mapa, chave):
    mapa[chave] = mapa.get(chave, 0) + 1


def metricas(acervo, anunciantes, eventos):
    ent = (acervo or {}).get('entities', {})
    por_pais, por_empresa, por_produto, por_categoria = {}, {}, {}, {}
    por_ativacao = {}
    ativos = crop_proved = issue_proved = 0
    inativos_365 = 0
    sem_data_fim = 0
    limite = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()

    for e in ent.values():
        for p in (e.get('countries_reached_observed') or []):
            _conta(por_pais, p)
        _conta(por_empresa, e.get('company') or 'NOT_KNOWN')
        r = e.get('reading') or {}
        for c in (r.get('product_category') or []):
            _conta(por_categoria, c)
        for a in (r.get('activation_type') or []):
            _conta(por_ativacao, a)
        for p in (r.get('product_candidates') or []):
            if p.get('state') == PROVED:
                _conta(por_produto, p['product_name'])
        if r.get('crop_state') == PROVED:
            crop_proved += 1
        if r.get('issue_state') == PROVED:
            issue_proved += 1
        if e.get('active_status') == 'ACTIVE':
            ativos += 1
        else:
            fim = e.get('end_date')
            if not fim:
                sem_data_fim += 1
            elif fim >= limite:
                inativos_365 += 1

    empresas = (anunciantes or {}).get('companies', [])
    return {
        'advertisers_attempted': (anunciantes or {}).get('advertisers_attempted'),
        'advertisers_resolved': (anunciantes or {}).get('advertisers_resolved'),
        'pages_resolved_with_page_id': sum(
            1 for c in empresas for p in c.get('pages', []) if p.get('page_id')),
        # DOIS NUMEROS, PORQUE SAO DUAS COISAS
        # A entidade do acervo e um CARTAO (grupo de criativo). A fonte conta
        # ANUNCIOS. Publicar so um dos dois faria a leitura errada em algum
        # lugar: "1.111 anuncios" quando sao 1.111 cartoes, ou o contrario.
        'ad_cards_found': len(ent),
        'ads_represented_by_source_declaration': sum(
            int(e.get('ads_in_this_creative_group') or 1) for e in ent.values()),
        'cards_with_declared_creative_group': sum(
            1 for e in ent.values()
            if int(e.get('ads_in_this_creative_group') or 1) > 1),
        'ads_found': len(ent),
        'ads_found_nota': 'igual a ad_cards_found. CARTAO != ANUNCIO — ver '
                          'ads_represented_by_source_declaration.',
        'active_ads_observed': ativos,
        'inactive_last_365d': inativos_365,
        'inactive_end_date_not_read': sem_data_fim,
        'inactive_end_date_not_read_nota': (
            'anuncio inativo sem data de fim legivel na fonte. Nao entra em '
            'INACTIVE_LAST_365D: supor recencia seria inventar.'),
        'ads_by_country_reached': por_pais,
        'ads_by_company': por_empresa,
        'ads_by_product_proved': por_produto,
        'ads_by_category': por_categoria,
        'ads_by_activation_type': por_ativacao,
        'ads_with_crop_proved': crop_proved,
        'ads_with_issue_proved': issue_proved,
        'crop_proved_denominator': len(ent),
        'issue_proved_denominator': len(ent),
        'events_total': len((eventos or {}).get('events', [])),
        'baseline': (eventos or {}).get('baseline'),
        'aviso': 'todas as contagens sao de ANUNCIO OBSERVADO. Nao medem '
                 'investimento, venda, share nem pressao competitiva.',
    }


# PERFIL DE ENTREGA — o escopo da pagina medido, em vez de lido no nome
# ----------------------------------------------------------------------
# Medido em 30/08/2026, com a coleta pais a pais:
#
#     Bayer Crop Science Espana .... ES 189 · IT 0 · FR 0
#     Bayer Crop Science Italia .... ES   0 · IT 48 · FR 0
#     Bayer Crop Science Australia . ES   1 · IT  1 · FR 0
#
# Isso e prova de comportamento, e vale mais que o "Espana" no fim do nome: uma
# pagina pode se chamar Espana e entregar na Europa inteira. O estado sai como
# `SINGLE_COUNTRY_DELIVERY_OBSERVED` — OBSERVADO, nunca DECLARADO, porque so
# medimos os tres paises do piloto. Uma pagina que entrega so na Espanha ENTRE
# ES, IT e FR pode estar entregando na Alemanha sem que a gente saiba.
#
#     ENTREGA_OBSERVADA_NOS_TRES != ENTREGA_NO_MUNDO
UM_PAIS = 'SINGLE_COUNTRY_DELIVERY_OBSERVED'
VARIOS_PAISES = 'MULTI_COUNTRY_DELIVERY_OBSERVED'
SEM_ENTREGA = 'NO_DELIVERY_OBSERVED_IN_PILOT_COUNTRIES'


def perfil_de_entrega(acervo, paises=('ES', 'IT', 'FR')):
    ent = (acervo or {}).get('entities', {})
    por_pagina = {}
    for e in ent.values():
        pid = e.get('page_id')
        if not pid:
            continue
        p = por_pagina.setdefault(pid, {
            'page_id': pid, 'page_name': e.get('page_name_resolved'),
            'company': e.get('company'),
            'ads_by_country_reached': {c: 0 for c in paises}})
        for c in (e.get('countries_reached_observed') or []):
            if c in p['ads_by_country_reached']:
                p['ads_by_country_reached'][c] += 1
    for p in por_pagina.values():
        com = [c for c, n in p['ads_by_country_reached'].items() if n > 0]
        p['countries_with_ads'] = com
        p['delivery_profile'] = (SEM_ENTREGA if not com else
                                 UM_PAIS if len(com) == 1 else VARIOS_PAISES)
        p['delivery_profile_denominator'] = list(paises)
        p['nota'] = ('perfil OBSERVADO entre ES, IT e FR apenas. Nao diz nada '
                     'sobre entrega fora desses tres paises.')
    return por_pagina


def _resumo_reading(entidades, campo, estado_campo):
    saida = {}
    for e in entidades:
        r = e.get('reading') or {}
        if r.get(estado_campo) != PROVED:
            continue
        for item in (r.get(campo) or []):
            if item.get('state') == PROVED and item.get('canonical'):
                saida[item['canonical']] = saida.get(item['canonical'], 0) + 1
    return saida


def artefato(acervo, eventos):
    ent = list((acervo or {}).get('entities', {}).values())
    por_chave = {}
    for e in ent:
        for pais in (e.get('countries_reached_observed') or []):
            por_chave.setdefault((pais, e.get('company')), []).append(e)

    blocos = []
    for (pais, empresa), lista in sorted(por_chave.items(),
                                         key=lambda kv: (kv[0][0], kv[0][1] or '')):
        ativos = [e for e in lista if e.get('active_status') == 'ACTIVE']
        recentes = sorted(
            [e for e in lista if e.get('start_date')],
            key=lambda e: e['start_date'], reverse=True)[:5]
        produtos = {}
        for e in lista:
            for p in ((e.get('reading') or {}).get('product_candidates') or []):
                if p.get('state') == PROVED:
                    produtos[p['product_name']] = produtos.get(p['product_name'], 0) + 1
        eventos_desta = [ev for ev in (eventos or {}).get('events', [])
                         if ev.get('meta_ad_library_id') in
                         {e['meta_ad_library_id'] for e in lista}]
        blocos.append({
            'country_reached': pais,
            'country_semantics': 'AD_REACHED_COUNTRY, nao AD_TARGET_COUNTRY',
            'competitor': empresa,
            'ads_observed': len(lista),
            'active_ads': len(ativos),
            'active_ads_denominator': len(lista),
            'recent_ads_by_source_start_date': [
                {'meta_ad_library_id': e['meta_ad_library_id'],
                 'start_date': e.get('start_date'),
                 'active_status': e.get('active_status')} for e in recentes],
            'products': produtos or {'state': 'NOT_KNOWN'},
            'crops': _resumo_reading(lista, 'crop', 'crop_state') or {'state': 'NOT_KNOWN'},
            'issues': _resumo_reading(lista, 'issue', 'issue_state') or {'state': 'NOT_KNOWN'},
            'last_change': (eventos_desta[-1] if eventos_desta
                            else {'state': 'BASELINE_ONLY'}),
            'top_evidence': [
                {'meta_ad_library_id': e['meta_ad_library_id'],
                 'ad_snapshot_url': e.get('ad_snapshot_url'),
                 'source_url': e.get('source_url'),
                 'page_name': e.get('page_name_resolved'),
                 'page_id': e.get('page_id'),
                 'start_date': e.get('start_date'),
                 'active_status': e.get('active_status'),
                 'creative_text_excerpt': (e.get('creative_text') or '')[:220]}
                for e in lista[:3]],
        })

    return {
        'artifact': 'META-COMPETITOR-PILOT-EAME',
        'dataset_owner': 'META_COMPETITOR_EAME',
        'derived_from': ['META-ADS-ENTITIES-EAME-V1.json',
                         'META-ADS-EVENTS-EAME-V1.json'],
        'read_only': True,
        'is_source_of_truth': False,
        'not_wired_to_portal': True,
        'as_of_date': (acervo or {}).get('as_of_date'),
        'meta_route': (acervo or {}).get('meta_route'),
        'blocks': blocos,
        'cannot_claim': [
            'que o concorrente vendeu qualquer coisa',
            'que o concorrente tem participacao de mercado',
            'que o produto anunciado esta autorizado naquele pais',
            'que o produto esta disponivel nas lojas',
            'quanto o concorrente investiu',
            'que a atividade cresceu, sem uma coleta anterior para comparar',
            'que o pais alcancado e o pais alvo',
        ],
    }


def _so_especie(entidade, campo):
    return sorted({c['canonical'] for c in ((entidade.get('reading') or {}).get(campo) or [])
                   if c.get('state') == PROVED and c.get('canonical')})


def _so_grupo(entidade, campo):
    return sorted({c['term_matched'] for c in ((entidade.get('reading') or {}).get(campo) or [])
                   if c.get('state') != PROVED and c.get('term_matched')})


def top_evidencias(acervo, n=20):
    ent = list((acervo or {}).get('entities', {}).values())
    pontuados = sorted(
        ent,
        key=lambda e: (
            (e.get('reading') or {}).get('crop_state') == PROVED,
            (e.get('reading') or {}).get('issue_state') == PROVED,
            e.get('active_status') == 'ACTIVE',
            e.get('start_date') or ''),
        reverse=True)[:n]
    return [{
        'meta_ad_library_id': e['meta_ad_library_id'],
        'company': e.get('company'),
        'page_name': e.get('page_name_resolved'),
        'page_id': e.get('page_id'),
        'country_reached': (e.get('countries_reached_observed') or [None])[0],
        'start_date': e.get('start_date'), 'end_date': e.get('end_date'),
        'active_status': e.get('active_status'),
        'ad_snapshot_url': e.get('ad_snapshot_url'),
        'source_url': e.get('source_url'),
        # especie e grupo em campos diferentes. Misturar os dois enfiava um
        # `None` no meio da lista de culturas — o `None` era o termo de grupo,
        # que por definicao nao tem especie. Ficavam parecendo dado faltando
        # quando eram dois tipos de achado distintos.
        'crop_proved': _so_especie(e, 'crop'),
        'crop_group_partial': _so_grupo(e, 'crop'),
        'issue_proved': _so_especie(e, 'issue'),
        'issue_group_partial': _so_grupo(e, 'issue'),
        'activation_type': (e.get('reading') or {}).get('activation_type'),
        'creative_text_excerpt': (e.get('creative_text') or '')[:300],
    } for e in pontuados]


def rodar():
    acervo = _ler(ENTIDADES, {})
    eventos = _ler(EVENTOS, {})
    anunciantes = _ler(ANUNCIANTES, {})
    art = artefato(acervo, eventos)
    met = metricas(acervo, anunciantes, eventos)
    met['top_20_evidence'] = top_evidencias(acervo)
    perfis = perfil_de_entrega(acervo)
    met['page_delivery_profile'] = list(perfis.values())
    art['page_delivery_profile'] = list(perfis.values())
    os.makedirs(PASTA, exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
    with open(DEST_METRICAS, 'w', encoding='utf-8') as f:
        json.dump(met, f, ensure_ascii=False, indent=2)
    return art, met


if __name__ == '__main__':
    art, met = rodar()
    print(json.dumps({k: met[k] for k in (
        'advertisers_attempted', 'advertisers_resolved', 'ads_found',
        'active_ads_observed', 'inactive_last_365d', 'ads_with_crop_proved',
        'ads_with_issue_proved', 'ads_by_country_reached')},
        ensure_ascii=False, indent=2))
    print('blocos no artefato: %d' % len(art['blocks']))
