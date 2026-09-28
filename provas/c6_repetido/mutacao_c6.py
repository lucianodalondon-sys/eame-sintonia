#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C6-REPETIDO — mutacao: tirar uma exigencia do C6 tem de fazer um teste falhar.

Cada mutante e aplicado numa COPIA da arvore (`git archive <ref>`), nunca aqui.
Corre `tests.test_c6_repetido` e `tests.test_micro_coleta_instrumento`; o
mutante MORRE se algum teste que passava na copia limpa passa a falhar.

    python3 provas/c6_repetido/mutacao_c6.py [ref] [saida.json]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ALVO = "scripts/micro_coleta/micro_coleta.py"
TESTES = ["tests.test_c6_repetido", "tests.test_micro_coleta_instrumento"]

MUTANTES = {
    "M01_SEM_FORWARD_IDENTIFIED_NO_BRUTO_DO_ITEM":
        ('        if est != FORWARD_IDENTIFIED:\n', '        if False:\n'),
    "M02_SEM_FORWARD_IDENTIFIED_NA_LINHA_DA_SALA":
        ('        elif s_est != FORWARD_IDENTIFIED:\n', '        elif False:\n'),
    "M03_SEM_MESMO_UNIVERSO_NO_DOCUMENTO":
        ('        elif not universo(i) or s_uni != universo(i):\n', '        elif False:\n'),
    "M04_SEM_MESMO_UNIVERSO_NO_ITEM":
        ('if i in num and i not in out["POR_ITEM"] and universo(i) and uni == universo(i):',
         'if i in num and i not in out["POR_ITEM"]:'),
    "M05_FUSAO_POR_DOCUMENTO_NAO_TIRA_DO_FORA":
        ('if i not in fundidos["POR_ITEM"] and i not in fundidos["POR_DOCUMENTO"]]',
         'if i not in fundidos["POR_ITEM"]]'),
    "M06_FUSAO_POR_ITEM_NAO_TIRA_DO_FORA":
        ('if i not in fundidos["POR_ITEM"] and i not in fundidos["POR_DOCUMENTO"]]',
         'if i not in fundidos["POR_DOCUMENTO"]]'),
    "M07_CONTAGEM_SEM_A_FUSAO_POR_DOCUMENTO":
        ('len(ja_na_sala) + len(fundidos["POR_ITEM"]) + len(fundidos["POR_DOCUMENTO"]),',
         'len(ja_na_sala) + len(fundidos["POR_ITEM"]),'),
    "M08_TUDO_O_QUE_NAO_POUSOU_CONTA_COMO_FUNDIDO":
        ('    sim_fora_da_sala = [i for i in sim_nao_pousou\n',
         '    sim_fora_da_sala = [i for i in []\n'),
    "M09_SALA_SEM_SIM_DEIXA_DE_REPROVAR":
        ('"PASSA": not sala_sem_sim and not sim_fora_da_sala},',
         '"PASSA": not sim_fora_da_sala},'),
    "M10_PROVA_APONTA_PARA_O_PROPRIO_ITEM":
        ('"COMO": "FUNDIDO_POR_DOCUMENTO", "SALA_ITEM": s_item,',
         '"COMO": "FUNDIDO_POR_DOCUMENTO", "SALA_ITEM": i,'),
}


def correr(arvore):
    r = subprocess.run([sys.executable, "-m", "unittest", "-v"] + TESTES, cwd=arvore,
                       capture_output=True, text=True, timeout=600)
    falhas = sorted({l.split(" ", 1)[1].split(" (")[0] for l in r.stderr.splitlines()
                     if l.startswith(("FAIL: ", "ERROR: "))})
    return falhas


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    res = {"REF": subprocess.run(["git", "rev-parse", ref], cwd=RAIZ, capture_output=True,
                                 text=True).stdout.strip(), "TESTES": TESTES, "MUTANTES": {}}
    with tempfile.TemporaryDirectory(prefix="mut-c6-") as t:
        limpa = Path(t) / "limpa"
        limpa.mkdir()
        subprocess.run(f"git archive {ref} | tar -x -C {limpa}", shell=True, cwd=RAIZ, check=True)
        base = set(correr(limpa))
        res["FALHAS_NA_COPIA_LIMPA"] = sorted(base)
        for nome, (de, para) in MUTANTES.items():
            f = limpa / ALVO
            original = f.read_text(encoding="utf-8")
            if original.count(de) != 1:
                res["MUTANTES"][nome] = {"ESTADO": "ANCORA_NAO_UNICA", "VEZES": original.count(de)}
                continue
            f.write_text(original.replace(de, para), encoding="utf-8")
            try:
                novas = sorted(set(correr(limpa)) - base)
            finally:
                f.write_text(original, encoding="utf-8")
            res["MUTANTES"][nome] = {"ESTADO": "MORTO" if novas else "SOBREVIVEU", "MATOU": novas}
    mortos = sum(v["ESTADO"] == "MORTO" for v in res["MUTANTES"].values())
    res["PLACAR"] = f"{mortos}/{len(MUTANTES)}"
    texto = json.dumps(res, ensure_ascii=False, indent=1)
    if saida:
        saida.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main())
