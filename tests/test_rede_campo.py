"""
Provas da rede. O risco desta rodada é o inverso do da anterior: agora que UMA
pessoa provou sinal prospectivo, a tentação é deixá-la falar pela cultura do caso
e pela Itália inteira.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import fato_local as fl           # noqa: E402
import italia_rede_campo as rc    # noqa: E402
import italia_sensores_v2 as sv   # noqa: E402


class OVereditoSobrePessoasSoUsaPessoas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = rc.medir()

    def test_toda_entrada_declara_pessoa_ou_organizacao(self):
        for e in rc.PESSOAS + rc.ORGANIZACOES_NOVAS:
            self.assertIn(e['ENTITY_KIND'], sv.ENTITY_KINDS, e['NAME'])

    def test_a_lista_de_pessoas_so_tem_pessoas(self):
        for p in rc.PESSOAS:
            self.assertEqual(p['ENTITY_KIND'], sv.PERSON, p['NAME'])

    def test_o_veredito_de_pessoa_vem_de_uma_pessoa_de_verdade(self):
        self.assertEqual(self.M['PROSPECTIVE_HUMAN_PERSON_SENSOR'], 'PROVED')
        prosp = [p for p in rc.PESSOAS
                 if p['SENSOR_POTENTIAL'] == sv.PROSPECTIVE_SENSOR]
        self.assertTrue(prosp)
        for p in prosp:
            self.assertEqual(p['ENTITY_KIND'], sv.PERSON)
            self.assertNotEqual(p['PRIMARY_PUBLIC_CHANNEL'],
                                'INSTITUTIONAL_CHANNEL_ONLY', p['NAME'])

    def test_pessoa_sem_canal_proprio_nao_conta_como_sensor_pessoal(self):
        """Os dois técnicos do ERSA são as pessoas certas — e o sinal delas sai
        pela instituição. PERSON_INSIDE_INSTITUTION ≠ PERSON_AS_PUBLIC_SENSOR."""
        dentro = [p for p in rc.PESSOAS
                  if p['PRIMARY_PUBLIC_CHANNEL'] == 'INSTITUTIONAL_CHANNEL_ONLY']
        self.assertEqual(len(dentro), 2)
        for p in dentro:
            self.assertNotEqual(p['SENSOR_POTENTIAL'], sv.PROSPECTIVE_SENSOR)
            self.assertIn(rc.REPETITION_ONLY, p['ADDS'])
        self.assertIn('PERSON_INSIDE_INSTITUTION ≠ PERSON_AS_PUBLIC_SENSOR',
                      self.M['LAWS'])

    def test_a_correcao_da_rodada_anterior_esta_registrada(self):
        c = self.M['CORRECTION_OF_PREVIOUS_ROUND']
        self.assertIn('organizações', c)
        self.assertIn('INSTITUTIONAL_SIGNAL ≠ HUMAN_PERSON_SIGNAL', c)


class OPositivoNaoFalaPelaCulturaDoCaso(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = rc.medir()

    def test_o_veredito_carrega_que_a_cultura_e_outra(self):
        deve = self.M['PROSPECTIVE_HUMAN_PERSON_SENSOR_MUST_CARRY']
        self.assertIn('vite', deve['CROP'])
        self.assertIn('não grano duro', deve['CROP'])
        self.assertIn('Friuli', deve['REGION'])
        self.assertIn('não é sinal do caso', deve['CASE'])

    def test_a_lei_que_impede_a_promocao_esta_declarada(self):
        self.assertIn('CLASS_PROVED_ON_ANOTHER_CROP ≠ CASE_SIGNAL', self.M['LAWS'])

    def test_o_pesquisador_continua_NOT_PROVED_para_antecipacao(self):
        self.assertEqual(self.M['PROSPECTIVE_RESEARCHER_SENSOR'], 'NOT_PROVED')

    def test_os_seis_vereditos_nao_sao_o_mesmo_valor(self):
        vals = [self.M[k] for k in
                ('PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR',
                 'PROSPECTIVE_TECHNICAL_PERSON_SENSOR', 'PROSPECTIVE_PRODUCER_SENSOR',
                 'PROSPECTIVE_CREATOR_SENSOR', 'PROSPECTIVE_RESEARCHER_SENSOR')]
        self.assertGreaterEqual(len(set(vals)), 3)


class ARedeNaoInventaRelacao(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = rc.medir()

    def test_toda_aresta_tem_evidencia_textual(self):
        for e in self.M['NETWORK_EDGES']:
            self.assertTrue(e['EVIDENCE'], e)
            self.assertIn(e['FROM_KIND'], sv.CLASSES)
            self.assertIn(e['TO_KIND'], sv.CLASSES)

    def test_o_creator_citado_pelo_boletim_esta_no_texto_preservado(self):
        """A aresta mais improvável da rede precisa estar no arquivo, não na
        minha memória."""
        caminho = os.path.join(RAIZ, 'data/samples/IT-T5-SENSORES',
                               'collio-boll-06-vite-2026-05-15.txt')
        with open(caminho, encoding='utf-8') as fh:
            t = fh.read()
        self.assertIn('Lorenzo Ghiraldelli', t)
        self.assertIn('Pazzi per il Meteo Goriziano', t)
        self.assertIn('Telegram', t)

    def test_o_autor_nomeado_do_boletim_esta_no_texto_preservado(self):
        caminho = os.path.join(RAIZ, 'data/samples/IT-T5-SENSORES',
                               'collio-boll-06-vite-2026-05-15.txt')
        with open(caminho, encoding='utf-8') as fh:
            t = fh.read()
        self.assertIn('Dario Maurigh', t)
        self.assertIn('Consorzio Collio', t)

    def test_a_rede_propria_de_estacoes_esta_no_texto(self):
        """É o que sustenta MORE_LOCAL_THAN_INSTITUTION."""
        caminho = os.path.join(RAIZ, 'data/samples/IT-T5-SENSORES',
                               'collio-boll-06-vite-2026-05-15.txt')
        with open(caminho, encoding='utf-8') as fh:
            t = fh.read()
        self.assertIn('stazioni agrometeorologiche gestite dal Consorzio Collio', t)
        for localidade in ('Dolegna', 'Plessiva', 'Pradis'):
            self.assertIn(localidade, t)

    def test_nenhum_dado_pessoal_nos_arquivos_preservados(self):
        import re
        for L in self.M['CONTENTS_READ']:
            with open(os.path.join(RAIZ, L['EVIDENCE_PATH']), encoding='utf-8') as fh:
                self.assertIsNone(re.search(r'[\w.+-]+@[\w.-]+\.\w{2,}', fh.read()),
                                  L['ID'])

    def test_o_teto_de_novas_entradas_foi_respeitado(self):
        self.assertLessEqual(self.M['NEW_ENTRIES'], rc.CAP_NEW_ENTRIES
                             if hasattr(rc, 'CAP_NEW_ENTRIES') else rc.TETO_NOVOS)


class PrevisaoEObservacaoFicamSeparadas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = rc.medir()

    def test_os_dois_tipos_convivem_sem_se_fundir(self):
        self.assertEqual(self.M['MODELLED_RISK'], ['Friuli-Venezia Giulia'])
        self.assertEqual(sorted(self.M['FIELD_OBSERVATION']),
                         ['Branca di Gubbio', 'Parrano'])
        self.assertEqual(set(self.M['MODELLED_RISK']) &
                         set(self.M['FIELD_OBSERVATION']), set())

    def test_a_convergencia_e_registrada_e_nao_somada(self):
        c = self.M['CONVERGENCE']
        self.assertIn('preservados separados', c)
        self.assertIn('MESMO documento', c)

    def test_amostra_de_diagnostico_nunca_vira_incidencia(self):
        for L in self.M['CONTENTS_READ']:
            o = L['OCCURRENCE_NOT_INCIDENCE']
            self.assertEqual(o['INCIDENCE'], 'NOT_KNOWN', L['ID'])
            self.assertEqual(o['REGIONAL_PRESSURE'], 'NOT_KNOWN', L['ID'])

    def test_nenhuma_execucao_paga_e_nenhuma_palavra_proibida(self):
        self.assertEqual(self.M['APIFY_RUNS'], 0)
        corpo = json.dumps({k: v for k, v in self.M.items()
                            if k != 'STILL_FORBIDDEN_TO_WRITE'}, ensure_ascii=False)
        for p in self.M['STILL_FORBIDDEN_TO_WRITE']:
            self.assertNotIn(p, corpo, p)
