#!/usr/bin/env python3
"""A GESTAO DA COLETA — a fronteira que impede a G-05 uma camada acima.

    O GESTOR DECIDE O QUE E QUANDO.
    O ORQUESTRADOR DECIDE COMO E POR ONDE.

Sem esta fronteira, «vale a pena ir buscar isto outra vez?» acaba escrita
dentro de um coletor, e a decisao de coletar passa a viver espalhada.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import gestao_da_coleta as g  # noqa: E402


class AFronteiraEntreGestorEOrquestrador(unittest.TestCase):

    def test_as_duas_listas_nao_se_tocam(self):
        """⚠️ Se um conceito aparecesse nas duas, havia dois donos para a mesma
        decisao — e duas respostas possiveis para a mesma pergunta."""
        self.assertEqual(set(g.GESTOR_DECIDE) & set(g.ORQUESTRADOR_DECIDE),
                         set())

    def test_o_gestor_nao_chama_executor(self):
        junto = ' '.join(g.GESTOR_NAO_PODE)
        self.assertIn('chamar executor', junto)
        self.assertIn('escolher rota', junto)

    def test_a_rota_e_do_orquestrador(self):
        self.assertIn('QUAL_ROTA', g.ORQUESTRADOR_DECIDE)
        self.assertIn('QUAL_EXECUTOR', g.ORQUESTRADOR_DECIDE)
        self.assertNotIn('QUAL_ROTA', g.GESTOR_DECIDE)

    def test_a_razao_da_fronteira_esta_escrita(self):
        self.assertIn('G-05', g.PORQUE_A_FRONTEIRA)


class AsConfusoesRecusadas(unittest.TestCase):

    def test_unknown_nao_e_not_satisfied(self):
        """«Nao temos» e uma medida. «Ninguem foi ver» e outra. Achatar as duas
        faz o sistema ir buscar o que ja tem."""
        self.assertIn('UNKNOWN', g.SATISFACAO)
        self.assertIn('NOT_SATISFIED', g.SATISFACAO)

    def test_stale_e_um_estado_proprio(self):
        """JA TEMOS != ESTA ATUALIZADO."""
        self.assertIn('STALE', g.SATISFACAO)

    def test_as_leis_dizem_que_velho_nao_e_inutil(self):
        junto = ' | '.join(g.LEIS)
        self.assertIn('VELHO != INUTIL', junto)
        self.assertIn('FALTA != URGENTE', junto)
        self.assertIn('CARO != IMPOSSIVEL', junto)


class ADecisaoEUmArtefato(unittest.TestCase):

    def test_a_decisao_diz_quem_decidiu_e_porque(self):
        """Decisao que nao fica escrita nao pode ser avaliada depois."""
        for c in ('PORQUE', 'QUEM_DECIDIU', 'QUANDO', 'POLICY_VERSION'):
            self.assertIn(c, g.CAMPOS_DA_DECISAO)

    def test_ha_como_dizer_que_a_politica_nao_cobre(self):
        """⚠️ Sem `NEEDS_HUMAN`, um caso nao previsto seria forcado numa
        decisao qualquer — e forcar e como se inventa politica sem querer."""
        self.assertIn('NEEDS_HUMAN', g.DECISOES)
        self.assertIn('DEFER_UNKNOWN', g.DECISOES)

    def test_nao_coletar_e_uma_decisao_legitima(self):
        self.assertIn('DO_NOT_COLLECT', g.DECISOES)

    def test_ha_resultado_para_ligar_a_decisao(self):
        """Decisao sem resultado medido nao ensina nada."""
        self.assertIn('DECISION_ID', g.CAMPOS_DO_RESULTADO)
        self.assertIn('CUSTO_REAL', g.CAMPOS_DO_RESULTADO)
        self.assertIn('GANHO_REAL', g.CAMPOS_DO_RESULTADO)
        self.assertIn('NOT_RUN', g.RESULTADOS)


class ANecessidadeEDeclarada(unittest.TestCase):

    def test_a_necessidade_declara_janela_e_frescura(self):
        """«Velho» só quer dizer alguma coisa em relação a uma necessidade que
        declara a sua própria janela."""
        self.assertIn('JANELA', g.CAMPOS_DA_NECESSIDADE)
        self.assertIn('FRESCURA_EXIGIDA', g.CAMPOS_DA_NECESSIDADE)

    def test_a_necessidade_diz_porque_importa(self):
        """Sem isto, é recolha por recolha."""
        self.assertIn('PORQUE_IMPORTA', g.CAMPOS_DA_NECESSIDADE)

    def test_a_falta_diz_como_foi_medida(self):
        """Sem isto, a falta é uma impressão."""
        self.assertIn('COMO_FOI_MEDIDO', g.CAMPOS_DA_FALTA)


class APrioridadeNaoEUmNumeroMagico(unittest.TestCase):

    def test_a_prioridade_diz_de_onde_veio(self):
        self.assertIn('PRIORITY_BASIS', g.CAMPOS_DA_PRIORIDADE)
        self.assertIn('QUEM_DECIDIU', g.CAMPOS_DA_PRIORIDADE)

    def test_ha_prioridade_desconhecida(self):
        """Forçar uma prioridade em quem não foi avaliado inventa urgência."""
        self.assertIn('UNKNOWN', g.PRIORIDADES)


class NaoHaIAViva(unittest.TestCase):

    def test_esta_escrito_que_nada_corre_sozinho(self):
        self.assertIn('nao decide nada sozinho', g.SEM_IA_VIVA)
        self.assertIn('CONTRATO NAO E IMPLEMENTACAO', g.SEM_IA_VIVA)

    def test_o_modulo_nao_executa_nada(self):
        """⚠️ Contra o código, não contra a intenção."""
        import inspect
        fonte = inspect.getsource(g)
        for proibido in ('subprocess', 'requests', 'urllib', 'psycopg'):
            self.assertNotIn('import %s' % proibido, fonte)


if __name__ == '__main__':
    unittest.main(verbosity=2)
