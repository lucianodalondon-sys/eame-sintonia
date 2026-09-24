"""LADO DO ROBO da 1.a execucao da bancada: busca as paginas dos casos do lote (o agente nao vai a
rede). Transporte do robo (canario.buscar), robots pela porta do robo, 2 s por anfitriao, portao de
egresso IT no inicio e de 10 em 10. Bytes em C:/cur/bancada/paginas/, indice PAGINAS.jsonl.
uso: py buscar_lote.py <raiz da copia> <FILA.json> <n>"""
import hashlib, json, os, subprocess, sys, time
RAIZ, FILA, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.chdir(RAIZ); sys.path.insert(0, RAIZ + "/curadoria")
import canario as C, gate_de_rota as G   # noqa: E402

V = "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/"
cand = {x["CANDIDATA_ID"]: x for x in json.load(open(V + "candidatas/FONTES-CANDIDATAS.json", encoding="utf-8"))["CANDIDATAS"]}
casos = json.load(open(FILA, encoding="utf-8"))["CASOS"][:N]
OUT = "C:/cur/bancada/paginas"; os.makedirs(OUT, exist_ok=True)
idx = open("C:/cur/bancada/PAGINAS.jsonl", "a", encoding="utf-8")
ULT, ROB, n = {}, {}, [0]


def egresso():
    r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"], capture_output=True, text=True)
    return '"EGRESS_GATE": "PASS"' in r.stdout


def pega(caso, url):
    host = url.split("/")[2]
    if host not in ROB:
        try:
            ROB[host] = G.robots_de(host)[0]
        except Exception:        # noqa: BLE001
            ROB[host] = None
    l = {"CASO": caso, "URL": url, "LIDO_EM": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if ROB[host] is None:
        l["ESTADO"] = "ROBOTS_ILEGIVEL"
    elif not G.permitido(url, ROB[host]):
        l["ESTADO"] = "ROBOTS_PROIBE"
    else:
        if n[0] % 10 == 0 and not egresso():
            sys.exit("PARAR: egresso IT nao passa")
        w = 2.0 - (time.time() - ULT.get(host, 0))
        if w > 0: time.sleep(w)
        st, b, e = C.buscar(url); ULT[host] = time.time(); n[0] += 1
        h = hashlib.sha256(b).hexdigest()
        p = "%s/%s-%s.bin" % (OUT, caso, h[:12]); open(p, "wb").write(b)
        l.update(HTTP=st, ERRO=e, BYTES=len(b), SHA256=h, BYTES_EM=p, EGRESSO="IT (consenso)")
    idx.write(json.dumps(l, ensure_ascii=False) + "\n"); idx.flush()
    print(caso, l.get("HTTP", l.get("ESTADO")), l.get("BYTES"), url[:80], flush=True)


for c in casos:
    if c["PERGUNTA"] == "RELEVANCIA_D2":
        continue                     # bytes ja guardados (C:/cur/d32/recusas)
    url = c["ENTRADA"] or (cand.get(c["CASO"]) or {}).get("URL")
    if url:
        pega(c["CASO"], url)
print("pedidos:", n[0])
