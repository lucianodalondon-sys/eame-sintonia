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
API, LB, PA, WF, CP = ("ferramentas/linha_busca/api_oficial.py", "coleta/linha_busca.py",
                       "ferramentas/linha_busca/pedido_actions.py", ".github/workflows/linha-busca-google.yml",
                       "ferramentas/linha_busca/comentarios_piloto_d106.py")

MUTANTES = [
    ('a tesoura nao corta pelo valor', API,
     '            t = t.replace(v, "***")\n',
     '            pass\n', T, "tests"),
    ('a tesoura nao corta key=', API,
     '    return _RE_KEY.sub(lambda m: m.group(1) + "=***", t)',
     '    return t', T, "tests"),
    ('API desligada nao e reconhecida', API,
     '        d.update(API_ATIVA="NAO", PORQUE="a Custom Search JSON API nao esta ativada neste projeto do Google Cloud")',
     '        pass', T, "tests"),
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
    ('CX com qualquer forma', PA,
     '    if cx and not RE_CX.match(cx):\n',
     '    if False:\n', T, "tests"),
    ('N sem limite', PA,
     '    if not 1 <= n <= N_MAX:\n',
     '    if False:\n', T, "tests"),
    ('artifact so quando tudo corre bem', WF,
     '        if: always()\n        uses: actions/upload-artifact@v4\n',
     '        uses: actions/upload-artifact@v4\n', T, "tests"),
    ('secret pelo nome (entrega todos)', WF,
     '          YOUTUBE_DATA_API_KEY: ${{ secrets.YOUTUBE_DATA_API_KEY }}\n',
     "          YOUTUBE_DATA_API_KEY: ${{ secrets['YOUTUBE_DATA_API_KEY'] }}\n", T, "tests"),
    ('um SUPABASE entra no runner', WF,
     '          YOUTUBE_DATA_API_KEY: ${{ secrets.YOUTUBE_DATA_API_KEY }}\n',
     '          YOUTUBE_DATA_API_KEY: ${{ secrets.YOUTUBE_DATA_API_KEY }}\n          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}\n', T, "tests"),
    ('dispara noutro ramo', WF,
     '    branches: [busca-no-actions-v1]\n',
     '    branches: [busca-no-actions-v1, main]\n', T, "tests"),
    ('workflow_dispatch de volta', WF,
     'on:\n  push:\n',
     'on:\n  workflow_dispatch:\n  push:\n', T, "tests"),
    ('permissao de escrita', WF,
     'permissions:\n  contents: read\n',
     'permissions:\n  contents: write\n', T, "tests"),
    ('comentarios fora da corrida', WF,
     '        run: python3 ferramentas/linha_busca/comentarios_piloto_d106.py --saida=saida\n',
     '        run: echo sem comentarios\n', T, "tests"),
    ('piloto so com uma ordem', CP,
     'ORDENS = ("relevance", "time")',
     'ORDENS = ("relevance",)', T, "tests"),
    ('piloto com menos de 100 por pagina', CP,
     '"maxResults": 100',
     '"maxResults": 20', T, "tests"),
    ('erro da chave nao para o piloto', CP,
     '                if {r.upper() for r in g["RAZOES"]} & PARAM_TUDO:\n',
     '                if False:\n', T, "tests"),
    ('comentarios desligados param tudo', CP,
     'PARAM_TUDO = {"QUOTAEXCEEDED",',
     'PARAM_TUDO = {"COMMENTSDISABLED", "QUOTAEXCEEDED",', T, "tests"),
    ('sem chave o piloto chama na mesma', CP,
     '    if not chave:\n        doc.update(PAROU=',
     '    if False:\n        doc.update(PAROU=', T, "tests"),
    ('o piloto pede sem o sha', CP,
     'SHA256=hashlib.sha256(corpo).hexdigest()',
     'SHA256=None', T, "tests"),
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
