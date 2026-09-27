#!/usr/bin/env python3
"""INTELLIGENCE R3 · DATA_DO_FACTO_ERRADA · teste de mutacao da regra do INICIO DE ATIVIDADE / SERIE
(leis/fato_do_texto.py::_RE_INICIO_DE_ATIVIDADE).

Cada mutante estraga UMA parte da regra numa COPIA (pasta temporaria; a arvore nao e tocada) e corre
tests/test_data_do_fato.py contra ela. Mutante que passa nos testes = o teste nao guarda a regra.
Mesma forma de `mutar_fato_do_texto.py`.

    py scripts/lugar_fato/mutar_data_do_fato.py      -> escreve MUTACAO-DATA-DO-FATO-V1.json ao lado
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ALVO = "leis/fato_do_texto.py"
TESTE = "tests.test_data_do_fato"

MUTANTES = [
    ("D1_SEM_A_REGRA", "reprova se «avviata nel 2013» voltar a ser o ano do facto",
     [('    ("INICIO_DE_ATIVIDADE_OU_SERIE", _RE_INICIO_DE_ATIVIDADE),\n', "")]),
    ("D2_SEM_AVVIAT", "reprova se o verbo do caso real («avviata») sair da lista",
     [("(?:avviat|iniziat|", "(?:iniziat|")]),
    ("D3_SEM_DAL_SOZINHO", "reprova se «dal 2019/20» (inicio de serie) voltar a ser o tempo do facto",
     [("|fin\\s+dal|dal(?:l", "|fin\\s+dal|dalZZ(?:l")]),
    ("D4_DAL_APANHA_DIA", "reprova se «dal 12 settembre» (um DIA, o facto) passar a ser tapado",
     [('_ANO_OU_SAFRA = r"(?:19|20)', '_ANO_OU_SAFRA = r"(?:\\d{1,2}\\s+\\w+\\s+)?(?:19|20)')]),
    ("D5_NEL_SOZINHO_TAPA", "reprova se «Nel 2025 … constatati» (data propria do facto) passar a ser tapado",
     [('r"(?:avviat|iniziat|partit|cominciat|attivat|istituit|intrapres|lanciat)[oaie]\\s+',
       'r"(?:(?:avviat|iniziat|partit|cominciat|attivat|istituit|intrapres|lanciat)[oaie]\\s+)?')]),
    ("D6_SEM_MES_ANTES_DO_ANO", "reprova se «avviato a settembre 2013» voltar a dar fact_time = settembre",
     [("\\s+(?:(?:%s)\\s+(?:del\\s+)?)?%s", "\\s+%s%s"),
      ("% (_MES, _ANO_OU_SAFRA, _ANO_OU_SAFRA)", '% ("", _ANO_OU_SAFRA, _ANO_OU_SAFRA)')]),
]


def correr(pasta):
    p = subprocess.run([sys.executable, "-m", "unittest", TESTE], cwd=pasta,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    ult = [l for l in p.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    return p.returncode, " | ".join(ult)


def main():
    orig = (RAIZ / ALVO).read_text(encoding="utf-8")
    res = {"DATASET": "MUTACAO-DATA-DO-FATO-V1", "ALVO": ALVO, "TESTE": TESTE,
           "ALVO_SHA256": hashlib.sha256(orig.encode("utf-8")).hexdigest(), "MUTANTES": []}
    with tempfile.TemporaryDirectory(prefix="mut-data-") as tmp:
        tmp = Path(tmp)
        for d in ("leis", "tests"):
            shutil.copytree(RAIZ / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
        rc, linha = correr(tmp)
        res["SEM_MUTANTE"] = {"RC": rc, "SAIDA": linha}
        if rc != 0:
            print("o original ja falha:", linha)
            sys.exit(2)
        for nome, regra, trocas in MUTANTES:
            s = orig
            for a, b in trocas:
                if s.count(a) != 1:
                    raise SystemExit("mutante %s: trecho aparece %d vezes: %r" % (nome, s.count(a), a[:60]))
                s = s.replace(a, b)
            (tmp / ALVO).write_text(s, encoding="utf-8")
            shutil.rmtree(tmp / "leis" / "__pycache__", ignore_errors=True)
            comp = subprocess.run([sys.executable, "-c", "import ast,sys;ast.parse(open(sys.argv[1],encoding='utf-8').read())",
                                   str(tmp / ALVO)], capture_output=True, text=True)
            rc, linha = correr(tmp)
            # so conta como morto se um teste FALHOU (assert); erro de execucao nao prova nada
            morto = rc != 0 and comp.returncode == 0 and "FAILED (failures=" in linha
            res["MUTANTES"].append({"MUTANTE": nome, "REGRA": regra, "COMPILA": comp.returncode == 0,
                                    "RC": rc, "SAIDA": linha, "RESULTADO": "MORTO" if morto else "SOBREVIVEU"})
            print("%-26s %s  %s" % (nome, "MORTO" if morto else "SOBREVIVEU", linha))
        (tmp / ALVO).write_text(orig, encoding="utf-8")
    res["MORTOS"] = sum(m["RESULTADO"] == "MORTO" for m in res["MUTANTES"])
    res["TOTAL"] = len(res["MUTANTES"])
    out = Path(__file__).with_name("MUTACAO-DATA-DO-FATO-V1.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mortos %d de %d -> %s" % (res["MORTOS"], res["TOTAL"], out.name))
    sys.exit(0 if res["MORTOS"] == res["TOTAL"] else 1)


if __name__ == "__main__":
    main()
