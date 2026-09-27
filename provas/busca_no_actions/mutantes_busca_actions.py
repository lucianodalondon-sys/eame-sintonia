"""BUSCA-NO-ACTIONS · prova de mutacao — cada regra nova, estragada de proposito, tem de fazer um teste falhar.

    py provas/busca_no_actions/mutantes_busca_actions.py [saida.json]

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
T = [PY, "-m", "unittest", "test_busca_no_actions"]
API, LB, PA, WF = ("ferramentas/linha_busca/api_oficial.py", "coleta/linha_busca.py",
                   "ferramentas/linha_busca/pedido_actions.py", ".github/workflows/linha-busca-google.yml")

MUTANTES = [
    ('a tesoura nao corta pelo valor', API,
     '            t = t.replace(v, "***")\n',
     '            pass\n', T, "tests"),
    ('a tesoura nao corta key=', API,
     '    return _RE_KEY.sub(lambda m: m.group(1) + "=***", t)',
     '    return t', T, "tests"),
    ('API desligada nao e reconhecida', API,
     '    if razoes & {"SERVICE_DISABLED", "ACCESSNOTCONFIGURED"} or "has not been used in project" in m \\\n            or "it is disabled" in m:\n',
     '    if False:\n', T, "tests"),
    ('chave restrita nao e reconhecida', API,
     '    elif razoes & {"API_KEY_SERVICE_BLOCKED"} or "are blocked" in m:\n',
     '    elif False:\n', T, "tests"),
    ('chave invalida vira falta de CX', API,
     '    elif razoes & {"API_KEY_INVALID", "KEYINVALID"} or "api key not valid" in m:\n',
     '    elif False:\n', T, "tests"),
    ('sem CX nao se mede obrigatorio', API,
     'CX="OBRIGATORIO_E_AUSENTE" if not com_cx else "INVALIDO"',
     'CX="INVALIDO"', T, "tests"),
    ('o diagnostico manda sempre cx', API,
     '    if cx:\n        q["cx"] = cx\n',
     '    q["cx"] = cx\n', T, "tests"),
    ('sem chave o diagnostico chama na mesma', API,
     '    if not chave:\n        return {"HTTP": None',
     '    if False:\n        return {"HTTP": None', T, "tests"),
    ('--sem-portao-it serve paginas', LB,
     '    if sem_portao and not ("--diagnosticar-cse" in argv or ("--buscar" in argv and motor_api)):\n',
     '    if False:\n', T, "tests"),
    ('a API sai pelo transporte das paginas', LB,
     '    buscar = API.transporte() if ("--buscar" in argv and motor_api) else transporte_real(saida)\n',
     '    buscar = transporte_real(saida)\n', T, "tests"),
    ('a quota nao se cobra', LB,
     '        if teto is not None and not 1 <= n <= teto:\n',
     '        if False:\n', T, "tests"),
    ('nome de secret livre', PA,
     'RE_NOME = re.compile(r"^[A-Z][A-Z0-9_]{0,99}$")',
     'RE_NOME = re.compile(r"^.+$")', T, "tests"),
    ('GITHUB_* aceite', PA,
     '        if not RE_NOME.match(v) or v.startswith("GITHUB_"):\n',
     '        if not RE_NOME.match(v):\n', T, "tests"),
    ('N sem limite', PA,
     '    if not 1 <= n <= N_MAX:\n',
     '    if False:\n', T, "tests"),
    ('artifact so quando tudo corre bem', WF,
     '        if: always()\n        uses: actions/upload-artifact\nv4\n',
     '        uses: actions/upload-artifact\nv4\n', T, "tests"),
    ('o push dispara no ramo de codigo', WF,
     '    branches: [disparo-linha-busca-google]\n',
     '    branches: [disparo-linha-busca-google, busca-no-actions-v1]\n', T, "tests"),
    ('input direto num run', WF,
     '--n="$N" --saida=saida',
     '--n=${{ inputs.n }} --saida=saida', T, "tests"),
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
        cache = tempfile.mkdtemp(prefix="mut-busca-pyc-")
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
