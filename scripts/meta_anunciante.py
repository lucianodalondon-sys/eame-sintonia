#!/usr/bin/env python3
"""
QUEM E O ANUNCIANTE — resolver a PAGINA, nao a palavra "Syngenta".

A missao proibe pesquisar so por palavra de marca, e a primeira leitura mostrou
por que. Em 30/08/2026, `q=syngenta&country=ES` devolveu, no topo, anuncios em
TAGALO da pagina `syngenta.ph`, falando de arroz hibrido nas Filipinas. Sao
anuncios reais, e a Espanha e mesmo um pais alcancado — ha diaspora filipina la.
Mas chamar aquilo de "atividade da Syngenta na Espanha" seria inventar.

    IDIOMA != PAIS          PAGINA_GLOBAL != PAGINA_LOCAL
    PAIS_ALCANCADO != PAIS_ALVO

AS TRES PROVAS QUE ESTE ARQUIVO PRODUZ
---------------------------------------
1. PAGE_ID de verdade. Abrir `?id=<library_id>` faz a propria Meta reescrever o
   endereco com `view_all_page_id=<numero>`. O numero nao e adivinhado do nome
   nem deduzido da foto de perfil: e o que a fonte poe na barra do navegador.
   Prova: `PAGE_ID_FROM_AD_DETAIL_URL`.

2. As paginas IRMAS. A visao por pagina traz o painel "Similar regional ads",
   onde a propria Meta lista as outras paginas da mesma marca COM O ROTULO DE
   PAIS ("Syngenta / Agricultural Service / Italy"). Clicar em "View ads"
   navega e revela o `view_all_page_id` daquela irma. Foi assim que
   `Syngenta Italy = 2007689772789481` apareceu, com ~530 resultados na Italia.
   Prova: `PAGE_ID_FROM_SIBLING_PANEL_CLICK`, e o rotulo de pais e da Meta.

3. O ESCOPO da pagina, com estado explicito:

       LOCAL_COUNTRY_PAGE           a Meta rotulou a pagina com UM pais
       MULTI_COUNTRY_PAGE           rotulo do tipo "X and other locations"
       GLOBAL_OR_UNLABELED_PAGE     sem rotulo de pais no painel
       PAGE_SCOPE_NOT_KNOWN         nao chegamos a ver o painel

   Nome terminado em "Espana" NAO promove uma pagina a LOCAL_COUNTRY_PAGE. Nome
   e pista, rotulo da fonte e prova, e os dois nao entram na mesma coluna.

O QUE ESTE ARQUIVO NAO DECIDE
------------------------------
Nao decide que a lista de concorrentes esta completa. Uma marca sem pagina
encontrada vira `ADVERTISER_NOT_RESOLVED` — o que significa "nao achei por esta
rota", e nunca "nao anuncia". Ausencia de prova nao e prova de ausencia.

    NAO_RESOLVIDO != NAO_ANUNCIA

E nao mistura os dois acervos. ADAMA sai por `OWN_PUBLIC_META_ACTIVITY`, os
outros por `COMPETITOR_PAID_META_ACTIVITY`, em arquivos separados, porque
comparar a si mesmo com o concorrente exige saber qual linha e qual.
"""
import datetime
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import meta_navegador as nav  # noqa: E402

PASTA = os.path.join(ROOT, 'data', 'samples', 'META-EAME')
DEST_COMP = os.path.join(PASTA, 'META-ADVERTISERS-EAME-V1.json')
DEST_ADAMA = os.path.join(PASTA, 'META-OWN-ADVERTISERS-ADAMA-V1.json')
CHECKPOINT = os.path.join(PASTA, 'META-ADVERTISERS-CHECKPOINT.json')

PAISES = ['ES', 'IT', 'FR']
# O rotulo que a Meta escreve no painel, e o codigo de pais que ele significa.
# So estes tres importam no piloto; os demais sao registrados como rotulo cru.
ROTULO_PAIS = {'Spain': 'ES', 'Italy': 'IT', 'France': 'FR'}

# A CONSULTA NAO E O NOME DA EMPRESA
# -----------------------------------
# Medido em 30/08/2026: `q=Bayer&country=ES` declara ~27.000 resultados e o topo
# e farmacia — Aspirin, CVS Pharmacy, Supradyn. A Bayer e um conglomerado, e
# procurar pelo nome do grupo devolve o grupo inteiro, nao o agro.
#
#     NOME_DA_EMPRESA != CONSULTA_DE_ANUNCIANTE
#
# Por isso cada empresa carrega uma LISTA de consultas, agro primeiro, com as
# formas locais que a marca usa em cada mercado. A ordem importa: a primeira
# consulta que trouxer identidade com o nome da empresa vira semente.
CONSULTAS = {
    'Bayer': ['Bayer Crop Science', 'Bayer Agro', 'Bayer Agricoltura',
              'Bayer Agri', 'Bayer'],
    'Syngenta': ['Syngenta'],
    'BASF': ['BASF Agro', 'BASF Agricultural Solutions', 'BASF Agricultura',
             'BASF'],
    'Corteva': ['Corteva Agriscience', 'Corteva'],
    'FMC': ['FMC Agricultural Solutions', 'FMC Agro', 'FMC'],
    'UPL': ['UPL Iberia', 'UPL Italia', 'UPL'],
    'Nufarm': ['Nufarm'],
    'Albaugh': ['Albaugh'],
    'Certis Belchim': ['Certis Belchim'],
    'Seipasa': ['Seipasa'],
    'ADAMA': ['ADAMA'],
}
CONCORRENTES = ['Bayer', 'Syngenta', 'BASF', 'Corteva', 'FMC', 'UPL',
                'Nufarm', 'Albaugh', 'Certis Belchim', 'Seipasa']
PROPRIA = ['ADAMA']

# Sinal agro NO NOME DA PAGINA. E pista, e o estado diz que e pista.
AGRO_TOKENS = ('crop', 'agro', 'agri', 'agricult', 'agricol', 'seed', 'semilla',
               'sementi', 'campo', 'farm', 'phyto', 'fito')
AGRO_PROVED = 'AGRO_NAME_SIGNAL_PRESENT'
AGRO_PARTIAL = 'AGRO_RELEVANCE_PARTIAL_BARE_BRAND'
AGRO_NAO = 'AGRO_RELEVANCE_NOT_PROVED'

PANEL_LIDO = 'SIBLING_PANEL_READ'
PANEL_AUSENTE = 'SIBLING_PANEL_NOT_AVAILABLE'


def relevancia_agro(page_name, empresa):
    n = (page_name or '').lower()
    if any(t in n for t in AGRO_TOKENS):
        return AGRO_PROVED
    if n.strip() == empresa.lower():
        return AGRO_PARTIAL
    return AGRO_NAO

LOCAL_COUNTRY_PAGE = 'LOCAL_COUNTRY_PAGE'
MULTI_COUNTRY_PAGE = 'MULTI_COUNTRY_PAGE'
GLOBAL_OR_UNLABELED_PAGE = 'GLOBAL_OR_UNLABELED_PAGE'
PAGE_SCOPE_NOT_KNOWN = 'PAGE_SCOPE_NOT_KNOWN'

ADVERTISER_RESOLVED = 'ADVERTISER_RESOLVED'
ADVERTISER_NOT_RESOLVED = 'ADVERTISER_NOT_RESOLVED'

PROVA_DETALHE = 'PAGE_ID_FROM_AD_DETAIL_URL'
PROVA_IRMA = 'PAGE_ID_FROM_SIBLING_PANEL_CLICK'


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def hoje():
    return datetime.date.today().isoformat()


# ── busca semente ────────────────────────────────────────────────────────────
def buscar(empresa, pais, espera=15):
    url = nav.url_biblioteca(active_status='all', ad_type='all', country=pais,
                             q=empresa, media_type='all')
    alvo = nav.abrir(url, espera=espera)
    try:
        cab = nav.cabecalho(alvo)
        cart = nav.cartoes(alvo)
    finally:
        nav.fechar(alvo)
    return url, cab, cart.get('cartoes', [])


def _nome_anunciante(texto):
    """O nome fica na linha imediatamente anterior a 'Sponsored'."""
    linhas = [l.strip() for l in (texto or '').split('\n')]
    for i, l in enumerate(linhas):
        if l == 'Sponsored' and i > 0:
            for j in range(i - 1, -1, -1):
                if linhas[j] and linhas[j] != '​':
                    return linhas[j]
    return None


def identidades_da_busca(cartoes):
    """Agrupa os cartoes por (nome exibido, link da pagina)."""
    grupos = {}
    for c in cartoes:
        nome = _nome_anunciante(c.get('texto'))
        link = next((h for h in c.get('links', [])
                     if re.search(r'facebook\.com/[^/?]+/?$', h)
                     and '/ads/library' not in h), None)
        chave = (nome, link)
        g = grupos.setdefault(chave, {'page_name': nome, 'page_url': link,
                                      'ads_observed': 0, 'library_ids': []})
        g['ads_observed'] += 1
        if len(g['library_ids']) < 3:
            g['library_ids'].append(c['library_id'])
    return [g for g in grupos.values() if g['page_name']]


# ── PAGE_ID pelo detalhe do anuncio ──────────────────────────────────────────
def page_id_por_anuncio(library_id, espera=12):
    url = nav.url_biblioteca(id=library_id)
    alvo = nav.abrir(url, espera=espera)
    try:
        cab = nav.cabecalho(alvo)
    finally:
        nav.fechar(alvo)
    final = cab.get('url') or ''
    m = re.search(r'view_all_page_id=(\d+)', final)
    return (m.group(1) if m else None), final


# ── painel de paginas irmas ──────────────────────────────────────────────────
_PAINEL = r'''(()=>{
 const bs=[...document.querySelectorAll('div[role="button"],a')]
   .filter(e=>/^View ads$/i.test((e.innerText||'').trim()));
 const itens=bs.map((b,i)=>{let p=b;for(let k=0;k<5;k++){if(p.parentElement)p=p.parentElement}
   return {indice:i, bloco:(p.innerText||'').split('\n').map(s=>s.trim()).filter(s=>s&&s!=='View ads').slice(0,3)};
 });
 return JSON.stringify({total:itens.length, itens:itens});
})()'''

_CLIQUE = '''(()=>{const bs=[...document.querySelectorAll('div[role="button"],a')]
 .filter(e=>/^View ads$/i.test((e.innerText||'').trim()));
 if(bs.length<=%d) return "FORA_DE_ALCANCE"; bs[%d].click(); return "CLICADO"})()'''


def url_pagina(page_id, pais):
    return nav.url_biblioteca(active_status='all', ad_type='all', country=pais,
                             view_all_page_id=page_id, search_type='page',
                             media_type='all')


def irmas_por_pais(page_id, pais_base, paises_alvo=PAISES, espera=15):
    """Le o painel e resolve o PAGE_ID das irmas rotuladas com os paises do piloto."""
    alvo = nav.abrir(url_pagina(page_id, pais_base), espera=espera)
    achados = []
    try:
        painel = nav.js_json(alvo, _PAINEL, timeout=90)
        itens = painel.get('itens', [])
        # bloco = [nome, categoria, rotulo_de_pais?]
        querer = []
        for it in itens:
            bloco = it['bloco']
            rotulo = bloco[2] if len(bloco) >= 3 else None
            achados.append({'page_name': bloco[0] if bloco else None,
                            'category': bloco[1] if len(bloco) > 1 else None,
                            'country_label': rotulo,
                            'page_id': None,
                            'identity_proof': None})
            if rotulo in ROTULO_PAIS and ROTULO_PAIS[rotulo] in paises_alvo:
                querer.append((it['indice'], len(achados) - 1))
        for indice, pos in querer:
            r = nav.js(alvo, _CLIQUE % (indice, indice), timeout=30)
            if 'CLICADO' not in str(r):
                continue
            time.sleep(9)
            cab = nav.cabecalho(alvo)
            m = re.search(r'view_all_page_id=(\d+)', cab.get('url') or '')
            if m:
                achados[pos]['page_id'] = m.group(1)
                achados[pos]['identity_proof'] = PROVA_IRMA
                achados[pos]['evidence_url'] = cab.get('url')
                achados[pos]['results_declared'] = cab.get('resultados_declarados')
            # voltar ao painel da pagina base para o proximo clique
            nav.js(alvo, 'location.href=%s; "ok"' % json.dumps(url_pagina(page_id, pais_base)),
                   timeout=30)
            time.sleep(espera)
    finally:
        nav.fechar(alvo)
    return achados


def escopo(rotulo):
    if rotulo in ROTULO_PAIS:
        return LOCAL_COUNTRY_PAGE
    if rotulo and 'other locations' in rotulo:
        return MULTI_COUNTRY_PAGE
    if rotulo:
        return LOCAL_COUNTRY_PAGE
    return GLOBAL_OR_UNLABELED_PAGE


# ── resolucao de uma empresa ─────────────────────────────────────────────────
def _token_empresa(empresa):
    return empresa.lower().split()[0]


def resolver(empresa, paises=PAISES, max_paginas=5):
    """Varre as consultas agro-primeiro e junta as identidades cujo NOME carrega
    o token da empresa. Guardar tudo o que a busca mostrou (inclusive o que foi
    descartado) e o que permite auditar depois por que uma pagina nao entrou."""
    tentativas = []
    candidatos = {}
    token = _token_empresa(empresa)
    for consulta in CONSULTAS.get(empresa, [empresa]):
        for pais in paises:
            url, cab, cartoes = buscar(consulta, pais)
            ids = identidades_da_busca(cartoes)
            do_token = [i for i in ids if token in (i['page_name'] or '').lower()]
            tentativas.append({
                'query': consulta, 'country_searched': pais, 'search_url': url,
                'results_declared': cab.get('resultados_declarados'),
                'cards_read': len(cartoes),
                'identities_seen': [i['page_name'] for i in ids][:10],
                'identities_kept': [i['page_name'] for i in do_token],
                'nota_descarte': 'identidade sem o token da empresa no nome nao '
                                 'entra; ver identities_seen para auditar',
            })
            for i in do_token:
                c = candidatos.setdefault(i['page_name'], dict(i))
                c['ads_observed'] = c.get('ads_observed', 0) + i['ads_observed']
                c.setdefault('countries_seen', [])
                if pais not in c['countries_seen']:
                    c['countries_seen'].append(pais)
                c.setdefault('queries', [])
                if consulta not in c['queries']:
                    c['queries'].append(consulta)
        if len(candidatos) >= 3:
            break

    if not candidatos:
        return {'company': empresa, 'estado': ADVERTISER_NOT_RESOLVED,
                'attempts': tentativas, 'pages': [],
                'nota': 'Nao encontrado por esta rota. Isto NAO significa que a '
                        'empresa nao anuncia.'}

    ordem = sorted(candidatos.values(),
                   key=lambda c: (relevancia_agro(c['page_name'], empresa) != AGRO_PROVED,
                                  -c['ads_observed']))
    paginas = []
    for c in ordem[:max_paginas]:
        pid, final = page_id_por_anuncio(c['library_ids'][0])
        paginas.append({
            'company': empresa,
            'page_name': c['page_name'],
            'page_id': pid,
            'page_url': c['page_url'],
            'category': None,
            'country_label_by_meta': None,
            'country_code': None,
            'page_scope': PAGE_SCOPE_NOT_KNOWN,
            'agro_relevance': relevancia_agro(c['page_name'], empresa),
            'identity_proof': PROVA_DETALHE if pid else None,
            'evidence_url': final,
            'found_by_queries': c.get('queries'),
            'found_in_country_searches': c.get('countries_seen'),
            'ads_seen_in_search': c['ads_observed'],
            'first_observed': hoje(),
            'last_observed': hoje(),
        })

    # painel de irmas: tenta na primeira pagina resolvida. Nem toda pagina tem —
    # a da Bayer global nao tinha nenhum botao "View ads" em 30/08/2026.
    estado_painel = PANEL_AUSENTE
    base = next((p for p in paginas if p['page_id']), None)
    if base:
        pais_base = (base.get('found_in_country_searches') or PAISES)[0]
        irmas = irmas_por_pais(base['page_id'], pais_base)
        if irmas:
            estado_painel = PANEL_LIDO
        vistos = {(p['page_name'], p['page_id']) for p in paginas}
        for pag in irmas:
            rotulo = pag.get('country_label')
            item = {
                'company': empresa,
                'page_name': pag.get('page_name'),
                'page_id': pag.get('page_id'),
                'page_url': None,
                'category': pag.get('category'),
                'country_label_by_meta': rotulo,
                'country_code': ROTULO_PAIS.get(rotulo),
                'page_scope': escopo(rotulo),
                'agro_relevance': relevancia_agro(pag.get('page_name'), empresa),
                'identity_proof': pag.get('identity_proof'),
                'evidence_url': pag.get('evidence_url'),
                'results_declared_in_country': pag.get('results_declared'),
                'first_observed': hoje(),
                'last_observed': hoje(),
            }
            if (item['page_name'], item['page_id']) in vistos:
                continue
            vistos.add((item['page_name'], item['page_id']))
            paginas.append(item)

    return {'company': empresa, 'estado': ADVERTISER_RESOLVED,
            'sibling_panel': estado_painel,
            'attempts': tentativas, 'pages': paginas}


def _salvar(caminho, obj):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def rodar(empresas, dono, destino):
    checkpoint = {}
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT, encoding='utf-8') as f:
            checkpoint = json.load(f)
    resultados = []
    for e in empresas:
        chave = dono + '::' + e
        if chave in checkpoint:
            resultados.append(checkpoint[chave])
            print('  (checkpoint) %s' % e)
            continue
        print('  resolvendo %s ...' % e, flush=True)
        try:
            r = resolver(e)
        except Exception as exc:
            r = {'company': e, 'estado': ADVERTISER_NOT_RESOLVED,
                 'erro': str(exc)[:300], 'pages': [], 'attempts': []}
        checkpoint[chave] = r
        _salvar(CHECKPOINT, checkpoint)
        resultados.append(r)
        print('     -> %s, %d pagina(s)' % (r['estado'], len(r.get('pages', []))))
    saida = {
        'dataset_owner': 'META_COMPETITOR_EAME',
        'dataset': dono,
        'as_of_date': agora(),
        'countries': PAISES,
        'meta_route': 'META_ADS_LIBRARY_UI_CHROME_COM_JANELA',
        'advertisers_attempted': len(empresas),
        'advertisers_resolved': sum(1 for r in resultados
                                    if r['estado'] == ADVERTISER_RESOLVED),
        'companies': resultados,
        'limitacoes': [
            'ADVERTISER_NOT_RESOLVED significa "nao achei por esta rota", nunca '
            '"nao anuncia".',
            'O rotulo de pais e da Meta, no painel de paginas irmas. Pagina sem '
            'rotulo fica GLOBAL_OR_UNLABELED_PAGE — nao vira local pelo nome.',
            'A pagina semente sai com PAGE_SCOPE_NOT_KNOWN quando nao aparece '
            'rotulada no proprio painel.',
        ],
    }
    _salvar(destino, saida)
    return saida


def main():
    quais = sys.argv[1] if len(sys.argv) > 1 else 'todos'
    if quais in ('todos', 'concorrentes'):
        print('CONCORRENTES (COMPETITOR_PAID_META_ACTIVITY)')
        r = rodar(CONCORRENTES, 'COMPETITOR_PAID_META_ACTIVITY', DEST_COMP)
        print('  %d/%d resolvidos -> %s' % (r['advertisers_resolved'],
                                            r['advertisers_attempted'],
                                            os.path.relpath(DEST_COMP, ROOT)))
    if quais in ('todos', 'adama'):
        print('ADAMA (OWN_PUBLIC_META_ACTIVITY)')
        r = rodar(PROPRIA, 'OWN_PUBLIC_META_ACTIVITY', DEST_ADAMA)
        print('  %d/%d resolvidos -> %s' % (r['advertisers_resolved'],
                                            r['advertisers_attempted'],
                                            os.path.relpath(DEST_ADAMA, ROOT)))


if __name__ == '__main__':
    main()
