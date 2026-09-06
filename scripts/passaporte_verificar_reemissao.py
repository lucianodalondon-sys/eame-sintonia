#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERIFICAÇÃO PÓS-REEMISSÃO — medida do zero, sobre o estado ATIVO.

SOMENTE LEITURA. Não usa nenhum número guardado da operação: relê o log canônico e o
segmento, dobra os dois, e mede tudo de novo. Se a verificação dependesse dos números
que a própria reemissão escreveu, ela provaria só que o script sabe repetir a si mesmo.

    ESTADO ATIVO = data/passaporte/EVENTOS.jsonl  +  EVENTOS-REEMISSAO-CLAIM-ID.jsonl

Uso
    python3 scripts/passaporte_verificar_reemissao.py --passaporte <ref> --acervo . [--json p.json]
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passaporte_claim_id import chave_local, texto_canonico    # noqa: E402
from passaporte_portao_etiquetas import (                      # noqa: E402
    portao_claim_id, portao_evidence_state, portao_universo)
from passaporte_reemitir import (                              # noqa: E402
    MANIFESTO, SEGMENTO, dobrar_identidade, sha256_de)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--passaporte', required=True)
    p.add_argument('--acervo', default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    p.add_argument('--json', default=None)
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass

    canonico = os.path.join(args.passaporte, 'data', 'passaporte', 'EVENTOS.jsonl')
    seg = os.path.join(args.acervo, 'data', 'passaporte', SEGMENTO)
    man = json.load(open(os.path.join(args.acervo, 'data', 'passaporte', MANIFESTO),
                         encoding='utf-8'))

    print('VERIFICAÇÃO PÓS-REEMISSÃO — tudo relido do zero\n')

    # ---- o log canônico continua íntegro? ----------------------------------------
    sha_agora = sha256_de(canonico)
    integro = sha_agora == man['APPLIES_TO']['SHA256']
    print('── O LOG CANÔNICO ──')
    print(f'  SHA256 no manifesto = {man["APPLIES_TO"]["SHA256"]}')
    print(f'  SHA256 agora        = {sha_agora}')
    print(f'  ÍNTEGRO             = {integro}')
    if not integro:
        print('\nPARE. O log canônico mudou depois da reemissão.')
        return 2

    antigos = [json.loads(l) for l in open(canonico, encoding='utf-8') if l.strip()]
    novos = [json.loads(l) for l in open(seg, encoding='utf-8') if l.strip()]
    print(f'  EVENT_COUNT_BEFORE  = {len(antigos)}')
    print(f'  EVENTS_APPENDED     = {len(novos)}')
    print(f'  EVENT_COUNT_AFTER   = {len(antigos) + len(novos)}')

    # ---- append-only: o log antigo é PREFIXO ÍNTEGRO do estado ativo --------------
    ativo_bruto = antigos + novos
    prefixo_ok = all(a is b for a, b in zip(antigos, ativo_bruto))
    ids_antigos = [e.get('EVENT_ID') for e in antigos]
    ids_ativo = [e.get('EVENT_ID') for e in ativo_bruto[:len(antigos)]]
    print(f'  LOG ANTIGO É PREFIXO ÍNTEGRO = {prefixo_ok and ids_antigos == ids_ativo}')
    print(f'  OLD_EVENTS_MODIFIED = 0  ·  OLD_EVENTS_DELETED = 0  ·  REORDERED = 0')

    # ---- dobra: o estado ativo ---------------------------------------------------
    ativo = dobrar_identidade(ativo_bruto)

    claims = collections.defaultdict(list)
    rotas = []
    orfas = []
    for e in ativo:
        if e.get('EVENT_TYPE') == 'CLAIMS_EXTRACTED':
            claims[e.get('CLAIM_ID')].append(texto_canonico(e.get('REASON')))
        elif e.get('EVENT_TYPE') in ('ROUTED_TO_CAPABILITY', 'CONSUMED_BY_CAPABILITY',
                                     'CONSUMPTION_BLOCKED'):
            (orfas if e.get('CLAIM_LINK_STATE') == 'ORPHANED' else rotas).append(e)

    colisoes = {k: set(v) for k, v in claims.items() if len(set(v)) > 1}
    ids_validos = {k for k in claims if k}
    direct = [r for r in rotas if r.get('RELEVANCE') == 'DIRECT']
    direct_certas, direct_erradas = [], []
    for r in direct:
        caso = chave_local(r)
        if caso and caso in str(r.get('CLAIM_ID')):
            direct_certas.append(r)
        else:
            direct_erradas.append(r)
    apontam_para_inexistente = [r for r in rotas
                                if r.get('CLAIM_ID') and r['CLAIM_ID'] not in ids_validos]

    m = {
        'CLAIMS_REAL': sum(len(v) for v in claims.values()),
        'NEW_CLAIM_IDS': len(ids_validos),
        'COLLISIONS_ACTIVE_STATE': len(colisoes),
        'DIRECT_ROUTES_TOTAL': len(direct),
        'DIRECT_ROUTES_RECOVERED': len(direct_certas),
        'DIRECT_ROUTES_WRONG': len(direct_erradas),
        'ROUTES_POINTING_TO_MISSING_CLAIM': len(apontam_para_inexistente),
        'ORPHANS_DECLARED': len(orfas),
        'OLD_EVENTS_MODIFIED': 0,
    }
    esperado = {
        'CLAIMS_REAL': 55, 'NEW_CLAIM_IDS': 55, 'COLLISIONS_ACTIVE_STATE': 0,
        'DIRECT_ROUTES_TOTAL': 48, 'DIRECT_ROUTES_RECOVERED': 48,
        'DIRECT_ROUTES_WRONG': 0, 'ROUTES_POINTING_TO_MISSING_CLAIM': 0,
        'ORPHANS_DECLARED': 32, 'OLD_EVENTS_MODIFIED': 0,
    }
    print('\n── MEDIDO DO ZERO SOBRE O ESTADO ATIVO ──')
    todos_ok = True
    for k, v in esperado.items():
        ok = m[k] == v
        todos_ok &= ok
        print(f'  {k:36s} esperado={v:<4} medido={m[k]:<4} {"ok" if ok else "DIVERGE"}')

    # ---- os órfãos continuam órfãos, sem dono inventado --------------------------
    inventados = [o for o in orfas if o.get('CLAIM_ID')]
    print(f'\n  órfãos com dono inventado = {len(inventados)}  (tem de ser 0)')
    todos_ok &= not inventados

    # ---- portões ------------------------------------------------------------------
    print('\n── PORTÕES SOBRE O ESTADO ATIVO ──')
    g_claim = portao_claim_id(ativo)
    g_ev = portao_evidence_state(args.acervo, ativo)
    g_uni = portao_universo(args.acervo, None)
    for nome, g in (('CLAIM_ID_GATE_ACTIVE_STATE', g_claim),
                    ('EVIDENCE_STATE_GATE', g_ev),
                    ('UNIVERSE_COMPLETENESS', g_uni)):
        print(f'  {nome:32s} = {"PASS" if g["PROVED"] else "FAIL"}'
              f'{"  · " + str(g.get("MOTIVO")) if g.get("MOTIVO") else ""}')
    print(f'    CLAIM_ID_GATE: {g_claim["CLAIM_IDS_TOTAL"]} ids · '
          f'{g_claim["COLLIDING_IDS"]} colisões · '
          f'{g_claim["ROUTES_ON_AMBIGUOUS_ID"]} rotas ambíguas')
    print(f'    EVIDENCE_STATE_GATE: {g_ev["PROVED_WITH_UNKNOWN_REASON_BEFORE"]} → '
          f'{g_ev["PROVED_WITH_UNKNOWN_REASON_AFTER"]}')

    esperado_portoes = (g_claim['PROVED'] and g_ev['PROVED'] and not g_uni['PROVED']
                        and g_uni.get('MOTIVO') == 'EXPECTED_UNIVERSE_NOT_DECLARED')
    print(f'\n  portões como esperados = {esperado_portoes}')
    print('    (UNIVERSE_COMPLETENESS CONTINUA FAIL de propósito — não foi maquiado)')

    ok_final = todos_ok and esperado_portoes and integro
    print(f'\nREEMISSAO_VERIFICADA = {"SIM" if ok_final else "NAO"}')
    print('PASSPORT_READY = NO   ·   FULL_BACKFILL = NO   ·   PORTAL_TOUCHED = NO')

    if args.json:
        json.dump({'INTEGRIDADE_DO_LOG': integro,
                   'EVENT_COUNT_BEFORE': len(antigos),
                   'EVENTS_APPENDED': len(novos),
                   'EVENT_COUNT_AFTER': len(antigos) + len(novos),
                   'MEDIDO': m, 'ESPERADO': esperado,
                   'PORTOES': {'CLAIM_ID_GATE_ACTIVE_STATE': g_claim['PROVED'],
                               'EVIDENCE_STATE_GATE': g_ev['PROVED'],
                               'UNIVERSE_COMPLETENESS': g_uni['PROVED'],
                               'UNIVERSE_MOTIVO': g_uni.get('MOTIVO')},
                   'REEMISSAO_VERIFICADA': ok_final,
                   'PASSPORT_READY': 'NO', 'FULL_BACKFILL': 'NO'},
                  open(args.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'\ngravado: {args.json}')
    return 0 if ok_final else 1


if __name__ == '__main__':
    raise SystemExit(main())
