"""BOLETINS D61/D62 fase 2 — 1 documento real por dominio (o mais recente da lista guardada na fase 1), para
ler ONDE o boletim diz a emissao, o periodo e a area. Portao de consenso PASS IT; robots LIDO NA HORA pelo
leitor RFC 9309 + D39; D38 continua a conta da fase 1 (no maximo 5 por dominio); 5 s entre pedidos.
uso: py provas/boletins_data_local/fase2_um_item.py <pasta da fase 1> --rede-autorizada <missao>"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--rede-autorizada")
a = ap.parse_args()
if not (a.rede_autorizada or "").strip():
    sys.exit("RECUSA (D41.3): sem --rede-autorizada <missao> nao vai a rede")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN        # noqa: E402
import capturador as CAP     # noqa: E402
_s = importlib.util.spec_from_file_location(
    "robots_rfc9309", "C:/Users/London1/orca/workspaces/eame-sintonia/robots-rfc9309-v1/coleta/robots_rfc9309.py")
RR = importlib.util.module_from_spec(_s); sys.modules["robots_rfc9309"] = RR; _s.loader.exec_module(RR)

r = subprocess.run([sys.executable, "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py",
                    "--portao-de-egresso", "IT"], capture_output=True, text=True)
if '"EGRESS_GATE": "PASS"' not in r.stdout:
    sys.exit("PARAR: portao de egresso de consenso nao da PASS IT")

ITENS = {   # o mais recente de cada lista da fase 1 (lido nos bytes guardados)
    "IT-T2-148": "https://arsac.calabria.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-vite-e-kiwi-valido-fino-a-giorno-29-settembre-2026/",
    "IT-T3-032": None,   # o 1.o anexo PDF da pagina (Comunicato fitosanitario n.6/2026), lido abaixo
    "IT-T3-055": "https://www.regione.vda.it/allegato.aspx?pk=130369",
    "IT-T3-058": "https://www.regione.veneto.it/documents/11979050/14331610/Olivicolo_2026_32.pdf/335b1782-faf1-4762-b6d5-d8d0092eb5b5",
}
OUT = Path(a.pasta)
F1 = json.loads((OUT / "FASE1.json").read_text(encoding="utf-8"))
if ITENS["IT-T3-032"] is None:
    import re
    lista = [x for x in F1["RESULTADOS"] if "IT-T3-032" in x["SOURCE_IDS"]][0]["PAGINA"]
    b = Path(lista["EM"]).read_bytes().decode("utf-8", "replace")
    import html as _h
    ITENS["IT-T3-032"] = _h.unescape(re.search(r'href="([^"]*ServeAttachment[^"]*E/pdf[^"]*)"', b).group(1))
    if ITENS["IT-T3-032"].startswith("/"):
        ITENS["IT-T3-032"] = "https://www.regione.molise.it" + ITENS["IT-T3-032"]
CONTA = OUT / "PEDIDOS-POR-DOMINIO.json"
DOM = json.loads(CONTA.read_text(encoding="utf-8"))


def dominio(host):
    return ".".join(host.split(".")[-2:])


def pedir(url):
    d = dominio(url.split("/")[2])
    if DOM.get(d, 0) >= 5:
        return None
    DOM[d] = DOM.get(d, 0) + 1
    CONTA.write_text(json.dumps(DOM, indent=1), encoding="utf-8")
    st, b, e = CAN.buscar(url)
    b = b or b""
    h = hashlib.sha256(b).hexdigest()
    p = OUT / "bytes" / ("%s.bin" % h[:20]); p.write_bytes(b)
    time.sleep(5)
    return {"URL": url, "HTTP": st, "ERRO": e, "BYTES": len(b), "SHA256": h, "EM": str(p),
            "PDF": b[:5] == b"%PDF-", "LIDO_EM": datetime.now(timezone.utc).isoformat()}


res = {}
for sid, url in ITENS.items():
    host = url.split("/")[2]
    rb = pedir("https://%s/robots.txt" % host)
    robots = RR.de_resposta(rb["HTTP"] or None, Path(rb["EM"]).read_bytes(), erro=rb["ERRO"])
    dec = robots.decidir(CAP.UA, url)
    lin = {"URL": url, "ROBOTS": dict(rb, ESTADO=robots.estado), "ROBOTS_ITEM": {"PERMITE": dec.permite, "REGRA": dec.regra}}
    if dec.permite:
        lin["ITEM"] = pedir(url)
    res[sid] = lin
    it = lin.get("ITEM") or {}
    print(sid, robots.estado, dec.permite, it.get("HTTP"), it.get("BYTES"), "PDF" if it.get("PDF") else "nao-PDF", url[:100])
(OUT / "FASE2-ITENS.json").write_text(json.dumps({"FASE": "BOLETINS D61/D62 fase 2", "REDE_AUTORIZADA_POR": a.rede_autorizada,
                                                  "ITENS": res, "PEDIDOS_POR_DOMINIO": DOM}, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
print("pedidos:", DOM)
