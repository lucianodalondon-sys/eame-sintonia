#!/usr/bin/env python3
"""Valida security-baseline.json. Existe para o Security Ratchet poder correr
sozinho: um mapeamento que aponta para um controlo inexistente e uma norma que
perdeu o dono, e isso degrada em silencio.

    SECURITY THAT DEPENDS ON MEMORY DEGRADES WITH TIME.

Uso: python3 security/validate-baseline.py   (exit 0 = ok, 1 = falha)
"""
import json, sys, pathlib, collections

VALID_STATUS = {"PROVED","PARTIAL","ABSENT","UNKNOWN","NOT_APPLICABLE","FUTURE","NOT_APPLICABLE_YET"}
VALID_PHASE  = {"NOW","BEFORE_REAL_USERS","BEFORE_CONTRACT","BEFORE_ADAMA_IT_REVIEW"}

def main():
    p = pathlib.Path(__file__).with_name("security-baseline.json")
    d = json.loads(p.read_text(encoding="utf-8"))
    err = []

    ids = [c["CONTROL_ID"] for c in d["CONTROLS"]]
    dup = [k for k, n in collections.Counter(ids).items() if n > 1]
    if dup:
        err.append(f"CONTROL_ID duplicado: {dup}")

    for c in d["CONTROLS"]:
        if c["STATUS"] not in VALID_STATUS:
            err.append(f"{c['CONTROL_ID']}: STATUS invalido {c['STATUS']!r}")

    known = set(ids)
    mapped = set()
    for m in d.get("STANDARDS_MAPPING", []):
        cid = m["CONTROL_ID"]
        mapped.add(cid)
        if cid not in known:
            err.append(f"STANDARDS_MAPPING aponta para controlo inexistente: {cid}")
        if m["CURRENT_STATUS"] not in VALID_STATUS:
            err.append(f"{cid}: CURRENT_STATUS invalido {m['CURRENT_STATUS']!r}")
        if m["PHASE"] not in VALID_PHASE:
            err.append(f"{cid}: PHASE invalida {m['PHASE']!r}")

    # Uma norma sem controlo nosso e um requisito sem dono. ONE CONCEPT -> ONE OWNER.
    for cid in sorted(known - mapped):
        err.append(f"controlo sem mapeamento de norma: {cid}")

    if not d.get("STANDARDS"):
        err.append("STANDARDS ausente")
    for s in d.get("STANDARDS", []):
        for k in ("name","version","status","date_accessed"):
            if not s.get(k):
                err.append(f"STANDARDS {s.get('name')}: falta {k}")

    for e in err:
        print("FALHA:", e)
    print(f"controlos {len(ids)} · mapeamentos {len(d.get('STANDARDS_MAPPING',[]))} · normas {len(d.get('STANDARDS',[]))}")
    print("OK" if not err else f"{len(err)} falha(s)")
    return 1 if err else 0

if __name__ == "__main__":
    sys.exit(main())
