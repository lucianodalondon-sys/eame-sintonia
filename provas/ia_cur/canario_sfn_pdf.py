"""D32 (4): o SFN (IT-T3-014) com OUTPUT_TYPE=PDF, julgado pela esteira de PDF — NUMA COPIA.

A linha do coletor diz HTML e aponta para paginas-slug; o que a entrada publica sao os DTU em PDF
(wp-content/uploads/AAAA/MM/dtu-*.pdf). Aqui o contrato da copia troca SO o OUTPUT_TYPE e o
LINK_PATTERN, o canario corre com rede (robots pela porta do robo) e a regua DETAIL/v1 e aplicada.
Nada e escrito no livro nem na tabela do coletor (essa troca e a porta do dono: onboardar_rotas_provadas).
uso: py provas/ia_cur/canario_sfn_pdf.py <raiz da copia> <saida.json>"""
import copy
import json
import sys
from datetime import datetime, timezone

RAIZ, SAIDA = sys.argv[1], sys.argv[2]
sys.path.insert(0, RAIZ + "/curadoria")
import canario as CAN        # noqa: E402
import gate_de_rota as GATE  # noqa: E402
import ready_split as RS     # noqa: E402

PADRAO_PDF = (r"^https?://(www\.)?protezionedellepiante\.it/wp-content/uploads/\d{4}/\d{2}/"
              r"dtu-[^/?#]+\.pdf(\?|#|$)")
linha = next(c for c in json.load(open(RAIZ + "/regras/italy_contracts_onboarded.json", encoding="utf-8"))["FONTES"]
             if c["SOURCE_ID"] == "IT-T3-014")
c = copy.deepcopy(linha)
c["OUTPUT_TYPE"] = "PDF"
c["ACQUISITION"]["LINK_PATTERN"] = PADRAO_PDF
c.setdefault("IDENTITY", {"DOCUMENT_ID": "IT-T3-014:{doc.1}"})

real = CAN.buscar
ROBOTS = {}


def buscar(url):
    host = url.split("/")[2]
    if host not in ROBOTS:
        ROBOTS[host] = GATE.robots_de(host)[0]
    if ROBOTS[host] is None or not GATE.permitido(url, ROBOTS[host]):
        return 0, b"", "ROBOTS_PROIBE_OU_ILEGIVEL"
    return real(url)


CAN.buscar = buscar
agora = datetime.now(timezone.utc).isoformat()
r = CAN.canario_html(c)
reg = RS.passos_da_promocao({"OBSERVED_AT": agora, "EVIDENCE_REF": "copia"}, {"DADOS": r}, c) if r.get("PASS") else None
saida = {"SOURCE_ID": "IT-T3-014", "OBSERVED_AT": agora, "ONDE": "COPIA — nada instalado",
         "CONTRATO_DA_LINHA_DO_COLETOR": {"OUTPUT_TYPE": linha["OUTPUT_TYPE"],
                                          "LINK_PATTERN": linha["ACQUISITION"]["LINK_PATTERN"]},
         "CONTRATO_DA_COPIA": {"OUTPUT_TYPE": c["OUTPUT_TYPE"], "LINK_PATTERN": PADRAO_PDF},
         "CANARIO": r, "REGUA": reg}
json.dump(saida, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"PASS": r.get("PASS"), "CLASSE": r.get("CLASSE"), "PORQUE": r.get("PORQUE"),
                  "ALVOS": r.get("DETAIL_ENUMERATED"), "ITEM": r.get("ITEM_ABERTO"),
                  "REGUA": (reg or {}).get("REGUA"), "PASSOS": (reg or {}).get("PASSOS")}, ensure_ascii=False, indent=1))
