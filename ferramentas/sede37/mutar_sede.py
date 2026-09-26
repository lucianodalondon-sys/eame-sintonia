#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao da SEDE-37-PREP: cada mutante tem de pôr tests/test_sede_da_fonte.py vermelho. Repoe sempre o original."""
import json, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTE = "tests/test_sede_da_fonte.py"
MUTANTES = {
    "M1_uma_pagina_sem_sede_basta": ("curadoria/sede_da_fonte.py",
                                     "    forte = len(vistas[k]) >= 2 or com_sede[k] > 0\n", "    forte = True\n"),
    # (1.a versao: adivinhar o proprio comune SOBREVIVIA — a conferencia pelo leitor do contrato ja o trava;
    #  o palpite perigoso e uma provincia QUE EXISTE no gazetteer para uma sigla desconhecida)
    "M2_sigla_desconhecida_vira_roma": ("curadoria/sede_da_fonte.py",
                                        "    if sigla in PROVINCIA_DA_SIGLA:\n        p = PROVINCIA_DA_SIGLA[sigla]\n",
                                        "    if sigla:\n        p = PROVINCIA_DA_SIGLA.get(sigla, \"Roma\")\n"),
    "M3_ponte_escreve_sempre": ("curadoria/onboardar_rotas_provadas.py",
                                '    sede = {"SOURCE_LOCATION_RULE": c["SOURCE_LOCATION_RULE"]} if c.get("SOURCE_LOCATION_RULE") else {}\n',
                                '    sede = {"SOURCE_LOCATION_RULE": c.get("SOURCE_LOCATION_RULE") or "NAO SEI"}\n'),
    "M4_nao_sei_escreve_no_contrato": ("curadoria/sede_da_fonte.py",
                                       '    if r.get("SOURCE_LOCATION") in (None, "", NAO_SEI) or not r.get("SOURCE_LOCATION_RULE"):\n        return {}\n', ""),
}


def main():
    res = {}
    for nome, (rel, a, b) in MUTANTES.items():
        alvo = RAIZ / rel
        original = alvo.read_bytes()
        texto = original.decode("utf-8")
        nl = "\r\n" if "\r\n" in texto else "\n"
        try:
            a2, b2 = a.replace("\n", nl), b.replace("\n", nl)
            assert texto.count(a2) == 1, nome
            alvo.write_bytes(texto.replace(a2, b2).encode("utf-8"))
            r = subprocess.run([sys.executable, "-B", TESTE], cwd=RAIZ, capture_output=True, text=True)
            res[nome] = "MORTO" if r.returncode else "SOBREVIVEU"
        finally:
            alvo.write_bytes(original)
    print(json.dumps({"MUTANTES": res, "MORTOS": sum(v == "MORTO" for v in res.values()), "DE": len(res)}, indent=1))
    return 0 if all(v == "MORTO" for v in res.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
