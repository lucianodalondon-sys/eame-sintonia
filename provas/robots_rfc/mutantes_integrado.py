"""Mutantes extra da integracao: 2.o leitor de robots e guarda do robots inteiro (sha256)."""
import hashlib, os, subprocess, sys
from pathlib import Path
os.chdir(sys.argv[1])
PY = [sys.executable, "-m", "unittest", "tests.test_robots_rfc9309"]
ENV = dict(os.environ, HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
# (nome, ficheiro, de, para) ; de=None => ficheiro NOVO com o conteudo `para`
ATAQUES = [
    ("S1 nasce leitor novo com urllib.robotparser", "curadoria/leitor_intruso.py", None,
     "import urllib.robotparser\n"),
    ("S2 nasce leitor novo com RobotFileParser()", "coleta/leitor_intruso.py", None,
     "from urllib import robotparser as r\nrp = r.RobotFileParser()\n"),
    ("S3 descobrir.py le Disallow por conta propria", "curadoria/descobrir.py",
     "_robots_cache: dict[str, \"RR.Robots\"] = {}\n",
     "_robots_cache: dict[str, \"RR.Robots\"] = {}\n_x = lambda k: k.lower() == 'disallow'\n"),
    ("S4 gate_de_rota decide sozinho (ignora o dono: tudo permitido)", "curadoria/gate_de_rota.py",
     "    return rp.can_fetch(CAP.UA, url)\n", "    return True\n"),
    ("S5 gate_de_rota: decisao sem o dono (Decisao inventada)", "curadoria/gate_de_rota.py",
     "    return rp.decidir(CAP.UA, url)\n", "    return RR.Decisao(True, 'x', rp.estado)\n"),
    ("H1 sha256 so dos 120 primeiros", "curadoria/worker.py",
     'hashlib.sha256((rp.texto or "").encode("utf-8")).hexdigest()',
     'hashlib.sha256((rp.texto or "")[:120].encode("utf-8")).hexdigest()'),
    ("H2 tamanho do recorte, nao do inteiro", "curadoria/worker.py",
     '"ROBOTS_CARACTERES": len(rp.texto or "")', '"ROBOTS_CARACTERES": len(origem[:120])'),
    ("H3 sha256 do texto vazio", "curadoria/worker.py",
     'hashlib.sha256((rp.texto or "").encode("utf-8")).hexdigest()', 'hashlib.sha256(b"").hexdigest()'),
]
mortos = 0
for nome, f, de, para in ATAQUES:
    p = Path(f); novo = de is None
    if novo:
        assert not p.exists(); p.write_text(para, encoding="utf-8")
    else:
        orig = p.read_bytes(); h = hashlib.sha256(orig).hexdigest(); t = orig.decode("utf-8")
        assert t.count(de) == 1, (nome, "alvo nao encontrado 1x")
        p.write_bytes(t.replace(de, para).encode("utf-8"))
    try:
        r = subprocess.run(PY, env=ENV, capture_output=True, text=True, timeout=900)
        morto = r.returncode != 0
    finally:
        if novo:
            p.unlink()
        else:
            p.write_bytes(orig); assert hashlib.sha256(p.read_bytes()).hexdigest() == h
    mortos += morto
    print(("MORTO   " if morto else "VIVO    ") + nome, flush=True)
print("INTEGRADO_MUTACAO mortos=%d de %d" % (mortos, len(ATAQUES)))
