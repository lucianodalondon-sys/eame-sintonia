"""YT-403 · prova de mutacao — cada regra nova, estragada de proposito, tem de fazer um teste falhar.

    py provas/yt403/mutantes_yt403.py [saida.json]

Cada mutante troca UM trecho exacto num ficheiro, corre so os testes que guardam essa regra e repoe os bytes
originais (conferidos por sha256) — nunca `git checkout`. Os .pyc vao para uma pasta propria por mutante
(`-X pycache_prefix`): um mutante do mesmo tamanho nao engana a cache.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
T = [PY, "-m", "unittest", "test_yt_403"]
A, S, Y, F = ("coleta/adaptador_youtube.py", "coleta/scrap_colheita.py", "ferramentas/youtube_transcrever.py",
              "ferramentas/yt_dlp_com_freio.py")

MUTANTES = [
    ('403 volta a ser fonte doente', A,
     "    if 'http error 403' in m or '403: forbidden' in m:\n        return 'BLOCKED'\n",
     '', T, "tests"),
    ('yt_dlp ausente volta a ser fonte doente', A,
     "    if any(x in m for x in ('no module named', 'modulenotfounderror', 'importerror')):\n        return 'EXECUTOR_UNAVAILABLE'\n",
     '', T, "tests"),
    ('o aviso decide a falha', A,
     "    m = str(motivo or '').split(' | ')[0].lower()",
     "    m = str(motivo or '').lower()", T, "tests"),
    ('o CHECK volta a perguntar so pelo programa', A,
     '    if not _yt_dlp_do_freio()[0]:\n',
     '    if False:\n', T, "tests"),
    ('--no-warnings de volta', Y,
     "    return ['-q', '--print-traffic',",
     "    return ['-q', '--no-warnings', '--print-traffic',", T, "tests"),
    ('a fatia 0 e ignorada', Y,
     "    return None if v == '0' else v\n",
     '    return v\n', T, "tests"),
    ('o motivo so leva a ultima linha', Y,
     "    return (' | '.join(erro + avisos))[:600]",
     "    return (' | '.join(erro))[:600]", T, "tests"),
    ('o filho ignora a pasta da casa', F,
     'def instalar():\n    _pasta_a_frente()\n',
     'def instalar():\n', T, "tests"),
    ('SINTONIA_YT_DLP_DIR ignorado', F,
     '    for p in (os.environ.get("SINTONIA_YT_DLP_DIR"), PASTA_DA_CASA):',
     '    for p in (PASTA_DA_CASA,):', T, "tests"),
    ('zero por falha volta a ser zero legitimo', S,
     '            if res and FA.e_falha(res):\n',
     '            if False:\n', T, "tests"),
    ('o processo que falhou sai com 0', S,
     "    return 3 if envelope.get('ESTADO') == rc.FAILED else 0\n",
     '    return 0\n', T, "tests"),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(saida=None):
    res = []
    for nome, rel, antes, depois, cmd, cwd in MUTANTES:
        p = os.path.join(RAIZ, rel)
        orig = open(p, "rb").read()
        texto = orig.decode("utf-8")
        if "\r\n" in texto and "\n" in antes and "\r\n" not in antes:
            # a copia de trabalho pode estar em CRLF (autocrlf) e o Git em LF: a ancora segue o ficheiro
            antes, depois = antes.replace("\n", "\r\n"), depois.replace("\n", "\r\n")
        n = texto.count(antes)
        if n != 1:
            res.append({"MUTANTE": nome, "ESTADO": "ANCORA_PARTIDA", "OCORRENCIAS": n})
            print("ANCORA_PARTIDA", nome, n)
            continue
        cache = tempfile.mkdtemp(prefix="mut-yt403-pyc-")
        env = dict(os.environ, PYTHONPYCACHEPREFIX=cache, PYTHONUTF8="1", NODE_DISABLE_COMPILE_CACHE="1")
        for k in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA"):
            env.pop(k, None)
        try:
            with open(p, "wb") as f:
                f.write(texto.replace(antes, depois).encode("utf-8"))
            r = subprocess.run(cmd, cwd=os.path.join(RAIZ, cwd), env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=900)
            estado = "MORTO" if r.returncode != 0 else "SOBREVIVEU"
        finally:
            with open(p, "wb") as f:
                f.write(orig)
        assert sha(open(p, "rb").read()) == sha(orig), "nao repus %s" % rel
        res.append({"MUTANTE": nome, "FICHEIRO": rel, "ESTADO": estado})
        print("%-11s %s" % (estado, nome))
    mortos = sum(1 for x in res if x["ESTADO"] == "MORTO")
    out = {"MUTANTES": len(res), "MORTOS": mortos, "RESULTADOS": res}
    if saida:
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
    print("MORTOS %d/%d" % (mortos, len(res)))
    return 0 if mortos == len(res) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
