#!/usr/bin/env python3
"""
pares_conferir.py — a PROVA de que a lista reconstruida serve no lugar da original.

`pares_reconstruir.py` remonta os pares; este script nao acredita nele. Ele roda
a esteira que consumia o arquivo de `sintonia/canonical` contra a lista
reconstruida e compara o resultado, campo a campo, com o que esta versionado:

  1. `v1/coleta/exclusao.py` (R-10) tem de devolver o MESMO veredito nas 2928
     chaves de `EXCLUSAO.json`.
  2. `v1/casco/payload.py` tem de devolver os MESMOS `uses` de
     `CASCO-PAYLOAD.json`, nos 2926 pares publicados, nos 9 campos.

Se qualquer um dos dois divergir, a reconstrucao **nao serve**, e o script diz
onde. Um empate aqui nao prova que a lista e byte-identica a original — prova a
unica coisa que importa: que a esteira inteira chega ao mesmo lugar com ela.

  uso:  python3 v1/fonte/pares_conferir.py
"""
import argparse, json, os, subprocess, sys, tempfile


def roda(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:]); print(r.stderr[-3000:], file=sys.stderr)
        sys.exit(f"  falhou: {' '.join(cmd)}")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", default="v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json")
    ap.add_argument("--exclusao", default="v1/dados/EXCLUSAO.json")
    ap.add_argument("--payload", default="v1/dados/CASCO-PAYLOAD.json")
    ap.add_argument("--hoje", default="2026-09-06")
    ap.add_argument("--cache", default="/tmp/exclusao-txt")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="paresconf")
    falhas = []

    # 1 · R-10 contra a lista reconstruida
    ex_novo = os.path.join(tmp, "EXCLUSAO.json")
    roda([sys.executable, "v1/coleta/exclusao.py", "--pares", a.pares,
          "--cache", a.cache, "--out", ex_novo])
    velho = json.load(open(a.exclusao, encoding="utf-8"))
    novo = json.load(open(ex_novo, encoding="utf-8"))
    dif = [k for k in velho["VERDICT"]
           if velho["VERDICT"][k] != novo["VERDICT"].get(k)]
    faltam = set(velho["VERDICT"]) ^ set(novo["VERDICT"])
    print(f"  R-10 · {len(novo['VERDICT'])} chaves | {len(dif)} veredito(s) diferente(s) | "
          f"{len(faltam)} chave(s) so de um lado")
    if dif or faltam:
        falhas.append("R-10")
        for k in list(dif)[:10]:
            print(f"    {k}: era {velho['VERDICT'][k]} · virou {novo['VERDICT'].get(k)}")

    # 2 · o payload contra a lista reconstruida
    pay_novo = os.path.join(tmp, "CASCO-PAYLOAD.json")
    roda([sys.executable, "v1/casco/payload.py", "--pares", a.pares,
          "--exclusao", ex_novo, "--hoje", a.hoje, "--out", pay_novo])
    pv = json.load(open(a.payload, encoding="utf-8"))
    pn = json.load(open(pay_novo, encoding="utf-8"))
    uv = {p["reg"]: p.get("uses") or [] for p in pv["products"]}
    un = {p["reg"]: p.get("uses") or [] for p in pn["products"]}
    campos = ["crop", "target", "crop_raw", "target_raw", "page", "route",
              "evidence", "quote", "exclusion_check"]
    n = ruim = 0
    for reg in sorted(set(uv) | set(un)):
        if len(uv.get(reg, [])) != len(un.get(reg, [])):
            ruim += 1
            print(f"    {reg}: {len(uv.get(reg,[]))} usos versionados, {len(un.get(reg,[]))} agora")
            continue
        for i, (x, y) in enumerate(zip(uv[reg], un[reg])):
            n += 1
            d = [c for c in campos if x.get(c) != y.get(c)]
            if d:
                ruim += 1
                if ruim <= 10:
                    print(f"    {reg}#{i} difere em {d}: "
                          f"{[x.get(c) for c in d]} vs {[y.get(c) for c in d]}")
    print(f"  payload · {n} pares comparados nos {len(campos)} campos | {ruim} divergente(s)")
    if ruim:
        falhas.append("payload.uses")

    if falhas:
        print(f"\n  A RECONSTRUCAO NAO SERVE: {', '.join(falhas)}")
        return 1
    print("\n  a esteira chega ao mesmo lugar com a lista reconstruida — "
          "R-10 identico e os 2926 pares publicados identicos nos 9 campos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
