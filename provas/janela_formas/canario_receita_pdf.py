"""JANELA-FORMAS A — canario REAL da receita PDF para as 3 fontes de janela (SFN, ERSA FVG, Campania).

Pela porta (reparar_contrato.aplicar, OUTPUT_TYPE=PDF explicito) -> canario PDF -> regua DETAIL/v1.
Numa COPIA (nada escrito no livro). D41.3: rede FECHADA por omissao; so com --rede-autorizada.
Cortesia: a pagina de entrada vem dos bytes que o robo JA guardou (lote da bancada de 25/09) e o
robots vem dos ficheiros ja baixados na medicao RFC (quando o anfitriao coincide): o UNICO pedido
novo por dominio e o do PDF (+ o robots quando nao ha copia do mesmo anfitriao). Teto D38: 5/dominio.
uso: py provas/janela_formas/canario_receita_pdf.py <raiz copia> <LOTE.json> <pasta robots> <saida.json> --rede-autorizada <missao>"""
import argparse
import hashlib
import json
import subprocess
import sys
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("raiz"); ap.add_argument("lote"); ap.add_argument("robots"); ap.add_argument("saida")
ap.add_argument("--rede-autorizada")
ap.add_argument("--so", nargs="*", help="so estes SOURCE_ID (para nao repetir pedidos a quem ja passou)")
a = ap.parse_args()
if not (a.rede_autorizada or "").strip():
    sys.exit("RECUSA (D41.3): sem --rede-autorizada <missao> este canario nao vai a rede")
RAIZ = Path(a.raiz)
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN            # noqa: E402
import capturador as CAP         # noqa: E402
import escrever_contratos as EC  # noqa: E402
import ready_split as RS         # noqa: E402
import reparar_contrato as RC    # noqa: E402

CASOS = {
    "IT-T3-014": {"INDEX_URL": "https://www.protezionedellepiante.it/category/documenti-tecnici-ufficiali/",
                  "LINK_PATTERN": r"^https?://(www\.)?protezionedellepiante\.it/wp-content/uploads/\d{4}/\d{2}/dtu-[^/?#]+\.pdf(\?|#|$)"},
    "IT-T3-027": {"INDEX_URL": "http://www.ersa.fvg.it/cms/aziende/in-formazione/Bollettini/index.html",
                  # tentativa 1: (cms/)? -> o 1.o alvo (/aziende/...) deu HTTP 404; o item que o robo abriu
                  # de manha estava em /cms/aziende/... — a receita corrigida pela prova so aceita /cms/
                  "LINK_PATTERN": r"^https?://(www\.)?ersa\.fvg\.it/cms/aziende/bollettini-(integrata|biologica)/.+\.pdf$"},
    "IT-T3-025": {"INDEX_URL": "http://www.agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/NA_2026.html",
                  "LINK_PATTERN": r"^https?://(www\.)?agricoltura\.regione\.campania\.it/difesa/bollettini/bollettini_2026/pdf/NA-\d{2}-\d{2}\.pdf$"},
}
lote = json.loads(Path(a.lote).read_text(encoding="utf-8"))
guardadas = {p["URL"]: p for c in lote["CASOS"] for p in c["PAGINAS"] if p.get("SHA256")}
contratos = {c["SOURCE_ID"]: c for c in json.loads((RAIZ / "curadoria/italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
tabela = {c["SOURCE_ID"]: c for c in json.loads((RAIZ / "regras/italy_contracts_onboarded.json").read_text(encoding="utf-8"))["FONTES"]}

r = subprocess.run([sys.executable, str(RAIZ / "superficie" / "rede.py"), "--portao-de-egresso", "IT"],
                   capture_output=True, text=True)
if '"EGRESS_GATE": "PASS"' not in r.stdout:
    sys.exit("PARAR: portao de egresso de consenso nao da PASS IT")

REDE, ROBOTS, POR_DOMINIO = [], {}, {}


def dominio(u):
    h = u.split("/")[2].lower()
    return h[4:] if h.startswith("www.") else h


def robots_de(host):
    if host not in ROBOTS:
        f = Path(a.robots) / (host + ".txt")
        rp = urllib.robotparser.RobotFileParser()
        if f.exists():
            rp.parse(f.read_text(encoding="utf-8", errors="replace").splitlines()); ROBOTS[host] = (rp, "COPIA " + str(f))
        else:
            st, b, e = pedir("http://%s/robots.txt" % host, robots=True)
            rp.parse([] if st in (404, 410) else b.decode("utf-8", "replace").splitlines()); ROBOTS[host] = (rp, "LIDO HTTP %s" % st)
    return ROBOTS[host]


def pedir(url, robots=False):
    d = dominio(url)
    if POR_DOMINIO.get(d, 0) >= 5:
        return 0, b"", "TETO_D38"
    POR_DOMINIO[d] = POR_DOMINIO.get(d, 0) + 1
    st, b, e = REAL(url)
    REDE.append({"URL": url, "HTTP": st, "BYTES": len(b or b""), "SHA256": hashlib.sha256(b or b"").hexdigest(),
                 "ROBOTS_TXT": robots, "LIDO_EM": datetime.now(timezone.utc).isoformat()})
    return st, b, e


REAL = CAN.buscar


def buscar(url):
    if url in guardadas:                     # a entrada: bytes que o robo ja guardou
        p = guardadas[url]
        return p.get("HTTP") or 200, Path(p["BYTES_EM"]).read_bytes(), None
    rp, _ = robots_de(url.split("/")[2])
    if not rp.can_fetch(CAP.UA, url):
        return 0, b"", "ROBOTS_PROIBE"
    return pedir(url)


CAN.buscar = buscar
saida = {"CANARIO": "JANELA-FORMAS A — receita PDF", "REDE_AUTORIZADA_POR": a.rede_autorizada,
         "EM": datetime.now(timezone.utc).isoformat(), "FONTES": []}
for sid, rec in CASOS.items():
    if a.so and sid not in a.so:
        continue
    base = contratos.get(sid)
    if base is None:
        ln = tabela[sid]
        base = EC.contrato_html({"SOURCE_ID": sid, "NOME": ln.get("NAME") or sid, "TERRITORY": ln.get("TERRITORY"),
                                 "URL": rec["INDEX_URL"]}, {})
        # como o piloto (propor_arsac): o contrato do molde leva versao e hash antes de ir a porta
        base["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
        base["SOURCE_CONTRACT_HASH"] = EC.hash_do_contrato(base)
    proposta = dict(rec, DESFECHO="PADRAO_NOVO", OUTPUT_TYPE="PDF", COMO="JANELA-FORMAS A (bancada, agente)",
                    PORQUE="boletins em PDF na entrada (lote LOTE-20260925T072003Z)")
    try:
        novo = RC.aplicar(base, proposta)
    except RC.ReparoInvalido as e:
        saida["FONTES"].append({"SOURCE_ID": sid, "PORTA": "RECUSOU: %s" % e}); continue
    res = CAN.canario_html(novo)
    reg = RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(), "EVIDENCE_REF": "copia"},
                                {"DADOS": res}, novo) if res.get("PASS") else None
    saida["FONTES"].append({"SOURCE_ID": sid, "PORTA": "ACEITOU", "OUTPUT_TYPE": novo["OUTPUT_TYPE"],
                            "PROVENIENCIA": {k: novo["ROUTE_PROVENANCE"].get(k) for k in ("OUTPUT_TYPE", "OUTPUT_TYPE_ANTERIOR", "LISTAGEM")},
                            "CANARIO": {k: res.get(k) for k in ("PASS", "CLASSE", "PORQUE", "DETAIL_ENUMERATED", "ALVO", "ITEM_ABERTO")},
                            "REGUA": reg})
saida["PEDIDOS_A_REDE"] = REDE
saida["PEDIDOS_POR_DOMINIO"] = POR_DOMINIO
saida["ROBOTS"] = {h: v[1] for h, v in ROBOTS.items()}
Path(a.saida).write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
for f in saida["FONTES"]:
    c = f.get("CANARIO") or {}
    print(f["SOURCE_ID"], f["PORTA"], c.get("PASS"), c.get("DETAIL_ENUMERATED"), (c.get("ITEM_ABERTO") or {}).get("TEXT_CHARACTERS"),
          (f.get("REGUA") or {}).get("REGUA"), (c.get("PORQUE") or "")[:80])
print("pedidos:", len(REDE), POR_DOMINIO)
