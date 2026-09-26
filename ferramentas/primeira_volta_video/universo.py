# -*- coding: utf-8 -*-
"""PRIMEIRA-VOLTA-VIDEO · o universo: as 41 do CANAIS-41 + as 18 contas sociais novas do vivo.

Le o livro de contratos e o de estados do VIVO (so leitura) e a lista das 41 do runbook
(`ferramentas/canais41/RODADAS-41.tsv` do ramo canais-41-runbook-v1, passada por argumento).

    py ferramentas/primeira_volta_video/universo.py --vivo=<arvore do vivo> --rodadas=<RODADAS-41.tsv> --saida=UNIVERSO-59.json
"""
import json
import sys
from pathlib import Path


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    vivo = Path(arg["vivo"])
    sys.path.insert(0, str(vivo / "curadoria"))
    import lifecycle as LC   # noqa: E402  (le o livro de estados do vivo, so leitura)
    contratos = {c["SOURCE_ID"]: c for c in
                 json.loads((vivo / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
    linhas = Path(arg["rodadas"]).read_text(encoding="utf-8").splitlines()[1:]
    os41 = [l.split("\t")[1] for l in linhas if "canais-pesquisa" not in l]
    novas = sorted(s for s, c in contratos.items()
                   if (c.get("ACQUISITION") or {}).get("STRATEGY") == "SCRAP_FASE" and s not in os41)
    out = []
    for grupo, ids in (("CANAIS-41", os41), ("CONTAS-18", novas)):
        for s in ids:
            c = contratos[s]
            aq = c.get("ACQUISITION") or {}
            out.append({"SOURCE_ID": s, "GRUPO": grupo, "PLATAFORMA": aq.get("PLATFORM"), "FASE": aq.get("FASE"),
                        "NOME": " ".join((c.get("NAME") or c.get("OWNER") or "").split()),
                        "CANAL": aq.get("CHANNEL_ID") or aq.get("LINKEDIN_SLUG"),
                        "URL": c.get("CANONICAL_ENTRY_URL"), "TERRITORIO": c.get("TERRITORY"),
                        "ESTADO": LC.estado_de(s)})
    Path(arg["saida"]).write_text(json.dumps({"DATASET": "PRIMEIRA-VOLTA-VIDEO-UNIVERSO", "N": len(out),
                                              "FONTES": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("UNIVERSO", len(out), "=", len(os41), "+", len(novas))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
