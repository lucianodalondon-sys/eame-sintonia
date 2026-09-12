#!/usr/bin/env python3
"""Um ficheiro que so corre dentro do harness nao corre.

    PASSAR NO HARNESS NAO E CORRER.

O defeito que obrigou este teste: `leis/telemetria.py` inseria a PROPRIA pasta
no `sys.path`, e `_gavetas.py` mora na RAIZ. `python3 leis/telemetria.py`
rebentava com ModuleNotFoundError — e a suite inteira passava, porque cada
teste ja insere a raiz antes de importar. O contrato central da observabilidade
esteve ilegivel na linha de comando sem que nenhuma prova notasse.

Este teste corre cada ficheiro COMO SUBPROCESSO, a partir da raiz, com o
ambiente limpo — que e como uma pessoa o corre.
"""
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ficheiros que declaram `main()` e sao feitos para se poder correr a mao.
# Nao inclui provas que precisam de banco: essas tem as suas proprias portas.
EXECUTAVEIS = (
    'leis/telemetria.py',
    'leis/diagnostico.py',
    'leis/falhas.py',
    'leis/politica_da_coleta.py',
    'leis/gestao_da_coleta.py',
    'leis/evolucao.py',
    'leis/aprender_com_a_fonte.py',
    'leis/relevancia_da_fonte.py',
    'provas/paridade_da_lingua.py',
)


class CorreForaDoHarness(unittest.TestCase):

    def test_cada_lei_corre_sozinha_a_partir_da_raiz(self):
        ambiente = dict(os.environ)
        ambiente.pop('PYTHONPATH', None)   # sem muleta: so o que o ficheiro faz
        for rel in EXECUTAVEIS:
            caminho = os.path.join(RAIZ, rel)
            if not os.path.exists(caminho):
                continue
            with self.subTest(ficheiro=rel):
                r = subprocess.run([sys.executable, caminho], cwd=RAIZ,
                                   capture_output=True, text=True, env=ambiente)
                self.assertEqual(0, r.returncode,
                                 '%s nao corre sozinho:\n%s' % (rel, r.stderr[-600:]))

    def test_o_caminho_aponta_para_a_raiz_e_nao_para_a_propria_pasta(self):
        """A causa, e nao so o sintoma: quem insere `HERE` em vez da raiz erra."""
        for rel in EXECUTAVEIS:
            caminho = os.path.join(RAIZ, rel)
            if not os.path.exists(caminho):
                continue
            fonte = open(caminho, encoding='utf-8').read()
            if '_gavetas' not in fonte:
                continue
            with self.subTest(ficheiro=rel):
                self.assertNotIn(
                    'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))',
                    fonte,
                    '%s poe a propria pasta no caminho; `_gavetas` vive na raiz' % rel)


if __name__ == '__main__':
    unittest.main(verbosity=2)
