#!/usr/bin/env python3
"""O RELATORIO DO FLUXO — sem dado nao e zero.

    UM RELATORIO QUE MOSTRA 0 ONDE NINGUEM MEDIU
    E PIOR DO QUE NAO EXISTIR.

Ele convida a concluir que nada aconteceu. Estes testes guardam a diferenca
entre «medimos e deu nada» e «ninguem mediu».
"""
import json
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUXO = os.path.join(RAIZ, 'system-map', 'data', 'fluxo.generated.json')


def _json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


class SemDadoNaoEZero(unittest.TestCase):

    def setUp(self):
        self.d = _json(FLUXO)

    def test_etapa_executor_e_custo_dizem_not_instrumented(self):
        """⚠️ Nenhum deles pode aparecer como 0."""
        for chave in ('POR_ETAPA', 'POR_EXECUTOR', 'CUSTO'):
            self.assertEqual(self.d[chave]['ESTADO'], 'NOT_INSTRUMENTED',
                             chave)

    def test_cada_buraco_diz_quem_teria_de_emitir(self):
        """«Nao instrumentado» sem dono e uma queixa. Com dono, e uma tarefa."""
        for chave, texto in self.d['O_QUE_FALTA_INSTRUMENTAR'].items():
            self.assertIn('emitir', texto.lower(), chave)

    def test_a_regra_esta_escrita_no_proprio_relatorio(self):
        self.assertIn('NOT_INSTRUMENTED', self.d['SEM_DADO_NAO_E_ZERO'])

    def test_nenhuma_corrida_finge_ter_etapa(self):
        for l in self.d['POR_CORRIDA']:
            self.assertEqual(l['STAGE'], 'NOT_INSTRUMENTED', l['RUN_ID'])


class AContaTemDeFechar(unittest.TestCase):
    """100% nao precisa CHEGAR. 100% precisa ser EXPLICADO."""

    def setUp(self):
        self.d = _json(FLUXO)

    def test_nenhuma_observacao_fica_sem_porta(self):
        for l in self.d['POR_CORRIDA']:
            self.assertEqual(
                l['UNACCOUNTED_INPUT'], 0,
                '%s tem %d observacoes sem destino com nome'
                % (l['RUN_ID'], l['UNACCOUNTED_INPUT']))

    def test_a_soma_dos_destinos_bate_com_a_entrada(self):
        for l in self.d['POR_CORRIDA']:
            self.assertEqual(sum(l['DESTINOS'].values()), l['INPUT_COUNT'],
                             l['RUN_ID'])

    def test_o_relatorio_diz_porque_a_conta_importa_mais_que_o_rendimento(self):
        self.assertIn('100%', self.d['PORQUE_A_CONTA_IMPORTA_MAIS_QUE_O_RENDIMENTO'])


class OGraoEDeclarado(unittest.TestCase):

    def test_toda_corrida_declara_os_dois_graos(self):
        for l in _json(FLUXO)['POR_CORRIDA']:
            self.assertTrue(l['INPUT_GRAIN'])
            self.assertTrue(l['OUTPUT_GRAIN'])


class ARotaNaoEmiteNaoERotaComZero(unittest.TestCase):

    def test_o_ledger_e_todo_de_uma_rota_so_e_isso_esta_dito(self):
        """⚠️ As outras rotas nao emitiram ZERO — nao emitem NADA. E esta e
        divida (RC-9), nao estrada a fechar."""
        d = _json(FLUXO)
        self.assertIn('DIVIDA', d['POR_ROTA']['NOTA'].upper())
        self.assertIn('nao e que tenham emitido', d['POR_ROTA']['NOTA'])


class ADuracaoSoContaComAsDuasPontas(unittest.TestCase):

    def test_duracao_medida_ou_nula_nunca_zero_por_omissao(self):
        """Meia medida nao e medida: sem uma das pontas, fica None."""
        for l in _json(FLUXO)['POR_CORRIDA']:
            if l['DURATION_MS'] is not None:
                self.assertGreater(l['DURATION_MS'], 0, l['RUN_ID'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
