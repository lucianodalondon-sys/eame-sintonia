#!/usr/bin/env python3
"""
recontar_motor.py — os numeros do motor de mudanca, recontados NESTA build.

A missao da demo exige: "nao herdar numeros sem recontar no build da demo". Este
script NAO le IT-REGISTRO-VERSOES.json nem o payload para obter os numeros: ele
reexecuta o differ sobre os instantaneos oficiais em disco e so no fim compara
com o que a tela exibe. Se divergir, a demo esta mostrando numero herdado.
"""
import glob, hashlib, json, os, sys

sys.path.insert(0, "pilot-label-intelligence/bin")
import registro_it as R


def main():
    snaps = sorted(glob.glob("pilot-label-intelligence/registry/snapshots/*.csv"))
    if not snaps:
        print("  instantaneos oficiais nao estao neste worktree (sao gitignored). "
              "Ligue-os por symlink antes de recontar.", file=sys.stderr)
        return 2
    vistos, ordem = set(), []
    for s in snaps:
        h = hashlib.sha256(open(s, "rb").read()).hexdigest()
        if h in vistos:
            continue                      # republicacao identica nao e versao nova
        vistos.add(h); ordem.append(s)

    bruto = norm = 0
    eventos = []
    ant = ant_meta = None
    for s in ordem:
        linhas = R.adama_rows(R.read_rows(s))
        meta = {"sha256": hashlib.sha256(open(s, "rb").read()).hexdigest()[:16],
                "date": os.path.basename(s)[11:19], "url": s}
        if ant is not None:
            bruto += R.contar_diffs_de_campo(ant, linhas, False)
            norm += R.contar_diffs_de_campo(ant, linhas, True)
            ev = R.mark_oscillations(R.diff(ant, linhas, ant_meta, meta))
            eventos += [e for e in ev if not e.get("UNSTABLE_SOURCE")]
        ant, ant_meta = linhas, meta

    medido = {"snapshots": len(snaps), "distinct": len(ordem),
              "raw_field_diffs": bruto, "normalised_field_diffs": norm,
              "noise": bruto - norm, "noise_pct": round(100 * (bruto - norm) / bruto, 1),
              "true_changes": len(eventos)}
    tela = json.load(open("v1/dados/CASCO-PAYLOAD.json", encoding="utf-8"))["history"]
    campos = ["snapshots", "distinct", "raw_field_diffs", "noise", "noise_pct", "true_changes"]
    difs = [(k, medido[k], tela[k]) for k in campos if medido[k] != tela[k]]

    print("  recontado nesta build:")
    for k in campos:
        print(f"    {k:<24} {medido[k]}")
    print("  exibido pela tela:")
    for k in campos:
        print(f"    {k:<24} {tela[k]}")
    if difs:
        print("\n  DIVERGENCIA — a demo estaria exibindo numero herdado:")
        for k, m, t in difs:
            print(f"    {k}: recontado {m}, tela {t}")
        return 1
    print("\n  RECONTAGEM BATE COM A TELA em todos os campos")
    json.dump({"MEDIDO": medido, "TELA": tela, "BATE": True},
              open("v1/demo/RECONTAGEM-MOTOR.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
