#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o MANIFESTO da evidencia e mantem os BYTES fora do Git.

    A PROVA E O SHA, NAO O FICHEIRO NO REPOSITORIO.

Os 124 exemplos reais pesam 58 MB — sobretudo um MP4 de 12 MB e PDFs de
catalogo. Commitar isso poria dezenas de megabytes de material de terceiros
na arvore, para sempre, por causa de uma missao de qualificacao.

O que fica versionado e o MANIFESTO: por candidata, o endereco do item, o
`sha256`, os bytes, o tipo e a data visivel. Com ele, qualquer pessoa refaz a
captura e compara o hash — que e exactamente o que o `MANIFEST.json` das 140
fontes ja registadas no Atlas faz.

    OS BYTES PROVAM-SE PELO HASH; O HASH E QUE TEM DE SOBREVIVER.

Os bytes ficam em `curadoria/evidencia/` (ignorada pelo Git) ate a missao de
onboarding os promover ao caminho canonico do Atlas —
`data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/` — que e onde eles pertencem
QUANDO a fonte tiver SOURCE_ID. Hoje nao tem: sao candidatas.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
EVID = RAIZ / "curadoria" / "evidencia"


def main() -> int:
    fichas = {f["CANDIDATE_ID"]: f for f in json.loads(
        (RAIZ / "curadoria" / "REAL-EXAMPLE-INDEX-V1.json").read_text(encoding="utf-8"))["FICHAS"]}

    linhas, total = [], 0
    for pasta in sorted(EVID.iterdir()) if EVID.exists() else []:
        for fich in sorted(pasta.iterdir()):
            b = fich.read_bytes()
            f = fichas.get(pasta.name, {})
            total += len(b)
            linhas.append({
                "CANDIDATE_ID": pasta.name,
                "CAMINHO_LOCAL": str(fich.relative_to(RAIZ)).replace("\\", "/"),
                "SOURCE_URL": f.get("REAL_EXAMPLE_URL"),
                "HTTP_STATUS": f.get("HTTP_STATUS"),
                "BYTES": len(b),
                "SHA256": hashlib.sha256(b).hexdigest(),
                "ASSINATURA_REAL_DOS_BYTES": f.get("REAL_EXAMPLE_MEDIA_TYPE"),
                "TITULO": f.get("REAL_EXAMPLE_TITLE"),
                "DATA_VISIVEL": f.get("REAL_EXAMPLE_PUBLISHED_AT"),
                "FAMILY": f.get("FAMILY"),
                "CAPTURED_AT": f.get("CAPTURED_AT"),
            })

    # ⚠️ O manifesto tem de concordar com o indice. Um sha diferente entre os
    # dois significaria que os bytes no disco nao sao os que a ficha descreve.
    divergentes = [l["CANDIDATE_ID"] for l in linhas
                   if fichas.get(l["CANDIDATE_ID"], {}).get("REAL_EXAMPLE_SHA256")
                   not in (l["SHA256"], None)]

    saida = {
        "DATASET": "REAL-EXAMPLE-MANIFEST-V1",
        "O_QUE_ISTO_E": ("manifesto verificavel dos exemplos reais capturados. Os BYTES "
                         "nao estao no Git (58 MB de material de terceiros); o que esta "
                         "e o sha256, que permite refazer a captura e comparar."),
        "COMO_VERIFICAR": ("descarregar SOURCE_URL e comparar sha256. Um hash diferente "
                           "significa que a fonte publicou coisa nova — o que e uma "
                           "observacao valida, nao um erro do manifesto."),
        "ONDE_VIVEM_OS_BYTES": ("curadoria/evidencia/<CANDIDATE_ID>/ nesta worktree, "
                                "ignorada pelo Git. Na promocao, mudam para o caminho "
                                "canonico data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/, "
                                "que so existe quando houver SOURCE_ID."),
        "GERADO_EM": datetime.now(timezone.utc).isoformat(),
        "EGRESSO_DA_CAPTURA": "205.147.30.6 · Milano, IT · AS208172 Proton AG",
        "TOTAL_FICHEIROS": len(linhas),
        "TOTAL_BYTES": total,
        "SHA_DIVERGENTE_DO_INDICE": divergentes,
        "FILES": linhas,
    }
    p = RAIZ / "curadoria" / "REAL-EXAMPLE-MANIFEST-V1.json"
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("ficheiros  %d" % len(linhas))
    print("bytes      %.1f MB" % (total / 1e6))
    print("divergentes %d %s" % (len(divergentes), divergentes or ""))
    print("escrito: %s" % p.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
