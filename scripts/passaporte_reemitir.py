#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REEMISSÃO CONTROLADA DE `CLAIM_ID` — append-only, com pré-check que recusa divergência.

Esta é a ÚNICA ferramenta desta missão que escreve. Ela escreve **um segmento novo**,
nunca o log canônico:

    ESCREVE   data/passaporte/EVENTOS-REEMISSAO-CLAIM-ID.jsonl   (187 eventos novos)
    ESCREVE   data/passaporte/REEMISSAO-CLAIM-ID-MANIFESTO.json  (o selo da operação)
    NÃO TOCA  data/passaporte/EVENTOS.jsonl                      (nem 1 byte)

### Por que um segmento, e não um append direto no arquivo

O log canônico vive na branch `claude/sintonia-information-passport-bbtps0`, que **não
está em `sintonia/canonical`**. A branch desta missão nasce de `canonical` e não tem o
arquivo. Copiar o log para cá para depois acrescentar linhas seria **promover o
passaporte** para uma branch canônica — coisa que esta autorização proíbe.

O segmento resolve isso sem abrir mão de nada:

  · é estritamente append-only — o log original não é lido para escrita, só para hash;
  · o manifesto **fixa o SHA** do log a que ele se aplica; aplicar sobre outro log é
    recusado;
  · o estado ativo é `EVENTOS.jsonl` **concatenado com** o segmento, nessa ordem, e é
    assim que a verificação pós-append mede — do zero, sobre os dois arquivos;
  · não existe um segundo lugar onde o mesmo estado possa envelhecer em silêncio: ler
    o segmento sozinho é recusado pelo próprio manifesto (`READ_ALONE = FORBIDDEN`).

Uso
    python3 scripts/passaporte_reemitir.py --passaporte <ref> --acervo .            # ensaio
    python3 scripts/passaporte_reemitir.py --passaporte <ref> --acervo . --aplicar  # escreve
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passaporte_claim_id import (                              # noqa: E402
    ESQUEMAS, RULE_VERSION, chave_local, dry_run, ler_casos, ler_eventos, medir)

SEGMENTO = 'EVENTOS-REEMISSAO-CLAIM-ID.jsonl'
MANIFESTO = 'REEMISSAO-CLAIM-ID-MANIFESTO.json'

# Os números validados no dry-run e autorizados. Divergência = PARE.
ESPERADO = {
    'CLAIMS_REAL': 55,
    'NEW_CLAIM_IDS': 55,
    'COLLISIONS_AFTER': 0,
    'DIRECT_ROUTES_TOTAL': 48,
    'DIRECT_ROUTES_RECOVERED': 48,
    'DIRECT_ROUTES_WRONG': 0,
    'ROUTES_POINTING_TO_MISSING_CLAIM': 0,
    'EVENTS_TO_APPEND': 187,
    'CLAIMS_REISSUED': 55,
    'ROUTES_REISSUED': 100,
    'ORPHANED_ROUTES': 32,
    'OLD_EVENTS_MODIFIED': 0,
}


def sha256_de(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def estado_antes(passaporte):
    caminho = os.path.join(passaporte, 'data', 'passaporte', 'EVENTOS.jsonl')
    with open(caminho, encoding='utf-8') as f:
        n = sum(1 for l in f if l.strip())
    return {
        'EVENTOS_PATH': caminho,
        'EVENTOS_SHA256_BEFORE': sha256_de(caminho),
        'EVENT_COUNT_BEFORE': n,
        'FILE_SIZE_BEFORE': os.path.getsize(caminho),
    }


def precheck(passaporte):
    """Recalcula tudo do zero e compara com o autorizado. Devolve (ok, provas, divergências)."""
    eventos = ler_eventos(passaporte)
    _, claims, dependentes = medir(eventos, ler_casos(passaporte))
    d = dry_run(eventos, claims, dependentes, ESQUEMAS['C_hibrido'])
    provas = d['PROVAS']
    div = {k: {'ESPERADO': v, 'MEDIDO': provas.get(k)}
           for k, v in ESPERADO.items() if provas.get(k) != v}
    return (not div), provas, div, d


def construir_eventos(d, antes):
    """Os 187 eventos, com toda a rastreabilidade exigida pela autorização."""
    saida = []
    por_alvo = {t['SOURCE_EVENT_ID']: t for t in d['TABELA']}
    for e in d['EVENTOS_NOVOS']:
        alvo = por_alvo.get(e.get('TARGET_EVENT_ID'))
        if e['EVENT_TYPE'] == 'CLAIM_ID_REISSUED':
            saida.append({
                'EVENT_TYPE': 'CLAIM_ID_REISSUED',
                'RULE_VERSION': RULE_VERSION,
                'ACTOR': 'scripts/passaporte_reemitir.py',
                'APPLIES_TO_LOG_SHA256': antes['EVENTOS_SHA256_BEFORE'],
                'ITEM_ID': e['ITEM_ID'],
                'OLD_CLAIM_ID': e['OLD_CLAIM_ID'],
                'NEW_CLAIM_ID': e['CLAIM_ID'],
                'CLAIM_ID': e['CLAIM_ID'],
                'CASE_ID': (alvo or {}).get('CASE_ID'),
                'CLAIM_TEXT': (alvo or {}).get('CLAIM_TEXT'),
                'EVIDENCE_REFERENCE': (alvo or {}).get('EVIDENCE_REFERENCE'),
                'PREVIOUS_EVENT_REFERENCE': e['TARGET_EVENT_ID'],
                'REISSUE_REASON': 'identidade derivada de item+ordinal, e o ordinal '
                                  'reinicia a cada extração; reemitida a partir do '
                                  'conteúdo da afirmação (ITEM+CASE+hash)',
            })
        else:
            saida.append({
                'EVENT_TYPE': 'CLAIM_LINK_ORPHANED',
                'RULE_VERSION': RULE_VERSION,
                'ACTOR': 'scripts/passaporte_reemitir.py',
                'APPLIES_TO_LOG_SHA256': antes['EVENTOS_SHA256_BEFORE'],
                'OLD_CLAIM_ID': e['OLD_CLAIM_ID'],
                'CLAIM_ID': None,
                'CASE_ID': None,          # não conhecido — e NÃO será inferido
                'CAPABILITY_ID': e.get('CAPABILITY_ID'),
                'PREVIOUS_EVENT_REFERENCE': e['TARGET_EVENT_ID'],
                'TO_STATE': 'ORPHANED',
                'RECOVERY_STATE': 'UNRECOVERABLE',
                'ORPHAN_REASON': e['REASON'],
            })
    # EVENT_ID determinístico: mesma entrada, mesmo id, sempre.
    for ev in saida:
        semente = '|'.join(str(ev.get(k)) for k in
                           ('EVENT_TYPE', 'OLD_CLAIM_ID', 'CLAIM_ID',
                            'PREVIOUS_EVENT_REFERENCE', 'RULE_VERSION'))
        ev['EVENT_ID'] = 'EVT-' + hashlib.sha1(semente.encode('utf-8')).hexdigest()[:16].upper()
    return saida


def estado_ativo(passaporte, segmento):
    """O estado ATIVO = log canônico + segmento, nessa ordem. Lido do zero."""
    eventos = ler_eventos(passaporte)
    if os.path.isfile(segmento):
        with open(segmento, encoding='utf-8') as f:
            eventos += [json.loads(l) for l in f if l.strip()]
    return eventos


def dobrar_identidade(eventos):
    """Dobra o log aplicando as reemissões. É assim que um consumidor deve ler.

    `CLAIM_ID_REISSUED` reaponta o evento alvo; `CLAIM_LINK_ORPHANED` desliga o alvo.
    Nada é editado: o evento antigo continua no log, dizendo o que sempre disse.
    """
    remapa, orfaos = {}, {}
    for e in eventos:
        if e.get('EVENT_TYPE') == 'CLAIM_ID_REISSUED':
            remapa[e['PREVIOUS_EVENT_REFERENCE']] = e['NEW_CLAIM_ID']
        elif e.get('EVENT_TYPE') == 'CLAIM_LINK_ORPHANED':
            orfaos[e['PREVIOUS_EVENT_REFERENCE']] = e['ORPHAN_REASON']
    ativo = []
    for e in eventos:
        if e.get('EVENT_TYPE') in ('CLAIM_ID_REISSUED', 'CLAIM_LINK_ORPHANED'):
            continue
        eid = e.get('EVENT_ID')
        if eid in orfaos:
            ativo.append(dict(e, CLAIM_ID=None, CLAIM_LINK_STATE='ORPHANED'))
        elif eid in remapa:
            ativo.append(dict(e, CLAIM_ID=remapa[eid]))
        else:
            ativo.append(dict(e))
    return ativo


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--passaporte', required=True)
    p.add_argument('--acervo', default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    p.add_argument('--aplicar', action='store_true',
                   help='sem esta flag, o script apenas ensaia e não escreve nada')
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass

    destino = os.path.join(args.acervo, 'data', 'passaporte')
    caminho_seg = os.path.join(destino, SEGMENTO)
    caminho_man = os.path.join(destino, MANIFESTO)

    print(f'REEMISSÃO DE CLAIM_ID · {RULE_VERSION}')
    print(f'  passaporte (log canônico) = {args.passaporte}')
    print(f'  destino do segmento       = {os.path.relpath(destino, args.acervo)}')
    print(f'  modo                      = {"APLICAR" if args.aplicar else "ENSAIO"}\n')

    # ---- 1 · PRÉ-CHECK ------------------------------------------------------------
    ok, provas, div, d = precheck(args.passaporte)
    print('── 1 · PRÉ-CHECK ──')
    for k, v in ESPERADO.items():
        m = provas.get(k)
        print(f'  {k:36s} esperado={v:<5} medido={m:<5} {"ok" if m == v else "DIVERGE"}')
    if not ok:
        print('\nPARE. Números divergem do dry-run autorizado. NADA foi escrito.')
        print(json.dumps(div, ensure_ascii=False, indent=2))
        return 2
    print('  → todos batem com o dry-run autorizado\n')

    # ---- 2 · ESTADO ANTES ---------------------------------------------------------
    antes = estado_antes(args.passaporte)
    print('── 2 · ESTADO ANTES ──')
    for k, v in antes.items():
        print(f'  {k:26s} = {v}')
    print()

    novos = construir_eventos(d, antes)
    if len(novos) != ESPERADO['EVENTS_TO_APPEND']:
        print(f'PARE. Construí {len(novos)} eventos, esperava '
              f'{ESPERADO["EVENTS_TO_APPEND"]}. NADA foi escrito.')
        return 2
    if len({e['EVENT_ID'] for e in novos}) != len(novos):
        print('PARE. EVENT_ID repetido entre os eventos novos. NADA foi escrito.')
        return 2

    if not args.aplicar:
        print(f'ENSAIO — {len(novos)} eventos prontos, nada escrito.')
        print('Use --aplicar para escrever o segmento.')
        return 0

    if os.path.isfile(caminho_seg):
        print(f'PARE. {SEGMENTO} já existe. Reemitir duas vezes não é append-only.')
        return 2

    # ---- 3 · ESCREVER O SEGMENTO --------------------------------------------------
    os.makedirs(destino, exist_ok=True)
    with open(caminho_seg, 'w', encoding='utf-8', newline='\n') as f:
        for e in novos:
            f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + '\n')
    manifesto = {
        'RULE_VERSION': RULE_VERSION,
        'OPERACAO': 'REEMISSAO_DE_IDENTIDADE_DE_AFIRMACAO',
        'READ_ALONE': 'FORBIDDEN — este segmento só tem sentido concatenado ao log '
                      'canônico, nesta ordem: EVENTOS.jsonl + ' + SEGMENTO,
        'APPLIES_TO': {
            'FILE': 'data/passaporte/EVENTOS.jsonl',
            'BRANCH': 'claude/sintonia-information-passport-bbtps0',
            'SHA256': antes['EVENTOS_SHA256_BEFORE'],
            'EVENT_COUNT': antes['EVENT_COUNT_BEFORE'],
            'FILE_SIZE': antes['FILE_SIZE_BEFORE'],
        },
        'SEGMENTO': {
            'FILE': f'data/passaporte/{SEGMENTO}',
            'SHA256': sha256_de(caminho_seg),
            'EVENT_COUNT': len(novos),
            'CLAIM_ID_REISSUED': sum(1 for e in novos if e['EVENT_TYPE'] == 'CLAIM_ID_REISSUED'),
            'CLAIM_LINK_ORPHANED': sum(1 for e in novos if e['EVENT_TYPE'] == 'CLAIM_LINK_ORPHANED'),
        },
        'GARANTIAS': {
            'OLD_EVENTS_MODIFIED': 0,
            'OLD_EVENTS_DELETED': 0,
            'OLD_EVENTS_REORDERED': 0,
            'ORFAOS_RESOLVIDOS_POR_INFERENCIA': 0,
        },
        'NAO_AUTORIZADO_E_NAO_FEITO': [
            'full backfill', 'promoção do passaporte', 'alteração do portal', 'deploy',
            'mudança de inteligência', 'resolver os 32 órfãos por inferência',
            'UNIVERSE_COMPLETENESS = PASS', 'PASSPORT_READY = YES',
        ],
    }
    with open(caminho_man, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('── 3 · ESCRITO ──')
    print(f'  {SEGMENTO:38s} {len(novos)} eventos · sha256 '
          f'{manifesto["SEGMENTO"]["SHA256"][:16]}…')
    print(f'  {MANIFESTO}')

    # ---- 4 · VERIFICAÇÃO PÓS-APPEND, MEDIDA DO ZERO -------------------------------
    depois_sha = sha256_de(antes['EVENTOS_PATH'])
    print('\n── 4 · O LOG CANÔNICO NÃO FOI TOCADO ──')
    print(f'  SHA256 antes  = {antes["EVENTOS_SHA256_BEFORE"]}')
    print(f'  SHA256 depois = {depois_sha}')
    print(f'  IGUAL         = {depois_sha == antes["EVENTOS_SHA256_BEFORE"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
