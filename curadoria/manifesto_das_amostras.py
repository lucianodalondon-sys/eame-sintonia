#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manifesto das AMOSTRAS da missao 03 — os bytes ficam fora do Git.

    A PROVA E O SHA, NAO O FICHEIRO NO REPOSITORIO.

Irmao de `manifesto_da_evidencia.py`, que faz o mesmo para o CANONICAL_EXAMPLE
da missao 02. Aqui sao os 717 itens da amostragem representativa: 64 MB de
material de terceiros, que nao pertencem ao historico do repositorio.

O que se versiona e o sha256 de cada um. Com ele qualquer pessoa refaz a
captura e compara — e se o byte mudou, sabe-se.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "curadoria" / "amostras"
CAR = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"


def main() -> int:
    linhas, total = [], 0
    for d in sorted(BASE.iterdir()) if BASE.exists() else []:
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            b = f.read_bytes()
            total += len(b)
            linhas.append({
                "CANDIDATE_ID": d.name,
                "PATH": "curadoria/amostras/%s/%s" % (d.name, f.name),
                "BYTES": len(b),
                "SHA256": hashlib.sha256(b).hexdigest(),
            })

    # ⚠️ CONFERIR CONTRA A CARACTERIZACAO, NAO CONTRA O DISCO.
    # Um manifesto que so se descreve a si proprio nao prova nada: confirmaria
    # alegremente uma pasta vazia. O que interessa e se cada amostra que a
    # ficha INVOCA existe mesmo e tem o sha que se diz.
    #
    # ⚠️ E CONFERIR CONTRA OS DOIS MANIFESTOS. Medido: 619 das 824 referencias
    # apontam para `curadoria/evidencia/` — sao o CANONICAL_EXAMPLE da missao
    # 02, REUTILIZADO como primeiro item da amostra em vez de recapturado.
    # Isso e o comportamento correcto («nao repetir rede sem necessidade»), e
    # um verificador que so olhasse para `amostras/` acusaria 619 ficheiros
    # perdidos que estao todos no sitio.
    #
    #     UMA PROVA REUTILIZADA NAO E UMA PROVA EM FALTA.
    sha = {x["PATH"]: x["SHA256"] for x in linhas}
    evid = RAIZ / "curadoria" / "REAL-EXAMPLE-MANIFEST-V1.json"
    if evid.exists():
        for x in json.loads(evid.read_text(encoding="utf-8"))["FILES"]:
            # o manifesto da missao 02 chama-lhe CAMINHO_LOCAL, nao PATH
            sha.setdefault(x.get("PATH") or x["CAMINHO_LOCAL"], x["SHA256"])

    refs, faltam, divergem, reusados = set(), [], [], 0
    if CAR.exists():
        for c in json.loads(CAR.read_text(encoding="utf-8"))["FONTES"]:
            for i in c["SAMPLE_ITEMS"]:
                p = i.get("EVIDENCE") or ""
                if not p or p.startswith("http"):
                    continue
                refs.add(p)
                if p.startswith("curadoria/evidencia/"):
                    reusados += 1
                if p not in sha:
                    faltam.append(p)
                elif i.get("SHA256") and i["SHA256"] != sha[p]:
                    divergem.append(p)

    saida = {
        "DATASET": "SAMPLE-MANIFEST-V1",
        "O_QUE_ISTO_E": ("sha256 das amostras representativas da missao 03. Os bytes "
                         "NAO estao no Git: 64 MB de material de terceiros."),
        "COMO_REFAZER": "curadoria/amostrar.py --familia <FAMILIA>",
        "GERADO_EM": datetime.now(timezone.utc).isoformat(),
        "TOTAL_FICHEIROS": len(linhas),
        "TOTAL_BYTES": total,
        "REFERENCIADOS_PELA_CARACTERIZACAO": len(refs),
        "REUSADOS_DO_CANONICAL_EXAMPLE": reusados,
        "EM_FALTA": faltam,
        "SHA_DIVERGENTE": divergem,
        "FILES": linhas,
    }
    p = RAIZ / "curadoria" / "SAMPLE-MANIFEST-V1.json"
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("ficheiros   %d novos em amostras/  (%.1f MB)" % (len(linhas), total / 1e6))
    print("invocados   %d caminhos distintos pela caracterizacao" % len(refs))
    print("reusados    %d referencias ao CANONICAL_EXAMPLE da missao 02" % reusados)
    print("em falta    %d %s" % (len(faltam), faltam[:3] or ""))
    print("divergentes %d %s" % (len(divergem), divergem[:3] or ""))
    print("escrito: %s" % p.relative_to(RAIZ))
    return 1 if (faltam or divergem) else 0


if __name__ == "__main__":
    raise SystemExit(main())
