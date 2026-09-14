#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O MERCADO ITALIANO INTEIRO — quanto se distribui, por provincia e por categoria.

    py coleta/mercado_italia.py                 coleta e normaliza
    py coleta/mercado_italia.py --coletar       so o bruto
    py coleta/mercado_italia.py --normalizar    so as tabelas

POR QUE ESTE FICHEIRO EXISTE
----------------------------
A declaracao de venda por produto (IT-T10-001) existe no Veneto e, ate onde se leu, so la.
Perguntar «e nas outras regioes?» sem fonte devolveria opiniao. O ISTAT publica, para TODA
a Italia, a quantidade de fitossanitarios distribuida **por provincia e por categoria**
(fungicida, inseticida/acaricida, herbicida, varios) em kg — levantamento censitario anual.

    NAO E A MESMA COISA QUE O VENETO, E O ARTEFATO DIZ ISSO EM VOZ ALTA.
    ARPAV = venda declarada POR PRODUTO, com numero de registro: da para saber a MARCA.
    ISTAT = quantidade distribuida POR CATEGORIA: NAO da para saber marca nem produto.

Juntas, as duas respondem coisas diferentes: o ISTAT diz ONDE ha mercado e de que tipo; o
ARPAV diz, no Veneto, DE QUEM e esse mercado. Onde o ISTAT esta sozinho, a marca e NAO SEI —
e fica escrito NAO SEI, nao preenchido por semelhanca com o Veneto.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import proveniencia as pv  # noqa: E402

SOURCE_ID = 'IT-T10-003'
PAIS = 'italy'
BASE = 'https://esploradati.istat.it/SDMXWS/rest/data/IT1,%s,1.0/all?startPeriod=%d'
ACCEPT = 'application/vnd.sdmx.data+csv;version=1.0.0;labels=both'
FLUXOS = {
    '101_22_DF_DCSP_FITOSANITARI_1': 'produtos distribuidos por provincia',
    '101_22_DF_DCSP_FITOSANITARI_2': 'substancias ativas contidas, por provincia',
}
ANO_INICIAL = 2015
STORE = os.path.join(ROOT, 'data', 'collection-store', PAIS, SOURCE_ID)
LEDGER = os.path.join(ROOT, 'data', 'collection-ledger', PAIS)
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-MERCADO-NACIONAL')

# O que o proprio dado declara ser. Categoria NAO e marca, e a distancia entre as duas e
# exatamente o que separa «ha mercado aqui» de «vende-se ADAMA aqui».
CATEGORIAS = {'FUN': 'fungicida', 'INS': 'inseticida e acaricida', 'HER': 'herbicida',
              'VAI': 'varios', 'OTHBIO': 'outros, inclusive de origem biologica',
              'ALL': 'todos os itens'}
INDICADOR_KG = 'PPPKG'
# A DIMENSAO QUE QUASE PRODUZIU UM NUMERO CONFIANTE E ERRADO.
# Cada (territorio, ano, categoria) aparece QUATRO vezes, uma por classe de toxicidade:
# ALL, NC (nao classificavel), HARM (nocivo) e TOX (muito toxico ou toxico). Ler sem filtrar
# faz a ultima linha sobrescrever as outras — e o Veneto de 2024 saiu 624.887 kg em vez de
# 17.737.397. Vinte e oito vezes menos, sem nenhum erro visivel na tela.
TOXICIDADE_TOTAL = 'ALL'


def agora():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def egresso():
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=15) as r:
            return r.read().decode().strip() or pv.NAO_SEI
    except Exception:                                            # noqa: BLE001
        return pv.NAO_SEI


def _baixar(url, tentativas=3):
    """O tunel de saida fecha em resposta grande. Tres tentativas antes de declarar falha."""
    erro = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={'Accept': ACCEPT,
                                                       'Accept-Encoding': 'gzip',
                                                       'User-Agent': 'SintoniaEAME/1.0 (coleta)'})
            with urllib.request.urlopen(req, timeout=240) as r:
                corpo = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    import gzip
                    corpo = gzip.decompress(corpo)
                return corpo, r.status
        except Exception as e:                                   # noqa: BLE001
            erro = e
            import time
            time.sleep(5 * (i + 1))
    raise erro


def _campo(linha, prefixo):
    for k in linha:
        if k.startswith(prefixo):
            return linha[k]
    return ''


def _rotulo(v):
    """'ITC1: Piemonte' -> ('ITC1', 'Piemonte'). Sem rotulo, devolve o codigo e NAO SEI."""
    if ':' in v:
        cod, nome = v.split(':', 1)
        return cod.strip(), nome.strip()
    return v.strip(), pv.NAO_SEI


def conferir(corpo):
    """SCHEMA + IDENTIDADE. Lista vazia e FALHA; HTML com 200 tambem."""
    motivos = []
    cabeca = corpo[:200].lstrip().lower()
    if cabeca.startswith(b'<'):
        return 'FAILED', ['resposta nao e CSV (comeca com <)'], []
    linhas = list(csv.DictReader(io.StringIO(corpo.decode('utf-8', errors='replace'))))
    if not linhas:
        return 'FAILED', ['lista vazia — e FALHA, nunca zero distribuicao'], []
    for exigido in ('REF_AREA', 'DATA_TYPE', 'PLANT_PROTECTION_PROD', 'TIME_PERIOD', 'OBS_VALUE'):
        if not any(k.startswith(exigido) for k in linhas[0]):
            motivos.append('campo do contrato ausente: %s' % exigido)
    areas = {_rotulo(_campo(l, 'REF_AREA'))[0] for l in linhas}
    if len(areas) < 100:
        motivos.append('so %d territorios — o esperado e Italia + regioes + ~107 provincias' % len(areas))
    if any('campo do contrato ausente' in m for m in motivos):
        return 'FAILED', motivos, linhas
    return ('DEGRADED' if motivos else 'HEALTHY'), motivos, linhas


def coletar():
    inicio, ip = agora(), egresso()
    run_id = 'IT-T10-003-%s' % datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H%M%S')
    guardados = []
    for fluxo, oque in FLUXOS.items():
        url = BASE % (fluxo, ANO_INICIAL)
        corpo, status = _baixar(url)
        h = sha256(corpo)
        destino = os.path.join(STORE, fluxo, 'v1_%s' % h[:12])
        os.makedirs(destino, exist_ok=True)
        caminho = os.path.join(destino, '%s.csv' % fluxo)
        with open(caminho, 'wb') as f:                           # BRUTO ANTES DE PARSE
            f.write(corpo)
        saude, motivos, linhas = conferir(corpo)
        rel = os.path.relpath(caminho, ROOT).replace(os.sep, '/')
        guardados.append({'FLUXO': fluxo, 'O_QUE_E': oque, 'RAW_PATH': rel, 'RAW_SHA256': h,
                          'BYTES': len(corpo), 'LINHAS': len(linhas), 'HEALTH_STATE': saude,
                          'HEALTH_REASONS': motivos, 'HTTP': status})
        print('  %s · %s · %d linhas · sha %s' % (saude, fluxo, len(linhas), h[:12]))
        obs = {
            'RUN_ID': run_id, 'SOURCE_ID': SOURCE_ID, 'SOURCE_URL': url,
            'DOCUMENT_ID': '%s:%d+' % (fluxo, ANO_INICIAL), 'DOCUMENT_VERSION_ID': 'v1_%s' % h[:12],
            'RAW_SHA256': h, 'BYTES': len(corpo), 'MIME_ASSINATURA': 'CSV', 'HTTP_STATUS': status,
            'SOURCE_DATE': agora()[:10], 'SOURCE_DATE_ISO': agora()[:10],
            'FACT_TIME': 'ano civil, por TIME_PERIOD de cada linha (serie desde %d)' % ANO_INICIAL,
            'SOURCE_LOCATION': 'ISTAT — SDMX esploradati.istat.it',
            'FACT_LOCATION': 'Italia: pais, regioes e provincias',
            'CAPTURED_AT': agora(), 'COLLECTION_RUN_STARTED_AT': inicio,
            'OBSERVATION_RESULT': 'BASELINE_DOCUMENT', 'HEALTH_STATE': saude,
            'HEALTH_REASONS': motivos, 'CADENCE_STATE': 'UPDATED',
            'DECLARED_FREQUENCY': 'anual — levantamento censitario do ISTAT',
            'OBSERVED_FREQUENCY': 'NAO SEI — primeira captura desta fonte nesta casa',
            'EXPECTED_NEXT_UPDATE': 'UNKNOWN',
            'RAW_OBJECT_CREATED': True, 'RAW_PATH': rel, 'RAW_PRESERVED_BEFORE_PARSE': True,
            'DISCOVERY_DEGRADED': None, 'PARSE_ERROR': None, 'EGRESS_IP': ip,
            'LICENCA': 'ISTAT — dados publicos, CC BY 3.0 IT segundo a politica do instituto',
            'parse': {'LINHAS': len(linhas)},
        }
        os.makedirs(LEDGER, exist_ok=True)
        with open(os.path.join(LEDGER, 'observations.ndjson'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(obs, ensure_ascii=False) + '\n')

    fim = agora()
    with open(os.path.join(LEDGER, 'runs.ndjson'), 'a', encoding='utf-8') as f:
        f.write(json.dumps({'RUN_ID': run_id, 'STARTED_AT': inicio, 'FINISHED_AT': fim,
                            'IS_BASELINE': True, 'COLLECTOR_VERSION': 'mercado_italia-v1',
                            'SOURCE_CONTRACT_VERSION': 'IT-T10-003-v1',
                            'VPN_COUNTRY': pv.NAO_SEI, 'EGRESS_IP': ip,
                            'contadores': {'SOURCES_ATTEMPTED': len(FLUXOS),
                                           'RAW_OBJECTS_CREATED': len(guardados),
                                           'ITEM_COUNT_RAW': sum(g['LINHAS'] for g in guardados)}},
                           ensure_ascii=False) + '\n')
    return {'RUN_ID': run_id, 'GUARDADOS': guardados, 'CAPTURED_AT': fim}


def normalizar(info=None):
    """Le o bruto do store e escreve a demanda por territorio, ano e categoria."""
    fluxo = '101_22_DF_DCSP_FITOSANITARI_1'
    base = os.path.join(STORE, fluxo)
    if not os.path.isdir(base):
        raise SystemExit('sem bruto preservado — rode --coletar primeiro')
    versao = sorted(os.listdir(base))[-1]
    caminho = os.path.join(base, versao, '%s.csv' % fluxo)
    with open(caminho, encoding='utf-8') as f:
        linhas = list(csv.DictReader(f))

    territorios, descartadas = {}, []
    for i, l in enumerate(linhas, start=2):
        if _rotulo(_campo(l, 'DATA_TYPE'))[0] != INDICADOR_KG:
            descartadas.append({'LINHA_NO_FICHEIRO': i, 'EXCLUSION_REASON': 'INDICADOR_NAO_E_KG',
                                'MOTIVO_DA_RECUSA': 'a linha mede armadilhas ou tratamentos, nao quilos de produto'})
            continue
        if _rotulo(_campo(l, 'LEVEL_OF_TOXICITY'))[0] != TOXICIDADE_TOTAL:
            descartadas.append({'LINHA_NO_FICHEIRO': i, 'EXCLUSION_REASON': 'RECORTE_DE_TOXICIDADE',
                                'MOTIVO_DA_RECUSA': ('a linha e um RECORTE por classe de toxicidade; somar '
                                                     'com o total contaria o mesmo quilo duas vezes')})
            continue
        cod_area, nome_area = _rotulo(_campo(l, 'REF_AREA'))
        cod_cat, _ = _rotulo(_campo(l, 'PLANT_PROTECTION_PROD'))
        ano = l.get('TIME_PERIOD') or _campo(l, 'TIME_PERIOD')
        try:
            valor = float(l.get('OBS_VALUE') or 0)
        except ValueError:
            descartadas.append({'LINHA_NO_FICHEIRO': i, 'EXCLUSION_REASON': 'VALOR_ILEGIVEL',
                                'MOTIVO_DA_RECUSA': 'OBS_VALUE nao converte para numero'})
            continue
        t = territorios.setdefault(cod_area, {'CODIGO': cod_area, 'NOME': nome_area,
                                              'NIVEL': _nivel(cod_area), 'ANOS': {}})
        t['ANOS'].setdefault(ano, {})[CATEGORIAS.get(cod_cat, cod_cat)] = valor

    anos = sorted({a for t in territorios.values() for a in t['ANOS']})
    ultimo = anos[-1]
    provincias = [t for t in territorios.values() if t['NIVEL'] == 'PROVINCIA']
    regioes = [t for t in territorios.values() if t['NIVEL'] == 'REGIAO']

    def kg(t, ano, cat='todos os itens'):
        return t['ANOS'].get(ano, {}).get(cat)

    ranking_prov = sorted([p for p in provincias if kg(p, ultimo) is not None],
                          key=lambda p: -kg(p, ultimo))
    ranking_reg = sorted([r for r in regioes if kg(r, ultimo) is not None],
                         key=lambda r: -kg(r, ultimo))
    corpo = {
        'ARTIFACT_ID': 'IT-DEMANDA-POR-TERRITORIO', 'GERADO_EM': agora(),
        'GERADO_POR': 'coleta/mercado_italia.py', 'FONTE': SOURCE_ID,
        'FONTE_NOME': 'ISTAT — Distribuzione per uso agricolo dei prodotti fitosanitari',
        'COLETA': info or 'NAO SEI — normalizacao rodada sem coleta na mesma execucao',
        'INDICADOR': 'quantidade de produtos fitossanitarios distribuida para uso agricola (kg)',
        'ANOS': anos, 'ANO_MAIS_RECENTE': ultimo,
        'O_QUE_ESTA_FONTE_NAO_PROVA': [
            'marca ou titular — o ISTAT mede CATEGORIA, nunca produto',
            'quem vendeu e quem comprou', 'preco ou valor',
            'se o produto foi aplicado (distribuido != aplicado)'],
        'DIFERENCA_PARA_O_VENETO': ('IT-T10-001 (ARPAV) e venda declarada POR PRODUTO, com numero de '
                                    'registro: da marca. Esta fonte e distribuicao POR CATEGORIA: nao '
                                    'da marca. Onde so existe esta, a marca e NAO SEI.'),
        'TERRITORIOS': len(territorios), 'PROVINCIAS': len(provincias), 'REGIOES': len(regioes),
        'DESCARTADAS': len(descartadas),
        'RANKING_REGIOES_%s' % ultimo: [
            {'REGIAO': r['NOME'], 'CODIGO': r['CODIGO'], 'KG': kg(r, ultimo),
             'FUNGICIDA': kg(r, ultimo, 'fungicida'), 'HERBICIDA': kg(r, ultimo, 'herbicida'),
             'INSETICIDA': kg(r, ultimo, 'inseticida e acaricida')} for r in ranking_reg],
        'RANKING_PROVINCIAS_%s' % ultimo: [
            {'PROVINCIA': p['NOME'], 'CODIGO': p['CODIGO'], 'KG': kg(p, ultimo),
             'FUNGICIDA': kg(p, ultimo, 'fungicida'), 'HERBICIDA': kg(p, ultimo, 'herbicida'),
             'INSETICIDA': kg(p, ultimo, 'inseticida e acaricida')} for p in ranking_prov],
        'PROVA_CRUZADA_VENETO': _prova_cruzada(territorios),
        'SERIE_POR_TERRITORIO': territorios,
        'O_QUE_FOI_DESCARTADO_E_POR_QUE': descartadas[:50],
    }
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, 'IT-DEMANDA-POR-TERRITORIO.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('DEMANDA · %d territorios (%d provincias, %d regioes) · anos %s-%s · %d linhas descartadas'
          % (len(territorios), len(provincias), len(regioes), anos[0], anos[-1], len(descartadas)))
    return corpo


def _prova_cruzada(territorios):
    """Duas fontes oficiais e independentes medindo a MESMA coisa no mesmo territorio.

    O ISTAT levanta a distribuicao por provincia; a ARPAV publica a declaracao de venda dos
    revendedores do Veneto. Nao sao a mesma operacao estatistica e nao tem de bater na casa
    decimal — mas se divergirem por ordem de grandeza, uma das duas leituras esta errada.
    Isto ja pagou o proprio custo: foi esta comparacao que revelou o filtro de toxicidade em
    falta, quando o Veneto do ISTAT apareceu 28 vezes menor do que o da ARPAV.
    """
    serie = os.path.join(ROOT, 'data', 'samples', 'IT-VENETO-CANALE', 'SERIE-POR-ANO.json')
    if not os.path.exists(serie):
        return 'NAO SEI — a serie do Veneto (IT-T10-001) nao esta no repositorio'
    with open(serie, encoding='utf-8') as f:
        arpav = {str(a['ANO']): a['TOTAL_KG_L'] for a in json.load(f)['ANOS_MEDIDOS']}
    ven = territorios.get('ITD3', {}).get('ANOS', {})
    linhas = []
    for ano in sorted(set(arpav) & set(ven)):
        i = ven[ano].get('todos os itens')
        a = arpav[ano]
        if not i or not a:
            continue
        linhas.append({'ANO': ano, 'ISTAT_KG': round(i, 2), 'ARPAV_KG': round(a, 2),
                       'DIFERENCA_PCT': round(100 * (i - a) / a, 2)})
    return {'O_QUE_COMPARA': 'ISTAT (distribuicao por provincia) x ARPAV (venda declarada por produto), Veneto',
            'POR_QUE_NAO_TEM_DE_BATER_EXATO': ('sao levantamentos diferentes: o ISTAT mede distribuicao e a '
                                               'ARPAV mede venda declarada pelo revendedor. Ordem de grandeza '
                                               'igual e o que se espera; casa decimal, nao'),
            'LINHAS': linhas}


def _nivel(codigo):
    """ITxx = pais; ITC/ITF/ITG/ITH/ITI + digito = regiao; ITxxx com 3 letras+digitos = provincia."""
    if codigo == 'IT':
        return 'PAIS'
    if len(codigo) == 4 and codigo[:2] == 'IT':
        return 'REGIAO'
    if len(codigo) == 5:
        return 'PROVINCIA'
    return 'NAO SEI'


def main():
    p = argparse.ArgumentParser(description='Mercado italiano — distribuicao por provincia (ISTAT)')
    p.add_argument('--coletar', action='store_true')
    p.add_argument('--normalizar', action='store_true')
    a = p.parse_args()
    tudo = not (a.coletar or a.normalizar)
    info = coletar() if (a.coletar or tudo) else None
    if a.normalizar or tudo:
        normalizar(info)


if __name__ == '__main__':
    main()
