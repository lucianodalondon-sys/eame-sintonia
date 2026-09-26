"""D47 — mutacao do corte STRIP_SUFFIX e da IDENTITY explicita: cada mutante numa COPIA da arvore
(sem data/, portal, mapa), sem .pyc (PYTHONDONTWRITEBYTECODE); a copia SEM mutacao tem de ficar verde
primeiro. Corre test_strip_suffix + test_receita_identidade; o mutante tem de ser MORTO (teste vermelho)."""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]
MUTANTES = [
    ("canario: nao corta", "curadoria/canario.py",
     "            if strip_suffix and h.endswith(strip_suffix):\n                h = h[:-len(strip_suffix)]\n", ""),
    ("canario: ignora o corte do contrato", "curadoria/canario.py",
     'hrefs_da_entrada(b, aq["INDEX_URL"], aq.get("STRIP_SUFFIX"))', 'hrefs_da_entrada(b, aq["INDEX_URL"])'),
    ("porta: nao grava o corte", "curadoria/reparar_contrato.py", '        aq["STRIP_SUFFIX"] = corte', "        pass"),
    ("porta: aceita corte vazio", "curadoria/reparar_contrato.py",
     "if not isinstance(corte, str) or not corte.strip() or corte != corte.strip():", "if not isinstance(corte, str):"),
    ("porta: sem proveniencia do corte", "curadoria/reparar_contrato.py",
     '        **({"STRIP_SUFFIX": corte} if corte is not None else {}),\n', ""),
    ("porta: nao confere a identidade no motor", "curadoria/reparar_contrato.py",
     '        erro = _conferir_identidade_no_motor(novo.get("SOURCE_ID"), ident)', "        erro = None"),
    ("porta: nao grava a identidade", "curadoria/reparar_contrato.py",
     '        novo["IDENTITY"] = copy.deepcopy(ident)', "        pass"),
    ("cli: SO_CONFERIR aceita tudo", "regras/identidade_do_motor_cli.mjs",
     "    conferirIdentidade(pedido.SOURCE_ID, pedido.IDENTITY);", "    void 0;"),
    ("canario pdf: identidade a mao (como antes)", "curadoria/canario.py",
     "capturas.\n    ident = identidade_pelo_motor(c, alvo, b2, texto_da_ligacao)",
     'capturas.\n    ident = {"DOCUMENT_ID": c["IDENTITY"]["DOCUMENT_ID"].replace("{doc.1}", re.sub(r"^https?://[^/]+/?", "", alvo).rstrip("/"))}'),
]
mortos = 0
MUTANTES.insert(0, ("BASE sem mutacao (tem de ficar VERDE)", "curadoria/canario.py", "def hrefs_da_entrada(", "def hrefs_da_entrada("))
for nome, f, de, para in MUTANTES:
    tmp = Path(tempfile.mkdtemp(prefix="mut_t2b_"))
    try:
        # a arvore inteira menos o que e grande e nao e codigo (data/, portal, mapa, .git)
        FORA = {".git", "data", "italia-portale", "system-map", "build", "docs", "node_modules"}
        for d in RAIZ.iterdir():
            if d.name in FORA:
                continue
            if d.is_dir():
                shutil.copytree(d, tmp / d.name, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
            else:
                shutil.copy2(d, tmp / d.name)
        alvo = tmp / f; s = alvo.read_text(encoding="utf-8")
        assert s.count(de) == 1, (nome, s.count(de))
        alvo.write_text(s.replace(de, para), encoding="utf-8")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, "-m", "unittest", "test_strip_suffix", "test_receita_identidade"], cwd=tmp / "curadoria",
                           capture_output=True, text=True, env=env, timeout=600)
        if nome.startswith("BASE"):
            print("BASE", "VERDE" if r.returncode == 0 else "VERMELHA", (r.stderr.strip().splitlines() or [""])[-1])
            if r.returncode != 0:
                print(r.stderr[-2000:]); sys.exit("a copia sem mutacao nao passa: a medicao nao vale")
            continue
        # vermelho = morto (a base e verde na mesma copia); o erro mostrado tem de ser do teste, nao de import
        import re as _re
        erros = sorted(set(_re.findall(r"^(\w+(?:Error|Exception)):", r.stderr, _re.M)))
        morto = r.returncode != 0 and "ModuleNotFoundError" not in erros and "SyntaxError" not in erros
        mortos += morto
        print("MORTO " if morto else "VIVO  ", nome, "|", (r.stderr.strip().splitlines() or [""])[-1], erros)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print("MUTACAO_T2B (STRIP_SUFFIX + IDENTITY) · mortos=%d de %d" % (mortos, len(MUTANTES) - 1))
sys.exit(0 if mortos == len(MUTANTES) - 1 else 1)
