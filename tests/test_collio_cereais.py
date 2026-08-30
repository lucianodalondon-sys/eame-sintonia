"""
Provas da pergunta central. O risco aqui é o mais sutil de todos: um NO honesto
virar um NO preguiçoso, ou o positivo da vinha escorregar para os cereais.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import fato_local as fl              # noqa: E402
import italia_collio_cereais as cc   # noqa: E402
import italia_sensores_v2 as sv      # noqa: E402


class ONaoEEstruturalENaoPreguicoso(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = cc.medir()

    def test_o_nao_se_apoia_em_evidencia_verificavel_e_nao_em_ausencia_de_busca(self):
        """"não achei" e "a instituição não abriu a porta" são coisas diferentes."""
        e = self.M['STRUCTURAL_EVIDENCE']
        self.assertEqual(e['CONSORTIUM_SLOT_UNDER'], ['vite'])
        self.assertEqual(len(e['SECTIONS']), 8)
        self.assertIn('colture-erbacee-orticole', e['SECTIONS'])
        self.assertIn('ausência verificável', e['WHY_THIS_MATTERS'])

    def test_a_hipotese_que_explica_esta_marcada_como_nao_medida(self):
        h = self.M['STRUCTURAL_HYPOTHESIS']
        self.assertIn('NOT_MEASURED', h['STATE'])
        self.assertIn('não foi testada', h['STATE'])

    def test_o_que_ficou_por_medir_esta_nomeado_e_nao_e_pequeno(self):
        falta = self.M['RECOMMENDATION']['STILL_UNMEASURED']
        self.assertGreaterEqual(len(falta), 4)
        junto = ' '.join(falta)
        self.assertIn('Emilia', junto)
        self.assertIn('AgroAmbiente', junto)

    def test_falha_de_transporte_nao_vira_ausencia_de_sinal(self):
        cae = next(c for c in cc.CANDIDATOS if 'Emilia' in c['NAME'])
        self.assertEqual(cae['VERDICT'], cc.NOT_MEASURED)
        self.assertIn('TLS', cae['WHY'])
        self.assertIn('ROUTE_TLS_CHAIN_INCOMPLETE ≠ NO_SIGNAL', self.M['LAWS'])

    def test_a_correcao_da_porta_que_eu_dera_por_morta(self):
        """AgroAmbiente: eu tinha dito ARSIA morta com links de 2013. Mudou de host."""
        a = next(c for c in cc.CANDIDATOS if 'AgroAmbiente' in c['NAME'])
        self.assertEqual(a['VERDICT'], cc.NOT_MEASURED)
        self.assertIn('CORREÇÃO', a['WHY'])
        self.assertIn('DEAD_LINK ≠ DEAD_SERVICE', self.M['LAWS'])


class OPositivoDaVinhaNaoEscorregaParaOsCereais(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = cc.medir()

    def test_o_controle_esta_marcado_como_controle_e_nao_conta_como_achado(self):
        collio = next(c for c in cc.CANDIDATOS if c['NAME'] == 'Consorzio Collio')
        self.assertTrue(collio['IS_THE_CONTROL'])
        self.assertEqual(collio['CROP'], 'vite')
        self.assertEqual(self.M['CEREAL_COLLIO_EQUIVALENT_FOUND'], 'PARTIAL')

    def test_nao_existe_equivalente_para_grano_duro(self):
        self.assertEqual(self.M['EXISTS_FOR_DURUM_FUSARIUM'], 'NO')
        self.assertIn('institucional', self.M['EXISTS_FOR_DURUM_FUSARIUM_WHY'])

    def test_todo_veredito_carrega_cultura_e_geografia(self):
        for k, v in self.M.items():
            if k.startswith('PROSPECTIVE_'):
                self.assertIn('STATE', v, k)
                self.assertIn(v['STATE'], ('PROVED', 'PROMISING', 'NOT_PROVED'), k)
                self.assertIn('CROP_SCOPE', v, k)
                self.assertIn('GEOGRAPHIC_SCOPE', v, k)

    def test_os_vereditos_de_vinha_dizem_explicitamente_que_nao_sao_cereais(self):
        for k in ('PROSPECTIVE_TECHNICAL_PERSON_SENSOR',
                  'PROSPECTIVE_PRODUCER_COOP_SENSOR', 'PROSPECTIVE_CREATOR_SENSOR'):
            self.assertIn('NÃO', self.M[k]['CROP_SCOPE'], k)

    def test_existe_um_veredito_separado_para_pessoa_em_cereais(self):
        v = self.M['PROSPECTIVE_HUMAN_PERSON_SENSOR_FOR_CEREALS']
        self.assertEqual(v['STATE'], 'NOT_PROVED')
        self.assertNotEqual(v['STATE'],
                            self.M['PROSPECTIVE_HUMAN_PERSON_SENSOR']['STATE'])

    def test_cooperativa_nao_virou_produtor_pessoa(self):
        self.assertEqual(self.M['PROSPECTIVE_PRODUCER_COOP_SENSOR']['STATE'], 'PROVED')
        self.assertEqual(self.M['PROSPECTIVE_PRODUCER_PERSON_SENSOR']['STATE'],
                         'NOT_PROVED')
        self.assertIn('PRODUCER_COOP_ORGANIZATION ≠ PRODUCER_PERSON', self.M['LAWS'])
        self.assertIn('ORGANIZAÇÃO', self.M['PRODUCER_CORRECTION'])


class APernaDeCampoDoCaso(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = cc.medir()
        cls.L = cls.M['CASE_FIELD_LEG']

    def test_o_boletim_do_caso_agora_produz_o_lugar_do_caso(self):
        fatos = {a['FACT_LOCATION']: a for a in self.L['FACT_LOCATIONS']}
        self.assertIn('Grosseto', fatos)
        self.assertEqual(fatos['Grosseto']['FACT_LOCATION_PRECISION'], fl.PROVINCE)
        self.assertEqual(fatos['Grosseto']['PRECISION_SOURCE'], fl.DOCUMENT_SCOPE)

    def test_a_evidencia_e_a_frase_do_sintoma_no_duro(self):
        fatos = {a['FACT_LOCATION']: a for a in self.L['FACT_LOCATIONS']}
        ev = fatos['Grosseto']['FACT_LOCATION_EVIDENCE']
        self.assertIn('frumento duro', ev)
        self.assertIn('sintomi', ev)

    def test_a_zona_sub_provincial_nao_virou_lugar(self):
        """§14: não inventar município — e "area nord/sud" é zona, não unidade."""
        nomes = {a['FACT_LOCATION'] for a in self.L['FACT_LOCATIONS']}
        for zona in ('nord', 'sud', 'area nord', 'area sud'):
            self.assertNotIn(zona, nomes)
        self.assertIn('zona agronômica', self.L['SUB_PROVINCIAL_QUALIFIER'])
        self.assertIn('AGRONOMIC_ZONE ≠ ADMIN_UNIT', self.M['LAWS'])

    def test_a_fonte_separa_observacao_de_modelo_e_o_registro_tambem(self):
        self.assertIn('Rischio fusariosi da modello',
                      self.L['SEPARATES_OBSERVATION_FROM_MODEL'])

    def test_o_hash_da_evidencia_confere(self):
        import hashlib
        with open(os.path.join(RAIZ, self.L['EVIDENCE_PATH']), 'rb') as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), self.L['SHA256'])

    def test_amostra_nao_virou_incidencia(self):
        o = self.L['OCCURRENCE_NOT_INCIDENCE']
        self.assertEqual(o['INCIDENCE'], 'NOT_KNOWN')
        self.assertEqual(o['REGIONAL_PRESSURE'], 'NOT_KNOWN')


class NaoInventarAntecedencia(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = cc.medir()

    def test_a_antecedencia_medida_e_zero_e_esta_dita(self):
        t = self.M['TIMELINE']
        self.assertTrue(t['FIRST_REGIONAL_INSTITUTION_SIGNAL'].startswith(t['CASE_DATE']))
        self.assertIn('ZERO dias', t['ANTICIPATION'])
        self.assertIn('SAME_DATE ≠ ANTICIPATION', self.M['LAWS'])

    def test_nao_ha_observacao_humana_anterior_inventada(self):
        t = self.M['TIMELINE']
        self.assertIn('NOT_OBSERVED', t['FIRST_HUMAN_OBSERVATION'])
        self.assertIn('NOT_OBSERVED', t['FIRST_LOCAL_ORGANIZATION_SIGNAL'])

    def test_ninguem_ficou_como_EARLIER_ou_MORE_LOCAL_nos_cereais(self):
        a = self.M['ADDS_OVER_REGIONAL_BASELINE']
        self.assertEqual(a['EARLIER_THAN_INSTITUTION'], [])
        self.assertEqual(a['MORE_LOCAL_THAN_INSTITUTION'], [])
        self.assertTrue(a['REPETITION_ONLY'])

    def test_creator_citado_pela_cadeia_nao_existe_em_cereais(self):
        c = self.M['CREATOR_CITED_BY_TECHNICAL_CHAIN']
        self.assertEqual(c['IN_CEREALS'], 'NOT_FOUND_IN_THIS_SEARCH')
        self.assertTrue(c['IN_VINE'])

    def test_a_recomendacao_nao_promete_antecedencia_em_cereais(self):
        r = self.M['RECOMMENDATION']
        self.assertIn('antecedência', r['DO_NOT_EXPECT'])
        self.assertIn('institucional', r['COLLECT_RECURRENTLY'])

    def test_nenhuma_execucao_paga_e_nenhuma_palavra_proibida(self):
        self.assertEqual(self.M['APIFY_RUNS'], 0)
        corpo = json.dumps({k: v for k, v in self.M.items()
                            if k != 'STILL_FORBIDDEN_TO_WRITE'}, ensure_ascii=False)
        for p in self.M['STILL_FORBIDDEN_TO_WRITE']:
            self.assertNotIn(p, corpo, p)
