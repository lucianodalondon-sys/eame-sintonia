#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Colhe os MAPAS NACIONAIS de resistencia do GIRE (sistema iMAR).

Os links "Mappa" no indice de especies apontam para cl2.agriserv.org, dominio
que nao existe mais (NXDOMAIN). A MESMA aplicacao responde em agrovoltaico.org.
O mapa nao e imagem: e um overlay vetorial GML com nome do comune, REGIAO e
numerosita. Este script troca o host, abre cada mapa, pega o GML e le a tabela.

    py .tmp/gire_mapas.py            -> .tmp/gire_mapas.json
"""
import json
import os
import re
import sys
import time
import urllib.request

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
MORTO = 'http://cl2.agriserv.org'
VIVO = 'http://agrovoltaico.org'
IDX = 'http://gire.mlib.cnr.it/index.php?sel=specieCoinvolte'
AQUI = os.path.dirname(os.path.abspath(__file__))


def baixar(url, binario=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = r.read()
    return d if binario else d.decode('utf-8', errors='replace')


def indice():
    """Cada link Mappa com a especie e a cultura que o rotulam no indice."""
    h = baixar(IDX)
    itens = []
    # cada bloco de especie comeca no link da ficha
    blocos = re.split(r"(?=index\.php\?sel=schedeSpecie/)", h)
    for b in blocos:
        m = re.search(r"index\.php\?sel=schedeSpecie/([A-Za-z_]+)", b)
        if not m:
            continue
        especie = m.group(1)
        rotulo = None
        # texto "Mappa (cultura) MECANISMO" antes de cada href javascript
        for mm in re.finditer(
                r"Mappa\s*\(([^)]*)\)|href=javascript:finestra\('([^']+)'\)>\s*([^<]*)<", b):
            if mm.group(1):
                rotulo = mm.group(1).strip()
            else:
                itens.append({
                    'especie_slug': especie,
                    'cultura_rotulo': rotulo,
                    'mecanismo_rotulo': (mm.group(3) or '').strip(),
                    'url_no_site': mm.group(2),
                    'url_viva': mm.group(2).replace(MORTO, VIVO),
                })
    return itens


def abrir_mapa(url):
    h = baixar(url)
    camadas = {}
    for i, v in re.findall(r"id_HRAC\[(\d+)\]='([^']*)'", h):
        camadas.setdefault(i, {})['hrac'] = v
    for i, v in re.findall(r"descrizione_HRAC\[(\d+)\]='([^']*)'", h):
        camadas.setdefault(i, {})['legenda'] = v
    for i, v in re.findall(r"file2gml_js\[(\d+)\]='([^']*)'", h):
        camadas.setdefault(i, {})['gml'] = v
    # cor da amostra da legenda, na ordem em que aparecem
    cores = re.findall(r"background-color:\s*([#\w]+)'>__</span>"
                       r"<span class='bluTit'>\s*([^<]*)</span>", h)
    # especies latinas citadas no painel
    painel = re.search(r"<div id='infoRes2'>(.*?)<div id='specie_inf'>", h, re.S)
    especies = []
    if painel:
        especies = [re.sub(r'\s+', ' ', x).strip()
                    for x in re.findall(r'<i>(.*?)</i>', painel.group(1))]
    return camadas, cores, especies, len(h)


def ler_gml(caminho):
    g = baixar(VIVO + caminho)
    linhas = []
    for fid, corpo in re.findall(
            r'<ogr:file_di_prova_gml fid="(.*?)">(.*?)</ogr:file_di_prova_gml>', g, re.S):
        d = {}
        for k in ('id', 'nome_comuni', 'regioni', 'numerosita'):
            mm = re.search(r'<ogr:%s>(.*?)</ogr:%s>' % (k, k), corpo, re.S)
            d[k] = mm.group(1).strip() if mm else None
        linhas.append(d)
    return linhas, len(g)


def main():
    saida = []
    for it in indice():
        reg = dict(it)
        try:
            camadas, cores, especies, tam = abrir_mapa(it['url_viva'])
            reg['bytes_pagina'] = tam
            reg['especies_no_painel'] = especies
            reg['legenda_cores'] = [{'cor': c, 'rotulo': r.strip()} for c, r in cores]
            reg['camadas'] = []
            for i in sorted(camadas, key=int):
                c = camadas[i]
                if not c.get('gml'):
                    continue
                comuni, gtam = ler_gml(c['gml'])
                reg['camadas'].append({
                    'hrac': c.get('hrac'),
                    'legenda': c.get('legenda'),
                    'gml': c['gml'],
                    'bytes_gml': gtam,
                    'n_comuni': len(comuni),
                    'comuni': comuni,
                })
            reg['estado'] = 'LIDO'
        except Exception as e:                                   # noqa: BLE001
            reg['estado'] = 'FALHA'
            reg['erro'] = '%s: %s' % (type(e).__name__, str(e)[:200])
        saida.append(reg)
        print('%-16s %-18s %-10s %s' % (
            reg['especie_slug'], (reg.get('cultura_rotulo') or '-')[:18],
            reg.get('mecanismo_rotulo', '')[:10], reg['estado']), flush=True)
        time.sleep(1.0)
    with open(os.path.join(AQUI, 'gire_mapas.json'), 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print('\nmapas: %d  lidos: %d' % (
        len(saida), sum(1 for r in saida if r['estado'] == 'LIDO')))


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:                                            # noqa: BLE001
        pass
    main()
