"""Mutacao D39: cada ataque muda UMA linha, corre o teste, repoe o ficheiro (confere por sha)."""
import hashlib, os, subprocess, sys
from pathlib import Path

os.chdir(sys.argv[1])
ENV = dict(os.environ, HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9",
           PYTHONPATH="C:/Users/London1/.sintonia-libs", NODE_DISABLE_COMPILE_CACHE="1")
PY = [sys.executable, "-m", "unittest", "tests.test_robots_rfc9309"]
NODE = ["node", "provas/cortesia_http_local.mjs"]
ATAQUES = [
    ("P1 401/403 volta a AUSENTE", "coleta/robots_rfc9309.py",
     "    if status in (401, 403):\n        return Robots(ACCESS_DENIED", "    if False:\n        return Robots(ACCESS_DENIED", PY),
    ("P2 HTML perde o nome (vira ILEGIVEL)", "coleta/robots_rfc9309.py",
     'return Robots(INVALID_CONTENT, porque="HTML', 'return Robots(ILEGIVEL, porque="HTML', PY),
    ("P3 ACCESS_DENIED fica com o nome errado", "coleta/robots_rfc9309.py",
     'ACCESS_DENIED = "ROBOTS_ACCESS_DENIED"', 'ACCESS_DENIED = "ROBOTS_ILEGIVEL_403"', PY),
    ("P4 robo classifica como ROBOTS (Disallow)", "curadoria/worker.py",
     'return "BLOCK", dict(prova, CLASSE=rp.estado, PORQUE=dec.regra)',
     'return "BLOCK", dict(prova, CLASSE="ROBOTS", PORQUE=dec.regra)', PY),
    ("P5 livro perde o mapeamento (cai em CAPABILITY)", "curadoria/worker.py",
     '                "ROBOTS_ACCESS_DENIED": LC.CONTRACT_READY_ROUTE_BLOCKED,\n', '', PY),
    ("P6 livro perde o nome ao lado", "curadoria/worker.py",
     'extra=({"ROBOTS_ESTADO": detalhe["ROBOTS_ESTADO"]}', 'extra=({"X": detalhe["ROBOTS_ESTADO"]}', PY),
    ("P7 transporte deixa a excecao do dono atravessar", "coleta/scrap_http.py",
     "    if estado in (RR.INVALID_CONTENT, RR.ACCESS_DENIED):\n", "    if False:\n", PY),
    ("N1 coletor: 403 volta a AUSENTE", "coleta/italy_pilot_collect.mjs",
     'if (r.status === 401 || r.status === 403) return { estado: "ROBOTS_ACCESS_DENIED"',
     'if (false) return { estado: "ROBOTS_ACCESS_DENIED"', NODE),
    ("N2 coletor: HTML volta a ILEGIVEL", "coleta/italy_pilot_collect.mjs",
     'return { estado: "ROBOTS_INVALID_CONTENT", origemLida', 'return { estado: "ILEGIVEL", origemLida', NODE),
    ("N3 coletor: licenca nao recusa os estados D39", "coleta/italy_pilot_collect.mjs",
     '  if (rb.estado === "ROBOTS_ACCESS_DENIED" || rb.estado === "ROBOTS_INVALID_CONTENT")\n    return { recusado: rb.estado, porque: rb.porque };\n',
     '', NODE),
]
# O criterio Node era «nao aparece FALHAS=0». Na producao 290e7349 a C5 (teto D38) ja falha SEM
# mutacao, e esse criterio matava qualquer mutante Node de graca. Morto = aparece uma FALHA NOVA,
# comparada PELO NOME com a corrida sem mutacao (integracao ROBOTS-INTEGRADO).
import re
def falhas_node():
    r = subprocess.run(NODE, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    return set(re.findall(r"^\s*FALHA (.*)$", r.stdout + r.stderr, re.M))
FALHAS_SEM_MUTACAO = falhas_node()
print("NODE sem mutacao: %d falhas %s" % (len(FALHAS_SEM_MUTACAO), sorted(FALHAS_SEM_MUTACAO)), flush=True)
mortos = 0
for nome, f, de, para, cmd in ATAQUES:
    p = Path(f); orig = p.read_bytes(); h = hashlib.sha256(orig).hexdigest()
    t = orig.decode("utf-8")
    if "\r\n" in t:
        de, para = de.replace("\n", "\r\n"), para.replace("\n", "\r\n")
    assert t.count(de) == 1, (nome, "linha alvo nao encontrada 1x")
    p.write_bytes(t.replace(de, para).encode("utf-8"))
    try:
        if cmd is NODE:
            morto = bool(falhas_node() - FALHAS_SEM_MUTACAO)
        else:
            r = subprocess.run(cmd, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
            morto = r.returncode != 0
    finally:
        p.write_bytes(orig)
        assert hashlib.sha256(p.read_bytes()).hexdigest() == h, "restauro falhou: " + f
    mortos += morto
    print(("MORTO   " if morto else "VIVO    ") + nome, flush=True)
print("D39_MUTACAO mortos=%d de %d" % (mortos, len(ATAQUES)))
