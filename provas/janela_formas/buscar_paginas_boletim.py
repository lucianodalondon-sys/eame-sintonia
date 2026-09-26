"""JANELA-FORMAS B — fase 1 (rede): 1 pedido por fonte as paginas que a bancada chamou «a pagina e o
boletim», + a pagina do boletim de viticultura do CAAR (candidata). D41.3: so com --rede-autorizada;
portao de consenso PASS IT; robots das copias da medicao RFC (ou lido, se o anfitriao nao tem copia);
teto D38 de 5 pedidos por dominio. Bytes em <pasta>/<SOURCE_ID>.bin com sha256 no indice.
uso: py provas/janela_formas/buscar_paginas_boletim.py <raiz copia> <pasta robots> <pasta saida> --rede-autorizada <missao>"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("raiz"); ap.add_argument("robots"); ap.add_argument("saida"); ap.add_argument("--rede-autorizada")
a = ap.parse_args()
if not (a.rede_autorizada or "").strip():
    sys.exit("RECUSA (D41.3): sem --rede-autorizada <missao> nao se vai a rede")
RAIZ = Path(a.raiz)
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN      # noqa: E402
import capturador as CAP   # noqa: E402

PAGINAS = {
    "IT-T1-006": "https://arsac.calabria.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-vite-e-kiwi-valido-fino-al-4-agosto-2026/",
    "IT-T2-148": "https://www.arsacweb.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-e-vite/",
    "IT-T2-152": "https://www.lamma.toscana.it/agrometeo/firenze",
    "IT-T2-136": "https://www.arpalombardia.it/temi-ambientali/meteo-e-clima/bollettini-meteorologici/agrometeo/",
    "IT-T2-138": "https://www.arpae.it/it/temi-ambientali/meteo/dati-e-osservazioni/mappe-settimanali",
    "IT-T2-139": "https://www.arpae.it/it/temi-ambientali/meteo/previsioni-meteo/previsioni-agrometeo",
    "IT-T2-153": "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar.html",
    "IT-T3-031": "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/servizio-fitosanitario-regionale/sorveglianza-del-territorio-carte-di-diffusione-e-monitoraggio-degli-organismi-nocivi.html",
    "IT-T2-153~viticoltura": "https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar/bollettino-di-viticoltura.html",
}
r = subprocess.run([sys.executable, str(RAIZ / "superficie" / "rede.py"), "--portao-de-egresso", "IT"], capture_output=True, text=True)
if '"EGRESS_GATE": "PASS"' not in r.stdout:
    sys.exit("PARAR: portao de egresso de consenso nao da PASS IT")
out, ROB, DOM, ULT = [], {}, {}, {}
pasta = Path(a.saida); pasta.mkdir(parents=True, exist_ok=True)


def dominio(h):
    return h[4:] if h.startswith("www.") else h


def conta(h):
    d = dominio(h)
    DOM[d] = DOM.get(d, 0) + 1
    return DOM[d] <= 5


for sid, url in PAGINAS.items():
    host = url.split("/")[2]
    if host not in ROB:
        f = Path(a.robots) / (host + ".txt")
        rp = urllib.robotparser.RobotFileParser()
        if f.exists():
            rp.parse(f.read_text(encoding="utf-8", errors="replace").splitlines()); ROB[host] = rp
        elif conta(host):
            st, b, e = CAN.buscar("https://%s/robots.txt" % host)
            rp.parse([] if st in (404, 410) else (b or b"").decode("utf-8", "replace").splitlines()); ROB[host] = rp
            out.append({"CASO": host + "/robots.txt", "URL": "https://%s/robots.txt" % host, "HTTP": st})
    if not ROB[host].can_fetch(CAP.UA, url):
        out.append({"CASO": sid, "URL": url, "ESTADO": "ROBOTS_PROIBE"}); continue
    if not conta(host):
        out.append({"CASO": sid, "URL": url, "ESTADO": "TETO_D38"}); continue
    w = 2.0 - (time.time() - ULT.get(host, 0))
    if w > 0:
        time.sleep(w)
    st, b, e = CAN.buscar(url); ULT[host] = time.time()
    h = hashlib.sha256(b or b"").hexdigest()
    (pasta / (sid.replace("~", "_") + ".bin")).write_bytes(b or b"")
    out.append({"CASO": sid, "URL": url, "HTTP": st, "ERRO": e, "BYTES": len(b or b""), "SHA256": h,
                "BYTES_EM": str(pasta / (sid.replace("~", "_") + ".bin")), "LIDO_EM": datetime.now(timezone.utc).isoformat()})
    print(sid, st, len(b or b""))
json.dump({"REDE_AUTORIZADA_POR": a.rede_autorizada, "PEDIDOS_POR_DOMINIO": DOM, "PAGINAS": out},
          open(pasta / "INDICE.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("pedidos por dominio:", DOM)
