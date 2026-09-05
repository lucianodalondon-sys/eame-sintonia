#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMADA MARKET PULSE — do resultado do leque de mercado para o pacote.

    python3 scripts/pacote_mercado.py .tmp/mkt.json

⚠️ O ACHADO QUE MANDA NESTA CAMADA
------------------------------------
As duas fontes italianas centrais de mercado — **ISMEA** e **ISTAT** — não respondem a
este ambiente. A ISMEA devolve, literalmente, `GEO_IP_BLOCK` para o IP de saída
179.172.231.127; a ISTAT dá tempo esgotado de TCP.

    É A MESMA LIÇÃO QUE O PORTAL SINTONIA BRASIL JÁ TINHA PAGO:
    «o 403 era VPN, não bloqueio de robô. Antes de qualquer tentativa,
     conferir de onde a conexão está saindo.»

Consequência honesta, e ela vai no artefato: o Market Pulse italiano **não é** uma
ferramenta impossível — é uma ferramenta que exige **rota de saída italiana ou europeia**.
Do Brasil, ela nasce com as duas melhores fontes fechadas.

    FONTE BLOQUEADA POR IP NÃO É FONTE INEXISTENTE. É PROBLEMA DE ROTA.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pacote_normalizar import grava, env, novo_id, DR, ROOT, local_json  # noqa: E402

REAL, DERIV = 'REAL_SOURCE', 'REAL_DERIVED'


def camada_mercado(caminho=None):
    caminho = caminho or (sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '.tmp', 'mkt.json'))
    if not os.path.exists(caminho):
        print('FALTA %s — rode o leque de mercado antes' % caminho); return 1
    r = json.load(open(caminho, encoding='utf-8'))

    # ── 1 · capacidade por fonte ──────────────────────────────────────────────
    caps, fontes = [], []
    for f in r['fontes']:
        L = f['lido']
        v = f.get('veredito') or {}
        fid = novo_id('IT-MKTSRC')
        fontes.append(OrderedDict([
            ('ID', fid), ('SOURCE', L.get('fonte')), ('URL', L.get('url_base')),
            ('REACHED', L.get('alcancada')),
            ('ACCESS_EVIDENCE', str(L.get('estado_evidencia'))[:1200]),
            ('CAPABILITIES_DECLARED', len(L.get('capacidades') or [])),
            ('ADVERSARIAL_REFUTED', v.get('refuted')),
            ('ADVERSARIAL_REASON', str(v.get('reason'))[:1600]),
            ('ADVERSARIAL_CORRECTIONS', (v.get('corrections') or [])[:12]),
            ('WHAT_IT_DOES_NOT_PROVE', L.get('o_que_esta_fonte_nao_prova') or []),
            ('PROVENANCE', REAL)]))
        for c in (L.get('capacidades') or []):
            caps.append(OrderedDict([
                ('ID', novo_id('IT-MKTCAP')), ('SOURCE_REF', fid),
                ('SOURCE', L.get('fonte', '').split('—')[0].strip()),
                ('METRIC', c.get('metrica')), ('AVAILABLE', c.get('disponivel')),
                ('CADENCE', c.get('cadencia')), ('GEOGRAPHY', c.get('geografia')),
                ('LATEST_PERIOD', c.get('ultimo_periodo')),
                ('CROPS', c.get('culturas_cobertas') or []),
                ('ACCESS_ROUTE', c.get('rota_de_acesso')),
                ('LIMITATION', c.get('limitacao')),
                ('PROVENANCE', REAL)]))

    grava('MARKET-PULSE', 'market-sources.json', OrderedDict(list(env(
        'MARKET_SOURCES', 'leque de mercado 2026-09-02', REAL,
        'Cada fonte foi mapeada por um agente e RELIDA por um refutador independente. '
        'ADVERSARIAL_REFUTED=true quase sempre significa UM CAMPO errado, nao a fonte '
        'inteira — a razao esta escrita ao lado.').items()) + [
        ('COUNT', len(fontes)),
        ('BY_REACHED', dict(Counter(x['REACHED'] for x in fontes))),
        ('CRITICAL_FINDING', {
            'WHAT': 'as duas fontes italianas centrais de mercado nao respondem a este ambiente',
            'ISMEA': 'HTTP 404 com corpo «Blocked» e a string literal GEO_IP_BLOCK; IP de '
                     'saida 179.172.231.127; WAF Barracuda. Lida so pelo Internet Archive.',
            'ISTAT': 'o mapeador reportou GREEN e o refutador nao conseguiu reproduzir: '
                     'timeout de TCP em esploradati.istat.it:443 por dois caminhos de rede, '
                     'em ~25 minutos. OS DOIS ESTADOS FICAM REGISTRADOS — nao escolho um.',
            'PRECEDENT': 'o Portal Sintonia Brasil ja tinha pago esta licao: «o 403 era VPN, '
                         'nao bloqueio de robo. Antes de qualquer tentativa, conferir de '
                         'onde a conexao esta saindo.»',
            'CONSEQUENCE': 'o Market Pulse italiano exige ROTA DE SAIDA italiana ou europeia. '
                           'Do Brasil ele nasce com as duas melhores fontes fechadas.',
            'LAW': 'FONTE BLOQUEADA POR IP NAO E FONTE INEXISTENTE. E problema de rota.'}),
        ('SOURCES', fontes)]))

    grava('MARKET-PULSE', 'market-capabilities.json', OrderedDict(list(env(
        'MARKET_CAPABILITIES', 'leque de mercado 2026-09-02', REAL,
        'o que CADA fonte publica, com cadencia, geografia e ultimo periodo. E a base da '
        'auditoria de viabilidade.').items()) + [
        ('COUNT', len(caps)),
        ('BY_AVAILABLE', dict(Counter(c['AVAILABLE'] for c in caps))),
        ('CAPABILITIES', caps)]))

    # ── 2 · preço observado, do que já está gravado ───────────────────────────
    precos = []
    for arq, rot in (('IT-MERCADO/EU-AGRIFOOD-cereal-prices-IT.json', 'CEREAL'),
                     ('IT-MERCADO/EU-AGRIFOOD-oliveOil-prices-IT.json', 'OLIVE_OIL'),
                     ('IT-MERCADO/EU-AGRIFOOD-wine-prices-IT.json', 'WINE')):
        d = local_json(arq)
        if not d:
            continue
        for u in d.get('LATEST_BY_PRODUCT_MARKET', []):
            fim = str(u.get('END') or '')
            ano = fim.split('/')[-1] if '/' in fim else ''
            parada = bool(ano) and int(ano) < 2026
            atual, ant, anoatras = u.get('PRICE_NUM'), u.get('PREV_PRICE_NUM'), \
                u.get('YEAR_AGO_PRICE_NUM')
            precos.append(OrderedDict([
                ('ID', novo_id('IT-MKT')), ('GROUP', rot),
                ('PRODUCT', u.get('PRODUCT')), ('MARKET', u.get('MARKET')),
                ('PRICE_RAW', u.get('PRICE_RAW')), ('PRICE_NUM', atual),
                ('UNIT', u.get('UNIT')), ('STAGE', u.get('STAGE')),
                ('REFERENCE_PERIOD', '%s..%s' % (u.get('BEGIN'), u.get('END'))),
                ('PUBLICATION_DATE', u.get('REFERENCE_PERIOD')),
                ('GEOGRAPHY', 'IT — praca nomeada'),
                ('PREV_PRICE_NUM', ant),
                ('CHANGE_VS_PREV_PCT', round((atual - ant) / ant * 100, 1)
                 if (atual and ant) else None),
                ('YEAR_AGO_PRICE_NUM', anoatras),
                ('CHANGE_VS_YEAR_AGO_PCT', round((atual - anoatras) / anoatras * 100, 1)
                 if (atual and anoatras) else None),
                ('SERIES_STATE', 'PARADA_EM_%s' % ano if parada else 'CORRENTE'),
                ('SERIES_WARNING', 'esta praca parou de cotar; a ultima cotacao NAO e preco '
                                   'atual' if parada else None),
                ('OBSERVATIONS_IN_SERIES', u.get('OBSERVATIONS_IN_SERIES')),
                ('SOURCE_ID', 'IT-SRC-AGRIFOOD'), ('PROVENANCE', REAL)]))
    grava('MARKET-PULSE', 'market-pulse.json', OrderedDict(list(env(
        'MARKET_PRICE_OBSERVATIONS', 'data/samples/IT-MERCADO/', REAL,
        'observacao de mercado por praca. NAO e preco pago por ninguem em particular, e '
        'pracas so se comparam depois de conferir STAGE e UNIT.').items()) + [
        ('COUNT', len(precos)),
        ('BY_SERIES_STATE', dict(Counter(p['SERIES_STATE'] for p in precos))),
        ('DEAD_SERIES_LAW', 'praca que parou de cotar mantem a ultima cotacao no indice. '
                            'Mostrar isso como preco atual e o erro mais caro de um painel '
                            'de mercado — por isso SERIES_STATE vem em toda linha.'),
        ('PRICES', precos)]))

    # ── 3 · resumo por cultura, texto ─────────────────────────────────────────
    d = os.path.join(DR, 'MARKET-PULSE')
    os.makedirs(d, exist_ok=True)
    resumos = []
    for x in r.get('resumos_por_cultura', []):
        nome = str(x['cultura']).replace('/', '-').replace(' ', '-').lower()
        arq = 'crop-summary-%s.md' % nome
        open(os.path.join(d, arq), 'w', encoding='utf-8').write(str(x['texto']))
        resumos.append({'CROP': x['cultura'], 'FILE': 'MARKET-PULSE/' + arq,
                        'CHARS': len(str(x['texto']))})
    json.dump(OrderedDict([
        ('LAYER', 'CROP_MARKET_SUMMARIES'), ('BUILT_AT', '2026-09-02'),
        ('LAW', 'a TEMPERATURA DE MERCADO e INTERPRETACAO DO SINTONIA, nunca fato '
                'observado, e nunca aparece sem o bloco «POR QUE» ao lado.'),
        ('FORBIDDEN', ['nota de 0 a 100', 'mercado quente', 'os clientes vao comprar',
                       'previsao de venda da ADAMA']),
        ('COUNT', len(resumos)), ('SUMMARIES', resumos)]),
        open(os.path.join(d, 'crop-market-summaries.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)
    print('  MARKET-PULSE/crop-market-summaries.json           %d culturas' % len(resumos))

    open(os.path.join(d, 'FEASIBILITY-AUDIT.md'), 'w', encoding='utf-8').write(
        str(r.get('viabilidade') or ''))
    print('  MARKET-PULSE/FEASIBILITY-AUDIT.md                 %d caracteres'
          % len(str(r.get('viabilidade') or '')))
    return 0


if __name__ == '__main__':
    sys.exit(camada_fenologia() if 'fenologia' in __file__ else camada_mercado())
