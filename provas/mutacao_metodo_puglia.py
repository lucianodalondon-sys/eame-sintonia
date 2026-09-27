#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTAÇÃO DO MÉTODO PUGLIA — prova que `tests/test_metodo_puglia.py` morde.

    py provas/mutacao_metodo_puglia.py

Cada mutante planta UM defeito no ficheiro real, corre a suite real, exige que
ela REPROVE, e devolve o ficheiro byte a byte. Uma suite verde prova que nada
rebentou; só a mutação prova que ela apanha o que diz apanhar.

    UMA SUITE QUE NÃO REPROVA UM DEFEITO PLANTADO
    NÃO ESTÁ A GUARDAR NADA.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = os.path.join(RAIZ, 'tests', 'test_metodo_puglia.py')

MUTANTES = [
    ('M1_VISUAL_HEADER_VIRA_FACT_LOCATION', 'leis/lugar_do_fato.py',
     "LOCATION_SOURCES_QUE_SUSTENTAM_FATO = ('TEXT', 'SECTION_HEADER')",
     "LOCATION_SOURCES_QUE_SUSTENTAM_FATO = ('TEXT', 'SECTION_HEADER', 'VISUAL_HEADER_CANDIDATE')"),
    ('M2_ENTITY_SOURCE_REMOVIDO_DA_LEI', 'BIBLIA-CANONICA-DA-COLETA.md',
     'SECTION_TITLE      o nome está no título da secção que governa o trecho\n',
     ''),
    ('M3_SPAN_SEM_NOME_NO_TRECHO', 'leis/afirmacao_da_fonte.py',
     "        if not nome_no_trecho:\n            return False, 'SPAN exige o nome dentro do trecho'\n",
     ''),
    ('M4_LINT_IGNORA_COLCHETE', 'leis/afirmacao_da_fonte.py',
     "            erros.append('ACRESCENTA_COLCHETE: [%s]' % dentro)",
     "            pass"),
    ('M5_LINT_IGNORA_QUALIFICADOR', 'leis/afirmacao_da_fonte.py',
     "        if len(na_traducao) < len(na_fonte):",
     "        if False:"),
    ('M6_ESPERADO_DO_DONO_ALTERADO', 'tests/fixtures/puglia/GOLD-FIXTURE-PUGLIA-V1.json',
     '"LOCATION_SOURCE": "VISUAL_HEADER_CANDIDATE",\n    "CLASSE": "OBSERVADO"',
     '"LOCATION_SOURCE": "SECTION_HEADER",\n    "CLASSE": "OBSERVADO"'),
]


def corre_a_suite():
    r = subprocess.run([sys.executable, SUITE], cwd=RAIZ,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return r.returncode


def main():
    if corre_a_suite() != 0:
        print('MUTACAO=FAIL · a suite já reprova sem mutante — nada a medir')
        return 1
    sobreviventes = []
    for nome, rel, antes, depois in MUTANTES:
        p = os.path.join(RAIZ, rel)
        with open(p, 'rb') as f:
            original = f.read()
        texto = original.decode('utf-8')
        if texto.count(antes) != 1:
            print('  ERRO %-38s o alvo não está no ficheiro (%s)' % (nome, rel))
            sobreviventes.append(nome)
            continue
        try:
            with open(p, 'wb') as f:
                f.write(texto.replace(antes, depois).encode('utf-8'))
            codigo = corre_a_suite()
        finally:
            with open(p, 'wb') as f:
                f.write(original)
        apanhado = codigo != 0
        print('  %-9s %-38s %s' % ('APANHADO' if apanhado else 'SOBREVIVE', nome, rel))
        if not apanhado:
            sobreviventes.append(nome)
    print('\nMUTANTES=%d · SURVIVORS=%d' % (len(MUTANTES), len(sobreviventes)))
    print('MUTACAO=%s' % ('PASS' if not sobreviventes else 'FAIL'))
    return 0 if not sobreviventes else 1


if __name__ == '__main__':
    raise SystemExit(main())
