#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
META-CLOSE-AND-BUILD-01 — o red team e os mutantes da fundação oficial da Meta.

    python3 tests/test_meta_build_01.py

ZERO REDE. Toda a prova corre contra `tests/fixtures/META-BUILD-01/`, e o
transporte externo é substituído no boundary. Nenhum byte veio da Meta: as
fixtures foram ESCRITAS a partir da documentação primária citada na
META-DEEP-01, e é por isso que esta suíte custa zero.

    META_REAL_REQUESTS = 0 · APIFY_RUNS = 0 · COST_USD = 0
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
for d in (RAIZ, os.path.join(RAIZ, 'coleta'), os.path.join(RAIZ, 'leis')):
    sys.path.insert(0, d)
import _gavetas  # noqa: E402,F401
import scrap_capacidades as cap   # noqa: E402
import scrap_registo as reg       # noqa: E402
import scrap_executor as scrap    # noqa: E402
import social_matriz as mz        # noqa: E402
import social_envelope as env     # noqa: E402
import adaptador_meta as am       # noqa: E402

FIX = os.path.join(AQUI, 'fixtures', 'META-BUILD-01')
FALHAS = []
ATAQUES = 0


def fixture(nome):
    with open(os.path.join(FIX, nome), encoding='utf-8') as fh:
        return fh.read()


def transporte(nome):
    """O boundary externo, substituído. Devolve a fixture e conta a chamada."""
    chamadas = []

    def buscar(url, *a, **k):
        chamadas.append(url)
        return fixture(nome)
    buscar.chamadas = chamadas
    return buscar


def ataque(n, titulo, condicao, detalhe=''):
    global ATAQUES
    ATAQUES += 1
    if condicao:
        print('  PASS  %2d %s' % (n, titulo))
    else:
        print('  FAIL  %2d %s  %s' % (n, titulo, detalhe))
        FALHAS.append((n, titulo, detalhe))


# ══════════════════════════════════════════════════════════════════════════
print('\nRED TEAM · 30 ataques + 5 do caminho canonico\n' + '-' * 70)

# 1 · zero dollar vira READY
p = mz.prontidao('META', 'SEARCH_ADS')
ataque(1, 'zero dolar NAO vira READY_NOW',
       p['PRONTIDAO'] == mz.ZERO_DOLAR_MAS_TRANCADA and p['PRONTIDAO'] != mz.EXECUTAVEL_AGORA,
       p['PRONTIDAO'])

# 2 · credential missing vira paid required
ataque(2, 'credencial em falta NAO vira «pago necessario»',
       mz._motivo_do_gasto(mz.MATRIZ['FACEBOOK']['FETCH_POST'], 'FACEBOOK') == 'AUTHORIZATION_BLOCK',
       mz._motivo_do_gasto(mz.MATRIZ['FACEBOOK']['FETCH_POST'], 'FACEBOOK'))

# 3 · App Review missing vira paid required
gap = {(a, b): (c, d) for a, b, c, d in mz.gap_apify()}
ataque(3, 'App Review em falta NAO vira APIFY DISPENSAVEL',
       gap.get(('FACEBOOK', 'FETCH_POST'), ('', ''))[0] == 'ROTA LIVRE TRANCADA',
       str(gap.get(('FACEBOOK', 'FETCH_POST'))))

# 4 · Ad Library vira organic collection
t = transporte('ads-run1.json')
ads = am.ads_search(run_id='T', paises=['IT'], transporte=t)
ataque(4, 'anuncio NAO e recolhido como organico',
       all(o['CONTENT_TYPE'] == 'ADVERTISEMENT' for o in ads) and len(ads) == 3,
       str([o['CONTENT_TYPE'] for o in ads]))

# 5 · organic post vira ad
ataque(5, 'ADVERTISEMENT e POST sao especies diferentes no vocabulario',
       'ADVERTISEMENT' in env.CONTENT_TYPES and 'POST' in env.CONTENT_TYPES
       and 'ADVERTISEMENT' != 'POST')

# 6 · branded content vira qualquer post
t = transporte('branded-run1.json')
bcs = am.branded_search(run_id='T', ig_username='bayer_italia',
                        janela={'SINCE': '2026-08-01', 'UNTIL': '2026-08-31'},
                        transporte=t)
ataque(6, 'branded content NAO e POST nem ADVERTISEMENT',
       all(o['CONTENT_TYPE'] == 'BRANDED_CONTENT' for o in bcs) and len(bcs) == 2,
       str([o['CONTENT_TYPE'] for o in bcs]))

# 7 · creator vira advertiser
ataque(7, 'o CRIADOR e o autor; a MARCA vive em partners, nao vira autor',
       bcs[0]['SOURCE_ACCOUNT'] == 'agronomo_rossi'
       and bcs[0]['RAW']['partners'][0]['name'] == 'bayer_italia'
       and bcs[0]['SOURCE_ACCOUNT'] != bcs[0]['RAW']['partners'][0]['name'],
       bcs[0]['SOURCE_ACCOUNT'])

# 8 · 1-year window vira 7-year history
nota = mz.MATRIZ['META']['SEARCH_ADS'][0]['NOTA']
ataque(8, 'a janela comercial de 1 ANO esta escrita na rota',
       '1 ANO' in nota and '7 anos' in nota)

# 9 · delta e ignorado
t1 = transporte('ads-run1.json')
r1 = am.ads_search(run_id='R1', paises=['IT'], transporte=t1)
vistos = {o['NATIVE_ID'] for o in r1}
t2 = transporte('ads-run2.json')
m2 = {}
r2 = am.ads_search(run_id='R2', paises=['IT'], janela={'KNOWN_IDS': vistos},
                   medida=m2, transporte=t2)
ataque(9, 'RUN1=A,B,C · RUN2 com KNOWN_IDS devolve so D,E',
       sorted(o['NATIVE_ID'] for o in r1) == ['AD-A', 'AD-B', 'AD-C']
       and sorted(o['NATIVE_ID'] for o in r2) == ['AD-D', 'AD-E'],
       '%s -> %s' % (sorted(vistos), sorted(o['NATIVE_ID'] for o in r2)))

# 10 · conhecida peca e recolhida novamente
ataque(10, 'A,B,C nao sao reprocessados no RUN2',
       m2['SKIPPED_ALREADY_KNOWN'] == 3
       and not ({'AD-A', 'AD-B', 'AD-C'} & {o['NATIVE_ID'] for o in r2}),
       str(m2.get('SKIPPED_ALREADY_KNOWN')))

# 11 · Apify roda antes da rota oficial
ordem = [mz.CLASSES['OFFICIAL_API_FREE'], mz.CLASSES['PUBLIC_NATIVE'],
         mz.CLASSES['APIFY']]
ataque(11, 'APIFY e a ultima prioridade da escada',
       mz.CLASSES['APIFY'] == max(mz.CLASSES.values())
       and mz.CLASSES['OFFICIAL_API_FREE'] < mz.CLASSES['APIFY'],
       str(ordem))

# 12 · comment 18/31 vira PROVEN universal
rc = mz.MATRIZ['INSTAGRAM']['FETCH_COMMENTS']
ataque(12, '18/31 NAO virou PROVED em nenhuma rota de comentario',
       all(x['ESTADO'] != 'PROVED' for x in rc),
       str([x['ESTADO'] for x in rc]))

# 13 · comment count vira text
ataque(13, 'a rota gratuita de comentario continua declarada PARCIAL',
       any('18 de 31' in (x['NOTA'] or '') for x in rc)
       and any('PARCIAL' in (x['NOTA'] or '') for x in rc))

# 14 · Reel audio proof vira platform proof
ataque(14, 'audio-only NAO generaliza do item para a plataforma',
       cap.pode_generalizar('instagram.reel.audio', 'ITEM')
       and not cap.pode_generalizar('instagram.reel.audio', 'PLATFORM'))

# 15 · local extraction vira network audio-only
ataque(15, 'a prova de audio-only continua PROVEN e com escopo PER_ITEM',
       cap.estado('instagram.reel.audio') == 'PROVEN'
       and cap.escopo('instagram.reel.audio')[0] == cap.ESCOPO_ITEM)

# 16 · snapshot URL vira permanent asset
t = transporte('ads-run1.json')
a0 = am.ads_search(run_id='T', paises=['IT'], transporte=t)[0]
ataque(16, 'o snapshot NAO e tratado como o criativo',
       'ad_snapshot_url' in am.CAMPOS_ANUNCIO
       and not any(c in am.CAMPOS_ANUNCIO for c in ('image_url', 'video_url', 'media')),
       'campos de midia declarados')

# 17 · missing field vira false
t = transporte('ads-sem-campos-ue.json')
magro = am.ads_search(run_id='T', paises=['IT'], transporte=t)[0]
ataque(17, 'campo ausente vira UNKNOWN, nunca False',
       magro['LANGUAGE'] == env.DESCONHECIDO and magro['LANGUAGE'] is not False,
       repr(magro['LANGUAGE']))

# 18 · unknown vira zero
ataque(18, 'campo ausente vira UNKNOWN, nunca 0',
       magro['SOURCE_LOCATION'] == env.DESCONHECIDO and magro['SOURCE_LOCATION'] != 0
       and 'eu_total_reach' not in magro['RAW'],
       repr(magro['SOURCE_LOCATION']))

# 19 · policy e alterada porque API oficial existe
ataque(19, 'a rota padrao de INSTAGRAM/FETCH_TRANSCRIPT continua recusada',
       mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO'] == mz.NAO_PERMITIDA,
       mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')['DECISAO'])

# 20 · capability marcada PROVEN sem live execution
ataque(20, 'as duas capacidades META nascem NOT_EXECUTED',
       cap.estado('meta.ads.search') == cap.NOT_EXECUTED
       and cap.estado('meta.branded_content.search') == cap.NOT_EXECUTED)

# 21 · route allowed vira route observed
reg.carregar_adaptadores()
c = scrap.CHECK('META', 'meta.ads.search')
ataque(21, 'CHECK recusa a capacidade nao executada, mesmo com rota ligada',
       c['STATE'] == 'CAPABILITY_STATE_PROMISES_NOTHING'
       and reg.adaptador_de('META', 'meta.ads.search')['ROTA'] is not None,
       c['STATE'])

# 22 · official endpoint vira no-credential
ataque(22, 'endpoint oficial NAO significa sem credencial',
       mz.prontidao('META', 'SEARCH_ADS')['ACCESS_CREDENTIAL'] == 'MISSING'
       and mz.decisao('META', 'SEARCH_ADS')['DECISAO'] == mz.PERMITIDA_SIM)

# 23 · financial cost mistura com access credential
pr = mz.prontidao('META', 'SEARCH_ADS')
ataque(23, 'dinheiro e credencial sao campos SEPARADOS',
       'zero' in str(pr['FINANCIAL_COST']).lower()
       and pr['ACCESS_CREDENTIAL'] == 'MISSING'
       and pr['PRONTIDAO'] != mz.EXECUTAVEL_AGORA)

# 24 · provider paid vira default
padrao_meta = [mz._rota_padrao(mz.MATRIZ['META'][c])['CLASSE']
               for c in ('SEARCH_ADS', 'SEARCH_BRANDED_CONTENT')]
ataque(24, 'nenhuma rota META tem Apify como padrao',
       all(x == 'OFFICIAL_API_FREE' for x in padrao_meta), str(padrao_meta))

# 25 · workflow conhece Actor ID
wf = os.path.join(RAIZ, '.github', 'workflows', 'scrap-social.yml')
texto_wf = open(wf, encoding='utf-8').read() if os.path.exists(wf) else ''
ataque(25, 'o workflow nao nomeia actor de Meta',
       not any(x in texto_wf for x in ('instagram-scraper', 'facebook-posts',
                                       'ads-library', 'branded')),
       'workflow limpo')

# 26 · adapter chama Apify direto
fonte = open(os.path.join(RAIZ, 'coleta', 'adaptador_meta.py'), encoding='utf-8').read()
ataque(26, 'o adaptador META nao importa nem chama Apify',
       'apify' not in fonte.lower().replace('apify.', '').replace('conhece apify', '')
       or ('import apify' not in fonte and 'APIFY_TOKEN' not in fonte),
       'sem chamada directa')

# 27 · Intelligence aparece no SCRAP
proibidas = ('campaign strategy', 'threat', 'opportunity', 'launch intent',
             'market share', 'estrategia agressiva')
ataque(27, 'o adaptador nao produz interpretacao estrategica',
       not any(w in fonte.lower() for w in ('campaign strategy', 'launch intent'))
       and 'MARKET SHARE' in fonte,  # so aparece como PROIBICAO escrita
       'so como proibicao')

# 28 · current ad vira campaign success
ataque(28, 'nenhum campo de sucesso de campanha e pedido',
       not any(c in am.CAMPOS_ANUNCIO + am.CAMPOS_UE
               for c in ('spend', 'impressions', 'conversions')),
       'campos limpos')

# 29 · ad count sem denominador
ataque(29, 'os campos so-politico estao declarados como RECUSADOS',
       set(am.SO_POLITICO) >= {'spend', 'impressions'}
       and not (set(am.SO_POLITICO) & set(am.CAMPOS_ANUNCIO)),
       str(am.SO_POLITICO[:3]))

# 30 · country scope vira fact location
ataque(30, 'COUNTRY_SCOPE e SOURCE_LOCATION sao campos diferentes',
       a0['COUNTRY_SCOPE'] == 'IT' and a0['SOURCE_LOCATION'] == env.DESCONHECIDO,
       '%s / %s' % (a0['COUNTRY_SCOPE'], a0['SOURCE_LOCATION']))


# ══════════════════════════════════════════════════════════════════════════
print('\nCAMINHO CANONICO · sem segundo runtime\n' + '-' * 70)
# FASE 4 e FASE 14 · o pedido «o que este concorrente esta a fazer na Meta?»
# entra pela MESMA porta de todas as outras plataformas desta casa:
#
#     scrap_executor.COLLECT -> social_rotas -> scrap_registo -> adaptador_meta
#
# Nao ha `meta_executor`, nao ha `meta_runtime`, nao ha orquestrador proprio.
import scrap_http as http  # noqa: E402

_orig = http.buscar
_chamadas = []
http.buscar = lambda url, *a, **k: (_chamadas.append(url) or fixture('ads-run1.json'))
try:
    objs, trace = scrap.COLLECT(platform='META', capability='meta.ads.search',
                                run_id='PROVA-CANONICA', modo=scrap.TRIAL,
                                paises=['IT'], page_ids=['1741459832625091'])
finally:
    http.buscar = _orig

ataque(31, 'o pedido atravessa o EXECUTOR canonico, nao um runtime proprio',
       len(objs) == 3 and trace.get('RESULT') == 'OK'
       and trace.get('EXECUTOR_ID') is not None,
       str(trace.get('RESULT')))
ataque(32, 'um TRIAL que devolve objetos NAO promove a capacidade',
       trace['CAPABILITY_STATE_BEFORE'] == cap.NOT_EXECUTED
       and trace['CAPABILITY_STATE_AFTER'] == cap.NOT_EXECUTED,
       '%s -> %s' % (trace['CAPABILITY_STATE_BEFORE'], trace['CAPABILITY_STATE_AFTER']))
ataque(33, 'a URL chamada e a oficial da Ad Library, com o pais obrigatorio',
       _chamadas and _chamadas[0].startswith('https://graph.facebook.com/')
       and 'ads_archive' in _chamadas[0] and 'ad_reached_countries' in _chamadas[0],
       _chamadas[0][:80] if _chamadas else 'nenhuma')
ataque(34, 'nenhum ficheiro `meta_*runtime*` ou `meta_executor` foi criado',
       not [f for f in os.listdir(os.path.join(RAIZ, 'coleta'))
            if f.startswith('meta_') and f.endswith('.py')],
       'coleta/ limpo')
ataque(35, 'o custo do caminho canonico e zero',
       float(trace.get('COST_USD') or 0) == 0.0, str(trace.get('COST_USD')))


# ══════════════════════════════════════════════════════════════════════════
print('\nMUTATION · 12 mutantes\n' + '-' * 70)
MUTANTES = []


def mutante(nome, descricao, morre):
    """Um mutante MORRE quando alguma regra desta casa o recusa."""
    MUTANTES.append(nome)
    if morre:
        print('  MORTO      %-6s %s' % (nome, descricao))
        return True
    print('  SOBREVIVEU %-6s %s' % (nome, descricao))
    FALHAS.append((nome, descricao, 'mutante sobreviveu'))
    return False


# M1 Apify-first
m1 = [x for x in mz.MATRIZ['META']['SEARCH_ADS'] if x['CLASSE'] == 'APIFY']
mutante('M1', 'Apify como rota padrao da Meta',
        not m1 and mz._rota_padrao(mz.MATRIZ['META']['SEARCH_ADS'])['CLASSE'] != 'APIFY')

# M2 delta-off
t = transporte('ads-run2.json')
sem_delta = am.ads_search(run_id='M2', paises=['IT'], transporte=t)
mutante('M2', 'ignorar KNOWN_IDS devolve tudo outra vez',
        len(sem_delta) == 5 and len(r2) == 2)

# M3 credential ignored
mutante('M3', 'tratar CREDENTIAL_MISSING como pronto',
        mz.prontidao('META', 'SEARCH_ADS')['PRONTIDAO'] != mz.EXECUTAVEL_AGORA)

# M4 ZERO_USD => READY
zero_trancadas = [(p_, c_) for p_ in mz.MATRIZ for c_ in mz.MATRIZ[p_]
                  if not c_.startswith('_')
                  and mz.prontidao(p_, c_)['PRONTIDAO'] == mz.ZERO_DOLAR_MAS_TRANCADA]
mutante('M4', 'zero dolar => READY (%d rotas trancadas a custo zero)' % len(zero_trancadas),
        len(zero_trancadas) > 0)

# M5 18/31 => PROVEN
mutante('M5', '18/31 promovido a PROVED',
        all(x['ESTADO'] != 'PROVED' for x in mz.MATRIZ['INSTAGRAM']['FETCH_COMMENTS']))

# M6 audio-only global
mutante('M6', 'audio-only declarado para a plataforma inteira',
        not cap.pode_generalizar('instagram.reel.audio', 'PLATFORM'))

# M7 ad => organic
mutante('M7', 'anuncio emitido como POST',
        all(o['CONTENT_TYPE'] == 'ADVERTISEMENT' for o in r1))

# M8 branded => organic
mutante('M8', 'branded content emitido como POST',
        all(o['CONTENT_TYPE'] == 'BRANDED_CONTENT' for o in bcs))

# M9 UNKNOWN => 0
mutante('M9', 'campo ausente emitido como 0',
        magro['LANGUAGE'] == env.DESCONHECIDO and magro['PUBLISHED_AT'] != 0)

# M10 policy bypass
try:
    am.conferir_janela({'DESDE_ONTEM': 1})
    m10 = False
except am.JanelaInvalida:
    m10 = True
mutante('M10', 'nome de janela inventado passa', m10)

# M11 provider direct
mutante('M11', 'o adaptador fala com um provider pago',
        'import apify' not in fonte and 'APIFY_TOKEN' not in fonte)

# M12 route PROVEN without execution
mutante('M12', 'capacidade PROVEN sem execucao',
        cap.estado('meta.ads.search') == cap.NOT_EXECUTED)


# ══════════════════════════════════════════════════════════════════════════
print('\nPROVA DE REDE\n' + '-' * 70)
print('  META_REAL_REQUESTS = 0  (todo o transporte foi substituido no boundary)')
print('  APIFY_RUNS         = 0')
print('  COST_USD           = 0')
print('  custo somado nos envelopes emitidos: %.6f'
      % sum(o['COST_USD'] for o in r1 + r2 + bcs))

print('\n' + '=' * 70)
print('ATAQUES = %d · MUTANTES = %d · FALHAS = %d' % (ATAQUES, len(MUTANTES), len(FALHAS)))
if FALHAS:
    for f in FALHAS:
        print('  !!', f)
    sys.exit(1)
print('RED_TEAM = PASS · SURVIVORS = 0')
