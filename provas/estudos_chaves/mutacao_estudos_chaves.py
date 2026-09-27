#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESTUDOS-CHAVES · MUTACAO: planta um defeito de cada vez e prova que `tests/test_estudo_chaves.py` o apanha.

    python3 provas/estudos_chaves/mutacao_estudos_chaves.py [--saida provas/estudos_chaves/MUTACAO-ESTUDOS-CHAVES.json]

Cada mutante troca UM trecho (que tem de existir UMA vez), corre o teste, e repoe o ficheiro; o sha256 do
ficheiro reposto e conferido contra o original (se nao bater, para e grita). A copia limpa corre antes e
tem de passar. Sem rede, sem banco.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TESTE = "tests/test_estudo_chaves.py"
SAIDA = os.path.join(RAIZ, "provas", "estudos_chaves", "MUTACAO-ESTUDOS-CHAVES.json")

MUTANTES = [
    ("M01", "leis/estudo_chaves.py", "if _INSTITUCIONAL.search(antes):", "if False and _INSTITUCIONAL.search(antes):",
     "a afiliacao do autor volta a poder virar lugar do estudo (INT-LAW-102)"),
    ("M02", "leis/estudo_chaves.py", "if forma in AMBIGUAS_CULTURA:", "if False:",
     "a forma ambigua («vite» = vidas) passa a dar cultura"),
    ("M03", "leis/estudo_chaves.py", "return texto[mapa[ini]:mapa[fim - 1] + 1]",
     "return texto[mapa[ini]:mapa[fim - 1] + 1].lower()", "o trecho deixa de ser literal (D112)"),
    ("M04", "leis/estudo_chaves.py", "        if not pista:", "        if False:",
     "o lugar conta sem verbo/nome de experimento na frase (PLACE_MENTION vira lugar do estudo)"),
    ("M05", "leis/estudo_chaves.py", 'ESTADO_DO_PROBLEMA = "NOMEADO_NO_ESTUDO"', 'ESTADO_DO_PROBLEMA = "PRESENTE"',
     "CAP-SCI: a praga do estudo passa a PRESENTE (incidencia de campo)"),
    ("M06", "leis/estudo_chaves.py", 'if h["FORMA"] in AMBIGUOS_LUGAR and', 'if False and',
     "o lugar homonimo de palavra comum («Potenza») conta sem «provincia di»"),
    ("M07", "leis/estudo_chaves.py", "    return a[0] < b[1] and b[0] < a[1]", "    return False",
     "dois vocabularios no mesmo trecho dao duas entidades"),
    ("M08", "admissao/admissao.py", "    if estudo and regiao == AUSENCIA:", "    if estudo:",
     "o lugar do estudo passa por cima de fact_location declarado"),
    ("M09", "admissao/admissao.py", 'UNIVERSOS_DE_ESTUDO = ("T5",)', 'UNIVERSOS_DE_ESTUDO = ("T5", "T10", "T3", "T2", "T7")',
     "o extrator de estudo passa a ler universos que nao sao estudo"),
    ("M10", "admissao/admissao.py", "    if not da_regua and not estudo:", "    if not da_regua:",
     "em T5 a leitura antiga do titulo volta (sem ambiguidade: «salvare vite» da vite)"),
    ("M11", "admissao/reprocessar_estudos_chaves.py", 'if e.get("janela_declarada") is not None and',
     'if False and', "o reprocesso repete a revisao com o mesmo codigo (deixa de ser idempotente)"),
    ("M12", "coleta/pesquisadores_t6.py", "'olivo': ('olea europaea', ", "'olivo': (",
     "o nome cientifico do olivo sai do lexico T6"),
    ("M13", "leis/estudo_chaves.py", 'r"performed|set\\s+up|', 'r"performed|established|located|set\\s+up|',
     "«established/located» voltam a ser pista de ensaio (incidencia vira lugar do estudo)"),
]


def _sha(p):
    with open(p, "rb") as h:
        return hashlib.sha256(h.read()).hexdigest()


def _correr():
    r = subprocess.run([sys.executable, TESTE], cwd=RAIZ, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    out = r.stdout + r.stderr
    falhas = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+)", out, re.M)))
    return r.returncode, falhas, (out.strip().splitlines() or [""])[-1]


def main(argv):
    saida = SAIDA
    for a in argv:
        if a.startswith("--saida="):
            saida = a.split("=", 1)[1]
    rc, falhas, fim = _correr()
    if rc != 0:
        print("A COPIA LIMPA NAO PASSA: %s %s" % (fim, falhas))
        return 2
    res = {"TESTE": TESTE, "LIMPA": fim, "MUTANTES": []}
    for mid, rel, velho, novo, porque in MUTANTES:
        cam = os.path.join(RAIZ, rel)
        with open(cam, encoding="utf-8", newline="") as h:
            original = h.read()
        antes = _sha(cam)
        if original.count(velho) != 1:
            res["MUTANTES"].append({"ID": mid, "FICHEIRO": rel, "ESTADO": "NAO_APLICADO",
                                    "PORQUE": "o trecho aparece %d vezes" % original.count(velho)})
            continue
        try:
            with open(cam, "w", encoding="utf-8", newline="") as h:
                h.write(original.replace(velho, novo))
            rc, falhas, fim = _correr()
        finally:
            with open(cam, "w", encoding="utf-8", newline="") as h:
                h.write(original)
        if _sha(cam) != antes:
            print("REPOSICAO FALHOU em %s" % rel)
            return 3
        res["MUTANTES"].append({"ID": mid, "FICHEIRO": rel, "DEFEITO": porque,
                                "ESTADO": "MORTO" if rc != 0 else "VIVO", "APANHADO_POR": falhas, "FIM": fim})
    mortos = sum(1 for m in res["MUTANTES"] if m["ESTADO"] == "MORTO")
    res["RESUMO"] = "%d/%d MORTOS" % (mortos, len(MUTANTES))
    with open(saida, "w", encoding="utf-8", newline="\n") as h:
        json.dump(res, h, ensure_ascii=False, indent=1)
    for m in res["MUTANTES"]:
        print(m["ID"], m["ESTADO"], ", ".join(x.split(".")[-1] for x in m.get("APANHADO_POR", []))[:160])
    print(res["RESUMO"])
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
