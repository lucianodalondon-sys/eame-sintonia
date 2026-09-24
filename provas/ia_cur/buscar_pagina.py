"""IA-CUR: o agente le uma pagina VIVA pelo MESMO transporte do robo de fontes.
Portao de egresso (superficie/rede.py, consenso) no inicio; robots.txt pela porta do robo
(gate_de_rota.robots_de/permitido); pausa de 2 s por pedido; os bytes ficam guardados com sha256
em provas/ia_cur/paginas/<caso>/ (fora do Git se forem grandes) e o registo em PAGINAS.jsonl.
uso: py buscar_pagina.py <raiz da copia> <caso> <url> [<url> ...]"""
import hashlib, json, os, subprocess, sys, time
from datetime import datetime, timezone
from urllib.parse import urlparse

RAIZ, CASO, URLS = sys.argv[1], sys.argv[2], sys.argv[3:]
sys.path.insert(0, RAIZ + "/curadoria")
import canario as CAN, gate_de_rota as GATE     # noqa: E402

r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"], cwd=RAIZ,
                   capture_output=True, text=True)
if '"EGRESS_GATE": "PASS"' not in r.stdout:
    sys.exit("PARAR: egresso IT nao passa — nenhum pedido feito")
OUT = os.path.join("C:/cur/ia/paginas", CASO)
os.makedirs(OUT, exist_ok=True)
reg = open("C:/cur/ia/PAGINAS.jsonl", "a", encoding="utf-8")
for i, url in enumerate(URLS):
    host = urlparse(url).netloc
    try:
        rp, origem = GATE.robots_de(host)
    except Exception as e:  # noqa: BLE001
        print("ROBOTS ILEGIVEL", url, type(e).__name__); continue
    if not GATE.permitido(url, rp):
        print("ROBOTS PROIBE", url); reg.write(json.dumps({"CASO": CASO, "URL": url, "ESTADO": "ROBOTS_PROIBE"}) + "\n"); continue
    st, b, err = CAN.buscar(url)
    sha = hashlib.sha256(b).hexdigest() if b else None
    nome = "%02d.bin" % i
    if b:
        open(os.path.join(OUT, nome), "wb").write(b)
    e = {"CASO": CASO, "URL": url, "HTTP": st, "ERRO": err, "SHA256": sha, "BYTES": len(b),
         "EGRESSO": "IT (consenso)", "LIDO_EM": datetime.now(timezone.utc).isoformat(),
         "BYTES_EM": "C:/cur/ia/paginas/%s/%s" % (CASO, nome) if b else None}
    reg.write(json.dumps(e, ensure_ascii=False) + "\n"); reg.flush()
    print(CASO, st, len(b), (sha or "")[:16], url)
    time.sleep(2)
