#!/usr/bin/env python3
"""D70 · teste de mutacao da lei do tempo do fato (`leis/artefato.py::conferir`).

Cada mutante estraga UMA regra numa COPIA (pasta temporaria) e corre tests/test_artefato_tempo_do_fato.py
+ tests/test_fato_do_texto.py. So conta como morto se um teste FALHOU (assercao).

    py scripts/lugar_fato/mutar_lei_do_tempo.py   -> MUTACAO-LEI-DO-TEMPO-D70.json ao lado
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ALVO = "leis/artefato.py"
TESTES = ["tests.test_artefato_tempo_do_fato", "tests.test_fato_do_texto"]

MUTANTES = [
    ("L1_NOTA_AUSENTE_PASSA", "cada nota da relativa ausente tem de reprovar",
     [("    if falta:\n        q.append(", "    if False:\n        q.append(")]),
    ("L2_CALCULO_ERRADO_PASSA", "a conta refeita diferente do FACT_TIME tem de reprovar",
     [("    if conta[0] != a.FACT_TIME:\n", "    if False:\n")]),
    ("L3_PUBLICACAO_NAO_PROVADA_PASSA", "publicacao NAO SEI/UNKNOWN tem de reprovar",
     [('    if base_pub.upper().startswith(("NAO SEI", "NÃO SEI", "UNKNOWN")):\n', "    if False:\n")]),
    ("L4_CONFLITO_PASSA", "publicacao em conflito (DA-9) tem de reprovar",
     [('    if "CONFLIT" in base_pub.upper():\n', "    if False:\n")]),
    ("L5_BASE_COM_TEXTO_A_MAIS_PASSA", "base relativa com texto a mais tem de reprovar",
     [("    if base != RELATIVA_A_PUBLICACAO:\n", "    if False:\n")]),
    ("L6_COMPARA_LETRAS", "a protecao antiga tem de comparar o significado, nao as letras",
     [("                and _mesma_data(a.FACT_TIME, a.PUBLISHED_AT)\n",
       "                and a.FACT_TIME == a.PUBLISHED_AT\n")]),
    ("L7_RELATIVA_DE_CONFIANCA", "a base relativa nao pode passar sem refazer a conta",
     [("            quebras += _conferir_relativa(a, base_do_tempo)\n", "            pass\n")]),
    ("L8_PRECISAO_NAO_CONFERIDA", "a precisao sem CALCULADA ou com resolucao errada tem de reprovar",
     [('    if prec and not prec.endswith("+CALCULADA"):\n', "    if False:\n"),
      ('    if prec != conta[1] + "+CALCULADA":\n', "    if False:\n")]),
    ("L9_INSTANTE_SO_POR_LETRAS", "o mesmo instante noutro fuso tem de reprovar",
     [("    return a[1] == b[1]\n", "    return x == y\n")]),
    ("L10_CALCULO_DE_OUTRA_ESPECIE_PASSA", "FACT_TIME_CALCULO que nao e RELATIVA_A_PUBLICACAO tem de reprovar",
     [('    if str(n.get("FACT_TIME_CALCULO", "")) not in ("", RELATIVA_A_PUBLICACAO) and "FACT_TIME_CALCULO" not in falta:\n',
       "    if False:\n")]),
    ("L11_INTERVALO_DE_UM_DIA_NAO_E_DIA", "o intervalo de um dia igual ao dia da publicacao tem de reprovar",
     [("    return f[1] == f[2] and f[1] == _dia_unico(p)\n", "    return False\n")]),
]


def correr(pasta):
    p = subprocess.run([sys.executable, "-m", "unittest"] + TESTES, cwd=pasta,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    ult = [l for l in p.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    return p.returncode, " | ".join(ult)


def main():
    orig = (RAIZ / ALVO).read_bytes().decode("utf-8").replace("\r\n", "\n")
    res = {"DATASET": "MUTACAO-LEI-DO-TEMPO-D70", "ALVO": ALVO, "TESTES": TESTES,
           "ALVO_SHA256_LF": hashlib.sha256(orig.encode("utf-8")).hexdigest(), "MUTANTES": []}
    with tempfile.TemporaryDirectory(prefix="mut-lei-") as tmp:
        tmp = Path(tmp)
        for d in ("leis", "tests"):
            shutil.copytree(RAIZ / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
        (tmp / ALVO).write_text(orig, encoding="utf-8", newline="\n")
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
            (tmp / ALVO).write_text(s, encoding="utf-8", newline="\n")
            shutil.rmtree(tmp / "leis" / "__pycache__", ignore_errors=True)
            comp = subprocess.run([sys.executable, "-c", "import ast,sys;ast.parse(open(sys.argv[1],encoding='utf-8').read())",
                                   str(tmp / ALVO)], capture_output=True, text=True)
            rc, linha = correr(tmp)
            morto = rc != 0 and comp.returncode == 0 and "FAILED (failures=" in linha
            res["MUTANTES"].append({"MUTANTE": nome, "REGRA": regra, "COMPILA": comp.returncode == 0,
                                    "RC": rc, "SAIDA": linha, "RESULTADO": "MORTO" if morto else "SOBREVIVEU"})
            print("%-38s %s  %s" % (nome, "MORTO" if morto else "SOBREVIVEU", linha))
    res["MORTOS"] = sum(m["RESULTADO"] == "MORTO" for m in res["MUTANTES"])
    res["TOTAL"] = len(res["MUTANTES"])
    out = Path(__file__).with_name("MUTACAO-LEI-DO-TEMPO-D70.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mortos %d de %d -> %s" % (res["MORTOS"], res["TOTAL"], out.name))
    sys.exit(0 if res["MORTOS"] == res["TOTAL"] else 1)


if __name__ == "__main__":
    main()
