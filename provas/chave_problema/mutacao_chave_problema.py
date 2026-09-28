#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHAVE-PROBLEMA · MUTACAO: planta um defeito de cada vez e prova que `tests/test_chave_problema.py` o apanha.

    python3 provas/chave_problema/mutacao_chave_problema.py [--saida=provas/chave_problema/MUTACAO-CHAVE-PROBLEMA.json]

Cada mutante troca UM trecho (que tem de existir UMA vez), corre o teste, e repoe o ficheiro; o sha256 do
ficheiro reposto e conferido contra o original (se nao bater, para e grita). A copia limpa corre antes e
tem de passar. Sem rede, sem banco. (O mesmo mecanismo de provas/estudos_chaves/mutacao_estudos_chaves.py.)
"""
import hashlib
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TESTE = "tests.test_chave_problema"
SAIDA = os.path.join(RAIZ, "provas", "chave_problema", "MUTACAO-CHAVE-PROBLEMA.json")
BC, AF, AD = "leis/boletim_do_campo.py", "leis/afirmacao_da_fonte.py", "admissao/admissao.py"
RP = "admissao/reprocessar_problema.py"

MUTANTES = [
    # ── os quatro que a missao nomeou ──
    ("M01", BC, 'return "SECTION_HEADER", s', 'return "TEXT", s',
     "a praga do CABECALHO vira praga do TRECHO (VEIO_DE = TEXT sem o nome na frase)"),
    ("M02", BC, "    if len(nomes) != 1:", "    if not nomes:",
     "OUTRA PRAGA NO MEIO: com duas pragas no item fica a primeira (D112 violada)"),
    ("M03", BC, '            fora.append({"NOME": nome_do_problema(re.sub(r"\\s+", " ", m.group(0))),',
     '            fora.append({"NOME": re.sub(r"\\s+", " ", m.group(0)).lower(),',
     "SINONIMO NAO UNIFICADO: as formas da mesma mosca contam como pragas diferentes (D111)"),
    ("M04", BC, '        hit = b["TABELA"].get(b["NORM"](f))',
     '        hit = next((b["TABELA"][k] for k in __import__("difflib").get_close_matches('
     'b["NORM"](f), list(b["TABELA"]), n=1, cutoff=0.5)), None)',
     "INFERENCIA POR SEMELHANCA: o codigo EPPO passa a vir do nome mais parecido (COL-LAW-034)"),
    ("M05", BC, 'r"bactrocera\\s+oleae"', 'r"bactrocera\\s+olea\\w*"',
     "INFERENCIA POR SEMELHANCA: uma forma parecida («Bactrocera olea») passa a ser mencao"),
    # ── o contrato e quem o le ──
    ("M06", AF, "    if bloco.get('CONTRATO') != CONTRATO_PROBLEMA:", "    if False:",
     "o leitor aceita PROBLEMA fora do contrato (a forma antiga, VEIO_DE livre)"),
    ("M07", AF, "    if texto is not None and base not in _espacos(texto):", "    if False:",
     "o leitor nao confere a BASE contra o texto (praga inferida passa)"),
    ("M08", AF, "    if not isinstance(valor, str) or not valor.strip():", "    if not valor:",
     "o leitor aceita LISTA como valor (a CAP-WIN colava nomes num ISSUE_ID)"),
    ("M09", "motor/cap_win.py", '        if campo == "PROBLEMA":', "        if False:",
     "a CAP-WIN volta a ler o PROBLEMA sem contrato"),
    ("M10", "motor/motor_das_capacidades.py", '        if campo == "PROBLEMA":', "        if False:",
     "o motor (objeto do futuro) volta a ler o PROBLEMA sem contrato"),
    ("M11", BC, '    vivas = [m for m in lidas if m["ESTADO"] != "AUSENTE"]', "    vivas = list(lidas)",
     "praga marcada AUSENTE vira valor"),
    ("M12", BC, "    if linha.strip() == primeira or s in titulos:", "    if False:",
     "o TITULO deixa de ser DOCUMENT_TITLE"),
    ("M13", AD, "        p = BC.problema_do_boletim(texto)\n", "        p = _problema_do_boletim(boletim, universo)\n",
     "a porta volta a escrever o PROBLEMA dos boletins fora do contrato"),
    # ── o reprocesso da Sala ──
    ("M14", RP, "        nova = dict(atual, PROBLEMA=problema)",
     "        nova = dict(adm.JANELA_NAO_MEDIDA, PROBLEMA=problema)",
     "o reprocesso apaga as outras chaves da janela atual"),
    ("M15", RP, '        if _texto_json(atual) == revs[0]["VALOR"]:', "        if False:",
     "o reprocesso repete a revisao com o mesmo codigo (deixa de ser idempotente)"),
    ("M16", RP, '    if revisoes.get("VERSAO_DO_EXTRATOR") != agora:', "    if False:",
     "--aplicar grava revisoes de outro codigo (o que se reviu a seco nao e o que se aplica)"),
]


def _sha(p):
    with open(p, "rb") as h:
        return hashlib.sha256(h.read()).hexdigest()


def _correr():
    r = subprocess.run([sys.executable, "-m", "unittest", TESTE], cwd=RAIZ, capture_output=True, text=True,
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
            res["MUTANTES"].append({"ID": mid, "FICHEIRO": rel, "DEFEITO": porque, "ESTADO": "NAO_APLICADO",
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
