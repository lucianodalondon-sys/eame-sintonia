# -*- coding: utf-8 -*-
"""LUGAR-FATO · mede o extrator (leis/fato_do_texto.py) nos textos da Sala, contra o leitor sozinho.

    py scripts/lugar_fato/medir_78.py <sala-78.json (fora do Git)> <saida.json>

O ficheiro de entrada e a leitura so-SELECT da Sala (texto inteiro) e fica FORA do Git. A saida guarda
so identificadores, os campos e trechos curtos (<= 400 letras) — nao o texto.
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
    # A Sala nao guarda a base da publicacao: sem base, a publicacao nao e provada (e isso e o certo).
    r = FT.campos_do_fato(x["texto"], x.get("published_at") if x.get("published_at") not in ("", "NAO SEI") else None, None)
    ok, _ = FL.localizacoes_do_fato(x["texto"])
    t = FL.tempo_do_fato(x["texto"], None)
    c["lugar_extrator"] += r["fact_location"] != FT.NAO_SEI
    c["lugar_%s" % r["fact_location_kind"]] += 1
    c["tempo_extrator"] += r["fact_time"] != FT.NAO_SEI
    c["tempo_%s" % r["fact_time_kind"]] += 1
    c["com_expressao_relativa"] += bool(r["EVIDENCIA"]["EXPRESSOES_RELATIVAS"])
    c["com_expressao_relativa_presa_a_um_facto"] += any(e["KIND"] for e in r["EVIDENCIA"]["EXPRESSOES_RELATIVAS"])
    # SIMULACAO, so para medir o efeito da D63/D64: a mesma linha com uma publicacao «provada» inventada.
    # Nunca e gravada como valor; so a contagem sai.
    s = FT.campos_do_fato(x["texto"], "2026-09-24", "SIMULADO so para medir")
    c["SIMULADO_tempo_relativa_contada_se_a_publicacao_fosse_provada"] += s["fact_time_basis"].startswith(FT.RELATIVA)
    c["SIMULADO_oggi_recusado_por_D64"] += any(e["EXPRESSAO"].lower() == "oggi" and "D64" in (e.get("PORQUE") or "")
                                              for e in s["EVIDENCIA"]["EXPRESSOES_RELATIVAS"])
    c["lugar_leitor_sozinho"] += bool(ok)
    c["tempo_leitor_sozinho"] += t["FACT_TIME"] != "NOT_KNOWN"
    c["sem_corpo"] += r["EVIDENCIA"]["LINHAS_DE_CORPO"] == 0
    linhas.append({"item_id": x["item_id"], "source_id": x["source_id"], "universo": x["universo"],
                   "fact_location": r["fact_location"], "fact_location_kind": r["fact_location_kind"],
                   "fact_location_precision": r["fact_location_precision"], "fact_location_basis": r["fact_location_basis"][:400],
                   "fact_time": r["fact_time"], "fact_time_kind": r["fact_time_kind"],
                   "fact_time_precision": r["fact_time_precision"], "fact_time_basis": r["fact_time_basis"][:400],
                   "OUTROS_LUGARES": ["%s (%s)" % (l["LUGAR"], l["KIND"]) for l in r["EVIDENCIA"]["LUGARES"]
                                      if l["KIND"] != r["fact_location_kind"]],
                   "EXPRESSOES_RELATIVAS": [(e["EXPRESSAO"], e["KIND"]) for e in r["EVIDENCIA"]["EXPRESSOES_RELATIVAS"]],
                   "LEITOR_SOZINHO": {"LUGARES": [a["FACT_LOCATION"] for a in ok], "TEMPO": t["FACT_TIME"]},
                   "LINHAS_DE_CORPO": r["EVIDENCIA"]["LINHAS_DE_CORPO"]})
out = {"DATASET": "MEDIDA-LUGAR-TEMPO-78-V2", "REGRAS": "D61 + D62 (EVENTO/MERCADO como tipo) + D63 (relativa com a conta)",
       "N": len(d), "CONTAGENS": dict(sorted(c.items())),
       "PUBLICATION_TIME_NA_SALA": "sem base provada em todas as linhas: nenhuma relativa pode ser contada (D63 -> NAO SEI)",
       "ITENS": linhas}
Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(out["CONTAGENS"], ensure_ascii=False))
