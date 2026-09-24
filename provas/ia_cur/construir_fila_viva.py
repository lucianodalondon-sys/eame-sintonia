"""Constroi a FILA-PRECISA-DE-IA a partir dos livros VIVOS (so leitura) + decisoes da copia D32."""
import json, sys
V = "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/curadoria/"
sys.path.insert(0, sys.argv[1] + "/curadoria")
import bancada_ia as B, janela_de_cultura as JC
L = json.load(open(V + "LIFECYCLE-LEDGER-V1.json", encoding="utf-8"))["TRANSICOES"]
E = {p["EVIDENCE_REF"]: p.get("OBSERVED_AT") for p in json.load(open(V + "LIFECYCLE-EVIDENCE-V1.json", encoding="utf-8"))["PROVAS"]}
D = json.load(open("C:/cur/d32/DECISOES-COPIA.json", encoding="utf-8"))["DECISOES"]
C = {c["SOURCE_ID"]: c for c in json.load(open(V + "italy_contracts_curator.json", encoding="utf-8"))["FONTES"]}
f = B.construir(transicoes=L, decisoes=D, propostas=[], contratos=C, janela=JC.e_janela, provas_em=E)
f["ORIGEM"] = {"LIVRO_E_PROVAS": "vivo, so leitura", "DECISOES": "C:/cur/d32/DECISOES-COPIA.json (vivo + D32 bloco 5)"}
json.dump(f, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: f[k] for k in ("TOTAL", "POR_PERGUNTA", "FORA_DA_FILA")}, ensure_ascii=False, indent=1))
for c in f["CASOS"][:30]:
    print("%-11s %-13s %s | %s" % (c["CASO"], c["PERGUNTA"], c["GATILHO"][:75], (c["ENTRADA"] or "")[:60]))
