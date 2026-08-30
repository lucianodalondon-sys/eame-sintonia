"""
Provas da última falsificação. O risco: um "NÃO" honesto virar nacional, ou o nó
provincial encontrado virar uma pessoa que não existe.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import fato_local as fl               # noqa: E402
import italia_falsificar_cereais as fc  # noqa: E402


class AHipoteseCaiuPelaMetadeENaoInteira(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = fc.medir()

    def test_o_resultado_e_falsificacao_parcial_e_diz_as_duas_partes(self):
        self.assertEqual(self.M['RESULT'], 'PARTIALLY_FALSIFIED')
        self.assertIn('apenas regional', self.M['WHAT_FELL'])
        self.assertIn('sem camada pessoal', self.M['WHAT_HELD'])

    def test_a_organizacao_local_foi_provada_e_a_pessoa_nao(self):
        self.assertEqual(self.M['CEREAL_LOCAL_FIELD_ORGANIZATION_FOUND'], 'YES')
        self.assertEqual(self.M['LOCAL_ORGANIZATION_SENSOR']['STATE'], 'PROVED')
        self.assertEqual(self.M['TECHNICAL_PERSON_SENSOR']['STATE'], 'NOT_PROVED')
        self.assertIn('LOCAL_ORGANIZATION_SENSOR ≠ TECHNICAL_PERSON_SENSOR',
                      self.M['LAWS'])

    def test_nenhuma_pessoa_foi_encontrada_e_a_lista_esta_vazia(self):
        self.assertEqual(self.M['PERSONS_FOUND'], [])
        for m in fc.MEDIDOS:
            self.assertNotEqual(m['TECHNICIAN_STATE'], 'TECHNICIAN_PUBLIC_SENSOR',
                                m['NAME'])

    def test_a_rede_de_fazendas_nao_virou_produtor_pessoa(self):
        p = self.M['PRODUCER_PERSON_SENSOR']
        self.assertEqual(p['STATE'], 'NOT_PROVED')
        self.assertIn('sem nome', p['WHY'])

    def test_a_arquitetura_dominante_carrega_a_ressalva(self):
        self.assertEqual(self.M['IN_CEREALS_MEASURED_SIGNAL_ARCHITECTURE'],
                         'REGIONAL_INSTITUTION_DOMINANT')
        self.assertIn('NÃO quer dizer exclusivamente regional',
                      self.M['ARCHITECTURE_MUST_CARRY'])


class ONaoNuncaVirouNacional(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = fc.medir()

    def test_a_frase_proibida_esta_na_lista_de_proibidas(self):
        self.assertIn('DOES_NOT_EXIST_IN_ITALY', self.M['STILL_FORBIDDEN_TO_WRITE'])
        corpo = json.dumps({k: v for k, v in self.M.items()
                            if k != 'STILL_FORBIDDEN_TO_WRITE'}, ensure_ascii=False)
        for p in self.M['STILL_FORBIDDEN_TO_WRITE']:
            self.assertNotIn(p, corpo, p)

    def test_o_estado_do_sensor_local_usa_o_rotulo_longo_e_honesto(self):
        self.assertEqual(self.M['CEREAL_LOCAL_FIELD_SENSOR_FOUND'],
                         'NOT_OBSERVED_IN_MEASURED_HIGH_PRIORITY_NETWORKS')

    def test_o_grano_duro_nao_e_NO_e_sim_PROMISING(self):
        self.assertIn(self.M['DURUM_FUSARIUM_LOCAL_HUMAN_SENSOR'],
                      ('PROVED', 'PROMISING',
                       'NOT_OBSERVED_IN_MEASURED_HIGH_PRIORITY_NETWORKS',
                       'NOT_PROVED'))
        self.assertNotEqual(self.M['DURUM_FUSARIUM_LOCAL_HUMAN_SENSOR'], 'NO')

    def test_porta_com_cadastro_e_GATED_e_nunca_ausente(self):
        alsia = [m for m in fc.MEDIDOS if 'ALSIA' in m['NAME']]
        self.assertTrue(alsia)
        for m in alsia:
            self.assertEqual(m['VERDICT'], fc.NOT_MEASURED_ACCESS)
        self.assertIn('GATED ≠ ABSENT', self.M['LAWS'])

    def test_falha_de_transporte_e_registrada_com_as_tentativas(self):
        cae = next(m for m in fc.MEDIDOS if 'Emilia' in m['NAME'])
        self.assertEqual(cae['VERDICT'], fc.NOT_MEASURED_ACCESS)
        self.assertGreaterEqual(len(cae['ATTEMPTS']), 4)
        self.assertIn('NOT_MEASURED_ACCESS_LIMIT ≠ NOT_PRODUCTIVE', self.M['LAWS'])

    def test_o_que_falta_medir_esta_nomeado_e_repetido_na_recomendacao(self):
        falta = self.M['STILL_NOT_MEASURED']
        self.assertGreaterEqual(len(falta), 3)
        self.assertEqual(sorted(falta),
                         sorted(self.M['RECOMMENDATION']['STILL_UNMEASURED']))

    def test_as_cinco_regioes_prioritarias_foram_todas_tocadas(self):
        regioes = {m['REGION'] for m in fc.MEDIDOS}
        for r in ('Marche', 'Basilicata', 'Emilia-Romagna', 'Puglia', 'Sicilia'):
            self.assertIn(r, regioes, r)

    def test_norma_tecnica_nao_virou_sinal_de_campo(self):
        sic = next(m for m in fc.MEDIDOS if m['REGION'] == 'Sicilia')
        self.assertEqual(sic['VERDICT'], fc.INSTITUTION_ONLY)
        self.assertIn('NORMA TÉCNICA ≠ SINAL DE CAMPO', self.M['LAWS'])


class OConteudoDasMarche(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = fc.medir()

    def test_a_serie_semanal_cobre_a_janela_de_floracao(self):
        amap = next(m for m in fc.MEDIDOS if 'AMAP' in m['NAME'])
        self.assertEqual(len(amap['SERIES_2026']), 4)
        self.assertTrue(any('22/04' in x for x in amap['SERIES_2026']))

    def test_ha_sinal_publicado_ANTES_da_data_do_caso(self):
        self.assertIn('AMAP-MARCHE/AN-615', self.M['SIGNALS_BEFORE_CASE'])

    def test_mas_antes_do_caso_nao_e_antes_da_instituicao(self):
        """O boletim de Ancona é institucional. Publicar antes do caso não o
        torna anterior à instituição — ele É a instituição."""
        self.assertEqual(self.M['EARLIER_THAN_REGION'], [])

    def test_o_escopo_do_documento_deu_a_provincia_e_nao_mais_fino(self):
        for L in self.M['CONTENTS_READ']:
            self.assertEqual(L['DOCUMENT_SCOPE']['PLACE'], 'Ancona')
            for a in L['FACT_LOCATIONS']:
                self.assertEqual(a['FACT_LOCATION_PRECISION'], fl.PROVINCE)
                self.assertEqual(a['PRECISION_SOURCE'], fl.DOCUMENT_SCOPE)

    def test_as_localidades_de_ensaio_nao_viraram_local_do_fato(self):
        """Jesi e Tolentino são onde ficam os campos experimentais — não onde um
        fato foi observado."""
        for L in self.M['CONTENTS_READ']:
            nomes = {a['FACT_LOCATION'] for a in L['FACT_LOCATIONS']}
            self.assertNotIn('Jesi', nomes)
            self.assertNotIn('Tolentino', nomes)

    def test_o_prazo_de_tratamento_nao_virou_data_do_fato(self):
        n615 = next(L for L in self.M['CONTENTS_READ'] if '615' in L['ID'])
        self.assertEqual(n615['TIME']['FACT_TIME'], 'NOT_KNOWN')
        motivos = {d['WHY'] for d in n615['TIME']['TIME_CANDIDATES_DISCARDED']}
        self.assertTrue(motivos & {'PLANNED_ACTION_DATE_NOT_FACT_TIME',
                                   'FUTURE_DATE_NOT_FACT_TIME'})

    def test_a_evidencia_esta_preservada_com_hash_e_sem_dado_pessoal(self):
        import re
        for L in self.M['CONTENTS_READ']:
            caminho = os.path.join(RAIZ, L['EVIDENCE_PATH'])
            with open(caminho, encoding='utf-8') as fh:
                t = fh.read()
            self.assertIsNone(re.search(r'[\w.+-]+@[\w.-]+\.\w{2,}', t), L['ID'])
            import hashlib
            self.assertEqual(hashlib.sha256(t.encode('utf-8')).hexdigest(),
                             L['SHA256'])

    def test_amostra_nao_virou_incidencia_e_nao_houve_gasto(self):
        for L in self.M['CONTENTS_READ']:
            self.assertEqual(L['OCCURRENCE_NOT_INCIDENCE']['INCIDENCE'], 'NOT_KNOWN')
        self.assertEqual(self.M['APIFY_RUNS'], 0)
