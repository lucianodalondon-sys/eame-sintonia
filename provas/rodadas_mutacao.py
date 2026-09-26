"""DISPARADOR-RODADAS · o ataque: cada guarda do disparador desligada, uma de cada vez, numa COPIA.

    py provas/rodadas_mutacao.py [--ref=HEAD]

A copia sai de `git archive <ref>` para uma pasta temporaria: o repositorio nao e tocado.
Cada mutante troca UM trecho exacto de um ficheiro; se o trecho nao existir uma vez so, o
ataque falha alto (um mutante que nao muda nada nao prova nada).
MORTO = `tests/test_rodadas.py` reprova ou sai com codigo != 0.
Resultado em `provas/RODADAS-MUTACAO.json`.
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
ALVO = "ferramentas/big_collection/rodadas.py"
MUTANTES = [
    ("M01_SEM_PROVA_TETO", ALVO, 'if prova["ESTADO"] != "PASS":', "if False:"),
    ("M02_NAO_SEI_FECHA", ALVO, 'if prova["ESTADO"] != "PASS":', 'if prova["ESTADO"] == "FAIL":'),
    ("M03_SEM_EGRESSO_ANTES", ALVO, 'if not antes.get("PASSA"):', "if False:"),
    ("M04_SEM_EGRESSO_DEPOIS", ALVO, 'if not depois.get("PASSA"):', "if False:"),
    ("M05_PLANO_MAIOR_OU_IGUAL", ALVO, "if gasto + p > teto:", "if gasto + p >= teto:"),
    ("M06_RETOMA_REPETE_FECHADAS", ALVO, 'if reg.get("ESTADO") == "FECHADA":
            continue', 'if reg.get("ESTADO") == "FECHADA":
            pass'),
    ("M07_RETOMA_ONDA_NOVA", ALVO, 'retomar = (pasta / "TETO-ONDA.json").exists()', "retomar = False"),
    ("M08_TETO_DIA_IGNORADO", ALVO, 'if ja.get(d, 0) + f["PREVISTOS"] > teto_dia:', "if False:"),
    ("M09_LIVROS_DE_QUALQUER_DIA", ALVO, "if date.fromtimestamp(f.stat().st_mtime) != hoje:
            continue
", ""),
    ("M10_CODIGO_DA_ONDA_IGNORADO", ALVO, 'if reg["CODIGO_DA_ONDA"] != 0 or e.get("PAROU"):', 'if e.get("PAROU"):'),
    ("M11_ACEITA_OUTRA_COORTE", ALVO, 'if plano.get("COORTE_SHA256") != sha:', "if False:"),
    ("M12_PASTA_UNICA", ALVO, 'pasta = base / ("RODADA-%02d" % n)', 'pasta = base / "RODADA-01"'),
    ("M13_RELATORIO_SEM_ESTADO", ALVO, 'relatorio(pasta / "ONDA-WEB-ESTADO.json", pasta / "relatorio")', 'relatorio(pasta, pasta / "relatorio")'),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    r = subprocess.run([sys.executable, "tests/test_rodadas.py"], cwd=pasta, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=600)
    m = re.search(r"Ran (\d+) test", r.stderr)
    return r.returncode, int(m.group(1)) if m else None, r.stderr[-600:]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="rodadas-mutacao-")
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
    with open(os.path.join(RAIZ, "provas", "RODADAS-MUTACAO.json"), "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
    print("RODADAS_MUTACAO · mortos=%d de %d" % (out["MORTOS"], out["TOTAL"]))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
