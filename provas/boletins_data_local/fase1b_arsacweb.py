"""BOLETINS D61/D62 fase 1 — a lista de cada uma das 4 rotas novas de boletim (ARSAC, Molise, VdA, Veneto).

Rede so com --rede-autorizada (D41.3). Portao de consenso PASS IT antes de tudo. Fila FILTRADA as 7
agencias (6 anfitrioes). Robots LIDO NA HORA e classificado pelo leitor da casa RFC 9309 + D39
(`coleta/robots_rfc9309.py`, ramo robots-rfc9309-v1 9057284d — o leitor unico, pronto para instalar):
recusa em INVALID_CONTENT / ACCESS_DENIED / INACESSIVEL. Depois 1 pagina por anfitriao (a que o acervo
aponta como a do boletim, ou a entrada). Teto D38: 5 por dominio, contado num ficheiro que a fase 2 continua.
uso: py provas/boletins_data_local/fase1_listas.py <pasta saida> --rede-autorizada <missao>"""
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
ap.add_argument("saida")
ap.add_argument("--rede-autorizada")
a = ap.parse_args()
if not (a.rede_autorizada or "").strip():
    sys.exit("RECUSA (D41.3): sem --rede-autorizada <missao> esta fase nao vai a rede")
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

ALVOS = [   # arsacweb.it: onde as edicoes da ARSAC vivem (a pagina de arsac.calabria.it so as anuncia)
    (["IT-T2-148"], "https://www.arsacweb.it/"),
]
OUT = Path(a.saida); (OUT / "bytes").mkdir(parents=True, exist_ok=True)
CONTA = OUT / "PEDIDOS-POR-DOMINIO.json"
DOM = json.loads(CONTA.read_text(encoding="utf-8")) if CONTA.exists() else {}
PAUSA = 5.0


def dominio(host):
    return ".".join(host.split(".")[-2:])


def pedir(url):
    host = url.split("/")[2]
    if DOM.get(dominio(host), 0) >= 5:
        return None
    DOM[dominio(host)] = DOM.get(dominio(host), 0) + 1
    CONTA.write_text(json.dumps(DOM, indent=1), encoding="utf-8")
    st, b, e = CAN.buscar(url)
    b = b or b""
    h = hashlib.sha256(b).hexdigest()
    (OUT / "bytes" / ("%s.bin" % h[:20])).write_bytes(b)
    return {"URL": url, "HTTP": st, "ERRO": e, "BYTES": len(b), "SHA256": h,
            "EM": str(OUT / "bytes" / ("%s.bin" % h[:20])), "LIDO_EM": datetime.now(timezone.utc).isoformat()}


res = []
for sids, url in ALVOS:
    host = url.split("/")[2]
    lin = {"SOURCE_IDS": sids, "HOST": host}
    rb = pedir("https://%s/robots.txt" % host)
    if rb is None:
        lin["FIM"] = "TETO_D38"; res.append(lin); continue
    corpo = Path(rb["EM"]).read_bytes()
    robots = RR.de_resposta(rb["HTTP"] or None, corpo, erro=rb["ERRO"])
    dec = robots.decidir(CAP.UA, url)
    lin["ROBOTS"] = dict(rb, ESTADO=robots.estado, PORQUE=robots.porque, CRAWL_DELAY=robots.crawl_delay(CAP.UA))
    lin["ROBOTS_PAGINA"] = {"PERMITE": dec.permite, "REGRA": dec.regra}
    if not dec.permite:
        lin["FIM"] = "ROBOTS_RECUSA"; res.append(lin); continue
    time.sleep(max(PAUSA, robots.crawl_delay(CAP.UA) or 0))
    pg = pedir(url)
    lin["PAGINA"] = pg
    lin["FIM"] = "LIDA" if pg else "TETO_D38"
    res.append(lin)
    print(host, rb["HTTP"], robots.estado, dec.permite, pg and pg["HTTP"], pg and pg["BYTES"])
(OUT / "FASE1-ARSACWEB.json").write_text(json.dumps({"FASE": "BOLETINS D61/D62 fase 1", "REDE_AUTORIZADA_POR": a.rede_autorizada,
                                            "ROBOTS_LEITOR": RR.VERSAO, "RESULTADOS": res, "PEDIDOS_POR_DOMINIO": DOM},
                                           ensure_ascii=False, indent=1), encoding="utf-8")
print("pedidos por dominio:", DOM)
