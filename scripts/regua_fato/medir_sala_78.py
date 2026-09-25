#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGUA-DO-TIPO-DE-FATO · as 78 linhas da Sala (COPIA so-leitura) com o tipo do facto, e o que a regra
de ligacao muda no lugar/tempo da LUGAR-FATO.

    py scripts/regua_fato/medir_sala_78.py [--sala=C:/Users/London1/lugar-fato/sala-78.json]

Sem rede, sem banco. `published_at` da Sala vai como publicacao SEM base (a Sala nao guarda a base):
pela D63 nenhuma relativa e contada — igual a medida da LUGAR-FATO.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).parent
sys.path.insert(0, str(RAIZ / "leis"))
import tipo_do_fato as TF  # noqa: E402


def main():
    f = Path(next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--sala=")),
                  "C:/Users/London1/lugar-fato/sala-78.json"))
    linhas = json.loads(f.read_text(encoding="utf-8"))
    tipos, mudou, detalhe = Counter(), Counter(), []
    for l in linhas:
        base = TF.FT.campos_do_fato(l["texto"])
        r = TF.fato_com_tipo(l["texto"])
        tipos[r["agro_fact_kind"]] += 1
        m = {}
        for k in ("fact_location", "fact_time"):
            if (base[k], base[k + "_kind"]) != (r[k], r[k + "_kind"]):
                mudou[k] += 1
                m[k] = {"ANTES": "%s (%s)" % (base[k], base[k + "_kind"]), "DEPOIS": "%s (%s)" % (r[k], r[k + "_kind"])}
        detalhe.append({"item_id": l["item_id"], "source_id": l["source_id"], "universo": l["universo"],
                        "agro_fact_kind": r["agro_fact_kind"], "agro_fact_kind_basis": r["agro_fact_kind_basis"][:200],
                        "fact_location": r["fact_location"], "fact_location_kind": r["fact_location_kind"],
                        "fact_time": r["fact_time"], "fact_time_kind": r["fact_time_kind"],
                        "MUDOU_PELA_LIGACAO": m or None})
    out = {"DATASET": "MEDIDA-TIPO-DO-FATO-SALA-78-V2", "SALA_COPIA": str(f),
           "SALA_COPIA_SHA256": hashlib.sha256(f.read_bytes()).hexdigest(), "LINHAS": len(linhas),
           "POR_AGRO_FACT_KIND": dict(tipos.most_common()), "SAEM_DE_NAO_SEI": len(linhas) - tipos[TF.NAO_SEI],
           "LUGAR_E_TEMPO_MUDADOS_PELA_LIGACAO": dict(mudou), "DESCARTADOS": 0, "ITENS": detalhe}
    (AQUI / "MEDIDA-TIPO-DO-FATO-SALA-78-V2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                             encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("LINHAS", "POR_AGRO_FACT_KIND", "SAEM_DE_NAO_SEI",
                                          "LUGAR_E_TEMPO_MUDADOS_PELA_LIGACAO")}, ensure_ascii=False, indent=1))
    for d in detalhe:
        if d["MUDOU_PELA_LIGACAO"]:
            print(d["source_id"], d["agro_fact_kind"], json.dumps(d["MUDOU_PELA_LIGACAO"], ensure_ascii=False))


if __name__ == "__main__":
    main()
