"""SCRAP-EVOLUCAO · peca 6 — quanto de memoria custa UMA pagina no navegador real (patchright + chromium). Sem rede.

    <python com patchright> provas/scrap_evolucao/medir_ram_navegador.py <pasta com .html> [saida.json]

O patchright NAO e dependencia do repositorio (zero dependencia nova nesta fase): corre-se com o Python de estudo
que o tem (medido: C:/g/scrapling-estudo/.venv-full). As paginas sao servidas por um servidor em 127.0.0.1 e o
chromium sai por um proxy numa porta fechada (127.0.0.1:9): tudo o que a pagina pediria fora (scripts, imagens,
analytics) falha. Por isso o numero e um PISO — a pagina real, com os recursos dela, custa mais.

Mede a soma da memoria (Working Set e Private) da arvore de processos do chromium, por instante:
  VAZIO (navegador aberto, sem pagina) · cada pagina aberta, uma de cada vez, num contexto novo · o pico.
"""
import http.server
import json
import os
import subprocess
import sys
import threading
import time


def arvore(pid_raiz):
    """(working set, private) em MB da arvore de processos de `pid_raiz` (Win32_Process)."""
    ps = ("$p=Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,WorkingSetSize,PrivatePageCount;"
          "$p | ConvertTo-Json -Compress")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
    todos = json.loads(r.stdout)
    filhos = {}
    for x in todos:
        filhos.setdefault(x["ParentProcessId"], []).append(x)
    ws = pv = n = 0
    pilha = [pid_raiz]
    vistos = set()
    while pilha:
        p = pilha.pop()
        for x in filhos.get(p, []):
            if x["ProcessId"] in vistos:
                continue
            vistos.add(x["ProcessId"])
            ws += x["WorkingSetSize"] or 0
            pv += x["PrivatePageCount"] or 0
            n += 1
            pilha.append(x["ProcessId"])
    return round(ws / 2**20, 1), round(pv / 2**20, 1), n


def main(pasta, saida=None):
    from patchright.sync_api import sync_playwright
    paginas = sorted(f for f in os.listdir(pasta) if f.endswith(".html"))

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=pasta, **k)

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    eu = os.getpid()
    out = {"PAGINAS": [], "NOTA": "piso: recursos externos bloqueados (proxy fechado); a pagina real custa mais"}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--proxy-server=http://127.0.0.1:9",
                                                    "--disable-background-networking"])
        time.sleep(2)
        out["VAZIO_MB"] = dict(zip(("WORKING_SET", "PRIVADA", "PROCESSOS"), arvore(eu)))
        pico = 0
        for f in paginas:
            ctx = b.new_context(locale="it-IT")
            pg = ctx.new_page()
            t = time.time()
            pg.goto(base + f, wait_until="load", timeout=60000)
            time.sleep(2)
            ws, pv, n = arvore(eu)
            pico = max(pico, ws)
            out["PAGINAS"].append({"PAGINA": f, "BYTES": os.path.getsize(os.path.join(pasta, f)),
                                   "WORKING_SET_MB": ws, "PRIVADA_MB": pv, "PROCESSOS": n,
                                   "A_MAIS_QUE_VAZIO_MB": round(ws - out["VAZIO_MB"]["WORKING_SET"], 1),
                                   "SEGUNDOS": round(time.time() - t, 1)})
            ctx.close()
            time.sleep(1)
        out["PICO_WORKING_SET_MB"] = pico
        b.close()
    srv.shutdown()
    if saida:
        with open(saida, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
