#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1 · O CONTRATO DE GEOGRAFIA, medido sobre o pacote inteiro.

    python3 scripts/v21_geografia_contrato.py

    PROVINCIAL != REGIONAL.

Esta lei já estava escrita em dois lugares — no cabeçalho do arquivo que a
quebrava e nos 73 registros da fonte, que declaram «boletim provincial NAO
representa a regiao». Estava escrita e não era medida.

    LEI QUE NINGUÉM MEDE É COMENTÁRIO.

Este arquivo transforma a lei em contador. Ele FALHA (código 1) se qualquer
violação aparecer, para que a cadeia pare em vez de publicar.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_normalizar as N  # noqa: E402

PROMOVIVEIS = ('PROVINCIAL', 'AREALE', 'ESTACAO', 'PIAZZA', 'GRADE_DE_MODELO')


def colecoes():
    for a in sorted(os.listdir(ING)):
        if not a.endswith('.json') or a in ('APP-MANIFEST.json',
                                            'CANONICAL-INTELLIGENCE-MASTER.json'):
            continue
        d = json.load(open(os.path.join(ING, a), encoding='utf-8'))
        if isinstance(d, dict) and isinstance(d.get('RECORDS'), list):
            yield a, d['RECORDS']


def main():
    v = {'PAR_DE_REGIOES_SEM_DOCUMENTO': [], 'PROVINCIA_PROMOVIDA': [],
         'ESCOPO_REGIONAL_COM_PROVINCIA_NO_TITULO': [],
         'PROVINCIA_SEM_REGIAO_CONTINENTE': [], 'ID_DE_PROVINCIA_DUPLICADO': []}
    checados = idx = 0
    todos = {}
    for arq, recs in colecoes():
        for r in recs:
            todos[r.get('ID')] = r
            if not (r.get('REGION_IDS') or r.get('PROVINCE_IDS')):
                continue
            checados += 1
            provs = r.get('PROVINCE_IDS') or []
            regs = r.get('REGION_IDS') or []
            esc = r.get('GEOGRAPHIC_SCOPE')

            # 1 · província promovida: escopo específico dizendo que fala pela região
            if esc in PROMOVIVEIS and r.get('REGION_REPRESENTS') is True:
                v['PROVINCIA_PROMOVIDA'].append(f"{arq}:{r.get('ID')}")

            # 2 · província cujo continente não está declarado
            for p in provs:
                pai = N.PROVINCIA_ALIAS.get(p, {}).get('regiao')
                if pai and pai not in regs:
                    v['PROVINCIA_SEM_REGIAO_CONTINENTE'].append(
                        f"{arq}:{r.get('ID')} {p} fora de {pai}")

            # 3 · o mesmo ID de província contado duas vezes
            if len(provs) != len(set(provs)):
                v['ID_DE_PROVINCIA_DUPLICADO'].append(f"{arq}:{r.get('ID')}")

            # 4 · duas regiões sem que o documento nomeie as duas
            if len(regs) > 1 and not provs:
                titulo = ' '.join(str(r.get(k) or '') for k in
                                  ('BULLETIN_TITLE', 'NAME', 'TITLE'))
                url = ' '.join(r.get('SOURCE_URLS') or [])
                g = N.geografia(titulo, url)
                if g['REGION_IDS'] and sorted(g['REGION_IDS']) != sorted(regs):
                    v['PAR_DE_REGIOES_SEM_DOCUMENTO'].append(
                        f"{arq}:{r.get('ID')} declara {regs}, o documento prova {g['REGION_IDS']}")

            # 5 · escopo REGIONAL com nome de província no próprio título
            if esc == 'REGIONAL':
                titulo = str(r.get('BULLETIN_TITLE') or r.get('NAME') or '')
                if N.province_ids(titulo):
                    v['ESCOPO_REGIONAL_COM_PROVINCIA_NO_TITULO'].append(
                        f"{arq}:{r.get('ID')} {N.province_ids(titulo)}")

    # 6 · o cruzamento não pode alegar mais do que o apoio mais fraco
    cx = os.path.join(ING, 'CLIENT-SAFE-CROSSINGS.json')
    cruz_ruins = []
    if os.path.exists(cx):
        for x in json.load(open(cx, encoding='utf-8'))['RECORDS']:
            idx += 1
            alegado = x.get('GEOGRAPHIC_CLAIM_SCOPE')
            sup = x.get('SUPPORTING_IDS') or {}
            ids = [i for val in (sup.values() if isinstance(sup, dict) else [sup])
                   for i in (val if isinstance(val, list) else [val])]
            for i in ids:
                a = todos.get(i, {})
                if a.get('GEOGRAPHIC_SCOPE') in PROMOVIVEIS and alegado in ('REGIONAL', 'NACIONAL'):
                    cruz_ruins.append(f"{x['ID']} alega {alegado} sobre {i}")
                if a.get('REGION_REPRESENTS') is False and alegado in ('REGIONAL', 'NACIONAL'):
                    cruz_ruins.append(f"{x['ID']} alega {alegado} sobre {i} (nao representa)")
    v['CRUZAMENTO_ALEGA_MAIS_QUE_O_APOIO'] = cruz_ruins

    total = sum(len(x) for x in v.values())
    print('== R1 · CONTRATO DE GEOGRAFIA ==')
    print(f'  registros com geografia checados : {checados}')
    print(f'  cruzamentos checados             : {idx}')
    for k, val in v.items():
        print(f'  {k:44s}: {len(val)}')
        for ex in val[:4]:
            print(f'      {ex}')
    print(f'\n  VIOLACOES: {total}')
    destino = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                           'GEOGRAPHY-CONTRACT.json')
    json.dump({'CHECADOS': checados, 'CRUZAMENTOS': idx, 'VIOLACOES': total,
               'DETALHE': v}, open(destino, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'  gravado: {destino}')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
