"""CONTADOR-24H (D90) · o ataque: cada peca do contador multicanal desligada, uma de cada vez, numa COPIA.

    py provas/contador_24h_mutacao.py [--ref=HEAD]

A copia sai de `git archive <ref>` para uma pasta temporaria: o repositorio nao e tocado.
Cada mutante troca UM trecho exacto de um ficheiro; se o trecho nao existir uma vez so, o
ataque falha alto (um mutante que nao muda nada nao prova nada).
MORTO = `tests/test_contador_24h.py` reprova ou sai com codigo != 0.
Resultado em `provas/CONTADOR-24H-MUTACAO.json`.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = "coleta/reserva_24h.py"
JS = "coleta/italy_pilot_collect.mjs"
MUTANTES = [
    ("P1_TETO_FOLGADO", PY, "            if g + qtd > teto:", "            if g + qtd > teto + 1:"),
    ("P2_SEM_TRINCO", PY, "        with _Trinco(f):", "        with open(os.devnull):"),
    ("P3_ILEGIVEL_VIRA_VAZIO", PY, '        raise ValueError("TETO_24H sem RESERVAS[]")', "        return []"),
    ("P4_JANELA_IGNORADA", PY,
     '    return sum(int(r["QTD"]) for r in reservas if r["DOMINIO"] == dom and float(r["EM"]) > agora - JANELA_S)',
     '    return sum(int(r["QTD"]) for r in reservas if r["DOMINIO"] == dom)'),
    ("P5_GOOGLEVIDEO_SEPARADO", PY, 'MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com", "ytimg.com": "youtube.com"}',
     "MESMO_ORCAMENTO = {}"),
    ("P6_NAO_ESCREVE_A_RESERVA", PY, "            os.replace(tmp, f)\n", ""),
    ("N1_TRANSPORTE_NAO_RESERVA", JS, "  if (livro24h()) {\n    const r = reservar24h(host, 1);",
     "  if (false) {\n    const r = reservar24h(host, 1);"),
    ("N2_NODE_SEM_TRINCO", JS, "    try { mkdirSync(trinco); break; }\n    catch (e) {\n      if (e.code !== \"EEXIST\") return",
     "    try { break; }\n    catch (e) {\n      if (e.code !== \"EEXIST\") return"),
    ("N3_NODE_ILEGIVEL_VIRA_VAZIO", JS,
     "  if (!d || !Array.isArray(d.RESERVAS)) throw new Error(`TETO_24H_ILEGIVEL: ${f}: sem RESERVAS[]`);",
     "  if (!d || !Array.isArray(d.RESERVAS)) return [];"),
    ("N4_NODE_TETO_FOLGADO", JS, "    if (g + qtd > teto) {", "    if (g + qtd > teto + 1) {"),
    ("S1_SOCIAL_NAO_RESERVA", "coleta/teto_da_onda.py", '    if os.environ.get("SINTONIA_TETO_24H"):',
     "    if False:"),
    ("S2_SOCIAL_IGNORA_ADIADO", "coleta/teto_da_onda.py", '        if r24["ESTADO"] != "RESERVADO":',
     '        if r24["ESTADO"] == "FAIL":'),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    env.pop("SINTONIA_TETO_24H", None)
    r = subprocess.run([sys.executable, "tests/test_contador_24h.py"], cwd=pasta, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=1200)
    m = re.search(r"Ran (\d+) test", r.stderr)
    return r.returncode, int(m.group(1)) if m else None, r.stderr[-600:]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="contador24h-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "MUTANTES": []}
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        cod, n, cauda = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base:\n" + cauda)
        for nome, alvo, de, para in MUTANTES:
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, alvo)
            with open(f, encoding="utf-8", newline="") as h:
                s = h.read()
            s2 = s.replace("\r\n", "\n")
            if s2.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s: o trecho aparece %d vezes em %s" % (nome, s2.count(de), alvo))
            s2 = s2.replace(de, para)
            with open(f, "w", encoding="utf-8", newline="") as h:
                h.write(s2.replace("\n", "\r\n") if "\r\n" in s else s2)
            cod, n, cauda = correr(pasta)
            morto = cod != 0
            out["MUTANTES"].append({"MUTANTE": nome, "ALVO": alvo, "MORTO": morto, "CODIGO": cod,
                                    "CAUDA": None if morto else cauda})
            print(nome, "MORTO" if morto else "SOBREVIVEU", flush=True)
            shutil.rmtree(pasta, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(1 for m in out["MUTANTES"] if m["MORTO"])
    out["TOTAL"] = len(out["MUTANTES"])
    with open(os.path.join(RAIZ, "provas", "CONTADOR-24H-MUTACAO.json"), "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
    print("CONTADOR_24H_MUTACAO · mortos=%d de %d" % (out["MORTOS"], out["TOTAL"]))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
