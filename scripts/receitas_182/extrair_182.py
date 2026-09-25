# -*- coding: utf-8 -*-
"""RECEITAS-182 · passo 1: as fontes novas da FILA-UNICA paradas em CONTRACTED_CANARY_FAILED,
com a ultima prova que o robo guardou de cada uma. SO LEITURA do vivo, sem rede.

    py scripts/receitas_182/extrair_182.py <FILA-UNICA-CORRESPONDENCIA-V1.json>

Le no vivo (source-curator-service-v1): SOURCE-ID-ALLOCATION-V1 (CAND -> SOURCE_ID),
LIFECYCLE-LEDGER-V1 (estado e motivo da ultima transicao), LIFECYCLE-EVIDENCE-V1 (a prova
dessa transicao: retrato da entrada, familias vistas, paginas lidas) e o contrato do curador.
Escreve scripts/receitas_182/EXTRACAO-182-V1.json.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")


def ler(rel):
    b = (VIVO / rel).read_bytes()
    return json.loads(b.decode("utf-8")), hashlib.sha256(b).hexdigest()


corr = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
novas = {x["CAND_NOVO"]: x["FAMILIA"] for x in corr["CORRESPONDENCIA"] if x["RESULTADO"].startswith("NOVA")}
aloc, h_aloc = ler("curadoria/SOURCE-ID-ALLOCATION-V1.json")
livro, h_livro = ler("curadoria/LIFECYCLE-LEDGER-V1.json")
evid, h_evid = ler("curadoria/LIFECYCLE-EVIDENCE-V1.json")
contr, h_contr = ler("curadoria/italy_contracts_curator.json")
sid_de = {x["CANDIDATE_ID"]: x["SOURCE_ID"] for x in aloc.get("NOVAS", []) if x.get("SOURCE_ID")}
ult = {}
for t in livro.get("TRANSICOES", []):
    ult[t.get("SOURCE_ID")] = t
prova = {p["EVIDENCE_REF"]: p for p in evid["PROVAS"] if p.get("EVIDENCE_REF")}
contrato = {c["SOURCE_ID"]: c for c in contr["FONTES"]}
fontes = []
for cand, fam in sorted(novas.items()):
    sid = sid_de.get(cand)
    t = ult.get(sid) if sid else None
    if not t or t.get("NEW_STATE") != "CONTRACTED_CANARY_FAILED":
        continue
    p = prova.get(t.get("EVIDENCE_REF")) or {}
    c = contrato.get(sid) or {}
    fontes.append({"CANDIDATE_ID": cand, "FAMILIA_DA_FILA": fam, "SOURCE_ID": sid,
                   "TERRITORY": c.get("TERRITORY"), "NAME": c.get("NAME"),
                   "ACQUISITION": c.get("ACQUISITION"), "REASON": t.get("REASON"),
                   "PREVIOUS_STATE": t.get("PREVIOUS_STATE"), "OBSERVED_AT": t.get("OBSERVED_AT"),
                   "ETAPA": p.get("ETAPA"), "PROVA": p.get("DADOS")})
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(VIVO), capture_output=True, text=True).stdout.strip()
out = {"DATASET": "EXTRACAO-182-V1", "VIVO_HEAD": head, "NOVAS": len(novas), "PARADAS": len(fontes),
       "LIDO_SHA256": {"SOURCE-ID-ALLOCATION-V1": h_aloc, "LIFECYCLE-LEDGER-V1": h_livro,
                       "LIFECYCLE-EVIDENCE-V1": h_evid, "italy_contracts_curator": h_contr},
       "FONTES": fontes}
(AQUI / "EXTRACAO-182-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(head, len(novas), len(fontes))
