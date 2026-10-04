"""C-JS: confirmar as saidas publicas de dados das fontes «JavaScript» (D42 (3)). Pedidos limitados:
Emilia-Romagna 1 (a REST API ++api++ do Plone; robots da copia da medicao RFC), agrometeopuglia 2
(robots + Bollettini.js), SIMfito 2 (robots + /bollettini). Portao de consenso PASS IT; robots pelo
leitor da casa (curadoria/gate_de_rota.py da producao, via janela-formas-v1 = 7cdb7ea4 neste ponto);
teto D38 5/dominio; 2 s por anfitriao. Bytes em C:/cur/cjs/bytes, indice em C:/cur/cjs/INDICE.json."""
import hashlib, json, subprocess, sys, time, urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path("C:/Users/London1/orca/workspaces/eame-sintonia/janela-formas-v1")
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN, capturador as CAP, gate_de_rota as GATE   # noqa: E402

r = subprocess.run([sys.executable, "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py",
                    "--portao-de-egresso", "IT"], capture_output=True, text=True)
assert '"EGRESS_GATE": "PASS"' in r.stdout, "portao de egresso nao da PASS IT"
ALVOS = [
    ("IT-T3-013/028", "https://agricoltura.regione.emilia-romagna.it/++api++/fitosanitario/difesa-sostenibile/bollettini/bollettini-interprovinciali-di-produzione-integrata-e-biologica-2026"),
    ("IT-T2-150/151", "https://www.agrometeopuglia.it/modules/custom/Bollettini/js/Bollettini.js?v=1"),
    ("IT-T3-026", "https://simfito.regione.campania.it/bollettini"),
]
PASTA = Path("C:/cur/cjs/bytes"); PASTA.mkdir(parents=True, exist_ok=True)
DOM, ROB, out, ULT = {}, {}, [], {}


def dom(h):
    return h[4:] if h.startswith("www.") else h


for caso, url in ALVOS:
    host = url.split("/")[2]
    if host not in ROB:
        copia = Path("C:/cur/rfc/rede/robots") / (host + ".txt")
        if copia.exists():
            rp = urllib.robotparser.RobotFileParser(); rp.parse(copia.read_text(encoding="utf-8", errors="replace").splitlines())
            ROB[host] = (rp, "copia da medicao RFC")
        else:
            DOM[dom(host)] = DOM.get(dom(host), 0) + 1
            rp, origem = GATE.robots_de(host)
            ROB[host] = (rp, "lido agora: " + str(origem)[:160])
    rp, de_onde = ROB[host]
    linha = {"CASO": caso, "URL": url, "ROBOTS": de_onde}
    if not GATE.permitido(url, rp):
        out.append(dict(linha, ESTADO="ROBOTS_PROIBE")); continue
    if DOM.get(dom(host), 0) >= 5:
        out.append(dict(linha, ESTADO="TETO_D38")); continue
    w = 2.0 - (time.time() - ULT.get(host, 0))
    if w > 0: time.sleep(w)
    DOM[dom(host)] = DOM.get(dom(host), 0) + 1
    st, b, e = CAN.buscar(url); ULT[host] = time.time()
    h = hashlib.sha256(b or b"").hexdigest()
    p = PASTA / ("%s.bin" % h[:20]); p.write_bytes(b or b"")
    out.append(dict(linha, ESTADO="LIDO", HTTP=st, ERRO=e, BYTES=len(b or b""), SHA256=h, BYTES_EM=str(p),
                    LIDO_EM=datetime.now(timezone.utc).isoformat()))
    print(caso, st, len(b or b""), (b or b"")[:120])
json.dump({"PEDIDOS_POR_DOMINIO": DOM, "PAGINAS": out}, open("C:/cur/cjs/INDICE.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("pedidos por dominio:", DOM)
