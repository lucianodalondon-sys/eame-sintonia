#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do EXTRATOR-LUGAR-V2: cada mutante tem de pôr tests/test_extrator_lugar_v2.py vermelho. Repoe sempre."""
import json, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTE = "tests/test_extrator_lugar_v2.py"
MUTANTES = {
    "M1_sem_provincia_di": ("leis/fato_local.py", "    for m in _RE_PROVINCIA_DI.finditer(low):\n", "    for m in []:\n"),
    "M2_qualquer_adjectivo_em_ese": ("leis/fato_local.py", "        if m.group(1) in adj:\n            nome, prec = adj[m.group(1)]\n",
                                     "        if True:\n            nome, prec = adj.get(m.group(1), ('Roma', PROVINCE))\n"),
    "M3_homonimo_fica_com_o_primeiro": ("leis/fato_local.py", "                if len({c[2] for c in cands}) != 1:\n", "                if False:\n"),
    "M4_titulo_com_o_nome_do_site": ("leis/fato_do_texto.py", "        t = t[:m.start()].strip()\n", "        pass\n"),
    "M5_in_provincia_volta_a_ser_negativa": ("leis/fato_local.py", "(r'(?<!in )(?<!nella )provinci[ae]", "(r'provinci[ae]"),
    # EXTRATORES-V2-JUNTOS: a constante juntou-se a da EVENTO-V2 numa linha; o mutante muda so a da LUGAR-V2
    "M6_titulo_de_qualquer_tamanho": ("leis/fato_do_texto.py", "PALAVRAS_MINIMAS_DO_TITULO = PALAVRAS_DO_TITULO = 3\n",
                                      "PALAVRAS_MINIMAS_DO_TITULO = 1\nPALAVRAS_DO_TITULO = 3\n"),
    "M7_ancora_dentro_de_orgao_conta": ("leis/fato_do_texto.py",
                                        "                          if not _ancora_dentro_de_orgao(r[\"EVIDENCE\"], m)\n", ""),
    "M8_titulo_corta_a_data": ("leis/fato_do_texto.py", "    if m and not re.search(r\"\\d\", t[m.end():]):\n", "    if m:\n"),
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
