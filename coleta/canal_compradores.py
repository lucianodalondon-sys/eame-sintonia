#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OS PONTOS DO CANAL — onde o comprador esta, quando a fonte oficial nao diz quem ele e.

    py coleta/canal_compradores.py --coletar      puxa o OSM e geocodifica
    py coleta/canal_compradores.py --normalizar   escreve a tabela de pontos
    py coleta/canal_compradores.py --sondar       so mede as rotas gratis, sem puxar nada

POR QUE ESTE FICHEIRO EXISTE
----------------------------
A declaracao de venda (IT-T10-001) e publicada AGREGADA POR PROVINCIA: o nome de quem
vendeu e exatamente o campo que ela omite. O universo existe e tem tamanho conhecido —
531 titulares de autorizacao em 2022 — mas nao tem nome publico.

Enquanto o nome nao chega pela porta certa (accesso civico as 9 ULSS, ou extracao paga no
Registro Imprese), o OpenStreetMap da a UNICA coisa que da para ter de graca e hoje:
COORDENADA. E ja provou valer: localiza filiais do Consorzio Agrario di Treviso e Belluno
e do Nordest que nenhum dos dois publica.

    O OSM NAO E CENSO, E ESTE FICHEIRO NAO FINGE QUE E.
    A cobertura e medida contra os 531 e escrita no proprio artefato.

O QUE ESTE COLETOR NAO FAZ
--------------------------
Nao guarda pessoa fisica. As listas gratis que trazem nome de gente — beneficiarios da PAC
e operadores biologicos, em que «AGOSTINI CELESTINO» e uma pessoa, nao uma empresa — sao
registadas na SONDAGEM como rota conhecida e NAO sao baixadas para o repositorio. A regra
esta em docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md e a pendencia P-008 continua aberta.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import proveniencia as pv  # noqa: E402

SOURCE_ID = 'IT-T10-002'
PAIS = 'italy'
REGIAO = 'Veneto'
# Espelhos do Overpass, em ordem. Um espelho que devolve 504 nao e a fonte dizendo «nao ha»:
# e o espelho dizendo «agora nao». Tratar um pelo outro e como confundir porta fechada com
# casa vazia — a lei da casa chama isso de ROUTE_NOT_FOUND != SOURCE_BLOCKED.
OVERPASS_ESPELHOS = ('https://overpass.kumi.systems/api/interpreter',
                     'https://overpass.private.coffee/api/interpreter',
                     'https://overpass.osm.ch/api/interpreter',
                     'https://overpass-api.de/api/interpreter')
OVERPASS = OVERPASS_ESPELHOS[0]
NOMINATIM = 'https://nominatim.openstreetmap.org/reverse'
UA = 'SintoniaEAME-research/1.0 (github.com/lucianodalondon-sys/eame-sintonia)'
BBOX = (44.7, 10.6, 46.8, 13.2)          # Veneto e um pouco de folga; o filtro fino e por provincia
PROVINCIAS = {'Verona': 'VR', 'Vicenza': 'VI', 'Padova': 'PD', 'Treviso': 'TV',
              'Venezia': 'VE', 'Rovigo': 'RO', 'Belluno': 'BL',
              'Provincia di Verona': 'VR', 'Provincia di Vicenza': 'VI',
              'Provincia di Padova': 'PD', 'Provincia di Treviso': 'TV',
              'Città metropolitana di Venezia': 'VE', 'Provincia di Rovigo': 'RO',
              'Provincia di Belluno': 'BL'}
STORE = os.path.join(ROOT, 'data', 'collection-store', PAIS, SOURCE_ID)
LEDGER = os.path.join(ROOT, 'data', 'collection-ledger', PAIS)
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-VENETO-CANALE')

# O universo contra o qual a cobertura deste coletor tem de ser medida — sempre.
TITULARES_DECLARANTES_2022 = 531

CONSULTAS = [
    ('shop=agrarian', '[out:json][timeout:120];(nwr["shop"="agrarian"](%f,%f,%f,%f););out center tags;'),
    ('shop=garden_centre', '[out:json][timeout:120];(nwr["shop"="garden_centre"](%f,%f,%f,%f););out center tags;'),
    ('shop=farm', '[out:json][timeout:120];(nwr["shop"="farm"](%f,%f,%f,%f););out center tags;'),
    ('name~Consorzio Agrario', '[out:json][timeout:140];(nwr["name"~"Consorzio Agrario",i](%f,%f,%f,%f););out center tags;'),
]


def agora():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def egresso():
    """EGRESS_IP — por onde a requisicao saiu. O padrao da casa exige isto em toda corrida:
    sem ele, nao da para saber depois se a fonte respondeu diferente por causa da rota."""
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=15) as r:
            return r.read().decode().strip() or pv.NAO_SEI
    except Exception:                                            # noqa: BLE001
        return pv.NAO_SEI


def _pedir(url, dados=None, headers=None, timeout=180):
    req = urllib.request.Request(url, data=dados, headers=headers or {'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.status


def _overpass(consulta, tentativas=2):
    """Espelho por espelho, duas tentativas em cada. 504 mede o minuto, nao a fonte.

    O que sobrar de erro entra no ledger como FALHA nomeada, com o espelho que falhou —
    nunca como «zero pontos».
    """
    erros = []
    for espelho in OVERPASS_ESPELHOS:
        for i in range(tentativas):
            try:
                corpo, status = _pedir(espelho,
                                       urllib.parse.urlencode({'data': consulta}).encode(),
                                       {'User-Agent': UA,
                                        'Content-Type': 'application/x-www-form-urlencoded'})
                if espelho != OVERPASS_ESPELHOS[0]:
                    print('    (respondeu o espelho %s)' % espelho.split('/')[2])
                return corpo, status
            except Exception as e:                               # noqa: BLE001
                erros.append('%s: %s' % (espelho.split('/')[2], str(e)[:60]))
                time.sleep(3 * (i + 1))
    raise RuntimeError(' | '.join(erros[-4:]))


def _geocodificacao_ja_feita():
    """Reaproveita o que ja foi geocodificado: a politica do Nominatim e 1 pedido por segundo,
    e refazer 300 pontos so para repetir a mesma resposta e desperdicio de fonte alheia."""
    caminho = os.path.join(SAIDA, 'DIM-PONTO-DE-CANAL.json')
    if not os.path.exists(caminho):
        return {}
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    return {(p['OSM_TYPE'], p['OSM_ID']): p for p in d.get('PONTOS', [])}


def coletar():
    """Puxa as quatro consultas, guarda o BRUTO de cada uma antes de olhar o conteudo."""
    inicio = agora()
    ip = egresso()
    run_id = 'IT-T10-002-%s' % datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H%M%S')
    brutos, elementos, falhas = [], {}, []
    for nome, gabarito in CONSULTAS:
        consulta = gabarito % BBOX
        try:
            corpo, status = _overpass(consulta)
        except Exception as e:                                   # noqa: BLE001
            falhas.append({'CONSULTA': nome, 'ERRO': str(e)[:200]})
            print('  %-24s FALHOU · %s' % (nome, str(e)[:80]))
            continue
        h = sha256(corpo)
        destino = os.path.join(STORE, 'OSM_%s' % re.sub(r'\W+', '_', nome), 'v1_%s' % h[:12])
        os.makedirs(destino, exist_ok=True)
        caminho = os.path.join(destino, 'overpass.json')
        with open(caminho, 'wb') as f:                           # BRUTO ANTES DE PARSE
            f.write(corpo)
        try:
            d = json.loads(corpo)
        except ValueError:
            falhas.append({'CONSULTA': nome, 'ERRO': 'resposta nao e JSON (HTTP %s)' % status})
            print('  %-24s RESPOSTA NAO E JSON' % nome)
            continue
        achados = d.get('elements', [])
        if not achados:
            falhas.append({'CONSULTA': nome, 'ERRO': 'lista vazia — e FALHA, nunca zero pontos'})
        for e in achados:
            elementos[(e['type'], e['id'])] = e
        brutos.append({'CONSULTA': nome, 'RAW_PATH': os.path.relpath(caminho, ROOT).replace(os.sep, '/'),
                       'RAW_SHA256': h, 'BYTES': len(corpo), 'ELEMENTOS': len(achados)})
        print('  %-24s %4d elementos · sha %s' % (nome, len(achados), h[:12]))
        time.sleep(2)

    pontos = []
    for (tipo, ident), e in elementos.items():
        t = e.get('tags', {})
        lat = e.get('lat') or (e.get('center') or {}).get('lat')
        lon = e.get('lon') or (e.get('center') or {}).get('lon')
        if lat is None:
            continue
        pontos.append({'OSM_TYPE': tipo, 'OSM_ID': ident, 'NOME': t.get('name'),
                       'SHOP': t.get('shop'), 'OPERADOR': t.get('operator'),
                       'LAT': lat, 'LON': lon,
                       'RUA': t.get('addr:street'), 'NUMERO': t.get('addr:housenumber'),
                       'CIDADE_TAG': t.get('addr:city'), 'CAP': t.get('addr:postcode'),
                       'TELEFONE': t.get('phone') or t.get('contact:phone'),
                       'SITE': t.get('website') or t.get('contact:website'),
                       'HORARIO': t.get('opening_hours')})
    cache = _geocodificacao_ja_feita()
    novos = [p for p in pontos if (p['OSM_TYPE'], p['OSM_ID']) not in cache]
    print('  geocodificando %d pontos novos (%d reaproveitados do que ja foi geocodificado)...'
          % (len(novos), len(pontos) - len(novos)))
    for i, p in enumerate(pontos):
        antigo = cache.get((p['OSM_TYPE'], p['OSM_ID']))
        if antigo:
            for k in ('COMUNE', 'PROVINCIA_NOME', 'PROVINCIA', 'REGIAO_OSM'):
                p[k] = antigo.get(k)
            continue
        try:
            corpo, _ = _pedir('%s?format=jsonv2&lat=%s&lon=%s&zoom=10&addressdetails=1'
                              % (NOMINATIM, p['LAT'], p['LON']), timeout=30)
            a = json.loads(corpo).get('address', {})
            p['COMUNE'] = a.get('city') or a.get('town') or a.get('village') or a.get('municipality')
            p['PROVINCIA_NOME'] = a.get('county') or a.get('state_district')
            p['PROVINCIA'] = PROVINCIAS.get(p['PROVINCIA_NOME'] or '')
            p['REGIAO_OSM'] = a.get('state')
        except Exception:                                        # noqa: BLE001
            p['COMUNE'] = p['PROVINCIA_NOME'] = p['PROVINCIA'] = p['REGIAO_OSM'] = None
        time.sleep(1.1)
        if i and i % 50 == 0:
            print('    ... %d/%d' % (i, len(pontos)))

    fim = agora()
    no_veneto = [p for p in pontos if p['PROVINCIA']]
    fora = len(pontos) - len(no_veneto)
    obs = {
        'RUN_ID': run_id, 'SOURCE_ID': SOURCE_ID,
        'SOURCE_URL': OVERPASS, 'DOCUMENT_ID': 'OSM:VENETO:%s' % fim[:10],
        'DOCUMENT_VERSION_ID': 'v1_%s' % sha256(json.dumps(brutos, sort_keys=True).encode())[:12],
        'RAW_SHA256': sha256(json.dumps(brutos, sort_keys=True).encode()),
        'BYTES': sum(b['BYTES'] for b in brutos), 'MIME_ASSINATURA': 'JSON',
        'SOURCE_DATE': fim[:10], 'SOURCE_DATE_ISO': fim[:10],
        'FACT_TIME': 'o OSM nao data o ponto: a data e a da CAPTURA, nao a da abertura da loja',
        'SOURCE_LOCATION': 'OpenStreetMap (mirror Overpass kumi.systems) + Nominatim',
        'FACT_LOCATION': 'Veneto, por coordenada',
        'CAPTURED_AT': fim, 'COLLECTION_RUN_STARTED_AT': inicio,
        'OBSERVATION_RESULT': 'BASELINE_DOCUMENT',
        'HEALTH_STATE': 'DEGRADED' if falhas else 'HEALTHY',
        'HEALTH_REASONS': [f['CONSULTA'] + ': ' + f['ERRO'] for f in falhas],
        'CADENCE_STATE': 'CONTINUOUS — o OSM muda a qualquer hora, sem versao',
        'DECLARED_FREQUENCY': 'nenhuma — base colaborativa',
        'OBSERVED_FREQUENCY': 'NAO SEI',
        'EXPECTED_NEXT_UPDATE': 'UNKNOWN',
        'RAW_OBJECT_CREATED': True, 'RAW_PATH': [b['RAW_PATH'] for b in brutos],
        'RAW_PRESERVED_BEFORE_PARSE': True, 'DISCOVERY_DEGRADED': bool(falhas),
        'EGRESS_IP': ip,
        'PARSE_ERROR': None, 'LICENCA': 'ODbL — atribuicao obrigatoria a © OpenStreetMap contributors',
        'parse': {'PONTOS': len(pontos), 'NO_VENETO': len(no_veneto), 'FORA_DO_VENETO': fora,
                  'COM_NOME': sum(1 for p in no_veneto if p['NOME']),
                  'COM_TELEFONE': sum(1 for p in no_veneto if p['TELEFONE']),
                  'COBERTURA_CONTRA_531_PCT': round(100 * len(no_veneto) / TITULARES_DECLARANTES_2022, 1)},
    }
    os.makedirs(LEDGER, exist_ok=True)
    with open(os.path.join(LEDGER, 'observations.ndjson'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(obs, ensure_ascii=False) + '\n')
    with open(os.path.join(LEDGER, 'runs.ndjson'), 'a', encoding='utf-8') as f:
        f.write(json.dumps({'RUN_ID': run_id, 'STARTED_AT': inicio, 'FINISHED_AT': fim,
                            'IS_BASELINE': True, 'COLLECTOR_VERSION': 'canal_compradores-v1',
                            'SOURCE_CONTRACT_VERSION': 'IT-T10-002-v1',
                            'VPN_COUNTRY': pv.NAO_SEI, 'EGRESS_IP': ip,
                            'contadores': {'SOURCES_ATTEMPTED': len(CONSULTAS),
                                           'FAILED': len(falhas),
                                           'RAW_OBJECTS_CREATED': len(brutos),
                                           'ITEM_COUNT_RAW': len(pontos),
                                           'ITEM_COUNT_NORMALIZED': len(no_veneto)}},
                           ensure_ascii=False) + '\n')

    # UNIAO DO QUE JA FOI VISTO, e nao so do que esta corrida viu.
    # O OSM muda a qualquer hora e o espelho falha a qualquer hora: apagar um ponto porque a
    # consulta que o traria caiu com 504 seria transformar falha de rota em ausencia no mundo.
    # Cada ponto carrega a data em que foi visto pela primeira e pela ultima vez, e diz se
    # esta corrida o viu.
    vistos_agora = {(p['OSM_TYPE'], p['OSM_ID']) for p in no_veneto}
    uniao = {}
    for antigo in cache.values():
        k = (antigo['OSM_TYPE'], antigo['OSM_ID'])
        antigo = dict(antigo)
        antigo['VISTO_NESTA_CORRIDA'] = k in vistos_agora
        uniao[k] = antigo
    for novo in no_veneto:
        k = (novo['OSM_TYPE'], novo['OSM_ID'])
        base = uniao.get(k, {})
        novo = dict(novo)
        novo['PRIMEIRA_VEZ_VISTO'] = base.get('PRIMEIRA_VEZ_VISTO', fim[:10])
        novo['ULTIMA_VEZ_VISTO'] = fim[:10]
        novo['VISTO_NESTA_CORRIDA'] = True
        uniao[k] = novo
    for k, v in uniao.items():
        v.setdefault('PRIMEIRA_VEZ_VISTO', fim[:10])
        v.setdefault('ULTIMA_VEZ_VISTO', fim[:10])
    no_veneto = list(uniao.values())

    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, 'DIM-PONTO-DE-CANAL.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'ARTIFACT_ID': 'IT-VENETO-DIM-PONTO-DE-CANAL', 'RUN_ID': run_id,
            'GERADO_EM': fim, 'GERADO_POR': 'coleta/canal_compradores.py',
            'FONTE': {'NOME': 'OpenStreetMap via Overpass + Nominatim', 'SOURCE_ID': SOURCE_ID,
                      'LICENCA': 'ODbL — © OpenStreetMap contributors',
                      'CONSULTAS': [c[0] for c in CONSULTAS], 'BRUTOS': brutos, 'FALHAS': falhas},
            'LIMITE': ('o OSM NAO e censo. %d pontos no Veneto contra %d titulares de autorizacao '
                       'de venda declarados em 2022 = %.1f%% de cobertura MAXIMA, e boa parte dos '
                       'pontos e garden centre de varejo, nao canal profissional. Serve como camada '
                       'de LOCALIZACAO, nunca como lista-mae.'
                       % (len(no_veneto), TITULARES_DECLARANTES_2022,
                          100 * len(no_veneto) / TITULARES_DECLARANTES_2022)),
            'POR_PROVINCIA': {p: sum(1 for x in no_veneto if x['PROVINCIA'] == p)
                              for p in sorted({x['PROVINCIA'] for x in no_veneto})},
            'PONTOS': sorted(no_veneto, key=lambda x: (x['PROVINCIA'], x['NOME'] or 'zzz')),
            'FORA_DO_VENETO_DESCARTADOS': fora,
            'NAO_VISTOS_NESTA_CORRIDA': sum(1 for p in no_veneto if not p.get('VISTO_NESTA_CORRIDA')),
            'AVISO_DE_AUSENCIA': ('ponto com VISTO_NESTA_CORRIDA=false pode ter sumido do OSM OU '
                                  'pertencer a uma consulta que falhou nesta corrida. Falha de rota '
                                  'nao e ausencia no mundo: so a proxima corrida limpa sem duvida.'),
        }, f, ensure_ascii=False, indent=1)
    print('PONTOS · %d no Veneto (%d fora, descartados) · cobertura maxima %.1f%% dos 531'
          % (len(no_veneto), fora, 100 * len(no_veneto) / TITULARES_DECLARANTES_2022))
    return obs


def main():
    p = argparse.ArgumentParser(description='Pontos do canal — a camada de localizacao')
    p.add_argument('--coletar', action='store_true')
    a = p.parse_args()
    coletar()


if __name__ == '__main__':
    main()
