#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTAÇÃO DO TEMPO-E-LUGAR — as duas confusões que a lei proíbe têm de morder.

    publicação       -> fact_time      reprova
    source_location  -> fact_location  reprova

E o encanamento: se uma paragem deixar de passar o recado, reprova.

Cada mutante estraga o CÓDIGO, corre `tests.test_tempo_e_lugar_atravessa` e
exige VERMELHO. O ficheiro é restaurado da cópia em memória (não por
`git checkout`, que apagaria trabalho por commitar), sempre, mesmo em falha.
Corre com `-B` e sem .pyc: um mutante do mesmo tamanho engana o .pyc.

    py tests/mutacao_tempo_e_lugar.py
"""
import io
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
MODULO = "tests.test_tempo_e_lugar_atravessa"

CASOS = [
    ("coleta/italy_executor.py",
     '            fora["PUBLISHED_AT"] = obs["SOURCE_DATE_ISO"]',
     '            fora["PUBLISHED_AT"] = fora["FACT_TIME"] = obs["SOURCE_DATE_ISO"]',
     "M1 · a publicacao vira FACT_TIME no tradutor do livro"),
    ("coleta/italy_executor.py",
     '            fora["SOURCE_LOCATION"] = lugar["VALOR"]',
     '            fora["SOURCE_LOCATION"] = fora["FACT_LOCATION"] = lugar["VALOR"]',
     "M2 · a sede vira FACT_LOCATION no tradutor do livro"),
    ("coleta/ingresso.py",
     '    "PUBLISHED_AT": "published_at",',
     '    "PUBLISHED_AT": "fact_time",',
     "M3 · o tradutor da porta poe a publicacao no tempo do facto"),
    ("coleta/ingresso.py",
     '    "SOURCE_LOCATION": "source_location",',
     '    "SOURCE_LOCATION": "fact_location",',
     "M4 · o tradutor da porta poe a sede no lugar do facto"),
    ("coleta/italy_executor.py",
     '        if especie["E_PUBLICACAO"]:',
     '        if True:',
     "M5 · validade passa por publicacao"),
    ("coleta/ingresso.py",
     '                         "TEMPO_E_LUGAR": dict((tempo_e_lugar or {}).get(',
     '                         "TEMPO_E_LUGAR": {} if True else dict((tempo_e_lugar or {}).get(',
     "M6 · a unidade da derivacao larga o recado"),
    ("orquestrador/orquestrador.py",
     '    tl = estruturado.get("TEMPO_E_LUGAR") or {}',
     '    tl = {}',
     "M7 · o item da porta larga o recado"),
    ("coleta/italy_executor.py",
     '    if valor and not re.match(r"^\\d{4}", valor):',
     '    if False:',
     "M8 · prosa do coletor volta a ser um instante"),
]


def corre():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([PY, "-B", "-m", "unittest", MODULO], cwd=RAIZ,
                       capture_output=True, text=True, env=env)
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:]


def main():
    print("MUTACAO_DO_TEMPO_E_LUGAR")
    mordeu, falhas = 0, []
    for ficheiro, velho, novo, nome in CASOS:
        caminho = os.path.join(RAIZ, ficheiro)
        original = io.open(caminho, encoding="utf-8", newline="").read()
        n = original.count(velho)
        if n != 1:
            print("  NAO_APLICOU  %s (ocorrencias=%d)" % (nome, n))
            falhas.append(nome)
            continue
        try:
            io.open(caminho, "w", encoding="utf-8", newline="").write(
                original.replace(velho, novo))
            verde, cauda = corre()
        finally:
            io.open(caminho, "w", encoding="utf-8", newline="").write(original)
        if verde:
            print("  NAO_MORDEU   %s" % nome)
            falhas.append(nome)
        else:
            mordeu += 1
            print("  MORDEU       %s — %s" % (nome, cauda[0][:80] if cauda else ""))
    print()
    print("MUTACOES_MORDERAM=%d/%d" % (mordeu, len(CASOS)))
    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())
