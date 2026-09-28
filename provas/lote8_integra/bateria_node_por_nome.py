import json, os, re, subprocess, sys
raiz, saida = sys.argv[1], sys.argv[2]
fs = sorted([f"regras/{f}" for f in os.listdir(f"{raiz}/regras") if f.endswith("test.mjs")] +
            [f"tests/{f}" for f in os.listdir(f"{raiz}/tests") if f.endswith(".mjs")] +
            [f"system-map/tests/{f}" for f in os.listdir(f"{raiz}/system-map/tests") if f.endswith(".mjs")])
env = dict(os.environ, HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
res = {}
for f in fs:
    try:
        p = subprocess.run(["node", f], cwd=raiz, env=env, capture_output=True, text=True, timeout=600)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired:
        out, rc = "<TIMEOUT>", "TIMEOUT"
    falhas = sorted({l.strip()[:160] for l in out.splitlines()
                     if re.match(r"^\s*(FAIL\b|FALHOU\b|FALHA\b|✗|✘|not ok|NOK\b|  x )", l)})
    res[f] = {"RC": str(rc), "FALHAS": falhas, "RESUMO": [l for l in out.splitlines() if re.search(r"passou|PASSOU|provas|passaram|FALHAS=", l)][-2:]}
json.dump(res, open(saida, "w"), ensure_ascii=False, indent=1)
print({f: (v["RC"], len(v["FALHAS"])) for f, v in res.items()})
