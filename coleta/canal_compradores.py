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


REGIOES_IT = {
    'IT-21': 'Piemonte', 'IT-23': "Valle d'Aosta", 'IT-25': 'Lombardia',
    'IT-32': 'Trentino-Alto Adige', 'IT-34': 'Veneto', 'IT-36': 'Friuli-Venezia Giulia',
    'IT-42': 'Liguria', 'IT-45': 'Emilia-Romagna', 'IT-52': 'Toscana', 'IT-55': 'Umbria',
    'IT-57': 'Marche', 'IT-62': 'Lazio', 'IT-65': 'Abruzzo', 'IT-67': 'Molise',
    'IT-72': 'Campania', 'IT-75': 'Puglia', 'IT-77': 'Basilicata', 'IT-78': 'Calabria',
    'IT-82': 'Sicilia', 'IT-88': 'Sardegna',
}
# UMA consulta por regiao, e a mais especifica que existe: shop=agrarian e a etiqueta do OSM
# para loja de insumo agricola. A busca por NOME e cara — o espelho devolve 504 com regex
# sobre area inteira — e por isso corre UMA vez, em bbox nacional, no fim. Vinte consultas
# caras nao medem mais o mercado: medem a paciencia do espelho.
CONSULTAS_IT = (
    ('shop=agrarian', '[out:json][timeout:120];area["ISO3166-2"="%s"]->.r;(nwr["shop"="agrarian"](area.r););out center tags;'),
)
BBOX_ITALIA = (35.4, 6.6, 47.1, 18.6)
CONSULTA_NOME_NACIONAL = ('name~Consorzio Agrario (bbox Italia)',
                          '[out:json][timeout:160];(nwr["name"~"Consorzio Agrario",i](%f,%f,%f,%f););out center tags;')


def _gravar_parcial(pontos, por_regiao, brutos, falhas):
    """Grava o que ja se tem, a cada regiao. Corrida longa que so escreve no fim perde tudo se
    o relogio bater antes — e trabalho perdido volta a pedir de graca a uma fonte alheia."""
    unicos = {(p['OSM_TYPE'], p['OSM_ID']): p for p in pontos}
    destino = os.path.join(ROOT, 'data', 'samples', 'IT-MERCADO-NACIONAL')
    os.makedirs(destino, exist_ok=True)
    with open(os.path.join(destino, 'DIM-PONTO-DE-CANAL-ITALIA.json'), 'w', encoding='utf-8') as f:
        json.dump({'ARTIFACT_ID': 'IT-DIM-PONTO-DE-CANAL-ITALIA',
                   'ESTADO': 'PARCIAL — corrida em curso',
                   'GERADO_EM': agora(), 'GERADO_POR': 'coleta/canal_compradores.py --italia',
                   'POR_REGIAO': por_regiao, 'FALHAS': falhas, 'BRUTOS': brutos,
                   'PONTOS': sorted(unicos.values(), key=lambda x: (x['REGIAO'], x['NOME']))},
                  f, ensure_ascii=False, indent=1)


def repescar(isos):
    """Volta so as regioes que nao devolveram nada, e funde no artefato que ja existe.

    Uma regiao que veio vazia por espelho sobrecarregado nao pode ficar marcada como zero, e
    tambem nao justifica repetir as vinte consultas: repete-se a que falhou. O que ja estava
    guardado permanece — a repescagem soma, nunca substitui o que veio antes.
    """
    caminho = os.path.join(ROOT, 'data', 'samples', 'IT-MERCADO-NACIONAL',
                           'DIM-PONTO-DE-CANAL-ITALIA.json')
    if not os.path.exists(caminho):
        raise SystemExit('nao ha artefato nacional para repescar — rode --italia primeiro')
    with open(caminho, encoding='utf-8') as f:
        antigo = json.load(f)
    pontos = list(antigo.get('PONTOS', []))
    por_regiao = dict(antigo.get('POR_REGIAO', {}))
    brutos = list(antigo.get('BRUTOS', []))
    falhas = [f for f in antigo.get('FALHAS', []) if f.get('REGIAO') not in
              {REGIOES_IT[i] for i in isos if i in REGIOES_IT}]
    etiqueta, gabarito = CONSULTAS_IT[0]
    for iso in isos:
        nome = REGIOES_IT.get(iso)
        if not nome:
            print('  %s nao e uma regiao conhecida — ignorada' % iso)
            continue
        try:
            corpo, _ = _overpass(gabarito % iso)
            elementos = json.loads(corpo).get('elements', [])
        except Exception as e:                                   # noqa: BLE001
            falhas.append({'REGIAO': nome, 'CONSULTA': etiqueta, 'ERRO': str(e)[:160]})
            print('  %-22s FALHOU de novo' % nome, flush=True)
            continue
        if not elementos:
            falhas.append({'REGIAO': nome, 'CONSULTA': etiqueta,
                           'ERRO': 'LISTA_VAZIA — resposta 200 sem nenhum elemento'})
            por_regiao[nome] = pv.NAO_SEI
            print('  %-22s NAO SEI (vazio de novo)' % nome, flush=True)
            continue
        h = sha256(corpo)
        destino = os.path.join(STORE, 'OSM_IT_%s_repescagem' % iso.replace('-', ''), 'v1_%s' % h[:12])
        os.makedirs(destino, exist_ok=True)
        with open(os.path.join(destino, 'overpass.json'), 'wb') as f:
            f.write(corpo)
        brutos.append({'REGIAO': nome, 'CONSULTA': etiqueta + ' (repescagem)', 'RAW_SHA256': h,
                       'BYTES': len(corpo),
                       'RAW_PATH': os.path.relpath(os.path.join(destino, 'overpass.json'),
                                                   ROOT).replace(os.sep, '/')})
        n = 0
        for e in elementos:
            tg = e.get('tags', {})
            lat = e.get('lat') or (e.get('center') or {}).get('lat')
            lon = e.get('lon') or (e.get('center') or {}).get('lon')
            if lat is None:
                continue
            pontos.append({'REGIAO': nome, 'ISO': iso, 'OSM_TYPE': e['type'], 'OSM_ID': e['id'],
                           'NOME': tg.get('name') or pv.NAO_SEI, 'SHOP': tg.get('shop'),
                           'OPERADOR': tg.get('operator'), 'LAT': lat, 'LON': lon,
                           'RUA': tg.get('addr:street') or pv.NAO_SEI,
                           'COMUNE': tg.get('addr:city') or pv.NAO_SEI,
                           'CAP': tg.get('addr:postcode') or pv.NAO_SEI,
                           'TELEFONE': tg.get('phone') or tg.get('contact:phone') or pv.NAO_SEI,
                           'SITE': tg.get('website') or tg.get('contact:website') or pv.NAO_SEI,
                           'HORARIO': tg.get('opening_hours') or pv.NAO_SEI,
                           'ENCONTRADO_POR': etiqueta + ' (repescagem)'})
            n += 1
        por_regiao[nome] = n
        print('  %-22s %4d pontos (repescagem)' % (nome, n), flush=True)
        _gravar_parcial(pontos, por_regiao, brutos, falhas)
        time.sleep(2)
    _gravar_parcial(pontos, por_regiao, brutos, falhas)
    unicos = {(p['OSM_TYPE'], p['OSM_ID']) for p in pontos}
    print('REPESCAGEM · %d pontos unicos no total' % len(unicos))


def geo_pendentes():
    """Da regiao aos pontos que vieram da busca NACIONAL por nome.

    A consulta por bbox nao sabe em que regiao cada ponto caiu — e adivinhar por caixa
    envolvente seria inventar. Aqui se MEDE, ponto a ponto, pela geocodificacao reversa, ao
    ritmo que a politica do Nominatim permite. O que nao resolver continua NAO SEI.
    """
    caminho = os.path.join(ROOT, 'data', 'samples', 'IT-MERCADO-NACIONAL',
                           'DIM-PONTO-DE-CANAL-ITALIA.json')
    with open(caminho, encoding='utf-8') as f:
        art = json.load(f)
    pendentes = [p for p in art['PONTOS'] if p.get('REGIAO') in (None, pv.NAO_SEI)]
    print('  %d pontos sem regiao' % len(pendentes), flush=True)
    resolvidos = 0
    for i, p in enumerate(pendentes):
        try:
            corpo, _ = _pedir('%s?format=jsonv2&lat=%s&lon=%s&zoom=8&addressdetails=1'
                              % (NOMINATIM, p['LAT'], p['LON']), timeout=30)
            a = json.loads(corpo).get('address', {})
            regiao = a.get('state')
            if a.get('country_code') != 'it':
                p['REGIAO'] = 'FORA DA ITALIA'
            elif regiao:
                p['REGIAO'] = regiao
                p['PROVINCIA_NOME'] = a.get('county') or a.get('state_district') or pv.NAO_SEI
                if p.get('COMUNE') in (None, pv.NAO_SEI):
                    p['COMUNE'] = (a.get('city') or a.get('town') or a.get('village')
                                   or a.get('municipality') or pv.NAO_SEI)
                resolvidos += 1
        except Exception:                                        # noqa: BLE001
            pass
        time.sleep(1.1)
        if i and i % 50 == 0:
            print('    ... %d/%d' % (i, len(pendentes)), flush=True)
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(art, f, ensure_ascii=False, indent=1)
    por_regiao = {}
    for p in art['PONTOS']:
        por_regiao[p['REGIAO']] = por_regiao.get(p['REGIAO'], 0) + 1
    art['POR_REGIAO'] = dict(sorted(por_regiao.items(), key=lambda x: -x[1]))
    art['GEOCODIFICACAO_REVERSA'] = {
        'PONTOS_SEM_REGIAO_ANTES': len(pendentes), 'RESOLVIDOS': resolvidos,
        'CONTINUAM_NAO_SEI': len(pendentes) - resolvidos,
        'FONTE': 'Nominatim (OSM) — 1 pedido por segundo, como a politica manda'}
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=1)
    print('GEO · %d de %d pontos ganharam regiao' % (resolvidos, len(pendentes)))


def italia():
    """Os pontos de canal das 20 regioes. A regiao vem da CONSULTA, nao de adivinhacao.

    Sem Nominatim de proposito: geocodificar 3.000 pontos a 1 por segundo seria uma hora de
    pedido a uma fonte alheia para descobrir o que a propria consulta ja sabe. Comune so entra
    quando o OSM o declara em addr:city — quando nao declara, fica NAO SEI, e nao se inventa.
    """
    inicio, ip = agora(), egresso()
    run_id = 'IT-T10-002-IT-%s' % datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H%M%S')
    por_regiao, falhas, brutos, pontos = {}, [], [], []
    for iso, nome in REGIOES_IT.items():
        achados_regiao = 0
        for etiqueta, gabarito in CONSULTAS_IT:
            try:
                corpo, _ = _overpass(gabarito % iso)
            except Exception as e:                               # noqa: BLE001
                falhas.append({'REGIAO': nome, 'CONSULTA': etiqueta, 'ERRO': str(e)[:160]})
                continue
            h = sha256(corpo)
            destino = os.path.join(STORE, 'OSM_IT_%s_%s' % (iso.replace('-', ''),
                                                            re.sub(r'\W+', '_', etiqueta)),
                                   'v1_%s' % h[:12])
            os.makedirs(destino, exist_ok=True)
            with open(os.path.join(destino, 'overpass.json'), 'wb') as f:
                f.write(corpo)                                    # BRUTO ANTES DE PARSE
            brutos.append({'REGIAO': nome, 'CONSULTA': etiqueta, 'RAW_SHA256': h,
                           'BYTES': len(corpo),
                           'RAW_PATH': os.path.relpath(os.path.join(destino, 'overpass.json'),
                                                       ROOT).replace(os.sep, '/')})
            try:
                elementos = json.loads(corpo).get('elements', [])
            except ValueError:
                falhas.append({'REGIAO': nome, 'CONSULTA': etiqueta, 'ERRO': 'resposta nao e JSON'})
                continue
            if not elementos:
                # LISTA VAZIA E FALHA, NUNCA ZERO. Uma regiao agricola inteira sem uma unica loja
                # de insumo e, em toda a probabilidade, espelho sobrecarregado devolvendo vazio
                # com HTTP 200 — foi o que aconteceu com a Lombardia e a Toscana na primeira
                # varredura. Gravar 0 ali seria publicar «nao ha» onde o certo e «nao consegui ver».
                falhas.append({'REGIAO': nome, 'CONSULTA': etiqueta,
                               'ERRO': 'LISTA_VAZIA — resposta 200 sem nenhum elemento; '
                                       'a regiao fica NAO SEI, nao zero'})
                continue
            for e in elementos:
                tg = e.get('tags', {})
                lat = e.get('lat') or (e.get('center') or {}).get('lat')
                lon = e.get('lon') or (e.get('center') or {}).get('lon')
                if lat is None:
                    continue
                pontos.append({'REGIAO': nome, 'ISO': iso, 'OSM_TYPE': e['type'], 'OSM_ID': e['id'],
                               'NOME': tg.get('name') or pv.NAO_SEI, 'SHOP': tg.get('shop'),
                               'OPERADOR': tg.get('operator'), 'LAT': lat, 'LON': lon,
                               'RUA': tg.get('addr:street') or pv.NAO_SEI,
                               'COMUNE': tg.get('addr:city') or pv.NAO_SEI,
                               'CAP': tg.get('addr:postcode') or pv.NAO_SEI,
                               'TELEFONE': tg.get('phone') or tg.get('contact:phone') or pv.NAO_SEI,
                               'SITE': tg.get('website') or tg.get('contact:website') or pv.NAO_SEI,
                               'HORARIO': tg.get('opening_hours') or pv.NAO_SEI,
                               'ENCONTRADO_POR': etiqueta})
                achados_regiao += 1
            time.sleep(1.5)
        vazia = any(f['REGIAO'] == nome for f in falhas)
        por_regiao[nome] = pv.NAO_SEI if (achados_regiao == 0 and vazia) else achados_regiao
        print('  %-22s %s' % (nome, 'NAO SEI (consulta nao devolveu nada)' if vazia and not achados_regiao
                              else '%4d pontos' % achados_regiao), flush=True)
        _gravar_parcial(pontos, por_regiao, brutos, falhas)   # o relogio nao pode apagar trabalho feito

    etiqueta, gabarito = CONSULTA_NOME_NACIONAL
    try:
        corpo, _ = _overpass(gabarito % BBOX_ITALIA)
        h = sha256(corpo)
        destino = os.path.join(STORE, 'OSM_IT_NOME_CONSORZIO', 'v1_%s' % h[:12])
        os.makedirs(destino, exist_ok=True)
        with open(os.path.join(destino, 'overpass.json'), 'wb') as f:
            f.write(corpo)
        brutos.append({'REGIAO': 'ITALIA (bbox)', 'CONSULTA': etiqueta, 'RAW_SHA256': h,
                       'BYTES': len(corpo),
                       'RAW_PATH': os.path.relpath(os.path.join(destino, 'overpass.json'),
                                                   ROOT).replace(os.sep, '/')})
        achados = json.loads(corpo).get('elements', [])
        for e in achados:
            tg = e.get('tags', {})
            lat = e.get('lat') or (e.get('center') or {}).get('lat')
            lon = e.get('lon') or (e.get('center') or {}).get('lon')
            if lat is None:
                continue
            pontos.append({'REGIAO': pv.NAO_SEI, 'ISO': pv.NAO_SEI, 'OSM_TYPE': e['type'],
                           'OSM_ID': e['id'], 'NOME': tg.get('name') or pv.NAO_SEI,
                           'SHOP': tg.get('shop'), 'OPERADOR': tg.get('operator'),
                           'LAT': lat, 'LON': lon,
                           'RUA': tg.get('addr:street') or pv.NAO_SEI,
                           'COMUNE': tg.get('addr:city') or pv.NAO_SEI,
                           'CAP': tg.get('addr:postcode') or pv.NAO_SEI,
                           'TELEFONE': tg.get('phone') or tg.get('contact:phone') or pv.NAO_SEI,
                           'SITE': tg.get('website') or tg.get('contact:website') or pv.NAO_SEI,
                           'HORARIO': tg.get('opening_hours') or pv.NAO_SEI,
                           'ENCONTRADO_POR': etiqueta})
        print('  %-22s %4d pontos (bbox nacional; a regiao destes fica NAO SEI)'
              % ('nome Consorzio', len(achados)), flush=True)
        _gravar_parcial(pontos, por_regiao, brutos, falhas)
    except Exception as e:                                       # noqa: BLE001
        falhas.append({'REGIAO': 'ITALIA (bbox)', 'CONSULTA': etiqueta, 'ERRO': str(e)[:160]})

    unicos = {(p['OSM_TYPE'], p['OSM_ID']): p for p in pontos}
    fim = agora()
    obs = {'RUN_ID': run_id, 'SOURCE_ID': SOURCE_ID, 'SOURCE_URL': OVERPASS_ESPELHOS[0],
           'DOCUMENT_ID': 'OSM:ITALIA:%s' % fim[:10], 'DOCUMENT_VERSION_ID': 'v1_%s' % sha256(
               json.dumps(sorted(b['RAW_SHA256'] for b in brutos)).encode())[:12],
           'RAW_SHA256': sha256(json.dumps(sorted(b['RAW_SHA256'] for b in brutos)).encode()),
           'BYTES': sum(b['BYTES'] for b in brutos), 'MIME_ASSINATURA': 'JSON',
           'SOURCE_DATE': fim[:10], 'SOURCE_DATE_ISO': fim[:10],
           'FACT_TIME': 'o OSM nao data o ponto: a data e a da CAPTURA',
           'SOURCE_LOCATION': 'OpenStreetMap via Overpass', 'FACT_LOCATION': 'Italia, 20 regioes',
           'CAPTURED_AT': fim, 'COLLECTION_RUN_STARTED_AT': inicio,
           'OBSERVATION_RESULT': 'BASELINE_DOCUMENT',
           'HEALTH_STATE': 'DEGRADED' if falhas else 'HEALTHY',
           'HEALTH_REASONS': ['%s/%s: %s' % (f['REGIAO'], f['CONSULTA'], f['ERRO']) for f in falhas],
           'CADENCE_STATE': 'CONTINUOUS', 'DECLARED_FREQUENCY': 'nenhuma — base colaborativa',
           'OBSERVED_FREQUENCY': pv.NAO_SEI, 'EXPECTED_NEXT_UPDATE': 'UNKNOWN',
           'RAW_OBJECT_CREATED': True, 'RAW_PATH': [b['RAW_PATH'] for b in brutos],
           'RAW_PRESERVED_BEFORE_PARSE': True, 'DISCOVERY_DEGRADED': bool(falhas),
           'PARSE_ERROR': None, 'EGRESS_IP': ip,
           'LICENCA': 'ODbL — © OpenStreetMap contributors',
           'parse': {'PONTOS': len(unicos), 'POR_REGIAO': por_regiao,
                     'REGIOES_SEM_RESPOSTA': sorted({f['REGIAO'] for f in falhas})}}
    with open(os.path.join(LEDGER, 'observations.ndjson'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(obs, ensure_ascii=False) + '\n')
    with open(os.path.join(LEDGER, 'runs.ndjson'), 'a', encoding='utf-8') as f:
        f.write(json.dumps({'RUN_ID': run_id, 'STARTED_AT': inicio, 'FINISHED_AT': fim,
                            'IS_BASELINE': True, 'COLLECTOR_VERSION': 'canal_compradores-v1-italia',
                            'SOURCE_CONTRACT_VERSION': 'IT-T10-002-v1',
                            'VPN_COUNTRY': pv.NAO_SEI, 'EGRESS_IP': ip,
                            'contadores': {'SOURCES_ATTEMPTED': len(REGIOES_IT) * len(CONSULTAS_IT),
                                           'FAILED': len(falhas), 'RAW_OBJECTS_CREATED': len(brutos),
                                           'ITEM_COUNT_RAW': len(pontos),
                                           'ITEM_COUNT_NORMALIZED': len(unicos)}},
                           ensure_ascii=False) + '\n')

    destino = os.path.join(ROOT, 'data', 'samples', 'IT-MERCADO-NACIONAL')
    os.makedirs(destino, exist_ok=True)
    with open(os.path.join(destino, 'DIM-PONTO-DE-CANAL-ITALIA.json'), 'w', encoding='utf-8') as f:
        json.dump({'ARTIFACT_ID': 'IT-DIM-PONTO-DE-CANAL-ITALIA', 'RUN_ID': run_id,
                   'GERADO_EM': fim, 'GERADO_POR': 'coleta/canal_compradores.py --italia',
                   'FONTE': {'NOME': 'OpenStreetMap via Overpass', 'SOURCE_ID': SOURCE_ID,
                             'LICENCA': 'ODbL — © OpenStreetMap contributors',
                             'CONSULTAS': [c[0] for c in CONSULTAS_IT],
                             'BRUTOS': brutos, 'FALHAS': falhas},
                   'LIMITE': ('o OSM NAO e censo de pontos de venda. E uma base colaborativa: onde ha '
                              'mapeador ativo ha pontos, onde nao ha, nao. Comparar contagem entre '
                              'regioes mede o MAPEAMENTO tanto quanto o mercado.'),
                   'POR_REGIAO': por_regiao, 'PONTOS': sorted(unicos.values(),
                                                              key=lambda x: (x['REGIAO'], x['NOME'])),
                   }, f, ensure_ascii=False, indent=1)
    print('ITALIA · %d pontos unicos em %d regioes · %d consultas falharam'
          % (len(unicos), len([v for v in por_regiao.values() if v]), len(falhas)))
    return obs


def main():
    p = argparse.ArgumentParser(description='Pontos do canal — a camada de localizacao')
    p.add_argument('--coletar', action='store_true')
    p.add_argument('--italia', action='store_true', help='as 20 regioes, sem geocodificacao')
    p.add_argument('--geo-pendentes', dest='geo_pendentes', action='store_true',
                   help='mede a regiao dos pontos vindos da busca nacional por nome')
    p.add_argument('--repescar', type=str, default='',
                   help='so estas regioes, por codigo ISO, ex.: --repescar IT-25,IT-52')
    a = p.parse_args()
    if getattr(a, 'geo_pendentes', False):
        geo_pendentes()
    elif a.repescar:
        repescar([x.strip() for x in a.repescar.split(',') if x.strip()])
    elif a.italia:
        italia()
    else:
        coletar()


if __name__ == '__main__':
    main()
