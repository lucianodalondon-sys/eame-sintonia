"""T2-BOLETINS fase 1b — ARPAV (IT-T2-145/146): o que ha dentro de «AGROMETEOROLOGICO REGIONALE» e de
«Bollettino mese», pela REST API do Plone (++api++). Robots lido na fase 1 (LIDO, sem regras = tudo
permitido), reconferido aqui pelo mesmo leitor. Continua a conta D38 da fase 1. So com --rede-autorizada."""
import hashlib, importlib.util, json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
OUT = Path(sys.argv[1])
if "--rede-autorizada" not in sys.argv:
    sys.exit("RECUSA (D41.3)")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN, capturador as CAP  # noqa: E402,E401
_s = importlib.util.spec_from_file_location("robots_rfc9309", "C:/Users/London1/orca/workspaces/eame-sintonia/robots-rfc9309-v1/coleta/robots_rfc9309.py")
RR = importlib.util.module_from_spec(_s); sys.modules["robots_rfc9309"] = RR; _s.loader.exec_module(RR)
r = subprocess.run([sys.executable, "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py", "--portao-de-egresso", "IT"], capture_output=True, text=True)
assert '"EGRESS_GATE": "PASS"' in r.stdout, "portao nao da PASS IT"
F1 = json.loads((OUT / "FASE1.json").read_text(encoding="utf-8"))
rb = [x for x in F1["RESULTADOS"] if x["HOST"] == "www.arpa.veneto.it"][0]["ROBOTS"]
robots = RR.de_resposta(rb["HTTP"], Path(rb["EM"]).read_bytes())
CONTA = OUT / "PEDIDOS-POR-DOMINIO.json"; DOM = json.loads(CONTA.read_text(encoding="utf-8"))
res = []
URLS = sys.argv[3:] or ("https://www.arpa.veneto.it/++api++/temi-ambientali/agrometeo/bollettini/copy_of_andamento-annate-agrarie",
          "https://www.arpa.veneto.it/++api++/temi-ambientali/agrometeo/bollettini/bollettino-mese")
for u in URLS:
    dec = robots.decidir(CAP.UA, u)
    if not dec.permite or DOM.get("veneto.it", 0) >= 5:
        res.append({"URL": u, "FIM": "ROBOTS_RECUSA" if not dec.permite else "TETO_D38"}); continue
    time.sleep(5)
    DOM["veneto.it"] = DOM.get("veneto.it", 0) + 1; CONTA.write_text(json.dumps(DOM, indent=1), encoding="utf-8")
    st, b, e = CAN.buscar(u); b = b or b""
    h = hashlib.sha256(b).hexdigest(); p = OUT / "bytes" / ("%s.bin" % h[:20]); p.write_bytes(b)
    res.append({"URL": u, "HTTP": st, "ERRO": e, "BYTES": len(b), "SHA256": h, "EM": str(p), "ROBOTS": dec.regra,
                "LIDO_EM": datetime.now(timezone.utc).isoformat()})
    print(st, len(b), u)
(OUT / ("FASE1B-ARPAV%s.json" % ("-HTML" if sys.argv[3:] else ""))).write_text(json.dumps({"RESULTADOS": res, "PEDIDOS_POR_DOMINIO": DOM}, ensure_ascii=False, indent=1), encoding="utf-8")
print(DOM)
