#!/usr/bin/env python3
"""
RECUPERAR execuções JÁ PAGAS. Nenhum Actor é iniciado aqui.

A rodada anterior gastou 8 execuções e não conseguiu ler nada — não porque a
plataforma falhou, mas porque o RAW ficou dentro do runner do Actions, que foi
destruído. A cicatriz do Brasil, aplicada:

    DINHEIRO GASTO ≠ DADO PRESERVADO

Um run pago só vira ativo quando há **identidade de execução + output
recuperável**. Sem `RUN_ID` e `DATASET_ID` persistidos, o que se comprou some
junto com a máquina.

O QUE ESTE ARQUIVO FAZ, E O QUE ELE SE PROÍBE
-----------------------------------------------
Faz só três chamadas, todas de LEITURA:

    GET /v2/actor-runs            lista as execuções da conta
    GET /v2/actor-runs/{id}       metadados de uma execução
    GET /v2/datasets/{id}/items   o output que já foi pago

**Não existe POST neste arquivo.** Iniciar Actor é o que se está tentando
evitar, e a garantia não pode depender de eu lembrar: há teste que varre o
código-fonte atrás de qualquer método que não seja GET.

A ORDEM É INEGOCIÁVEL
----------------------
    PAID_RESULT → RAW_PRESERVED → PARSED → INTERPRETED

Nunca mais `PAID_RESULT → PARSED → RAW LOST`. O RAW é gravado com SHA-256
ANTES de qualquer tentativa de entender o conteúdo, e o schema é lido do que
está em disco, não do que está em memória.

E O SCHEMA É OBSERVADO, NÃO ADIVINHADO
---------------------------------------
`esqueleto()` devolve apenas a ESTRUTURA — nomes de campo, tipos, aninhamento —
sem valores. É o que vai para o log, para que dê para desenhar o parser sem
baixar artefato e sem expor conteúdo de perfil de ninguém.
"""
import datetime
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap  # noqa: E402

API = 'https://api.apify.com/v2'
RAW_DIR = os.path.join(ROOT, 'data', 'samples', 'raw-paid')
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-LINKEDIN-RECOVERY.json')


def _get(caminho, token, params=None):
    """SOMENTE GET. Nenhum POST existe neste arquivo, e há teste que prova."""
    url = API + caminho
    if params:
        url += '?' + '&'.join('%s=%s' % (k, v) for k, v in params.items())
    cmd = ['curl', '-sS', '-G', '-H', 'Authorization: Bearer %s' % token, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(ap.redigir('curl falhou: %s' % r.stderr[:200]))
    try:
        return json.loads(r.stdout)
    except ValueError as e:
        raise ValueError(ap.redigir('json invalido: %s' % e))


def esqueleto(o, prof=0, max_prof=4):
    """Só a ESTRUTURA: nome de campo, tipo, aninhamento. Nenhum valor."""
    if prof > max_prof:
        return '...'
    if isinstance(o, dict):
        return {k: esqueleto(v, prof + 1, max_prof) for k, v in sorted(o.items())}
    if isinstance(o, list):
        return ['list[%d] de %s' % (len(o), esqueleto(o[0], prof + 1, max_prof))] if o else 'list[0]'
    if isinstance(o, str):
        return 'str(%d)' % len(o)
    if o is None:
        return 'null'
    return type(o).__name__


def preservar(run_id, itens):
    """RAW com hash, ANTES de interpretar. Devolve (caminho, sha256, bytes)."""
    os.makedirs(RAW_DIR, exist_ok=True)
    nome = '%s.raw.json.gz' % re.sub(r'[^A-Za-z0-9_.-]', '-', run_id)
    caminho = os.path.join(RAW_DIR, nome)
    corpo = json.dumps(itens, ensure_ascii=False, sort_keys=True).encode('utf-8')
    with gzip.open(caminho, 'wb', compresslevel=9) as f:
        f.write(corpo)
    with open(caminho, 'rb') as f:
        disco = f.read()
    return ('data/samples/raw-paid/' + nome,
            hashlib.sha256(corpo).hexdigest(), len(disco))


def recuperar(token, limite=30):
    runs = _get('/actor-runs', token,
                {'limit': limite, 'desc': 'true'}).get('data', {}).get('items', [])
    fora = []
    for r in runs:
        rid = r.get('id')
        ds = r.get('defaultDatasetId')
        reg = {
            'ACTOR_RUN_ID': rid,
            'ACTOR_ID': r.get('actId'),
            'DATASET_ID': ds,
            'KEY_VALUE_STORE_ID': r.get('defaultKeyValueStoreId'),
            'REQUEST_QUEUE_ID': r.get('defaultRequestQueueId'),
            'STATUS': r.get('status'),
            'STATUS_MESSAGE': (r.get('statusMessage') or '')[:200],
            'STARTED_AT': r.get('startedAt'),
            'FINISHED_AT': r.get('finishedAt'),
            'BUILD_NUMBER': r.get('buildNumber'),
            'COST': (r.get('usageTotalUsd') if r.get('usageTotalUsd') is not None
                     else 'NOT_MEASURED'),
        }
        if not ds:
            reg['ITEMS'] = 0
            reg['RECOVERY_STATE'] = 'NO_DATASET'
            fora.append(reg)
            continue
        try:
            itens = _get('/datasets/%s/items' % ds, token, {'clean': 'false'})
        except Exception as e:
            reg['ITEMS'] = 0
            reg['RECOVERY_STATE'] = 'DATASET_READ_FAILED'
            reg['ERROR'] = ap.redigir(str(e))[:200]
            fora.append(reg)
            continue
        itens = itens if isinstance(itens, list) else []
        caminho, sha, nbytes = preservar(rid, itens)
        reg.update({
            'ITEMS': len(itens),
            'RAW_PATH': caminho, 'RAW_SHA256': sha, 'RAW_BYTES': nbytes,
            'RAW_PRESERVED': 'YES',
            'RECOVERY_STATE': 'RECOVERED' if itens else 'RECOVERED_EMPTY',
            'ITEM_SCHEMA': esqueleto(itens[0]) if itens else None,
        })
        fora.append(reg)
    return fora


def main():
    censo = ap.censo()
    out = {
        'SOURCE_ID': 'DERIVED/IT-LINKEDIN-RECOVERY',
        'source': 'recuperacao de execucoes JA PAGAS na Apify — nenhum Actor iniciado',
        'SOURCE_LOCATION': 'Apify', 'FACT_LOCATION': 'n/a — metadado de coleta',
        'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_RAW',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'NEW_ACTOR_RUNS': 0,
        'LAW': 'DINHEIRO GASTO ≠ DADO PRESERVADO',
        'ORDER_ENFORCED': 'PAID_RESULT → RAW_PRESERVED → PARSED → INTERPRETED',
        'POOL': censo,
        'TOKEN_VALUE_LOGGED': 'NO', 'TOKEN_VALUE_COMMITTED': 'NO',
    }
    ks = ap.pool()
    if not ks:
        out['PAID_RUNS_RECOVERABLE'] = 'NOT_MEASURED'
        out['STATE'] = 'APIFY_ENV_MISSING'
        print('APIFY_ENV_MISSING'); _grava(out); return

    pos, regs, erro = 0, [], None
    while pos < len(ks):
        try:
            regs = recuperar(ks[pos])
            break
        except Exception as e:
            est = ap.classificar(excecao=e)
            erro = {'POOL_POSITION': pos + 1, 'STATE': est,
                    'ERROR': ap.redigir(str(e))[:200]}
            if est in ap.ROTACIONAM:
                pos += 1
                continue
            break                                   # parser/bug meu nao gasta chave

    rec = [r for r in regs if r.get('RECOVERY_STATE', '').startswith('RECOVERED')]
    out.update({
        'POOL_POSITION_USED': pos + 1,
        'PAID_RUNS_RECOVERABLE': 'YES' if rec else 'NO',
        'RUNS_LISTED': len(regs), 'RUNS_RECOVERED': len(rec),
        'ITEMS_RECOVERED': sum(r.get('ITEMS', 0) for r in rec),
        'RAW_PRESERVED': 'YES' if rec else 'NO',
        'COST_RECOVERED': ('MEASURED' if any(r.get('COST') != 'NOT_MEASURED' for r in rec)
                           else 'NOT_MEASURED'),
        'RUNS': regs, 'ERROR': erro,
        'STATE': 'RECOVERED' if rec else 'NOTHING_RECOVERED',
    })
    _grava(out)
    print('PAID_RUNS_RECOVERABLE =', out['PAID_RUNS_RECOVERABLE'])
    print('RUNS_LISTED           =', out['RUNS_LISTED'])
    print('RUNS_RECOVERED        =', out['RUNS_RECOVERED'])
    print('ITEMS_RECOVERED       =', out['ITEMS_RECOVERED'])
    print('NEW_ACTOR_RUNS        = 0')
    for r in regs[:12]:
        print('  %-28s %-10s ds=%-20s itens=%-4s custo=%s' % (
            r.get('ACTOR_RUN_ID'), r.get('STATUS'), r.get('DATASET_ID'),
            r.get('ITEMS'), r.get('COST')))
    prim = next((r for r in rec if r.get('ITEM_SCHEMA')), None)
    if prim:
        print('\n=== ESQUELETO DO PRIMEIRO ITEM (so estrutura, sem valores) ===')
        print(json.dumps(prim['ITEM_SCHEMA'], ensure_ascii=False, indent=1)[:3000])


def _grava(out):
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        fh.write(ap.redigir(json.dumps(out, ensure_ascii=False, indent=2)))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
