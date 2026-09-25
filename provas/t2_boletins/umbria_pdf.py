"""D51.3 — IT-T3-053 (Umbria, janela D29) na rota PDF da D42, como SFN/ERSA/Campania: pela porta
(`reparar_contrato.aplicar`, OUTPUT_TYPE=PDF explicito), PRESERVANDO origem e identidade (o molde
por endereco `IT-T3-053:URL:{doc.1}` nao muda; ONBOARDED_BY/QUALIFY ficam; o contrato anterior fica
na proveniencia). Base = o contrato do livro VIVO do Curator (so leitura), numa COPIA.

Rede so com --rede-autorizada (D41.3); portao de consenso PASS IT; fila = so IT-T3-053; robots LIDO NA
HORA pelo leitor RFC 9309 + D39; D38 5 por dominio, 5 s entre pedidos.
  --so-lista             robots + a lista (guarda os bytes; mostra as ligacoes .pdf)          2 pedidos
  --padrao RX [--corte S] canario pela porta sobre a lista guardada + 1 PDF (+ robots de novo) 2 pedidos
uso: py provas/t2_boletins/umbria_pdf.py <pasta> --rede-autorizada <missao> (--so-lista | --padrao RX)"""
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--rede-autorizada")
ap.add_argument("--so-lista", action="store_true")
ap.add_argument("--padrao")
ap.add_argument("--corte")
a = ap.parse_args()
if not (a.rede_autorizada or "").strip():
    sys.exit("RECUSA (D41.3): sem --rede-autorizada <missao> nao vai a rede")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN            # noqa: E402
import capturador as CAP         # noqa: E402
import ready_split as RS         # noqa: E402
import reparar_contrato as RC    # noqa: E402

_s = importlib.util.spec_from_file_location(
    "robots_rfc9309", "C:/Users/London1/orca/workspaces/eame-sintonia/robots-rfc9309-v1/coleta/robots_rfc9309.py")
RR = importlib.util.module_from_spec(_s); sys.modules["robots_rfc9309"] = RR; _s.loader.exec_module(RR)
LIVRO_VIVO = Path("C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/curadoria/italy_contracts_curator.json")

SID, LISTA, DOMINIO = "IT-T3-053", "https://www.regione.umbria.it/agricoltura/bollettini-fitosanitari", "umbria.it"
r = subprocess.run([sys.executable, "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py",
                    "--portao-de-egresso", "IT"], capture_output=True, text=True)
if '"EGRESS_GATE": "PASS"' not in r.stdout:
    sys.exit("PARAR: portao de egresso de consenso nao da PASS IT")

OUT = Path(a.pasta); (OUT / "bytes").mkdir(parents=True, exist_ok=True)
CONTA = OUT / "PEDIDOS-UMBRIA.json"
DOM = json.loads(CONTA.read_text(encoding="utf-8")) if CONTA.exists() else {}
REDE, ULT = [], {"t": 0.0}
REAL = CAN.buscar


def pedir(url):
    if DOM.get(DOMINIO, 0) >= 5:
        return 0, b"", "TETO_D38"
    espera = 5.0 - (time.time() - ULT["t"])
    if espera > 0:
        time.sleep(espera)
    DOM[DOMINIO] = DOM.get(DOMINIO, 0) + 1
    CONTA.write_text(json.dumps(DOM, indent=1), encoding="utf-8")
    st, b, e = REAL(url)
    ULT["t"] = time.time()
    b = b or b""
    h = hashlib.sha256(b).hexdigest()
    p = OUT / "bytes" / ("%s.bin" % h[:20]); p.write_bytes(b)
    REDE.append({"URL": url, "HTTP": st, "ERRO": e, "BYTES": len(b), "SHA256": h, "EM": str(p),
                 "LIDO_EM": datetime.now(timezone.utc).isoformat()})
    return st, b, e


st, b, e = pedir("https://www.regione.umbria.it/robots.txt")
robots = RR.de_resposta(st or None, b, erro=e)
saida = {"MISSAO": "D51.3 IT-T3-053 rota PDF", "REDE_AUTORIZADA_POR": a.rede_autorizada,
         "ROBOTS": {"ESTADO": robots.estado, "PORQUE": robots.porque, "LEITOR": RR.VERSAO}}

if a.so_lista:
    d = robots.decidir(CAP.UA, LISTA)
    saida["ROBOTS"]["LISTA"] = {"PERMITE": d.permite, "REGRA": d.regra}
    if d.permite:
        st, b, e = pedir(LISTA)
        hrefs = sorted(CAN.hrefs_da_entrada(b, LISTA))
        saida["LISTA"] = REDE[-1]
        saida["LIGACOES_PDF"] = [h for h in hrefs if re.search(r"\.pdf(\?|$)|/download|@@download|/documents/", h, re.I)]
        saida["LIGACOES_TOTAL"] = len(hrefs)
    saida["PEDIDOS"] = REDE; saida["PEDIDOS_POR_DOMINIO"] = DOM
    (OUT / "UMBRIA-LISTA.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: saida.get(k) for k in ("ROBOTS", "LIGACOES_TOTAL")}, ensure_ascii=False))
    for h in saida.get("LIGACOES_PDF", []):
        print("  ", h)
    sys.exit(0)

lista = json.loads((OUT / "UMBRIA-LISTA.json").read_text(encoding="utf-8"))["LISTA"]


def buscar(url):
    if url == LISTA:
        return 200, Path(lista["EM"]).read_bytes(), ""
    d = robots.decidir(CAP.UA, url)
    if not d.permite:
        return 0, b"", "ROBOTS_RECUSA: " + d.regra
    return pedir(url)


CAN.buscar = buscar
base = [c for c in json.loads(LIVRO_VIVO.read_text(encoding="utf-8"))["FONTES"] if c["SOURCE_ID"] == SID][0]
proposta = {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": LISTA, "LINK_PATTERN": a.padrao, "OUTPUT_TYPE": "PDF",
            "COMO": "D51.3 rota PDF (bancada, agente)",
            "PORQUE": "os boletins fitossanitarios bons da Umbria sao PDF; o item READY de 25/09 era a pagina do servico"}
if a.corte:
    proposta["STRIP_SUFFIX"] = a.corte
novo = RC.aplicar(base, proposta)
res = CAN.canario_html(novo)
saida["CONTRATO_BASE_HASH"] = base.get("SOURCE_CONTRACT_HASH")
saida["CONTRATO_PROPOSTO"] = novo
saida["IDENTIDADE_PRESERVADA"] = novo["IDENTITY"] == base["IDENTITY"]
saida["ORIGEM_PRESERVADA"] = all(novo.get(k) == base.get(k) for k in ("SOURCE_ID", "OWNER", "NAME", "TERRITORY", "ONBOARDED_BY", "CANONICAL_ENTRY_URL"))
saida["CANARIO"] = {k: res.get(k) for k in ("PASS", "CLASSE", "PORQUE", "DETAIL_ENUMERATED", "ALVO", "ITEM_ABERTO", "DOCUMENT_ID", "TEMPOS", "DETAIL_GATE")}
saida["REGUA"] = RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(), "EVIDENCE_REF": "copia"},
                                       {"DADOS": res}, novo) if res.get("PASS") else None
saida["PEDIDOS"] = REDE; saida["PEDIDOS_POR_DOMINIO"] = DOM
(OUT / "UMBRIA-CANARIO.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
print("canario:", res.get("PASS"), res.get("CLASSE"), res.get("DETAIL_ENUMERATED"), res.get("DOCUMENT_ID"), (res.get("PORQUE") or "")[:120])
print("regua:", (saida["REGUA"] or {}).get("REGUA"), "| identidade preservada:", saida["IDENTIDADE_PRESERVADA"], "| origem:", saida["ORIGEM_PRESERVADA"])
print("pedidos:", DOM)
