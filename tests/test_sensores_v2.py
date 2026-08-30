"""
Provas do mapa V2. O risco aqui é o oposto do da rodada anterior: agora que há um
positivo forte, a tentação é deixá-lo contaminar as classes vizinhas.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import fato_local as fl          # noqa: E402
import italia_sensores_v2 as sv  # noqa: E402


class OTetoEAAmostraNaoSeMovem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = sv.medir()

    def test_o_teto_e_de_50_e_nao_foi_preenchido_artificialmente(self):
        self.assertLessEqual(self.M['TOTAL_VOICES'], sv.TETO)
        self.assertEqual(self.M['TOTAL_VOICES'], len(sv.VOZES))

    def test_as_quatro_classes_existem_e_nenhuma_esta_vazia(self):
        for c in sv.CLASSES:
            self.assertGreater(self.M['BY_CLASS'][c], 0, c)

    def test_os_pesquisadores_continuam_congelados(self):
        """Nenhum dos cinco pode reaparecer como voz nova."""
        nomes = {v['NAME'] for v in sv.VOZES}
        for p in self.M['RESEARCHERS_FROZEN']:
            self.assertNotIn(p, nomes, p)

    def test_toda_voz_tem_os_campos_do_contrato(self):
        for v in sv.VOZES:
            for campo in ('NAME', 'CLASS', 'ROLE', 'ORGANIZATION', 'SOURCE_LOCATION',
                          'OPERATING_GEOGRAPHY', 'PRIMARY_PUBLIC_CHANNEL',
                          'ACTIVE_2026', 'LAST_OBSERVED_CONTENT_DATE',
                          'CADENCE', 'SENSOR_POTENTIAL', 'WHY'):
                self.assertIsNotNone(v.get(campo), '%s / %s' % (v['NAME'], campo))
            self.assertIn(v['CLASS'], sv.CLASSES, v['NAME'])
            self.assertIn(v['CADENCE'], (sv.FIELD_SEASONAL, sv.RECURRENT,
                                         sv.EVENT_DRIVEN, sv.OCCASIONAL,
                                         sv.EVERGREEN_ONLY, sv.CADENCE_NOT_KNOWN))

    def test_nenhuma_voz_carrega_score_numerico(self):
        corpo = json.dumps(sv.VOZES, ensure_ascii=False)
        for proibido in ('SCORE', 'FOLLOWERS', 'RANK', 'PUNTEGGIO'):
            self.assertNotIn(proibido, corpo.upper(), proibido)


class AsPortasQueNaoRendemFicamRegistradas(unittest.TestCase):

    def test_a_agencia_extinta_esta_no_mapa_como_porta_morta(self):
        """Registrar o que não rende é resultado, não sujeira."""
        arsia = next(v for v in sv.VOZES if 'ARSIA' in v['NAME'])
        self.assertEqual(arsia['ACTIVE_2026'], 'NO')
        self.assertEqual(arsia['SENSOR_POTENTIAL'], sv.COMMUNICATION_ONLY)
        self.assertIn('2013', arsia['LAST_OBSERVED_CONTENT_DATE'])

    def test_falha_de_acesso_nao_vira_ausencia_de_sinal(self):
        """O consórcio devolveu 503 duas vezes: NOT_KNOWN, nunca NOT_PRODUCTIVE."""
        cae = next(v for v in sv.VOZES if 'Consorzio Agrario' in v['NAME'])
        self.assertEqual(cae['SENSOR_POTENTIAL'], sv.POTENTIAL_NOT_KNOWN)
        self.assertEqual(cae['ACTIVE_2026'], 'NOT_KNOWN')
        self.assertIn('503', cae['WHY'])
        self.assertIn('ROUTE_UNAVAILABLE ≠ NO_SIGNAL', sv.medir()['LAWS'])

    def test_a_classe_creator_ficou_negativa_e_isso_nao_foi_reamostrado(self):
        creators = [v for v in sv.VOZES if v['CLASS'] == sv.CREATOR_INFLUENCER]
        potenciais = {v['SENSOR_POTENTIAL'] for v in creators}
        self.assertNotIn(sv.PROSPECTIVE_SENSOR, potenciais)
        agregada = next(v for v in creators if 'agro-influencer' in v['NAME'])
        self.assertIn('RESULTADO', agregada['WHY'].upper())

    def test_o_boletim_da_umbria_fica_NOT_KNOWN_para_2026(self):
        """A página lista até 2024. "Não sei se publica em 2026" ≠ "não publica"."""
        u = next(v for v in sv.VOZES if 'Umbria' in v['NAME'])
        self.assertEqual(u['ACTIVE_2026'], 'NOT_KNOWN')
        self.assertEqual(u['SENSOR_POTENTIAL'], sv.PROSPECTIVE_SENSOR)


class OQueOsConteudosLidosSustentam(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = sv.medir()

    def test_todo_conteudo_lido_esta_preservado_com_hash(self):
        for L in self.M['CONTENTS_READ']:
            self.assertEqual(L['EVIDENCE_STATE'], 'PRESERVED', L['ID'])
            self.assertEqual(len(L['SHA256']), 64)
            self.assertTrue(os.path.exists(os.path.join(RAIZ, L['EVIDENCE_PATH'])))

    def test_nenhum_dado_pessoal_ficou_no_material_preservado(self):
        """O boletim traz e-mail e telefone de servidores. O papel fica; o
        endereço não — publicar dado de contato de terceiro não é preservar
        evidência, é redistribuí-lo."""
        import re
        for L in self.M['CONTENTS_READ']:
            with open(os.path.join(RAIZ, L['EVIDENCE_PATH']), encoding='utf-8') as fh:
                t = fh.read()
            self.assertIsNone(re.search(r'[\w.+-]+@[\w.-]+\.\w{2,}', t), L['ID'])

    def test_o_boletim_em_janela_e_de_tres_dias_antes_do_caso(self):
        ersa = next(L for L in self.M['CONTENTS_READ'] if L['ID'].startswith('ERSA'))
        self.assertEqual(ersa['PUBLISHED_AT'], '2026-04-20')
        self.assertEqual(ersa['IN_CASE_WINDOW'], 'IN_WINDOW')

    def test_o_comune_veio_do_texto_e_nao_do_gazetteer(self):
        fatos = {a['FACT_LOCATION']: a for a in self.M['FACT_LOCATIONS_FOUND']}
        self.assertEqual(fatos['Parrano']['PRECISION_SOURCE'], 'DECLARED_BY_TEXT')
        self.assertEqual(fatos['Parrano']['FACT_LOCATION_PRECISION'], fl.MUNICIPALITY)
        self.assertNotIn('Parrano', {n for n, _ in fl.GAZETTEER})

    def test_o_risco_modelado_nao_entrou_como_observacao(self):
        fatos = {a['FACT_LOCATION']: a for a in self.M['FACT_LOCATIONS_FOUND']}
        self.assertEqual(fatos['Friuli-Venezia Giulia']['TYPE_OF_EVIDENCE'],
                         fl.MODELLED_RISK)

    def test_a_geografia_da_voz_nunca_e_a_do_fato(self):
        for v in sv.VOZES:
            self.assertTrue(v['OPERATING_GEOGRAPHY_IS_NOT_FACT_LOCATION'])
        self.assertIn('OPERATING_GEOGRAPHY ≠ FACT_LOCATION', self.M['LAWS'])
        # a região das vozes não aparece como FACT só por elas atuarem lá
        fatos = {a['FACT_LOCATION'] for a in self.M['FACT_LOCATIONS_FOUND']}
        self.assertNotIn('Toscana', fatos)
        self.assertNotIn('Veneto', fatos)


class OsVereditosContinuamSeparados(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = sv.medir()

    def test_o_pesquisador_e_o_institucional_sao_vereditos_diferentes(self):
        """O pesquisador provou contexto; a instituição provou antecipação.
        São capacidades distintas, e nenhuma das duas é sobre pessoa em campo."""
        self.assertEqual(self.M['RESEARCHER_SENSOR'],
                         'CONTEXT_AND_RETROSPECTIVE_PROVED')
        self.assertEqual(self.M['PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR'], 'PROVED')
        self.assertEqual(self.M['PROSPECTIVE_RESEARCHER_SENSOR'], 'NOT_PROVED')

    def test_o_ecossistema_nao_se_declara_MAPPED_com_15_vozes(self):
        self.assertEqual(self.M['ITALY_HUMAN_SENSOR_ECOSYSTEM'], 'PARTIALLY_MAPPED')

    def test_o_prospectivo_so_e_PROVED_com_observacao_de_campo_e_local(self):
        self.assertTrue(self.M['WITH_FIELD_OBSERVATION'])
        self.assertTrue(self.M['FACT_LOCATIONS_COUNT'])
        campo = [a for a in self.M['FACT_LOCATIONS_FOUND']
                 if a['TYPE_OF_EVIDENCE'] == fl.FIELD_OBSERVATION]
        self.assertGreaterEqual(len(campo), 2)

    def test_a_recomendacao_nao_manda_coletar_rede_social(self):
        n = self.M['NEXT_STEP']
        self.assertIn('boletim', n['CHANNEL'].lower())
        self.assertIn('falta de sinal de campo', n['WHY_NOT_SOCIAL'])
        alvos = json.dumps(self.M['HIGH_VALUE_SENSOR_TARGETS'], ensure_ascii=False)
        for rede in ('Instagram', 'TikTok', 'LinkedIn'):
            self.assertNotIn(rede, alvos, rede)

    def test_o_que_ficou_por_medir_esta_nomeado(self):
        falta = ' '.join(self.M['NEXT_STEP']['STILL_UNMEASURED'])
        self.assertIn('Emilia', falta)
        self.assertIn('Umbria', falta)

    def test_nenhuma_palavra_proibida_aparece_fora_da_lista(self):
        corpo = json.dumps({k: v for k, v in self.M.items()
                            if k != 'STILL_FORBIDDEN_TO_WRITE'}, ensure_ascii=False)
        for p in self.M['STILL_FORBIDDEN_TO_WRITE']:
            self.assertNotIn(p, corpo, p)

    def test_nenhuma_execucao_paga(self):
        self.assertEqual(self.M['APIFY_RUNS'], 0)
        self.assertEqual(self.M['APIFY_COST_USD'], 0)


class InstituicaoNaoEPessoa(unittest.TestCase):
    """A prova que faltava na rodada anterior.

    `PROSPECTIVE_HUMAN_SENSOR = PROVED` foi publicado a partir de cinco vozes
    prospectivas das quais CINCO eram organizações. Nenhuma pessoa produziu sinal
    prospectivo medido, e mesmo assim o veredito falava de sensor humano.

        INSTITUTIONAL_SIGNAL ≠ HUMAN_PERSON_SIGNAL
    """

    @classmethod
    def setUpClass(cls):
        cls.M = sv.medir()

    def test_toda_voz_declara_se_e_pessoa_ou_organizacao(self):
        """Era o campo ausente que permitiu a confusão."""
        for v in sv.VOZES:
            self.assertIn(v['ENTITY_KIND'], sv.ENTITY_KINDS, v['NAME'])

    def test_nenhuma_voz_prospectiva_medida_e_uma_pessoa(self):
        por_tipo = self.M['ENTITY_KIND_OF_PROSPECTIVE_VOICES']
        self.assertEqual(por_tipo[sv.PERSON], 0)
        self.assertGreater(por_tipo[sv.ORGANIZATION], 0)

    def test_o_veredito_sobre_pessoas_nao_herda_o_das_instituicoes(self):
        self.assertEqual(self.M['PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR'], 'PROVED')
        self.assertEqual(self.M['PROSPECTIVE_HUMAN_PERSON_SENSOR'], 'NOT_PROVED')
        self.assertNotEqual(self.M['PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR'],
                            self.M['PROSPECTIVE_HUMAN_PERSON_SENSOR'])

    def test_os_cinco_estados_existem_separados_antes_do_sexto(self):
        for k in ('PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR',
                  'PROSPECTIVE_TECHNICAL_PERSON_SENSOR',
                  'PROSPECTIVE_PRODUCER_SENSOR', 'PROSPECTIVE_CREATOR_SENSOR',
                  'PROSPECTIVE_RESEARCHER_SENSOR'):
            self.assertIn(self.M[k], ('PROVED', 'PROMISING', 'NOT_PROVED'), k)

    def test_o_veredito_antigo_nao_existe_mais_com_o_nome_ambiguo(self):
        """"HUMAN_SENSOR" sem dizer pessoa ou instituição foi o que confundiu."""
        self.assertNotIn('PROSPECTIVE_HUMAN_SENSOR', self.M)

    def test_a_correcao_esta_registrada_e_nao_apagada(self):
        c = self.M['CORRECTION_OF_PREVIOUS_ROUND']
        self.assertIn('PROVED', c)
        self.assertIn('organizações', c)

    def test_mutacao_se_o_tipo_de_entidade_for_ignorado_o_erro_volta(self):
        """A prova de que é ENTITY_KIND que segura a distinção."""
        salvo = [v['ENTITY_KIND'] for v in sv.VOZES]
        try:
            for v in sv.VOZES:
                v['ENTITY_KIND'] = sv.PERSON
            m = sv.medir()
            self.assertEqual(m['PROSPECTIVE_HUMAN_PERSON_SENSOR'], 'PROMISING',
                             'a mutação não mudou nada — a prova não mordia')
        finally:
            for v, k in zip(sv.VOZES, salvo):
                v['ENTITY_KIND'] = k
        self.assertEqual(sv.medir()['PROSPECTIVE_HUMAN_PERSON_SENSOR'], 'NOT_PROVED')
