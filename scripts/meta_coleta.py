#!/usr/bin/env python3
"""
A COLETA — um anuncio por vez, e nenhum campo que a fonte nao tenha escrito.

Le a visao por PAGINA (`view_all_page_id`), pais a pais, rola ate a lista parar
de crescer e transforma cada cartao em um registro. A disciplina inteira cabe
numa frase: se o cartao nao escreveu, o campo sai `None` — nunca um valor
plausivel.

O CAMPO DE GASTO, E POR QUE ELE APARECE SO AS VEZES
----------------------------------------------------
Medido em 30/08/2026, num anuncio da pagina Bayer global:

    Categories · Estimated audience size: >1M
                 Amount spent (USD): $1K - $1.5K
                 Impressions: >1M

Isso NAO e um campo comercial. E o bloco extra que a Meta publica para anuncios
declarados de tema social, eleicao ou politica. O anuncio comercial de defensivo
ao lado nao traz nada disso — traz "EU transparency" e mais nada.

Entao o registro guarda o gasto QUANDO A FONTE O ESCREVE, marcando de onde veio
(`DECLARED_ISSUE_POLITICAL_AD_BLOCK`), e deixa `None` no resto. O que ele nunca
faz e estimar. A missao proibe, e com razao:

    AD_COUNT != SPEND        FAIXA_DE_GASTO_DE_ANUNCIO_POLITICO != INVESTIMENTO_AGRO

O PAIS DO PARAMETRO E "ALCANCADO", NAO "ALVO"
----------------------------------------------
A URL leva `country=ES` e a propria Meta acrescenta `is_targeted_country=false`.
Ou seja: a lista responde "anuncios que ALCANCARAM a Espanha", nao "anuncios
dirigidos a Espanha". Por isso o campo se chama `country_reached`, e existe
`target_location_state = NOT_PROVED` ao lado. A prova de que um anuncio mirava
a Franca esta no bloco de transparencia da UE, que exige outro clique, e ate la
o estado correto e "nao provado".

    PAIS_ALCANCADO != PAIS_ALVO
"""
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import meta_navegador as nav  # noqa: E402
import meta_leitura as leitura  # noqa: E402
import meta_relogio as relogio  # noqa: E402

PASTA = os.path.join(ROOT, 'data', 'samples', 'META-EAME')
ENTIDADES = os.path.join(PASTA, 'META-ADS-ENTITIES-EAME-V1.json')
EVENTOS = os.path.join(PASTA, 'META-ADS-EVENTS-EAME-V1.json')

PAISES = ['ES', 'IT', 'FR']
BLOCO_POLITICO = 'DECLARED_ISSUE_POLITICAL_AD_BLOCK'
NOT_PROVED = 'NOT_PROVED'
NOT_KNOWN = 'NOT_KNOWN'


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def hoje():
    return datetime.date.today().isoformat()


# ── texto do cartao -> registro ──────────────────────────────────────────────
_LIXO_FINAL = re.compile(
    r'\n(Business|Product/service|Agricultural Service|Company|Brand)\n.*$'
    r'|\n[\d.,]+ people like this\n.*$'
    r'|\nLike Page\s*$'
    r'|\n\d+:\d\d ?/ ?\d+:\d\d.*$', re.S)


def creative_text(texto):
    partes = (texto or '').split('\nSponsored\n', 1)
    if len(partes) < 2:
        return None
    corpo = partes[1]
    corpo = _LIXO_FINAL.sub('', corpo)
    corpo = corpo.replace('​', '').strip()
    return corpo or None


def nome_anunciante(texto):
    linhas = [l.strip() for l in (texto or '').split('\n')]
    for i, l in enumerate(linhas):
        if l == 'Sponsored' and i > 0:
            for j in range(i - 1, -1, -1):
                if linhas[j] and linhas[j] != '​':
                    return linhas[j]
    return None


_GASTO = re.compile(r'Amount spent \(([A-Z]{3})\):\s*\n?\s*([^\n]+)')
_IMPRESSOES = re.compile(r'Impressions:\s*\n?\s*([^\n]+)')
_AUDIENCIA = re.compile(r'Estimated audience size:\s*\n?\s*([^\n]+)')


def bloco_declarado(texto):
    """Gasto/impressoes so existem no bloco de anuncio de tema social/politico."""
    g = _GASTO.search(texto or '')
    i = _IMPRESSOES.search(texto or '')
    a = _AUDIENCIA.search(texto or '')
    if not (g or i or a):
        return {'spend': None, 'impressions': None, 'estimated_audience_size': None,
                'spend_source': None,
                'nota': 'a fonte nao publica gasto para este tipo de anuncio'}
    return {
        'spend': ({'currency': g.group(1), 'range': g.group(2).strip()} if g else None),
        'impressions': (i.group(1).strip() if i else None),
        'estimated_audience_size': (a.group(1).strip() if a else None),
        'spend_source': BLOCO_POLITICO,
        'nota': 'campo publicado porque o anuncio foi DECLARADO de tema social, '
                'eleicao ou politica. Nao e metrica de campanha comercial.',
    }


_MEDIA = {'VIDEO': lambda c: c.get('n_video', 0) > 0,
          'IMAGE': lambda c: c.get('n_img', 0) > 0}


def media_type(cartao):
    for nome, teste in _MEDIA.items():
        if teste(cartao):
            return nome
    return NOT_KNOWN


PLATAFORMAS = ('Facebook', 'Instagram', 'Audience Network', 'Messenger', 'Threads')


def plataformas(cartao):
    achadas = [p for p in PLATAFORMAS
               if any(p.lower() in (r or '').lower() for r in cartao.get('rotulos', []))]
    return achadas or [NOT_KNOWN]


def registro(cartao, pagina, pais, completude, momento):
    texto = cartao.get('texto') or ''
    inicio, fim = nav.datas_do_texto(texto)
    criativo = creative_text(texto)
    r = {
        'meta_ad_library_id': cartao['library_id'],
        'ad_snapshot_url': nav.url_biblioteca(id=cartao['library_id']),
        'company': pagina.get('company'),
        'page_name_in_card': nome_anunciante(texto),
        'page_name_resolved': pagina.get('page_name'),
        'page_id': pagina.get('page_id'),
        'page_scope': pagina.get('page_scope'),
        'country_reached': pais,
        'country_param_semantics': 'AD_REACHED_COUNTRY (is_targeted_country=false)',
        'target_locations': None,
        'target_location_state': NOT_PROVED,
        'target_ages': None,
        'target_gender': None,
        'beneficiary': None,
        'payer': None,
        'eu_transparency_block_present': 'EU transparency' in texto,
        'eu_transparency_detail_state': 'NOT_COLLECTED_THIS_ROUND',
        'start_date': inicio,
        'end_date': fim,
        'active_status': nav.status_do_texto(texto),
        'publisher_platforms': plataformas(cartao),
        'media_type': media_type(cartao),
        'creative_text': criativo,
        'creative_text_hash': (hashlib.sha256(criativo.encode('utf-8')).hexdigest()[:16]
                               if criativo else None),
        'headline': None,
        'description': None,
        'as_of_date': momento,
        'collection_completeness': completude,
        'source_url': nav.url_biblioteca(active_status='all', ad_type='all',
                                         country=pais,
                                         view_all_page_id=pagina.get('page_id'),
                                         search_type='page', media_type='all'),
    }
    r.update(bloco_declarado(texto))
    r['reading'] = leitura.ler(r)
    return r


# ── coleta de uma pagina num pais ────────────────────────────────────────────
# POR QUE NENHUMA PAGINA E FILTRADA PELO NOME
# --------------------------------------------
# A tentacao era coletar so as paginas com cara de agro. A lista resolvida em
# 30/08/2026 mostra que o nome erra dos DOIS lados:
#
#     "UPL Iberia", "Certis Belchim Espana", "FMC Italia"   sem token agro,
#                                                            e sao as certas
#     "Instytut Adama Mickiewicza"                           casa com "adama",
#                                                            e e um instituto
#                                                            cultural polones
#     "FMC Moto Srl"                                         motocicletas
#
# Entao coleta-se tudo, e quem decide relevancia sao os ANUNCIOS: o leitor extrai
# cultura, problema e categoria do texto, e pagina sem sinal nenhum aparece com
# zero. Nada e descartado em silencio — a missao pede exatamente isso.
def coletar_pagina(pagina, pais, momento, max_rolagens=12):
    pid = pagina.get('page_id')
    if not pid:
        return [], {'page_id': None, 'estado': 'PAGE_ID_AUSENTE'}
    url = nav.url_biblioteca(active_status='all', ad_type='all', country=pais,
                             view_all_page_id=pid, search_type='page',
                             media_type='all')
    alvo = nav.abrir(url, espera=15)
    try:
        cab = nav.cabecalho(alvo)
        rol = nav.rolar_ate_parar(alvo, max_rolagens=max_rolagens)
        cart = nav.cartoes(alvo)
    finally:
        nav.fechar(alvo)
    completude = rol['completude']
    regs = [registro(c, pagina, pais, completude, momento)
            for c in cart.get('cartoes', [])]
    diag = {'page_id': pid, 'page_name': pagina.get('page_name'), 'country': pais,
            'url': url, 'results_declared': cab.get('resultados_declarados'),
            'cards_read': len(regs), 'scrolls': rol['rolagens'],
            'completeness': completude}
    return regs, diag


def paginas_de(arquivo, so_com_id=True):
    with open(arquivo, encoding='utf-8') as f:
        d = json.load(f)
    saida = []
    for c in d.get('companies', []):
        for p in c.get('pages', []):
            if so_com_id and not p.get('page_id'):
                continue
            saida.append(p)
    return saida


def _carregar(caminho, padrao):
    if os.path.exists(caminho):
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)
    return padrao


def _salvar(caminho, obj):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def rodar(arquivo_anunciantes, paises=PAISES, limite_paginas=None,
          destino_entidades=ENTIDADES, destino_eventos=EVENTOS):
    momento = agora()
    paginas = paginas_de(arquivo_anunciantes)
    if limite_paginas:
        paginas = paginas[:limite_paginas]
    snapshot, diagnostico = [], []
    for p in paginas:
        alvos = [p['country_code']] if p.get('country_code') else paises
        for pais in alvos:
            try:
                regs, diag = coletar_pagina(p, pais, momento)
            except Exception as e:
                regs, diag = [], {'page_id': p.get('page_id'), 'country': pais,
                                  'erro': str(e)[:200]}
            snapshot.extend(regs)
            diagnostico.append(diag)
            print('  %-34s %s  %3d cartoes  %s' % (
                (p.get('page_name') or '')[:34], pais, len(regs),
                diag.get('completeness', diag.get('erro', ''))), flush=True)

    acervo = _carregar(destino_entidades, {})
    entidades_antes = acervo.get('entities', {})
    data_anterior = acervo.get('as_of_date')
    entidades, eventos = relogio.fundir(entidades_antes, snapshot)
    por_inicio = relogio.novos_por_data_de_inicio(eventos, entidades, data_anterior)

    _salvar(destino_entidades, {
        'dataset_owner': 'META_COMPETITOR_EAME',
        'as_of_date': momento,
        'previous_as_of_date': data_anterior,
        'meta_route': 'META_ADS_LIBRARY_UI_CHROME_COM_JANELA',
        'countries': paises,
        'collection_diagnostics': diagnostico,
        'summary': relogio.resumo(entidades, eventos, bool(data_anterior)),
        'entities': entidades,
    })
    _salvar(destino_eventos, {
        'dataset_owner': 'META_COMPETITOR_EAME',
        'as_of_date': momento,
        'previous_as_of_date': data_anterior,
        'baseline': not bool(data_anterior),
        'events': eventos,
        'new_by_start_date': por_inicio,
        'nota': ('sem coleta anterior, todo evento comparativo e BASELINE_ONLY. '
                 'Isso NAO significa que nada mudou.'),
    })
    return {'snapshot': len(snapshot), 'entities': len(entidades),
            'events': len(eventos), 'diagnostics': diagnostico}


def main():
    alvo = sys.argv[1] if len(sys.argv) > 1 else 'concorrentes'
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else None
    if alvo == 'adama':
        arq = os.path.join(PASTA, 'META-OWN-ADVERTISERS-ADAMA-V1.json')
        ent = os.path.join(PASTA, 'META-OWN-ADS-ENTITIES-ADAMA-V1.json')
        evt = os.path.join(PASTA, 'META-OWN-ADS-EVENTS-ADAMA-V1.json')
    else:
        arq = os.path.join(PASTA, 'META-ADVERTISERS-EAME-V1.json')
        ent, evt = ENTIDADES, EVENTOS
    r = rodar(arq, limite_paginas=limite, destino_entidades=ent, destino_eventos=evt)
    print(json.dumps({k: r[k] for k in ('snapshot', 'entities', 'events')},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
