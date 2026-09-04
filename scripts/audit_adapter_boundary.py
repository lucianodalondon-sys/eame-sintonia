#!/usr/bin/env python3
"""AUDITORIA DA FRONTEIRA DO ADAPTER — os «25 records corrected».

Responde uma pergunta so: o adapter APRESENTOU, ou ele DECIDIU?

    O PORTAL APRESENTA. ELE NAO RECALCULA.

Uso:
    python3 scripts/audit_adapter_boundary.py <client-model.json> [--map renames.json]

<client-model.json> e qualquer JSON produzido pelo adapter/client. O script o
percorre inteiro e reconhece um caso por ter uma chave de ID casando OPP_[0-9A-F]+.
Renomes de chave sao APRESENTACAO e nao sao defeito: declare-os em --map
({"CLIENT_KEY": "SNAPSHOT_KEY"}) e a comparacao passa a ser semantica.

Saida: veredito A / B / C / D do protocolo, e a lista exata dos ofensores.
Codigo de saida 0 = PASS (A ou B), 1 = FAIL (C ou D), 2 = nao mediu.
"""
import json, re, sys, collections

REF_PATH = 'MEETING-DECISION-FIELDS-REFERENCE.json'
OPP = re.compile(r'^OPP_[0-9A-F]+$')


def walk_cases(node, out):
    """Acha todo objeto que carrega um ID de oportunidade, em qualquer profundidade."""
    if isinstance(node, dict):
        for v in node.values():
            if isinstance(v, str) and OPP.match(v):
                out.setdefault(v, []).append(node)
                break
        for v in node.values():
            walk_cases(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_cases(v, out)
    return out


def norm(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ref = json.load(open(REF_PATH, encoding='utf-8'))
    client = json.load(open(sys.argv[1], encoding='utf-8'))
    rename = {}
    if '--map' in sys.argv:
        rename = json.load(open(sys.argv[sys.argv.index('--map') + 1], encoding='utf-8'))

    found = walk_cases(client, {})
    print(f"REFERENCE_DIGEST      {ref['REFERENCE_DIGEST']}")
    print(f"SOURCE_HEAD esperado  {ref['SOURCE_HEAD']}")
    print(f"casos no client       {len(found)}   (referencia: {ref['TOTAL_CASES']})\n")

    fields = ref['DECISION_FIELDS']
    offenders = collections.defaultdict(list)   # field -> [(id, snap, cli)]
    compared = absent = 0

    for oid, blobs in found.items():
        if oid not in ref['CASES']:
            offenders['__CASO_DESCONHECIDO'].append((oid, '—', 'nao existe nos 43'))
            continue
        r = ref['CASES'][oid]
        merged = {}
        for b in blobs:
            for k, v in b.items():
                merged.setdefault(rename.get(k, k), v)
        for f in fields:
            if f not in merged:
                absent += 1
                continue
            compared += 1
            if norm(merged[f]) != norm(r[f]):
                offenders[f].append((oid, r[f], merged[f]))

    for oid in ref['CASES']:
        if oid not in found:
            offenders['__CASO_AUSENTE'].append((oid, 'nos 43', 'nao chegou ao client'))

    # ---- testemunhas numericas, medidas no client ----
    def count(field, val):
        n = 0
        for oid, blobs in found.items():
            for b in blobs:
                m = {rename.get(k, k): v for k, v in b.items()}
                if m.get(field) == val:
                    n += 1
                    break
        return n

    w = ref['WITNESSES']
    got = {'TOTAL_CASES': len(found), 'ACT_NOW': count('STATUS', 'ACT_NOW'),
           'WINDOW_DEFINED_YES': count('WINDOW_DEFINED', 'YES'),
           'PUBLISHABLE': count('PUBLICATION_STATE', 'PUBLISHABLE'),
           'VALIDATION_REQUIRED': count('PUBLICATION_STATE', 'VALIDATION_REQUIRED')}
    print("TESTEMUNHAS NUMERICAS")
    bad_w = []
    for k in w:
        ok = got[k] == w[k]
        print(f"  {k:22} esperado {w[k]:>3}   medido {got[k]:>3}   {'OK' if ok else '<<< DIVERGE'}")
        if not ok:
            bad_w.append(k)
    if got['ACT_NOW'] == 16:
        print("\n  *** ACT_NOW = 16. Isso e WINDOW_DEFINED usado como ACT_NOW. REJECT_CANDIDATE. ***")

    # ---- as duas confusoes nomeadas no protocolo ----
    print("\nCONFUSOES NOMEADAS")
    pm = [o for o, s, c in offenders.get('PRIMARY_MATCH', []) if s is None and c is not None]
    print(f"  PRIMARY_MATCH inventado onde snapshot e nulo   {len(pm)}"
          + (f"   {pm[:6]}" if pm else "   OK"))
    wd = 0
    for oid, blobs in found.items():
        m = {}
        for b in blobs:
            m.update({rename.get(k, k): v for k, v in b.items()})
        if m.get('WINDOW_DEFINED') == 'YES' and m.get('WINDOW_OPEN_NOW') == 'YES' \
           and ref['CASES'].get(oid, {}).get('WINDOW_OPEN_NOW') != 'YES':
            wd += 1
    print(f"  WINDOW_DEFINED=YES normalizado para OPEN_NOW=YES   {wd}"
          + ("   <<< semanticamente falso" if wd else "   OK"))

    # ---- veredito ----
    print(f"\ncampos decisorios comparados {compared} · ausentes no client {absent}")
    print(f"DECISION_FIELDS_CHANGED_BY_FRONTEND = {sum(len(v) for v in offenders.values())}")
    if offenders:
        print("\nOFENSORES — registro e campo:")
        for f, rows in sorted(offenders.items()):
            print(f"\n  {f}   ({len(rows)})")
            for oid, s, c in rows[:8]:
                print(f"    {oid}\n      snapshot: {norm(s)[:150]}\n      client:   {norm(c)[:150]}")
            if len(rows) > 8:
                print(f"    … mais {len(rows)-8}")

    fail = bool(offenders) or bool(bad_w)
    print("\n" + "=" * 60)
    if not fail:
        print("VEREDITO  A/B — PRESENTATION_ONLY ou SCHEMA_ADAPTATION_WITH_SEMANTIC_IDENTITY")
        print("FRONTEND_INTELLIGENCE_RECALCULATION = NO")
        print("ADAPTER_BOUNDARY = PASS   -> seguir o caminho critico, nao abrir nova auditoria")
        return 0
    only_missing = set(offenders) <= {'__CASO_AUSENTE', '__CASO_DESCONHECIDO'} and not bad_w
    print("VEREDITO  D — MIXED (casos faltando/sobrando)" if only_missing
          else "VEREDITO  C — FRONTEND_INTELLIGENCE_RECALCULATION = YES")
    print("ADAPTER_BOUNDARY = FAIL / MUST_FIX")
    print("Corrigir a UI para entender o estado. Nunca corrigir o estado para caber na UI.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
