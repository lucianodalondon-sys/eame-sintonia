#!/usr/bin/env python3
"""E1..E6 — A ESCADA DA CONEXAO.

    GREP NEGATIVO prova que a ligacao NAO existe.
    GREP POSITIVO so promove a CANDIDATA.

E candidata nao fecha arquitetura — era exatamente esse o atalho que pintava
verde cedo demais.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'system-map', 'scripts'))
import _gavetas  # noqa: E402,F401
import censo_das_estradas_it as ce   # noqa: E402

FIX = os.path.join('tests', 'fixtures', 'ARESTAS')


class AEscadaDaConexao(unittest.TestCase):

    def _nivel(self, ficheiro, agulha='derived_artifact', **k):
        return ce._liga([os.path.join(FIX, ficheiro), agulha], **k)

    # ── E1 e E2 ───────────────────────────────────────────────────────────
    def test_E1_string_so_em_comentario_nao_fecha(self):
        n = self._nivel('so_comentario.py')
        self.assertEqual(n, ce.CANDIDATA)
        self.assertFalse(ce._fecha(n), 'um comentario fechou uma aresta')

    def test_E2_string_so_em_docstring_nao_fecha(self):
        """O mesmo ficheiro carrega o caso do docstring — e o AST o remove."""
        with open(os.path.join(RAIZ, FIX, 'so_comentario.py'), encoding='utf-8') as f:
            self.assertIn('derived_artifact', f.read(), 'a fixture perdeu o caso')
        codigo = ce._codigo_executavel(os.path.join(RAIZ, FIX, 'so_comentario.py'))
        self.assertIsNotNone(codigo)
        self.assertNotIn('derived_artifact', codigo,
                         'o docstring sobreviveu ao AST e ainda pode «provar»')

    # ── E3 ────────────────────────────────────────────────────────────────
    def test_E3_codigo_executavel_e_CODE_CONNECTED(self):
        n = self._nivel('codigo_real.py')
        self.assertEqual(n, ce.POR_CODIGO)
        self.assertTrue(ce._fecha(n))

    # ── E4 e E5 ───────────────────────────────────────────────────────────
    def test_E4_prova_de_teste_sobe_para_TESTED(self):
        n = self._nivel('codigo_real.py', prova_de_teste='provas/x.py::caso')
        self.assertEqual(n, ce.POR_TESTE)
        self.assertTrue(ce._fecha(n))

    def test_E5_prova_de_execucao_sobe_para_OBSERVED(self):
        n = self._nivel('codigo_real.py', prova_observada='run 34258433872')
        self.assertEqual(n, ce.OBSERVADA)
        self.assertTrue(ce._fecha(n))

    def test_E5b_prova_nao_promove_o_que_o_grep_negou(self):
        """CAN DO != DID DO, e prova de execucao nao inventa mencao que nao ha."""
        n = self._nivel('codigo_real.py', 'artefato_que_nao_existe',
                        prova_observada='run 1')
        self.assertEqual(n, ce.SEM_EVIDENCIA)

    # ── E6 ────────────────────────────────────────────────────────────────
    def test_E6_candidata_nunca_resulta_arquitetura_fechada(self):
        for degrau in ce.ESCADA:
            fecha = ce._fecha(degrau)
            if degrau in (ce.SEM_EVIDENCIA, ce.CANDIDATA):
                self.assertFalse(fecha, '%s fechou arquitetura' % degrau)
            else:
                self.assertTrue(fecha, '%s deixou de fechar' % degrau)

    def test_E6b_o_degrau_minimo_e_CODE_e_nao_OBSERVED(self):
        """Arquitetura e observacao continuam eixos separados."""
        self.assertEqual(ce.DEGRAU_QUE_FECHA, ce.POR_CODIGO)
        self.assertTrue(ce._fecha(ce.POR_CODIGO))

    def test_E6c_grep_negativo_continua_sendo_prova(self):
        self.assertEqual(self._nivel('codigo_real.py', 'nada_disto_existe'),
                         ce.SEM_EVIDENCIA)
        self.assertEqual(self._nivel('ficheiro_que_nao_existe.py'),
                         ce.SEM_EVIDENCIA)

    def test_E6d_nenhuma_aresta_do_modelo_fecha_por_candidata(self):
        for r in ce.rotas_medidas():
            for nome, st in r['STEPS'].items():
                if st.get('CONNECTION_LEVEL') == ce.CANDIDATA:
                    self.assertIn(nome, r['STEPS_BLOQUEANDO'],
                                  '%s/%s fechou com ligacao apenas candidata'
                                  % (r['ROUTE_CLASS_ID'], nome))


if __name__ == '__main__':
    unittest.main(verbosity=2)
