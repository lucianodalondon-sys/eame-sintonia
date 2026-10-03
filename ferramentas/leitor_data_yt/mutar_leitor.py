#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do LEITOR-DATA-YOUTUBE: cada mutante tem de pôr pelo menos um teste vermelho.
Escreve o mutante no ficheiro, corre os testes, e repoe SEMPRE o original (try/finally)."""
import json, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ALVO = RAIZ / "coleta" / "executor_texto_de_html.py"
TESTES = ["tests/test_leitor_data_youtube.py", "tests/test_tempo_e_lugar_da_publicacao.py"]
MUTANTES = {
    "M1_sem_o_nivel_itemprop": ("        (BASE_ITEMPROP, _datas_do_itemprop(texto)),\n", ""),
    "M2_itemprop_antes_do_time": (
        "        (BASE_TIME, _datas_do_time(texto)),\n        (BASE_ITEMPROP, _datas_do_itemprop(texto)),\n",
        "        (BASE_ITEMPROP, _datas_do_itemprop(texto)),\n        (BASE_TIME, _datas_do_time(texto)),\n"),
    "M3_uploadDate_tambem_conta": ('== "datepublished" and a.get("content")',
                                   'in ("datepublished", "uploaddate") and a.get("content")'),
    "M4_sem_ambiguidade_fica_a_primeira": ("        if len(boas) > 1:\n", "        if False and len(boas) > 1:\n"),
}


def correr():
    vermelhos = 0
    for t in TESTES:
        r = subprocess.run([sys.executable, "-B", t], cwd=RAIZ, capture_output=True, text=True)
        vermelhos += r.returncode != 0
    return vermelhos


def main():
    original = ALVO.read_bytes()
    texto = original.decode("utf-8")
    nl = "\r\n" if "\r\n" in texto else "\n"
    res = {}
    try:
        assert correr() == 0, "os testes tem de passar antes de mutar"
        for nome, (a, b) in MUTANTES.items():
            a2, b2 = a.replace("\n", nl), b.replace("\n", nl)
            assert texto.count(a2) == 1, nome
            ALVO.write_bytes(texto.replace(a2, b2).encode("utf-8"))
            v = correr()
            res[nome] = "MORTO" if v else "SOBREVIVEU"
            ALVO.write_bytes(original)
    finally:
        ALVO.write_bytes(original)
    ok = all(v == "MORTO" for v in res.values())
    print(json.dumps({"MUTANTES": res, "MORTOS": sum(v == "MORTO" for v in res.values()), "DE": len(res),
                      "ORIGINAL_REPOSTO": ALVO.read_bytes() == original}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
