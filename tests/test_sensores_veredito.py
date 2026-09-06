"""
O veredito da camada de sensores humanos não pode crescer sozinho.

Este arquivo não testa código: testa a AFIRMAÇÃO. Um artefato de conclusão é
onde o exagero entra mais fácil, porque ninguém executa um JSON.
"""
import json
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO = os.path.join(RAIZ, 'data', 'samples', 'IT-CASOS',
                       'IT-SENSORES-HUMANOS-VEREDITO.json')


class OVereditoNaoUltrapassaOMedido(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(CAMINHO, encoding='utf-8') as fh:
            cls.V = json.load(fh)

    def test_o_veredito_e_do_painel_e_nao_da_camada(self):
        """"NESTE PAINEL" e a palavra que impede a generalizacao."""
        self.assertEqual(self.V['HUMAN_SENSOR_VERDICT'],
                         'HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL')
        self.assertIn('IN_THIS_PANEL', self.V['HUMAN_SENSOR_VERDICT'])

    def test_o_numero_de_autores_perguntados_bate_com_o_de_elegiveis(self):
        """Se sobrar autor por perguntar, o veredito nao podia ter sido dado."""
        e = self.V['ETAPA_2_POSTS']
        self.assertEqual(e['AUTORES_POR_PERGUNTAR'], 0)
        self.assertEqual(e['AUTORES_PERGUNTADOS'], e['AUTORES_ELEGIVEIS'])

    def test_os_confirmados_e_plausiveis_nao_se_misturam(self):
        e1 = self.V['ETAPA_1_IDENTIDADE']
        confirmados = set(e1['IDENTITY_CONFIRMED'])
        plausiveis = set(e1['IDENTITY_PLAUSIBLE_NOT_PROVED'])
        sem = set(e1['IDENTITY_NOT_ENOUGH_EVIDENCE'])
        self.assertEqual(confirmados & plausiveis, set())
        self.assertEqual(confirmados & sem, set())
        self.assertEqual(len(confirmados | plausiveis | sem), 8)

    def test_os_elegiveis_sao_exatamente_confirmados_mais_plausiveis(self):
        e1, e2 = self.V['ETAPA_1_IDENTIDADE'], self.V['ETAPA_2_POSTS']
        self.assertEqual(e2['AUTORES_ELEGIVEIS'],
                         len(e1['IDENTITY_CONFIRMED']) +
                         len(e1['IDENTITY_PLAUSIBLE_NOT_PROVED']))

    def test_zero_sinal_nao_foi_promovido_a_zero_no_mundo(self):
        nao = self.V['O_QUE_ESTE_VEREDITO_NAO_DIZ']['NAO_DIZ']
        junto = ' '.join(nao)
        self.assertIn('não medem isso', junto)
        self.assertIn('não foram medidos', junto)
        self.assertIn('é diferente', junto)

    def test_o_que_nao_foi_medido_esta_nomeado(self):
        nm = self.V['O_QUE_ESTE_VEREDITO_NAO_DIZ']['NOT_MEASURED']
        for plataforma in ('Instagram', 'YouTube', 'Meta'):
            self.assertIn(plataforma, nm)

    def test_nenhuma_palavra_proibida_aparece_como_afirmacao(self):
        """As proibicoes podem ser NOMEADAS na lista de proibicoes — e so la."""
        proibidas = self.V['AINDA_PROIBIDO_ESCREVER']
        corpo = json.dumps({k: v for k, v in self.V.items()
                            if k != 'AINDA_PROIBIDO_ESCREVER'}, ensure_ascii=False)
        for p in proibidas:
            self.assertNotIn(p, corpo, p)

    def test_a_localizacao_do_fato_ficou_desconhecida_e_nao_foi_chutada(self):
        self.assertTrue(self.V['FACT_LOCATION'].startswith('NOT_KNOWN'))

    def test_nenhum_token_no_artefato(self):
        with open(CAMINHO, encoding='utf-8') as fh:
            self.assertNotIn('apify_api_', fh.read())
        self.assertEqual(self.V['TOKEN_VALUE_COMMITTED'], 'NO')

    def test_as_leis_da_rodada_estao_registradas(self):
        leis = self.V['LEIS_QUE_ESTA_RODADA_ACRESCENTOU']
        for essencial in ('NAME_MATCH ≠ PERSON', 'UNIT_EMPTY ≠ ROUTE_FAILURE',
                          'PLACE_MENTION ≠ FACT_LOCATION',
                          'PUBLISHED_AT ≠ FACT_TIME'):
            self.assertIn(essencial, leis)
