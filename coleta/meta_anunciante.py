#!/usr/bin/env python3
"""
QUEM É O ANUNCIANTE — resolver a PÁGINA (PAGE_ID), não a palavra «Syngenta».

    python3 coleta/meta_anunciante.py Sipcam Gowan Ascenza "Certis Belchim"

AÇÃO de DESCOBERTA da linha da Meta. Trazido do ramo `claude/eame-meta-competitor`
(a2fad2d0, 31/08/2026), `scripts/meta_anunciante.py`, com três mudanças na vinda:

  · fala com o Chrome por `ferramentas/cdp.py` + `ferramentas/meta_biblioteca.py`;
  · a guarda de identidade (`regras/meta_identidade.py`) corre AQUI, na hora em
    que a página é achada — o Instytut Adama Mickiewicza não chega a proposta;
  · escreve uma PROPOSTA em `data/colheita/meta/PROPOSTAS/`, e NUNCA a lista da
    linha. Entrar em `PAGINAS-META-IT-V1.json` é gesto de gente, com a prova ao
    lado. Fonte nasce; não aparece pronta.

AS DUAS PROVAS DE PAGE_ID
-------------------------
1. `PAGE_ID_FROM_AD_DETAIL_URL`: abrir `?id=<library_id>` faz a própria Meta
   reescrever o endereço com `view_all_page_id=<número>`.
2. `PAGE_ID_FROM_SIBLING_PANEL_CLICK`: o painel «Similar regional ads» lista as
   irmãs COM rótulo de país («Syngenta / Agricultural Service / Italy»); o
   clique em «View ads» revela o id.

A CONSULTA NÃO É O NOME DA EMPRESA
-----------------------------------
`q=Bayer&country=ES` declarou ~27.000 resultados e o topo era farmácia. Cada
empresa carrega uma LISTA de consultas, agro primeiro.

    NOME_DA_EMPRESA != CONSULTA_DE_ANUNCIANTE
    NAO_RESOLVIDO != NAO_ANUNCIA          FERRAMENTA_CAIU != NAO_ENCONTRADO
"""
import datetime
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import meta_biblioteca as bib  # noqa: E402
import meta_identidade as ident  # noqa: E402

PROPOSTAS = os.path.join(RAIZ, 'data', 'colheita', 'meta', 'PROPOSTAS')

CONSULTAS = {
    'Bayer': ['Bayer Crop Science', 'Bayer Agricoltura', 'Bayer Agro'],
    'Syngenta': ['Syngenta Italia', 'Syngenta'],
    'BASF': ['BASF Agricoltura', 'BASF Agricultural Solutions', 'BASF Agro'],
    'Corteva': ['Corteva Agriscience Italia', 'Corteva Agriscience'],
    'FMC': ['FMC Italia', 'FMC Agricultural Solutions'],
    'UPL': ['UPL Italia', 'UPL'],
    'Nufarm': ['Nufarm Italia', 'Nufarm'],
    'Sipcam': ['Sipcam Italia', 'Sipcam Oxon', 'Sipcam'],
    'Gowan': ['Gowan Italia', 'Gowan'],
    'Certis Belchim': ['Certis Belchim Italia', 'Certis Belchim'],
    'Ascenza': ['Ascenza Italia', 'Ascenza'],
    'ADAMA': ['ADAMA Italia', 'ADAMA'],
}

ADVERTISER_RESOLVED = 'ADVERTISER_RESOLVED'
ADVERTISER_NOT_RESOLVED = 'ADVERTISER_NOT_RESOLVED'
COLLECTION_FAILED = 'COLLECTION_FAILED_TOOL'


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def nome_anunciante(texto):
    """O nome fica na linha imediatamente anterior a «Sponsored»."""
    linhas = [ln.strip() for ln in (texto or '').split('\n')]
    for i, ln in enumerate(linhas):
        if ln == 'Sponsored' and i > 0:
            for j in range(i - 1, -1, -1):
                if linhas[j] and linhas[j] != '​':
                    return linhas[j]
    return None


def identidades_da_busca(cartoes):
    """Agrupa os cartões por (nome exibido, link da página)."""
    grupos = {}
    for c in cartoes or []:
        nome = nome_anunciante(c.get('texto'))
        link = next((h for h in c.get('links', [])
                     if re.search(r'facebook\.com/[^/?]+/?$', h)
                     and '/ads/library' not in h), None)
        g = grupos.setdefault((nome, link), {'page_name': nome, 'page_url': link,
                                             'ads_observed': 0, 'library_ids': []})
        g['ads_observed'] += 1
        if len(g['library_ids']) < 3:
            g['library_ids'].append(c['library_id'])
    return [g for g in grupos.values() if g['page_name']]


def page_id_do_endereco(url):
    m = re.search(r'view_all_page_id=(\d+)', url or '')
    return m.group(1) if m else None


class Porta:
    """A aba da Biblioteca. Injetável: o teste passa uma falsa."""

    def __init__(self, porta=bib.PORTA):
        import cdp  # noqa: E402 — ferramentas/cdp.py
        self.cdp, self.porta = cdp, porta

    def ler(self, url, espera=15, com_cartoes=True):
        aba, _ = self.cdp.abrir(url, porta=self.porta, espera=espera, timeout=120)
        try:
            cab = bib._json(aba.js(bib.JS_CABECALHO))
            cart = bib._json(aba.js(bib.JS_CARTOES, timeout_ms=120000)) if com_cartoes else {}
        finally:
            aba.fechar()
        return cab, cart.get('cartoes', [])


def resolver(empresa, porta, pais='IT', max_paginas=5):
    """Consultas agro primeiro; guarda tudo o que a busca mostrou (auditável)."""
    tentativas, candidatos = [], {}
    for consulta in CONSULTAS.get(empresa, [empresa]):
        url = bib.url_biblioteca(active_status='all', ad_type='all', country=pais,
                                 q=consulta, media_type='all')
        cab, cartoes = porta.ler(url)
        if cab.get('logado') != bib.NAO_LOGADO:
            raise RuntimeError('LOGIN_DETECTED_STOP: a pagina nao mostrou "Log in" (D88)')
        ids = identidades_da_busca(cartoes)
        aceites = [i for i in ids
                   if ident.guarda_identidade(i['page_name'], empresa)['state']
                   == ident.IDENTIDADE_ACEITA]
        tentativas.append({'query': consulta, 'country_searched': pais,
                           'search_url': url,
                           'results_declared': cab.get('resultados_declarados'),
                           'cards_read': len(cartoes),
                           'identities_seen': [i['page_name'] for i in ids][:10],
                           'identities_kept': [i['page_name'] for i in aceites]})
        for i in aceites:
            c = candidatos.setdefault(i['page_name'], dict(i, ads_observed=0))
            c['ads_observed'] += i['ads_observed']
        if candidatos:
            break
    if not candidatos:
        return {'company': empresa, 'estado': ADVERTISER_NOT_RESOLVED,
                'attempts': tentativas, 'pages': [],
                'nota': 'Nao encontrado por esta rota. NAO significa que nao anuncia.'}
    paginas = []
    for c in sorted(candidatos.values(), key=lambda c: -c['ads_observed'])[:max_paginas]:
        cab, _ = porta.ler(bib.url_biblioteca(id=c['library_ids'][0]), espera=12,
                           com_cartoes=False)
        pid = page_id_do_endereco(cab.get('url'))
        paginas.append({'company': empresa, 'page_name': c['page_name'],
                        'page_id': pid,
                        'identity_proof': ident.PROVA_DETALHE if pid else None,
                        'evidence_url': cab.get('url'),
                        'country_label_by_meta': None,
                        'ads_seen_in_search': c['ads_observed'],
                        'proposed_at': agora(), 'EM_LINHA': False,
                        'MOTIVO_FORA_DA_LINHA': 'PROPOSTA: falta revisao humana'})
    return {'company': empresa, 'estado': ADVERTISER_RESOLVED,
            'attempts': tentativas, 'pages': paginas}


def rodar(empresas, porta=None, pais='IT', destino=PROPOSTAS):
    porta = porta or Porta()
    saida = []
    for e in empresas:
        try:
            r = resolver(e, porta, pais=pais)
        except Exception as exc:                              # noqa: BLE001
            r = {'company': e, 'estado': COLLECTION_FAILED, 'pages': [],
                 'erro': '%s: %s' % (type(exc).__name__, str(exc)[:200]),
                 'failure_state': getattr(exc, 'estado', None) or 'NAO SEI',
                 'nota': 'falha da NOSSA ferramenta. Nada se conclui sobre a empresa.'}
        saida.append(r)
        print('  %-16s %s  %d pagina(s)' % (e, r['estado'], len(r['pages'])), flush=True)
        time.sleep(1)
    doc = {'DATASET': 'CONCORRENCIA-META-PROPOSTA-DE-PAGINAS', 'ROTA': bib.ROTA,
           'PAIS_DA_BUSCA': pais, 'GERADO_EM': agora(),
           'NOTA': 'PROPOSTA. Nenhuma pagina daqui entra na linha sem revisao humana.',
           'companies': saida}
    os.makedirs(destino, exist_ok=True)
    caminho = os.path.join(destino, 'PROPOSTA-%s.json'
                           % re.sub(r'[^0-9T]', '', doc['GERADO_EM'])[:15])
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    return doc, caminho


if __name__ == '__main__':
    nomes = sys.argv[1:] or ['Sipcam', 'Gowan', 'Ascenza', 'Certis Belchim']
    _, onde = rodar(nomes)
    print('proposta ->', os.path.relpath(onde, RAIZ))
