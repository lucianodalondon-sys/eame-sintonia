#!/usr/bin/env python3
"""
CORRIGE O CUSTO DOS MANIFESTOS — porque o coletor leu antes de a plataforma fechar.

O QUE ACONTECEU, MEDIDO
------------------------
`coletor` grava `COST_USD` lendo `usageTotalUsd` do objeto de run devolvido pelo
`waitForFinish`. Nesse instante a Apify ainda não fechou a conta da execução, e o campo
vem **0**. Os artefatos ficaram assim:

    VIDEOS-C   COST_USD 0.0000   real 1.1920
    VIDEOS-D   COST_USD 0.0000   real 1.5800
    COMENTARIOS-C  0.6220        real 0.6700
    COMENTARIOS-D  0.2820        real 1.4820
    TRANSCRICOES-C/D  0.0000     real 0.1200

    CUSTO ANUNCIADO 0.9040 · CUSTO REAL 5.0440 · 5,6x

    CUSTO LIDO CEDO DEMAIS NÃO É CUSTO ZERO.

É a mesma família do erro que o `apify_pool` já documenta para a cota ("cota esgotada se
apresenta como sucesso"): a plataforma responde com uma verdade parcial, e ler cedo demais
transforma verdade parcial em número errado.

O QUE ESTE ARQUIVO FAZ
-----------------------
Relê o custo em `GET /v2/actor-runs` (leitura, não execução — funciona mesmo com a chave
esgotada), casa por `DATASET_ID`, e reescreve `COST_USD` nos manifestos e nos artefatos.
O valor lido cedo fica preservado em `COST_USD_AT_WRITE_TIME` — apagar o erro apagaria a
prova de que ele existe.
"""
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'SENSOR-PILOT')


def _runs_reais(token):
    """DATASET_ID -> (usd, status). GET não é execução: não gasta e não precisa de saldo."""
    req = urllib.request.Request(
        'https://api.apify.com/v2/actor-runs?limit=200&desc=true',
        headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.load(r)
    fora = {}
    for it in d.get('data', {}).get('items', []):
        ds = it.get('defaultDatasetId')
        if ds:
            fora[ds] = (float(it.get('usageTotalUsd') or 0.0), it.get('status'))
    return fora


def corrigir(token):
    reais = _runs_reais(token)
    print('runs lidos na plataforma: %d' % len(reais))
    total_antes = total_depois = 0.0
    for lote in ('A', 'B', 'C', 'D'):
        cam = os.path.join(SAIDA, 'RUNS-%s.json' % lote)
        if not os.path.exists(cam):
            continue
        with open(cam, encoding='utf-8') as f:
            man = json.load(f)
        mudou = 0
        por_run = {}
        for r in man.get('RUNS', []):
            ds = r.get('DATASET_ID')
            # `NOT_PRESERVED` é um ESTADO, não um número: significa que o campo existiu na
            # execução e não foi capturado. Somar como 0 apagaria a diferença entre
            # "custou zero" e "não sei quanto custou".
            bruto = r.get('COST_USD')
            antes = float(bruto) if isinstance(bruto, (int, float)) else 0.0
            total_antes += antes
            if ds in reais:
                usd, st = reais[ds]
                if abs(usd - antes) > 1e-9:
                    r['COST_USD_AT_WRITE_TIME'] = antes
                    r['COST_USD'] = round(usd, 6)
                    r['COST_STATE'] = 'RESETTLED_FROM_PLATFORM'
                    r['PLATFORM_STATUS_AT_SETTLEMENT'] = st
                    mudou += 1
                total_depois += usd
            else:
                r['COST_STATE'] = 'NOT_RESETTLED_RUN_NOT_LISTED'
                total_depois += antes
            fin = r.get('COST_USD')
            por_run[r['RUN_ID']] = float(fin) if isinstance(fin, (int, float)) else 0.0
        man['COST_CORRECTION'] = {
            'WHY': ('COST_USD foi lido antes de a plataforma fechar a conta da execução '
                    'e veio 0. CUSTO LIDO CEDO DEMAIS != CUSTO ZERO.'),
            'CORRECTED_AT': '2026-09-02',
            'METHOD': 'GET /v2/actor-runs, casamento por DATASET_ID',
            'RUNS_CORRECTED': mudou,
            'ORIGINAL_VALUE_PRESERVED_IN': 'COST_USD_AT_WRITE_TIME',
        }
        with open(cam, 'w', encoding='utf-8') as f:
            json.dump(man, f, ensure_ascii=False, indent=1)
        print('  RUNS-%s.json: %d runs corrigidos' % (lote, mudou))

        # e os artefatos que somam esses runs
        for nome in ('VIDEOS-%s.json', 'TRANSCRICOES-%s.json', 'COMENTARIOS-%s.json',
                     'CANAIS-%s.json'):
            cam2 = os.path.join(SAIDA, nome % lote)
            if not os.path.exists(cam2):
                continue
            with open(cam2, encoding='utf-8') as f:
                art = json.load(f)
            ids = art.get('RUN_IDS') or []
            novo = round(sum(por_run.get(i, 0.0) for i in ids), 6)
            vb = art.get('COST_USD')
            velho = float(vb) if isinstance(vb,(int,float)) else 0.0
            if abs(novo - velho) > 1e-9:
                art['COST_USD_AT_WRITE_TIME'] = velho
                art['COST_USD'] = novo
                art['COST_STATE'] = 'RESETTLED_FROM_PLATFORM'
                with open(cam2, 'w', encoding='utf-8') as f:
                    json.dump(art, f, ensure_ascii=False, indent=1)
                print('     %s: %.4f -> %.4f USD' % (nome % lote, velho, novo))
    print('\nsoma dos manifestos: antes %.4f · depois %.4f USD'
          % (total_antes, total_depois))
    return 0


if __name__ == '__main__':
    tk = os.environ.get('APIFY_TOKEN_POOL', '').split(',')[0].strip()
    if not tk:
        print('SEM_TOKEN — exporte APIFY_TOKEN_POOL'); sys.exit(1)
    sys.exit(corrigir(tk))
