"""BOLETINS-V2 — mutacao da LISTA UNICA das reguas que admitem (ready_split.REGUAS_QUE_ADMITEM). Cada mutante
numa COPIA da arvore (sem data/, portal, mapa, .git), sem .pyc; a copia SEM mutacao tem de ficar VERDE primeiro
nas provas escolhidas. Os testes do SOCIAL e dos BOLETINS tem de morder a lista inteira — nao so metade.
uso: py provas/boletins_data_local/mutacao_lista_unica.py"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SOCIAL = [sys.executable, "-m", "unittest", "test_regua_social", "test_soc_onda2_social"]
BOLETINS = [sys.executable, "-m", "unittest", "test_pagina_boletim", "test_um_so_canario_promove"]
RS, W = "curadoria/ready_split.py", "curadoria/worker.py"
UNICA = "REGUAS_QUE_ADMITEM = frozenset({REGUA_CURRENT, REGUA_SOCIAL, REGUA_PAGINA_BOLETIM})"
MUTANTES = [
    ("a lista esquece a regua SOCIAL", RS, UNICA, "REGUAS_QUE_ADMITEM = frozenset({REGUA_CURRENT, REGUA_PAGINA_BOLETIM})", [SOCIAL]),
    ("a lista esquece a regua PAGINA_BOLETIM", RS, UNICA, "REGUAS_QUE_ADMITEM = frozenset({REGUA_CURRENT, REGUA_SOCIAL})", [BOLETINS]),
    ("o worker volta a so aceitar DETAIL/v1", W, 'if regua["REGUA"] not in RS.REGUAS_QUE_ADMITEM:',
     'if regua["REGUA"] != RS.REGUA_CURRENT:', [BOLETINS]),
]
FORA = {".git", "data", "italia-portale", "system-map", "build", "docs", "node_modules"}


def copia():
    tmp = Path(tempfile.mkdtemp(prefix="mut_lista_"))
    for d in RAIZ.iterdir():
        if d.name in FORA:
            continue
        if d.is_dir():
            shutil.copytree(d, tmp / d.name, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
        else:
            shutil.copy2(d, tmp / d.name)
    return tmp


def correr(tmp, cmds):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return [(r.returncode, (r.stdout + r.stderr)[-1500:]) for r in
            (subprocess.run(c, cwd=tmp / "curadoria", capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=env, timeout=900) for c in cmds)]


tmp = copia()
try:
    base = correr(tmp, [SOCIAL, BOLETINS])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
if any(rc for rc, _ in base):
    for rc, out in base:
        print(rc, out[-800:])
    sys.exit("a copia sem mutacao nao passa: a medicao nao vale")
print("BASE VERDE (social, boletins)")
mortos = 0
for nome, f, de, para, cmds in MUTANTES:
    tmp = copia()
    try:
        alvo = tmp / f
        s = alvo.read_text(encoding="utf-8")
        assert s.count(de) == 1, (nome, s.count(de))
        alvo.write_text(s.replace(de, para), encoding="utf-8", newline="\n")
        res = correr(tmp, cmds)
        erros = sorted({e for _, out in res for e in re.findall(r"(ModuleNotFoundError|SyntaxError|ImportError)", out)})
        morto = any(rc for rc, _ in res) and not erros
        mortos += morto
        print("MORTO " if morto else "VIVO  ", nome, "|", " / ".join(out.strip().splitlines()[-1][:80] for _, out in res), erros)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print("MUTACAO_LISTA_UNICA · mortos=%d de %d" % (mortos, len(MUTANTES)))
sys.exit(0 if mortos == len(MUTANTES) else 1)
