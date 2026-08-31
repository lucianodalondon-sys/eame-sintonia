#!/usr/bin/env python3
"""
O SEGUNDO SNAPSHOT — com o denominador congelado ANTES de coletar.

POR QUE O UNIVERSO E CONGELADO PRIMEIRO
----------------------------------------
A tentacao era revisitar so as paginas que hoje tem anuncio. Isso viesaria a
medida de forma silenciosa e numa direcao so: um recorte que era ZERO no
snapshot 1 pode estar ATIVO no snapshot 2, e nunca ficariamos sabendo. O
resultado seria um acervo capaz de ver anuncio parar e incapaz de ver anuncio
comecar.

    ZERO_NAO_REVISITADO = ZERO_PARA_SEMPRE

Por isso o manifesto e escrito antes da coleta, com TODOS os 67 recortes do
snapshot 1 — os 38 com conteudo e os 29 zeros honestos. O denominador do
segundo snapshot e o mesmo do primeiro, por construcao.

O QUE ESTA RODADA COLETA, E O QUE ELA SE PROIBE
------------------------------------------------
Coleta so o necessario para COMPARAR:

    PAGE_ID · AD_DELIVERY_COUNTRY · LIBRARY_ID · OBSERVED_STATE
    SOURCE_DECLARED_RESULT_COUNT · OBSERVED_AT

Nao reexecuta leitura de cultura, problema, produto nem criativo para entidade
ja conhecida. Entidade nova e PRESERVADA em bruto para processamento posterior
— esta rodada mede mudanca, nao enriquece acervo.

O QUE DOIS SNAPSHOTS PROVAM, E O QUE NAO
-----------------------------------------
Provam:  PRESENT_BOTH · NEWLY_OBSERVED · NO_LONGER_OBSERVED
         ZERO_TO_ACTIVE · ACTIVE_TO_ZERO

Nao provam: ACTIVE_AGAIN. Esse estado exige a sequencia ativo -> ausente ->
ativo, e tres pontos no tempo. Com dois pontos, afirma-lo seria inventar o
ponto do meio.

    TEMPORAL_CHANGE_CAPABILITY != FULL_LIFECYCLE_STATE_CAPABILITY

E ha uma confusao pior, que este arquivo se recusa a cometer: se nada mudar
entre os dois snapshots, o resultado e CHANGE_OBSERVED = NO com a comparacao
VALIDA. Isso NAO e o mesmo que nao ter conseguido medir.

    NENHUMA_MUDANCA_OCORREU != NAO_CONSEGUIMOS_MEDIR
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import meta_navegador as nav  # noqa: E402

PASTA = os.path.join(ROOT, 'data', 'samples', 'META-EAME')
SNAP1 = os.path.join(PASTA, 'META-ADS-ENTITIES-EAME-V1.json')
ANUNCIANTES = os.path.join(PASTA, 'META-ADVERTISERS-EAME-V1.json')
MANIFESTO = os.path.join(PASTA, 'META-TEMPORAL-SNAPSHOT-MANIFEST.json')
SNAP2 = os.path.join(PASTA, 'META-SNAPSHOT-2-OBSERVATIONS.json')
COMPARACAO = os.path.join(PASTA, 'META-TEMPORAL-COMPARISON-V1.json')

COM_CONTEUDO = 'SLICE_WITH_ADS'
ZERO_HONESTO = 'SLICE_HONEST_ZERO'

PRESENT_BOTH = 'PRESENT_BOTH'
NEWLY_OBSERVED = 'NEWLY_OBSERVED'
NO_LONGER_OBSERVED = 'NO_LONGER_OBSERVED'
ZERO_TO_ACTIVE = 'ZERO_TO_ACTIVE'
ACTIVE_TO_ZERO = 'ACTIVE_TO_ZERO'
SLICE_UNCHANGED = 'SLICE_UNCHANGED_STATE'


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def _ler(caminho, padrao=None):
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _salvar(caminho, obj):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ── 1. congelar o manifesto ──────────────────────────────────────────────────
def congelar_manifesto():
    s1 = _ler(SNAP1, {})
    adv = _ler(ANUNCIANTES, {})
    empresa_de = {}
    for c in adv.get('companies', []):
        for p in c.get('pages', []):
            if p.get('page_id'):
                empresa_de[p['page_id']] = c['company']
    ids_por_slice = {}
    for e in (s1.get('entities') or {}).values():
        for pais in (e.get('countries_reached_observed') or []):
            ids_por_slice.setdefault((e.get('page_id'), pais), set()).add(
                e['meta_ad_library_id'])

    slices = []
    for d in s1.get('collection_diagnostics', []):
        chave = (d.get('page_id'), d.get('country'))
        ids = sorted(ids_por_slice.get(chave, set()))
        slices.append({
            'competitor': empresa_de.get(d.get('page_id')),
            'page_id': d.get('page_id'),
            'page_name': d.get('page_name'),
            'ad_delivery_country': d.get('country'),
            'snapshot_1_state': (COM_CONTEUDO if (d.get('cards_read') or 0) > 0
                                 else ZERO_HONESTO),
            'snapshot_1_completeness': d.get('completeness'),
            'snapshot_1_cards': d.get('cards_read'),
            'snapshot_1_ads_represented': d.get('ads_represented'),
            'snapshot_1_source_declared_count': d.get('results_declared'),
            'snapshot_1_library_ids': ids,
        })
    manifesto = {
        'dataset_owner': 'META_COMPETITOR_EAME',
        'frozen_at': agora(),
        'snapshot_1_as_of_date': s1.get('as_of_date'),
        'slices_total': len(slices),
        'slices_with_ads': sum(1 for s in slices if s['snapshot_1_state'] == COM_CONTEUDO),
        'slices_honest_zero': sum(1 for s in slices if s['snapshot_1_state'] == ZERO_HONESTO),
        'regra': ('o snapshot 2 percorre TODOS estes recortes, inclusive os zeros. '
                  'Revisitar so os ativos esconderia ZERO_TO_ACTIVE e viesaria a '
                  'medida numa direcao so.'),
        'slices': slices,
    }
    _salvar(MANIFESTO, manifesto)
    return manifesto


# ── 2. coletar o snapshot 2, so os campos de comparacao ──────────────────────
_LEVE = r'''(()=>{
 const conta = t => ((t||'').match(/Library ID:\s*\d{6,}/g)||[]).length;
 const nos = [...document.querySelectorAll('div')].filter(d => conta(d.innerText)===1);
 const set = new Set(nos);
 const cartoes = nos.filter(n=>{let p=n.parentElement;while(p){if(set.has(p))return false;p=p.parentElement}return true});
 const vistos = new Set(); const saida = [];
 for (const n of cartoes){
   const t = n.innerText || '';
   const m = t.match(/Library ID:\s*(\d{6,})/);
   if (!m || vistos.has(m[1])) continue;
   vistos.add(m[1]);
   const g = t.match(/(\d+)\s+ads?\s+use\s+this\s+creative\s+and\s+text/i);
   saida.push({library_id: m[1],
               ads_neste_cartao: g ? parseInt(g[1],10) : 1,
               observed_state: /\bActive\b/.test(t.slice(0,200)) ? 'ACTIVE'
                             : /\bInactive\b/.test(t.slice(0,200)) ? 'INACTIVE'
                             : 'NOT_KNOWN'});
 }
 return JSON.stringify({total: saida.length, cartoes: saida});
})()'''


def coletar_slice(s, momento, max_rolagens=60):
    url = nav.url_biblioteca(active_status='all', ad_type='all',
                             country=s['ad_delivery_country'],
                             view_all_page_id=s['page_id'],
                             search_type='page', media_type='all')
    aba = nav.abrir(url, espera=15)
    try:
        cab = nav.cabecalho(aba)
        declarado = cab.get('resultados_declarados')
        rol = nav.rolar_ate_parar(aba, declarado=declarado, max_rolagens=max_rolagens)
        leve = nav.js_json(aba, _LEVE, timeout=120)
    finally:
        nav.fechar(aba)
    cartoes = leve.get('cartoes', [])
    anuncios = nav.anuncios_em(cartoes)
    comp = nav.completude(anuncios, declarado,
                          sem_resultados=bool(cab.get('sem_resultados')))
    return {
        'competitor': s['competitor'],
        'page_id': s['page_id'],
        'page_name': s['page_name'],
        'ad_delivery_country': s['ad_delivery_country'],
        'observed_at': momento,
        'source_declared_result_count': declarado,
        'cards': len(cartoes),
        'ads_represented': anuncios,
        'completeness': comp['state'],
        'scrolls': rol.get('rolagens'),
        'source_url': url,
        'ads': cartoes,
        'slice_state': 'SLICE_OK',
    }


def coletar_snapshot_2():
    manifesto = _ler(MANIFESTO)
    if not manifesto:
        raise RuntimeError('manifesto nao congelado — rode `congelar` primeiro')
    momento = agora()
    anterior = _ler(SNAP2, {})
    feitos = {(o['page_id'], o['ad_delivery_country']): o
              for o in (anterior.get('observations') or [])
              if o.get('slice_state') == 'SLICE_OK'}
    saida, falhas = [], []
    for s in manifesto['slices']:
        chave = (s['page_id'], s['ad_delivery_country'])
        if chave in feitos:
            saida.append(feitos[chave])
            continue
        try:
            o = coletar_slice(s, momento)
        except Exception as e:
            o = {'competitor': s['competitor'], 'page_id': s['page_id'],
                 'page_name': s['page_name'],
                 'ad_delivery_country': s['ad_delivery_country'],
                 'observed_at': momento, 'slice_state': 'SLICE_FAILED',
                 'error': str(e)[:200], 'ads': []}
            falhas.append(o)
        saida.append(o)
        print('  %-34s %s  %3d cartoes  %s' % (
            (s['page_name'] or '')[:34], s['ad_delivery_country'],
            len(o.get('ads', [])), o.get('completeness', o.get('slice_state'))),
            flush=True)
        _salvar(SNAP2, {'dataset_owner': 'META_COMPETITOR_EAME',
                        'as_of_date': momento,
                        'manifest_frozen_at': manifesto['frozen_at'],
                        'slices_total': manifesto['slices_total'],
                        'observations': saida})
    _salvar(SNAP2, {'dataset_owner': 'META_COMPETITOR_EAME',
                    'as_of_date': momento,
                    'manifest_frozen_at': manifesto['frozen_at'],
                    'slices_total': manifesto['slices_total'],
                    'slices_successful': sum(1 for o in saida
                                             if o.get('slice_state') == 'SLICE_OK'),
                    'slices_failed': len(falhas),
                    'observations': saida})
    return saida, falhas


# ── 3. comparar ──────────────────────────────────────────────────────────────
def comparar_slice(ids_antes, ids_depois, ambas_pontas_completas):
    """A regra de comparacao de UM recorte, isolada para poder ser provada.

    `ambas_pontas_completas` e o que separa "sumiu" de "nao consegui ver": um
    anuncio ausente numa listagem incompleta pode nao ter parado — pode estar
    depois do ponto onde a leitura desistiu. Sem as duas pontas completas, a
    ausencia sai em `absent_but_not_claimable`, e nao vira NO_LONGER_OBSERVED.
    """
    antes, depois = set(ids_antes or []), set(ids_depois or [])
    sumidos = sorted(antes - depois)
    transicao = SLICE_UNCHANGED
    if not antes and depois:
        transicao = ZERO_TO_ACTIVE
    elif antes and not depois:
        transicao = ACTIVE_TO_ZERO
    return {
        'present_both': sorted(antes & depois),
        'newly_observed': sorted(depois - antes),
        'no_longer_observed': (sumidos if ambas_pontas_completas else []),
        'absent_but_not_claimable': ([] if ambas_pontas_completas else sumidos),
        'slice_transition': transicao,
    }


def comparar():
    manifesto = _ler(MANIFESTO, {})
    s2 = _ler(SNAP2, {})
    obs = {(o['page_id'], o['ad_delivery_country']): o
           for o in (s2.get('observations') or [])}
    linhas = []
    tot = {PRESENT_BOTH: 0, NEWLY_OBSERVED: 0, NO_LONGER_OBSERVED: 0,
           ZERO_TO_ACTIVE: 0, ACTIVE_TO_ZERO: 0}
    nao_comparaveis = []
    for s in manifesto.get('slices', []):
        chave = (s['page_id'], s['ad_delivery_country'])
        o = obs.get(chave)
        if not o or o.get('slice_state') != 'SLICE_OK':
            nao_comparaveis.append({**chave_dict(s), 'motivo': 'SLICE_NOT_OBSERVED'})
            continue
        # NO_LONGER_OBSERVED so pode ser afirmado com as duas pontas completas.
        forte = (s['snapshot_1_completeness'] in
                 (nav.COMPLETA_BATE_COM_A_FONTE, nav.ZERO_DECLARADO)
                 and o.get('completeness') in
                 (nav.COMPLETA_BATE_COM_A_FONTE, nav.ZERO_DECLARADO))
        r = comparar_slice(s['snapshot_1_library_ids'],
                           [a['library_id'] for a in o.get('ads', [])], forte)
        if r['slice_transition'] in tot:
            tot[r['slice_transition']] += 1
        tot[PRESENT_BOTH] += len(r['present_both'])
        tot[NEWLY_OBSERVED] += len(r['newly_observed'])
        tot[NO_LONGER_OBSERVED] += len(r['no_longer_observed'])
        linhas.append({
            **chave_dict(s),
            'snapshot_1_state': s['snapshot_1_state'],
            'snapshot_1_completeness': s['snapshot_1_completeness'],
            'snapshot_2_completeness': o.get('completeness'),
            'both_ends_complete': forte,
            **r,
        })
    mudou = any(v for k, v in tot.items()
                if k in (NEWLY_OBSERVED, NO_LONGER_OBSERVED, ZERO_TO_ACTIVE,
                         ACTIVE_TO_ZERO))
    saida = {
        'dataset_owner': 'META_COMPETITOR_EAME',
        'snapshot_1_as_of_date': manifesto.get('snapshot_1_as_of_date'),
        'snapshot_2_as_of_date': s2.get('as_of_date'),
        'slices_in_manifest': manifesto.get('slices_total'),
        'slices_compared': len(linhas),
        'slices_not_comparable': nao_comparaveis,
        'totals_unit_ad_card': tot,
        'change_observed': 'YES' if mudou else 'NO',
        'temporal_comparison_capability': (
            'PROVED' if linhas else 'NOT_PROVED'),
        'full_lifecycle_state_capability': 'NOT_PROVED',
        'full_lifecycle_nota': (
            'ACTIVE_AGAIN exige ativo -> ausente -> ativo, e isso pede tres '
            'pontos no tempo. Com dois, afirmar seria inventar o do meio.'),
        'nota_mudanca': (
            'change_observed = NO significa que nada mudou entre as duas datas, '
            'com a comparacao VALIDA. Nao significa que nao conseguimos medir.'),
        'slices': linhas,
    }
    _salvar(COMPARACAO, saida)
    return saida


def chave_dict(s):
    return {'competitor': s.get('competitor'), 'page_id': s.get('page_id'),
            'page_name': s.get('page_name'),
            'ad_delivery_country': s.get('ad_delivery_country')}


if __name__ == '__main__':
    acao = sys.argv[1] if len(sys.argv) > 1 else 'congelar'
    if acao == 'congelar':
        m = congelar_manifesto()
        print(json.dumps({k: m[k] for k in ('slices_total', 'slices_with_ads',
                                            'slices_honest_zero',
                                            'snapshot_1_as_of_date', 'frozen_at')},
                         ensure_ascii=False, indent=2))
    elif acao == 'coletar':
        ok, falhas = coletar_snapshot_2()
        print(json.dumps({'slices': len(ok), 'falhas': len(falhas)}))
    elif acao == 'comparar':
        r = comparar()
        print(json.dumps({k: r[k] for k in (
            'snapshot_1_as_of_date', 'snapshot_2_as_of_date', 'slices_compared',
            'totals_unit_ad_card', 'change_observed',
            'temporal_comparison_capability')}, ensure_ascii=False, indent=2))
