"""LOTE4-FINAL: a bateria INTEIRA por nome (o metodo do LOTE4-VERIFICAR). uso: python3 <este> <raiz> <saida.json> [workers]"""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
RAIZ, SAIDA, NJ = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 2
fs = subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True).stdout.split()
def e_teste(f):
    n = f.rsplit("/", 1)[-1]
    if n.endswith(".py") and (n.startswith("test_") or n.endswith("_test.py")): return True
    if f.startswith("provas/testa_") and n.endswith(".py"): return True
    if n.endswith("_test.mjs"): return True
    if f.startswith("system-map/tests/") and n.endswith(".mjs"): return True
    return False
fs = sorted(f for f in fs if e_teste(f) and "/fixtures/" not in f)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
           HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", http_proxy="http://127.0.0.1:9",
           https_proxy="http://127.0.0.1:9", ALL_PROXY="http://127.0.0.1:9", NO_PROXY="127.0.0.1,localhost",
           no_proxy="127.0.0.1,localhost")
def corre(f):
    t = time.time()
    cmd = ["node", f] if f.endswith(".mjs") else [sys.executable, f]
    try:
        r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=1500)
        out, rc = r.stdout + "\n" + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", "TIMEOUT"
    falhas = set(re.findall(r"^(?:FAIL|ERROR): (.+?)\s*$", out, re.M))
    falhas |= set(l.strip()[:200] for l in out.splitlines() if re.match(r"^\s*(✗|✘|FALHA\b|FAIL\b|not ok\b|reprovad)", l) and not l.startswith(("FAIL:", "ERROR:")))
    ran = re.search(r"^Ran (\d+) test", out, re.M)
    return f, {"CORRIDOS": int(ran.group(1)) if ran else None, "FALHAS": sorted(falhas), "RC": rc, "SEG": round(time.time() - t, 1),
               "FIM": (out.strip().splitlines() or [""])[-1][:160]}
sm = [f for f in fs if f.startswith("system-map/")]
outros = [f for f in fs if f not in sm]
res = {}
with ThreadPoolExecutor(NJ) as ex:
    fut = ex.map(corre, outros)
    serial = [corre(f) for f in sm]  # o system-map regera ficheiros da arvore: um de cada vez
    for f, v in list(fut) + serial: res[f] = v
SAIDA.write_text(json.dumps(dict(sorted(res.items())), ensure_ascii=False, indent=1), encoding="utf-8")
print(len(res), "ficheiros", sum(len(v["FALHAS"]) for v in res.values()), "falhas por nome", sum(1 for v in res.values() if v["RC"] != 0), "vermelhos")
