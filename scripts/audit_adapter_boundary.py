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

# pares codigo->rotulo vistos no acervo, para exigir bijecao (cardinalidade
# sozinha deixaria passar [A,B] -> [rotuloB, rotuloA]).
PAIRS: dict = collections.defaultdict(dict)
BACK: dict = collections.defaultdict(dict)


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


def flatten(obj, pre='', depth=0):
    """Achata dicts aninhados ate 2 niveis: window.DEFINED, products.primary.
    Um campo decisorio escondido dentro de um sub-objeto nao pode escapar da
    medicao so por estar aninhado."""
    out = {}
    for k, v in obj.items():
        key = pre + k
        out.setdefault(key, v)
        if isinstance(v, dict) and depth < 2:
            out.update(flatten(v, key + '.', depth + 1))
    return out


def norm(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def declared(field, got, want, spec):
    """Uma diferenca so e perdoada quando o adapter DECLAROU a transformacao e
    ela e deterministica e reversivel. Nao declarada e indistinguivel de
    recalculo, e reprova."""
    if norm(got) == norm(want):
        return None
    # prefixo de namespace no VALOR: "UNKNOWN" -> "NEED_DIRECTION_UNKNOWN"
    pre = (spec.get('value_prefix') or {}).get(field)
    if pre and isinstance(got, str) and got == pre + str(want):
        return f'prefixo «{pre}»'
    # join: o snapshot da um ID, o client mostra o objeto com aquele ID
    key = (spec.get('join_by') or {}).get(field)
    if key:
        if want is None and got is None:
            return 'nulo preservado'
        if isinstance(got, dict) and got.get(key) == want:
            return f'join por {key}'
    # conversao de tipo declarada: "YES"/"NO" -> booleano, deterministica e reversivel
    tb = (spec.get('value_bool') or {}).get(field)
    if tb is not None and isinstance(got, bool) and got == (want == tb):
        return f'booleano ({tb} -> true)'
    # codigo -> rotulo: cardinalidade e ordem preservadas, codigo nao aparece
    if field in (spec.get('code_to_label') or []):
        w = want or []
        if isinstance(got, list) and len(got) == len(w):
            for code, obj in zip(w, got):
                lb = obj.get('label') if isinstance(obj, dict) else str(obj)
                PAIRS[field].setdefault(code, set()).add(lb)
                BACK[field].setdefault(lb, set()).add(code)
            return 'codigo -> rotulo'
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ref = json.load(open(REF_PATH, encoding='utf-8'))
    client = json.load(open(sys.argv[1], encoding='utf-8'))
    rename, spec = {}, {}
    if '--map' in sys.argv:
        spec = json.load(open(sys.argv[sys.argv.index('--map') + 1], encoding='utf-8'))
        # formato simples {cliente: snapshot} ou rico {keys, value_prefix, join_by, code_to_label}
        rename = spec.get('keys', spec if not any(
            k in spec for k in ('keys', 'value_prefix', 'join_by', 'code_to_label')) else {})

    found = walk_cases(client, {})
    print(f"REFERENCE_DIGEST      {ref['REFERENCE_DIGEST']}")
    print(f"SOURCE_HEAD esperado  {ref['SOURCE_HEAD']}")
    print(f"casos no client       {len(found)}   (referencia: {ref['TOTAL_CASES']})\n")

    fields = ref['DECISION_FIELDS']
    offenders = collections.defaultdict(list)   # field -> [(id, snap, cli)]
    transforms = collections.defaultdict(set)  # field -> {motivo declarado}
    compared = absent = 0

    for oid, blobs in found.items():
        if oid not in ref['CASES']:
            offenders['__CASO_DESCONHECIDO'].append((oid, '—', 'nao existe nos 43'))
            continue
        r = ref['CASES'][oid]
        merged = {}
        for b in blobs:
            for k, v in flatten(b).items():
                merged.setdefault(rename.get(k, k), v)
        for f in fields:
            if f not in merged:
                absent += 1
                continue
            compared += 1
            got, want = merged[f], r[f]
            why = declared(f, got, want, spec)
            if why:
                transforms[f].add(why)
                continue
            if norm(got) != norm(want):
                offenders[f].append((oid, want, got))

    for oid in ref['CASES']:
        if oid not in found:
            offenders['__CASO_AUSENTE'].append((oid, 'nos 43', 'nao chegou ao client'))

    # ---- testemunhas numericas, medidas no client ----
    def count(field, val):
        tb = (spec.get('value_bool') or {}).get(field)
        n = 0
        for oid, blobs in found.items():
            for b in blobs:
                m = {rename.get(k, k): v for k, v in flatten(b).items()}
                v = m.get(field)
                if v == val or (tb is not None and isinstance(v, bool) and v is (val == tb)):
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
            m.update({rename.get(k, k): v for k, v in flatten(b).items()})
        if m.get('WINDOW_DEFINED') == 'YES' and m.get('WINDOW_OPEN_NOW') == 'YES' \
           and ref['CASES'].get(oid, {}).get('WINDOW_OPEN_NOW') != 'YES':
            wd += 1
    print(f"  WINDOW_DEFINED=YES normalizado para OPEN_NOW=YES   {wd}"
          + ("   <<< semanticamente falso" if wd else "   OK"))

    # ---- as seis provas nomeadas do protocolo ----
    def cli(oid):
        m = {}
        for b in found.get(oid, []):
            m.update({rename.get(k, k): v for k, v in flatten(b).items()})
        return m

    bij = []
    for f in PAIRS:
        amb = [c for c, v in PAIRS[f].items() if len(v) > 1]
        col = [l for l, v in BACK[f].items() if len(v) > 1]
        if amb or col:
            bij.append((f, amb, col))
            offenders[f].append((f, f'codigo ambiguo {amb}', f'rotulo colidido {col}'))

    print("\nAS SEIS PROVAS")
    proofs = {}

    # 1 · UNKNOWN permanece UNKNOWN
    bad = [o for o, r in ref['CASES'].items()
           if r['WINDOW_OPEN_NOW'] == 'UNKNOWN'
           and 'WINDOW_OPEN_NOW' in cli(o)
           and 'UNKNOWN' not in str(cli(o)['WINDOW_OPEN_NOW'])]
    proofs['WINDOW_OPEN_NOW_UNKNOWN_PRESERVED'] = bad
    print(f"  UNKNOWN permanece UNKNOWN                     {'OK' if not bad else str(len(bad))+' violados '+str(bad[:6])}")

    # 2 · WINDOW_DEFINED=YES nao promove ACT_NOW
    bad = [o for o, r in ref['CASES'].items()
           if r['WINDOW_DEFINED'] == 'YES' and r['STATUS'] != 'ACT_NOW'
           and cli(o).get('STATUS') == 'ACT_NOW']
    proofs['WINDOW_DEFINED_DOES_NOT_PROMOTE_ACT_NOW'] = bad
    print(f"  WINDOW_DEFINED=YES nao promove ACT_NOW        {'OK' if not bad else str(len(bad))+' promovidos '+str(bad[:6])}")

    # 3 · PORTFOLIO_MATCHES nao cria PRIMARY_MATCH
    nulls = [o for o, r in ref['CASES'].items() if r['PRIMARY_MATCH'] is None]
    bad = [o for o in nulls if 'PRIMARY_MATCH' in cli(o) and cli(o)['PRIMARY_MATCH'] is not None]
    # bijecao codigo->rotulo: o mesmo codigo nunca vira dois rotulos diferentes
    proofs['PORTFOLIO_DOES_NOT_CREATE_PRIMARY'] = bad
    seen = [o for o in nulls if 'PRIMARY_MATCH' in cli(o)]
    print(f"  PRIMARY_MATCH_NULL_REFERENCE = {len(nulls)}"
          f"   ·   CLIENT_PRIMARY_MATCH_NULL = {len(seen)-len(bad)} de {len(seen)} vistos")
    if bad:
        print(f"    frontend inventou primary em {len(bad)}: {bad}")

    # 4 · PUBLICATION_STATE nao e promovido
    bad = [o for o, r in ref['CASES'].items()
           if r['PUBLICATION_STATE'] == 'VALIDATION_REQUIRED'
           and cli(o).get('PUBLICATION_STATE') == 'PUBLISHABLE']
    proofs['PUBLICATION_STATE_NOT_PROMOTED'] = bad
    print(f"  PUBLICATION_STATE nao e promovido             {'OK' if not bad else str(len(bad))+' promovidos '+str(bad[:6])}")

    # 5 · ACTION_BY_DEPARTMENT nao e reescrito
    bad = [o for o, s2, c2 in offenders.get('ACTION_BY_DEPARTMENT', [])]
    proofs['ACTION_BY_DEPARTMENT_NOT_REWRITTEN'] = bad
    print(f"  ACTION_BY_DEPARTMENT nao e reescrito          {'OK' if not bad else str(len(bad))+' reescritos '+str(bad[:6])}")

    # 6 · WHY_COMMERCIAL nao e reconstruido
    bad = sorted({o for f in ('WHY_COMMERCIAL_IT', 'WHY_COMMERCIAL_EN', 'WHY_COMMERCIAL_CODES')
                  for o, s2, c2 in offenders.get(f, [])})
    proofs['WHY_COMMERCIAL_NOT_RECONSTRUCTED'] = bad
    print(f"  WHY_COMMERCIAL nao e reconstruido             {'OK' if not bad else str(len(bad))+' reconstruidos '+str(bad[:6])}")

    # ---- veredito ----
    if transforms:
        print("\nTRANSFORMACOES DECLARADAS — aceitas por serem deterministicas e reversiveis")
        for f, ws in sorted(transforms.items()):
            extra = ''
            if f in PAIRS:
                extra = (f"  ·  {len(PAIRS[f])} codigos -> {len(BACK[f])} rotulos"
                         f"{'  BIJECAO OK' if not any(b[0] == f for b in bij) else '  <<< NAO E BIJECAO'}")
            print(f"  {f:30} {' · '.join(sorted(ws))}{extra}")
    print(f"\ncampos decisorios comparados {compared} · ausentes no client {absent}")
    print(f"DECISION_FIELDS_CHANGED_BY_FRONTEND = {sum(len(v) for v in offenders.values())}")
    if offenders:
        print("\nOFENSORES — registro e campo:")
        for f, rows in sorted(offenders.items()):
            print(f"\n  {f}   ({len(rows)})")
            for oid, s2, c2 in rows[:8]:
                print(f"    {oid}\n      snapshot: {norm(s2)[:150]}\n      client:   {norm(c2)[:150]}")
            if len(rows) > 8:
                print(f"    … mais {len(rows)-8}")

    mutation = {f: v for f, v in offenders.items()
                if f not in ('__CASO_AUSENTE', '__CASO_DESCONHECIDO')}
    structural = {f: v for f, v in offenders.items()
                  if f in ('__CASO_AUSENTE', '__CASO_DESCONHECIDO')}
    broken_proofs = {k: v for k, v in proofs.items() if v}

    print("\n" + "=" * 60)
    if mutation or broken_proofs or bad_w:
        verdict = "MIXED" if (structural and not (mutation or broken_proofs)) else "FAIL_DECISION_MUTATION"
        print(f"ADAPTER_BOUNDARY = {verdict}")
        for k, v in broken_proofs.items():
            print(f"  prova quebrada: {k} -> {len(v)} registros")
        print("Corrigir SOMENTE a transformacao ofensora.")
        print("Nao voltar ao motor. Nao alterar snapshot. Nao abrir redesign.")
        return 1
    if structural:
        print("ADAPTER_BOUNDARY = MIXED   (casos faltando ou sobrando; campos intactos)")
        for f, rows in structural.items():
            print(f"  {f}: {len(rows)}")
        return 1
    verdict = ("PASS_DECLARED_SCHEMA_ADAPTATION"
               if (rename or transforms) else "PASS_PRESENTATION_ONLY")
    print(f"ADAPTER_BOUNDARY = {verdict}")
    print("FRONTEND_INTELLIGENCE_RECALCULATION = NO")
    print("-> seguir o caminho critico. Nao abrir nova auditoria.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
