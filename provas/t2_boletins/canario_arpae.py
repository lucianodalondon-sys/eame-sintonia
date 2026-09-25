"""T2-BOLETINS (D47) fase 2 — canario REAL da receita nova da ARPAE (IT-T2-051) + re-julgamento pela
Admissao atual (T2).

Pela porta (`reparar_contrato.aplicar`, com OUTPUT_TYPE=PDF, STRIP_SUFFIX=/view e IDENTITY explicitos),
numa COPIA: nada e escrito no livro. Rede so com --rede-autorizada (D41.3), portao de consenso PASS IT,
fila FILTRADA a IT-T2-051. Robots LIDO NA HORA pelo leitor RFC 9309 + D39 e respeitado o Crawl-delay.
A listagem vem dos bytes que a fase 1 guardou (mesmo endereco, lida ha minutos). Teto D38: a conta
continua a da fase 1 (PEDIDOS-POR-DOMINIO.json), no maximo 5 para arpae.it.
Pedidos novos: robots + o PDF do canario + o boletim mais recente (para a Admissao) = 3.
uso: py provas/t2_boletins/canario_arpae.py <pasta da fase 1> --rede-autorizada <missao>"""
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--rede-autorizada")
a = ap.parse_args()
if not (a.rede_autorizada or "").strip():
    sys.exit("RECUSA (D41.3): sem --rede-autorizada <missao> este canario nao vai a rede")
RAIZ = Path(__file__).resolve().parents[2]
for p in (RAIZ, RAIZ / "curadoria", RAIZ / "medidas"):
    sys.path.insert(0, str(p))
import _gavetas  # noqa: E402,F401
import admissao as adm            # noqa: E402
import canario as CAN             # noqa: E402
import capturador as CAP          # noqa: E402
import orquestrador as ORQ        # noqa: E402
import ready_split as RS          # noqa: E402
import reparar_contrato as RC     # noqa: E402

_s = importlib.util.spec_from_file_location(
    "robots_rfc9309", "C:/Users/London1/orca/workspaces/eame-sintonia/robots-rfc9309-v1/coleta/robots_rfc9309.py")
RR = importlib.util.module_from_spec(_s); sys.modules["robots_rfc9309"] = RR; _s.loader.exec_module(RR)
_x = importlib.util.spec_from_file_location("executor_texto_de_pdf", RAIZ / "coleta" / "executor_texto_de_pdf.py")
EXPDF = importlib.util.module_from_spec(_x); _x.loader.exec_module(EXPDF)

SID = "IT-T2-051"
LISTA = ("https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/"
         "bollettini-agrometeo/bollettini-2026")
RECEITA = {
    "DESFECHO": "PADRAO_NOVO", "INDEX_URL": LISTA,
    "LINK_PATTERN": (r"^https?://(www\.)?arpae\.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/"
                     r"bollettini-agrometeo/bollettini-2026/\d{2}_boll_agro_\d{8}(-\d+)?\.pdf$"),
    "OUTPUT_TYPE": "PDF", "STRIP_SUFFIX": "/view",
    "IDENTITY": {
        "STRATEGY": "CONTENT_CAPTURE",
        "CAPTURES": {"b": {"FROM": "URL", "PATTERN": r"/(\d{2})_boll_agro_(\d{4})(\d{2})(\d{2})(?:-\d+)?\.pdf$"}},
        "DOCUMENT_ID": SID + ":BOLETIM:AGROMETEO:{b.2}-{b.1}",
        "SOURCE_DATE_ISO": "{b.2}-{b.3}-{b.4}",
        "FACT_TIME": ("UNKNOWN — o periodo do boletim (a semana que ele descreve e preve) esta no texto do PDF; "
                      "o coletor nao injecta PDF_TEXT"),
    },
    "COMO": "T2-BOLETINS D47 (bancada, agente)",
    "PORQUE": "a entrada antiga (/it) leva a noticias gerais; o boletim agrometeo semanal e esta lista de PDFs",
}

r = subprocess.run([sys.executable, "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py",
                    "--portao-de-egresso", "IT"], capture_output=True, text=True)
if '"EGRESS_GATE": "PASS"' not in r.stdout:
    sys.exit("PARAR: portao de egresso de consenso nao da PASS IT")

PASTA = Path(a.pasta)
F1 = json.loads((PASTA / "FASE1.json").read_text(encoding="utf-8"))
lista_guardada = [x for x in F1["RESULTADOS"] if SID in x["SOURCE_IDS"]][0]["PAGINA"]
assert lista_guardada["URL"] == LISTA and lista_guardada["HTTP"] == 200
CONTA = PASTA / "PEDIDOS-POR-DOMINIO.json"
DOM = json.loads(CONTA.read_text(encoding="utf-8"))
REDE, ULT = [], {"t": 0.0}
ROBOTS = {}


def pedir(url):
    if DOM.get("arpae.it", 0) >= 5:
        return 0, b"", "TETO_D38"
    atraso = ROBOTS["r"].crawl_delay(CAP.UA) if "r" in ROBOTS else None
    espera = max(5.0, atraso or 0) - (time.time() - ULT["t"])
    if espera > 0:
        time.sleep(espera)
    DOM["arpae.it"] = DOM.get("arpae.it", 0) + 1
    CONTA.write_text(json.dumps(DOM, indent=1), encoding="utf-8")
    st, b, e = REAL(url)
    ULT["t"] = time.time()
    b = b or b""
    h = hashlib.sha256(b).hexdigest()
    (PASTA / "bytes" / ("%s.bin" % h[:20])).write_bytes(b)
    REDE.append({"URL": url, "HTTP": st, "ERRO": e, "BYTES": len(b), "SHA256": h,
                 "EM": str(PASTA / "bytes" / ("%s.bin" % h[:20])), "LIDO_EM": datetime.now(timezone.utc).isoformat()})
    return st, b, e


REAL = CAN.buscar
st, b, e = pedir("https://www.arpae.it/robots.txt")
ROBOTS["r"] = RR.de_resposta(st or None, b, erro=e)


def buscar(url):
    if url == LISTA:
        return 200, Path(lista_guardada["EM"]).read_bytes(), ""
    d = ROBOTS["r"].decidir(CAP.UA, url)
    if not d.permite:
        return 0, b"", "ROBOTS_RECUSA: " + d.regra
    return pedir(url)


CAN.buscar = buscar
saida = {"CANARIO": "T2-BOLETINS D47 — ARPAE receita PDF", "REDE_AUTORIZADA_POR": a.rede_autorizada,
         "EM": datetime.now(timezone.utc).isoformat(), "SOURCE_ID": SID,
         "ROBOTS": {"ESTADO": ROBOTS["r"].estado, "CRAWL_DELAY": ROBOTS["r"].crawl_delay(CAP.UA), "LEITOR": RR.VERSAO},
         "LISTAGEM_GUARDADA": {k: lista_guardada[k] for k in ("URL", "SHA256", "LIDO_EM")}}
base = [c for c in json.loads((RAIZ / "curadoria/italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]
        if c["SOURCE_ID"] == SID][0]
novo = RC.aplicar(base, RECEITA)
saida["CONTRATO_PROPOSTO"] = novo
saida["CONTRATO_ANTERIOR_HASH"] = base.get("SOURCE_CONTRACT_HASH")
res = CAN.canario_html(novo)
saida["CANARIO"] = {k: res.get(k) for k in ("PASS", "CLASSE", "PORQUE", "DETAIL_ENUMERATED", "ALVO", "ITEM_ABERTO",
                                             "DOCUMENT_ID", "TEMPOS", "DETAIL_GATE")}
saida["REGUA"] = RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(), "EVIDENCE_REF": "copia"},
                                       {"DADOS": res}, novo) if res.get("PASS") else None

# o boletim mais recente da lista (o canario abre o 1.o por ordem alfabetica, que e o mais antigo)
alvos = sorted(h for h in CAN.hrefs_da_entrada(Path(lista_guardada["EM"]).read_bytes(), LISTA, "/view")
               if re.match(RECEITA["LINK_PATTERN"], h))
recente = max(alvos, key=lambda u: re.search(r"_boll_agro_(\d{8})", u).group(1) + u)
saida["ALVOS_NA_LISTA"] = len(alvos)
saida["MAIS_RECENTE"] = recente


def julgar(url, pdf):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "b.pdf"
        p.write_bytes(pdf)
        texto, estado, erro, med = EXPDF.extrair(p)
    item = ORQ.item_documental_para_a_porta(
        {"TEXTO": texto, "SOURCE_ID": SID, "PARENT_SHA256": hashlib.sha256(pdf).hexdigest(),
         "DERIVED_ARTIFACT_ID": "canario-t2b:%s" % url.rsplit("/", 1)[-1],
         "CAPTURED_AT": datetime.now(timezone.utc).isoformat()}, source_id=SID)
    dec = adm.decidir(item, "T2", corrida="CANARIO-T2-BOLETINS-D47")
    tema = adm._do_universo({"texto": texto}, "T2", adm.PERGUNTAS_DO_UNIVERSO["T2"])
    return {"URL": url, "TEXT_LAYER": estado, "CARACTERES": (med or {}).get("NON_WHITESPACE_CHARACTERS"),
            "DECIDIR": {"RESULTADO": dec.resultado, "REGRA": dec.regra, "MOTIVO": (dec.motivo or "")[:240]},
            "TEMA_T2": {"RESULTADO": tema[0], "MOTIVO": tema[1][:240], "PALAVRAS": tema[2].get("palavras", [])},
            "TEXTO_INICIO": (texto or "")[:600]}


julgados = []
if res.get("ALVO") and res.get("PASS"):
    pdf_canario = Path([x for x in REDE if x["URL"] == res["ALVO"]][0]["EM"]).read_bytes()
    julgados.append(julgar(res["ALVO"], pdf_canario))
if recente != res.get("ALVO"):
    d = ROBOTS["r"].decidir(CAP.UA, recente)
    if d.permite:
        st, pdf, e = pedir(recente)
        if st == 200 and pdf[:5] == b"%PDF-":
            julgados.append(julgar(recente, pdf))
        else:
            julgados.append({"URL": recente, "HTTP": st, "ERRO": e or "nao e PDF"})
saida["ADMISSAO_T2"] = julgados
saida["ADMISSAO_VERSAO_DA_REGRA"] = adm.VERSAO_DA_REGRA
saida["PEDIDOS_A_REDE"] = REDE
saida["PEDIDOS_POR_DOMINIO"] = DOM
(PASTA / "CANARIO-ARPAE.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
print("canario:", res.get("PASS"), res.get("CLASSE"), res.get("DOCUMENT_ID"), res.get("TEMPOS"), (res.get("PORQUE") or "")[:120])
print("regua:", (saida["REGUA"] or {}).get("REGUA"), (saida["REGUA"] or {}).get("ESTADO"))
for j in julgados:
    print("admissao T2:", j.get("URL", "")[-40:], (j.get("DECIDIR") or {}).get("RESULTADO"), (j.get("TEMA_T2") or {}).get("RESULTADO"),
          (j.get("DECIDIR") or {}).get("MOTIVO", "")[:120])
print("pedidos:", DOM)
