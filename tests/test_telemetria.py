#!/usr/bin/env python3
"""O CONTRATO DA TELEMETRIA — as confusoes que ele recusa.

Cada teste aqui guarda uma distincao que ja foi achatada nalgum relatorio desta
casa. O resultado foi sempre o mesmo: um numero que parecia bom porque escondia
o que nao sabia.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import telemetria as t  # noqa: E402


class AsQuatroConfusoesRecusadas(unittest.TestCase):

    def test_error_nao_e_rejected(self):
        """O sistema falhou / o item nao servia. Somar os dois faz uma coleta
        saudavel parecer avariada, e uma avariada parecer exigente."""
        self.assertIn('ERROR', t.DESTINOS_DO_ITEM)
        self.assertIn('REJECTED', t.DESTINOS_DO_ITEM)

    def test_not_run_nao_e_error(self):
        """⚠️ Uma etapa a jusante de uma que falhou NAO falhou — nunca comecou.
        Chamar-lhe erro faz um defeito parecer cinco."""
        self.assertIn('NOT_RUN', t.ESTADOS_DE_ETAPA)
        self.assertIn('NOT_RUN', t.DESTINOS_DO_ITEM)

    def test_unknown_nao_e_zero(self):
        """Ninguem mediu / mediu-se e deu nada."""
        self.assertIn('UNKNOWN', t.DESTINOS_DO_ITEM)

    def test_o_vocabulario_e_fechado(self):
        """Mensagem livre por falha e mensagem que ninguem consegue contar."""
        self.assertIn('UNKNOWN_FAILURE', t.CODIGOS_DE_DIAGNOSTICO)
        self.assertIn('POLICY_REFUSED', t.CODIGOS_DE_DIAGNOSTICO)


class AContaQueTemDeFechar(unittest.TestCase):
    """100% nao precisa CHEGAR. 100% precisa ser EXPLICADO."""

    def test_tudo_explicado_fecha(self):
        fecha, sobra = t.reconcilia({'INPUT_COUNT': 100, 'PASSED': 40,
                                     'REJECTED': 30, 'ERRORS': 5,
                                     'NOT_RUN': 0, 'UNKNOWN': 20,
                                     'DEDUPED': 5})
        self.assertTrue(fecha)
        self.assertEqual(sobra, 0)

    def test_item_sem_porta_e_o_defeito(self):
        """⚠️ ESTE E O TESTE. 40 de 100 nao e o problema — os 60 sem nome sao."""
        fecha, sobra = t.reconcilia({'INPUT_COUNT': 100, 'PASSED': 40})
        self.assertFalse(fecha)
        self.assertEqual(sobra, 60)

    def test_sem_entrada_nao_se_finge_que_fecha(self):
        """UNKNOWN != ZERO: nao saber quanto entrou nao e ter entrado nada."""
        fecha, sobra = t.reconcilia({'PASSED': 10})
        self.assertFalse(fecha)
        self.assertIsNone(sobra)


class OGraoMudaNoCaminho(unittest.TestCase):

    def test_graos_diferentes_nao_se_dividem(self):
        """⚠️ Um PDF que vira 40 paginas nao tem 4000% de rendimento."""
        razao, erro = t.compara_contagens(
            {'INPUT_GRAIN': 'documento', 'OUTPUT_GRAIN': 'pagina',
             'INPUT_COUNT': 1, 'OUTPUT_COUNT': 40})
        self.assertIsNone(razao)
        self.assertIn('GRAIN_MISMATCH', erro)

    def test_mesmo_grao_compara(self):
        razao, erro = t.compara_contagens(
            {'INPUT_GRAIN': 'documento', 'OUTPUT_GRAIN': 'documento',
             'INPUT_COUNT': 10, 'OUTPUT_COUNT': 4})
        self.assertIsNone(erro)
        self.assertAlmostEqual(razao, 0.4)

    def test_sem_entrada_nao_ha_razao(self):
        razao, erro = t.compara_contagens(
            {'INPUT_GRAIN': 'x', 'OUTPUT_GRAIN': 'x', 'INPUT_COUNT': 0,
             'OUTPUT_COUNT': 5})
        self.assertIsNone(razao)
        self.assertIn('UNKNOWN', erro)


class RetomarNaoERecomecar(unittest.TestCase):

    def test_o_run_diz_a_ultima_etapa_boa(self):
        self.assertIn('LAST_GOOD_STAGE', t.CAMPOS_DO_RUN)
        self.assertIn('RESUME_SAFE', t.CAMPOS_DO_RUN)

    def test_retomar_desconhecido_nao_vira_seguro(self):
        """Nao provado nao e seguro. Recomecar do zero criaria uma SEGUNDA
        corrida — ja aconteceu aqui, quando um relatorio rebentou depois de a
        producao estar correta."""
        self.assertIn('RESUME_UNKNOWN', t.RESUME)
        self.assertIn('RESUME_UNSAFE', t.RESUME)


class NaoInstalarFerramentaAntesDaPergunta(unittest.TestCase):

    def test_as_referencias_ficam_de_fora(self):
        for nome in ('OpenTelemetry', 'Grafana', 'Prometheus'):
            self.assertIn(nome, t.NAO_INSTALAR)

    def test_a_razao_esta_escrita(self):
        self.assertIn('tampa', t.PORQUE_NAO_INSTALAR)

    def test_nenhuma_dessas_e_dependencia_do_repo(self):
        """⚠️ Contra o codigo, nao contra a intencao: se alguem as importar,
        isto reprova."""
        import subprocess
        r = subprocess.run(
            ['git', 'grep', '-lIE', r'^\s*(import|from)\s+(opentelemetry|prometheus_client)'],
            cwd=RAIZ, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), '', r.stdout)


class AsEtapasEAsLeis(unittest.TestCase):

    def test_as_oito_leis_estao_escritas(self):
        junto = ' | '.join(t.LEIS)
        self.assertIn('MODULE WORKS != EDGE WORKS != FLOW WORKS', junto)
        self.assertIn('UNACCOUNTED_INPUT DEVE SER 0', junto)
        self.assertIn('100% PRECISA SER EXPLICADO', junto)

    def test_a_etapa_declara_os_dois_graos(self):
        self.assertIn('INPUT_GRAIN', t.CAMPOS_DA_ETAPA)
        self.assertIn('OUTPUT_GRAIN', t.CAMPOS_DA_ETAPA)
        self.assertIn('UNACCOUNTED_INPUT', t.CAMPOS_DA_ETAPA)

    def test_not_applicable_existe_e_exige_razao(self):
        """Uma etapa que nao existe nesta rota nao e uma etapa que falhou."""
        self.assertIn('NOT_APPLICABLE', t.ESTADOS_DE_ETAPA)
        self.assertIn('SKIPPED', t.ESTADOS_DE_ETAPA)


if __name__ == '__main__':
    unittest.main(verbosity=2)
