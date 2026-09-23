#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENSAIO OFFLINE DA QUARENTENA DO NAO SEI (D11, opcao C) — os 2 gabaritos, o detector ACTUAL.

    MEDIR, NAO COPIAR OS NUMEROS DO BRIEFING.

Para cada pagina rotulada (CAPA ou MATERIA) dos dois gabaritos:
    bytes (sha256 conferido contra o manifesto da recolha)
      -> curadoria/retrato_html.retrato_do_html    (o detector, intocado)
      -> curadoria/politica_nao_sei.decidir(QUARENTENA)
Conta: quantas vao para QUARENTENA; quantas CAPAS entram (o detector disse materia);
quantas MATERIAS ficam retidas (quarentena) ou sao barradas (o detector disse capa).

VAZIA e AMBIGUA (so no controlo) ficam fora da contagem, e ficam ditas.
Sem rede. Nada e escrito fora da saida pedida.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import retrato_html as RH        # noqa: E402
import politica_nao_sei as PNS   # noqa: E402

HOME = Path.home()
GABARITOS = (
    ("ORIGINAL", RAIZ / "scripts" / "detector_capa" / "GABARITO-CAPA-V1.json", None, HOME / "detector-capa-gabarito"),
    ("CONTROLO_LD2", None, "origin/listing-detail-v3:scripts/detector_capa/GABARITO-CONTROLO-LD2.json",
     HOME / "ld2-controlo"),
)


def _gabarito(f, ref):
    if f is not None:
        return json.loads(f.read_text(encoding="utf-8"))
    r = subprocess.run(["git", "show", ref], cwd=RAIZ, capture_output=True)
    return json.loads(r.stdout.decode("utf-8"))


def medir(nome, f, ref, pasta) -> dict:
    g = _gabarito(f, ref)
    man = {p["FICHEIRO"]: p["SHA256"] for p in
           json.loads((pasta / "MANIFESTO.json").read_text(encoding="utf-8"))["PAGINAS"]}
    conta, fora, sha_mal, linhas = Counter(), Counter(), [], []
    for p in g["PAGINAS"]:
        v = p.get("VEREDITO")
        if v not in ("CAPA", "MATERIA"):
            fora[v] += 1
            continue
        b = (pasta / p["FICHEIRO"]).read_bytes()
        if man.get(p["FICHEIRO"]) and hashlib.sha256(b).hexdigest() != man[p["FICHEIRO"]]:
            sha_mal.append(p["FICHEIRO"])
            continue
        ret = RH.retrato_do_html(b)
        acc = PNS.decidir(ret, PNS.QUARENTENA)["ACCAO"]
        conta[(v, acc)] += 1
        linhas.append({"ID": p.get("ID"), "SOURCE_ID": p.get("SOURCE_ID"), "VEREDITO_HUMANO": v,
                       "DETECTOR": ret["CAPA_OU_MATERIA"], "ACCAO": acc})
    capas = sum(n for (v, _), n in conta.items() if v == "CAPA")
    mats = sum(n for (v, _), n in conta.items() if v == "MATERIA")
    return {
        "GABARITO": nome, "CAPAS": capas, "MATERIAS": mats, "FORA_DA_CONTAGEM": dict(fora),
        "SHA256_NAO_CONFERE": sha_mal,
        "QUARENTENA": conta[("CAPA", "QUARENTENA")] + conta[("MATERIA", "QUARENTENA")],
        "QUARENTENA_CAPAS": conta[("CAPA", "QUARENTENA")],
        "QUARENTENA_MATERIAS": conta[("MATERIA", "QUARENTENA")],
        "CAPAS_QUE_ENTRAM": conta[("CAPA", "ENTRA")],
        "CAPAS_BARRADAS": conta[("CAPA", "REPROVA")],
        "MATERIAS_QUE_ENTRAM": conta[("MATERIA", "ENTRA")],
        "MATERIAS_RETIDAS_EM_QUARENTENA": conta[("MATERIA", "QUARENTENA")],
        "MATERIAS_BARRADAS_COMO_CAPA": conta[("MATERIA", "REPROVA")],
        "SEM_QUARENTENA_CAPAS_QUE_ENTRARIAM": conta[("CAPA", "ENTRA")] + conta[("CAPA", "QUARENTENA")],
        "LINHAS": linhas,
    }


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    out = {"DATASET": "ENSAIO-QUARENTENA-NAOSEI-V1", "DETECTOR": "curadoria/retrato_html.py (intocado)",
           "POLITICA": "politica_nao_sei.QUARENTENA (D11)",
           "GABARITOS": [medir(*g) for g in GABARITOS]}
    for g in out["GABARITOS"]:
        print({k: v for k, v in g.items() if k != "LINHAS"})
    if argv:
        Path(argv[0]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
