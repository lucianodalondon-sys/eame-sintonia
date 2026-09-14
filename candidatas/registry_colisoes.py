#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOSSIE DAS COLISOES — quem afirmou o que, e quando.

O §7 PROIBE ESCOLHER SOZINHO
----------------------------
Quando o mesmo SOURCE_ID foi emitido para duas fontes diferentes, nao se
resolve automaticamente. Mede-se:

    qual apareceu PRIMEIRO no git?
    qual tinha ficha completa?
    qual tinha evidencia?
    quantas referencias ja dependem dele?

E escreve-se uma PROPOSTA. Renomear em silencio e' o unico erro irreversivel
desta missao: um ID e' identidade, e identidade trocada faz uma fonte passar a
responder pelo dado de outra.

E HA UM CASO QUE NAO E' COLISAO E PARECE
----------------------------------------
Uma ficha do atlas pode declarar VARIAS rotas da mesma natureza — e' o caso de
`FR/ES/IT-T9-001`, «sites e canais de comunicacao dos concorrentes», que cita
BASF, Bayer, Syngenta e Corteva no mesmo bloco. Varias rotas num bloco nao e'
colisao: e' uma ficha de familia. O que conta como colisao e' o MESMO ID
declarado com fontes diferentes em VERSOES diferentes do registo.
"""

import collections
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "build" / "source-registry-reconciliation"
CENSO = json.loads((SAIDA / "censo.json").read_text(encoding="utf-8"))
CLAS = json.loads((SAIDA / "classificacao.json").read_text(encoding="utf-8"))


def g(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    regs = collections.defaultdict(list)
    for r in CENSO["REGISTOS"]:
        regs[r["SOURCE_ID"]].append(r)

    linhas = []
    print("DOSSIE DAS COLISOES")
    print("=" * 104)
    for i in CLAS["COLISOES"]:
        print(f"\n### {i}   ({max(r.get('N_CITACOES', 0) for r in regs[i])} "
              "citacoes no repo)")
        # agrupar por (nome, rota) — cada grupo e' uma AFIRMACAO distinta
        grupos = collections.defaultdict(list)
        for r in regs[i]:
            grupos[(r.get("SOURCE_NAME", "")[:70],
                    r.get("URL", "")[:80])].append(r)
        for (nome, url), rs in sorted(grupos.items(),
                                      key=lambda x: -len(x[1])):
            onde = sorted({r["FILE"].split("/")[-1] for r in rs})
            refs = sorted({x for r in rs for x in r["REFS"].split()
                           if not x.startswith("hist:")})
            versoes = len({r["BLOB"] for r in rs})
            print(f"  · «{nome[:64]}»")
            print(f"      rota      : {url or '(sem rota na cerca)'}")
            print(f"      em        : {', '.join(onde)} · {versoes} versoes")
            print(f"      nas pontas: {', '.join(refs[:3]) or 'nenhuma ponta'}")
            linhas.append({
                "SOURCE_ID": i, "AFIRMACAO": nome, "ROTA": url,
                "EM_FICHEIROS": " | ".join(onde), "N_VERSOES": versoes,
                "NAS_PONTAS": " ".join(refs[:6]) or "NENHUMA",
                "TEM_EVIDENCIA": "SIM" if any(r.get("EVIDENCE_PATH")
                                              for r in rs) else "NAO",
                "TEM_CERCA": "SIM" if any(r.get("TEM_CERCA_DECLARADA") == "SIM"
                                          for r in rs) else "NAO",
                "FIRST_ASSIGNMENT_DATE": rs[0]["FIRST_ASSIGNMENT_DATE"],
                "FIRST_ASSIGNMENT_COMMIT": rs[0]["FIRST_ASSIGNMENT_COMMIT"],
                "N_CITACOES": max(r.get("N_CITACOES", 0) for r in rs),
            })
        # ── a proposta: quem tem mais prova, e o que NAO se faz ──
        vivos = [l for l in linhas if l["SOURCE_ID"] == i
                 and l["NAS_PONTAS"] != "NENHUMA"]
        so_historia = [l for l in linhas if l["SOURCE_ID"] == i
                       and l["NAS_PONTAS"] == "NENHUMA"]
        if len(vivos) <= 1:
            prop = ("RESOLVIVEL SEM TOCAR IDENTIDADE: apenas UMA afirmacao "
                    f"esta viva numa ponta; {len(so_historia)} existem so' na "
                    "historia. A ficha viva fica; as historicas ficam "
                    "registadas como versao anterior do mesmo numero.")
        else:
            prop = ("⚠️ IDENTITY_COLLISION VIVA: duas afirmacoes diferentes "
                    "estao em pontas ativas. NAO resolver aqui — renomear "
                    "quebraria referencias.")
        print(f"      PROPOSTA  : {prop}")
        for l in linhas:
            if l["SOURCE_ID"] == i:
                l["RESOLUCAO_PROPOSTA"] = prop
    print("\n" + "=" * 104)

    cab = list(linhas[0])
    with open(SAIDA / "COLLISIONS.csv", "w", encoding="utf-8-sig",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cab, delimiter=";",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)

    vivas = {l["SOURCE_ID"] for l in linhas
             if "COLLISION VIVA" in l["RESOLUCAO_PROPOSTA"]}
    print(f"COLISOES medidas         : {len(CLAS['COLISOES'])}")
    print(f"resolviveis sem tocar ID : {len(CLAS['COLISOES']) - len(vivas)}")
    print(f"VIVAS, sem solucao segura: {len(vivas)}  {sorted(vivas)}")
    json.dump({"VIVAS": sorted(vivas), "LINHAS": linhas},
              open(SAIDA / "colisoes.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\ngravado: COLLISIONS.csv ({len(linhas)} afirmacoes)")


if __name__ == "__main__":
    main()
