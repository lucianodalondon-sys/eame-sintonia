# -*- coding: utf-8 -*-
"""LUGAR-FATO · mede o extrator (leis/fato_do_texto.py) nos textos da Sala, contra o leitor sozinho.

    py scripts/lugar_fato/medir_78.py <sala-78.json (fora do Git)> <saida.json>

O ficheiro de entrada e a leitura so-SELECT da Sala (texto inteiro) e fica FORA do Git. A saida guarda
so identificadores, os quatro campos e trechos curtos (<= 200 letras) — nao o texto.
"""
import collections
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "leis"))
import fato_do_texto as FT   # noqa: E402
import fato_local as FL      # noqa: E402

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
linhas, c = [], collections.Counter()
for x in d:
    r = FT.campos_do_fato(x["texto"], x.get("published_at") if x.get("published_at") not in ("", "NAO SEI") else None, None)
    ok, _ = FL.localizacoes_do_fato(x["texto"])
    t = FL.tempo_do_fato(x["texto"], None)
    c["lugar_extrator"] += r["fact_location"] != FT.NAO_SEI
    c["tempo_extrator"] += r["fact_time"] != FT.NAO_SEI
    c["lugar_leitor_sozinho"] += bool(ok)
    c["tempo_leitor_sozinho"] += t["FACT_TIME"] != "NOT_KNOWN"
    c["sem_corpo"] += r["EVIDENCIA"]["LINHAS_DE_CORPO"] == 0
    linhas.append({"item_id": x["item_id"], "source_id": x["source_id"], "universo": x["universo"],
                   "fact_location": r["fact_location"], "fact_location_basis": r["fact_location_basis"][:400],
                   "fact_time": r["fact_time"], "fact_time_basis": r["fact_time_basis"][:400],
                   "LEITOR_SOZINHO": {"LUGARES": [a["FACT_LOCATION"] for a in ok], "TEMPO": t["FACT_TIME"]},
                   "LINHAS_DE_CORPO": r["EVIDENCIA"]["LINHAS_DE_CORPO"]})
out = {"DATASET": "MEDIDA-LUGAR-TEMPO-78-V1", "N": len(d), "CONTAGENS": dict(c), "PUBLICATION_TIME_NA_SALA": "NAO SEI em todos (nenhuma relativa pode ser resolvida)",
       "ITENS": linhas}
Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(out["CONTAGENS"], ensure_ascii=False))
