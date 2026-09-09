#!/usr/bin/env python3
"""A INTELIGENCIA ESTA CONGELADA — e este teste e o ato, nao o aviso.

Uma regra escrita num relatorio nao segura nada. Estes casos falham se alguem
implementar inteligencia antes de a fundacao da coleta fechar, e falham
olhando para o DIFF REAL contra a Biblia — nao para a palavra num comentario.

    APAGAR A MEMORIA DO ERRO NAO E CONSERTAR O ERRO,
    e um teste que le comentario nao le comportamento.
"""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import fundacao_da_coleta as fdc   # noqa: E402

# A base contra a qual esta missao e medida.
BASE = 'origin/claude/italia-biblia-integracao-v1'

# Onde a inteligencia vive. Medido, nao adivinhado: sao as gavetas e prefixos
# que as areas congeladas usam hoje neste repositorio.
CAMINHOS_DE_INTELIGENCIA = (
    'inteligencia/', 'field_voices', 'fieldvoices', 'oportunidade',
    'opportunity', 'signals', 'sinais_', 'scoring', 'score_',
    'recomenda', 'recommend',
)


def _git(*args):
    r = subprocess.run(('git',) + args, capture_output=True, text=True, cwd=RAIZ)
    return r.stdout.strip().split('\n') if r.stdout.strip() else []


class OCongelamentoEUmaTrava(unittest.TestCase):

    def test_a_fundacao_ainda_nao_fechou(self):
        """Se isto virar SIM sem o mapa mudar, alguem soltou a trava sozinho."""
        pode, motivo = fdc.pode_implementar_inteligencia()
        if fdc.COLLECTION_FOUNDATION_CLOSED:
            caminho = os.path.join(RAIZ, fdc.MAPA)
            self.assertTrue(os.path.exists(caminho),
                            'a fundacao foi declarada fechada sem o mapa que a sustenta')
        else:
            self.assertFalse(pode)
            self.assertIn(fdc.BLOQUEIO, motivo)

    def test_o_padrao_e_recusar(self):
        """Trava que so funciona quando configurada nao e trava."""
        self.assertIn(False, (fdc.COLLECTION_FOUNDATION_CLOSED, False))
        self.assertEqual(fdc.BLOQUEIO, 'INTELLIGENCE_IMPLEMENTATION_BLOCKED')

    def test_ler_continua_permitido(self):
        """Congelar implementacao nao pode virar proibir de olhar."""
        _pode, motivo = fdc.pode_implementar_inteligencia()
        self.assertIn(fdc.PERMITIDO_LER, motivo)

    def test_o_mapa_de_fechamento_existe(self):
        self.assertTrue(os.path.exists(os.path.join(RAIZ, fdc.MAPA)),
                        'a lei aponta para um mapa que nao existe')


class ODiffDestaMissaoNaoTocouInteligencia(unittest.TestCase):
    """A auditoria do ATO. Contra o diff, nunca contra a intencao."""

    @classmethod
    def setUpClass(cls):
        cls.tocados = [f for f in _git('diff', '--name-only', BASE, 'HEAD') if f]

    def test_a_base_de_comparacao_existe(self):
        """Sem base, esta auditoria diria «zero» por nao ter olhado nada."""
        self.assertTrue(_git('rev-parse', '--verify', BASE),
                        'a Biblia nao esta disponivel: a auditoria nao mediu nada')

    def test_nenhum_ficheiro_de_inteligencia_foi_tocado(self):
        sujos = [f for f in self.tocados
                 if any(p in f.lower() for p in CAMINHOS_DE_INTELIGENCIA)]
        self.assertEqual(sujos, [], 'INTELLIGENCE_IMPLEMENTATION != 0: %s' % sujos)

    def test_o_portal_nao_ganhou_implementacao(self):
        """Mapa gerado e servido nao e implementacao de portal — o resto e."""
        portal = [f for f in self.tocados if f.startswith('italia-portale/')]
        so_mapa = [f for f in portal if '/system-map/' in f]
        self.assertEqual(sorted(portal), sorted(so_mapa),
                         'PORTAL_IMPLEMENTATION != 0: %s'
                         % sorted(set(portal) - set(so_mapa)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
