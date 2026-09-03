#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2 · O CONTRATO DE PROCEDÊNCIA, medido sobre o pacote inteiro.

    python3 scripts/v21_procedencia_contrato.py

    O CARIMBO NÃO PODE PROMETER O QUE O REGISTRO NÃO TEM.

O defeito que este contrato impede de voltar: 2.217 registros client-safe
mostravam na tela «record acquisito da fonte pubblica identificata, con URL e
data» tendo `SOURCE_URLS` vazio e `REFERENCE_DATE` nulo.

Falha com código 1 se qualquer violação aparecer.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SENT = ('SRC_NAO_DECLARADA', 'SRC_DESCONHECIDA')

# Trechos que, em qualquer língua do pacote, PROMETEM endereço e data.
PROMETE = ('com URL e data', 'con URL e data', 'with URL and date',
           'com fonte e data', 'con fonte e data', 'with source and date')


def colecoes():
    for a in sorted(os.listdir(ING)):
        if not a.endswith('.json') or a in ('APP-MANIFEST.json',
                                            'CANONICAL-INTELLIGENCE-MASTER.json'):
            continue
        d = json.load(open(os.path.join(ING, a), encoding='utf-8'))
        if isinstance(d, dict) and isinstance(d.get('RECORDS'), list):
            yield a, d['RECORDS']


def main():
    v = {'CARIMBO_PROMETE_URL_QUE_NAO_EXISTE': [],
         'SENTINELA_SEM_ESTADO_DECLARADO': [],
         'FONTE_CITADA_SEM_CADASTRO': [],
         'URL_DO_EDITOR_EM_SOURCE_URLS': [],
         'RECUPERADO_SEM_DIZER_COMO': []}
    todos = {}
    fontes = json.load(open(os.path.join(ING, 'SOURCES.json'), encoding='utf-8'))
    idx = set()
    for r in fontes['RECORDS']:
        for k in [r.get('ID'), r.get('ID_ANTERIOR')] + list(r.get('ID_ALIASES') or []):
            if k:
                idx.add(k)

    n = 0
    for arq, recs in colecoes():
        for r in recs:
            todos[r.get('ID')] = r
            n += 1
            tem_url = bool(r.get('SOURCE_URLS'))
            tem_data = r.get('REFERENCE_DATE') not in (None, '')
            textos = ' '.join(str(r.get(k) or '') for k in r
                              if k.startswith('EVIDENCE_STATUS_WHY'))
            promete = any(p in textos for p in PROMETE)

            # 1 · o carimbo promete endereço e data que o registro não tem
            if promete and not (tem_url and tem_data):
                v['CARIMBO_PROMETE_URL_QUE_NAO_EXISTE'].append(
                    f"{arq}:{r.get('ID')} url={tem_url} data={tem_data}")

            # 2 · sentinela tem de declarar o próprio estado
            if (r.get('SOURCE_IDS') or []) and all(s in SENT for s in r['SOURCE_IDS']):
                if r.get('PROVENANCE_STATE') != 'UNRECOVERABLE':
                    v['SENTINELA_SEM_ESTADO_DECLARADO'].append(f"{arq}:{r.get('ID')}")

            # 3 · toda fonte citada tem de existir
            for s in (r.get('SOURCE_IDS') or []):
                if s not in idx and s not in SENT:
                    v['FONTE_CITADA_SEM_CADASTRO'].append(f"{arq}:{r.get('ID')} {s}")

            # 4 · o endereço do editor nunca entra como endereço do item
            if r.get('PROVENANCE_RECOVERED_VIA') == 'LEGACY_SOURCE_ID' and tem_url:
                v['URL_DO_EDITOR_EM_SOURCE_URLS'].append(f"{arq}:{r.get('ID')}")

            # 5 · quem foi religado tem de dizer por onde
            if r.get('PROVENANCE_STATE') == 'RECOVERED' and not r.get('PROVENANCE_RECOVERED_VIA'):
                v['RECUPERADO_SEM_DIZER_COMO'].append(f"{arq}:{r.get('ID')}")

    total = sum(len(x) for x in v.values())
    print('== R2 · CONTRATO DE PROCEDENCIA ==')
    print(f'  registros checados : {n}')
    for k, val in v.items():
        print(f'  {k:38s}: {len(val)}')
        for ex in val[:4]:
            print(f'      {ex}')
    print(f'\n  VIOLACOES: {total}')
    destino = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                           'PROVENANCE-CONTRACT.json')
    json.dump({'CHECADOS': n, 'VIOLACOES': total, 'DETALHE': v},
              open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  gravado: {destino}')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
