#!/usr/bin/env python3
"""Nenhuma asserção pode comparar um literal com outro literal.

`self.assertIn('ORGANIZATION', 'CEREAL_LOCAL_FIELD_ORGANIZATION_SENSOR_FOUND')` é
verdade em qualquer repositório, com ou sem o código que ela diz guardar. Um teste
assim não pode reprovar — e a suíte inteira fica um pouco menos verdadeira por causa
dele, porque ele conta como prova no total publicado.

    LITERAL_vs_LITERAL != PROVA

Esta varredura é um META-TESTE: ela não olha para o produto, olha para a suíte.
"""
import ast
import glob
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTES = os.path.join(ROOT, 'tests')

COMPARADORES = {'assertEqual', 'assertNotEqual', 'assertIn', 'assertNotIn',
                'assertIs', 'assertIsNot', 'assertLess', 'assertGreater',
                'assertLessEqual', 'assertGreaterEqual', 'assertRegex',
                'assertNotRegex'}


def _e_literal(no):
    return isinstance(no, ast.Constant) and isinstance(no.value, (str, int, float, bool))


class TestNenhumaAssercaoCompara2LiteraisEntreSi(unittest.TestCase):

    def test_a_suite_inteira(self):
        achados = []
        for caminho in sorted(glob.glob(os.path.join(TESTES, 'test_*.py'))):
            with open(caminho, encoding='utf-8') as f:
                fonte = f.read()
            try:
                arvore = ast.parse(fonte)
            except SyntaxError:
                continue
            for no in ast.walk(arvore):
                if not (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)):
                    continue
                if no.func.attr not in COMPARADORES or len(no.args) < 2:
                    continue
                if _e_literal(no.args[0]) and _e_literal(no.args[1]):
                    achados.append('%s:%d %s' % (os.path.basename(caminho),
                                                 no.lineno, no.func.attr))
        self.assertEqual([], achados,
                         'asserção que compara dois literais — não pode reprovar nunca')


if __name__ == '__main__':
    unittest.main(verbosity=2)
