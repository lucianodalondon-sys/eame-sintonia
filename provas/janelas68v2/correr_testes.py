import sys, os, subprocess, json, re
raiz, out = sys.argv[1], sys.argv[2]
files = sys.argv[3:]
env = dict(os.environ, HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", PYTHONUTF8="1",
           PYTHONIOENCODING="utf-8", PYTHONPATH=os.path.join(raiz, ".sintonia-libs"))
res = {}
for f in files:
    d, b = os.path.split(f)
    if not os.path.exists(os.path.join(raiz, f)):
        res[f + "::AUSENTE"] = "AUSENTE"; continue
    r = subprocess.run([sys.executable, "-m", "unittest", "-v", b[:-3]], cwd=os.path.join(raiz, d), env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    for m in re.finditer(r"^(test\w+) \(([\w.]+)\)(?: \((.*?)\))? \.\.\. (ok|FAIL|ERROR|skipped.*)$", r.stderr, re.M):
        k = f + "::" + m.group(2) + "." + m.group(1)
        v = m.group(4).split()[0].upper()
        if res.get(k) in ("FAIL", "ERROR"): continue
        res[k] = v
    for m in re.finditer(r"^(FAIL|ERROR): (test\w+) \(([\w.]+)\)", r.stderr, re.M):
        res[f + "::" + m.group(3) + "." + m.group(2)] = m.group(1)
    if "Ran " not in r.stderr:
        res[f + "::LOAD"] = "ERROR"
json.dump(res, open(out, "w"), indent=0)
from collections import Counter; print(raiz, Counter(res.values()))
