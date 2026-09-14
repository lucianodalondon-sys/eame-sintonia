#!/usr/bin/env python3
"""A OBSERVABILIDADE — nunca verde por silencio.

Uma dimensao sem dado NAO e uma dimensao saudavel. Estes testes guardam as tres
respostas que um mapa mal feito juntaria numa cor so.
"""
import json
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBS = os.path.join(RAIZ, 'system-map', 'data', 'observabilidade.generated.json')


def _json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


class NuncaVerdePorSilencio(unittest.TestCase):

    def setUp(self):
        self.d = _json(OBS)

    def test_o_vocabulario_separa_as_tres_respostas(self):
        """⚠️ NOT_INSTRUMENTED pede codigo que emita. NOT_MEASURED pede um
        leitor. MEDIDO pede leitura. Juntar as tres apaga o que fazer."""
        vale = {'MEDIDO', 'PARCIAL', 'NOT_MEASURED', 'NOT_INSTRUMENTED'}
        for dim in self.d['DIMENSOES']:
            self.assertIn(dim['ESTADO'], vale, dim['DIMENSAO'])

    def test_dimensao_sem_dado_nao_e_medida(self):
        for dim in self.d['DIMENSOES']:
            if dim['ESTADO'] in ('NOT_MEASURED', 'NOT_INSTRUMENTED'):
                self.assertTrue(dim.get('PORQUE'), dim['DIMENSAO'])

    def test_toda_dimensao_medida_diz_onde(self):
        for dim in self.d['DIMENSOES']:
            if dim['ESTADO'] in ('MEDIDO', 'PARCIAL'):
                self.assertTrue(dim['ONDE'], dim['DIMENSAO'])

    def test_parcial_diz_o_que_falta(self):
        """Meia medida publicada como medida e a maneira mais limpa de
        enganar."""
        for dim in self.d['DIMENSOES']:
            if dim['ESTADO'] == 'PARCIAL':
                self.assertTrue(dim.get('RESSALVA'), dim['DIMENSAO'])

    def test_a_regra_esta_escrita(self):
        self.assertIn('NOT_INSTRUMENTED', self.d['NUNCA_VERDE_POR_SILENCIO'])


class OsDoisReadyNaoProometemDemais(unittest.TestCase):

    def setUp(self):
        self.d = _json(OBS)

    def test_observability_ready_diz_o_que_nao_significa(self):
        """⚠️ Contrato pronto NAO e instrumentado, e instrumentado NAO e
        observado."""
        o = self.d['OBSERVABILITY']
        self.assertIn('NAO significa que se esta a medir', o['O_QUE_SIGNIFICA'])
        self.assertIn('CONTRATO PRONTO', o['O_QUE_NAO_SIGNIFICA'])

    def test_evolution_ready_nao_promete_ia_autonoma(self):
        e = self.d['EVOLUTION']
        self.assertIn('NAO significa IA autonoma pronta',
                      e['O_QUE_NAO_SIGNIFICA'])
        for p in ('ML_LIVE', 'BANDIT_LIVE', 'AUTO_PROMOTION'):
            self.assertIn(p, e['PROIBIDO_HOJE'])

    def test_ready_sim_exige_lista_de_faltas_vazia(self):
        for chave in ('OBSERVABILITY', 'EVOLUTION'):
            bloco = self.d[chave]
            valor = bloco['%s_READY' % chave]
            if valor == 'SIM':
                self.assertEqual(bloco['FALTAS'], [], chave)


class OScannerExistirNaoFechaFundacao(unittest.TestCase):

    def test_a_fundacao_continua_a_ser_lida_do_dono(self):
        """⚠️ Sao perguntas diferentes. Ter observabilidade nao fecha coleta."""
        d = _json(OBS)
        self.assertIn('nao decide a fundacao',
                      d['O_SCANNER_EXISTIR_NAO_FECHA_FUNDACAO'])
        self.assertIn('fundacao_da_coleta.py',
                      d['O_SCANNER_EXISTIR_NAO_FECHA_FUNDACAO'])

    def test_observability_ready_nao_destrava_a_fundacao(self):
        d = _json(OBS)
        if d['OBSERVABILITY']['OBSERVABILITY_READY'] == 'SIM':
            self.assertFalse(
                d['COLLECTION_FOUNDATION_CLOSED'],
                'observabilidade pronta fechou a fundacao sozinha')


class OsQuatroContratosExistem(unittest.TestCase):

    def test_os_contratos_estao_declarados(self):
        c = _json(OBS)['CONTRATOS_QUE_JA_EXISTEM']
        for k in ('TELEMETRIA', 'GESTAO_DA_COLETA', 'APRENDER_COM_A_FONTE',
                  'EVOLUCAO'):
            self.assertTrue(c.get(k), k)

    def test_o_dono_duplicado_e_contado_e_explicado(self):
        o = _json(OBS)['OBSERVABILITY']
        self.assertIsInstance(o['QUANTOS_CONCEITOS_COM_DONO_DUPLICADO'], int)
        self.assertIn('divergir', o['PORQUE_O_DUPLICADO_IMPORTA'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
